"""
Test Tier1Pipeline — mongomock-motor, fixture sintetiche, zero PII reali.
"""
from __future__ import annotations

import pytest
import mongomock_motor
from pathlib import Path

from aiura_legal.core.anonymizer.anonymizer import LegalAnonymizer
from aiura_legal.ingestion.chunker import Chunker
from aiura_legal.ingestion.pipeline import Tier1Pipeline, IngestResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_db():
    """Database mongomock-motor isolato per ogni test."""
    client = mongomock_motor.AsyncMongoMockClient()
    return client["aiura_legal_test"]


@pytest.fixture
def pipeline(mock_db):
    return Tier1Pipeline(
        mongo_db=mock_db,
        workspace="test-workspace",
        anonymizer=LegalAnonymizer(use_spacy=False),
        chunker=Chunker(max_tokens=256, overlap=32),
    )


def _write_txt(tmp_path: Path, name: str, content: str) -> str:
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return str(f)


# ---------------------------------------------------------------------------
# Test base
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ingest_txt_ok(pipeline, mock_db, tmp_path):
    """Pipeline completa su file TXT sintetico."""
    fp = _write_txt(
        tmp_path,
        "contratto_test.txt",
        "Clausola 1. Le parti concordano sulla fornitura di servizi professionali. " * 20,
    )
    result = await pipeline.ingest(fp)

    assert result.status == "ok"
    assert result.filename == "contratto_test.txt"
    assert result.workspace == "test-workspace"
    assert result.document_id != ""
    assert result.text_length > 0
    assert result.chunk_count >= 1
    assert result.duration_s > 0


@pytest.mark.asyncio
async def test_ingest_creates_document_in_mongo(pipeline, mock_db, tmp_path):
    """Il documento deve essere salvato in MongoDB.documents."""
    fp = _write_txt(tmp_path, "doc_test.txt", "Testo sintetico del documento legale. " * 30)
    result = await pipeline.ingest(fp)

    assert result.status == "ok"
    doc = await mock_db["documents"].find_one({"_id": result.document_id})
    assert doc is not None
    assert doc["workspace"] == "test-workspace"
    assert doc["is_anonymized"] is True
    assert doc["is_chunked"] is True
    assert doc["source"] == "upload"


@pytest.mark.asyncio
async def test_ingest_creates_chunks_in_mongo(pipeline, mock_db, tmp_path):
    """I chunk devono essere salvati in MongoDB.chunks."""
    fp = _write_txt(tmp_path, "lungo.txt", "Articolo di prova senza PII. " * 100)
    result = await pipeline.ingest(fp)

    assert result.status == "ok"
    count = await mock_db["chunks"].count_documents({"document_id": result.document_id})
    assert count == result.chunk_count
    assert count >= 1


@pytest.mark.asyncio
async def test_ingest_enqueues_embed_job(pipeline, mock_db, tmp_path):
    """Deve essere accodato un IngestionJob EMBED per Tier 2."""
    fp = _write_txt(tmp_path, "doc_job.txt", "Testo per test della coda. " * 30)
    result = await pipeline.ingest(fp)

    assert result.status == "ok"
    job = await mock_db["ingestion_queue"].find_one({
        "document_id": result.document_id,
        "job_type": "EMBED",
    })
    assert job is not None
    assert job["status"] == "pending"
    assert job["tier"] == 2


@pytest.mark.asyncio
async def test_ingest_chunk_fields(pipeline, mock_db, tmp_path):
    """Ogni chunk deve avere i campi obbligatori."""
    fp = _write_txt(tmp_path, "chunk_fields.txt", "Paragrafo legale sintetico. " * 50)
    result = await pipeline.ingest(fp)

    chunks = await mock_db["chunks"].find(
        {"document_id": result.document_id}
    ).to_list(length=100)

    for c in chunks:
        assert "chunk_index" in c
        assert "text" in c
        assert "token_count" in c
        assert c["workspace"] == "test-workspace"
        assert c["source_id"] == "chunk_fields"


# ---------------------------------------------------------------------------
# Test errori
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ingest_unsupported_format_returns_error(pipeline, tmp_path):
    """File .xlsx → status=error, nessun documento in MongoDB."""
    f = tmp_path / "dati.xlsx"
    f.write_bytes(b"PK fake xlsx")
    result = await pipeline.ingest(str(f))

    assert result.status == "error"
    assert result.document_id == ""
    assert result.chunk_count == 0
    assert "Formato non supportato" in (result.error or "")


@pytest.mark.asyncio
async def test_ingest_empty_file_returns_error(pipeline, tmp_path):
    """File TXT vuoto → status=error."""
    fp = _write_txt(tmp_path, "vuoto.txt", "")
    result = await pipeline.ingest(fp)

    assert result.status == "error"
    assert result.chunk_count == 0


