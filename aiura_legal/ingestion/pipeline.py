"""
Tier 1 Pipeline: file → MongoDB (documents + chunks + ingestion_queue).

Flusso:
  1. Estrae testo  (DocumentExtractor)
  2. Anonimizza PII  (LegalAnonymizer)
  3. Salva LegalDocument in MongoDB.documents
  4. Chunking sliding window  (Chunker)
  5. Salva chunk in MongoDB.chunks
  6. Accoda IngestionJob EMBED per Tier 2
  7. Aggiorna documento: is_chunked=True
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from bson import ObjectId
from loguru import logger

from aiura_legal.core.anonymizer.anonymizer import LegalAnonymizer
from aiura_legal.core.graph.builder import LegalGraphBuilder
from aiura_legal.ingestion.chunker import Chunker
from aiura_legal.ingestion.extractor import DocumentExtractor, UnsupportedFormatError


# ---------------------------------------------------------------------------
# Risultato ingestione
# ---------------------------------------------------------------------------

@dataclass
class IngestResult:
    document_id: str
    filename: str
    workspace: str
    text_length: int
    chunk_count: int
    pii_stats: dict = field(default_factory=dict)
    duration_s: float = 0.0
    status: str = "ok"          # "ok" | "error"
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Pipeline Tier 1
# ---------------------------------------------------------------------------

class Tier1Pipeline:
    """
    Pipeline ingestione sincrona/async.
    Accetta un motor database per facilitare i test con mongomock-motor.
    """

    def __init__(
        self,
        mongo_db,
        workspace: str,
        anonymizer: Optional[LegalAnonymizer] = None,
        chunker: Optional[Chunker] = None,
        graph_builder: Optional[LegalGraphBuilder] = None,
        workspace_path: Optional[str] = None,  # path su disco per graph.json
        corpus: str = "studio",  # "studio" | "dottrina"
    ) -> None:
        self.db = mongo_db
        self.workspace = workspace
        self.corpus = corpus if corpus in ("studio", "dottrina") else "studio"
        self.extractor = DocumentExtractor()
        self.anonymizer = anonymizer or LegalAnonymizer(use_spacy=False)
        self.chunker = chunker or Chunker()
        self._graph_builder = graph_builder
        self._workspace_path = workspace_path

    # ------------------------------------------------------------------
    # Ingestione singolo file
    # ------------------------------------------------------------------

    async def ingest(self, file_path: str) -> IngestResult:
        """
        Processa un singolo file e lo salva in MongoDB.
        Mai solleva eccezioni — gli errori sono catturati in IngestResult.
        """
        t0 = time.monotonic()
        path = Path(file_path)
        logger.info(f"[Tier1] {path.name} → workspace={self.workspace}")

        # 1. Estrazione testo
        try:
            text, meta = self.extractor.extract(file_path)
        except UnsupportedFormatError as e:
            return self._error(path, t0, f"Formato non supportato: {e}")
        except Exception as e:
            return self._error(path, t0, f"Extractor: {e}")

        if not text.strip():
            return self._error(path, t0, "Testo estratto vuoto")

        # 2. Anonimizzazione PII
        try:
            anon = self.anonymizer.anonymize(text, doc_id=path.stem)
        except Exception as e:
            logger.warning(f"[Tier1] Anonymizer fallito, uso testo originale: {e}")
            from aiura_legal.core.anonymizer.anonymizer import AnonymizationResult
            anon = AnonymizationResult(anonymized_text=text, stats={})

        # 3. Salva LegalDocument
        doc_id = str(ObjectId())
        now = datetime.now(timezone.utc)
        doc_record = {
            "_id": doc_id,
            "title": path.stem,
            "text": anon.anonymized_text,
            "doc_type": "altro",
            "source": "upload",
            "source_id": path.stem,
            "workspace": self.workspace,
            "is_anonymized": True,
            "is_chunked": False,
            "is_indexed_bm25": False,
            "is_indexed_vector": False,
            "migrated_from_lab": False,
            "created_at": now,
        }
        try:
            await self.db["documents"].insert_one(doc_record)
        except Exception as e:
            return self._error(path, t0, f"MongoDB insert document: {e}")

        logger.debug(f"[Tier1] Documento salvato: {doc_id}")

        # 4. Chunking
        try:
            chunks = self.chunker.chunk(anon.anonymized_text)
        except Exception as e:
            logger.error(f"[Tier1] Chunker fallito: {e}")
            chunks = []

        # 5. Salva chunks
        if chunks:
            chunk_records = [
                {
                    "document_id": doc_id,
                    "chunk_index": c.index,
                    "text": c.text,
                    "token_count": c.token_count,
                    "doc_type": "altro",
                    "source": "upload",
                    "source_id": path.stem,
                    "workspace": self.workspace,
                    "corpus": self.corpus,
                    "fonte": "altro",
                    "testo_tipo": "normativo",
                }
                for c in chunks
            ]
            try:
                await self.db["chunks"].insert_many(chunk_records)
                logger.debug(f"[Tier1] {len(chunks)} chunk salvati")
            except Exception as e:
                logger.error(f"[Tier1] Errore salvataggio chunk: {e}")
                await self.db["documents"].update_one(
                    {"_id": doc_id},
                    {"$set": {"is_chunked": False, "error": str(e)}},
                )
                return self._error(path, t0, f"Salvataggio chunk fallito: {e}")

            # Hook grafo: update incrementale
            if self._graph_builder and self._workspace_path:
                try:
                    self._graph_builder.update_batch(chunk_records, self._workspace_path)
                except Exception as exc:
                    logger.warning(f"[Tier1] Graph update_batch error: {exc}")

        # 6. Aggiorna documento: is_chunked
        await self.db["documents"].update_one(
            {"_id": doc_id},
            {"$set": {"is_chunked": len(chunks) > 0}},
        )

        # 7. Accoda job Tier 2 (embedding)
        job_record = {
            "document_id": doc_id,
            "job_type": "EMBED",
            "tier": 2,
            "status": "pending",
            "priority": 5,
            "created_at": now,
            "retry_count": 0,
        }
        try:
            await self.db["ingestion_queue"].insert_one(job_record)
        except Exception as e:
            logger.warning(f"[Tier1] Job EMBED non accodato: {e}")

        duration = time.monotonic() - t0
        logger.success(
            f"[Tier1] OK: {path.name} → {len(chunks)} chunk in {duration:.2f}s "
            f"PII: {anon.stats}"
        )

        return IngestResult(
            document_id=doc_id,
            filename=path.name,
            workspace=self.workspace,
            text_length=len(text),
            chunk_count=len(chunks),
            pii_stats=anon.stats,
            duration_s=duration,
            status="ok",
        )

    async def ingest_batch(
        self, file_paths: list[str]
    ) -> list[IngestResult]:
        """Processa più file in sequenza."""
        results = []
        for fp in file_paths:
            results.append(await self.ingest(fp))
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _error(self, path: Path, t0: float, msg: str) -> IngestResult:
        logger.error(f"[Tier1] ERRORE {path.name}: {msg}")
        return IngestResult(
            document_id="",
            filename=path.name,
            workspace=self.workspace,
            text_length=0,
            chunk_count=0,
            status="error",
            error=msg,
            duration_s=time.monotonic() - t0,
        )
