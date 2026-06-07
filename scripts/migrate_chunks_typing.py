"""
Migrazione chunk esistenti: aggiunge i campi di tipizzazione (corpus, fonte, testo_tipo)
ai chunk già presenti in aiura_legal.chunks che ne sono privi.

Uso:
  python scripts/migrate_chunks_typing.py
  python scripts/migrate_chunks_typing.py --dry-run
  python scripts/migrate_chunks_typing.py --workspace mio-studio

Logica:
  - Se il chunk ha source="normattiva_it" → corpus="normattiva"
  - Altrimenti                             → corpus="studio"
  - fonte:      "altro" (non possiamo ricostruirla senza il documento sorgente)
  - testo_tipo: "normativo" (default sicuro)

Nota: i nuovi chunk creati da NormattivaPipeline hanno già tutti e tre i campi.
Questo script è un one-shot per allineare i chunk pre-esenti.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pymongo
from loguru import logger

from aiura_legal.ingestion.mongodb.client import settings


def _get_col() -> pymongo.collection.Collection:
    client = pymongo.MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        logger.error(f"MongoDB non raggiungibile: {e}")
        sys.exit(1)
    return client[settings.mongodb_database]["chunks"]


def _migrate(
    col: pymongo.collection.Collection,
    workspace: str | None,
    dry_run: bool,
    batch_size: int,
) -> None:
    """
    Aggiunge corpus/fonte/testo_tipo ai chunk che ne sono privi.
    """
    # Filtra chunk senza tutti e tre i campi
    base_query: dict = {
        "$or": [
            {"corpus":     {"$exists": False}},
            {"fonte":      {"$exists": False}},
            {"testo_tipo": {"$exists": False}},
        ]
    }
    if workspace:
        base_query["workspace"] = workspace

    total = col.count_documents(base_query)
    logger.info(f"Chunk da migrare: {total:,}" + (f" (workspace={workspace})" if workspace else ""))

    if total == 0:
        logger.success("Nessun chunk da migrare. Tutto aggiornato.")
        return

    if dry_run:
        logger.info("[dry-run] Nessuna scrittura. Fine.")
        return

    t0 = time.monotonic()
    processed = 0
    updated = 0

    cursor = col.find(base_query, {"_id": 1, "source": 1}, no_cursor_timeout=True).batch_size(batch_size)
    buffer: list[pymongo.UpdateOne] = []

    for doc in cursor:
        source = doc.get("source", "")
        corpus = "normattiva" if source == "normattiva_it" else "studio"

        buffer.append(
            pymongo.UpdateOne(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "corpus":     corpus,
                        "fonte":      "altro",
                        "testo_tipo": "normativo",
                    }
                },
            )
        )
        processed += 1

        if len(buffer) >= batch_size:
            result = col.bulk_write(buffer, ordered=False)
            updated += result.modified_count
            buffer = []
            elapsed = time.monotonic() - t0
            logger.info(
                f"  {processed:,} chunk processati "
                f"({processed / elapsed:.0f} chunk/s)"
            )

    if buffer:
        result = col.bulk_write(buffer, ordered=False)
        updated += result.modified_count

    elapsed = time.monotonic() - t0
    logger.success(
        f"Migrazione completata: {processed:,} chunk in {elapsed:.1f}s "
        f"({updated:,} aggiornati)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggiunge corpus/fonte/testo_tipo ai chunk pre-esistenti"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta i chunk da migrare senza scrivere")
    parser.add_argument("--workspace", default=None,
                        help="Limita la migrazione a un workspace specifico")
    parser.add_argument("--batch", type=int, default=500,
                        help="Dimensione batch bulk_write (default: 500)")
    args = parser.parse_args()

    col = _get_col()
    _migrate(col, workspace=args.workspace, dry_run=args.dry_run, batch_size=args.batch)


if __name__ == "__main__":
    main()
