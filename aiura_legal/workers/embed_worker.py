"""
Tier 2 EmbedWorker — consuma job EMBED da ingestion_queue e aggiunge
i chunk di ogni documento a ChromaDB (VectorRetriever).

Flusso per ogni job:
  1. Claim atomico via find_one_and_update (status: pending → processing)
  2. Recupera documento per ottenere workspace
  3. Carica chunk del documento da MongoDB
  4. Converte chunk → Document e fa upsert in ChromaDB
  5. Aggiorna documents.is_indexed_vector = True
  6. Marca job status = "done" (o "failed" con messaggio di errore)

Retry: job falliti con retry_count < max_retries vengono rimessi in pending.

Utilizzo tipico:
    worker = EmbedWorker(mongo_db=client.db, workspaces_base_path="workspaces/")
    await worker.run_once()          # elabora tutti i pending, poi torna
    await worker.run_loop(interval=5) # loop continuo con pausa tra cicli
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from loguru import logger

from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.core.types import Document


_MAX_RETRIES = 3
_EMBED_JOB_TYPE = "EMBED"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EmbedWorker:
    """
    Worker asincrono Tier 2: embedding chunk → ChromaDB.

    Supporta più workspace in un singolo processo: i VectorRetriever vengono
    creati lazily per workspace e tenuti in cache durante l'esecuzione.

    Args:
        mongo_db:             motor database (aiura_legal)
        workspaces_base_path: directory radice dei workspace (es. "workspaces/")
        batch_size:           job da processare per ciclo di run_once()
        chunk_batch_size:     chunk per singolo upsert ChromaDB
    """

    def __init__(
        self,
        mongo_db,
        workspaces_base_path: str,
        batch_size: int = 50,
        chunk_batch_size: int = 100,
    ) -> None:
        self.db = mongo_db
        self._base_path = Path(workspaces_base_path)
        self._batch_size = batch_size
        self._chunk_batch_size = chunk_batch_size
        # Cache VectorRetriever per workspace {workspace: VectorRetriever}
        self._retrievers: dict[str, VectorRetriever] = {}

    # ------------------------------------------------------------------
    # Vector retriever (lazy, per workspace)
    # ------------------------------------------------------------------

    def _get_retriever(self, workspace: str) -> VectorRetriever:
        if workspace not in self._retrievers:
            ws_path = str(self._base_path / workspace)
            self._retrievers[workspace] = VectorRetriever(ws_path)
            logger.debug(f"[EmbedWorker] VectorRetriever caricato: workspace={workspace}")
        return self._retrievers[workspace]

    # ------------------------------------------------------------------
    # Chunk → Document conversion
    # ------------------------------------------------------------------

    @staticmethod
    def _chunk_to_document(chunk: dict) -> Document:
        """Converte un chunk MongoDB in un Document per VectorRetriever."""
        chunk_id = str(chunk.get("_id", ""))
        if not chunk_id:
            # Fallback: source_id + chunk_index
            chunk_id = f"{chunk.get('source_id', 'unk')}_{chunk.get('chunk_index', 0)}"
        return Document(
            id=chunk_id,
            text=chunk.get("text", ""),
            source_id=chunk.get("source_id", ""),
            metadata={
                "corpus": chunk.get("corpus", ""),
                "fonte": chunk.get("fonte", ""),
                "testo_tipo": chunk.get("testo_tipo", ""),
                "titolo": chunk.get("titolo", ""),
                "articolo_num": chunk.get("articolo_num", ""),
                "workspace": chunk.get("workspace", ""),
                "source": chunk.get("source", ""),
                "document_id": chunk.get("document_id", ""),
            },
        )

    # ------------------------------------------------------------------
    # Singolo job EMBED
    # ------------------------------------------------------------------

    async def _process_job(self, job: dict) -> None:
        """
        Processa un job EMBED:
          1. Recupera documento + workspace
          2. Carica chunk da MongoDB
          3. Upsert in ChromaDB
          4. Aggiorna documento e job
        """
        job_id  = str(job["_id"])
        doc_id  = job["document_id"]
        logger.info(f"[EmbedWorker] Inizio job={job_id}, doc={doc_id}")

        try:
            # 1. Recupera il documento per ottenere il workspace
            doc = await self.db["documents"].find_one({"_id": doc_id})
            if doc is None:
                raise ValueError(f"Documento '{doc_id}' non trovato in MongoDB")

            workspace = doc.get("workspace", "default")

            # 2. Carica chunk del documento
            chunks: list[dict] = []
            async for chunk in self.db["chunks"].find(
                {"document_id": doc_id, "workspace": workspace}
            ):
                chunks.append(chunk)

            if not chunks:
                logger.warning(
                    f"[EmbedWorker] Nessun chunk per doc={doc_id} workspace={workspace}"
                )
                # Marca done ugualmente (documento senza chunk è già gestito da Tier 1)
                await self._mark_done(job_id)
                return

            # 3. Converti e upsert in ChromaDB
            retriever = self._get_retriever(workspace)
            documents = [self._chunk_to_document(c) for c in chunks]
            retriever.add_documents_batch(documents, batch_size=self._chunk_batch_size)
            logger.info(
                f"[EmbedWorker] Upserted {len(documents)} chunk → ChromaDB "
                f"(workspace={workspace}, doc={doc_id})"
            )

            # 4. Aggiorna documento: is_indexed_vector = True
            await self.db["documents"].update_one(
                {"_id": doc_id},
                {"$set": {"is_indexed_vector": True}},
            )

            await self._mark_done(job_id)

        except Exception as exc:
            logger.error(f"[EmbedWorker] Errore job={job_id}: {exc}")
            await self._mark_failed(job, str(exc))

    # ------------------------------------------------------------------
    # Job lifecycle helpers
    # ------------------------------------------------------------------

    async def _mark_done(self, job_id: str) -> None:
        await self.db["ingestion_queue"].update_one(
            {"_id": job_id},
            {"$set": {"status": "done", "completed_at": _utcnow()}},
        )

    async def _mark_failed(self, job: dict, error: str) -> None:
        retry_count = job.get("retry_count", 0) + 1
        new_status = "pending" if retry_count < _MAX_RETRIES else "failed"
        await self.db["ingestion_queue"].update_one(
            {"_id": job["_id"]},
            {
                "$set": {
                    "status": new_status,
                    "error": error,
                    "retry_count": retry_count,
                    "completed_at": _utcnow() if new_status == "failed" else None,
                }
            },
        )
        if new_status == "pending":
            logger.warning(
                f"[EmbedWorker] Job {job['_id']} rimesso in pending "
                f"(retry {retry_count}/{_MAX_RETRIES})"
            )
        else:
            logger.error(
                f"[EmbedWorker] Job {job['_id']} fallito definitivamente "
                f"dopo {retry_count} tentativi: {error}"
            )

    # ------------------------------------------------------------------
    # run_once() — un ciclo completo
    # ------------------------------------------------------------------

    async def run_once(self) -> int:
        """
        Processa tutti i job EMBED pending (fino a batch_size).
        Usa find_one_and_update per claim atomico (safe per workers concorrenti).

        Returns:
            Numero di job processati in questo ciclo.
        """
        processed = 0

        for _ in range(self._batch_size):
            # Claim atomico: pending → processing
            job = await self.db["ingestion_queue"].find_one_and_update(
                {
                    "job_type": _EMBED_JOB_TYPE,
                    "status": "pending",
                    "retry_count": {"$lt": _MAX_RETRIES},
                },
                {
                    "$set": {
                        "status": "processing",
                        "started_at": _utcnow(),
                    }
                },
                sort=[("priority", 1), ("created_at", 1)],
                return_document=True,
            )

            if job is None:
                break   # Nessun job pending rimasto

            await self._process_job(job)
            processed += 1

        if processed:
            logger.info(f"[EmbedWorker] Ciclo completato: {processed} job processati")
        else:
            logger.debug("[EmbedWorker] Nessun job EMBED pending")

        return processed

    # ------------------------------------------------------------------
    # run_loop() — loop continuo
    # ------------------------------------------------------------------

    async def run_loop(
        self,
        poll_interval: float = 5.0,
        stop_event: Optional[asyncio.Event] = None,
    ) -> None:
        """
        Loop continuo: run_once(), pausa poll_interval secondi, ripete.

        Args:
            poll_interval: secondi di pausa tra cicli quando la coda è vuota
            stop_event:    asyncio.Event — se settato ferma il loop gracefully
        """
        logger.info(
            f"[EmbedWorker] Loop avviato (poll_interval={poll_interval}s)"
        )
        while True:
            if stop_event and stop_event.is_set():
                logger.info("[EmbedWorker] Stop event ricevuto — uscita dal loop")
                break

            processed = await self.run_once()

            # Se non ci sono job, aspetta prima del prossimo poll
            if processed == 0:
                try:
                    if stop_event:
                        await asyncio.wait_for(
                            asyncio.shield(stop_event.wait()),
                            timeout=poll_interval,
                        )
                        break  # stop_event era settato
                    else:
                        await asyncio.sleep(poll_interval)
                except asyncio.TimeoutError:
                    pass   # timeout normale, prossimo ciclo
