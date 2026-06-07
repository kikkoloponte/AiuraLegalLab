"""Test WikiEngine — file_response end-to-end, URN propagati in page.sources."""
import pytest
from unittest.mock import AsyncMock, MagicMock

import mongomock_motor

from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult
from aiura_legal.wiki.engine import WikiEngine
from aiura_legal.wiki.store import WikiStore
from aiura_legal.wiki.writer import WikiWriter


@pytest.fixture
def db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_test"]


@pytest.fixture
def store(db):
    return WikiStore(db)


@pytest.fixture
def mock_writer():
    writer = MagicMock(spec=WikiWriter)
    writer.extract_concepts = AsyncMock(return_value=["licenziamento per giusta causa"])
    writer.merge_knowledge = AsyncMock(
        return_value=(
            "## Sintesi\nAggiornata.\n\n"
            "## Fonti\n- urn:nir:art2119\n"
        )
    )
    return writer


@pytest.fixture
def engine(store, mock_writer):
    return WikiEngine(store, mock_writer)


def _make_packet(urns: list[str]) -> ResearchPacket:
    sources = [
        SearchResult(doc_id=u, score=1.0, snippet="snippet", source_id=u)
        for u in urns
    ]
    return ResearchPacket(
        query_original="test query",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=sources,
        retrieval_confidence="HIGH",
    )


@pytest.mark.asyncio
async def test_file_response_creates_page(engine, store):
    packet = _make_packet(["urn:nir:art2119"])
    await engine.file_response(
        query="Quando si licenzia per giusta causa?",
        response_text="L'art. 2119 cc disciplina il recesso.",
        research_packet=packet,
        workspace="test-ws",
    )
    page = await store.get_page("licenziamento_per_giusta_causa", "test-ws")
    assert page is not None
    assert page.query_count == 1
    assert page.version == 1


@pytest.mark.asyncio
async def test_file_response_propagates_urns(engine, store):
    packet = _make_packet(["urn:nir:art2119", "urn:nir:art18"])
    await engine.file_response(
        query="Licenziamento",
        response_text="Risposta con art. 2119 e art. 18.",
        research_packet=packet,
        workspace="test-ws",
    )
    page = await store.get_page("licenziamento_per_giusta_causa", "test-ws")
    assert "urn:nir:art2119" in page.sources
    assert "urn:nir:art18" in page.sources


@pytest.mark.asyncio
async def test_file_response_increments_version(engine, store):
    packet = _make_packet(["urn:nir:art2119"])
    await engine.file_response("q", "r", packet, "test-ws")
    await engine.file_response("q2", "r2", packet, "test-ws")
    page = await store.get_page("licenziamento_per_giusta_causa", "test-ws")
    assert page.version == 2
    assert page.query_count == 2


@pytest.mark.asyncio
async def test_file_response_no_concepts_skips(engine, store, mock_writer):
    mock_writer.extract_concepts = AsyncMock(return_value=[])
    packet = _make_packet(["urn:nir:art1"])
    await engine.file_response("q", "r", packet, "test-ws")
    pages = await store.list_all("test-ws")
    assert len(pages) == 0


@pytest.mark.asyncio
async def test_file_response_swallows_exceptions(engine, mock_writer):
    """Un errore interno non deve propagarsi al chiamante."""
    mock_writer.extract_concepts = AsyncMock(side_effect=RuntimeError("boom"))
    packet = _make_packet([])
    await engine.file_response("q", "r", packet, "test-ws")  # non solleva
