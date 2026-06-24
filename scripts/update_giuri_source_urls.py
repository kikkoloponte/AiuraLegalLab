"""
Migrazione in-place: aggiunge source_url al payload Qdrant dei chunk giurisprudenziali.

Non richiede rebuild degli indici BM25 o Qdrant — aggiorna solo i payload
dei punti già esistenti in Qdrant.

Uso:
  python scripts/update_giuri_source_urls.py
  python scripts/update_giuri_source_urls.py --workspace mio-studio
  python scripts/update_giuri_source_urls.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from pathlib import Path

from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _to_qdrant_id(doc_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, doc_id))


def _main(workspace: str, dry_run: bool) -> None:
    # ── Carica .env ──────────────────────────────────────────────────────
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    mongo_uri  = os.environ.get("MONGODB_URI",      "mongodb://localhost:27017")
    legal_uri  = os.environ.get("LEGALAGENTLAB_MONGODB_URI", mongo_uri)
    giuri_db   = os.environ.get("MONGODB_DATABASE",  "aiura_legal_lab_db")
    qdrant_url = os.environ.get("QDRANT_URL", "").strip()

    # ── Connessione MongoDB (sync per script CLI) ────────────────────────
    import pymongo
    client = pymongo.MongoClient(mongo_uri)
    db     = client[giuri_db]

    # ── Connessione Qdrant ───────────────────────────────────────────────
    from qdrant_client import QdrantClient
    from qdrant_client.models import SetPayload

    ws_path = Path(os.environ.get("AIURA_WORKSPACES_PATH",
                                   str(Path(__file__).resolve().parent.parent / "workspaces"))) / workspace

    if qdrant_url:
        qdrant = QdrantClient(url=qdrant_url, timeout=60)
        logger.info(f"Qdrant server: {qdrant_url}")
    else:
        qdrant_path = str(ws_path / "indices" / "qdrant")
        qdrant = QdrantClient(path=qdrant_path)
        logger.info(f"Qdrant embedded: {qdrant_path}")

    collection = "legal_docs"

    # ── Leggi tutti i documenti giurisprudenziali da MongoDB ─────────────
    docs = list(db["jurisprudence"].find({}, {"_id": 1, "source_url": 1, "organo": 1,
                                              "numero": 1, "anno": 1}))
    logger.info(f"Documenti giurisprudenziali in MongoDB: {len(docs)}")

    updated = 0
    skipped = 0
    errors  = 0

    for doc in docs:
        doc_id     = str(doc["_id"])
        source_url = doc.get("source_url") or ""
        if not source_url:
            skipped += 1
            continue

        chunk_types = ["massima", "motivazione", "dispositivo"]
        point_ids   = [_to_qdrant_id(f"{doc_id}_{ct}") for ct in chunk_types]

        if dry_run:
            logger.info(f"[DRY] {doc_id} → {source_url} (points: {point_ids[:1]}...)")
            updated += len(chunk_types)
            continue

        try:
            qdrant.set_payload(
                collection_name=collection,
                payload={"source_url": source_url},
                points=point_ids,
            )
            updated += len(chunk_types)
        except Exception as exc:
            logger.warning(f"Errore su doc {doc_id}: {exc}")
            errors += 1

    logger.info(
        f"Completato — aggiornati: {updated} chunk | "
        f"senza URL: {skipped} doc | errori: {errors}"
    )
    if dry_run:
        logger.info("(--dry-run: nessuna modifica eseguita)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Aggiunge source_url al payload Qdrant dei chunk giurisprudenziali"
    )
    parser.add_argument("--workspace", default="mio-studio",
                        help="Nome del workspace (default: mio-studio)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa farebbe senza eseguire modifiche")
    args = parser.parse_args()
    _main(args.workspace, args.dry_run)
