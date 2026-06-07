"""
Estende il grafo NetworkX con nodi sentenza collegati alle norme.

Archi:
  sentenza → norma   : "interpreta"   (da norme_citate)
  sentenza → sentenza: "cita"         (da sentenze_citate)
  norma → sentenza   : "applicata_in" (inverso calcolato)
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
from loguru import logger

from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante

_SENTENZA_NODE_TYPE = "sentenza"
_NORMA_NODE_TYPE = "norma"


class JurisprudenceGraphBuilder:

    def __init__(self, graph_path: str | Path) -> None:
        self._path = Path(graph_path)
        self._graph: nx.DiGraph = self._load()

    # ------------------------------------------------------------------
    # Lettura
    # ------------------------------------------------------------------

    @property
    def graph(self) -> nx.DiGraph:
        return self._graph

    def get_sentenze_per_norma(self, urn: str) -> list[str]:
        """Restituisce gli id delle sentenze che interpretano la norma `urn`."""
        if urn not in self._graph:
            return []
        return [
            nbr for nbr in self._graph.predecessors(urn)
            if self._graph.nodes[nbr].get("type") == _SENTENZA_NODE_TYPE
        ]

    def get_norme_per_sentenza(self, sentenza_id: str) -> list[str]:
        """Restituisce gli URN delle norme citate dalla sentenza."""
        if sentenza_id not in self._graph:
            return []
        return [
            nbr for nbr in self._graph.successors(sentenza_id)
            if self._graph.nodes[nbr].get("type") == _NORMA_NODE_TYPE
        ]

    def sentenza_exists(self, sentenza_id: str) -> bool:
        return sentenza_id in self._graph and \
               self._graph.nodes[sentenza_id].get("type") == _SENTENZA_NODE_TYPE

    # ------------------------------------------------------------------
    # Scrittura
    # ------------------------------------------------------------------

    def add_document(self, doc: JurisprudenceDocument) -> None:
        """Aggiunge nodi e archi per un JurisprudenceDocument."""
        self._add_sentenza_node(doc)

        for urn in doc.norme_citate:
            self._ensure_norma_node(urn)
            self._graph.add_edge(doc.id, urn, type="interpreta")
            self._graph.add_edge(urn, doc.id, type="applicata_in")

        for cited_id in doc.sentenze_citate:
            self._graph.add_edge(doc.id, cited_id, type="cita")

        logger.debug(
            "GraphBuilder: aggiunto {} norme={} cita={}",
            doc.id, len(doc.norme_citate), len(doc.sentenze_citate),
        )

    def add_documents_batch(self, docs: list[JurisprudenceDocument]) -> None:
        for doc in docs:
            self.add_document(doc)

    def remove_document(self, sentenza_id: str) -> None:
        if sentenza_id in self._graph:
            self._graph.remove_node(sentenza_id)

    # ------------------------------------------------------------------
    # Persistenza
    # ------------------------------------------------------------------

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = nx.node_link_data(self._graph, edges="links")
        self._path.write_text(json.dumps(data, ensure_ascii=False, default=str), encoding="utf-8")
        logger.info("GraphBuilder: grafo salvato in {}", self._path)

    def _load(self) -> nx.DiGraph:
        if self._path.exists():
            data = json.loads(self._path.read_text(encoding="utf-8"))
            return nx.node_link_graph(data, directed=True, edges="links")
        return nx.DiGraph()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _add_sentenza_node(self, doc: JurisprudenceDocument) -> None:
        self._graph.add_node(
            doc.id,
            type=_SENTENZA_NODE_TYPE,
            organo=doc.organo.value,
            numero=doc.numero,
            anno=doc.anno,
            materia=doc.materia,
        )

    def _ensure_norma_node(self, urn: str) -> None:
        if urn not in self._graph:
            self._graph.add_node(urn, type=_NORMA_NODE_TYPE, urn=urn)
