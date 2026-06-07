"""Smoke test: tutti i tipi condivisi sono istanziabili."""
from aiura_legal.core.types import Document, SearchResult, ResearchPacket, QueryIntent
from datetime import date


def test_query_intent_values():
    assert QueryIntent.NORMA_LOOKUP.value == "norma_lookup"
    assert len(QueryIntent) == 6


def test_document_instantiable():
    doc = Document(id="d1", text="testo di prova")
    assert doc.id == "d1"
    assert doc.text == "testo di prova"
    assert doc.metadata == {}
    assert doc.source_id == ""
    assert doc.is_anonymized is False
    assert doc.valid_from is None


def test_document_with_dates():
    doc = Document(
        id="d2",
        text="t",
        valid_from=date(2020, 1, 1),
        valid_to=date(2024, 12, 31),
    )
    assert doc.valid_from == date(2020, 1, 1)
    assert doc.valid_to == date(2024, 12, 31)


def test_search_result_instantiable():
    sr = SearchResult(doc_id="r1", score=0.95, snippet="frammento")
    assert sr.doc_id == "r1"
    assert sr.score == 0.95
    assert sr.retrieval_method == ""


def test_research_packet_instantiable():
    packet = ResearchPacket(
        query_original="responsabilità contrattuale",
        query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
    )
    assert packet.sources == []
    assert packet.retrieval_confidence == "LOW"
    assert packet.gaps == []


def test_research_packet_with_sources():
    sr = SearchResult(doc_id="CC_ART_1218", score=1.2, snippet="...")
    packet = ResearchPacket(
        query_original="inadempimento",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=[sr],
        retrieval_confidence="HIGH",
    )
    assert len(packet.sources) == 1
    assert packet.sources[0].doc_id == "CC_ART_1218"
