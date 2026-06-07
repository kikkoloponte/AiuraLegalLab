"""
Test GraphRetriever.

Strategia:
  - Grafo costruito in memoria e salvato in tmp_path (no MongoDB)
  - Zero PII reali
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import networkx as nx
import pytest

from aiura_legal.core.graph.retriever import GraphRetriever
from aiura_legal.core.types import SearchResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(
        json.dumps(data), encoding="utf-8"
    )


def _article_node(
    node_id: str,
    fonte: str = "codice_civile",
    art_num: str = "1",
    valid_from: str | None = "20000101",
    valid_to: str | None = "99999999",
) -> dict:
    return {
        "node_type": "article",
        "fonte": fonte,
        "titolo": "Codice Civile",
        "articolo_num": art_num,
        "testo_tipo": "normativo",
        "valid_from": valid_from,
        "valid_to": valid_to,
    }


def _make_graph(edges: list[tuple[str, str, str]]) -> nx.DiGraph:
    """Costruisce un DiGraph con nodi article e archi dati come (from, to, edge_type)."""
    G: nx.DiGraph = nx.DiGraph()
    nodes: set[str] = set()
    for u, v, _ in edges:
        nodes.add(u)
        nodes.add(v)
    for n in nodes:
        G.add_node(n, **_article_node(n, art_num=n.split(":")[-1]))
    for u, v, et in edges:
        G.add_edge(u, v, edge_type=et)
    return G


# ---------------------------------------------------------------------------
# is_available
# ---------------------------------------------------------------------------

class TestIsAvailable:

    def test_false_quando_file_assente(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        assert r.is_available is False

    def test_true_quando_file_presente(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.is_available is True


# ---------------------------------------------------------------------------
# expand() — base
# ---------------------------------------------------------------------------

class TestExpand:

    def test_expand_depth1_due_vicini(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA"), ("A", "C", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"], depth=1)
        ids = {res.source_id for res in results}
        assert "B" in ids
        assert "C" in ids

    def test_expand_esclude_input(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"], depth=1)
        assert all(res.source_id != "A" for res in results)

    def test_expand_depth2_include_vicini_di_vicini(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA"), ("B", "C", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"], depth=2)
        ids = {res.source_id for res in results}
        assert "B" in ids
        assert "C" in ids

    def test_expand_score_decrescente_con_distanza(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA"), ("B", "C", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"], depth=2)
        by_id = {res.source_id: res.score for res in results}
        assert by_id["B"] > by_id["C"]

    def test_expand_max_nodes_limita_output(self, tmp_path):
        G = _make_graph([
            ("A", "B", "RINVIA"), ("A", "C", "RINVIA"),
            ("A", "D", "RINVIA"), ("A", "E", "RINVIA"),
        ])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"], depth=1, max_nodes=2)
        assert len(results) <= 2

    def test_expand_retrieval_method(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"], depth=1)
        assert all(res.retrieval_method == "graph_expansion" for res in results)

    def test_expand_ritorna_search_result(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["A"])
        assert all(isinstance(res, SearchResult) for res in results)

    def test_expand_grafo_vuoto(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.expand(["A"]) == []

    def test_expand_file_assente_lista_vuota(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        assert r.expand(["A"]) == []

    def test_expand_nodo_non_nel_grafo_lista_vuota(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.expand(["INESISTENTE"]) == []


# ---------------------------------------------------------------------------
# expand() — filtro vigenza
# ---------------------------------------------------------------------------

class TestExpandVigenza:

    def _graph_con_vigenza(self) -> nx.DiGraph:
        G: nx.DiGraph = nx.DiGraph()
        # Nodo vigente
        G.add_node("VIGENTE", **_article_node("VIGENTE", art_num="1",
                                               valid_from="20000101", valid_to="99999999"))
        # Nodo abrogato prima del 2024
        G.add_node("ABROGATO", **_article_node("ABROGATO", art_num="2",
                                                valid_from="19900101", valid_to="20221231"))
        # Nodo non ancora in vigore
        G.add_node("FUTURO", **_article_node("FUTURO", art_num="3",
                                              valid_from="20300101", valid_to="99999999"))
        G.add_edge("START", "VIGENTE", edge_type="RINVIA")
        G.add_edge("START", "ABROGATO", edge_type="RINVIA")
        G.add_edge("START", "FUTURO", edge_type="RINVIA")
        G.add_node("START", **_article_node("START", art_num="0"))
        return G

    def test_valid_on_esclude_nodo_abrogato(self, tmp_path):
        _save_graph(self._graph_con_vigenza(), tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["START"], depth=1, valid_on=date(2024, 1, 1))
        ids = {res.source_id for res in results}
        assert "ABROGATO" not in ids

    def test_valid_on_esclude_nodo_futuro(self, tmp_path):
        _save_graph(self._graph_con_vigenza(), tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["START"], depth=1, valid_on=date(2024, 1, 1))
        ids = {res.source_id for res in results}
        assert "FUTURO" not in ids

    def test_valid_on_include_nodo_vigente(self, tmp_path):
        _save_graph(self._graph_con_vigenza(), tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["START"], depth=1, valid_on=date(2024, 1, 1))
        ids = {res.source_id for res in results}
        assert "VIGENTE" in ids

    def test_senza_valid_on_include_tutti(self, tmp_path):
        _save_graph(self._graph_con_vigenza(), tmp_path)
        r = GraphRetriever(str(tmp_path))
        results = r.expand(["START"], depth=1)
        ids = {res.source_id for res in results}
        assert "VIGENTE" in ids
        assert "ABROGATO" in ids
        assert "FUTURO" in ids


# ---------------------------------------------------------------------------
# get_conflicts()
# ---------------------------------------------------------------------------

class TestGetConflicts:

    def test_trova_arco_contrasta(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("A", **_article_node("A", art_num="1"))
        G.add_node("B", **_article_node("B", art_num="2"))
        G.add_edge("A", "B", edge_type="CONTRASTA")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        conflicts = r.get_conflicts(["A", "B"])
        assert ("A", "B", "CONTRASTA") in conflicts

    def test_trova_arco_abroga(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("A", **_article_node("A", art_num="1"))
        G.add_node("B", **_article_node("B", art_num="2"))
        G.add_edge("A", "B", edge_type="ABROGA")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        conflicts = r.get_conflicts(["A", "B"])
        assert ("A", "B", "ABROGA") in conflicts

    def test_rinvia_non_e_conflitto(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.get_conflicts(["A", "B"]) == []

    def test_nessun_conflitto_lista_vuota(self, tmp_path):
        G = _make_graph([("A", "B", "RINVIA"), ("B", "C", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.get_conflicts(["A", "B", "C"]) == []

    def test_file_assente_lista_vuota(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        assert r.get_conflicts(["A"]) == []

    def test_solo_nodi_in_input_considerati(self, tmp_path):
        """Conflitti con nodi fuori dall'input non vengono restituiti."""
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("A", **_article_node("A", art_num="1"))
        G.add_node("B", **_article_node("B", art_num="2"))
        G.add_node("C", **_article_node("C", art_num="3"))
        G.add_edge("A", "C", edge_type="CONTRASTA")  # C non è nell'input
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        conflicts = r.get_conflicts(["A", "B"])  # C non incluso
        assert conflicts == []
