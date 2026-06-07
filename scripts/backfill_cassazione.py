"""
Backfill storico Cassazione — scarica per finestre mensili in parallelo
per aggirare il limite di deep pagination del Solr di italgiure (~50k/query).

Ogni mese è una task asyncio indipendente con il proprio httpx client.
Un semaforo limita le connessioni simultanee per non sovraccaricare il Solr.

Uso:
  python scripts/backfill_cassazione.py --from 2024-01-01 --to 2024-12-31
  python scripts/backfill_cassazione.py --from 2020-01-01           # fino a ieri
  python scripts/backfill_cassazione.py                             # riprende da watermark
  python scripts/backfill_cassazione.py --dry-run                   # conta, non scrive
  python scripts/backfill_cassazione.py --concurrency 6             # 6 mesi in parallelo

Watermark: salvato in sync_state (source="cassazione_backfill").
           In caso di interruzione, riprende dal primo mese non ancora completato.
           I duplicati sono sicuri: il coordinator li salta automaticamente.

Stima con --concurrency 4:
  2024 (12 mesi):  ~12 min
  2020-2024 (48 mesi): ~45 min
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.jurisprudence.coordinator import JurisprudenceCoordinator
from aiura_legal.jurisprudence.models import OrganoGiudicante
from aiura_legal.jurisprudence.parser import parse_html
from aiura_legal.jurisprudence.scrapers.cassazione import (
    CassazioneScraper,
    _RATE_LIMIT_INITIAL,
)

_WATERMARK_SOURCE   = "cassazione_backfill"
_MAX_PER_MONTH      = 20_000    # cap sicurezza: nessun mese ha > 20k sentenze
_DEFAULT_FROM       = date(2020, 1, 1)
_DEFAULT_CONCURRENCY = 4        # mesi in parallelo


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _months_in_range(start: date, end: date) -> list[tuple[date, date]]:
    """Genera (primo_giorno, ultimo_giorno) per ogni mese in [start, end]."""
    windows: list[tuple[date, date]] = []
    cur = date(start.year, start.month, 1)
    while cur <= end:
        last_day = monthrange(cur.year, cur.month)[1]
        month_end = date(cur.year, cur.month, last_day)
        windows.append((cur, min(month_end, end)))
        cur = date(cur.year + (cur.month // 12), cur.month % 12 + 1, 1)
    return windows


async def _get_watermark(db) -> date | None:
    doc = await db.sync_state.find_one({"source": _WATERMARK_SOURCE})
    if doc and doc.get("last_completed_month"):
        return date.fromisoformat(doc["last_completed_month"])
    return None


async def _save_watermark(db, month_end: date) -> None:
    await db.sync_state.update_one(
        {"source": _WATERMARK_SOURCE},
        {"$set": {"last_completed_month": month_end.isoformat()}},
        upsert=True,
    )


# ──────────────────────────────────────────────
# Worker: un mese, un httpx client dedicato
# ──────────────────────────────────────────────

async def _process_month(
    month_start: date,
    month_end:   date,
    coordinator: JurisprudenceCoordinator,
    semaphore:   asyncio.Semaphore,
    dry_run:     bool,
) -> dict:
    """
    Worker per una singola finestra mensile.
    Usa il semaforo per limitare le connessioni concorrenti al Solr.
    """
    label = f"{month_start.year}/{month_start.month:02d}"

    async with semaphore:
        async with CassazioneScraper() as scraper:
            raw_list = await scraper.fetch_since(
                since=month_start,
                until=month_end,
                max_results=_MAX_PER_MONTH,
                rate_limit=_RATE_LIMIT_INITIAL,
            )

    logger.info("{}: {} raw scaricati", label, len(raw_list))

    # Parsing (CPU-bound leggero, fuori dal semaforo)
    docs = []
    parse_errors = 0
    for raw in raw_list:
        try:
            if raw.raw_html:
                docs.append(parse_html(raw))
        except Exception as exc:
            logger.debug("{}: parse fallito {}/{} — {}", label, raw.numero, raw.anno, exc)
            parse_errors += 1

    if dry_run:
        logger.info("{}: [DRY RUN] {} da inserire ({} parse errors)", label, len(docs), parse_errors)
        return {"month": label, "month_end": month_end, "would_insert": len(docs), "dry_run": True}

    stats = await coordinator.ingest(docs)
    logger.success(
        "{}: inserted={} skipped={} errors={} (parse_err={})",
        label, stats["inserted"], stats["skipped"], stats["errors"], parse_errors,
    )
    return {"month": label, "month_end": month_end, **stats}


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

async def main(args: argparse.Namespace) -> None:
    # MongoDB
    mongo = MongoClient.get()
    if not await mongo.ping():
        logger.error("MongoDB non raggiungibile")
        sys.exit(1)
    coordinator = JurisprudenceCoordinator(mongo.db)

    # Range date
    end_date = date.fromisoformat(args.to) if args.to else date.today() - timedelta(days=1)

    if args.from_date:
        start_date = date.fromisoformat(args.from_date)
    else:
        wm = await _get_watermark(mongo.db)
        if wm:
            # Primo giorno del mese successivo all'ultimo completato
            start_date = date(wm.year + (wm.month // 12), wm.month % 12 + 1, 1)
            logger.info("Watermark: {} — riprendo da {}", wm, start_date)
        else:
            start_date = _DEFAULT_FROM
            logger.info("Nessun watermark — parto da {}", start_date)

    if start_date > end_date:
        logger.success("Niente da fare: tutto già scaricato fino a {}", end_date)
        return

    windows = _months_in_range(start_date, end_date)
    concurrency = args.concurrency

    current_total = await mongo.db.jurisprudence.count_documents(
        {"organo": OrganoGiudicante.CASSAZIONE.value}
    )
    logger.info(
        "Backfill Cassazione | {} finestre mensili | concurrency={} | "
        "DB attuale: {:,} sentenze",
        len(windows), concurrency, current_total,
    )

    # Semaforo condiviso — limita N httpx client aperti contemporaneamente
    semaphore = asyncio.Semaphore(concurrency)

    # Lancia tutti i mesi in parallelo (il semaforo li disciplina)
    tasks = [
        _process_month(month_start, month_end, coordinator, semaphore, args.dry_run)
        for month_start, month_end in windows
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Riepilogo e watermark
    total_inserted = total_skipped = total_errors = 0
    completed_months: list[date] = []

    for r in results:
        if isinstance(r, Exception):
            logger.error("Task fallita: {}", r)
            continue
        if r.get("dry_run"):
            continue
        total_inserted += r.get("inserted", 0)
        total_skipped  += r.get("skipped", 0)
        total_errors   += r.get("errors", 0)
        if r.get("errors", 0) == 0:
            completed_months.append(r["month_end"])

    # Salva watermark = mese più recente completato senza errori
    if completed_months and not args.dry_run:
        best_wm = max(completed_months)
        await _save_watermark(mongo.db, best_wm)
        logger.info("Watermark aggiornato: {}", best_wm)

    final_total = await mongo.db.jurisprudence.count_documents(
        {"organo": OrganoGiudicante.CASSAZIONE.value}
    )

    logger.success(
        "═══ BACKFILL COMPLETATO ═══\n"
        "  Inserite:  {:>8,}\n"
        "  Skippate:  {:>8,}\n"
        "  Errori:    {:>8,}\n"
        "  Cassazione: {:,} → {:,} (+{:,})",
        total_inserted, total_skipped, total_errors,
        current_total, final_total, final_total - current_total,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Backfill storico Cassazione per finestre mensili in parallelo"
    )
    parser.add_argument(
        "--from", dest="from_date",
        help="Data inizio ISO 8601 (es. 2024-01-01). Default: watermark o 2020-01-01",
    )
    parser.add_argument(
        "--to",
        help="Data fine ISO 8601 (es. 2024-12-31). Default: ieri",
    )
    parser.add_argument(
        "--concurrency", type=int, default=_DEFAULT_CONCURRENCY,
        help=f"Mesi in parallelo (default: {_DEFAULT_CONCURRENCY})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Conta le sentenze senza scrivere su MongoDB",
    )
    args = parser.parse_args()
    asyncio.run(main(args))
