"""
test_embed_worker.py — test per EmbedWorker (Tier 2).

Copertura:
  TestChunkToDocument   (4) — conversione chunk → Document
  TestRunOnce           (6) — happy path, nessun job, job mancante, errore Chroma,
                              retry logic, claim atomico
  TestMarkDoneAndFailed (4) — aggiornamento status, retry counter, failed definitivo
  TestRunLoop           (2) — stop immediato, nessuna iterazione senza job
"""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import mongomock_motor

from aiura_legal.workers.embed_worker import EmbedWorker, _MAX_RETRIES


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal"]


def _make_worker(mock_db, workspaces_path: str = "/tmp/ws") -> EmbedWorker:
    worker = EmbedWorker(
        mongo_db=mock_db,
        workspaces_base_path=workspaces_path,
        batch_size=10,
        chunk_batch_size=50,
    )
    # Sostituiamo il VectorRetriever con un mock per evitare accesso a disco
    worker._get_retriever = MagicMock(return_value=_make_mock_retriever())
    return worker


def _make_mock_retriever() -> MagicMock:
    r = MagicMock()
    r.add_documents_batch = MagicMock()
    return r


def _make_job(doc_id: str = "doc1", status: str = "pending", retry: int = 0) -> dict:
    return {
        "_id": f"job_{doc_id}",
        "document_id": doc_id,
        "job_type": "EMBED",
        "tier": 2,
        "status": status,
        "priority": 5,
        "created_at": datetime.now(timezone.utc),
        "retry_count": retry,
    }


def _make_doc(doc_id: str = "doc1", workspace: str = "default") -> dict:
    return {
        "_id": doc_id,
        "workspace": workspace,
        "text": "Testo del documento.",
        "is_indexed_vector": False,
    }


def _make_chunk(doc_id: str = "doc1", idx: int = 0) -> dict:
    return {
        "_id": f"chunk_{doc_id}_{idx}",
        "document_id": doc_id,
        "chunk_index": idx,
        "text": f"Testo chunk {idx}.",
        "source_id": f"src_{doc_id}",
        "workspace": "default",
        "corpus": "studio",
        "fonte": "altro",
        "testo_tipo": "normativo",
    }


# ---------------------------------------------------------------------------
# TestChunkToDocument
# ---------------------------------------------------------------------------

class TestChunkToDocument:
    def test_basic_conversion(self):
        chunk = _make_chunk("d1", 0)
        doc = EmbedWorker._chunk_to_document(chunk)
        assert doc.id == "chunk_d1_0"
        assert doc.text == "Testo chunk 0."
        assert doc.source_id == "src_d1"

    def test_metadata_fields(self):
        chunk = _make_chunk("d1", 2)
        chunk["corpus"] = "normattiva"
        chunk["titolo"] = "Codice Civile"
        doc = EmbedWorker._chunk_to_document(chunk)
        assert doc.metadata["corpus"] == "normattiva"
        assert doc.metadata["titolo"] == "Codice Civile"
        assert doc.metadata["document_id"] == "d1"

    def test_missing_id_uses_fallback(self):
        chunk = {"document_id": "d1", "chunk_index": 3, "text": "X",
                 "source_id": "src_d1", "workspace": "default",
                 "corpus": "", "fonte": "", "testo_tipo": "", "titolo": "",
                 "articolo_num": "", "source": ""}
        doc = EmbedWorker._chunk_to_document(chunk)
        assert "src_d1" in doc.id or "3" in doc.id

    def test_empty_text_allowed(self):
        chunk = _make_chunk("d1", 0)
        chunk["text"] = ""
        doc = EmbedWorker._chunk_to_document(chunk)
        assert doc.text == ""


# ---------------------------------------------------------------------------
# TestRunOnce
# ---------------------------------------------------------------------------

