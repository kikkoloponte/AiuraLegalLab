"""
GraphRetriever — neighbor expansion e conflict detection sul grafo giuridico.

Utilizzo:
    retriever = GraphRetriever(workspace_path)

    if retriever.is_available:
        # Espansione con filtro vigenza
        extra = retriever.expand(source_ids, depth=1, valid_on=date(2024,1,1))

        # Conflict detection per CitationReviewer
        conflicts = retriever.get_conflicts(source_ids)

Graceful degradation: se graph.json non esiste → is_available=False,
expand() e get_conflicts() ritornano liste vuote senza sollevare eccezioni.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from loguru import logger

try:
    import networkx as nx
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "networkx non installato. Esegui: pip install networkx>=3.3"
    ) from e

from aiura_legal.core.types import SearchResult


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

_GRAPH_FILENAME = "graph.json"
_EXPANSION_EDGE_TYPES = {"RINVIA", "ABROGA", "MODIFICA"}
_CONFLICT_EDGE_TYPES = {"CONTRASTA", "ABROGA"}


# ---------------------------------------------------------------------------
# GraphRetriever
# ---------------------------------------------------------------------------

class GraphRetriever:
    """
    Legge graph.json dal workspace e offre due operazioni:

    1. expand()       — neighbor expansion per retrieval (con filtro vigenza)
    2. get_conflicts() — trova archi CONTRASTA/ABROGA per CitationReviewer
    """

    def __init__(self, workspace_path: str) -> None:
        self._path = Path(workspace_path) / "indices" / _GRAPH_FILENAME
        self._graph: Optional[nx.DiGraph] = None
        self._loaded = False

    # ------------------------------------------------------------------
    # Proprietà pubblica
    # ------------------------------------------------------------------

    @property
    def is_available(self) -> bool:
        """True se graph.json esiste sul disco."""
        return self._path.exists()

    # ------------------------------------------------------------------
    # expand()
    # ------------------------------------------------------------------

    def expand(
        self,
        source_ids: list[str],
        depth: int = 1,
        edge_types: Optional[list[str]] = None,
        max_nodes: int = 10,
        valid_on: Optional[date] = None,
    ) -> list[SearchResult]:
        """
        Espande source_ids di `depth` hop nel grafo.

        Args:
            source_ids:  nodi di partenza (source_id degli articoli già recuperati)
            depth:       profondità di espansione (1 = vicini diretti)
            edge_types:  tipi di arco da seguire (default: RINVIA, ABROGA, MODIFICA)
            max_nodes:   numero massimo di risultati restituiti
            valid_on:    se specificato, filtra i nodi non vigenti alla data

        Returns:
            Lista di SearchResult con retrieval_method="graph_expansion".
            Score = 1/(1+distanza), decrescente con la distanza.
            I source_ids di input non compaiono nell'output.
        """
        if not self.is_available:
            return []

        G = self._load_graph()
        if G is None:
            return []

        allowed_types = set(edge_types) if edge_types is not None else _EXPANSION_EDGE_TYPES
        input_set = {sid.upper() for sid in source_ids}

        # BFS manuale fino a depth hop
        visited: dict[str, int] = {}   # node_id → distanza minima
        frontier = [(sid, 0) for sid in source_ids if G.has_node(sid)]

        while frontier:
            node, dist = frontier.pop(0)
            if dist >= depth:
                continue
            for _, neighbor, edge_data in G.out_edges(node, data=True):
                if edge_data.get("edge_type") not in allowed_types:
                    continue
                if neighbor.upper() in input_set:
                    continue
                n_dist = dist + 1
                if neighbor not in visited or visited[neighbor] > n_dist:
                    visited[neighbor] = n_dist
                    frontier.append((neighbor, n_dist))

        results: list[SearchResult] = []
        for node_id, dist in sorted(visited.items(), key=lambda x: x[1]):
            if len(results) >= max_nodes:
                break

            node_attrs = G.nodes.get(node_id, {})
            if node_attrs.get("node_type") != "article":
                continue

            # Filtro vigenza
            if valid_on is not None and not self._is_valid(node_attrs, valid_on):
                continue

            score = 1.0 / (1.0 + dist)
            results.append(SearchResult(
                doc_id=node_id,
                score=round(score, 4),
                snippet=f"[graph] {node_attrs.get('titolo', '')} {node_attrs.get('articolo_num', '')}".strip(),
                source_id=node_id,
                retrieval_method="graph_expansion",
                metadata={
                    "fonte": node_attrs.get("fonte", ""),
                    "titolo": node_attrs.get("titolo", ""),
                    "articolo_num": node_attrs.get("articolo_num", ""),
                    "graph_distance": dist,
                    "valid_from": node_attrs.get("valid_from"),
                    "valid_to": node_attrs.get("valid_to"),
                },
            ))

        return results

    # ------------------------------------------------------------------
    # get_conflicts()
    # ------------------------------------------------------------------

    def get_conflicts(
        self,
        source_ids: list[str],
    ) -> list[tuple[str, str, str]]:
        """
        Trova archi CONTRASTA o ABROGA tra i source_ids dati.

        Args:
            source_ids: lista di source_id (URN) da controllare

        Returns:
            Lista di (from_id, to_id, edge_type) per ogni coppia in conflitto.
            Lista vuota se nessun conflitto o grafo non disponibile.
        """
        if not self.is_available:
            return []

        G = self._load_graph()
        if G is None:
            return []

        id_set = set(source_ids)
        conflicts: list[tuple[str, str, str]] = []

        for sid in source_ids:
            if not G.has_node(sid):
                continue
            for _, neighbor, edge_data in G.out_edges(sid, data=True):
                if edge_data.get("edge_type") in _CONFLICT_EDGE_TYPES:
                    if neighbor in id_set:
                        conflicts.append((sid, neighbor, edge_data["edge_type"]))

        return conflicts

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    def _load_graph(self) -> Optional[nx.DiGraph]:
        """Carica il grafo in memoria (lazy, una sola volta)."""
        if self._loaded:
            return self._graph

        self._loaded = True
        if not self._path.exists():
            self._graph = None
            return None

        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._graph = nx.node_link_graph(data, edges="edges")
            logger.info(
                f"[GraphRetriever] caricato: {self._graph.number_of_nodes()} nodi, "
                f"{self._graph.number_of_edges()} archi"
            )
        except Exception as exc:
            logger.warning(f"[GraphRetriever] errore caricamento graph.json: {exc}")
            self._graph = None

        return self._graph

    @staticmethod
    def _is_valid(node_attrs: dict, valid_on: date) -> bool:
        """
        Ritorna True se il nodo è vigente alla data valid_on.

        Convenzioni:
          valid_from: "YYYYMMDD" o None (→ sempre valido)
          valid_to:   "YYYYMMDD", "99999999" (vigente), o None (→ vigente)
        """
        d_str = valid_on.strftime("%Y%m%d")

        vf = node_attrs.get("valid_from")
        if vf and vf != "00000000":
            if d_str < vf:
                return False  # non ancora in vigore

        vt = node_attrs.get("valid_to")
        if vt and vt != "99999999":
            if d_str > vt:
                return False  # abrogato

        return True
