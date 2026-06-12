"""
CrossEncoder Reranker — modello configurabile via env RERANKER_MODEL.

Default: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1 (mMARCO multilingue,
italiano incluso) — il precedente ms-marco-MiniLM-L-6-v2 era addestrato
solo su MS MARCO inglese e penalizzava il testo giuridico italiano.

Input del rerank: full_text (troncato a ~510 token, il limite di contesto
dei cross-encoder MiniLM) se disponibile, altrimenti lo snippet.

Target latenza: < 500ms su CPU per top_k <= 15.
"""
from __future__ import annotations
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.core.retrieval.context_budget import _truncate_to_tokens
from aiura_legal.core.types import SearchResult

_DEFAULT_RERANKER_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

# Limite input dei cross-encoder MiniLM (512 token, margine per i token speciali)
_RERANK_MAX_TOKENS = 510


class RerankerSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    reranker_model: str = _DEFAULT_RERANKER_MODEL


_reranker_settings = RerankerSettings()


def _rerank_input(c: SearchResult) -> str:
    """Testo passato al cross-encoder: full_text troncato se disponibile, altrimenti snippet."""
    if c.full_text:
        return _truncate_to_tokens(c.full_text, _RERANK_MAX_TOKENS)
    return c.snippet


class CrossEncoderReranker:

    def __init__(self, model_name: str = "") -> None:
        self._model = None
        self._model_name = model_name or _reranker_settings.reranker_model
        self._load_model()

    def _load_model(self) -> None:
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self._model_name)
            logger.info(f"CrossEncoder caricato: {self._model_name}")
        except Exception as e:
            logger.warning(f"CrossEncoder non disponibile ({e}). Reranking disabilitato.")

    def rerank(
        self,
        query: str,
        candidates: list[SearchResult],
        top_k: int = 7,
    ) -> list[SearchResult]:
        """
        Ri-ordina i candidati con il cross-encoder.
        Se il modello non è disponibile, ritorna i candidati nell'ordine originale.
        """
        if not candidates:
            return []

        if self._model is None:
            logger.debug("Reranker non disponibile — ordine originale mantenuto")
            return candidates[:top_k]

        pairs = [(query, _rerank_input(c)) for c in candidates]
        try:
            scores = self._model.predict(pairs)
        except Exception as e:
            logger.error(f"CrossEncoder predict fallito: {e}")
            return candidates[:top_k]

        reranked = sorted(
            zip(scores, candidates),
            key=lambda x: x[0],
            reverse=True,
        )
        result = []
        for score, candidate in reranked[:top_k]:
            candidate.score = float(score)
            result.append(candidate)
        return result
