"""
AiUra LegalLab — TfuePipeline.

Chunka una lista di TfueArticle (già parsati da parser.py) e salva i chunk
tipizzati in aiura_legal_lab_db.chunks. Riusa NormattivaChunker (adattivo,
stessa strategia degli articoli normattiva: gli articoli TFUE hanno
lunghezza paragonabile agli articoli dei codici italiani).
"""
from __future__ import annotations

import time
from dataclasses import dataclass

from loguru import logger

from aiura_legal.ingestion.chunker import NormattivaChunker
from aiura_legal.ingestion.eu_treaties.parser import TfueArticle, TfueDocAdapter


@dataclass
class TfueChunkResult:
    articles_processed: int = 0
    chunks_created: int = 0
    duration_s: float = 0.0


class TfuePipeline:
    """
    Chunka articoli TFUE e li salva in `chunks` (upsert per source_id+chunk_index+workspace,
    stessa convenzione di NormattivaPipeline).
    """

    def __init__(
        self,
        mongo_db,
        workspace: str,
        batch_size: int = 200,
        upsert: bool = True,
    ) -> None:
        self.db = mongo_db
        self.workspace = workspace
        self.chunker = NormattivaChunker()
        self.batch_size = batch_size
        self.upsert = upsert

    async def chunk_articles(self, articles: list[TfueArticle]) -> TfueChunkResult:
        result = TfueChunkResult()
        t0 = time.monotonic()
        buffer: list[dict] = []

        for article in articles:
            if not article.testo.strip():
                continue
            adapter = TfueDocAdapter.from_article(article)
            chunk_base = adapter.to_chunk_base(self.workspace)
            chunks = self.chunker.chunk(adapter.text)

            for c in chunks:
                buffer.append({
                    **chunk_base,
                    "chunk_index": c.index,
                    "text": c.text,
                    "token_count": c.token_count,
                })

            result.articles_processed += 1
            result.chunks_created += len(chunks)

            if len(buffer) >= self.batch_size:
                await self._flush(buffer)
                buffer = []

        if buffer:
            await self._flush(buffer)

        result.duration_s = time.monotonic() - t0
        logger.success(
            f"[TfuePipeline] {result.articles_processed} articoli → "
            f"{result.chunks_created} chunk in {result.duration_s:.1f}s "
            f"(workspace={self.workspace})"
        )
        return result

    async def _flush(self, buffer: list[dict]) -> None:
        if not buffer:
            return
        if self.upsert:
            from pymongo import UpdateOne
            ops = [
                UpdateOne(
                    {
                        "source_id": r["source_id"],
                        "chunk_index": r["chunk_index"],
                        "workspace": r["workspace"],
                    },
                    {"$set": r},
                    upsert=True,
                )
                for r in buffer
            ]
            await self.db["chunks"].bulk_write(ops, ordered=False)
        else:
            await self.db["chunks"].insert_many(buffer, ordered=False)
        logger.debug(f"[TfuePipeline] Flushed {len(buffer)} chunk")
