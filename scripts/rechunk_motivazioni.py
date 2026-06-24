#!/usr/bin/env python3
"""
rechunk_motivazioni.py — Re-chunking geometrico delle motivazioni giurisprudenziali.

Legge dalla collection MongoDB `jurisprudence`, applica Chunker(512, 64) alle
motivazioni e scrive i sub-chunk nella collection `chunks` (corpus="giurisprudenza").

IDEMPOTENTE: salta i chunk gia' presenti (check per _id).
RESUME-SAFE: checkpoint JSON salva l'ultimo doc_id processato.
              Alla ripartenza riprende da subito dopo l'ultimo checkpoint.

Uso:
  python scripts/rechunk_motivazioni.py --workspace mio-studio
  python scripts/rechunk_motivazioni.py --dry-run --limit 100
  python scripts/rechunk_motivazioni.py --batch-size 200 --checkpoint-every 5
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

_CHECKPOINT_FILE = Path("rechunk_motivazioni_checkpoint.json")
_DEFAULT_BATCH = 500
_DEFAULT_CHECKPOINT_EVERY = 10   # ogni 10 batch = ogni 5.000 doc

_JURISPRUDENCE_COLLECTION = "jurisprudence"
_CHUNKS_COLLECTION = "chunks"


# ---------------------------------------------------------------------------
# Checkpoint helpers
# ---------------------------------------------------------------------------

def _load_checkpoint() -> dict:
    if _CHECKPOINT_FILE.exists():
        try:
            with open(_CHECKPOINT_FILE, encoding="utf-8") as f:
                cp = json.load(f)
            logger.info(
                "Checkpoint trovato: processati={} ultimo_id={}",
                cp.get("processed", 0), cp.get("last_id", "—"),
            )
            return cp
        except Exception as e:
            logger.warning("Checkpoint illeggibile ({}): parto da zero", e)
    return {}


def _save_checkpoint(last_id: str, processed: int, chunks_written: int) -> None:
    cp = {
        "last_id": last_id,
        "processed": processed,
        "chunks_written": chunks_written,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    with open(_CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(cp, f, ensure_ascii=False, indent=2)


def _clear_checkpoint() -> None:
    if _CHECKPOINT_FILE.exists():
        _CHECKPOINT_FILE.unlink()
        logger.info("Checkpoint rimosso (elaborazione completata)")


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

async def rechunk(
    workspace: str,
    dry_run: bool = False,
    limit: Optional[int] = None,
    batch_size: int = _DEFAULT_BATCH,
    checkpoint_every: int = _DEFAULT_CHECKPOINT_EVERY,
    db=None,  # motor AsyncIOMotorDatabase; se None usa MongoDB reale
) -> None:
    """Esegue il rechunking delle motivazioni giurisprudenziali.

    Args:
        workspace:        nome workspace (usato nel log)
        dry_run:          se True, non scrive nulla su MongoDB
        limit:            numero massimo di sentenze da processare
        batch_size:       dimensione del batch di lettura da MongoDB
        checkpoint_every: salva il checkpoint ogni N batch
        db:               database motor iniettato (per test con mongomock);
                          se None viene aperta la connessione reale da .env
    """
    from aiura_legal.ingestion.chunker import Chunker
    from aiura_legal.jurisprudence.coordinator import _MOTIVAZIONE_MAX_TOKENS, _MOTIVAZIONE_OVERLAP

    chunker = Chunker(max_tokens=_MOTIVAZIONE_MAX_TOKENS, overlap=_MOTIVAZIONE_OVERLAP)

    # Connessione DB: usa quella iniettata (test) o apre la connessione reale
    if db is None:
        import motor.motor_asyncio as motor_async
        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        mongo_client = motor_async.AsyncIOMotorClient(mongo_uri)
        db = mongo_client["aiura_legal_lab_db"]

    # Carica checkpoint
    cp = _load_checkpoint()
    last_id = cp.get("last_id")
    already_processed = cp.get("processed", 0)
    already_chunks = cp.get("chunks_written", 0)

    # Filtro MongoDB: resume dopo l'ultimo id processato
    mongo_filter: dict = {}
    if last_id:
        mongo_filter["_id"] = {"$gt": last_id}
        logger.info("Resume: skippo fino a _id > {}", last_id)

    total_db = await db[_JURISPRUDENCE_COLLECTION].count_documents(mongo_filter)
    if limit:
        total_db = min(total_db, limit)
    logger.info(
        "Sentenze da processare: {:,} (workspace={}, dry_run={}, limit={})",
        total_db, workspace, dry_run, limit,
    )

    if total_db == 0:
        logger.success("Nulla da fare.")
        return

    # Pre-calcola gli ID di chunk gia' presenti in chunks (per idempotenza)
    # Legge i doc_id esistenti con corpus=giurisprudenza per filtrare i doppioni
    logger.info("Calcolo chunk giurisprudenza gia' presenti...")
    existing_chunk_ids: set[str] = set()
    async for rec in db[_CHUNKS_COLLECTION].find(
        {"corpus": "giurisprudenza"}, {"_id": 1}
    ):
        existing_chunk_ids.add(str(rec["_id"]))
    logger.info("Chunk giurisprudenza esistenti: {:,}", len(existing_chunk_ids))

    processed = 0
    chunks_written = 0
    skipped_doc = 0
    skipped_chunk = 0
    batch_num = 0
    t_start = time.perf_counter()
    current_last_id: str = last_id or ""

    cursor = db[_JURISPRUDENCE_COLLECTION].find(mongo_filter).sort("_id", 1)

    async for record in cursor:
        doc_id = str(record["_id"])
        motivazione = record.get("motivazione", "") or ""

        if not motivazione.strip():
            skipped_doc += 1
            current_last_id = doc_id
            processed += 1
            continue

        # Genera sub-chunk
        sub_chunks = chunker.chunk(motivazione)
        texts = [c.text for c in sub_chunks] if sub_chunks else [motivazione]

        # Costruisci i documenti chunk da inserire
        chunk_docs = []
        for i, chunk_text in enumerate(texts):
            chunk_id = f"{doc_id}_motivazione_{i:03d}"
            if chunk_id in existing_chunk_ids:
                skipped_chunk += 1
                continue
            chunk_docs.append({
                "_id": chunk_id,
                "corpus": "giurisprudenza",
                "chunk_type": "motivazione",
                "chunk_index": i,
                "source_id": doc_id,   # soddisfa unique index (source_id, chunk_index, workspace)
                "jdoc_id": doc_id,
                "text": chunk_text,
                "organo": record.get("organo", ""),
                "numero": record.get("numero", ""),
                "anno": record.get("anno", ""),
                "materia": record.get("materia", ""),
                "data_deposito": record.get("data_deposito", ""),
                "source_url": record.get("source_url", ""),
                "rechunked_at": datetime.now(timezone.utc).isoformat(),
            })

        if chunk_docs:
            n_inserted = len(chunk_docs) if dry_run else 0
            if not dry_run:
                try:
                    result = await db[_CHUNKS_COLLECTION].insert_many(
                        chunk_docs, ordered=False
                    )
                    n_inserted = len(result.inserted_ids)
                except Exception as exc:
                    from pymongo.errors import BulkWriteError
                    if isinstance(exc, BulkWriteError):
                        n_inserted = exc.details.get("nInserted", 0)
                        n_dup = len(exc.details.get("writeErrors", []))
                        if n_dup:
                            logger.debug("insert_many: {} inseriti, {} duplicati", n_inserted, n_dup)
                    else:
                        logger.warning("insert_many fallito: {}", exc)
            chunks_written += n_inserted
            # Aggiorna cache locale per evitare re-check al prossimo batch
            for d in chunk_docs:
                existing_chunk_ids.add(d["_id"])

        processed += 1
        current_last_id = doc_id
        batch_num = processed // batch_size

        # Checkpoint periodico
        if processed % batch_size == 0:
            elapsed = time.perf_counter() - t_start
            rate = processed / elapsed if elapsed > 0 else 0
            eta_s = (total_db - processed) / rate if rate > 0 else 0
            logger.info(
                "  [{}/{}] proc={:,} chunks_scritti={:,} skip_doc={:,} skip_chunk={:,} "
                "rate={:.0f} doc/s ETA={:.0f}s",
                processed, total_db, processed, chunks_written,
                skipped_doc, skipped_chunk, rate, eta_s,
            )
            if batch_num % checkpoint_every == 0 and not dry_run:
                _save_checkpoint(current_last_id, processed + already_processed,
                                 chunks_written + already_chunks)

        if limit and processed >= limit:
            break

    # Flush checkpoint finale
    if not dry_run:
        _save_checkpoint(current_last_id, processed + already_processed,
                         chunks_written + already_chunks)

    elapsed = time.perf_counter() - t_start
    logger.success(
        "Rechunking completato{}:\n"
        "  Sentenze processate : {:,}\n"
        "  Chunk scritti       : {:,}\n"
        "  Doc saltati (vuoti) : {:,}\n"
        "  Chunk saltati (dup) : {:,}\n"
        "  Tempo               : {:.1f}s",
        " [DRY-RUN]" if dry_run else "",
        processed, chunks_written, skipped_doc, skipped_chunk, elapsed,
    )

    # Se completamento totale senza limit, pulisci il checkpoint
    if not dry_run and not limit and processed + already_processed >= total_db:
        _clear_checkpoint()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Re-chunking motivazioni giurisprudenziali (idempotente, resume-safe)"
    )
    parser.add_argument(
        "--workspace", default="mio-studio",
        help="Nome workspace (default: mio-studio)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Non scrive nulla su MongoDB (solo log)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Numero massimo di sentenze da processare",
    )
    parser.add_argument(
        "--batch-size", type=int, default=_DEFAULT_BATCH,
        help=f"Sentenze per batch (default: {_DEFAULT_BATCH})",
    )
    parser.add_argument(
        "--checkpoint-every", type=int, default=_DEFAULT_CHECKPOINT_EVERY,
        help=f"Salva checkpoint ogni N batch (default: {_DEFAULT_CHECKPOINT_EVERY})",
    )
    args = parser.parse_args()
    asyncio.run(rechunk(
        workspace=args.workspace,
        dry_run=args.dry_run,
        limit=args.limit,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
    ))
