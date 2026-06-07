"""
Router per operazioni giurisprudenziali:
  POST /jurisprudence/upload  — carica sentenza PDF da studio
  GET  /jurisprudence/sync    — stato ultimo sync per fonte
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi import status as http_status
from loguru import logger
from pydantic import BaseModel

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.jurisprudence.coordinator import JurisprudenceCoordinator
from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza, SourceChannel
from aiura_legal.jurisprudence.parser import parse_pdf

router = APIRouter(prefix="/jurisprudence", tags=["jurisprudence"])


class UploadResponse(BaseModel):
    document_id: str
    organo: str
    numero: str
    anno: int
    status: str
    is_anonymized: bool


class SyncStateItem(BaseModel):
    source: str
    last_sync: str | None


class SyncStateResponse(BaseModel):
    sources: list[SyncStateItem]


@router.post("/upload", response_model=UploadResponse, status_code=http_status.HTTP_201_CREATED)
async def upload_sentenza(
    file: UploadFile = File(..., description="PDF della sentenza"),
    organo: str = Form(..., description="cassazione|tar|consiglio_stato|corte_cost|corte_conti"),
    numero: str = Form(..., description="Numero sentenza (es. '12345')"),
    anno: int = Form(..., description="Anno della sentenza"),
):
    """
    Carica una sentenza PDF dallo studio legale.
    Il documento viene sempre anonimizzato prima dell'indicizzazione
    (policy: upload_studio → anonymizer_bridge obbligatorio).
    """
    try:
        organo_enum = OrganoGiudicante(organo.lower())
    except ValueError:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"organo non valido: '{organo}'. Valori: {[o.value for o in OrganoGiudicante]}",
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo file PDF sono accettati per il caricamento di sentenze",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        pdf_bytes = Path(tmp_path).read_bytes()
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    raw = RawSentenza(
        numero=numero,
        anno=anno,
        organo=organo_enum,
        source_url=f"upload:{file.filename}",
        raw_pdf_bytes=pdf_bytes,
    )

    try:
        doc = parse_pdf(raw, source_channel=SourceChannel.UPLOAD_STUDIO)
    except Exception as exc:
        logger.error("Upload sentenza: parsing PDF fallito — {}", exc)
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Impossibile estrarre testo dal PDF: {exc}",
        )

    mongo = MongoClient.get()
    coordinator = JurisprudenceCoordinator(mongo.db)
    stats = await coordinator.ingest([doc])

    if stats["errors"]:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'ingestione della sentenza",
        )

    status_str = "skipped" if stats["skipped"] else "inserted"
    logger.info(
        "Upload sentenza: organo={} numero={} anno={} status={}",
        organo, numero, anno, status_str,
    )

    anon_doc = await mongo.db["jurisprudence"].find_one({"_id": doc.id})
    is_anon = anon_doc.get("is_anonymized", False) if anon_doc else False

    return UploadResponse(
        document_id=doc.id,
        organo=organo,
        numero=numero,
        anno=anno,
        status=status_str,
        is_anonymized=is_anon,
    )


@router.get("/sync", response_model=SyncStateResponse)
async def get_sync_state():
    """Stato dell'ultimo sync per ogni fonte di scraping."""
    mongo = MongoClient.get()
    coordinator = JurisprudenceCoordinator(mongo.db)

    items: list[SyncStateItem] = []
    for organo in OrganoGiudicante:
        last = await coordinator.get_last_sync(organo)
        items.append(SyncStateItem(
            source=organo.value,
            last_sync=last.isoformat() if last else None,
        ))

    return SyncStateResponse(sources=items)
