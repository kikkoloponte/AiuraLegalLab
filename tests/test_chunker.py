"""
Test Chunker sliding window.
"""
import pytest
from aiura_legal.ingestion.chunker import Chunker, TextChunk


@pytest.fixture
def chunker():
    return Chunker(max_tokens=512, overlap=64, min_tokens=20)


# ------------------------------------------------------------------
# Proprietà base
# ------------------------------------------------------------------

def test_empty_text_returns_no_chunks(chunker):
    assert chunker.chunk("") == []
    assert chunker.chunk("   ") == []


def test_short_text_single_chunk(chunker):
    # Testo sufficientemente lungo da superare min_tokens=20
    text = (
        "Articolo 1. Il presente contratto è stipulato tra le parti "
        "che si impegnano reciprocamente al rispetto delle clausole "
        "qui di seguito elencate in modo chiaro e dettagliato."
    )
    chunks = chunker.chunk(text)
    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].token_count >= 20


def test_chunk_indices_sequential(chunker):
    text = " ".join(["parola"] * 2000)
    chunks = chunker.chunk(text)
    for i, c in enumerate(chunks):
        assert c.index == i


def test_no_chunk_exceeds_max_tokens(chunker):
    text = " ".join(["termine"] * 3000)
    chunks = chunker.chunk(text)
    for c in chunks:
        assert c.token_count <= chunker.max_tokens


def test_overlap_creates_more_chunks_than_no_overlap():
    chunker_overlap = Chunker(max_tokens=100, overlap=20, min_tokens=5)
    chunker_no_overlap = Chunker(max_tokens=100, overlap=0, min_tokens=5)
    text = " ".join(["parola"] * 500)
    assert len(chunker_overlap.chunk(text)) >= len(chunker_no_overlap.chunk(text))


def test_overlap_invalid_raises():
    with pytest.raises(ValueError, match="overlap"):
        Chunker(max_tokens=100, overlap=100)


def test_min_tokens_filters_small_chunks():
    chunker = Chunker(max_tokens=50, overlap=10, min_tokens=40)
    # Testo corto → l'unico chunk ha meno di 40 token → scartato
    tiny_text = "Breve."
    chunks = chunker.chunk(tiny_text)
    for c in chunks:
        assert c.token_count >= 40


def test_count_tokens(chunker):
    n = chunker.count_tokens("uno due tre")
    assert n > 0


# ------------------------------------------------------------------
# Struttura TextChunk
# ------------------------------------------------------------------

def test_chunk_start_end_token(chunker):
    text = " ".join(["parola"] * 1000)
    chunks = chunker.chunk(text)
    assert chunks[0].start_token == 0
    for c in chunks:
        assert c.start_token < c.end_token


def test_iter_chunks_lazy(chunker):
    text = " ".join(["parola"] * 2000)
    gen = chunker.iter_chunks(text)
    first = next(gen)
    assert isinstance(first, TextChunk)


# ------------------------------------------------------------------
# Testo legale realistico (sintetico, no PII)
# ------------------------------------------------------------------

def test_legal_text_chunking():
    legal_text = (
        "Art. 1. Le parti si obbligano reciprocamente alla consegna dei beni. "
        * 100
    )
    chunker = Chunker(max_tokens=128, overlap=16)
    chunks = chunker.chunk(legal_text)
    assert len(chunks) > 1
    # Il testo di ogni chunk non è vuoto
    for c in chunks:
        assert c.text.strip() != ""
