"""
MongoDB client per AiUra LegalLab.
Motor (async) come driver principale.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Optional
import motor.motor_asyncio
from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    # Database AiUraLegalLab (unificato: normattiva + giurisprudenza + studio)
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "aiura_legal_lab_db"

    # Normattiva — ora in aiura_legal_lab_db (campo testo: "text")
    legalagentlab_mongodb_uri: str = "mongodb://localhost:27017"
    legalagentlab_mongodb_database: str = "aiura_legal_lab_db"
    legalagentlab_chunks_collection: str = "normattiva_docs"
    legalagentlab_text_field: str = "text"


settings = Settings()


class MongoClient:
    """Client MongoDB principale (AiUraLegalLab)."""

    _instance: Optional["MongoClient"] = None

    def __init__(self):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
        self.db = self._client[settings.mongodb_database]

    @classmethod
    def get(cls) -> "MongoClient":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @property
    def documents(self):
        return self.db["documents"]

    @property
    def chunks(self):
        return self.db["chunks"]

    @property
    def ingestion_queue(self):
        return self.db["ingestion_queue"]

    @property
    def normattiva_docs(self):
        return self.db["normattiva_docs"]

    @property
    def pii_vault(self):
        return self.db["pii_vault"]

    @property
    def istituti_giuridici(self):
        return self.db["istituti_giuridici"]

    async def count_chunks(self, filter_query: dict = None) -> int:
        """Conta i chunk in aiura_legal_lab_db.chunks."""
        return await self.db["chunks"].count_documents(filter_query or {})

    async def iter_chunks(
        self,
        batch_size: int = 500,
        filter_query: dict = None,
    ) -> "AsyncGenerator[dict, None]":
        """Itera su tutti i chunk di aiura_legal_lab_db.chunks."""
        cursor = self.db["chunks"].find(filter_query or {}).batch_size(batch_size)
        async for chunk in cursor:
            yield chunk

    async def ping(self) -> bool:
        try:
            await self.db.command("ping")
            return True
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False


class LegalAgentLabReader:
    """
    Accesso READ-ONLY al MongoDB di LegalAgentLab.
    Database: legal_lab, collection principale: normattiva_docs, campo testo: text.
    Non scrive mai nel database sorgente.
    """

    def __init__(self):
        if not settings.legalagentlab_mongodb_database:
            raise ValueError(
                "LEGALAGENTLAB_MONGODB_DATABASE non configurato in .env"
            )
        self._client = motor.motor_asyncio.AsyncIOMotorClient(
            settings.legalagentlab_mongodb_uri
        )
        self.db = self._client[settings.legalagentlab_mongodb_database]
        logger.info(
            f"LegalAgentLab reader (READ-ONLY): "
            f"{settings.legalagentlab_mongodb_database}"
        )

    async def count_chunks(self) -> int:
        return await self.db[settings.legalagentlab_chunks_collection].count_documents({})

    async def iter_chunks(
        self,
        batch_size: int = 500,
        filter_query: dict = None,
    ) -> AsyncGenerator[dict, None]:
        """
        Itera su tutti i chunk in batch. Usa il campo testo
        configurato in LEGALAGENTLAB_TEXT_FIELD (default: "text").
        """
        coll = settings.legalagentlab_chunks_collection
        cursor = self.db[coll].find(filter_query or {}).batch_size(batch_size)
        async for doc in cursor:
            if settings.legalagentlab_text_field not in doc:
                for field in ["text", "content", "testo", "body", "chunk_text"]:
                    if field in doc:
                        doc["_normalized_text"] = doc[field]
                        break
            else:
                doc["_normalized_text"] = doc[settings.legalagentlab_text_field]
            yield doc

    async def list_collections(self) -> list[str]:
        return await self.db.list_collection_names()

    async def sample_document(self, collection: str) -> dict | None:
        """Ritorna un documento di esempio per ispezionare lo schema."""
        return await self.db[collection].find_one({})
