"""
Test per ContextBudgetManager — context budget fisso 4k con sommario-first.
"""
from __future__ import annotations

import tiktoken
import pytest

from aiura_legal.core.retrieval.context_budget import ContextBudgetManager, _count_tokens
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


# ---------------------------------------------------------------------------
# Test 1: format_chunks — top-1 full text, gli altri sommario
# ---------------------------------------------------------------------------

def test_format_chunks_normativa_top1_full_rest_summary():
    mgr = ContextBudgetManager()

    chunks = [
        _make_chunk("Testo completo articolo 1 molto lungo " * 20, source_id="norm_1", sommario="Sintesi articolo 1"),
        _make_chunk("Testo completo articolo 2 molto lungo " * 20, source_id="norm_2", sommario="Sintesi articolo 2"),
        _make_chunk("Testo completo articolo 3 molto lungo " * 20, source_id="norm_3", sommario="Sintesi articolo 3"),
        _make_chunk("Testo completo articolo 4 molto lungo " * 20, source_id="norm_4", sommario="Sintesi articolo 4"),
    ]

    result = mgr.format_chunks(chunks, "normativa")

    # Il chunk 1 deve avere il testo completo (non "(sintesi)")
    assert "[1] norm_1\n" in result
    assert "(sintesi)" not in result.split("[2]")[0]  # sezione 1 senza "(sintesi)"

    # I chunk 2-4 devono avere "(sintesi)"
    assert "[2] norm_2 (sintesi)" in result
    assert "[3] norm_3 (sintesi)" in result
    assert "[4] norm_4 (sintesi)" in result

    # Il testo dei sommari deve comparire
    assert "Sintesi articolo 2" in result
    assert "Sintesi articolo 3" in result
    assert "Sintesi articolo 4" in result


# ---------------------------------------------------------------------------
# Test 2: fallback text[:150] quando sommario=None
# ---------------------------------------------------------------------------

def test_format_chunks_sommario_none_fallback():
    mgr = ContextBudgetManager()

    long_text = "A" * 500  # 500 caratteri, nessun sommario
    chunks = [
        _make_chunk("Primo articolo " * 30, source_id="n1", sommario="Sommario primo"),
        _make_chunk(long_text, source_id="n2", sommario=None),  # fallback
    ]

    result = mgr.format_chunks(chunks, "normativa")

    # n2 usa fallback: text[:150]
    assert "[2] n2 (sintesi)" in result
    # Il testo del fallback deve essere presente (primi 150 caratteri di long_text)
    assert "A" * 50 in result  # almeno 50 'A' sono presenti nel risultato


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
    # Budget massimo: 800 (normativa) + 600 (giurisprudenza) + 200 (dottrina) + 100 slack = 1700
    assert total_tokens <= 1700, (
        f"Research packet supera il budget: {total_tokens} > 1700 token"
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
