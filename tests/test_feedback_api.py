"""
Test endpoint feedback e history (PATCH /history/{id}/feedback,
GET /history/{id}, GET /history?feedback_only=true).

Usa mongomock-motor per zero MongoDB reale.
"""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Fixture: documento history di esempio
# ---------------------------------------------------------------------------

SAMPLE_DOC = {
    "_id": "test-history-id-001",
    "query": "Quali sono le conseguenze del ritardo nel pagamento?",
    "workspace": "mio-studio",
    "intent": "fattispecie_analysis",
    "mode": "standard",
    "verdict": "PASS",
    "confidence": "HIGH",
    "answer": "Il ritardo nel pagamento comporta...",
    "answer_summary": "Il ritardo nel pagamento",
    "analysis_sections": [{"step": "QUALIFICAZIONE", "content": "...", "citations": []}],
    "analysis_fase_1": [],
    "analysis_fase_2": [],
    "sources": [],
    "sources_count": 3,
    "duration_total_s": 4.2,
    "created_at": "2026-06-05T10:00:00Z",
}


def _make_mock_db(doc: dict | None = SAMPLE_DOC):
    """Crea un mock della collection query_history."""
    coll = MagicMock()
    coll.find_one = AsyncMock(return_value=doc)
    coll.update_one = AsyncMock()
    coll.insert_one = AsyncMock()
    coll.find = MagicMock(return_value=MagicMock(
        to_list=AsyncMock(return_value=[doc] if doc else [])
    ))
    coll.count_documents = AsyncMock(return_value=1 if doc else 0)

    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=coll)
    return db, coll


# ---------------------------------------------------------------------------
# Helper: importa app con DB mockato
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_mongo_client():
    db, coll = _make_mock_db()
    mongo = MagicMock()
    mongo.db = db
    with patch("aiura_legal.api.app.MongoClient.get", return_value=mongo):
        yield mongo, coll


# ---------------------------------------------------------------------------
# Test GET /history/{entry_id}
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_history_entry_ok(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    coll.find_one = AsyncMock(return_value=SAMPLE_DOC)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/history/test-history-id-001")

    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "test-history-id-001"
    assert data["answer"] == SAMPLE_DOC["answer"]
    assert data["feedback_rating"] is None


@pytest.mark.asyncio
async def test_get_history_entry_404(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    coll.find_one = AsyncMock(return_value=None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/history/non-esistente")

    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Test PATCH /history/{entry_id}/feedback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_feedback_ok(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    # Doc senza feedback_at
    coll.find_one = AsyncMock(return_value={"_id": "test-history-id-001"})
    coll.update_one = AsyncMock()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch(
            "/history/test-history-id-001/feedback",
            json={"rating": 4, "tags": ["Utile", "Citazioni corrette"], "note": "Ottima"},
        )

    assert r.status_code == 204
    coll.update_one.assert_called_once()
    call_args = coll.update_one.call_args
    set_data = call_args[0][1]["$set"]
    assert set_data["feedback_rating"] == 4
    assert "Utile" in set_data["feedback_tags"]
    assert set_data["feedback_note"] == "Ottima"
    assert "feedback_at" in set_data


@pytest.mark.asyncio
async def test_add_feedback_409_already_submitted(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    # Doc con feedback_at già presente
    coll.find_one = AsyncMock(return_value={
        "_id": "test-history-id-001",
        "feedback_at": "2026-06-05T10:05:00Z",
    })

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch(
            "/history/test-history-id-001/feedback",
            json={"rating": 3, "tags": []},
        )

    assert r.status_code == 409
    assert "già inviato" in r.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_feedback_404_not_found(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    coll.find_one = AsyncMock(return_value=None)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch(
            "/history/non-esistente/feedback",
            json={"rating": 3, "tags": []},
        )

    assert r.status_code == 404


@pytest.mark.asyncio
async def test_add_feedback_422_invalid_rating(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch(
            "/history/any/feedback",
            json={"rating": 6, "tags": []},
        )

    assert r.status_code == 422


@pytest.mark.asyncio
async def test_add_feedback_422_invalid_tag(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.patch(
            "/history/any/feedback",
            json={"rating": 3, "tags": ["TagNonValido"]},
        )

    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Test GET /history?feedback_only=true
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_list_history_feedback_only(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    doc_with_feedback = {**SAMPLE_DOC, "feedback_at": "2026-06-05T10:05:00Z", "feedback_rating": 5}
    coll.find = MagicMock(return_value=MagicMock(
        to_list=AsyncMock(return_value=[doc_with_feedback])
    ))
    coll.count_documents = AsyncMock(return_value=1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/history?workspace=mio-studio&feedback_only=true")

    assert r.status_code == 200
    entries = r.json()["entries"]
    assert len(entries) == 1
    assert entries[0]["feedback_rating"] == 5
    # Verifica che il filtro MongoDB sia stato applicato
    call_args = coll.count_documents.call_args[0][0]
    assert "feedback_at" in call_args


@pytest.mark.asyncio
async def test_list_history_normal_no_filter(mock_mongo_client):
    from httpx import AsyncClient, ASGITransport
    from aiura_legal.api.app import app

    mongo, coll = mock_mongo_client
    coll.find = MagicMock(return_value=MagicMock(
        to_list=AsyncMock(return_value=[SAMPLE_DOC])
    ))
    coll.count_documents = AsyncMock(return_value=1)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/history?workspace=mio-studio")

    assert r.status_code == 200
    call_args = coll.count_documents.call_args[0][0]
    # Senza feedback_only non deve esserci il filtro feedback_at
    assert "feedback_at" not in call_args
