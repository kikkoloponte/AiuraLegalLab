"""
Test PhaseRetriever — filtri settore soft/hard + corpus prassi.

Tutti i test usano mock di HybridRetriever (zero MongoDB, zero BM25 reale).
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from aiura_legal.core.types import SearchResult
from aiura_legal.core.retrieval.phase_retriever import (
    PhaseRetriever,
    _apply_soft_penalty,
    _merge_unique,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_result(doc_id: str, score: float = 1.0, settore: str | None = None) -> SearchResult:
    meta = {"settore": settore} if settore else {}
    return SearchResult(doc_id=doc_id, score=score, snippet="...", metadata=meta)


def _make_retriever(results: list[SearchResult] | None = None) -> MagicMock:
    """Crea un HybridRetriever mock che restituisce i risultati forniti."""
    mock = MagicMock()
    mock._search_round.return_value = results or []
    return mock


# ---------------------------------------------------------------------------
# _apply_soft_penalty
# ---------------------------------------------------------------------------

class TestApplySoftPenalty:
    def test_penalizza_fuori_settore(self):
        results = [
            _make_result("a", 1.0, settore="diritto_civile"),
            _make_result("b", 1.0, settore="diritto_penale"),
        ]
        out = _apply_soft_penalty(results, "diritto_civile")
        scores = {r.doc_id: r.score for r in out}
        assert scores["a"] == pytest.approx(1.0)
        assert scores["b"] == pytest.approx(0.5)

    def test_nessuna_penalita_settore_assente(self):
        results = [_make_result("a", 1.0)]  # no settore in metadata
        out = _apply_soft_penalty(results, "diritto_civile")
        assert out[0].score == pytest.approx(1.0)

    def test_ordinamento_post_penalita(self):
        results = [
            _make_result("a", 0.8, settore="diritto_penale"),
            _make_result("b", 0.6, settore="diritto_civile"),
        ]
        out = _apply_soft_penalty(results, "diritto_civile")
        # b (0.6 invariato) > a (0.8 × 0.5 = 0.4)
        assert out[0].doc_id == "b"


# ---------------------------------------------------------------------------
# _merge_unique
# ---------------------------------------------------------------------------

class TestMergeUnique:
    def test_rimuove_duplicati(self):
        primary = [_make_result("a"), _make_result("b")]
        secondary = [_make_result("b"), _make_result("c")]
        out = _merge_unique(primary, secondary, max_total=10)
        assert [r.doc_id for r in out] == ["a", "b", "c"]

    def test_rispetta_max_total(self):
        primary = [_make_result("a"), _make_result("b")]
        secondary = [_make_result("c"), _make_result("d")]
        out = _merge_unique(primary, secondary, max_total=3)
        assert len(out) == 3


# ---------------------------------------------------------------------------
# PhaseRetriever.retrieve_normativa
# ---------------------------------------------------------------------------

class TestRetrieveNormativa:
    def test_base_no_settore(self):
        mock = _make_retriever([_make_result("n1"), _make_result("n2")])
        pr = PhaseRetriever(mock)
        results = pr.retrieve_normativa("contratto di appalto")
        assert len(results) == 2
        assert all(r.source_layer == "normativa" for r in results)

    def test_query_vuota_ritorna_lista_vuota(self):
        pr = PhaseRetriever(_make_retriever())
        assert pr.retrieve_normativa("") == []
        assert pr.retrieve_normativa("   ") == []

    # --- Fallback hard filter ---

    @patch.dict(os.environ, {"AIURA_SETTORE_FILTER": "1", "AIURA_SETTORE_SOFT": "0"})
    def test_hard_filter_fallback_se_zero_risultati(self):
        """
        Con filtro hard attivo: se _search_round con filtro settore → 0 risultati,
        PhaseRetriever riprova senza filtro settore.

        Nota: _search_round viene chiamato 3 volte in totale perché retrieve_normativa
        chiama anche _retrieve_prassi (1 call aggiuntiva).
        """
        no_results: list[SearchResult] = []
        fallback_results = [_make_result("f1"), _make_result("f2"), _make_result("f3")]

        mock = MagicMock()
        # Call 1: normativa con filtro settore → 0 risultati (trigger fallback)
        # Call 2: normativa senza filtro settore → fallback_results
        # Call 3: prassi → lista vuota (graceful skip se StopIteration)
        mock._search_round.side_effect = [no_results, fallback_results, []]

        with patch(
            "aiura_legal.core.retrieval.phase_retriever._SETTORE_FILTER_ENABLED",
            True,
        ):
            pr = PhaseRetriever(mock)
            pr.retrieve_normativa(
                "licenziamento", settore="diritto_lavoro", settore_confidence=0.9
            )

        # Le prime due chiamate riguardano normativa (hard + fallback)
        first_call_filter = mock._search_round.call_args_list[0][1]["chunk_filter"]
        second_call_filter = mock._search_round.call_args_list[1][1]["chunk_filter"]
        assert first_call_filter.get("settore") == "diritto_lavoro"  # hard
        assert "settore" not in second_call_filter  # fallback senza settore

    @patch.dict(os.environ, {"AIURA_SETTORE_FILTER": "1", "AIURA_SETTORE_SOFT": "0"})
    def test_hard_filter_no_fallback_se_risultati_sufficienti(self):
        """Con filtro hard e >= 3 risultati, non si fa fallback per normativa."""
        enough = [_make_result(f"r{i}") for i in range(4)]
        # Prima call: normativa (risultati sufficienti), seconda call: prassi
        mock = MagicMock()
        mock._search_round.side_effect = [enough, []]

        with patch(
            "aiura_legal.core.retrieval.phase_retriever._SETTORE_FILTER_ENABLED",
            True,
        ):
            pr = PhaseRetriever(mock)
            pr.retrieve_normativa("appalto", settore="diritto_civile", settore_confidence=0.8)

        # Solo 1 call normativa (no fallback) + 1 call prassi = 2 totali
        normativa_calls = [
            c for c in mock._search_round.call_args_list
            if c[1].get("chunk_filter", {}).get("corpus") == "normattiva"
        ]
        assert len(normativa_calls) == 1

    # --- Corpus prassi ---

    def test_prassi_assente_nessuna_eccezione(self):
        """Se corpus prassi → 0 risultati, retrieve_normativa non solleva eccezione."""
        mock = _make_retriever([_make_result("n1")])
        pr = PhaseRetriever(mock)
        # _search_round ritorna lista vuota sia per normativa che per prassi
        results = pr.retrieve_normativa("contratto locazione")
        assert isinstance(results, list)

    def test_prassi_exception_nessuna_eccezione(self):
        """Se _search_round solleva eccezione per prassi, viene ignorata gracefully."""
        base_results = [_make_result("n1"), _make_result("n2")]

        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            cf = kwargs.get("chunk_filter", {})
            if cf.get("corpus") == "prassi":
                raise RuntimeError("corpus prassi non disponibile")
            return base_results

        mock = MagicMock()
        mock._search_round.side_effect = side_effect

        pr = PhaseRetriever(mock)
        results = pr.retrieve_normativa("usucapione")
        assert len(results) == 2
        assert all(r.source_layer == "normativa" for r in results)

    def test_prassi_risultati_aggiunti_al_pool(self):
        """Se corpus prassi ha risultati, vengono inclusi con score scalato."""
        normativa = [_make_result("n1", 1.0), _make_result("n2", 0.8)]
        prassi = [_make_result("p1", 1.0)]

        def side_effect(*args, **kwargs):
            cf = kwargs.get("chunk_filter", {})
            if cf.get("corpus") == "prassi":
                return prassi
            return normativa

        mock = MagicMock()
        mock._search_round.side_effect = side_effect

        pr = PhaseRetriever(mock)
        results = pr.retrieve_normativa("prelazione agraria")
        doc_ids = [r.doc_id for r in results]
        assert "p1" in doc_ids
        # Score prassi deve essere scalato (< score normativa originale)
        prassi_result = next(r for r in results if r.doc_id == "p1")
        assert prassi_result.score < 1.0


# ---------------------------------------------------------------------------
# PhaseRetriever.retrieve_giurisprudenza
# ---------------------------------------------------------------------------

class TestRetrieveGiurisprudenza:
    def test_base(self):
        mock = _make_retriever([_make_result("g1")])
        pr = PhaseRetriever(mock)
        results = pr.retrieve_giurisprudenza("responsabilità medica")
        assert results[0].source_layer == "giurisprudenza"

    def test_query_vuota(self):
        pr = PhaseRetriever(_make_retriever())
        assert pr.retrieve_giurisprudenza("") == []

    @patch.dict(os.environ, {"AIURA_SETTORE_FILTER": "1"})
    def test_fallback_giurisprudenza(self):
        """Fallback funziona anche per giurisprudenza."""
        no_results: list[SearchResult] = []
        fallback = [_make_result(f"g{i}") for i in range(3)]

        mock = MagicMock()
        mock._search_round.side_effect = [no_results, fallback]

        with patch(
            "aiura_legal.core.retrieval.phase_retriever._SETTORE_FILTER_ENABLED",
            True,
        ):
            pr = PhaseRetriever(mock)
            results = pr.retrieve_giurisprudenza(
                "licenziamento", settore="diritto_lavoro", settore_confidence=0.85
            )

        assert mock._search_round.call_count == 2


# ---------------------------------------------------------------------------
# PhaseRetriever.retrieve_dottrina
# ---------------------------------------------------------------------------

class TestRetrieveDottrina:
    def test_base(self):
        mock = _make_retriever([_make_result("d1")])
        pr = PhaseRetriever(mock)
        results = pr.retrieve_dottrina("interpretazione contrattuale")
        assert results[0].source_layer == "dottrina"

    def test_query_vuota(self):
        pr = PhaseRetriever(_make_retriever())
        assert pr.retrieve_dottrina("") == []


# ---------------------------------------------------------------------------
# Dual-path doctrinale — query_type cambia i pesi RRF, non solo il prompt
# ---------------------------------------------------------------------------

class TestQueryTypeWeights:
    def test_normativa_case_usa_pesi_bm25_heavy(self):
        from aiura_legal.core.retrieval.hybrid_retriever import _WEIGHTS_NORMATIVA
        mock = _make_retriever([_make_result("n1")])
        pr = PhaseRetriever(mock)
        pr.retrieve_normativa("art. 1218 c.c.", query_type="case")
        used_weights = mock._search_round.call_args_list[0][1]["weights"]
        assert used_weights == _WEIGHTS_NORMATIVA

    def test_normativa_doctrine_usa_pesi_vector_heavy(self):
        from aiura_legal.core.retrieval.hybrid_retriever import _WEIGHTS_NORMATIVA_DOCTRINE
        mock = _make_retriever([_make_result("n1")])
        pr = PhaseRetriever(mock)
        pr.retrieve_normativa("quando è legittima la recessione per giusta causa", query_type="doctrine")
        used_weights = mock._search_round.call_args_list[0][1]["weights"]
        assert used_weights == _WEIGHTS_NORMATIVA_DOCTRINE

    def test_dottrina_case_usa_pesi_bilanciati(self):
        from aiura_legal.core.retrieval.hybrid_retriever import _WEIGHTS_DOTTRINA
        mock = _make_retriever([_make_result("d1")])
        pr = PhaseRetriever(mock)
        pr.retrieve_dottrina("interpretazione art. 1218", query_type="case")
        used_weights = mock._search_round.call_args_list[0][1]["weights"]
        assert used_weights == _WEIGHTS_DOTTRINA

    def test_dottrina_doctrine_usa_pesi_vector_heavy(self):
        from aiura_legal.core.retrieval.hybrid_retriever import _WEIGHTS_DOTTRINA_DOCTRINE
        mock = _make_retriever([_make_result("d1")])
        pr = PhaseRetriever(mock)
        pr.retrieve_dottrina("cosa si intende per giusta causa", query_type="doctrine")
        used_weights = mock._search_round.call_args_list[0][1]["weights"]
        assert used_weights == _WEIGHTS_DOTTRINA_DOCTRINE

    def test_default_query_type_e_case(self):
        """Se query_type non viene passato, il comportamento resta quello legacy (case)."""
        from aiura_legal.core.retrieval.hybrid_retriever import _WEIGHTS_NORMATIVA
        mock = _make_retriever([_make_result("n1")])
        pr = PhaseRetriever(mock)
        pr.retrieve_normativa("art. 1218 c.c.")
        used_weights = mock._search_round.call_args_list[0][1]["weights"]
        assert used_weights == _WEIGHTS_NORMATIVA


# ---------------------------------------------------------------------------
# _effective_filter
# ---------------------------------------------------------------------------

class TestEffectiveFilter:
    def test_no_settore_ritorna_base(self):
        mock = _make_retriever()
        pr = PhaseRetriever(mock)
        base = {"corpus": "normattiva"}
        result = pr._effective_filter(base, settore=None, settore_confidence=0.9, label="test")
        assert result == base

    def test_bassa_confidence_nessun_filtro_settore(self):
        """confidence < 0.4 → nessun filtro settore anche se flag attivo."""
        mock = _make_retriever()
        pr = PhaseRetriever(mock)
        base = {"corpus": "normattiva"}
        with patch(
            "aiura_legal.core.retrieval.phase_retriever._SETTORE_FILTER_ENABLED",
            True,
        ):
            result = pr._effective_filter(base, settore="diritto_civile", settore_confidence=0.3, label="test")
        assert "settore" not in result

    def test_alta_confidence_hard_filter(self):
        """confidence >= 0.7 + flag → filtro hard con settore."""
        mock = _make_retriever()
        pr = PhaseRetriever(mock)
        base = {"corpus": "normattiva"}
        with patch(
            "aiura_legal.core.retrieval.phase_retriever._SETTORE_FILTER_ENABLED",
            True,
        ):
            result = pr._effective_filter(base, settore="diritto_civile", settore_confidence=0.8, label="test")
        assert result.get("settore") == "diritto_civile"

    def test_media_confidence_soft_solo_corpus(self):
        """confidence 0.4–0.7 + soft flag → solo filtro corpus (penalità post-hoc)."""
        mock = _make_retriever()
        pr = PhaseRetriever(mock)
        base = {"corpus": "normattiva"}
        with (
            patch("aiura_legal.core.retrieval.phase_retriever._SETTORE_FILTER_ENABLED", False),
            patch("aiura_legal.core.retrieval.phase_retriever._SETTORE_SOFT_ENABLED", True),
        ):
            result = pr._effective_filter(base, settore="diritto_civile", settore_confidence=0.55, label="test")
        assert "settore" not in result
