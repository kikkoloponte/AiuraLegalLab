"""
Graph router — GET /graph/search  e  GET /graph/subgraph

Il grafo NetworkX viene iniettato da app.py tramite set_graph() al lifespan.
Nessuna lettura da disco per richiesta.
"""
from __future__ import annotations

from typing import Any

import networkx as nx
from fastapi import APIRouter, HTTPException, Query
from fastapi import status as http_status
from pydantic import BaseModel

router = APIRouter()

# ---------------------------------------------------------------------------
# Stato globale iniettato da app.py
# ---------------------------------------------------------------------------

_graph: nx.DiGraph | None = None
_nodes_index: dict[str, dict[str, Any]] = {}  # id → attributi nodo


def set_graph(g: nx.DiGraph) -> None:
    global _graph, _nodes_index
    _graph = g
    _nodes_index = dict(g.nodes(data=True))


def _require_graph() -> nx.DiGraph:
    if _graph is None:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="grafo non caricato — riprovare tra qualche secondo",
        )
    return _graph


# ---------------------------------------------------------------------------
# Modelli risposta
# ---------------------------------------------------------------------------

class GraphNodeModel(BaseModel):
    id: str
    type: str       # "norma" | "sentenza"
    label: str
    meta: dict[str, Any] = {}


class GraphLinkModel(BaseModel):
    source: str
    target: str
    type: str


class SearchResponse(BaseModel):
    results: list[GraphNodeModel]


class SubgraphResponse(BaseModel):
    nodes: list[GraphNodeModel]
    links: list[GraphLinkModel]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_label(node_id: str, attrs: dict[str, Any]) -> str:
    if attrs.get("type") == "sentenza":
        organo = str(attrs.get("organo", "")).capitalize()
        numero = attrs.get("numero", "")
        anno = attrs.get("anno", "")
        return f"{organo} n.{numero}/{anno}"
    # norma: preferisci urn se diverso dall'id, altrimenti id
    urn = attrs.get("urn", "")
    return urn if urn and urn != node_id else node_id


def _node_to_model(node_id: str, attrs: dict[str, Any]) -> GraphNodeModel:
    meta = {k: v for k, v in attrs.items() if k not in ("type",)}
    return GraphNodeModel(
        id=node_id,
        type=attrs.get("type", "norma"),
        label=_make_label(node_id, attrs),
        meta=meta,
    )


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.get("/search", response_model=SearchResponse)
async def search_nodes(
    q: str = Query(..., min_length=2, description="Testo di ricerca"),
    limit: int = Query(default=20, ge=1, le=100),
) -> SearchResponse:
    """Cerca nodi nel grafo per testo (norma: id/urn, sentenza: organo+numero+anno)."""
    _require_graph()
    q_lower = q.lower()
    results: list[GraphNodeModel] = []

    for node_id, attrs in _nodes_index.items():
        if len(results) >= limit:
            break
        node_type = attrs.get("type", "norma")
        if node_type == "norma":
            haystack = f"{node_id} {attrs.get('urn', '')}".lower()
        else:
            haystack = (
                f"{attrs.get('organo', '')} {attrs.get('numero', '')} {attrs.get('anno', '')}"
            ).lower()
        if q_lower in haystack:
            results.append(_node_to_model(node_id, attrs))

    return SearchResponse(results=results)


@router.get("/subgraph", response_model=SubgraphResponse)
async def get_subgraph(
    center: str = Query(..., description="ID del nodo centrale"),
    depth: int = Query(default=1, ge=1, le=2),
    limit: int = Query(default=50, ge=1, le=200),
) -> SubgraphResponse:
    """Ritorna il sottografo BFS centrato su un nodo, nel formato react-force-graph."""
    g = _require_graph()

    if center not in _nodes_index:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"nodo '{center}' non trovato nel grafo",
        )

    # BFS undirected fino a depth livelli
    sub: nx.DiGraph = nx.ego_graph(g, center, radius=depth, undirected=True)

    # Se supera il limite: mantieni center + nodi con più archi
    if sub.number_of_nodes() > limit:
        degree_map = dict(sub.degree())
        sorted_nodes = sorted(degree_map, key=lambda n: degree_map[n], reverse=True)
        keep = {center} | set(sorted_nodes[: limit - 1])
        sub = sub.subgraph(keep).copy()

    nodes: list[GraphNodeModel] = []
    for nid, attrs in sub.nodes(data=True):
        nodes.append(_node_to_model(nid, attrs))

    links: list[GraphLinkModel] = []
    for src, dst, eattrs in sub.edges(data=True):
        links.append(GraphLinkModel(
            source=src,
            target=dst,
            type=eattrs.get("type", "cita"),
        ))

    return SubgraphResponse(nodes=nodes, links=links)
