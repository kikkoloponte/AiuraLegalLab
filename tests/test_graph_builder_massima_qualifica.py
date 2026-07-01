"""
Test LegalGraphBuilder.add_massima_batch / add_qualifica — vedi
docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest

from aiura_legal.core.graph.builder import LegalGraphBuilder


def _save_target_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(json.dumps(data), encoding="utf-8")


def _load_graph(workspace: Path) -> nx.DiGraph:
    data = json.loads((workspace / "indices" / "graph.json").read_text(encoding="utf-8"))
    return nx.node_link_graph(data, edges="edges")


@pytest.fixture
def builder() -> LegalGraphBuilder:
    return LegalGraphBuilder()


class TestAddMassimaBatch:

    def test_sentenza_presente_crea_nodo_e_arco(self, builder, tmp_path):
        target = nx.DiGraph()
        target.add_node("sentenza:123", node_type="sentenza", organo="cassazione")
        _save_target_graph(target, tmp_path)

        stats = builder.add_massima_batch(
            [{"sentenza_id": "sentenza:123", "massima_id": "massima:1", "testo": "Testo massima."}],
            str(tmp_path),
        )

        assert stats == {"nodi_massima": 1, "archi_sintetizza": 1, "archi_saltati_sentenza_assente": 0}
        G = _load_graph(tmp_path)
        assert G.nodes["massima:1"]["node_type"] == "massima"
        assert G.nodes["massima:1"]["corpus"] == "massimario"
        assert G.has_edge("sentenza:123", "massima:1")
        assert G.edges["sentenza:123", "massima:1"]["edge_type"] == "SINTETIZZA"

    def test_sentenza_assente_crea_solo_nodo_massima(self, builder, tmp_path):
        target = nx.DiGraph()
        _save_target_graph(target, tmp_path)

        stats = builder.add_massima_batch(
            [{"sentenza_id": "sentenza:non_esiste", "massima_id": "massima:1"}],
            str(tmp_path),
        )

        assert stats["nodi_massima"] == 1
        assert stats["archi_sintetizza"] == 0
        assert stats["archi_saltati_sentenza_assente"] == 1
        G = _load_graph(tmp_path)
        assert "massima:1" in G.nodes
        assert not G.has_edge("sentenza:non_esiste", "massima:1")

    def test_senza_massima_id_viene_ignorata(self, builder, tmp_path):
        target = nx.DiGraph()
        _save_target_graph(target, tmp_path)

        stats = builder.add_massima_batch([{"sentenza_id": "sentenza:123"}], str(tmp_path))

        assert stats == {"nodi_massima": 0, "archi_sintetizza": 0, "archi_saltati_sentenza_assente": 0}

    def test_idempotente_rerun_non_duplica(self, builder, tmp_path):
        target = nx.DiGraph()
        target.add_node("sentenza:123", node_type="sentenza")
        _save_target_graph(target, tmp_path)

        massime = [{"sentenza_id": "sentenza:123", "massima_id": "massima:1", "testo": "T"}]
        builder.add_massima_batch(massime, str(tmp_path))
        builder.add_massima_batch(massime, str(tmp_path))

        G = _load_graph(tmp_path)
        assert G.number_of_nodes() == 2  # sentenza:123 + massima:1
        assert G.number_of_edges() == 1


class TestAddQualifica:

    def test_entrambi_i_nodi_presenti_crea_arco(self, builder, tmp_path):
        target = nx.DiGraph()
        target.add_node("sentenza:123", node_type="sentenza")
        target.add_node("urn:art1453", node_type="article", articolo_num="1453")
        _save_target_graph(target, tmp_path)

        ok = builder.add_qualifica("sentenza:123", "urn:art1453", str(tmp_path))

        assert ok is True
        G = _load_graph(tmp_path)
        assert G.has_edge("sentenza:123", "urn:art1453")
        assert G.edges["sentenza:123", "urn:art1453"]["edge_type"] == "QUALIFICA"

    def test_nodo_assente_ritorna_false_senza_eccezione(self, builder, tmp_path):
        target = nx.DiGraph()
        target.add_node("sentenza:123", node_type="sentenza")
        _save_target_graph(target, tmp_path)

        ok = builder.add_qualifica("sentenza:123", "urn:non_esiste", str(tmp_path))

        assert ok is False
        G = _load_graph(tmp_path)
        assert not G.has_edge("sentenza:123", "urn:non_esiste")

    def test_idempotente_rerun_non_duplica(self, builder, tmp_path):
        target = nx.DiGraph()
        target.add_node("sentenza:123", node_type="sentenza")
        target.add_node("urn:art1453", node_type="article")
        _save_target_graph(target, tmp_path)

        builder.add_qualifica("sentenza:123", "urn:art1453", str(tmp_path))
        builder.add_qualifica("sentenza:123", "urn:art1453", str(tmp_path))

        G = _load_graph(tmp_path)
        assert G.number_of_edges() == 1
