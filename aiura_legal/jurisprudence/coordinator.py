"""
Coordinator — orchestra ingestione giurisprudenziale.
Dedup, generazione chunk, aggiornamento BM25/vector, sync_state.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from loguru import logger

from aiura_legal.core.types import Document
from aiura_legal.jurisprudence.anonymizer_bridge import anonymize_document
from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante

if TYPE_CHECKING:
    import motor.motor_asyncio as motor

_COLLECTION = "jurisprudence"
_SYNC_STATE_COLLECTION = "sync_state"

# Parametri chunking geometrico per le motivazioni (Fase 1)
_MOTIVAZIONE_MAX_TOKENS = 512
_MOTIVAZIONE_OVERLAP = 64


def _base_metadata(doc: JurisprudenceDocument, chunk_type: str, chunk_index: int) -> dict:
    """Metadati comuni a tutti i chunk di un JurisprudenceDocument."""
    return {
        "corpus": "giurisprudenza",
        "chunk_type": chunk_type,
        "chunk_index": chunk_index,
        "jdoc_id": doc.id,
        "organo": doc.organo.value,
        "numero": doc.numero,
        "anno": str(doc.anno),
        "materia": doc.materia,
        "source_url": doc.source_url or "",
    }


def to_chunks(doc: JurisprudenceDocument) -> list[Document]:
    """Genera Document indicizzabili da un JurisprudenceDocument.

    Massima e dispositivo → 1 chunk monolitico ciascuno (comportamento invariato).
    Motivazione → N chunk geometrici con Chunker(512, 64) se testo presente.
    ID chunk motivazione: {doc.id}_motivazione_{i:03d}
    """
    chunks: list[Document] = []
    common_kwargs: dict = {
        "source_id": f"giurisprudenza_{doc.organo.value}_{doc.numero}_{doc.anno}",
        "source_authority": doc.organo.value,
        "is_anonymized": doc.is_anonymized,
        "valid_from": doc.data_deposito,
    }

    # ── Massima — monolitico ────────────────────────────────────────────
    if doc.massima.strip():
        chunks.append(Document(
            id=f"{doc.id}_massima",
            text=doc.massima,
            metadata=_base_metadata(doc, "massima", 0),
            **common_kwargs,
        ))

    # ── Motivazione — chunking geometrico 512 tok / 64 overlap ─────────
    if doc.motivazione.strip():
        from aiura_legal.ingestion.chunker import Chunker
        _chunker = Chunker(max_tokens=_MOTIVAZIONE_MAX_TOKENS, overlap=_MOTIVAZIONE_OVERLAP)
        sub_chunks = _chunker.chunk(doc.motivazione)
        # Fallback: motivazione troppo corta per chunker → chunk unico (index 0)
        texts = [c.text for c in sub_chunks] if sub_chunks else [doc.motivazione]
        for i, chunk_text in enumerate(texts):
            chunks.append(Document(
                id=f"{doc.id}_motivazione_{i:03d}",
                text=chunk_text,
                metadata=_base_metadata(doc, "motivazione", i),
                **common_kwargs,
            ))
        logger.debug(
            "to_chunks: jdoc_id={} motivazione={} char -> {} chunk(s)",
            doc.id, len(doc.motivazione), len(texts),
        )

    # ── Dispositivo — monolitico ────────────────────────────────────────
    if doc.dispositivo.strip():
        chunks.append(Document(
            id=f"{doc.id}_dispositivo",
            text=doc.dispositivo,
            metadata=_base_metadata(doc, "dispositivo", 0),
            **common_kwargs,
        ))

    return chunks


class JurisprudenceCoordinator:

    def __init__(
        self,
        db: "motor.AsyncIOMotorDatabase",
        bm25_retriever=None,
        vector_retriever=None,
        graph_builder=None,
    ) -> None:
        self._db = db
        self._bm25 = bm25_retriever
        self._vector = vector_retriever
        self._graph = graph_builder

    async def ingest(self, docs: list[JurisprudenceDocument]) -> dict:
        """
        Ingestisce una lista di documenti: dedup → anonymize → store → index.
        Restituisce stats {inserted, skipped, errors}.
        """
        inserted = 0
        skipped = 0
        errors = 0

        for doc in docs:
            try:
                if await self._is_duplicate(doc):
                    skipped += 1
                    continue

                doc = await anonymize_document(doc, self._db)
                await self._store(doc)
                chunks = to_chunks(doc)
                await self._index(chunks, doc)
                inserted += 1
            except Exception as exc:
                logger.error("Coordinator: errore su doc {}/{} — {}", doc.numero, doc.anno, exc)
                errors += 1

        logger.info(
            "Coordinator.ingest: inserted={} skipped={} errors={}",
            inserted, skipped, errors,
        )
        return {"inserted": inserted, "skipped": skipped, "errors": errors}

    async def _is_duplicate(self, doc: JurisprudenceDocument) -> bool:
        existing = await self._db[_COLLECTION].find_one({"_id": doc.id})
        return existing is not None

    async def _store(self, doc: JurisprudenceDocument) -> None:
        record = {
            "_id": doc.id,
            "organo": doc.organo.value,
            "numero": doc.numero,
            "anno": doc.anno,
            "data_deposito": doc.data_deposito.isoformat(),
            "sezione": doc.sezione,
            "materia": doc.materia,
            "massima": doc.massima,
            "motivazione": doc.motivazione,
            "dispositivo": doc.dispositivo,
            "norme_citate": doc.norme_citate,
            "sentenze_citate": doc.sentenze_citate,
            "source_url": doc.source_url,
            "source_channel": doc.source_channel.value,
            "is_anonymized": doc.is_anonymized,
            "raw_pii_vault_id": doc.raw_pii_vault_id,
            "ingested_at": datetime.now(timezone.utc),
        }
        await self._db[_COLLECTION].insert_one(record)

    async def _index(self, chunks: list[Document], doc: JurisprudenceDocument) -> None:
        if self._bm25 is not None:
            self._bm25.add_documents_batch(chunks)
            self._bm25.save()

        if self._vector is not None:
            self._vector.add_documents_batch(chunks)

        if self._graph is not None:
            self._graph.add_document(doc)

    async def get_last_sync(self, organo: OrganoGiudicante) -> date | None:
        record = await self._db[_SYNC_STATE_COLLECTION].find_one(
            {"source": organo.value}
        )
        if record and "last_sync" in record:
            return date.fromisoformat(record["last_sync"])
        return None

    async def update_sync_state(self, organo: OrganoGiudicante, sync_date: date) -> None:
        await self._db[_SYNC_STATE_COLLECTION].update_one(
            {"source": organo.value},
            {"$set": {"last_sync": sync_date.isoformat()}},
            upsert=True,
        )
