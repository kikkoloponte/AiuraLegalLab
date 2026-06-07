"""
Coordinator per la pipeline prassi amministrativa.
Gestisce ingestione in MongoDB e cursori last_sync.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from aiura_legal.prassi.models import EmittentePrassi, PrassiDocument, TipoPrassi

_COLLECTION = "prassi_docs"
_SYNC_STATE  = "prassi_sync_state"


class PrassiCoordinator:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._db = db

    @property
    def collection(self):
        return self._db[_COLLECTION]

    @property
    def sync_state(self):
        return self._db[_SYNC_STATE]

    async def ensure_indexes(self) -> None:
        await self.collection.create_index([("tipo", 1), ("anno", 1)])
        await self.collection.create_index([("emittente", 1), ("tipo", 1)])
        await self.collection.create_index("data_emissione")
        logger.debug("PrassiCoordinator: indici OK")

    async def get_last_sync(self, emittente: EmittentePrassi, tipo: TipoPrassi) -> date | None:
        doc = await self.sync_state.find_one(
            {"emittente": emittente.value, "tipo": tipo.value}
        )
        if doc and doc.get("last_sync"):
            return date.fromisoformat(doc["last_sync"])
        return None

    async def update_sync_state(
        self, emittente: EmittentePrassi, tipo: TipoPrassi, sync_date: date
    ) -> None:
        await self.sync_state.update_one(
            {"emittente": emittente.value, "tipo": tipo.value},
            {"$set": {"last_sync": sync_date.isoformat()}},
            upsert=True,
        )

    async def ingest(self, docs: list[PrassiDocument]) -> dict[str, int]:
        """Insert nuovi documenti, salta i duplicati (dedup su _id)."""
        inserted = skipped = errors = 0

        for doc in docs:
            mongo_doc = self._to_mongo(doc)
            try:
                await self.collection.insert_one(mongo_doc)
                inserted += 1
            except Exception as exc:
                if "duplicate" in str(exc).lower() or "E11000" in str(exc):
                    skipped += 1
                else:
                    logger.warning("PrassiCoordinator ingest error: {}", exc)
                    errors += 1

        return {"inserted": inserted, "skipped": skipped, "errors": errors}

    def _to_mongo(self, doc: PrassiDocument) -> dict[str, Any]:
        return {
            "_id":           doc.id,
            "tipo":          doc.tipo.value,
            "emittente":     doc.emittente.value,
            "numero":        doc.numero,
            "anno":          doc.anno,
            "data_emissione": doc.data_emissione.isoformat() if doc.data_emissione else None,
            "titolo":        doc.titolo,
            "testo":         doc.testo,
            "materia":       doc.materia,
            "norme_citate":  doc.norme_citate,
            "source_url":    doc.source_url,
            "pdf_url":       doc.pdf_url,
            "ingested_at":   doc.ingested_at,
        }
