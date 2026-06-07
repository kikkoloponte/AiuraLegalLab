"""
Test retrieval: BM25, HybridRetriever (mock Vector/Reranker).
"""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from aiura_legal.core.types import Document, SearchResult, QueryIntent
from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever, _rrf_score


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------

_TOPICS = [
    "inadempimento obbligazione debitore",
    "appalto pubblico lavori opere infrastrutture",
    "responsabilita extracontrattuale risarcimento danni",
    "locazione immobile canone morosita",
    "fideiussione garanzia fideiussore",
    "sequestro conservativo cautelare beni",
    "diffida adempimento termine perentorio",
    "prescrizione acquistiva possesso usucapione",
    "nullita annullabilita vizi consenso",
    "risoluzione rescissione contratto inadempimento",
    "mora debitoris ritardo pagamento interessi",
    "cessione credito debitore ceduto",
    "ipoteca pegno garanzia reale immobiliare",
    "societa responsabilita limitata capitale",
    "matrimonio separazione divorzio assegno",
    "testamento eredita successione legittima",
    "brevetto marchio proprieta intellettuale",
    "fallimento insolvenza procedure concorsuali",
    "concorrenza sleale mercato antitrust",
    "danno biologico lesioni personali tabelle",
]


def _make_docs(n: int = 20) -> list[Document]:
    """Crea documenti con contenuto VARIO per garantire IDF positivo in BM25."""
    return [
        Document(
            id=f"doc_{i:03d}",
            text=f"Documento {i}: {_TOPICS[i % len(_TOPICS)]}. Diritto civile italiano.",
            source_id=f"DOC_SRC_{i}",
            metadata={"doc_type": "legge"},
        )
        for i in range(n)
    ]


@pytest.fixture
def ws(tmp_path) -> str:
    return str(tmp_path)


@pytest.fixture
def bm25(ws) -> BM25Retriever:
    r = BM25Retriever(ws)
    r.build(_make_docs(20))
    return r


# ------------------------------------------------------------------
# BM25
# ------------------------------------------------------------------

def test_bm25_search_returns_results(bm25):
    results = bm25.search("inadempimento obbligazione debitore", top_k=5)
    assert len(results) > 0
    assert all(isinstance(r, SearchResult) for r in results)


def test_bm25_results_have_scores(bm25):
    results = bm25.search("inadempimento obbligazione", top_k=5)
    for r in results:
        assert r.score > 0


def test_bm25_top_k_respected(bm25):
    results = bm25.search("articolo", top_k=3)
    assert len(results) <= 3


def test_bm25_retrieval_method(bm25):
    results = bm25.search("appalto lavori")
    for r in results:
        assert r.retrieval_method == "bm25"


def test_bm25_empty_index_returns_empty(ws):
    r = BM25Retriever(ws)
    results = r.search("qualsiasi query")
    assert results == []


def test_bm25_persist_reload(ws):
    docs = _make_docs(20)  # 20 doc con contenuto vario
    r1 = BM25Retriever(ws)
    r1.build(docs)
    pre_save = r1.search("inadempimento obbligazione", top_k=5)
    assert len(pre_save) > 0, "BM25 non trova nulla prima del save"
    r1.save()

    r2 = BM25Retriever(ws)  # auto-load
    results = r2.search("appalto lavori infrastrutture", top_k=5)
    assert len(results) > 0, f"BM25 caricato ma nessun risultato. Corpus: {len(r2._corpus)} doc"


def test_bm25_add_batch_incremental(ws):
    r = BM25Retriever(ws)
    r.add_documents_batch(_make_docs(5))
    r.add_documents_batch(_make_docs(5))
    assert len(r._doc_ids) == 10


# ------------------------------------------------------------------
# RRF score
# ------------------------------------------------------------------

def test_rrf_score_decreasing():
    scores = [_rrf_score(i) for i in range(10)]
    assert all(scores[i] > scores[i + 1] for i in range(len(scores) - 1))


def test_rrf_score_positive():
    assert _rrf_score(0) > 0
    assert _rrf_score(100) > 0


# ------------------------------------------------------------------
# HybridRetriever (mock Vector e Reranker)
# ------------------------------------------------------------------

def _make_search_results(n: int, method: str) -> list[SearchResult]:
    return [
        SearchResult(
            doc_id=f"doc_{i:03d}",
            score=1.0 - i * 0.05,
            snippet=f"snippet {i}",
            source_id=f"SRC_{i}",
            retrieval_method=method,
        )
        for i in range(n)
    ]


@pytest.fixture
def hybrid_retriever(ws):
    with patch("aiura_legal.core.retrieval.hybrid_retriever.VectorRetriever") as MockVec, \
         patch("aiura_legal.core.retrieval.hybrid_retriever.CrossEncoderReranker") as MockRR:

        mock_vec = MagicMock()
        mock_vec.search.return_value = _make_search_results(10, "vector")
        MockVec.return_value = mock_vec

        mock_rr = MagicMock()
        mock_rr.rerank.side_effect = lambda q, cands, top_k: cands[:top_k]
        MockRR.return_value = mock_rr

        h = HybridRetriever(ws)
        h.bm25.build(_make_docs(20))
        return h


def test_hybrid_search_returns_results(hybrid_retriever):
    results = hybrid_retriever.search("responsabilità contrattuale")
    assert len(results) > 0


def test_hybrid_search_intent_norma_lookup(hybrid_retriever):
    results = hybrid_retriever.search(
        "art. 1218 inadempimento",
        intent=QueryIntent.NORMA_LOOKUP,
    )
    assert len(results) > 0


def test_hybrid_rrf_merges_sources(hybrid_retriever):
    """Doc presenti in entrambi BM25 e Vector devono avere score RRF sommato."""
    results = hybrid_retriever.search("codice civile", top_k_retrieve=15)
    # Almeno un risultato deve avere retrieval_method hybrid_rrf
    methods = {r.retrieval_method for r in results}
    assert "hybrid_rrf" in methods


def test_build_research_packet(hybrid_retriever):
    packet = hybrid_retriever.build_research_packet(
        "responsabilità contrattuale inadempimento",
        intent=QueryIntent.FATTISPECIE_ANALYSIS,
    )
    assert packet.query_original == "responsabilità contrattuale inadempimento"
    assert packet.query_intent == QueryIntent.FATTISPECIE_ANALYSIS
    assert packet.retrieval_confidence in ("LOW", "MEDIUM", "HIGH")


def test_research_packet_confidence_levels(hybrid_retriever):
    # Con mock che ritorna 10 risultati → HIGH
    packet = hybrid_retriever.build_research_packet("query test")
    assert packet.retrieval_confidence == "HIGH"
