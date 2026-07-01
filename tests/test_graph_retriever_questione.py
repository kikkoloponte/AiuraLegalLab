"""
Test GraphRetriever.match_questione / expand_from_questione / is_abrogated /
has_anchor — vedi docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import networkx as nx
import pytest

from aiura_legal.core.graph.retriever import GraphRetriever


def _save_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(json.dumps(data), encoding="utf-8")


def _article_node(
    fonte: str = "codice_civile",
    art_num: str = "1218",
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
    monkeypatch.setenv("AIURA_GRAPH_BACKEND", "networkx")


class TestMatchQuestione:

    def test_match_sopra_soglia(self, tmp_path):
        G = nx.DiGraph()
        G.add_node(
            "q1", node_type="questione",
            formulazione="Quando l'inadempimento genera responsabilità contrattuale?",
            materia="civile", parole_chiave=["inadempimento", "responsabilità contrattuale"],
        )
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        result = r.match_questione("responsabilità contrattuale per inadempimento", threshold=0.5)
        assert result == "q1"

    def test_nessun_match_sotto_soglia(self, tmp_path):
        G = nx.DiGraph()
        G.add_node(
            "q1", node_type="questione",
            formulazione="Silenzio della PA equivale ad accoglimento tacito?",
            materia="amministrativo", parole_chiave=["silenzio-assenso"],
        )
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        result = r.match_questione("ricetta della carbonara", threshold=0.9)
        assert result is None

    def test_grafo_assente_ritorna_none(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        assert r.match_questione("qualunque cosa") is None

    def test_query_vuota_ritorna_none(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("q1", node_type="questione", formulazione="x", parole_chiave=[])
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.match_questione("") is None


class TestExpandFromQuestione:

    def test_segue_pertinente_a_e_risolve(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1218", **_article_node())
        G.add_node("sentenza:1", node_type="sentenza", organo="cassazione", numero="123", anno="2024")
        G.add_node("q1", node_type="questione", formulazione="x", materia="civile", parole_chiave=[])
        G.add_edge("urn:art1218", "q1", edge_type="PERTINENTE_A")
        G.add_edge("sentenza:1", "q1", edge_type="RISOLVE")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.expand_from_questione("q1")
        ids = {res.source_id for res in results}
        assert ids == {"urn:art1218", "sentenza:1"}
        assert all(res.retrieval_method == "questione_expansion" for res in results)

    def test_questione_inesistente_ritorna_vuoto(self, tmp_path):
        G = nx.DiGraph()
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.expand_from_questione("q_non_esiste") == []

    def test_filtro_vigenza_esclude_articolo_abrogato(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art_abrogato", **_article_node(valid_to="20100101"))
        G.add_node("q1", node_type="questione", formulazione="x", parole_chiave=[])
        G.add_edge("urn:art_abrogato", "q1", edge_type="PERTINENTE_A")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.expand_from_questione("q1", valid_on=date(2024, 1, 1))
        assert results == []

    def test_max_nodes_limita_output(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("q1", node_type="questione", formulazione="x", parole_chiave=[])
        for i in range(5):
            G.add_node(f"urn:art{i}", **_article_node(art_num=str(i)))
            G.add_edge(f"urn:art{i}", "q1", edge_type="PERTINENTE_A")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.expand_from_questione("q1", max_nodes=2)
        assert len(results) == 2


class TestIsAbrogated:

    def test_norma_vigente_ritorna_false(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node(valid_to="99999999"))
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.is_abrogated("urn:art1", date(2026, 1, 1)) is False

    def test_norma_abrogata_ritorna_true(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node(valid_to="20100101"))
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.is_abrogated("urn:art1", date(2026, 1, 1)) is True

    def test_nodo_assente_ritorna_false(self, tmp_path):
        G = nx.DiGraph()
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.is_abrogated("urn:non_esiste", date(2026, 1, 1)) is False

    def test_nodo_non_articolo_ritorna_false(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("sentenza:1", node_type="sentenza")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.is_abrogated("sentenza:1", date(2026, 1, 1)) is False


class TestHasAnchor:

    def test_principio_con_ancora_ritorna_true(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("principio:buona_fede", node_type="principio")
        G.add_node("urn:art1218", **_article_node())
        G.add_edge("principio:buona_fede", "urn:art1218", edge_type="ANCORATA_A")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.has_anchor("principio:buona_fede") is True

    def test_principio_senza_ancora_ritorna_false(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("principio:fluttuante", node_type="principio")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.has_anchor("principio:fluttuante") is False

    def test_nodo_assente_ritorna_false(self, tmp_path):
        G = nx.DiGraph()
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.has_anchor("principio:non_esiste") is False


class TestSearchNodes:

    def test_trova_articolo_per_articolo_num(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1218", **_article_node(art_num="1218"))
        G.add_node("urn:art2043", **_article_node(art_num="2043"))
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.search_nodes("1218", node_type="article")
        assert [res["id"] for res in results] == ["urn:art1218"]

    def test_trova_articolo_per_fonte(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node(fonte="codice_civile", art_num="1"))
        G.add_node("urn:art2", **_article_node(fonte="codice_penale", art_num="2"))
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.search_nodes("codice_penale", node_type="article")
        assert [res["id"] for res in results] == ["urn:art2"]

    def test_trova_sentenza_per_numero(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("sentenza:1", node_type="sentenza", organo="cassazione", numero="123", anno="2024")
        G.add_node("sentenza:2", node_type="sentenza", organo="cassazione", numero="456", anno="2023")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.search_nodes("123", node_type="sentenza")
        assert [res["id"] for res in results] == ["sentenza:1"]
        assert results[0]["label"] == "cassazione n.123/2024"

    def test_case_insensitive(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node(fonte="Codice_Civile", art_num="1"))
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.search_nodes("codice_civile", node_type="article")
        assert len(results) == 1

    def test_nessun_match_ritorna_vuoto(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node())
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        assert r.search_nodes("nessuna corrispondenza qui", node_type="article") == []

    def test_limit_rispettato(self, tmp_path):
        G = nx.DiGraph()
        for i in range(5):
            G.add_node(f"urn:art{i}", **_article_node(art_num=f"{i}00"))
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        assert len(r.search_nodes("00", node_type="article", limit=2)) == 2

    def test_grafo_assente_ritorna_vuoto(self, tmp_path):
        r = GraphRetriever(str(tmp_path))
        assert r.search_nodes("qualunque", node_type="article") == []

    def test_query_vuota_ritorna_vuoto(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node())
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))
        assert r.search_nodes("", node_type="article") == []

    def test_node_type_diverso_non_incluso(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("urn:art1", **_article_node(art_num="999"))
        G.add_node("sentenza:1", node_type="sentenza", organo="cassazione", numero="999", anno="2024")
        _save_graph(G, tmp_path)
        r = GraphRetriever(str(tmp_path))

        results = r.search_nodes("999", node_type="article")
        assert [res["id"] for res in results] == ["urn:art1"]
