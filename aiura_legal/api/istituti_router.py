"""
Istituti Giuridici router — GET /istituti, GET /istituti/{id}, POST /istituti,
PUT /istituti/{id}, DELETE /istituti/{id}.

UI di gestione degli Istituti Giuridici (vedi
docs/superpowers/specs/2026-06-30-istituti-giuridici-crud-design.md):
l'avvocato crea/modifica/cancella le schede istituto senza toccare MongoDB
a mano. Stesso stile di questioni_router.py, ma store su Mongo (documenti
indipendenti con optimistic locking per-documento) invece di YAML su disco.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status
from pydantic import BaseModel

from aiura_legal.core.graph.istituti_models import IstitutoGiuridico, IstitutoGiuridicoCreate
from aiura_legal.core.graph.istituti_store import (
    IstitutiStore,
    IstitutoNotFoundError,
    VersionConflictError,
)
from aiura_legal.ingestion.mongodb.client import MongoClient

router = APIRouter()


def _get_store() -> IstitutiStore:
    return IstitutiStore(MongoClient.get().istituti_giuridici)


class ChunkSearchResult(BaseModel):
    id: str
    label: str    # titolo breve per la UI
    preview: str  # inizio del testo del chunk


class ChunkSearchResponse(BaseModel):
    results: list[ChunkSearchResult]


class IstitutiListResponse(BaseModel):
    items: list[IstitutoGiuridico]


class IstitutoUpdateRequest(BaseModel):
    istituto: IstitutoGiuridicoCreate
    expected_version: int


@router.get("/search-chunks", response_model=ChunkSearchResponse)
async def search_chunks(
    q: str = Query(..., min_length=2, description="Testo libero da cercare nei chunk"),
    corpus: str | None = Query(default=None, description="normattiva | giurisprudenza | dottrina | studio"),
    limit: int = Query(default=10, ge=1, le=50),
) -> ChunkSearchResponse:
    """
    Ricerca full-text nei chunk MongoDB per popolare i campi source_mongo_id
    della scheda istituto senza dover conoscere l'ObjectId a memoria.
    Restituisce id, label (titolo/articolo) e preview del testo.
    """
    import re
    from bson import ObjectId

    coll = MongoClient.get().chunks
    filt: dict = {"text": {"$regex": re.escape(q), "$options": "i"}}
    if corpus:
        filt["corpus"] = corpus

    cursor = coll.find(filt, {"text": 1, "titolo": 1, "articolo_num": 1, "titolo_articolo": 1, "corpus": 1}).limit(limit)
    results: list[ChunkSearchResult] = []
    async for doc in cursor:
        titolo = doc.get("titolo") or ""
        articolo_num = doc.get("articolo_num") or ""
        titolo_articolo = doc.get("titolo_articolo") or ""
        corpus_val = doc.get("corpus") or ""
        label_parts = [p for p in [articolo_num, titolo_articolo or titolo, f"[{corpus_val}]"] if p]
        label = " — ".join(label_parts) if label_parts else str(doc["_id"])
        testo = (doc.get("text") or "")[:120].replace("\n", " ")
        results.append(ChunkSearchResult(id=str(doc["_id"]), label=label, preview=testo))
    return ChunkSearchResponse(results=results)


@router.get("", response_model=IstitutiListResponse)
async def list_istituti() -> IstitutiListResponse:
    """Lista tutti gli Istituti Giuridici."""
    items = await _get_store().list_all()
    return IstitutiListResponse(items=items)


@router.get("/{id}", response_model=IstitutoGiuridico)
async def get_istituto(id: str) -> IstitutoGiuridico:
    """Singolo istituto, con version (da passare in PUT come expected_version)."""
    try:
        istituto, _ = await _get_store().get(id)
    except IstitutoNotFoundError:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Istituto non trovato")
    return istituto


@router.post("", response_model=IstitutoGiuridico, status_code=http_status.HTTP_201_CREATED)
async def create_istituto(payload: IstitutoGiuridicoCreate) -> IstitutoGiuridico:
    """Crea un nuovo Istituto Giuridico."""
    istituto, _ = await _get_store().create(payload)
    return istituto


@router.put("/{id}", response_model=IstitutoGiuridico)
async def update_istituto(id: str, req: IstitutoUpdateRequest) -> IstitutoGiuridico:
    """
    Sovrascrive l'intero istituto. 409 se la version è obsoleta (il
    documento è cambiato da quando il chiamante l'ha letto), 404 se id
    inesistente.
    """
    try:
        istituto, _ = await _get_store().update(id, req.istituto, req.expected_version)
    except IstitutoNotFoundError:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Istituto non trovato")
    except VersionConflictError as exc:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=str(exc))
    return istituto


@router.delete("/{id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_istituto(id: str) -> None:
    """Cancella l'istituto intero. 404 se già assente."""
    try:
        await _get_store().delete(id)
    except IstitutoNotFoundError:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Istituto non trovato")
