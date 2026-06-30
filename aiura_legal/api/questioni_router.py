"""
Questioni router — GET /questioni, GET /questioni/{id}, PUT /questioni/{id},
GET /questioni/search-nodes.

UI di revisione per ontology/questioni_curate.yaml (vedi
docs/superpowers/specs/2026-06-26-questioni-review-ui-design.md): l'avvocato
approva/modifica/rifiuta le QuestioneGiuridica proposte senza editare YAML
a mano.

Stesso stile di graph_router.py: APIRouter a sé stante, stato lazy a livello
di modulo (qui: QuestioniRegistry e GraphRetriever, entrambi leggeri — nessun
caricamento bloccante al lifespan come per il grafo di /graph).
"""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.core.graph.questione_loader import QuestioneGiuridica, QuestioneRegistryError
from aiura_legal.core.graph.questioni_registry import (
    QuestioneNotFoundError,
    QuestioniRegistry,
    VersionConflictError,
)
from aiura_legal.core.graph.retriever import GraphRetriever

router = APIRouter()


class _QuestioniSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    aiura_workspaces_path: str = "C:/project/AiUraLegalLab/workspaces"


_settings = _QuestioniSettings()
_default_workspace_path = f"{_settings.aiura_workspaces_path}/mio-studio"

_registry: Optional[QuestioniRegistry] = None
_graph: Optional[GraphRetriever] = None


def _get_registry() -> QuestioniRegistry:
    global _registry
    if _registry is None:
        _registry = QuestioniRegistry(workspace_path=_default_workspace_path)
    return _registry


def _get_graph() -> GraphRetriever:
    global _graph
    if _graph is None:
        _graph = GraphRetriever(_default_workspace_path)
    return _graph


# ---------------------------------------------------------------------------
# Modelli risposta
# ---------------------------------------------------------------------------

class QuestioneModel(BaseModel):
    id: str
    formulazione: str
    materia: str
    parole_chiave: list[str] = []
    norme_pertinenti: list[str] = []
    decisioni_pertinenti: list[str] = []
    stato: str


class QuestioneWithVersion(BaseModel):
    questione: QuestioneModel
    version: str


class QuestioniListResponse(BaseModel):
    items: list[QuestioneModel]
    version: str
    # version è a livello di file (lock optimistic sull'intero registro, non
    # per voce — vedi QuestioniRegistry.current_version): tutte le voci di
    # questa risposta condividono la stessa version, da passare come
    # expected_version in qualunque PUT successivo.


class QuestioneUpdateRequest(BaseModel):
    changes: dict[str, Any]
    expected_version: str


class NodeSearchResult(BaseModel):
    id: str
    label: str


class NodeSearchResponse(BaseModel):
    results: list[NodeSearchResult]


def _to_model(q: QuestioneGiuridica) -> QuestioneModel:
    return QuestioneModel(
        id=q.id,
        formulazione=q.formulazione,
        materia=q.materia,
        parole_chiave=q.parole_chiave,
        norme_pertinenti=q.norme_pertinenti,
        decisioni_pertinenti=q.decisioni_pertinenti,
        stato=q.stato,
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("", response_model=QuestioniListResponse)
async def list_questioni(
    stato: Optional[str] = Query(default=None, description="proposto | approvato | rifiutato"),
) -> QuestioniListResponse:
    """Lista tutte le QuestioneGiuridica del registro, filtro opzionale per stato."""
    registry = _get_registry()
    questioni = registry.list(stato=stato)
    return QuestioniListResponse(items=[_to_model(q) for q in questioni], version=registry.current_version())


@router.get("/search-nodes", response_model=NodeSearchResponse)
async def search_nodes(
    q: str = Query(..., min_length=2, description="Testo di ricerca"),
    node_type: str = Query(..., pattern="^(article|sentenza)$"),
    limit: int = Query(default=10, ge=1, le=50),
) -> NodeSearchResponse:
    """Autocomplete id reali dal grafo per norme_pertinenti/decisioni_pertinenti."""
    results = _get_graph().search_nodes(q, node_type=node_type, limit=limit)
    return NodeSearchResponse(results=[NodeSearchResult(**r) for r in results])


@router.get("/{id}", response_model=QuestioneWithVersion)
async def get_questione(id: str) -> QuestioneWithVersion:
    """Singola voce + version (da passare in PUT come expected_version)."""
    try:
        questione, version = _get_registry().get(id)
    except QuestioneNotFoundError:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Questione non trovata")
    return QuestioneWithVersion(questione=_to_model(questione), version=version)


@router.put("/{id}", response_model=QuestioneWithVersion)
async def update_questione(id: str, req: QuestioneUpdateRequest) -> QuestioneWithVersion:
    """
    Modifica/approva/rifiuta una voce. 409 se la versione è obsoleta
    (il file è cambiato da quando il chiamante l'ha letto), 400 se changes
    referenzia un id inesistente nel grafo o uno stato non valido.
    """
    try:
        questione, version = _get_registry().update(id, req.changes, req.expected_version)
    except QuestioneNotFoundError:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Questione non trovata")
    except VersionConflictError as exc:
        raise HTTPException(status_code=http_status.HTTP_409_CONFLICT, detail=str(exc))
    except QuestioneRegistryError as exc:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return QuestioneWithVersion(questione=_to_model(questione), version=version)