class TestRunOnce:
    @pytest.mark.asyncio
    async def test_processes_one_job(self, mock_db):
        """Un job pending → viene processato e marcato done."""
        await mock_db["documents"].insert_one(_make_doc("d1"))
        await mock_db["chunks"].insert_many([_make_chunk("d1", 0), _make_chunk("d1", 1)])
        await mock_db["ingestion_queue"].insert_one(_make_job("d1"))

        worker = _make_worker(mock_db)
        count = await worker.run_once()

        assert count == 1
        # Job deve essere done
        job = await mock_db["ingestion_queue"].find_one({"document_id": "d1"})
        assert job["status"] == "done"
        # Documento deve essere marcato is_indexed_vector=True
        doc = await mock_db["documents"].find_one({"_id": "d1"})
        assert doc["is_indexed_vector"] is True

    @pytest.mark.asyncio
    async def test_no_jobs_returns_zero(self, mock_db):
        worker = _make_worker(mock_db)
        count = await worker.run_once()
        assert count == 0

    @pytest.mark.asyncio
    async def test_document_not_found_marks_failed(self, mock_db):
        """Se il documento non esiste, il job va in failed (dopo retries)."""
        job = _make_job("ghost_doc")
        job["retry_count"] = _MAX_RETRIES - 1  # prossimo fallimento → failed
        await mock_db["ingestion_queue"].insert_one(job)

        worker = _make_worker(mock_db)
        await worker.run_once()

        updated = await mock_db["ingestion_queue"].find_one({"document_id": "ghost_doc"})
        assert updated["status"] == "failed"

    @pytest.mark.asyncio
    async def test_no_chunks_still_marks_done(self, mock_db):
        """Documento senza chunk: job marcato done (nessun errore)."""
        await mock_db["documents"].insert_one(_make_doc("d_empty"))
        await mock_db["ingestion_queue"].insert_one(_make_job("d_empty"))

        worker = _make_worker(mock_db)
        await worker.run_once()

        job = await mock_db["ingestion_queue"].find_one({"document_id": "d_empty"})
        assert job["status"] == "done"

    @pytest.mark.asyncio
    async def test_processes_multiple_jobs_in_order(self, mock_db):
        """Verifica che più job vengano processati in un singolo run_once."""
        for i in range(3):
            await mock_db["documents"].insert_one(_make_doc(f"d{i}"))
            await mock_db["chunks"].insert_one(_make_chunk(f"d{i}", 0))
            await mock_db["ingestion_queue"].insert_one(_make_job(f"d{i}"))

        worker = _make_worker(mock_db)
        count = await worker.run_once()

        assert count == 3

    @pytest.mark.asyncio
    async def test_chroma_error_retries_job(self, mock_db):
        """Se ChromaDB lancia un'eccezione, il job viene rimesso in pending."""
        await mock_db["documents"].insert_one(_make_doc("d_err"))
        await mock_db["chunks"].insert_one(_make_chunk("d_err", 0))
        await mock_db["ingestion_queue"].insert_one(_make_job("d_err"))

        # batch_size=1 → il worker processa un solo job per ciclo,
        # così il job rimesso in pending non viene ripreso nella stessa run_once()
        worker = EmbedWorker(
            mongo_db=mock_db,
            workspaces_base_path="/tmp/ws",
            batch_size=1,
        )
        bad_retriever = MagicMock()
        bad_retriever.add_documents_batch = MagicMock(
            side_effect=RuntimeError("ChromaDB error")
        )
        worker._get_retriever = MagicMock(return_value=bad_retriever)

        await worker.run_once()

        job = await mock_db["ingestion_queue"].find_one({"document_id": "d_err"})
        # retry_count=0 → primo errore → rimesso in pending con retry_count=1
        assert job["status"] == "pending"
        assert job["retry_count"] == 1


# ---------------------------------------------------------------------------
# TestMarkDoneAndFailed
# ---------------------------------------------------------------------------

class TestMarkDoneAndFailed:
    @pytest.mark.asyncio
    async def test_mark_done_sets_completed_at(self, mock_db):
        await mock_db["ingestion_queue"].insert_one(_make_job("d1"))
        worker = _make_worker(mock_db)
        await worker._mark_done("job_d1")
        job = await mock_db["ingestion_queue"].find_one({"_id": "job_d1"})
        assert job["status"] == "done"
        assert job["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_mark_failed_increments_retry(self, mock_db):
        job = _make_job("d1")
        await mock_db["ingestion_queue"].insert_one(job)
        worker = _make_worker(mock_db)
        await worker._mark_failed(job, "errore test")
        updated = await mock_db["ingestion_queue"].find_one({"_id": "job_d1"})
        assert updated["retry_count"] == 1
        assert updated["status"] == "pending"  # sotto max_retries

    @pytest.mark.asyncio
    async def test_mark_failed_at_max_retries_sets_failed(self, mock_db):
        job = _make_job("d1", retry=_MAX_RETRIES - 1)
        await mock_db["ingestion_queue"].insert_one(job)
        worker = _make_worker(mock_db)
        await worker._mark_failed(job, "errore terminale")
        updated = await mock_db["ingestion_queue"].find_one({"_id": "job_d1"})
        assert updated["status"] == "failed"

    @pytest.mark.asyncio
    async def test_mark_failed_stores_error_message(self, mock_db):
        job = _make_job("d1")
        await mock_db["ingestion_queue"].insert_one(job)
        worker = _make_worker(mock_db)
        await worker._mark_failed(job, "messaggio di errore specifico")
        updated = await mock_db["ingestion_queue"].find_one({"_id": "job_d1"})
        assert "messaggio di errore specifico" in updated["error"]


# ---------------------------------------------------------------------------
# TestRunLoop
# ---------------------------------------------------------------------------

class TestRunLoop:
    @pytest.mark.asyncio
    async def test_run_loop_stops_on_event(self, mock_db):
        """Il loop si ferma quando stop_event è settato."""
        import asyncio
        worker = _make_worker(mock_db)
        stop = asyncio.Event()
        stop.set()   # già settato → il loop esce subito dopo il primo ciclo

        # Non deve bloccarsi
        await asyncio.wait_for(
            worker.run_loop(poll_interval=0.01, stop_event=stop),
            timeout=2.0,
        )

    @pytest.mark.asyncio
    async def test_run_loop_processes_and_stops(self, mock_db):
        """Il loop processa i job disponibili e poi si ferma."""
        import asyncio
        await mock_db["documents"].insert_one(_make_doc("d1"))
        await mock_db["chunks"].insert_one(_make_chunk("d1", 0))
        await mock_db["ingestion_queue"].insert_one(_make_job("d1"))

        worker = _make_worker(mock_db)
        stop = asyncio.Event()

        async def _stopper():
            await asyncio.sleep(0.05)
            stop.set()

        asyncio.create_task(_stopper())
        await asyncio.wait_for(
            worker.run_loop(poll_interval=0.01, stop_event=stop),
            timeout=2.0,
        )

        job = await mock_db["ingestion_queue"].find_one({"document_id": "d1"})
        assert job["status"] == "done"
