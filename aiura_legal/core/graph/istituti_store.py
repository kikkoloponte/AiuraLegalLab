"""
IstitutiStore — CRUD su aiura_legal_lab_db.istituti_giuridici per la UI di
gestione degli Istituti Giuridici (vedi
docs/superpowers/specs/2026-06-30-istituti-giuridici-crud-design.md).

A differenza di QuestioniRegistry (YAML su disco, lock a livello di file),
qui ogni istituto è un documento Mongo indipendente con optimistic locking
per-documento (campo version, intero incrementale).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from bson import ObjectId
from bson.errors import InvalidId
from loguru import logger

from aiura_legal.core.graph.istituti_models import IstitutoGiuridico, IstitutoGiuridicoCreate

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorCollection


class IstitutoNotFoundError(KeyError):
    """id non presente nella collection."""


class VersionConflictError(ValueError):
    """expected_version non coincide con la versione attuale del documento."""


class IstitutiStore:
    """
    Utilizzo tipico (router FastAPI):
        store = IstitutiStore(MongoClient.get().istituti_giuridici)
        istituti = await store.list_all()
        istituto, version = await store.get(id)
        istituto, version = await store.update(id, payload, expected_version=version)
    """

    def __init__(self, collection: "AsyncIOMotorCollection") -> None:
        self._collection = collection

    # ------------------------------------------------------------------
    # Lettura
    # ------------------------------------------------------------------

    async def list_all(self) -> list[IstitutoGiuridico]:
        items = []
        async for doc in self._collection.find({}):
            items.append(self._to_model(doc))
        return items

    async def get(self, id: str) -> tuple[IstitutoGiuridico, int]:
        """Raises IstitutoNotFoundError se id non esiste o non è un ObjectId valido."""
        doc = await self._collection.find_one({"_id": self._to_object_id(id)})
        if doc is None:
            raise IstitutoNotFoundError(id)
        istituto = self._to_model(doc)
        return istituto, istituto.version

    # ------------------------------------------------------------------
    # Scrittura
    # ------------------------------------------------------------------

    async def create(self, payload: IstitutoGiuridicoCreate) -> tuple[IstitutoGiuridico, int]:
        doc = payload.model_dump()
        doc["version"] = 1
        doc["updated_at"] = datetime.now(timezone.utc)
        result = await self._collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        logger.info(f"[IstitutiStore] create '{doc['_id']}': {payload.denominazione!r}")
        istituto = self._to_model(doc)
        return istituto, istituto.version

    async def update(
        self,
        id: str,
        payload: IstitutoGiuridicoCreate,
        expected_version: int,
    ) -> tuple[IstitutoGiuridico, int]:
        """
        Sovrascrive l'intero istituto (a parte _id/version/updated_at) con
        optimistic concurrency control: se il documento è stato modificato
        da quando il chiamante ha letto expected_version, nessuna scrittura
        — VersionConflictError.

        Raises:
            IstitutoNotFoundError: id non in collection.
            VersionConflictError: expected_version obsoleta.
        """
        object_id = self._to_object_id(id)
        update_doc = payload.model_dump()
        update_doc["version"] = expected_version + 1
        update_doc["updated_at"] = datetime.now(timezone.utc)

        result = await self._collection.find_one_and_replace(
            {"_id": object_id, "version": expected_version},
            {**update_doc, "_id": object_id},
            return_document=True,
        )
        if result is None:
            # Distingue "non trovato" da "conflitto di versione".
            existing = await self._collection.find_one({"_id": object_id})
            if existing is None:
                raise IstitutoNotFoundError(id)
            raise VersionConflictError(
                f"istituto '{id}': il documento è stato modificato da quando è stato letto "
                f"(expected_version={expected_version!r}, attuale={existing.get('version')!r})"
            )

        logger.info(f"[IstitutiStore] update '{id}': version -> {update_doc['version']}")
        return self._to_model(result), update_doc["version"]

    async def delete(self, id: str) -> None:
        """Raises IstitutoNotFoundError se id non esiste."""
        result = await self._collection.delete_one({"_id": self._to_object_id(id)})
        if result.deleted_count == 0:
            raise IstitutoNotFoundError(id)
        logger.info(f"[IstitutiStore] delete '{id}'")

    # ------------------------------------------------------------------
    # Utilità
    # ------------------------------------------------------------------

    @staticmethod
    def _to_object_id(id: str) -> ObjectId:
        try:
            return ObjectId(id)
        except (InvalidId, TypeError) as exc:
            raise IstitutoNotFoundError(id) from exc

    @staticmethod
    def _to_model(doc: dict) -> IstitutoGiuridico:
        doc = {**doc, "id": str(doc["_id"])}
        doc.pop("_id", None)
        return IstitutoGiuridico.model_validate(doc)
