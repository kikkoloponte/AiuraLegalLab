"""
Crea gli indici ottimizzati sulla collection query_history di aiura_legal_lab_db.

Idempotente: può essere eseguito più volte senza effetti collaterali
(MongoDB ignora create_index se l'indice esiste già con lo stesso nome).

Uso:
  python scripts/migrate_history_indexes.py
"""
from __future__ import annotations

from pymongo import ASCENDING, DESCENDING, TEXT, MongoClient
from loguru import logger

from aiura_legal.ingestion.mongodb.client import settings


def migrate() -> None:
    client = MongoClient(settings.mongodb_uri)
    coll = client[settings.mongodb_database]["query_history"]

    indexes: list[tuple[list, dict]] = [
        # Query principale: workspace + data desc (lista cronologia per workspace)
        (
            [("workspace", ASCENDING), ("created_at", DESCENDING)],
            {"name": "ws_date"},
        ),
        # Filtro "solo valutate" + ordinamento per data feedback
        (
            [("workspace", ASCENDING), ("feedback_at", DESCENDING)],
            {"name": "ws_feedback_date", "sparse": True},
        ),
        # Filtro per rating (analytics: quante 5 stelle nel workspace?)
        (
            [("workspace", ASCENDING), ("feedback_rating", ASCENDING)],
            {"name": "ws_rating", "sparse": True},
        ),
        # Tag multikey (MongoDB indicizza ogni elemento dell'array)
        (
            [("feedback_tags", ASCENDING)],
            {"name": "tags_multikey", "sparse": True},
        ),
        # Full-text sulla domanda (ricerca nella cronologia)
        (
            [("query", TEXT)],
            {"name": "query_text"},
        ),
    ]

    created = 0
    for keys, opts in indexes:
        name = opts["name"]
        try:
            coll.create_index(keys, **opts)
            logger.success(f"  ✓ Indice '{name}' — OK")
            created += 1
        except Exception as e:
            logger.error(f"  ✗ Indice '{name}' — ERRORE: {e}")

    client.close()
    logger.info(f"Migrazione completata: {created}/{len(indexes)} indici creati/verificati.")


if __name__ == "__main__":
    migrate()
