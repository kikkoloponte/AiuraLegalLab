"""
Test fusione RRF — chiave di fusione condivisa tra BM25 e Vector.

Bug storico: BM25 ritorna l'_id Mongo, Qdrant l'UUID v5 derivato — le chiavi
non collidevano mai e lo stesso chunk produceva 2 risultati (interleaving
invece di fusione). _fusion_key normalizza entrambi allo stesso UUID.
"""
from __future__ import annotations

from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever, _fusion_key
from aiura_legal.core.retrieval.vector_retriever import _to_qdrant_id
from aiura_legal.core.types import SearchResult

_MONGO_ID = "507f1f77bcf86cd799439011"
_MONGO_ID_2 = "507f1f77bcf86cd799439022"
_JDOC_ID = "e65a598d71052357_massima"


def _bm25_result(doc_id: str, rank_score: float = 5.0) -> SearchResult:
    return SearchResult(
        doc_id=doc_id,
        score=rank_score,
        snippet="snippet bm25",
        source_id=f"urn:nir:{doc_id}",
        metadata={"corpus": "normattiva"},
        retrieval_method="bm25",
    )


def _vector_result(doc_id: str, score: float = 0.9) -> SearchResult:
    return SearchResult(
        doc_id=doc_id,
        score=score,
        snippet="snippet vector",
        source_id=f"urn:nir:{doc_id}",
        metadata={"corpus": "normattiva"},
        retrieval_method="vector",
    )


# ---------------------------------------------------------------------------
# _fusion_key
# ---------------------------------------------------------------------------

class TestFusionKey:
    def test_mongo_id_e_uuid_qdrant_collidono(self):
        """L'_id Mongo (BM25) e l'UUID Qdrant legacy (Vector) → stessa chiave."""
        assert _fusion_key(_MONGO_ID) == _fusion_key(_to_qdrant_id(_MONGO_ID))

    def test_jdoc_id_e_uuid_qdrant_collidono(self):
        """ID giurisprudenza hex16_tipo → stessa chiave dell'UUID derivato."""
        assert _fusion_key(_JDOC_ID) == _fusion_key(_to_qdrant_id(_JDOC_ID))

    def test_id_diversi_chiavi_diverse(self):
        assert _fusion_key(_MONGO_ID) != _fusion_key(_MONGO_ID_2)

    def test_uuid_case_insensitive(self):
        uid = _to_qdrant_id(_MONGO_ID)
        assert _fusion_key(uid.upper()) == _fusion_key(uid.lower())


# ---------------------------------------------------------------------------
# _rrf_fuse
# ---------------------------------------------------------------------------

class TestRrfFuse:
    def test_stesso_chunk_bm25_e_vector_fuso_in_uno(self):
        """Stesso chunk da BM25 (Mongo _id) e Vector (UUID legacy) → 1 risultato
        con score RRF combinato, doc_id originale preservato."""
        bm25 = [_bm25_result(_MONGO_ID)]
        vector = [_vector_result(_to_qdrant_id(_MONGO_ID))]

        fused = HybridRetriever._rrf_fuse(bm25, vector, [], 0.5, 0.5, 0.0)

        assert len(fused) == 1
        r = fused[0]
        # Il doc_id esposto resta l'ID originale (S5 reviewer/frontend)
        assert r.doc_id == _MONGO_ID
        assert r.retrieval_method == "hybrid_rrf"
        # Score = somma dei contributi RRF dei due retriever (rank 0 in entrambi)
        expected = 0.5 * (1.0 / 61) + 0.5 * (1.0 / 61)
        assert abs(r.score - expected) < 1e-9

    def test_stesso_chunk_con_mongo_id_da_entrambi(self):
        """Punti Qdrant nuovi: Vector ritorna già il mongo_id → fusione diretta."""
        bm25 = [_bm25_result(_MONGO_ID)]
        vector = [_vector_result(_MONGO_ID)]

        fused = HybridRetriever._rrf_fuse(bm25, vector, [], 0.5, 0.5, 0.0)

        assert len(fused) == 1
        assert fused[0].doc_id == _MONGO_ID

    def test_nessun_duplicato_per_doc(self):
        """Mix di chunk condivisi e unici → nessun doc duplicato nel risultato."""
        bm25 = [_bm25_result(_MONGO_ID), _bm25_result(_MONGO_ID_2)]
        vector = [
            _vector_result(_to_qdrant_id(_MONGO_ID)),   # duplicato di bm25[0]
            _vector_result(_JDOC_ID),                    # unico
        ]

        fused = HybridRetriever._rrf_fuse(bm25, vector, [], 0.5, 0.5, 0.0)

        assert len(fused) == 3
        keys = [_fusion_key(r.doc_id) for r in fused]
        assert len(keys) == len(set(keys)), "doc duplicati dopo la fusione"

    def test_chunk_condiviso_batte_chunk_singolo(self):
        """Un chunk presente in entrambi i retriever (rank basso) deve superare
        un chunk presente in uno solo allo stesso rank."""
        bm25 = [_bm25_result(_MONGO_ID), _bm25_result(_MONGO_ID_2)]
        vector = [_vector_result(_to_qdrant_id(_MONGO_ID))]

        fused = HybridRetriever._rrf_fuse(bm25, vector, [], 0.5, 0.5, 0.0)

        assert fused[0].doc_id == _MONGO_ID, (
            "il chunk confermato da entrambi i retriever deve avere score maggiore"
        )

    def test_pesi_influenzano_ordinamento(self):
        """Con w_vec >> w_bm25 il top-1 vector deve superare il top-1 bm25 (e viceversa)."""
        bm25 = [_bm25_result(_MONGO_ID)]
        vector = [_vector_result(_MONGO_ID_2)]

        fused_vec_heavy = HybridRetriever._rrf_fuse(bm25, vector, [], 0.1, 0.9, 0.0)
        assert fused_vec_heavy[0].doc_id == _MONGO_ID_2

        fused_bm25_heavy = HybridRetriever._rrf_fuse(bm25, vector, [], 0.9, 0.1, 0.0)
        assert fused_bm25_heavy[0].doc_id == _MONGO_ID

    def test_graph_results_usano_la_stessa_chiave(self):
        """Anche i risultati graph (ID originale) si fondono con vector legacy."""
        graph = [_bm25_result(_MONGO_ID)]
        graph[0].retrieval_method = "graph"
        vector = [_vector_result(_to_qdrant_id(_MONGO_ID))]

        fused = HybridRetriever._rrf_fuse([], vector, graph, 0.0, 0.5, 0.5)

        assert len(fused) == 1
        assert fused[0].doc_id in (_MONGO_ID, _to_qdrant_id(_MONGO_ID))
