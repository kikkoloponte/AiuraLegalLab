"""
Indicizza le sentenze dalla collection jurisprudence negli indici BM25/Vector
del workspace specificato.

Da eseguire DOPO build_indexes.py (che ricostruisce la normattiva).
Lo script è idempotente: salta le sentenze già presenti nell'indice BM25.
Accumula TUTTI i chunk in memoria e fa una sola BM25Okapi build (~40 min totali).

Uso:
  python scripts/index_jurisprudence.py --workspace mio-studio
  python scripts/index_jurisprudence.py --workspace mio-studio --skip-vector
  python scripts/index_jurisprudence.py --workspace mio-studio --organo cassazione

Se devi ripartire da zero (es. cambio formato source_id):
  1. Ferma l'API
  2. del workspaces\\<ws>\\indices\\bm25.pkl
  3. del workspaces\\<ws>\\indices\\bm25_meta.json
  4. rmdir /s /q workspaces\\<ws>\\indices\\chromadb
  5. python scripts/build_indexes.py --workspace <ws>
  6. python scripts/index_jurisprudence.py --workspace <ws>

Requisiti:
  - build_indexes.py deve essere già completato (BM25/Vector normattiva presenti)
  - MongoDB deve essere raggiungibile
"""
from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path

from loguru import logger
from pymongo import MongoClient

from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.jurisprudence.coordinator import to_chunks
from aiura_legal.jurisprudence.models import (
    JurisprudenceDocument,
    OrganoGiudicante,
    SourceChannel,
)
from aiura_legal.ingestion.mongodb.client import settings

_DB_NAME    = settings.mongodb_database
_COLLECTION = "jurisprudence"
_REPORT_EVERY = 10_000   # log di avanzamento ogni N sentenze lette


# ---------------------------------------------------------------------------
# Conversione record MongoDB → JurisprudenceDocument
# ---------------------------------------------------------------------------

def _to_date(value) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        return date.fromisoformat(value[:10])
    raise ValueError(f"Impossibile convertire in date: {value!r}")


