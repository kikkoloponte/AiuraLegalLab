"""
Normalizza whitespace/tipografia dei chunk già presenti in aiura_legal_lab_db.chunks.

Vedi: docs/superpowers/specs/2026-06-28-chunk-text-normalizer-design.md
La normalizzazione (aiura_legal/ingestion/text_normalizer.py) è già applicata ai
chunk nuovi in fase di ingestione (aiura_legal/ingestion/chunker.py). Questo
script applica la stessa pulizia ai chunk già indicizzati prima di questa modifica.

Uso:
  python scripts/normalize_existing_chunks.py --dry-run
  python scripts/normalize_existing_chunks.py --apply
  python scripts/normalize_existing_chunks.py --apply --corpus normattiva

Dopo --apply, ricostruisci gli indici sul testo aggiornato:
  python scripts/build_indexes.py --workspace mio-studio --corpus <corpus>
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione   (per giurisprudenza)
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from loguru import logger
from pymongo import UpdateOne

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.ingestion.text_normalizer import normalize_text

_BATCH_SIZE = 500


async def normalize_chunks(corpus: str | None, dry_run: bool) -> None:
    mongo = MongoClient.get()
    chunks = mongo.db["chunks"]

    filter_query: dict = {"corpus": corpus} if corpus else {}

    total = 0
    changed = 0
    ops: list[UpdateOne] = []
    per_corpus_changed: dict[str, int] = {}

    cursor = chunks.find(filter_query, {"_id": 1, "text": 1, "sommario": 1, "corpus": 1})
    async for chunk in cursor:
        total += 1
        update: dict = {}

        text = chunk.get("text", "")
        normalized_text = normalize_text(text)
        if normalized_text != text:
            update["text"] = normalized_text

        sommario = chunk.get("sommario")
        if sommario:
            normalized_sommario = normalize_text(sommario)
            if normalized_sommario != sommario:
                update["sommario"] = normalized_sommario

        if update:
            changed += 1
            chunk_corpus = chunk.get("corpus", "unknown")
            per_corpus_changed[chunk_corpus] = per_corpus_changed.get(chunk_corpus, 0) + 1
            if not dry_run:
                ops.append(UpdateOne({"_id": chunk["_id"]}, {"$set": update}))
                if len(ops) >= _BATCH_SIZE:
                    await chunks.bulk_write(ops, ordered=False)
                    ops = []

    if ops:
        await chunks.bulk_write(ops, ordered=False)

    breakdown = " | ".join(f"{c}={n}" for c, n in sorted(per_corpus_changed.items())) or "nessuno"
    logger.success(
        f"{'[DRY-RUN] ' if dry_run else ''}Chunk ispezionati: {total:,}  |  "
        f"da modificare: {changed:,}  ({breakdown})"
    )


async def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--dry-run", action="store_true", help="Conta senza scrivere (default)")
    parser.add_argument("--apply", action="store_true", help="Applica la normalizzazione sui chunk")
    parser.add_argument("--corpus", default=None,
                         choices=["normattiva", "studio", "dottrina", "giurisprudenza", "massimario"],
                         help="Limita la normalizzazione a un corpus")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        logger.info("Nessun flag specificato — eseguo in modalità --dry-run.")
        args.dry_run = True

    await normalize_chunks(corpus=args.corpus, dry_run=not args.apply)

    if args.dry_run:
        logger.info(
            "Dry-run completato. Per applicare: "
            "python scripts/normalize_existing_chunks.py --apply"
            + (f" --corpus {args.corpus}" if args.corpus else "")
        )
    else:
        logger.info(
            "Normalizzazione applicata. Ricostruisci gli indici sul testo aggiornato: "
            "python scripts/build_indexes.py --workspace mio-studio"
            + (f" --corpus {args.corpus}" if args.corpus else "")
        )


if __name__ == "__main__":
    asyncio.run(main())
