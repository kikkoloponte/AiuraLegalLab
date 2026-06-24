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


def _make_doc(
    numero: str = "1",
    channel: SourceChannel = SourceChannel.SCRAPING,
    motivazione: str = "La motivazione.",
) -> JurisprudenceDocument:
    return JurisprudenceDocument(
        organo=OrganoGiudicante.CASSAZIONE,
        numero=numero,
        anno=2024,
        data_deposito=date(2024, 3, 1),
        sezione="III Civile",
        materia="contratti",
        massima="La massima.",
        motivazione=motivazione,
        dispositivo="Il dispositivo.",
        source_channel=channel,
    )


def _make_doc_long_motivazione(num_words: int = 5000) -> JurisprudenceDocument:
    """Sentenza con motivazione lunga (> 512 token) per test chunking."""
    # ~4 caratteri/parola media in italiano + spazio → ~5 token/parola con tiktoken
    # 5000 parole ~= ~4000+ token
    parola = "motivazione responsabilità contrattuale inadempimento risarcimento"
    text = (parola + " ") * num_words
    return _make_doc(motivazione=text)


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
# to_chunks — comportamento base
# ---------------------------------------------------------------------------

def test_to_chunks_massima_e_dispositivo_monolitici():
    """Massima e dispositivo restano chunk singoli (ID senza indice numerico)."""
    doc = _make_doc()
    chunks = to_chunks(doc)
    ids = [c.id for c in chunks]
    assert f"{doc.id}_massima" in ids
    assert f"{doc.id}_dispositivo" in ids


def test_to_chunks_motivazione_breve_singolo_chunk():
    """Motivazione < 512 token → 1 chunk con ID {hex16}_motivazione_000."""
    doc = _make_doc(motivazione="Breve motivazione.")
    chunks = to_chunks(doc)
    mot_chunks = [c for c in chunks if c.metadata["chunk_type"] == "motivazione"]
    assert len(mot_chunks) == 1
    assert mot_chunks[0].id == f"{doc.id}_motivazione_000"
    assert mot_chunks[0].metadata["chunk_index"] == 0


def test_to_chunks_motivazione_lunga_multipli_chunk():
    """Motivazione > 512 token → N chunk con ID {hex16}_motivazione_{i:03d}."""
    doc = _make_doc_long_motivazione(num_words=3000)
    chunks = to_chunks(doc)
    mot_chunks = [c for c in chunks if c.metadata["chunk_type"] == "motivazione"]
    # Con ~3k parole (~12k token) e Chunker(512, 64) ci aspettiamo molti chunk
    assert len(mot_chunks) > 1, f"Attesi >1 chunk, ottenuti {len(mot_chunks)}"
    # Verifica indici consecutivi a partire da 0
    for i, ch in enumerate(mot_chunks):
        assert ch.id == f"{doc.id}_motivazione_{i:03d}"
        assert ch.metadata["chunk_index"] == i


def test_to_chunks_overlap_corretto():
    """I chunk motivazione si sovrappongono (overlap 64 token)."""
    doc = _make_doc_long_motivazione(num_words=1000)
    chunks = to_chunks(doc)
    mot_chunks = [c for c in chunks if c.metadata["chunk_type"] == "motivazione"]
    if len(mot_chunks) < 2:
        pytest.skip("Motivazione troppo corta per testare overlap")
    # Verifico che chunk[1] inizi con la coda di chunk[0]
    # (overlap = i token finali del chunk precedente compaiono all'inizio del successivo)
    end_of_first = mot_chunks[0].text[-50:]  # ultimi 50 caratteri
    start_of_second = mot_chunks[1].text[:200]
    # L'overlap garantisce che parte del testo si sovrapponga
    # (almeno qualche parola in comune)
    words_first_end = set(end_of_first.split())
    words_second_start = set(start_of_second.split())
    assert words_first_end & words_second_start, "Nessuna sovrapposizione rilevata"


def test_to_chunks_integrità_massima():
    """La massima NON viene spezzata anche se > 512 token."""
    massima_lunga = "La massima della corte. " * 200  # ~2400 token circa
    doc = _make_doc(motivazione="Breve.")
    doc.massima = massima_lunga
    chunks = to_chunks(doc)
    massima_chunks = [c for c in chunks if c.metadata["chunk_type"] == "massima"]
    assert len(massima_chunks) == 1
    assert massima_chunks[0].id == f"{doc.id}_massima"
    assert massima_chunks[0].text == massima_lunga


def test_to_chunks_id_univoci():
    doc = _make_doc_long_motivazione(num_words=2000)
    chunks = to_chunks(doc)
    ids = [c.id for c in chunks]
    assert len(ids) == len(set(ids))


def test_to_chunks_jdoc_id():
    doc = _make_doc_long_motivazione(num_words=2000)
    chunks = to_chunks(doc)
    assert all(c.metadata["jdoc_id"] == doc.id for c in chunks)


def test_to_chunks_corpus_giurisprudenza():
    doc = _make_doc()
    chunks = to_chunks(doc)
    assert all(c.metadata["corpus"] == "giurisprudenza" for c in chunks)


def test_to_chunks_salta_testo_vuoto():
    doc = _make_doc()
    doc.massima = ""
    chunks = to_chunks(doc)
    types = {c.metadata["chunk_type"] for c in chunks}
    assert "massima" not in types


def test_to_chunks_metadati_chunk_index():
    """chunk_index deve essere presente in tutti i chunk."""
    doc = _make_doc_long_motivazione(num_words=2000)
    chunks = to_chunks(doc)
    for c in chunks:
        assert "chunk_index" in c.metadata


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