def _record_to_doc(rec: dict) -> JurisprudenceDocument | None:
    try:
        return JurisprudenceDocument(
            organo=OrganoGiudicante(rec["organo"]),
            numero=rec.get("numero", ""),
            anno=int(rec.get("anno", 0)),
            data_deposito=_to_date(rec.get("data_deposito", "2000-01-01")),
            sezione=rec.get("sezione", ""),
            materia=rec.get("materia", ""),
            massima=rec.get("massima", ""),
            motivazione=rec.get("motivazione", ""),
            dispositivo=rec.get("dispositivo", ""),
            norme_citate=rec.get("norme_citate", []),
            sentenze_citate=rec.get("sentenze_citate", []),
            source_url=rec.get("source_url", ""),
            source_channel=SourceChannel(rec.get("source_channel", "scraping")),
            is_anonymized=rec.get("is_anonymized", False),
            raw_pii_vault_id=rec.get("raw_pii_vault_id"),
        )
    except Exception as exc:
        logger.warning(f"  Skipping {rec.get('_id')}: {exc}")
        return None


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build(
    workspace: str,
    skip_vector: bool = False,
    skip_bm25: bool = False,
    organo: str | None = None,
) -> None:
    # ── MongoDB ───────────────────────────────────────────────────────
    mongo = MongoClient(settings.mongodb_uri)
    db = mongo[_DB_NAME]

    mongo_filter: dict = {}
    if organo:
        mongo_filter["organo"] = organo

    total = db[_COLLECTION].count_documents(mongo_filter)
    if total == 0:
        logger.warning("Nessuna sentenza trovata con il filtro specificato.")
        return
    logger.info(f"Sentenze in jurisprudence: {total:,}  (filtro: {mongo_filter or 'nessuno'})")

    # ── Caricamento indici ─────────────────────────────────────────────
    ws_path = Path(f"C:/project/AiUraLegalLab/workspaces/{workspace}")
    ws_path.mkdir(parents=True, exist_ok=True)

    if not skip_bm25:
        logger.info("Caricamento BM25 dal pickle (1-2 min)...")
    bm25 = BM25Retriever(str(ws_path)) if not skip_bm25 else None

    if not skip_vector:
        logger.info("Inizializzazione ChromaDB...")
    vector = VectorRetriever(str(ws_path)) if not skip_vector else None

    # Set di doc_id già presenti — usato per l'idempotenza
    existing_ids: set[str] = set(bm25._doc_ids) if bm25 else set()
    if bm25:
        logger.info(f"BM25 esistente: {len(existing_ids):,} doc")
    if skip_bm25:
        logger.info("BM25: SKIP")
    if skip_vector:
        logger.info("ChromaDB: SKIP")

    # ── Raccolta chunk in memoria ──────────────────────────────────────
    # Tutti i chunk vengono accumulati; il BM25 viene aggiornato con
    # una sola chiamata add_documents_batch → una sola BM25Okapi build.
    all_chunks: list = []
    processed = 0
    skipped   = 0
    errors    = 0

    logger.info("Raccolta chunk da MongoDB...")
    cursor = db[_COLLECTION].find(mongo_filter).batch_size(500)

    for rec in cursor:
        doc = _record_to_doc(rec)
        if doc is None:
            errors += 1
            continue

        chunks = to_chunks(doc)
        if not chunks:
            skipped += 1
            continue

        if chunks[0].id in existing_ids:
            skipped += 1
            continue

        all_chunks.extend(chunks)
        processed += 1

        total_seen = processed + skipped + errors
        if total_seen % _REPORT_EVERY == 0:
            pct = total_seen / total * 100
            logger.info(
                f"  {total_seen:,}/{total:,} ({pct:.0f}%) — "
                f"{processed:,} nuove | {skipped:,} già presenti | {len(all_chunks):,} chunk in memoria"
            )

    logger.info(
        f"Raccolta completata: {processed:,} nuove | {skipped:,} già presenti | "
        f"{errors:,} errori | {len(all_chunks):,} chunk totali"
    )

    if not all_chunks:
        logger.success("Nessun chunk da aggiungere — indici già aggiornati.")
        return

    # ── BM25: una sola add → una sola BM25Okapi build ─────────────────
    if bm25:
        logger.info(
            f"BM25: aggiunta {len(all_chunks):,} chunk (una sola BM25Okapi build, "
            f"può richiedere 5-10 min)..."
        )
        bm25.add_documents_batch(all_chunks)
        logger.info("BM25: build completata")

    # ── ChromaDB: batch da 2000 ────────────────────────────────────────
    if vector:
        _BATCH = 2000
        n_batches = (len(all_chunks) + _BATCH - 1) // _BATCH
        logger.info(f"ChromaDB: {len(all_chunks):,} chunk in {n_batches} batch...")
        for i, start in enumerate(range(0, len(all_chunks), _BATCH), 1):
            vector.add_documents_batch(all_chunks[start:start + _BATCH])
            if i % 10 == 0 or i == n_batches:
                logger.info(f"  ChromaDB: {i}/{n_batches} batch")

    # ── Salvataggio ────────────────────────────────────────────────────
    logger.info("Salvataggio indici (1-2 min)...")
    if bm25:
        bm25.save()
    if vector:
        vector.save()

    logger.success(
        f"Completato: {processed:,} sentenze | {len(all_chunks):,} chunk | "
        f"{skipped:,} già presenti | {errors:,} errori"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Indicizza la giurisprudenza negli indici BM25/Vector"
    )
    parser.add_argument("--workspace",   required=True, help="Nome workspace")
    parser.add_argument("--skip-vector", action="store_true",
                        help="Salta ChromaDB (solo BM25)")
    parser.add_argument("--skip-bm25",  action="store_true",
                        help="Salta BM25 (solo ChromaDB)")
    parser.add_argument("--organo",      default=None,
                        choices=[o.value for o in OrganoGiudicante],
                        help="Filtra per organo giudicante")
    args = parser.parse_args()

    build(
        workspace=args.workspace,
        skip_vector=args.skip_vector,
        skip_bm25=args.skip_bm25,
        organo=args.organo,
    )
