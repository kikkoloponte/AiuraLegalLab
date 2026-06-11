"""
Test per ContextBudgetManager — context budget per n_ctx=8192 con full-text-first.
"""
from __future__ import annotations

import tiktoken
import pytest

from aiura_legal.core.retrieval.context_budget import ContextBudgetManager, _count_tokens
from aiura_legal.core.types import SearchResult
from aiura_legal.ingestion.mongodb.models import Chunk


_ENCODING = tiktoken.get_encoding("cl100k_base")


def _make_chunk(
    text: str,
    source_id: str = "test_src",
    sommario: str | None = None,
    corpus: str = "normattiva",
) -> Chunk:
    return Chunk(
        document_id="doc-1",
        chunk_index=0,
        text=text,
        source_id=source_id,
        corpus=corpus,
        sommario=sommario,
    )


def _make_result(
    doc_id: str,
    full_text: str = "",
    snippet: str = "snippet breve",
    sommario: str | None = None,
) -> SearchResult:
    meta = {"corpus": "normattiva"}
    if sommario:
        meta["sommario"] = sommario
    return SearchResult(
        doc_id=doc_id,
        score=1.0,
        snippet=snippet,
        source_id=f"urn:nir:{doc_id}",
        metadata=meta,
        full_text=full_text,
    )


# ---------------------------------------------------------------------------
# Test 1: format_chunks — top-3 full text (normativa), gli altri sommario
# ---------------------------------------------------------------------------

def test_format_chunks_normativa_top3_full_rest_summary():
    mgr = ContextBudgetManager()

    chunks = [
        _make_chunk(f"Testo completo articolo {i} molto lungo " * 20,
                    source_id=f"norm_{i}", sommario=f"Sintesi articolo {i}")
        for i in range(1, 6)
    ]

    result = mgr.format_chunks(chunks, "normativa")

    # I chunk 1-3 devono avere il testo completo (non "(sintesi)")
    assert "[1] norm_1\n" in result
    assert "[2] norm_2\n" in result
    assert "[3] norm_3\n" in result
    assert "(sintesi)" not in result.split("[4]")[0]

    # I chunk 4-5 devono avere "(sintesi)" con il sommario
    assert "[4] norm_4 (sintesi)" in result
    assert "[5] norm_5 (sintesi)" in result
    assert "Sintesi articolo 4" in result
    assert "Sintesi articolo 5" in result


# ---------------------------------------------------------------------------
# Test 2: fallback testo troncato quando sommario=None
# ---------------------------------------------------------------------------

def test_format_chunks_sommario_none_fallback():
    mgr = ContextBudgetManager()

    long_text = "A" * 500  # 500 caratteri, nessun sommario
    chunks = [
        _make_chunk("Primo articolo " * 30, source_id=f"n{i}", sommario=f"Sommario {i}")
        for i in range(1, 4)
    ] + [
        _make_chunk(long_text, source_id="n4", sommario=None),  # slot sintesi, fallback testo
    ]

    result = mgr.format_chunks(chunks, "normativa")

    # n4 è oltre i 3 full-text slot → sintesi con fallback sul testo
    assert "[4] n4 (sintesi)" in result
    assert "A" * 50 in result  # parte del testo è presente come fallback


# ---------------------------------------------------------------------------
# Test 2b: budget_texts con SearchResult — full_text usato se presente
# ---------------------------------------------------------------------------

def test_budget_texts_search_result_full_text():
    mgr = ContextBudgetManager()

    results = [
        _make_result("d1", full_text="Testo pieno dell'articolo. " * 30),
        _make_result("d2", full_text="", snippet="Solo snippet disponibile."),
    ]

    texts = mgr.budget_texts(results, "normativa")

    assert "Testo pieno dell'articolo." in texts[0]
    # Senza full_text il fallback è lo snippet
    assert "Solo snippet disponibile." in texts[1]


def test_budget_texts_search_result_truncates_to_budget():
    mgr = ContextBudgetManager()

    long_full = "parola " * 2000  # >> 400 token
    results = [_make_result("d1", full_text=long_full)]

    texts = mgr.budget_texts(results, "normativa")

    assert _count_tokens(texts[0]) <= 400


