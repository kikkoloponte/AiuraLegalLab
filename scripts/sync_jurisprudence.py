"""
Batch settimanale per sincronizzare la giurisprudenza dalle 4 fonti pubbliche.

Uso:
  python scripts/sync_jurisprudence.py                        # ultimi 7 giorni
  python scripts/sync_jurisprudence.py --source cassazione
  python scripts/sync_jurisprudence.py --since 2024-01-01
  python scripts/sync_jurisprudence.py --initial-load         # caricamento storico 2 anni
  python scripts/sync_jurisprudence.py --dry-run

Ogni fonte ha il proprio cursore last_sync in aiura_legal.sync_state
— il fallimento di una fonte non blocca le altre.
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
from aiura_legal.jurisprudence.coordinator import JurisprudenceCoordinator
from aiura_legal.jurisprudence.models import OrganoGiudicante
from aiura_legal.jurisprudence.parser import parse_html, parse_pdf
from aiura_legal.jurisprudence.scrapers import (
    CassazioneScraper,
    CorteContiScraper,
    CorteCostScraper,
    GiustiziaAmmScraper,
)
from aiura_legal.jurisprudence.scrapers.cassazione import _MAX_RESULTS_INITIAL, _RATE_LIMIT_INITIAL

_SCRAPER_MAP = {
    OrganoGiudicante.CASSAZIONE: CassazioneScraper,
    OrganoGiudicante.TAR: GiustiziaAmmScraper,
    OrganoGiudicante.CORTE_COST: CorteCostScraper,
    OrganoGiudicante.CORTE_CONTI: CorteContiScraper,
}

_DEFAULT_LOOKBACK_DAYS = 7        # sync settimanale
_INITIAL_LOAD_YEARS = 5           # caricamento storico (era 2)


async def sync_source(
    organo: OrganoGiudicante,
    coordinator: JurisprudenceCoordinator,
    since: date | None,
    dry_run: bool,
    initial_load: bool = False,
) -> dict:
    last_sync = since or await coordinator.get_last_sync(organo)
    if last_sync is None:
        if initial_load:
            last_sync = date.today() - timedelta(days=365 * _INITIAL_LOAD_YEARS)
        else:
            last_sync = date.today() - timedelta(days=_DEFAULT_LOOKBACK_DAYS)

    scraper_cls = _SCRAPER_MAP[organo]
    logger.info("Sync {}: dal {} (initial_load={})", organo.value, last_sync, initial_load)

    try:
        async with scraper_cls() as scraper:
            # Cassazione supporta max_results esplicito per il caricamento storico
            if initial_load and hasattr(scraper, "fetch_since"):
                import inspect
                sig = inspect.signature(scraper.fetch_since)
                if "max_results" in sig.parameters:
                    raw_list = await scraper.fetch_since(
                        last_sync,
                        max_results=_MAX_RESULTS_INITIAL,
                        rate_limit=_RATE_LIMIT_INITIAL,
                    )
                else:
                    raw_list = await scraper.fetch_since(last_sync)
            else:
                raw_list = await scraper.fetch_since(last_sync)
    except Exception as exc:
        logger.error("Sync {}: scraping fallito — {}", organo.value, exc)
        return {"source": organo.value, "error": str(exc)}

    logger.info("Sync {}: {} raw sentenze scaricate", organo.value, len(raw_list))

    docs = []
    for raw in raw_list:
        try:
            if raw.raw_html:
                doc = parse_html(raw)
            elif raw.raw_pdf_bytes:
                doc = parse_pdf(raw)
            else:
                logger.debug("Skipping raw senza contenuto: {}/{}", raw.numero, raw.anno)
                continue
            docs.append(doc)
        except Exception as exc:
            logger.warning("Parsing fallito {}/{}: {}", raw.numero, raw.anno, exc)

    if dry_run:
        logger.info("[DRY RUN] {}: {} doc sarebbero ingestiti", organo.value, len(docs))
        return {"source": organo.value, "dry_run": True, "would_insert": len(docs)}

    stats = await coordinator.ingest(docs)
    await coordinator.update_sync_state(organo, date.today())

    logger.success(
        "Sync {} completato: inserted={} skipped={} errors={}",
        organo.value, stats["inserted"], stats["skipped"], stats["errors"],
    )
    return {"source": organo.value, **stats}


async def main(args: argparse.Namespace) -> None:
    since: date | None = None
    if args.since:
        since = date.fromisoformat(args.since)
    elif args.initial_load:
        since = date.today() - timedelta(days=365 * _INITIAL_LOAD_YEARS)

    organi: list[OrganoGiudicante] = []
    if args.source:
        try:
            organi = [OrganoGiudicante(args.source)]
        except ValueError:
            logger.error("Fonte non valida: {}. Valori: {}", args.source, [o.value for o in _SCRAPER_MAP])
            sys.exit(1)
    else:
        # Esclude Corte Cost (bloccata da hCaptcha) dal sync automatico
        organi = [o for o in _SCRAPER_MAP if o != OrganoGiudicante.CORTE_COST]

    mongo = MongoClient.get()
    ok = await mongo.ping()
    if not ok:
        logger.error("MongoDB non raggiungibile — sync interrotto")
        sys.exit(1)

    coordinator = JurisprudenceCoordinator(mongo.db)

    if args.initial_load:
        logger.info("Modalità caricamento storico: ultimi {} anni", _INITIAL_LOAD_YEARS)

    results = []
    for organo in organi:
        result = await sync_source(
            organo, coordinator, since, args.dry_run,
            initial_load=args.initial_load,
        )
        results.append(result)

    logger.info("=== Riepilogo sync ===")
    for r in results:
        if "error" in r:
            logger.error("  {}: ERRORE — {}", r["source"], r["error"])
        elif r.get("dry_run"):
            logger.info("  {}: [DRY RUN] would_insert={}", r["source"], r.get("would_insert"))
        else:
            logger.success(
                "  {}: inserted={} skipped={} errors={}",
                r["source"], r.get("inserted", 0), r.get("skipped", 0), r.get("errors", 0),
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync giurisprudenza da fonti pubbliche")
    parser.add_argument("--source", help="Fonte specifica (cassazione|tar|corte_conti)")
    parser.add_argument("--since", help="Data inizio sync ISO 8601 (es. 2024-01-01)")
    parser.add_argument("--initial-load", action="store_true",
                        help=f"Caricamento storico {_INITIAL_LOAD_YEARS} anni — alza i limiti")
    parser.add_argument("--dry-run", action="store_true", help="Simula senza scrivere")
    args = parser.parse_args()

    asyncio.run(main(args))
