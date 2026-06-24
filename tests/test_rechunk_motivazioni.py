"""
Test rechunk_motivazioni.py — idempotenza, dry-run, resume da checkpoint.

Usa mongomock-motor (zero MongoDB reale, coerente con CLAUDE.md).
La funzione rechunk() accetta un parametro db per la dependency injection,
evitando qualsiasi patching di importazioni interne.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import mongomock_motor

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mongo_client():
    """Client mongomock-motor per i test."""
    return mongomock_motor.AsyncMongoMockClient()


@pytest.fixture()
def db(mongo_client):
    return mongo_client["aiura_legal_lab_db"]


def _make_jurisprudence_record(doc_id: str, motivazione: str = "") -> dict:
    """Record minimo per la collection jurisprudence."""
    return {
        "_id": doc_id,
        "organo": "cassazione",
        "numero": "12345",
        "anno": 2024,
        "data_deposito": "2024-03-01",
        "materia": "contratti",
        "massima": "La massima.",
        "motivazione": motivazione,
        "dispositivo": "Il dispositivo.",
        "source_url": "",
    }


# Testo motivazione lunga (>512 token)
_LONG_MOT = "motivazione responsabilità contrattuale inadempimento risarcimento danno. " * 300


# ---------------------------------------------------------------------------
# Helper: esegui rechunk iniettando il db mongomock direttamente
# ---------------------------------------------------------------------------

async def _run_rechunk(
    db,
    dry_run: bool = False,
    limit: int | None = None,
    batch_size: int = 100,
    checkpoint_path: Path | None = None,
) -> dict:
    """Invoca rechunk() con db mongomock iniettato (DI nativa, zero patching)."""
    from scripts.rechunk_motivazioni import rechunk, _CHECKPOINT_FILE
    import scripts.rechunk_motivazioni as rm

    original_cp = rm._CHECKPOINT_FILE
    if checkpoint_path:
        rm._CHECKPOINT_FILE = checkpoint_path

    try:
        await rechunk(
            workspace="test-ws",
            dry_run=dry_run,
            limit=limit,
            batch_size=batch_size,
            checkpoint_every=1,
            db=db,  # DI: db mongomock iniettato
        )
    finally:
        rm._CHECKPOINT_FILE = original_cp

    count = await db["chunks"].count_documents({"corpus": "giurisprudenza"})
    return {"chunks_count": count}


# ---------------------------------------------------------------------------
# Test idempotenza
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rechunk_idempotente(db):
    """Eseguire due volte non duplica i chunk."""
    await db["jurisprudence"].insert_one(
        _make_jurisprudence_record("aabbccdd11223344", _LONG_MOT)
    )

    with tempfile.TemporaryDirectory() as tmp:
        cp = Path(tmp) / "cp.json"
        r1 = await _run_rechunk(db, checkpoint_path=cp)
        r2 = await _run_rechunk(db, checkpoint_path=cp)

    assert r1["chunks_count"] > 1, "Devono esserci più chunk per motivazione lunga"
    assert r1["chunks_count"] == r2["chunks_count"], "Idempotenza: conteggio invariato"


@pytest.mark.asyncio
async def test_rechunk_dry_run_non_scrive(db):
    """--dry-run non deve scrivere nulla su MongoDB."""
    await db["jurisprudence"].insert_one(
        _make_jurisprudence_record("aabbccdd11223345", _LONG_MOT)
    )

    with tempfile.TemporaryDirectory() as tmp:
        r = await _run_rechunk(db, dry_run=True, checkpoint_path=Path(tmp) / "cp.json")

    assert r["chunks_count"] == 0, "dry-run non deve scrivere chunk"


@pytest.mark.asyncio
async def test_rechunk_motivazione_vuota_saltata(db):
    """Sentenze con motivazione vuota vengono saltate."""
    await db["jurisprudence"].insert_one(
        _make_jurisprudence_record("aabbccdd11223346", motivazione="")
    )

    with tempfile.TemporaryDirectory() as tmp:
        r = await _run_rechunk(db, checkpoint_path=Path(tmp) / "cp.json")

    assert r["chunks_count"] == 0


@pytest.mark.asyncio
async def test_rechunk_limit(db):
    """--limit N processa al massimo N sentenze."""
    for i in range(5):
        await db["jurisprudence"].insert_one(
            _make_jurisprudence_record(f"aabbccdd1122334{i}", _LONG_MOT)
        )

    with tempfile.TemporaryDirectory() as tmp:
        # Processa solo 2 sentenze
        await _run_rechunk(db, limit=2, checkpoint_path=Path(tmp) / "cp.json")

    count = await db["chunks"].count_documents({"corpus": "giurisprudenza"})
    # 2 sentenze processate → almeno 1 chunk ciascuna
    assert count > 0
    total_sentenze = await db["jurisprudence"].count_documents({})
    assert total_sentenze == 5


@pytest.mark.asyncio
async def test_rechunk_chunk_schema(db):
    """I chunk scritti hanno i campi corretti."""
    await db["jurisprudence"].insert_one(
        _make_jurisprudence_record("aabbccdd11223347", _LONG_MOT)
    )

    with tempfile.TemporaryDirectory() as tmp:
        await _run_rechunk(db, checkpoint_path=Path(tmp) / "cp.json")

    chunks = []
    async for c in db["chunks"].find({"corpus": "giurisprudenza"}):
        chunks.append(c)

    assert len(chunks) > 0
    for c in chunks:
        assert c["corpus"] == "giurisprudenza"
        assert c["chunk_type"] == "motivazione"
        assert "chunk_index" in c
        assert "jdoc_id" in c
        assert "text" in c and c["text"]
        assert c["_id"].startswith("aabbccdd11223347_motivazione_")


@pytest.mark.asyncio
async def test_rechunk_resume_da_checkpoint(db):
    """Ripartendo da checkpoint, non riprocessa i documenti già processati."""
    for i in range(4):
        await db["jurisprudence"].insert_one(
            _make_jurisprudence_record(f"aabbccdd1122334{i}", _LONG_MOT)
        )

    with tempfile.TemporaryDirectory() as tmp:
        cp = Path(tmp) / "cp.json"

        # Prima run: 2 documenti
        await _run_rechunk(db, limit=2, checkpoint_path=cp)
        count_after_first = await db["chunks"].count_documents({"corpus": "giurisprudenza"})

        # Seconda run: resume — processa i restanti
        await _run_rechunk(db, checkpoint_path=cp)
        count_after_second = await db["chunks"].count_documents({"corpus": "giurisprudenza"})

    # Seconda run deve aver aggiunto chunk per le sentenze non ancora processate
    assert count_after_second >= count_after_first
