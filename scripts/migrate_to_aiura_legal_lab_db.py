"""
Migrazione database: unifica tutto in aiura_legal_lab_db.

Copia:
  legal_lab.normattiva_docs        → aiura_legal_lab_db.normattiva_docs  (166k)
  aiura_legal.jurisprudence        → aiura_legal_lab_db.jurisprudence    (58k)
  aiura_legal.sync_state           → aiura_legal_lab_db.sync_state       (4)

Salta (dati stale/test):
  aiura_legal.chunks               → eliminato
  aiura_legal.wiki_pages           → eliminato
  aiura_legal.normattiva_docs      → sostituito dalla copia completa da legal_lab

Uso:
  python scripts/migrate_to_aiura_legal_lab_db.py
  python scripts/migrate_to_aiura_legal_lab_db.py --dry-run
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import motor.motor_asyncio
from loguru import logger

_MONGO_URI = "mongodb://localhost:27017"
_TARGET_DB = "aiura_legal_lab_db"
_BATCH_SIZE = 500


async def copy_collection(
    src_db,
    src_coll: str,
    dst_db,
    dst_coll: str,
    dry_run: bool,
) -> int:
    """Copia tutti i documenti da src a dst. Ritorna il numero di doc copiati."""
    src = src_db[src_coll]
    dst = dst_db[dst_coll]

    total = await src.count_documents({})
    if total == 0:
        logger.warning("  {} vuota — saltata", src_coll)
        return 0

    # Verifica se già popolata
    existing = await dst.count_documents({})
    if existing > 0:
        logger.info("  {}: già presenti {:,} doc nel target — skip", dst_coll, existing)
        return existing

    logger.info("  Copia {} → {} ({:,} documenti)...", src_coll, dst_coll, total)

    if dry_run:
        logger.info("  [DRY RUN] saltato")
        return total

    t0 = time.monotonic()
    batch = []
    count = 0

    async for doc in src.find({}):
        batch.append(doc)
        if len(batch) >= _BATCH_SIZE:
            await dst.insert_many(batch, ordered=False)
            count += len(batch)
            batch = []
            if count % 10_000 == 0:
                elapsed = time.monotonic() - t0
                logger.info("    {:,} / {:,}  ({:.0f}s)", count, total, elapsed)

    if batch:
        await dst.insert_many(batch, ordered=False)
        count += len(batch)

    elapsed = time.monotonic() - t0
    logger.success("  {} copiati in {:.1f}s", count, elapsed)
    return count


async def migrate(dry_run: bool) -> None:
    client = motor.motor_asyncio.AsyncIOMotorClient(_MONGO_URI)

    src_legal_lab = client["legal_lab"]
    src_aiura     = client["aiura_legal"]
    target        = client[_TARGET_DB]

    logger.info("=== Migrazione → {} ===", _TARGET_DB)
    if dry_run:
        logger.info("[DRY RUN] — nessuna scrittura")

    # ── 1. normattiva_docs da legal_lab (completa) ───────────────────────
    logger.info("\n[1/3] normattiva_docs (legal_lab → {})", _TARGET_DB)
    n_norm = await copy_collection(
        src_legal_lab, "normattiva_docs",
        target, "normattiva_docs",
        dry_run,
    )

    # ── 2. jurisprudence da aiura_legal ───────────────────────────────────
    logger.info("\n[2/3] jurisprudence (aiura_legal → {})", _TARGET_DB)
    n_jur = await copy_collection(
        src_aiura, "jurisprudence",
        target, "jurisprudence",
        dry_run,
    )

    # ── 3. sync_state da aiura_legal ──────────────────────────────────────
    logger.info("\n[3/3] sync_state (aiura_legal → {})", _TARGET_DB)
    n_sync = await copy_collection(
        src_aiura, "sync_state",
        target, "sync_state",
        dry_run,
    )

    # ── Crea indici ───────────────────────────────────────────────────────
    if not dry_run:
        logger.info("\nCreazione indici...")
        # jurisprudence: indice su organo + anno + numero (dedup)
        await target["jurisprudence"].create_index(
            [("organo", 1), ("numero", 1), ("anno", 1)], unique=True, background=True
        )
        # normattiva_docs: indice su urn (dedup)
        await target["normattiva_docs"].create_index(
            [("urn", 1)], background=True, sparse=True
        )
        # sync_state: indice su organo
        await target["sync_state"].create_index([("organo", 1)], unique=True, background=True)
        logger.success("Indici creati")

    # ── Riepilogo ─────────────────────────────────────────────────────────
    logger.info("\n=== Riepilogo ===")
    logger.success("  normattiva_docs:  {:,}", n_norm)
    logger.success("  jurisprudence:    {:,}", n_jur)
    logger.success("  sync_state:       {:,}", n_sync)

    if not dry_run:
        # Verifica finale
        collections = await target.list_collection_names()
        logger.info("\nCollezioni in {}:", _TARGET_DB)
        for c in sorted(collections):
            n = await target[c].count_documents({})
            logger.info("  {:30s} {:>10,}", c, n)

        logger.success(
            "\nMigrazione completata. Aggiorna .env:\n"
            "  MONGODB_DATABASE={}",
            _TARGET_DB,
        )
    else:
        logger.info("[DRY RUN] completato — nessuna scrittura effettuata")

    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migra DB verso aiura_legal_lab_db")
    parser.add_argument("--dry-run", action="store_true", help="Simula senza scrivere")
    args = parser.parse_args()
    asyncio.run(migrate(args.dry_run))
