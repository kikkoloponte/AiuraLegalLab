"""
Mirror Normattiva: copia legal_lab.normattiva_docs → aiura_legal.normattiva_docs.

Uso:
  python scripts/mirror_normattiva.py
  python scripts/mirror_normattiva.py --dry-run
  python scripts/mirror_normattiva.py --limit 500
  python scripts/mirror_normattiva.py --skip-chunks
  python scripts/mirror_normattiva.py --only-chunks

Flags:
  --dry-run        Conta i doc senza scrivere nulla
  --limit N        Processa solo N documenti (test)
  --batch N        Dimensione batch upsert (default: 500)
  --skip-chunks    Solo mirror normattiva_docs, non crea chunk
  --only-chunks    Presuppone normattiva_docs già popolata: solo chunking
  --filter-tipo    Filtra per tipo_provvedimento (es. LEGGE "DECRETO LEGISLATIVO")
  --skip-formule   Salta i documenti con testo_tipo="formula" al momento del chunk

Convenzione AiUra: questo è uno script CLI → sync (pymongo diretto).
Il chunking asincrono viene wrappato con asyncio.run().
"""
from __future__ import annotations

import argparse
import asyncio
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pymongo
from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient, settings
from aiura_legal.ingestion.normattiva.pipeline import NormattivaPipeline


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_source_col() -> pymongo.collection.Collection:
    """Connessione SYNC READ-ONLY a legal_lab.normattiva_docs."""
    client = pymongo.MongoClient(
        settings.legalagentlab_mongodb_uri,
        serverSelectionTimeoutMS=5000,
    )
    try:
        client.admin.command("ping")
    except Exception as e:
        logger.error(f"MongoDB sorgente non raggiungibile: {e}")
        sys.exit(1)
    return client[settings.legalagentlab_mongodb_database]["normattiva_docs"]


def _get_dest_col() -> pymongo.collection.Collection:
    """Connessione SYNC RW ad aiura_legal.normattiva_docs."""
    uri = settings.mongodb_uri
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        logger.error(f"MongoDB destinazione non raggiungibile: {e}")
        sys.exit(1)
    col = client[settings.mongodb_database]["normattiva_docs"]
    # Indici — drop preventivo per evitare conflitti se già esiste con opzioni diverse
    for idx_name in ("urn_1", "act_urn_1", "testo_tipo_1"):
        try:
            col.drop_index(idx_name)
        except Exception:
            pass  # non esiste: ignora
    col.create_index("urn", unique=True, background=True)
    col.create_index("act_urn", background=True)
    col.create_index("testo_tipo", background=True)
    return col


def _mirror(
    src: pymongo.collection.Collection,
    dst: pymongo.collection.Collection,
    batch_size: int,
    limit: int | None,
    dry_run: bool,
    tipo_filter: list[str] | None,
    urn_filter: list[str] | None = None,
) -> int:
    """
    Copia da src a dst via upsert per URN. Ritorna il numero di doc processati.

    urn_filter: lista di prefissi URN (es. ["urn:nir:stato:regio.decreto:1942-03-16;262"])
                — usa match esatto di prefisso, non regex.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    query: dict = {}
    if tipo_filter:
        query["tipo_provvedimento"] = {"$in": tipo_filter}
    if urn_filter:
        # $or con $regex per ciascun prefisso URN
        query["$or"] = [{"urn": {"$regex": f"^{re.escape(p)}"}} for p in urn_filter]

    total = src.count_documents(query)
    logger.info(f"Documenti in legal_lab.normattiva_docs: {total:,}")
    if limit:
        logger.info(f"Limite: {limit:,}")

    if dry_run:
        logger.info("[dry-run] Nessuna scrittura. Fine.")
        return 0

    processed = 0
    upserted = 0
    t0 = time.monotonic()

    cursor = src.find(query, no_cursor_timeout=True).batch_size(batch_size)
    buffer: list[pymongo.UpdateOne] = []

    for doc in cursor:
        if limit and processed >= limit:
            break

        urn = doc.get("urn", "")
        if not urn:
            continue

        # Aggiunge il timestamp di import AiUra e rimuove l'_id sorgente
        doc_to_write = {k: v for k, v in doc.items() if k != "_id"}
        doc_to_write["aiura_imported_at"] = now_iso

        buffer.append(
            pymongo.UpdateOne(
                {"urn": urn},
                {"$set": doc_to_write},
                upsert=True,
            )
        )
        processed += 1

        if len(buffer) >= batch_size:
            result = dst.bulk_write(buffer, ordered=False)
            upserted += result.upserted_count + result.modified_count
            buffer = []
            elapsed = time.monotonic() - t0
            logger.info(
                f"  {processed:,} doc processati "
                f"({processed / elapsed:.0f} doc/s)"
            )

    if buffer:
        result = dst.bulk_write(buffer, ordered=False)
        upserted += result.upserted_count + result.modified_count

    elapsed = time.monotonic() - t0
    logger.success(
        f"Mirror completato: {processed:,} doc in {elapsed:.1f}s "
        f"({upserted:,} scritti/aggiornati)"
    )
    return processed


async def _chunk_collection(workspace: str, skip_formule: bool, limit: int | None) -> None:
    """Chunka la collection normattiva_docs (async, usa motor)."""
    mongo = MongoClient.get()
    pipeline = NormattivaPipeline(
        mongo_db=mongo.db,
        workspace=workspace,
        skip_formule=skip_formule,
    )
    result = await pipeline.chunk_collection(limit=limit)
    logger.success(
        f"Chunking completato: {result.docs_processed} doc → "
        f"{result.chunks_created} chunk ({result.errors} errori)"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mirror legal_lab.normattiva_docs → aiura_legal.normattiva_docs"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta i doc senza scrivere")
    parser.add_argument("--limit", type=int, default=None,
                        help="Numero massimo di documenti da processare")
    parser.add_argument("--batch", type=int, default=500,
                        help="Dimensione batch upsert (default: 500)")
    parser.add_argument("--skip-chunks", action="store_true",
                        help="Solo mirror, non crea chunk")
    parser.add_argument("--only-chunks", action="store_true",
                        help="Solo chunking (normattiva_docs già popolata)")
    parser.add_argument("--workspace", default="mio-studio",
                        help="Workspace per i chunk (default: mio-studio)")
    parser.add_argument("--filter-tipo", nargs="+", default=None,
                        metavar="TIPO",
                        help="Filtra per tipo_provvedimento (es. LEGGE)")
    parser.add_argument("--filter-urn", nargs="+", default=None,
                        metavar="URN",
                        help=(
                            "Filtra per prefisso URN (es. "
                            "urn:nir:stato:regio.decreto:1942-03-16;262). "
                            "Accetta piu prefissi separati da spazio."
                        ))
    parser.add_argument("--skip-formule", action="store_true",
                        help="Non chunka i documenti con testo_tipo=formula")
    args = parser.parse_args()

    if not args.only_chunks:
        src = _get_source_col()
        dst = _get_dest_col()
        _mirror(
            src=src,
            dst=dst,
            batch_size=args.batch,
            limit=args.limit,
            dry_run=args.dry_run,
            tipo_filter=args.filter_tipo,
            urn_filter=args.filter_urn,
        )

    if not args.skip_chunks and not args.dry_run:
        logger.info(f"Avvio chunking → workspace '{args.workspace}'")
        asyncio.run(_chunk_collection(
            workspace=args.workspace,
            skip_formule=args.skip_formule,
            limit=args.limit,
        ))


if __name__ == "__main__":
    main()
