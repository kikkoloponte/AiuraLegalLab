"""
CrossEncoder Reranker — cross-encoder/ms-marco-MiniLM-L-6-v2.
Target latenza: < 300ms su CPU per top_k <= 15.
"""
from __future__ import annotations
from loguru import logger
from aiura_legal.core.types import SearchResult

_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class CrossEncoderReranker:

    def __init__(self, model_name: str = _RERANKER_MODEL) -> None:
        self._model = None
        self._model_name = model_name
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

        pairs = [(query, c.snippet) for c in candidates]
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
