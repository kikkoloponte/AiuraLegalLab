"""
Test CrossEncoderReranker — modello configurabile, input full_text, fallback.

I test che richiedono il download del modello reale sono marcati skipif
(attivabili con AIURA_TEST_RERANKER=1).
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
import tiktoken

from aiura_legal.core.retrieval.reranker import (
    CrossEncoderReranker,
    RerankerSettings,
    _DEFAULT_RERANKER_MODEL,
    _RERANK_MAX_TOKENS,
    _rerank_input,
)
from aiura_legal.core.types import SearchResult

_ENC = tiktoken.get_encoding("cl100k_base")


def _result(doc_id: str, snippet: str = "snippet", full_text: str = "") -> SearchResult:
    return SearchResult(
        doc_id=doc_id, score=0.5, snippet=snippet,
        source_id=f"src_{doc_id}", full_text=full_text,
    )


# ---------------------------------------------------------------------------
# Configurazione modello
# ---------------------------------------------------------------------------

class TestModelConfig:
    def test_default_multilingue(self):
        assert "mmarco" in _DEFAULT_RERANKER_MODEL.lower()
        assert RerankerSettings().reranker_model == _DEFAULT_RERANKER_MODEL

    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("RERANKER_MODEL", "cross-encoder/modello-custom")
        assert RerankerSettings().reranker_model == "cross-encoder/modello-custom"

    def test_il_modello_configurato_viene_usato(self):
        with patch("sentence_transformers.CrossEncoder") as MockCE:
            CrossEncoderReranker()
            MockCE.assert_called_once_with(_DEFAULT_RERANKER_MODEL)

    def test_model_name_esplicito_ha_priorita(self):
        with patch("sentence_transformers.CrossEncoder") as MockCE:
            CrossEncoderReranker(model_name="cross-encoder/esplicito")
            MockCE.assert_called_once_with("cross-encoder/esplicito")


# ---------------------------------------------------------------------------
# Input del rerank: full_text troncato, fallback snippet
# ---------------------------------------------------------------------------

class TestRerankInput:
    def test_full_text_usato_se_presente(self):
        r = _result("d1", snippet="corto", full_text="testo pieno del documento")
        assert _rerank_input(r) == "testo pieno del documento"

    def test_full_text_troncato_a_510_token(self):
        r = _result("d1", full_text="parola " * 3000)
        out = _rerank_input(r)
        assert len(_ENC.encode(out)) <= _RERANK_MAX_TOKENS

    def test_fallback_snippet_senza_full_text(self):
        r = _result("d1", snippet="solo snippet disponibile")
        assert _rerank_input(r) == "solo snippet disponibile"

    def test_predict_riceve_full_text(self):
        with patch("sentence_transformers.CrossEncoder") as MockCE:
            model = MagicMock()
            model.predict.return_value = [0.9, 0.1]
            MockCE.return_value = model
            rr = CrossEncoderReranker()

            cands = [
                _result("d1", full_text="testo pieno uno"),
                _result("d2", snippet="snippet due"),
            ]
            rr.rerank("query", cands, top_k=2)

            pairs = model.predict.call_args.args[0]
            assert pairs[0] == ("query", "testo pieno uno")
            assert pairs[1] == ("query", "snippet due")


# ---------------------------------------------------------------------------
# Fallback: modello non disponibile → ordine originale
# ---------------------------------------------------------------------------

class TestFallback:
    def _broken_reranker(self) -> CrossEncoderReranker:
        with patch("sentence_transformers.CrossEncoder", side_effect=OSError("no model")):
            return CrossEncoderReranker()

    def test_modello_non_disponibile_mantiene_ordine(self):
        rr = self._broken_reranker()
        assert rr._model is None

        cands = [_result(f"d{i}") for i in range(5)]
        out = rr.rerank("query", cands, top_k=3)

        assert [r.doc_id for r in out] == ["d0", "d1", "d2"]

    def test_predict_fallito_mantiene_ordine(self):
        with patch("sentence_transformers.CrossEncoder") as MockCE:
            model = MagicMock()
            model.predict.side_effect = RuntimeError("CUDA boom")
            MockCE.return_value = model
            rr = CrossEncoderReranker()

        cands = [_result(f"d{i}") for i in range(4)]
        out = rr.rerank("query", cands, top_k=4)
        assert [r.doc_id for r in out] == ["d0", "d1", "d2", "d3"]

    def test_candidati_vuoti(self):
        rr = self._broken_reranker()
        assert rr.rerank("query", [], top_k=5) == []


# ---------------------------------------------------------------------------
# Test con modello reale (richiede download ~470MB) — opt-in
# ---------------------------------------------------------------------------

@pytest.mark.skipif(
    os.getenv("AIURA_TEST_RERANKER") != "1",
    reason="richiede il download del modello mmarco (~470MB) — attiva con AIURA_TEST_RERANKER=1",
)
@pytest.mark.slow
def test_rerank_reale_query_italiana():
    rr = CrossEncoderReranker()
    assert rr._model is not None, "modello mmarco non caricabile"

    cands = [
        _result("pertinente", full_text="La clausola penale manifestamente eccessiva può essere ridotta dal giudice ai sensi dell'art. 1384 c.c."),
        _result("non_pertinente", full_text="Il contratto di trasporto aereo internazionale è regolato dalla Convenzione di Montreal."),
    ]
    out = rr.rerank("riduzione della clausola penale eccessiva", cands, top_k=2)

    assert out[0].doc_id == "pertinente"
