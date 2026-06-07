"""
Workflow settimanale completo: sync + build indici.

Uso:
  python scripts/weekly_jurisprudence_update.py --workspace mio-studio
  python scripts/weekly_jurisprudence_update.py --workspace mio-studio --dry-run

Esegue in sequenza:
  1. sync_jurisprudence (ultimi 7 giorni, tutte le fonti)
  2. build_jurisprudence_indexes (append — aggiunge solo i nuovi chunk)
  3. Stampa riepilogo
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.jurisprudence.coordinator import JurisprudenceCoordinator, to_chunks
from aiura_legal.jurisprudence.models import OrganoGiudicante
from aiura_legal.jurisprudence.parser import parse_html, parse_pdf
from aiura_legal.jurisprudence.scrapers import (
    CassazioneScraper,
    CorteContiScraper,
    GiustiziaAmmScraper,
)
from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.core.types import Document

_WORKSPACES_BASE = Path("C:/project/AiUraLegalLab/workspaces")

_SCRAPER_MAP = {
    OrganoGiudicante.CASSAZIONE: CassazioneScraper,
    OrganoGiudicante.TAR: GiustiziaAmmScraper,
    OrganoGiudicante.CORTE_CONTI: CorteContiScraper,
}


def _mongo_to_jdoc(record: dict):
    from datetime import date
    from aiura_legal.jurisprudence.models import JurisprudenceDocument
    try:
        dep_raw = record.get("data_deposito", "")
        dep = date.fromisoformat(dep_raw) if dep_raw else date.today()
        return JurisprudenceDocument(
            organo=OrganoGiudicante(record["organo"]),
            numero=record["numero"],
            anno=int(record["anno"]),
            data_deposito=dep,
            sezione=record.get("sezione", ""),
            materia=record.get("materia", ""),
            massima=record.get("massima", ""),
            motivazione=record.get("motivazione", ""),
            dispositivo=record.get("dispositivo", ""),
            norme_citate=record.get("norme_citate", []),
            sentenze_citate=record.get("sentenze_citate", []),
            source_url=record.get("source_url", ""),
            is_anonymized=record.get("is_anonymized", False),
        )
    except Exception:
        return None


async def run(workspace: str, dry_run: bool) -> None:
    t0 = time.monotonic()
    mongo = MongoClient.get()

    if not await mongo.ping():
        logger.error("MongoDB non raggiungibile")
        sys.exit(1)

    ws_path = _WORKSPACES_BASE / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    coordinator = JurisprudenceCoordinator(mongo.db)
    bm25 = BM25Retriever(str(ws_path))
    vector = VectorRetriever(str(ws_path))

    total_inserted = 0
    total_skipped = 0
    new_ids: list[str] = []

    # ── 1. Sync da tutte le fonti ──────────────────────────────────────
    logger.info("── Fase 1: sync nuove sentenze ──")
    for organo, scraper_cls in _SCRAPER_MAP.items():
        last_sync = await coordinator.get_last_sync(organo)
        if last_sync is None:
            from datetime import date, timedelta
            last_sync = date.today() - timedelta(days=7)

        logger.info("  {}: dal {}", organo.value, last_sync)
        try:
            async with scraper_cls() as scraper:
                raw_list = await scraper.fetch_since(last_sync)
        except Exception as exc:
            logger.error("  {} scraping fallito: {}", organo.value, exc)
            continue

        docs = []
        for raw in raw_list:
            try:
                doc = parse_html(raw) if raw.raw_html else parse_pdf(raw) if raw.raw_pdf_bytes else None
                if doc:
                    docs.append(doc)
            except Exception:
                pass

        if dry_run:
            logger.info("  [DRY RUN] {}: {} nuovi doc", organo.value, len(docs))
            continue

        stats = await coordinator.ingest(docs)
        total_inserted += stats["inserted"]
        total_skipped += stats["skipped"]

        # Raccoglie ID dei nuovi doc per indicizzarli
        if stats["inserted"] > 0:
            for doc in docs:
                new_ids.append(doc.id)

        await coordinator.update_sync_state(organo, __import__("datetime").date.today())
        logger.success("  {}: +{} inserted, {} skipped", organo.value, stats["inserted"], stats["skipped"])

    if dry_run:
        logger.info("[DRY RUN] completato — nessuna scrittura effettuata")
        return

    if total_inserted == 0:
        logger.info("Nessuna nuova sentenza — indici già aggiornati")
        elapsed = time.monotonic() - t0
        logger.success("Completato in {:.1f}s", elapsed)
        return

    # ── 2. Indicizza solo i nuovi documenti ───────────────────────────
    logger.info("── Fase 2: indicizzazione {} nuovi doc ──", total_inserted)
    collection = mongo.db["jurisprudence"]
    batch: list[Document] = []
    indexed = 0

    async for record in collection.find({"_id": {"$in": new_ids}}):
        jdoc = _mongo_to_jdoc(record)
        if not jdoc:
            continue
        chunks = to_chunks(jdoc)
        batch.extend(chunks)
        indexed += 1
        if len(batch) >= 500:
            bm25.add_documents_batch(batch)
            vector.add_documents_batch(batch)
            batch = []

    if batch:
        bm25.add_documents_batch(batch)
        vector.add_documents_batch(batch)

    bm25.save()
    vector.save()

    # ── 3. Riepilogo ──────────────────────────────────────────────────
    elapsed = time.monotonic() - t0
    logger.success("── Riepilogo settimanale ──")
    logger.success("  Nuove sentenze:  {:,}", total_inserted)
    logger.success("  Già presenti:    {:,}", total_skipped)
    logger.success("  Doc indicizzati: {:,}", indexed)
    logger.success("  Tempo totale:    {:.1f}s", elapsed)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update settimanale giurisprudenza")
    parser.add_argument("--workspace", required=True, help="Nome workspace")
    parser.add_argument("--dry-run", action="store_true", help="Simula senza scrivere")
    args = parser.parse_args()
    asyncio.run(run(args.workspace, args.dry_run))
