"""
Test MongoDB client e models con mongomock-motor (zero MongoDB reale).
PII: solo dati sintetici.
"""
from __future__ import annotations
import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock
import mongomock_motor
from aiura_legal.ingestion.mongodb.models import (
    LegalDocument,
    Chunk,
    IngestionJob,
    DocType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_document() -> LegalDocument:
    return LegalDocument(
        title="Contratto di prova",
        text="Testo di prova senza dati personali reali.",
        doc_type=DocType.CONTRATTO,
        source="studio-test",
        source_id="TEST_DOC_001",
        workspace="test-workspace",
    )


@pytest.fixture
def sample_chunk() -> Chunk:
    return Chunk(
        document_id="doc_fake_id_001",
        chunk_index=0,
        text="Chunk di testo sintetico per i test.",
        doc_type=DocType.CONTRATTO,
        source_id="TEST_DOC_001",
        workspace="test-workspace",
        token_count=8,
    )


@pytest.fixture
def sample_job() -> IngestionJob:
    return IngestionJob(
        document_id="doc_fake_id_001",
        job_type="CHUNK",
        tier=1,
        status="pending",
        priority=5,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class TestLegalDocumentModel:
    def test_default_values(self):
        doc = LegalDocument(text="testo")
        assert doc.doc_type == "altro"
        assert doc.is_anonymized is False
        assert doc.is_chunked is False
        assert doc.is_indexed_bm25 is False
        assert doc.is_indexed_vector is False
        assert doc.migrated_from_lab is False
        assert isinstance(doc.created_at, datetime)

    def test_text_field_is_text(self):
        """Verifica che il campo testo sia 'text', allineato a LegalAgentLab."""
        doc = LegalDocument(text="articolo normativo di prova")
        assert doc.text == "articolo normativo di prova"

    def test_alias_id(self):
        doc = LegalDocument.model_validate({"_id": "abc123", "text": "t"})
        assert doc.id == "abc123"

    def test_doc_type_enum_values(self):
        for dtype in DocType:
            doc = LegalDocument(text="t", doc_type=dtype)
            assert doc.doc_type == dtype

    def test_full_document(self, sample_document):
        assert sample_document.title == "Contratto di prova"
        assert sample_document.source_id == "TEST_DOC_001"
        assert sample_document.workspace == "test-workspace"


class TestChunkModel:
    def test_required_fields(self, sample_chunk):
        assert sample_chunk.document_id == "doc_fake_id_001"
        assert sample_chunk.chunk_index == 0
        assert sample_chunk.text == "Chunk di testo sintetico per i test."
        assert sample_chunk.token_count == 8

    def test_embedding_optional(self):
        chunk = Chunk(document_id="x", chunk_index=0, text="t")
        assert chunk.embedding is None
        assert chunk.embedding_model is None

    def test_alias_id(self):
        chunk = Chunk.model_validate(
            {"_id": "chunk_id_001", "document_id": "doc_001", "chunk_index": 1, "text": "t"}
        )
        assert chunk.id == "chunk_id_001"


class TestIngestionJobModel:
    def test_defaults(self, sample_job):
        assert sample_job.status == "pending"
        assert sample_job.tier == 1
        assert sample_job.priority == 5
        assert sample_job.retry_count == 0
        assert sample_job.error is None
        assert sample_job.started_at is None
        assert sample_job.completed_at is None
        assert isinstance(sample_job.created_at, datetime)

    def test_job_types(self):
        for jtype in ["CHUNK", "ANONYMIZE", "EMBED", "INDEX_BM25", "GRAPH"]:
            job = IngestionJob(document_id="x", job_type=jtype)
            assert job.job_type == jtype


# ---------------------------------------------------------------------------
# MongoDB CRUD con mongomock-motor
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_motor_client():
    return mongomock_motor.AsyncMongoMockClient()


@pytest.mark.asyncio
class TestMongoClientCRUD:
    async def test_insert_and_find_document(self, mock_motor_client):
        db = mock_motor_client["aiura_legal_test_insert"]
        doc = LegalDocument(
            text="Testo normativo sintetico.",
            source_id="URN_SINTETICO_001",
            workspace="test-ws",
        )
        # Escludi _id:None per evitare duplicate key con mongomock
        data = {k: v for k, v in doc.model_dump(by_alias=True).items() if not (k == "_id" and v is None)}
        result = await db["documents"].insert_one(data)
        assert result.inserted_id is not None

        found = await db["documents"].find_one({"source_id": "URN_SINTETICO_001"})
        assert found is not None
        assert found["text"] == "Testo normativo sintetico."

    async def test_insert_chunk(self, mock_motor_client):
        db = mock_motor_client["aiura_legal"]
        chunk = Chunk(
            document_id="doc_test_001",
            chunk_index=0,
            text="Primo chunk di test.",
            token_count=5,
        )
        await db["chunks"].insert_one(chunk.model_dump(by_alias=True))
        count = await db["chunks"].count_documents({"document_id": "doc_test_001"})
        assert count == 1

    async def test_ingestion_queue_status_update(self, mock_motor_client):
        db = mock_motor_client["aiura_legal"]
        job = IngestionJob(document_id="doc_test_001", job_type="CHUNK")
        await db["ingestion_queue"].insert_one(job.model_dump(by_alias=True))

        await db["ingestion_queue"].update_one(
            {"document_id": "doc_test_001", "job_type": "CHUNK"},
            {"$set": {"status": "done"}},
        )
        updated = await db["ingestion_queue"].find_one({"document_id": "doc_test_001"})
        assert updated["status"] == "done"

    async def test_multiple_chunks_batch(self, mock_motor_client):
        db = mock_motor_client["aiura_legal_test_batch"]
        chunks = [
            # Escludi _id:None — mongomock lo tratta come duplicate key
            {k: v for k, v in Chunk(document_id="doc_batch_001", chunk_index=i, text=f"Chunk {i}").model_dump(by_alias=True).items() if not (k == "_id" and v is None)}
            for i in range(5)
        ]
        await db["chunks"].insert_many(chunks)
        count = await db["chunks"].count_documents({"document_id": "doc_batch_001"})
        assert count == 5

    async def test_pii_vault_insert(self, mock_motor_client):
        db = mock_motor_client["aiura_legal"]
        vault_entry = {
            "document_id": "doc_test_001",
            "entity_map_encrypted": b"encrypted_bytes_placeholder",
            "workspace": "test-ws",
        }
        result = await db["pii_vault"].insert_one(vault_entry)
        assert result.inserted_id is not None


# ---------------------------------------------------------------------------
# MongoClient ping test (mock del driver)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_mongo_client_ping_ok():
    with patch("aiura_legal.ingestion.mongodb.client.motor.motor_asyncio.AsyncIOMotorClient") as mock_cls:
        mock_instance = MagicMock()
        mock_db = AsyncMock()
        mock_db.command = AsyncMock(return_value={"ok": 1})
        mock_instance.__getitem__ = MagicMock(return_value=mock_db)
        mock_cls.return_value = mock_instance

        from aiura_legal.ingestion.mongodb.client import MongoClient
        MongoClient._instance = None
        client = MongoClient()
        client.db = mock_db

        result = await client.ping()
        assert result is True
        MongoClient._instance = None


@pytest.mark.asyncio
async def test_mongo_client_ping_fail():
    with patch("aiura_legal.ingestion.mongodb.client.motor.motor_asyncio.AsyncIOMotorClient") as mock_cls:
        mock_instance = MagicMock()
        mock_db = AsyncMock()
        mock_db.command = AsyncMock(side_effect=Exception("connection refused"))
        mock_instance.__getitem__ = MagicMock(return_value=mock_db)
        mock_cls.return_value = mock_instance

        from aiura_legal.ingestion.mongodb.client import MongoClient
        MongoClient._instance = None
        client = MongoClient()
        client.db = mock_db

        result = await client.ping()
        assert result is False
        MongoClient._instance = None
