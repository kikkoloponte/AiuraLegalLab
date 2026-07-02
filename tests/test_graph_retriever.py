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


@pytest.fixture(autouse=True)
def _force_networkx_backend(monkeypatch):
    """
    Questi test costruiscono grafi ad-hoc in tmp_path e verificano il
    comportamento del backend NetworkX. Devono restare isolati dalla
    configurazione di ambiente (.env): AIURA_GRAPH_BACKEND=neo4j in
    produzione punterebbe altrimenti tutti questi test al Neo4j reale,
    ignorando silenziosamente i grafi di test in tmp_path.
    """
    monkeypatch.setenv("AIURA_GRAPH_BACKEND", "networkx")


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


class TestGraphHealth:
    """Guardrail di staleness — vedi GraphHealthSettings in retriever.py."""

    def test_file_assente_available_false(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        h = r.get_health()
        assert h.available is False
        assert h.is_stale is False

    def test_built_at_assente_e_stale(self, tmp_path):
        """Grafo salvato senza built_at (legacy, pre-guardrail) → stale."""
        G = _make_graph([("A", "B", "RINVIA")])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        h = r.get_health()
        assert h.available is True
        assert h.is_stale is True
        assert any("built_at assente" in reason for reason in h.stale_reasons)

    def test_built_at_recente_non_stale(self, tmp_path):
        from datetime import datetime, timezone
        G = _make_graph([("A", "B", "RINVIA")])
        G.graph["built_at"] = datetime.now(timezone.utc).isoformat()
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        h = r.get_health()
        assert h.is_stale is False
        assert h.age_hours is not None
        assert h.age_hours < 1.0

    def test_built_at_vecchio_supera_soglia_age(self, tmp_path, monkeypatch):
        from datetime import datetime, timedelta, timezone
        monkeypatch.setenv("GRAPH_MAX_AGE_HOURS", "1")
        G = _make_graph([("A", "B", "RINVIA")])
        old = datetime.now(timezone.utc) - timedelta(hours=10)
        G.graph["built_at"] = old.isoformat()
        _save_graph(G, tmp_path)

        # Le settings sono lette a import-time: ricreo l'istanza con le env aggiornate
        import aiura_legal.core.graph.retriever as retriever_module
        monkeypatch.setattr(
            retriever_module, "_health_settings", retriever_module.GraphHealthSettings()
        )

        r = GraphRetriever(str(tmp_path))
        h = r.get_health()
        assert h.is_stale is True
        assert any("age=" in reason for reason in h.stale_reasons)

    def test_size_oltre_soglia(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GRAPH_MAX_SIZE_MB", "0.0001")
        import aiura_legal.core.graph.retriever as retriever_module
        monkeypatch.setattr(
            retriever_module, "_health_settings", retriever_module.GraphHealthSettings()
        )

        from datetime import datetime, timezone
        G = _make_graph([("A", "B", "RINVIA")])
        G.graph["built_at"] = datetime.now(timezone.utc).isoformat()
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        h = r.get_health()
        assert h.is_stale is True
        assert any("size=" in reason for reason in h.stale_reasons)


# ---------------------------------------------------------------------------
# expand() — nodi sentenza via INTERPRETA/APPLICATA_IN (merge_jurisprudence_graph)
# ---------------------------------------------------------------------------

def _sentenza_node(node_id: str, organo: str = "cassazione", numero: str = "123", anno: str = "2021") -> dict:
    return {
        "node_type": "sentenza",
        "organo": organo,
        "numero": numero,
        "anno": anno,
        "materia": "",
    }


class TestExpandSentenza:

    def test_da_norma_trova_sentenza_via_applicata_in(self, tmp_path):
        """Da un articolo recuperato, expand() trova la sentenza che lo interpreta."""
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("urn:nir:art2119", **_article_node("urn:nir:art2119", art_num="2119"))
        G.add_node("a1b2c3d4e5f60718", **_sentenza_node("a1b2c3d4e5f60718"))
        G.add_edge("a1b2c3d4e5f60718", "urn:nir:art2119", edge_type="INTERPRETA")
        G.add_edge("urn:nir:art2119", "a1b2c3d4e5f60718", edge_type="APPLICATA_IN")
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        results = r.expand(["urn:nir:art2119"])

        assert len(results) == 1
        assert results[0].source_id == "a1b2c3d4e5f60718"
        assert results[0].source_layer == "giurisprudenza"
        assert results[0].metadata["organo"] == "cassazione"

    def test_da_sentenza_trova_norma_via_interpreta(self, tmp_path):
        """Da una sentenza recuperata, expand() trova la norma che interpreta."""
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("urn:nir:art2119", **_article_node("urn:nir:art2119", art_num="2119"))
        G.add_node("a1b2c3d4e5f60718", **_sentenza_node("a1b2c3d4e5f60718"))
        G.add_edge("a1b2c3d4e5f60718", "urn:nir:art2119", edge_type="INTERPRETA")
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        results = r.expand(["a1b2c3d4e5f60718"])

        assert len(results) == 1
        assert results[0].source_id == "urn:nir:art2119"
        assert results[0].source_layer == "normativa"

    def test_sentenza_non_filtrata_da_valid_on(self, tmp_path):
        """Le sentenze non hanno valid_from/to: valid_on non le esclude mai."""
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("urn:nir:art2119", **_article_node("urn:nir:art2119", art_num="2119"))
        G.add_node("a1b2c3d4e5f60718", **_sentenza_node("a1b2c3d4e5f60718"))
        G.add_edge("urn:nir:art2119", "a1b2c3d4e5f60718", edge_type="APPLICATA_IN")
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        results = r.expand(["urn:nir:art2119"], valid_on=date(2024, 1, 1))

        assert len(results) == 1
        assert results[0].source_id == "a1b2c3d4e5f60718"


# ---------------------------------------------------------------------------
# resolve_labels() — chip leggibili per la UI di revisione questioni
# ---------------------------------------------------------------------------

class TestResolveLabels:

    def test_risolve_articolo(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("urn:art1218", **_article_node("urn:art1218", art_num="1218"))
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        labels = r.resolve_labels(["urn:art1218"])

        assert labels == {"urn:art1218": "Codice Civile 1218"}

    def test_risolve_sentenza(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("a1b2c3d4e5f60718", **_sentenza_node("a1b2c3d4e5f60718", organo="cassazione", numero="123", anno="2021"))
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        labels = r.resolve_labels(["a1b2c3d4e5f60718"])

        assert labels == {"a1b2c3d4e5f60718": "cassazione n.123/2021"}

    def test_id_inesistente_omesso(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("urn:art1218", **_article_node("urn:art1218", art_num="1218"))
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        labels = r.resolve_labels(["urn:art1218", "urn:non_esiste"])

        assert labels == {"urn:art1218": "Codice Civile 1218"}

    def test_lista_vuota_ritorna_vuoto(self, tmp_path):
        G: nx.DiGraph = nx.DiGraph()
        G.add_node("urn:art1218", **_article_node("urn:art1218", art_num="1218"))
        _save_graph(G, tmp_path)

        r = GraphRetriever(str(tmp_path))
        assert r.resolve_labels([]) == {}

    def test_grafo_assente_ritorna_vuoto(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        assert r.resolve_labels(["urn:qualsiasi"]) == {}
