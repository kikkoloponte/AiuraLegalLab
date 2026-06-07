"""
Test coordinator con mongomock-motor.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiura_legal.jurisprudence.coordinator import JurisprudenceCoordinator, to_chunks
from aiura_legal.jurisprudence.models import (
    JurisprudenceDocument,
    OrganoGiudicante,
    SourceChannel,
)


def _make_doc(numero: str = "1", channel: SourceChannel = SourceChannel.SCRAPING) -> JurisprudenceDocument:
    return JurisprudenceDocument(
        organo=OrganoGiudicante.CASSAZIONE,
        numero=numero,
        anno=2024,
        data_deposito=date(2024, 3, 1),
        sezione="III Civile",
        materia="contratti",
        massima="La massima.",
        motivazione="La motivazione.",
        dispositivo="Il dispositivo.",
        source_channel=channel,
    )


def _make_db(existing_id: str | None = None):
    db = MagicMock()

    async def find_one(query):
        if existing_id and query.get("_id") == existing_id:
            return {"_id": existing_id}
        return None

    collection = MagicMock()
    collection.find_one = find_one
    collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id="ok"))
    collection.update_one = AsyncMock()

    sync_collection = MagicMock()
    sync_collection.find_one = AsyncMock(return_value=None)
    sync_collection.update_one = AsyncMock()

    def getitem(name):
        if name == "sync_state":
            return sync_collection
        return collection

    db.__getitem__ = MagicMock(side_effect=getitem)
    return db, collection, sync_collection


# ---------------------------------------------------------------------------
# to_chunks
# ---------------------------------------------------------------------------

def test_to_chunks_genera_tre_chunk():
    doc = _make_doc()
    chunks = to_chunks(doc)
    assert len(chunks) == 3
    types = {c.metadata["chunk_type"] for c in chunks}
    assert types == {"massima", "motivazione", "dispositivo"}


def test_to_chunks_id_univoci():
    doc = _make_doc()
    chunks = to_chunks(doc)
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))


def test_to_chunks_jdoc_id():
    doc = _make_doc()
    chunks = to_chunks(doc)
    assert all(c.metadata["jdoc_id"] == doc.id for c in chunks)


def test_to_chunks_salta_testo_vuoto():
    doc = _make_doc()
    doc.massima = ""
    chunks = to_chunks(doc)
    types = {c.metadata["chunk_type"] for c in chunks}
    assert "massima" not in types
    assert len(chunks) == 2


# ---------------------------------------------------------------------------
# Coordinator.ingest
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ingest_nuovo_doc():
    db, collection, _ = _make_db()
    coordinator = JurisprudenceCoordinator(db)

    with patch("aiura_legal.jurisprudence.coordinator.anonymize_document", new=AsyncMock(side_effect=lambda d, _db: d)):
        stats = await coordinator.ingest([_make_doc()])

    assert stats["inserted"] == 1
    assert stats["skipped"] == 0
    assert stats["errors"] == 0
    collection.insert_one.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_dedup_skip():
    doc = _make_doc()
    db, collection, _ = _make_db(existing_id=doc.id)
    coordinator = JurisprudenceCoordinator(db)

    with patch("aiura_legal.jurisprudence.coordinator.anonymize_document", new=AsyncMock(side_effect=lambda d, _db: d)):
        stats = await coordinator.ingest([doc])

    assert stats["inserted"] == 0
    assert stats["skipped"] == 1
    collection.insert_one.assert_not_called()


@pytest.mark.asyncio
async def test_ingest_idempotente():
    doc = _make_doc()
    db, collection, _ = _make_db(existing_id=doc.id)
    coordinator = JurisprudenceCoordinator(db)

    with patch("aiura_legal.jurisprudence.coordinator.anonymize_document", new=AsyncMock(side_effect=lambda d, _db: d)):
        stats1 = await coordinator.ingest([doc])
        stats2 = await coordinator.ingest([doc])

    assert stats1["skipped"] == 1
    assert stats2["skipped"] == 1
    collection.insert_one.assert_not_called()


@pytest.mark.asyncio
async def test_ingest_chiama_bm25_e_vector():
    mock_bm25 = MagicMock()
    mock_vector = MagicMock()
    db, _, _ = _make_db()
    coordinator = JurisprudenceCoordinator(db, bm25_retriever=mock_bm25, vector_retriever=mock_vector)

    with patch("aiura_legal.jurisprudence.coordinator.anonymize_document", new=AsyncMock(side_effect=lambda d, _db: d)):
        await coordinator.ingest([_make_doc()])

    mock_bm25.add_documents_batch.assert_called_once()
    mock_vector.add_documents_batch.assert_called_once()


@pytest.mark.asyncio
async def test_ingest_errore_non_blocca_altri():
    db, collection, _ = _make_db()
    coordinator = JurisprudenceCoordinator(db)

    async def anon_raises_first(doc, _db):
        if doc.numero == "1":
            raise RuntimeError("errore simulato")
        return doc

    with patch("aiura_legal.jurisprudence.coordinator.anonymize_document", new=anon_raises_first):
        stats = await coordinator.ingest([_make_doc("1"), _make_doc("2")])

    assert stats["errors"] == 1
    assert stats["inserted"] == 1


# ---------------------------------------------------------------------------
# sync_state
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_last_sync_none_se_assente():
    db, _, _ = _make_db()
    coordinator = JurisprudenceCoordinator(db)
    result = await coordinator.get_last_sync(OrganoGiudicante.CASSAZIONE)
    assert result is None


@pytest.mark.asyncio
async def test_update_sync_state():
    db, _, sync_collection = _make_db()
    coordinator = JurisprudenceCoordinator(db)
    await coordinator.update_sync_state(OrganoGiudicante.CASSAZIONE, date(2024, 6, 1))
    sync_collection.update_one.assert_called_once()
    call_args = sync_collection.update_one.call_args
    assert call_args[0][0] == {"source": "cassazione"}
    assert "last_sync" in call_args[0][1]["$set"]
