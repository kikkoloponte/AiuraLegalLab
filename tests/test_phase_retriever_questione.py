"""
Test PhaseRetriever._expand_via_questione — pre-filtro Fase 2/3 via
QuestioneGiuridica. Vedi
docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md §9.

Tutti i test usano mock di HybridRetriever/GraphRetriever (zero MongoDB,
zero grafo reale).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from aiura_legal.core.types import SearchResult
from aiura_legal.core.retrieval.phase_retriever import PhaseRetriever


def _make_result(doc_id: str, score: float = 1.0, source_layer: str = "normativa") -> SearchResult:
    return SearchResult(doc_id=doc_id, score=score, snippet="...", source_layer=source_layer)


def _make_retriever(graph_available: bool = True) -> MagicMock:
    mock = MagicMock()
    mock.graph.is_available = graph_available
    return mock


class TestExpandViaQuestioneFlagOff:
    """Default (AIURA_QUESTIONE_EXPANSION non impostato) — zero regressione."""

    def test_flag_off_non_interroga_il_grafo(self, monkeypatch):
        monkeypatch.delenv("AIURA_QUESTIONE_EXPANSION", raising=False)
        # Serve ricaricare il modulo per far rileggere l'env var a freddo —
        # più semplice: importiamo la costante e la sovrascriviamo a mano
        # nei test che ne hanno bisogno (vedi classi sotto). Qui verifichiamo
        # solo che senza intervento il default sia "0" (comportamento storico).
        import aiura_legal.core.retrieval.phase_retriever as mod
        assert mod._QUESTIONE_EXPANSION_ENABLED is False


class TestExpandViaQuestioneFlagOn:
    """Forza il flag a True direttamente sul modulo (più robusto del monkeypatch
    su os.environ, dato che la costante è già risolta a import-time)."""

    @pytest.fixture(autouse=True)
    def _enable_flag(self, monkeypatch):
        import aiura_legal.core.retrieval.phase_retriever as mod
        monkeypatch.setattr(mod, "_QUESTIONE_EXPANSION_ENABLED", True)

    def test_nessun_match_ritorna_invariato(self):
        retriever = _make_retriever()
        retriever.graph.match_questione.return_value = None
        pr = PhaseRetriever(retriever)

        base = [_make_result("a")]
        out = pr._expand_via_questione("query qualunque", base, top_k=6, source_layer="normativa")

        assert out == base
        retriever.graph.expand_from_questione.assert_not_called()

    def test_grafo_non_disponibile_ritorna_invariato(self):
        retriever = _make_retriever(graph_available=False)
        pr = PhaseRetriever(retriever)

        base = [_make_result("a")]
        out = pr._expand_via_questione("query", base, top_k=6, source_layer="normativa")

        assert out == base
        retriever.graph.match_questione.assert_not_called()

    def test_match_fonde_risultati_dello_stesso_layer(self):
        retriever = _make_retriever()
        retriever.graph.match_questione.return_value = "q1"
        retriever.graph.expand_from_questione.return_value = [
            _make_result("urn:nuovo", score=1.0, source_layer="normativa"),
        ]
        pr = PhaseRetriever(retriever)

        base = [_make_result("a", score=0.5, source_layer="normativa")]
        out = pr._expand_via_questione("query", base, top_k=6, source_layer="normativa")

        ids = {r.doc_id for r in out}
        assert ids == {"a", "urn:nuovo"}

    def test_match_filtra_layer_diverso(self):
        """expand_from_questione può restituire fonti di entrambi i layer
        (article + sentenza collegati alla stessa questione) — solo quelle
        del layer richiesto vanno fuse, l'altro layer lo recupera la fase
        corrispondente con la sua chiamata separata."""
        retriever = _make_retriever()
        retriever.graph.match_questione.return_value = "q1"
        retriever.graph.expand_from_questione.return_value = [
            _make_result("urn:norma", score=1.0, source_layer="normativa"),
            _make_result("sentenza:1", score=1.0, source_layer="giurisprudenza"),
        ]
        pr = PhaseRetriever(retriever)

        base = [_make_result("a", score=0.5, source_layer="giurisprudenza")]
        out = pr._expand_via_questione("query", base, top_k=6, source_layer="giurisprudenza")

        ids = {r.doc_id for r in out}
        assert ids == {"a", "sentenza:1"}
        assert "urn:norma" not in ids

    def test_nessuna_expansion_del_layer_ritorna_invariato(self):
        retriever = _make_retriever()
        retriever.graph.match_questione.return_value = "q1"
        retriever.graph.expand_from_questione.return_value = [
            _make_result("sentenza:1", score=1.0, source_layer="giurisprudenza"),
        ]
        pr = PhaseRetriever(retriever)

        base = [_make_result("a", score=0.5, source_layer="normativa")]
        out = pr._expand_via_questione("query", base, top_k=6, source_layer="normativa")

        assert out == base

    def test_max_total_rispetta_top_k_piu_expansion(self):
        retriever = _make_retriever()
        retriever.graph.match_questione.return_value = "q1"
        retriever.graph.expand_from_questione.return_value = [
            _make_result(f"new{i}", score=1.0, source_layer="normativa") for i in range(5)
        ]
        pr = PhaseRetriever(retriever)

        base = [_make_result(f"base{i}", score=0.9, source_layer="normativa") for i in range(3)]
        out = pr._expand_via_questione("query", base, top_k=2, source_layer="normativa")

        # top_k=2 + 5 nuove = max_total 7, ma totale disponibile è 3+5=8 → troncato a 7
        assert len(out) == 7
