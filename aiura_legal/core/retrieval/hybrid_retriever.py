"""
Hybrid Retriever — RRF fusion di BM25 + Vector + CrossEncoder reranking.
Weight profiles per QueryIntent.

Ottimizzazioni latenza:
  - BM25 e Vector parallelizzati con ThreadPoolExecutor dentro ogni round
  - I due round bifasico parallelizzati con concurrent.futures.wait
  - L'intera pipeline può essere eseguita in asyncio.to_thread dall'orchestrator
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Optional
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.core.types import Document, QueryIntent, ResearchPacket, SearchResult
from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.core.retrieval.reranker import CrossEncoderReranker
from aiura_legal.core.graph.retriever import GraphRetriever


class RetrievalSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    retrieval_top_k_retrieve: int = 20
    retrieval_top_k_rerank:   int = 6


_retrieval_settings = RetrievalSettings()

# RRF constant (k=60 è lo standard)
_RRF_K = 60

# Weight profiles: (bm25, vector, graph)
# graph=0.0 se GraphRetriever non disponibile (graceful degradation automatica)
_INTENT_WEIGHTS: dict[QueryIntent, tuple[float, float, float]] = {
    QueryIntent.NORMA_LOOKUP:           (0.55, 0.25, 0.20),
    QueryIntent.GIURISPRUDENZA_SEARCH:  (0.20, 0.70, 0.10),
    QueryIntent.FATTISPECIE_ANALYSIS:   (0.25, 0.60, 0.15),
    QueryIntent.NORMA_EVOLUTION:        (0.40, 0.35, 0.25),
    QueryIntent.RISCHIO_CONTRATTUALE:   (0.35, 0.55, 0.10),
    QueryIntent.PRECEDENTE_INTERNO:     (0.30, 0.60, 0.10),
}


_WEIGHTS_NORMATIVA      = (0.65, 0.20, 0.15)   # BM25-heavy: per round normativa
_WEIGHTS_GIURISPRUDENZA = (0.15, 0.75, 0.10)   # Vector-heavy: per round giurisprudenza
_WEIGHTS_DOTTRINA       = (0.40, 0.50, 0.10)   # Bilanciato: dottrina richiede sia terminologia (BM25) che semantica (Vector)
_FILTER_NORMATIVA       = {"corpus": "normattiva"}
_FILTER_GIURISPRUDENZA  = {"corpus": "giurisprudenza"}
_FILTER_DOTTRINA        = {"corpus": "dottrina"}
_BIFASICO_INTENTS = {
    QueryIntent.FATTISPECIE_ANALYSIS,
    QueryIntent.RISCHIO_CONTRATTUALE,
    QueryIntent.NORMA_EVOLUTION,
    QueryIntent.PRECEDENTE_INTERNO,
}


def _rrf_score(rank: int, k: int = _RRF_K) -> float:
    return 1.0 / (k + rank + 1)


class HybridRetriever:
    """
    Orchestrates BM25 + Vector retrieval with RRF fusion,
    then applies CrossEncoder reranking.
    """

    def __init__(self, workspace_path: str) -> None:
        self.bm25 = BM25Retriever(workspace_path)
        self.vector = VectorRetriever(workspace_path)
        self.reranker = CrossEncoderReranker()
        self.graph = GraphRetriever(workspace_path)

    def search(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        top_k_retrieve: int = 0,   # 0 = usa valore da env (RETRIEVAL_TOP_K_RETRIEVE)
        top_k_rerank: int = 0,     # 0 = usa valore da env (RETRIEVAL_TOP_K_RERANK)
        valid_on: Optional[date] = None,
        chunk_filter: Optional[dict] = None,
    ) -> list[SearchResult]:
        """
        Pipeline completa:
          1. BM25 search
          2. Vector search
          3. RRF fusion con weights per intent
          4. CrossEncoder reranking → top_k_rerank

        Args:
            chunk_filter: filtro subset opzionale propagato a BM25 e Vector.
                          Esempio: {"corpus": "normattiva", "fonte": "codice_civile"}
                          None = nessun filtro (comportamento invariato)
        """
        # Legge da env se non specificato esplicitamente
        if top_k_retrieve == 0:
            top_k_retrieve = _retrieval_settings.retrieval_top_k_retrieve
        if top_k_rerank == 0:
            top_k_rerank = _retrieval_settings.retrieval_top_k_rerank

        w_bm25, w_vec, w_graph = _INTENT_WEIGHTS.get(intent, (0.45, 0.45, 0.10))

        bm25_results = self.bm25.search(query, top_k=top_k_retrieve, chunk_filter=chunk_filter)
        vector_results = self.vector.search(query, top_k=top_k_retrieve, valid_on=valid_on, chunk_filter=chunk_filter)

        # Graph expansion — attiva solo se graph.json disponibile
        graph_results: list[SearchResult] = []
        if self.graph.is_available:
            top_ids = [r.source_id for r in (bm25_results + vector_results)[:top_k_retrieve]]
            graph_results = self.graph.expand(
                top_ids, depth=1, max_nodes=top_k_retrieve, valid_on=valid_on
            )

        logger.debug(
            f"Hybrid [{intent.value}]: BM25={len(bm25_results)}, "
            f"Vector={len(vector_results)}, Graph={len(graph_results)}"
        )

        fused = self._rrf_fuse(
            bm25_results, vector_results, graph_results, w_bm25, w_vec, w_graph
        )
        reranked = self.reranker.rerank(query, fused, top_k=top_k_rerank)
        return reranked

    def build_research_packet(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        valid_on: Optional[date] = None,
        chunk_filter: Optional[dict] = None,
    ) -> ResearchPacket:
        sources = self.search(query, intent=intent, valid_on=valid_on, chunk_filter=chunk_filter)
        confidence = (
            "HIGH" if len(sources) >= 5
            else "MEDIUM" if len(sources) >= 2
            else "LOW"
        )
        return ResearchPacket(
            query_original=query,
            query_intent=intent,
            sources=sources,
            retrieval_confidence=confidence,
            gaps=[] if sources else ["Nessun documento trovato per la query"],
        )

    # ------------------------------------------------------------------
    # Bifasico retrieval (norme + giurisprudenza in round separati)
    # ------------------------------------------------------------------

    def build_research_packet_bifasico(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        valid_on: Optional[date] = None,
        top_k_rerank: int = 0,   # 0 = usa valore da env (RETRIEVAL_TOP_K_RERANK)
    ) -> ResearchPacket:
        """
        Due round separati: normativa (BM25-heavy) poi giurisprudenza (vector-heavy).
        Ogni SearchResult viene taggato con source_layer = "normativa"|"giurisprudenza".
        Intenti mono-layer delegano a search() con filtro corpus appropriato.

        Nota: i documenti giurisprudenziali devono avere corpus="giurisprudenza" nei
        metadata (impostato da JurisprudenceCoordinator.to_chunks()). Documenti
        indicizzati prima di questa versione restituiranno round 2 vuoto — degradazione
        graceful: il packet conterrà solo fonti normative.
        """
        if top_k_rerank == 0:
            top_k_rerank = _retrieval_settings.retrieval_top_k_rerank

        if intent == QueryIntent.NORMA_LOOKUP:
            sources = self.search(query, intent=intent, valid_on=valid_on,
                                  chunk_filter=_FILTER_NORMATIVA,
                                  top_k_rerank=top_k_rerank * 2)
            for s in sources:
                s.source_layer = "normativa"
            return self._make_packet(query, intent, sources)

        if intent == QueryIntent.GIURISPRUDENZA_SEARCH:
            sources = self.search(query, intent=intent, valid_on=valid_on,
                                  chunk_filter=_FILTER_GIURISPRUDENZA,
                                  top_k_rerank=top_k_rerank * 2)
            for s in sources:
                s.source_layer = "giurisprudenza"
            return self._make_packet(query, intent, sources)

        # I due round sono indipendenti: li eseguiamo in parallelo
        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_norm = pool.submit(
                self._search_round,
                query, _WEIGHTS_NORMATIVA, _FILTER_NORMATIVA, valid_on, 20, top_k_rerank,
            )
            fut_giuri = pool.submit(
                self._search_round,
                query, _WEIGHTS_GIURISPRUDENZA, _FILTER_GIURISPRUDENZA, valid_on, 20, top_k_rerank,
            )
            norm_sources  = fut_norm.result()
            giuri_sources = fut_giuri.result()

        for s in norm_sources:
            s.source_layer = "normativa"
        for s in giuri_sources:
            s.source_layer = "giurisprudenza"

        return self._make_packet(query, intent, norm_sources + giuri_sources)

    def _search_round(
        self,
        query: str,
        weights: tuple[float, float, float],
        chunk_filter: Optional[dict],
        valid_on: Optional[date],
        top_k_retrieve: int,
        top_k_rerank: int,
    ) -> list[SearchResult]:
        """BM25 e Vector girano in parallelo su thread separati."""
        w_bm25, w_vec, w_graph = weights

        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_bm25 = pool.submit(
                self.bm25.search, query, top_k_retrieve, chunk_filter
            )
            fut_vec = pool.submit(
                self.vector.search, query, top_k_retrieve, valid_on, chunk_filter
            )
            bm25_res   = fut_bm25.result()
            vector_res = fut_vec.result()

        graph_res: list[SearchResult] = []
        if self.graph.is_available:
            top_ids = [r.source_id for r in (bm25_res + vector_res)[:top_k_retrieve]]
            graph_res = self.graph.expand(
                top_ids, depth=1, max_nodes=top_k_retrieve, valid_on=valid_on
            )
        fused = self._rrf_fuse(bm25_res, vector_res, graph_res, w_bm25, w_vec, w_graph)
        return self.reranker.rerank(query, fused, top_k=top_k_rerank)

    @staticmethod
    def _make_packet(
        query: str, intent: QueryIntent, sources: list[SearchResult]
    ) -> ResearchPacket:
        confidence = (
            "HIGH" if len(sources) >= 5
            else "MEDIUM" if len(sources) >= 2
            else "LOW"
        )
        return ResearchPacket(
            query_original=query,
            query_intent=intent,
            sources=sources,
            retrieval_confidence=confidence,
            gaps=[] if sources else ["Nessun documento trovato per la query"],
        )

    # ------------------------------------------------------------------
    # RRF Fusion
    # ------------------------------------------------------------------

    @staticmethod
    def _rrf_fuse(
        bm25_results: list[SearchResult],
        vector_results: list[SearchResult],
        graph_results: list[SearchResult],
        w_bm25: float,
        w_vec: float,
        w_graph: float,
    ) -> list[SearchResult]:
        scores: dict[str, float] = {}
        best_result: dict[str, SearchResult] = {}

        for rank, r in enumerate(bm25_results):
            rrf = w_bm25 * _rrf_score(rank)
            scores[r.doc_id] = scores.get(r.doc_id, 0.0) + rrf
            best_result[r.doc_id] = r

        for rank, r in enumerate(vector_results):
            rrf = w_vec * _rrf_score(rank)
            scores[r.doc_id] = scores.get(r.doc_id, 0.0) + rrf
            if r.doc_id not in best_result:
                best_result[r.doc_id] = r

        for rank, r in enumerate(graph_results):
            rrf = w_graph * _rrf_score(rank)
            scores[r.doc_id] = scores.get(r.doc_id, 0.0) + rrf
            if r.doc_id not in best_result:
                best_result[r.doc_id] = r

        fused: list[SearchResult] = []
        for doc_id, fused_score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            r = best_result[doc_id]
            r.score = fused_score
            r.retrieval_method = "hybrid_rrf"
            fused.append(r)

        return fused
