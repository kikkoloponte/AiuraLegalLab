"""
AiUra LegalLab — NormattivaPipeline.

Legge da aiura_legal.normattiva_docs, chunka ogni articolo, salva i chunk
tipizzati in aiura_legal.chunks.

Progettato per essere richiamato da script CLI via asyncio.run().
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

from aiura_legal.ingestion.chunker import Chunker, NormattivaChunker
from aiura_legal.ingestion.normattiva.chunk_id import compute_deterministic_chunk_id
from aiura_legal.ingestion.normattiva.parser import NormattivaDocAdapter
from aiura_legal.core.graph.builder import LegalGraphBuilder


# ---------------------------------------------------------------------------
# Risultato chunking
# ---------------------------------------------------------------------------

@dataclass
class ChunkCollectionResult:
    docs_processed: int = 0
    chunks_created: int = 0
    docs_skipped: int = 0      # testo vuoto o formula (se skip_formule=True)
    errors: int = 0
    duration_s: float = 0.0


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class NormattivaPipeline:
    """
    Legge da `aiura_legal.normattiva_docs`, chunka e salva in `aiura_legal.chunks`.

    Ogni documento Normattiva (= un articolo) viene chunked con NormattivaChunker
    adattivo (≤400 token→intero, ≤800→256/32, >800→256/64). I chunk ottengono corpus="normattiva",
    fonte=fonte_from_doc(), testo_tipo dal documento sorgente.

    Utilizzo tipico:
        pipeline = NormattivaPipeline(mongo_db=client.db, workspace="mio-studio")
        result = await pipeline.chunk_collection()
    """

    def __init__(
        self,
        mongo_db,                               # motor database (aiura_legal)
        workspace: str,
        chunker: Optional[Chunker] = None,
        skip_formule: bool = False,             # se True, salta testo_tipo="formula"
        upsert: bool = True,                    # upsert chunk per source_id+chunk_index
        batch_size: int = 200,
        graph_builder: Optional[LegalGraphBuilder] = None,
        workspace_path: Optional[str] = None,  # path su disco per graph.json
    ) -> None:
        self.db = mongo_db
        self.workspace = workspace
        # NOTA: modifica chunk size invalida chunk esistenti — richiede rebuild completo
        self.chunker = chunker or NormattivaChunker()
        self.skip_formule = skip_formule
        self.upsert = upsert
        self.batch_size = batch_size
        self._graph_builder = graph_builder
        self._workspace_path = workspace_path

    # ------------------------------------------------------------------
    # Chunking dell'intera collection normattiva_docs
    # ------------------------------------------------------------------

    async def _ensure_indexes(self) -> None:
        """Crea gli indici necessari su chunks (idempotente, background=True)."""
        try:
            col = self.db["chunks"]
            await col.create_index(
                [("source_id", 1), ("chunk_index", 1), ("workspace", 1)],
                unique=True,
                background=True,
                name="source_chunk_ws",
            )
            await col.create_index([("workspace", 1)], background=True, name="workspace_1")
            await col.create_index(
                [("corpus", 1), ("fonte", 1)], background=True, name="corpus_fonte_1"
            )
        except Exception as exc:
            logger.warning(f"[NormPipeline] ensure_indexes (non-fatal): {exc}")

    async def chunk_collection(
        self,
        filter_query: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> ChunkCollectionResult:
        """
        Itera su normattiva_docs, chunka ogni articolo, salva in chunks.

        Args:
            filter_query: filtro MongoDB opzionale (es. {"testo_tipo": "normativo"})
            limit:        numero massimo di documenti da processare (None = tutti)
        """
        await self._ensure_indexes()
        result = ChunkCollectionResult()
        t0 = time.monotonic()

        query = filter_query or {}
        if self.skip_formule:
            query = {**query, "testo_tipo": {"$ne": "formula"}}

        cursor = self.db["normattiva_docs"].find(query).batch_size(self.batch_size)

        chunk_buffer: list[dict] = []
        count = 0

        async for raw_doc in cursor:
            if limit and count >= limit:
                break
            count += 1

            try:
                adapter = NormattivaDocAdapter.from_mongo_doc(raw_doc)
                n = await self._process_doc(adapter, chunk_buffer)
                result.docs_processed += 1
                result.chunks_created += n
            except Exception as exc:
                logger.warning(f"[NormPipeline] Errore doc {raw_doc.get('urn','?')}: {exc}")
                result.errors += 1

            # Flush buffer ogni batch_size documenti
            if len(chunk_buffer) >= self.batch_size:
                await self._flush(chunk_buffer)
                chunk_buffer = []

        # Flush finale
        if chunk_buffer:
            await self._flush(chunk_buffer)

        result.duration_s = time.monotonic() - t0
        logger.success(
            f"[NormPipeline] {result.docs_processed} doc → "
            f"{result.chunks_created} chunk in {result.duration_s:.1f}s "
            f"(workspace={self.workspace})"
        )
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _process_doc(
        self, adapter: NormattivaDocAdapter, buffer: list[dict]
    ) -> int:
        """
        Chunka un documento e aggiunge i chunk al buffer.
        Ritorna il numero di chunk generati.
        """
        if not adapter.text.strip():
            return 0

        chunk_base = adapter.to_chunk_base(self.workspace)
        chunks = self.chunker.chunk(adapter.text)

        for c in chunks:
            record = {
                **chunk_base,
                "chunk_index": c.index,
                "text": c.text,
                "token_count": c.token_count,
            }
            # _id deterministico da identità stabile (titolo dell'atto +
            # articolo_num + valid_from + chunk_index), NON dall'URN
            # posizionale del fetcher (source_id) né da "fonte" (tassonomia
            # grossolana condivisa da migliaia di atti diversi) — vedi
            # chunk_id.py per il motivo. Garantisce che lo stesso articolo
            # produca sempre lo stesso _id tra rebuild successivi.
            record["_id"] = compute_deterministic_chunk_id(
                workspace=chunk_base["workspace"],
                titolo=chunk_base["titolo"],
                articolo_num=chunk_base["articolo_num"],
                valid_from=chunk_base.get("valid_from"),
                chunk_index=c.index,
            )
            buffer.append(record)

        return len(chunks)

    async def _flush(self, buffer: list[dict]) -> None:
        """Salva/upserta i chunk dal buffer in MongoDB e aggiorna il grafo."""
        if not buffer:
            return
        try:
            if self.upsert:
                from pymongo import UpdateOne
                # _id è nel filtro, non nel $set: alcune versioni di MongoDB
                # rifiutano $set su _id anche a parità di valore. Sull'insert
                # (upsert=True), MongoDB usa comunque il filtro come valore
                # iniziale di _id per il nuovo documento.
                ops = [
                    UpdateOne(
                        {"_id": r["_id"]},
                        {"$set": {k: v for k, v in r.items() if k != "_id"}},
                        upsert=True,
                    )
                    for r in buffer
                ]
                await self.db["chunks"].bulk_write(ops, ordered=False)
            else:
                await self.db["chunks"].insert_many(buffer, ordered=False)
            logger.debug(f"[NormPipeline] Flushed {len(buffer)} chunk")
        except Exception as exc:
            logger.error(f"[NormPipeline] Flush error: {exc}")

        # Hook grafo: update incrementale per chunk del batch
        if self._graph_builder and self._workspace_path:
            try:
                self._graph_builder.update_batch(buffer, self._workspace_path)
            except Exception as exc:
                logger.warning(f"[NormPipeline] Graph update_batch error: {exc}")