def test_budget_texts_giurisprudenza_top3_500_tokens():
    mgr = ContextBudgetManager()

    long_full = "motivazione della corte " * 1000
    results = [
        SearchResult(doc_id=f"g{i}", score=1.0, snippet="snip",
                     source_id=f"giuri_{i}", metadata={"corpus": "giurisprudenza"},
                     full_text=long_full)
        for i in range(4)
    ]

    texts = mgr.budget_texts(results, "giurisprudenza")

    for t in texts[:3]:
        assert 400 < _count_tokens(t) <= 500   # full text slot
    assert _count_tokens(texts[3]) <= 60       # summary slot


def test_budget_prassi_no_full_text():
    mgr = ContextBudgetManager()

    results = [_make_result("p1", full_text="testo di prassi " * 200)]
    texts = mgr.budget_texts(results, "prassi")

    # Prassi: zero full-text slot → solo sintesi
    assert _count_tokens(texts[0]) <= 60


# ---------------------------------------------------------------------------
# Test 3: format_research_packet produce tutte le sezioni
# ---------------------------------------------------------------------------

def test_format_research_packet_all_sections():
    mgr = ContextBudgetManager()

    norm_chunks  = [_make_chunk("Norma civile.", source_id="norm_1", sommario="Sintesi norma", corpus="normattiva")]
    giuri_chunks = [_make_chunk("Sentenza Cassazione.", source_id="giuri_1", sommario="Sintesi sentenza", corpus="giurisprudenza")]
    dott_chunks  = [_make_chunk("Manuale diritto civile.", source_id="dott_1", sommario="Sintesi dottrina", corpus="dottrina")]

    result = mgr.format_research_packet(
        normativa_chunks=norm_chunks,
        giurisprudenza_chunks=giuri_chunks,
        dottrina_chunks=dott_chunks,
    )

    assert "--- NORMATIVA ---" in result
    assert "--- GIURISPRUDENZA ---" in result
    assert "--- DOTTRINA ---" in result
    # Sezione prassi omessa se vuota
    assert "--- PRASSI ---" not in result


# ---------------------------------------------------------------------------
# Test 4: token totali del research packet ≤ 1700
# ---------------------------------------------------------------------------

def test_research_packet_total_tokens_within_budget():
    mgr = ContextBudgetManager()

    # 4 normativa chunks, 3 giurisprudenza chunks, 2 dottrina chunks
    norm_chunks = [
        _make_chunk("Articolo del codice civile " * 50, source_id=f"norm_{i}", sommario=f"Sintesi {i}")
        for i in range(4)
    ]
    giuri_chunks = [
        _make_chunk("Motivazione sentenza Cassazione " * 50, source_id=f"giuri_{i}", sommario=f"Massima {i}")
        for i in range(3)
    ]
    dott_chunks = [
        _make_chunk("Commentario dottrinale " * 50, source_id=f"dott_{i}", sommario=f"Sintesi dottrina {i}")
        for i in range(2)
    ]

    result = mgr.format_research_packet(
        normativa_chunks=norm_chunks,
        giurisprudenza_chunks=giuri_chunks,
        dottrina_chunks=dott_chunks,
    )

    total_tokens = _count_tokens(result)
    # Budget massimo n_ctx=8192: 1380 (normativa) + 1620 (giurisprudenza)
    # + 320 (dottrina) + 200 slack (label/markers) = 3520
    assert total_tokens <= 3520, (
        f"Research packet supera il budget: {total_tokens} > 3520 token"
    )


# ---------------------------------------------------------------------------
# Test 5: sezioni vuote sono omesse
# ---------------------------------------------------------------------------

def test_format_research_packet_empty_sections_omitted():
    mgr = ContextBudgetManager()

    norm_chunks = [_make_chunk("Norma.", source_id="n1", sommario="S")]
    result = mgr.format_research_packet(
        normativa_chunks=norm_chunks,
        giurisprudenza_chunks=[],
        dottrina_chunks=[],
    )

    assert "--- NORMATIVA ---" in result
    assert "--- GIURISPRUDENZA ---" not in result
    assert "--- DOTTRINA ---" not in result


# ---------------------------------------------------------------------------
# Test 6: corpus sconosciuto — graceful fallback
# ---------------------------------------------------------------------------

def test_format_chunks_unknown_corpus_graceful():
    mgr = ContextBudgetManager()

    chunks = [_make_chunk("Testo.", source_id="x1", sommario="Sintesi")]
    # Non deve sollevare eccezioni
    result = mgr.format_chunks(chunks, "corpus_inesistente")
    assert "x1" in result
