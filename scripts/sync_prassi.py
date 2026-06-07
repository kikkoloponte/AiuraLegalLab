"""
Sincronizza la prassi amministrativa (circolari e risoluzioni AdE).

Uso:
  python scripts/sync_prassi.py                        # ultimi 30 giorni
  python scripts/sync_prassi.py --since 2020-01-01     # storico dal 2020
  python scripts/sync_prassi.py --tipo circolare       # solo circolari
  python scripts/sync_prassi.py --tipo risoluzione     # solo risoluzioni
  python scripts/sync_prassi.py --dry-run              # simula senza scrivere
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.prassi.coordinator import PrassiCoordinator
from aiura_legal.prassi.models import EmittentePrassi, TipoPrassi
from aiura_legal.prassi.scrapers.agenzia_entrate import AgenziaEntrateScraper

_DEFAULT_LOOKBACK_DAYS = 30
_TIPO_MAP = {
    "circolare":   TipoPrassi.CIRCOLARE,
    "risoluzione": TipoPrassi.RISOLUZIONE,
}


async def main(args: argparse.Namespace) -> None:
    # Determina data di inizio
    since: date
    if args.since:
        since = date.fromisoformat(args.since)
    else:
        mongo = MongoClient.get()
        await mongo.ping()
        coordinator = PrassiCoordinator(mongo.db)
        last = await coordinator.get_last_sync(EmittentePrassi.AGENZIA_ENTRATE, TipoPrassi.CIRCOLARE)
        since = last or date.today() - timedelta(days=_DEFAULT_LOOKBACK_DAYS)

    # Tipi da scaricare
    tipi: list[TipoPrassi]
    if args.tipo:
        if args.tipo not in _TIPO_MAP:
            logger.error("--tipo deve essere: {}", list(_TIPO_MAP.keys()))
            sys.exit(1)
        tipi = [_TIPO_MAP[args.tipo]]
    else:
        tipi = list(_TIPO_MAP.values())

    logger.info("Sync prassi AdE — dal {} — tipi: {}", since, [t.value for t in tipi])

    # MongoDB
    mongo = MongoClient.get()
    ok = await mongo.ping()
    if not ok:
        logger.error("MongoDB non raggiungibile")
        sys.exit(1)
    coordinator = PrassiCoordinator(mongo.db)
    await coordinator.ensure_indexes()

    # Scraping
    async with AgenziaEntrateScraper() as scraper:
        docs = await scraper.fetch_since(since=since, tipi=tipi)

    logger.info("Trovati {} documenti prassi", len(docs))

    if args.dry_run:
        for doc in docs[:5]:
            logger.info("  [DRY RUN] {} — {} chars", doc.riferimento, len(doc.testo))
        logger.info("[DRY RUN] Totale: {} documenti (non scritti)", len(docs))
        return

    # Ingestione
    stats = await coordinator.ingest(docs)
    logger.success(
        "Sync AdE completato: inserted={} skipped={} errors={}",
        stats["inserted"], stats["skipped"], stats["errors"],
    )

    # Aggiorna cursori
    today = date.today()
    for tipo in tipi:
        await coordinator.update_sync_state(EmittentePrassi.AGENZIA_ENTRATE, tipo, today)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync prassi AmministrativaAdE")
    parser.add_argument("--since", help="Data inizio ISO 8601 (es. 2020-01-01)")
    parser.add_argument("--tipo", help="circolare|risoluzione (default: entrambi)")
    parser.add_argument("--dry-run", action="store_true", help="Simula senza scrivere")
    args = parser.parse_args()
    asyncio.run(main(args))
