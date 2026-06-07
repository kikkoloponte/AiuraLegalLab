"""
PhaseRetriever — retrieval mirato per fase nel Sequential IQRAC.

Wrapper leggero su HybridRetriever che esegue re-query focalizzate
per corpus specifico (normattiva o giurisprudenza), usando la query
distillata dalla fase precedente invece della query originale grezza.

Usato da SequentialAnalyst nelle fasi 2 (normativa) e 3 (giurisprudenza).
"""
from __future__ import annotations

from loguru import logger

from aiura_legal.core.retrieval.hybrid_retriever import (
    HybridRetriever,
    _WEIGHTS_NORMATIVA,
    _WEIGHTS_GIURISPRUDENZA,
    _WEIGHTS_DOTTRINA,
    _FILTER_NORMATIVA,
    _FILTER_GIURISPRUDENZA,
    _FILTER_DOTTRINA,
)
from aiura_legal.core.types import SearchResult


class PhaseRetriever:
    """
    Esegue retrieval mirato per singola fase IQRAC.

    Le query di fase sono più precise della query originale:
    vengono estratte dall'output della Fase 1 (QUESTIONE, QUALIFICAZIONE)
    e usate per recuperare fonti più pertinenti.
    """

    def __init__(self, retriever: HybridRetriever) -> None:
        self._retriever = retriever

    def retrieve_normativa(
        self,
        query: str,
        top_k: int = 6,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=normattiva con pesi BM25-heavy.
        Usa la QUESTIONE distillata dalla Fase 1 come query.
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query normativa vuota — skip")
            return []

        logger.info(f"[PhaseRetriever] normativa re-query: {query[:80]!r}")
        results = self._retriever._search_round(
            query=query,
            weights=_WEIGHTS_NORMATIVA,
            chunk_filter=_FILTER_NORMATIVA,
            valid_on=None,
            top_k_retrieve=15,
            top_k_rerank=top_k,
        )
        for r in results:
            r.source_layer = "normativa"
        logger.info(f"[PhaseRetriever] normativa: {len(results)} fonti")
        return results

    def retrieve_giurisprudenza(
        self,
        query: str,
        top_k: int = 6,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=giurisprudenza con pesi Vector-heavy.
        Usa QUALIFICAZIONE+QUESTIONE dalla Fase 1 come query.
        """
        if not query.strip():
            logger.warning("[PhaseRetriever] query giurisprudenza vuota — skip")
            return []

        logger.info(f"[PhaseRetriever] giurisprudenza re-query: {query[:80]!r}")
        results = self._retriever._search_round(
            query=query,
            weights=_WEIGHTS_GIURISPRUDENZA,
            chunk_filter=_FILTER_GIURISPRUDENZA,
            valid_on=None,
            top_k_retrieve=15,
            top_k_rerank=top_k,
        )
        for r in results:
            r.source_layer = "giurisprudenza"
        logger.info(f"[PhaseRetriever] giurisprudenza: {len(results)} fonti")
        return results

    def retrieve_dottrina(
        self,
        query: str,
        top_k: int = 4,
    ) -> list[SearchResult]:
        """
        Re-query su corpus=dottrina con pesi bilanciati BM25+Vector.
        Usata nella Fase 2 (INTERPRETAZIONE) per citare manuali e commentari.
        Ritorna lista vuota (non errore) se nessun documento dottrinale è indicizzato.
        """
        if not query.strip():
            return []

        logger.info(f"[PhaseRetriever] dottrina re-query: {query[:80]!r}")
        results = self._retriever._search_round(
            query=query,
            weights=_WEIGHTS_DOTTRINA,
            chunk_filter=_FILTER_DOTTRINA,
            valid_on=None,
            top_k_retrieve=10,
            top_k_rerank=top_k,
        )
        for r in results:
            r.source_layer = "dottrina"
        logger.info(f"[PhaseRetriever] dottrina: {len(results)} fonti")
        return results