@pytest.mark.asyncio
async def test_ingest_nonexistent_file_returns_error(pipeline):
    """File inesistente → status=error, nessuna eccezione sollevata."""
    result = await pipeline.ingest("C:/nonexistent/file.txt")

    assert result.status == "error"
    assert result.document_id == ""


# ---------------------------------------------------------------------------
# Test PII anonimizzazione nella pipeline
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pipeline_anonymizes_pii(pipeline, mock_db, tmp_path):
    """Il testo salvato in MongoDB non deve contenere CF o email."""
    text = (
        "Il cliente TSTAVN80A01H501Z ha inviato email a test@cliente.it "
        "per richiedere informazioni sul contratto. " * 20
    )
    fp = _write_txt(tmp_path, "con_pii.txt", text)
    result = await pipeline.ingest(fp)

    assert result.status == "ok"
    doc = await mock_db["documents"].find_one({"_id": result.document_id})
    assert "TSTAVN80A01H501Z" not in doc["text"]
    assert "test@cliente.it" not in doc["text"]
    # Stats PII devono rilevare le redazioni
    assert result.pii_stats.get("CF", 0) >= 1
    assert result.pii_stats.get("EMAIL", 0) >= 1


# ---------------------------------------------------------------------------
# Test batch
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_ingest_batch(pipeline, mock_db, tmp_path):
    """ingest_batch processa più file e ritorna tutti i risultati."""
    files = [
        _write_txt(tmp_path, f"file_{i}.txt", f"Documento {i} con testo sintetico legale. " * 30)
        for i in range(3)
    ]
    results = await pipeline.ingest_batch(files)

    assert len(results) == 3
    ok_count = sum(1 for r in results if r.status == "ok")
    assert ok_count == 3

    total_docs = await mock_db["documents"].count_documents({"workspace": "test-workspace"})
    assert total_docs == 3


@pytest.mark.asyncio
async def test_batch_partial_failure(pipeline, mock_db, tmp_path):
    """Un file non valido nella batch non blocca gli altri."""
    good1 = _write_txt(tmp_path, "good1.txt", "Testo valido documento uno. " * 30)
    bad = str(tmp_path / "bad.xlsx")
    (tmp_path / "bad.xlsx").write_bytes(b"PK fake")
    good2 = _write_txt(tmp_path, "good2.txt", "Testo valido documento due. " * 30)

    results = await pipeline.ingest_batch([good1, bad, good2])

    statuses = [r.status for r in results]
    assert statuses == ["ok", "error", "ok"]


# ---------------------------------------------------------------------------
# Test isolamento workspace
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_corpus_massimario_accettato(mock_db, tmp_path):
    """Regressione: corpus='massimario' deve essere accettato e propagato ai
    chunk. Prima del fix la whitelist era ('studio','dottrina','prassi') e
    'massimario' veniva silenziosamente declassato a 'studio' (i chunk delle
    Rassegne del Massimario finivano nel corpus sbagliato, invisibili al round
    dedicato di Fase 3)."""
    p = Tier1Pipeline(
        mock_db, "test-ws", LegalAnonymizer(use_spacy=False), corpus="massimario",
    )
    assert p.corpus == "massimario"

    fp = _write_txt(tmp_path, "rassegna.txt", "Principio consolidato in materia di sequestro. " * 30)
    result = await p.ingest(fp)
    assert result.status == "ok"

    chunk = await mock_db["chunks"].find_one({"document_id": result.document_id})
    assert chunk is not None
    assert chunk["corpus"] == "massimario"


@pytest.mark.asyncio
async def test_corpus_sconosciuto_fallback_studio(mock_db):
    """Un corpus non riconosciuto resta declassato a 'studio' (comportamento difensivo)."""
    p = Tier1Pipeline(mock_db, "test-ws", LegalAnonymizer(use_spacy=False), corpus="inesistente")
    assert p.corpus == "studio"


@pytest.mark.asyncio
async def test_documents_tagged_with_workspace(mock_db, tmp_path):
    """Due pipeline con workspace diversi non si mescolano."""
    p1 = Tier1Pipeline(mock_db, "studio-alpha", LegalAnonymizer(use_spacy=False))
    p2 = Tier1Pipeline(mock_db, "studio-beta", LegalAnonymizer(use_spacy=False))

    fp1 = _write_txt(tmp_path, "alpha.txt", "Documento studio alpha. " * 30)
    fp2 = _write_txt(tmp_path, "beta.txt", "Documento studio beta. " * 30)

    await p1.ingest(fp1)
    await p2.ingest(fp2)

    alpha_docs = await mock_db["documents"].count_documents({"workspace": "studio-alpha"})
    beta_docs = await mock_db["documents"].count_documents({"workspace": "studio-beta"})

    assert alpha_docs == 1
    assert beta_docs == 1
