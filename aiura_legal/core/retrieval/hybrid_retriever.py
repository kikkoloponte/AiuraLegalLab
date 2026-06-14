"""
Hybrid Retriever — RRF fusion di BM25 + Vector + CrossEncoder reranking.
Weight profiles per QueryIntent.

Ottimizzazioni latenza:
  - BM25 e Vector parallelizzati con ThreadPoolExecutor dentro ogni round
  - I due round bifasico parallelizzati con concurrent.futures.wait
  - L'intera pipeline può essere eseguita in asyncio.to_thread dall'orchestrator
"""
from __future__ import annotations
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from typing import Optional
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.core.types import Document, QueryIntent, ResearchPacket, SearchResult
from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever, _to_qdrant_id
from aiura_legal.core.retrieval.reranker import CrossEncoderReranker
from aiura_legal.core.graph.retriever import GraphRetriever
from aiura_legal.core.retrieval.debug_log import rlog, rlog_sources


class RetrievalSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    retrieval_top_k_retrieve: int = 20
    retrieval_top_k_rerank:   int = 6
    # Soglia score reranker per contare una fonte come "forte" nella confidence.
    # I cross-encoder mmarco producono logit (anche negativi): 0.0 è il punto
    # medio della sigmoide — score > 0 ≈ probabilità di rilevanza > 50%.
    # Da ricalibrare empiricamente dopo l'eval (env RETRIEVAL_SCORE_THRESHOLD).
    retrieval_score_threshold: float = 0.0


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
    QueryIntent.NORMA_LOOKUP,           # corpus normattiva filtrato (fix corpus dilution)
    QueryIntent.GIURISPRUDENZA_SEARCH,  # corpus giurisprudenza filtrato
    QueryIntent.FATTISPECIE_ANALYSIS,
    QueryIntent.RISCHIO_CONTRATTUALE,
    QueryIntent.NORMA_EVOLUTION,
    QueryIntent.PRECEDENTE_INTERNO,
}


def _rrf_score(rank: int, k: int = _RRF_K) -> float:
    return 1.0 / (k + rank + 1)


def _confidence_from_scores(sources: list[SearchResult]) -> str:
    """
    Confidence del retrieval basata sugli score, non sul solo conteggio:
      HIGH   — almeno 3 fonti con score reranker sopra la soglia
      MEDIUM — almeno 2 fonti (qualunque score)
      LOW    — altrimenti
    """
    threshold = _retrieval_settings.retrieval_score_threshold
    strong = sum(1 for s in sources if s.score > threshold)
    if strong >= 3:
        return "HIGH"
    if len(sources) >= 2:
        return "MEDIUM"
    return "LOW"


_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
)


def _fusion_key(doc_id: str) -> str:
    """
    Chiave di fusione RRF uniforme tra retriever.

    BM25 e graph ritornano l'ID originale (Mongo _id 24-hex o jdoc "hex16_tipo");
    Qdrant ritorna UUID v5 derivato da quell'ID (punti legacy senza mongo_id nel
    payload) oppure l'ID originale (punti nuovi). Convertendo gli ID non-UUID
    con _to_qdrant_id, lo stesso chunk produce la stessa chiave da qualunque
    retriever provenga — i punteggi RRF si sommano invece di duplicarsi.

    NOTA: la chiave è solo interna alla fusione. SearchResult.doc_id resta
    l'ID originale (S5 reviewer e frontend ne dipendono).
    """
    if _UUID_RE.match(doc_id):
        return doc_id.lower()
    return _to_qdrant_id(doc_id)


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
        workspace: Optional[str] = None,
    ) -> list[SearchResult]:
        """
        Pipeline completa:
          1. BM25 search
          2. Vector search (con filtro workspace opzionale)
          3. RRF fusion con weights per intent
          4. CrossEncoder reranking → top_k_rerank

        Args:
            chunk_filter: filtro subset opzionale propagato a BM25 e Vector.
            workspace:    se passato, limita il vector search ai punti del workspace
                          (compat con punti legacy senza campo workspace — IsEmpty).
        """
        # Legge da env se non specificato esplicitamente
        if top_k_retrieve == 0:
            top_k_retrieve = _retrieval_settings.retrieval_top_k_retrieve
        if top_k_rerank == 0:
            top_k_rerank = _retrieval_settings.retrieval_top_k_rerank

        w_bm25, w_vec, w_graph = _INTENT_WEIGHTS.get(intent, (0.45, 0.45, 0.10))

        rlog("HYBRID:search:start",
             f"intent={intent.value} filter={chunk_filter} ws={workspace} "
             f"top_k_ret={top_k_retrieve} top_k_rerank={top_k_rerank} "
             f"w=(bm25={w_bm25}, vec={w_vec}, graph={w_graph})")

        bm25_results = self.bm25.search(query, top_k=top_k_retrieve, chunk_filter=chunk_filter)
        rlog("HYBRID:search:bm25_done", f"→ {len(bm25_results)} risultati")
        rlog_sources("HYBRID:search:bm25_top", bm25_results)

        vector_results = self.vector.search(
            query, top_k=top_k_retrieve, valid_on=valid_on,
            chunk_filter=chunk_filter, workspace=workspace,
        )
        rlog("HYBRID:search:vector_done", f"→ {len(vector_results)} risultati")
        rlog_sources("HYBRID:search:vector_top", vector_results)

        # Graph expansion — attiva solo se graph.json disponibile
        graph_results: list[SearchResult] = []
        if self.graph.is_available:
            top_ids = [r.source_id for r in (bm25_results + vector_results)[:top_k_retrieve]]
            graph_results = self.graph.expand(
                top_ids, depth=1, max_nodes=top_k_retrieve, valid_on=valid_on
            )
            rlog("HYBRID:search:graph_done", f"→ {len(graph_results)} risultati")

        logger.debug(
            f"Hybrid [{intent.value}]: BM25={len(bm25_results)}, "
            f"Vector={len(vector_results)}, Graph={len(graph_results)}"
        )

        fused = self._rrf_fuse(
            bm25_results, vector_results, graph_results, w_bm25, w_vec, w_graph
        )
        rlog("HYBRID:search:rrf_done", f"→ {len(fused)} unici dopo fusione")
        rlog_sources("HYBRID:search:rrf_top", fused)

        reranked = self.reranker.rerank(query, fused, top_k=top_k_rerank)
        rlog("HYBRID:search:rerank_done", f"→ {len(reranked)} fonti finali")
        rlog_sources("HYBRID:search:final", reranked)
        return reranked

    def build_research_packet(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        valid_on: Optional[date] = None,
        chunk_filter: Optional[dict] = None,
        workspace: Optional[str] = None,
    ) -> ResearchPacket:
        sources = self.search(
            query, intent=intent, valid_on=valid_on,
            chunk_filter=chunk_filter, workspace=workspace,
        )
        return self._make_packet(query, intent, sources)

    # ------------------------------------------------------------------
    # Bifasico retrieval (norme + giurisprudenza in round separati)
    # ------------------------------------------------------------------

    def build_research_packet_bifasico(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        valid_on: Optional[date] = None,
        top_k_rerank: int = 0,   # 0 = usa valore da env (RETRIEVAL_TOP_K_RERANK)
        workspace: Optional[str] = None,
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

        rlog("BIFASICO:entry", f"intent={intent.value} top_k_rerank={top_k_rerank} ws={workspace}")

        if intent == QueryIntent.NORMA_LOOKUP:
            rlog("BIFASICO:routing", "→ NORMA_LOOKUP: mono-round corpus=normattiva (BM25-heavy)")
            sources = self.search(query, intent=intent, valid_on=valid_on,
                                  chunk_filter=_FILTER_NORMATIVA,
                                  top_k_rerank=top_k_rerank * 2, workspace=workspace)
            for s in sources:
                s.source_layer = "normativa"
            rlog("BIFASICO:done", f"NORMA_LOOKUP → {len(sources)} fonti normativa")
            return self._make_packet(query, intent, sources)

        if intent == QueryIntent.GIURISPRUDENZA_SEARCH:
            rlog("BIFASICO:routing", "→ GIURISPRUDENZA_SEARCH: mono-round corpus=giurisprudenza (vector-heavy)")
            sources = self.search(query, intent=intent, valid_on=valid_on,
                                  chunk_filter=_FILTER_GIURISPRUDENZA,
                                  top_k_rerank=top_k_rerank * 2, workspace=workspace)
            for s in sources:
                s.source_layer = "giurisprudenza"
            rlog("BIFASICO:done", f"GIURISPRUDENZA_SEARCH → {len(sources)} fonti giurisprudenza")
            return self._make_packet(query, intent, sources)

        # I due round sono indipendenti: li eseguiamo in parallelo
        rlog("BIFASICO:routing",
             f"→ {intent.value}: due round paralleli normativa + giurisprudenza")
        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_norm = pool.submit(
                self._search_round,
                query, _WEIGHTS_NORMATIVA, _FILTER_NORMATIVA, valid_on, 20, top_k_rerank,
                workspace,
            )
            fut_giuri = pool.submit(
                self._search_round,
                query, _WEIGHTS_GIURISPRUDENZA, _FILTER_GIURISPRUDENZA, valid_on, 20, top_k_rerank,
                workspace,
            )
            norm_sources  = fut_norm.result()
            giuri_sources = fut_giuri.result()

        for s in norm_sources:
            s.source_layer = "normativa"
        for s in giuri_sources:
            s.source_layer = "giurisprudenza"

        rlog("BIFASICO:done",
             f"{intent.value} → norm={len(norm_sources)} giuri={len(giuri_sources)} "
             f"tot={len(norm_sources)+len(giuri_sources)}")
        return self._make_packet(query, intent, norm_sources + giuri_sources)

    def _search_round(
        self,
        query: str,
        weights: tuple[float, float, float],
        chunk_filter: Optional[dict],
        valid_on: Optional[date],
        top_k_retrieve: int,
        top_k_rerank: int,
        workspace: Optional[str] = None,
    ) -> list[SearchResult]:
        """BM25 e Vector girano in parallelo su thread separati."""
        w_bm25, w_vec, w_graph = weights
        corpus_tag = (chunk_filter or {}).get("corpus", "all")

        rlog(f"ROUND:{corpus_tag}:start",
             f"filter={chunk_filter} w=(bm25={w_bm25}, vec={w_vec}, graph={w_graph}) "
             f"top_k_ret={top_k_retrieve} top_k_rerank={top_k_rerank}")

        with ThreadPoolExecutor(max_workers=2) as pool:
            fut_bm25 = pool.submit(
                self.bm25.search, query, top_k_retrieve, chunk_filter
            )
            fut_vec = pool.submit(
                self.vector.search, query, top_k_retrieve, valid_on, chunk_filter,
                workspace,
            )
            bm25_res   = fut_bm25.result()
            vector_res = fut_vec.result()

        rlog(f"ROUND:{corpus_tag}:bm25", f"→ {len(bm25_res)} risultati")
        rlog_sources(f"ROUND:{corpus_tag}:bm25_top", bm25_res)
        rlog(f"ROUND:{corpus_tag}:vector", f"→ {len(vector_res)} risultati")
        rlog_sources(f"ROUND:{corpus_tag}:vector_top", vector_res)

        graph_res: list[SearchResult] = []
        if self.graph.is_available:
            top_ids = [r.source_id for r in (bm25_res + vector_res)[:top_k_retrieve]]
            graph_res = self.graph.expand(
                top_ids, depth=1, max_nodes=top_k_retrieve, valid_on=valid_on
            )
            rlog(f"ROUND:{corpus_tag}:graph", f"→ {len(graph_res)} risultati")

        fused = self._rrf_fuse(bm25_res, vector_res, graph_res, w_bm25, w_vec, w_graph)
        rlog(f"ROUND:{corpus_tag}:rrf", f"→ {len(fused)} unici dopo fusione")
        rlog_sources(f"ROUND:{corpus_tag}:rrf_top", fused)

        reranked = self.reranker.rerank(query, fused, top_k=top_k_rerank)
        rlog(f"ROUND:{corpus_tag}:rerank", f"→ {len(reranked)} fonti finali")
        rlog_sources(f"ROUND:{corpus_tag}:final", reranked)
        return reranked

    @staticmethod
    def _make_packet(
        query: str, intent: QueryIntent, sources: list[SearchResult]
    ) -> ResearchPacket:
        confidence = _confidence_from_scores(sources)
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
        """
        Fonde i risultati con Reciprocal Rank Fusion.

        La chiave di fusione è l'UUID Qdrant derivato dall'ID originale
        (_fusion_key): lo stesso chunk ritornato da BM25 e Vector somma i
        punteggi RRF in un unico risultato. Il SearchResult mantenuto è il
        primo incontrato in ordine BM25 → Vector → Graph, così doc_id resta
        l'ID originale quando disponibile.
        """
        scores: dict[str, float] = {}
        best_result: dict[str, SearchResult] = {}

        for rank, r in enumerate(bm25_results):
            key = _fusion_key(r.doc_id)
            scores[key] = scores.get(key, 0.0) + w_bm25 * _rrf_score(rank)
            best_result[key] = r

        for rank, r in enumerate(vector_results):
            key = _fusion_key(r.doc_id)
            scores[key] = scores.get(key, 0.0) + w_vec * _rrf_score(rank)
            if key not in best_result:
                best_result[key] = r

        for rank, r in enumerate(graph_results):
            key = _fusion_key(r.doc_id)
            scores[key] = scores.get(key, 0.0) + w_graph * _rrf_score(rank)
            if key not in best_result:
                best_result[key] = r

        fused: list[SearchResult] = []
        for key, fused_score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            r = best_result[key]
            r.score = fused_score
            r.retrieval_method = "hybrid_rrf"
            fused.append(r)

        rlog("RRF:fuse",
             f"input: bm25={len(bm25_results)} vec={len(vector_results)} "
             f"graph={len(graph_results)} → fused={len(fused)} unici  "
             f"w=(bm25={w_bm25}, vec={w_vec}, graph={w_graph})")
        return fused
