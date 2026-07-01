"""
Test QuestioneLoader — vedi
docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest
import yaml

from aiura_legal.core.graph.questione_loader import (
    QuestioneLoader,
    QuestioneRegistryError,
)


def _save_target_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(json.dumps(data), encoding="utf-8")


def _article(art_num: str, fonte: str = "codice_civile") -> dict:
    return {
        "node_type": "article",
        "fonte": fonte,
        "titolo": fonte,
        "articolo_num": art_num,
        "testo_tipo": "normativo",
        "valid_from": None,
        "valid_to": None,
    }


def _write_registry(tmp_path: Path, entries: list[dict]) -> Path:
    p = tmp_path / "questioni_curate.yaml"
    p.write_text(yaml.safe_dump(entries, allow_unicode=True), encoding="utf-8")
    return p


@pytest.fixture
def loader() -> QuestioneLoader:
    return QuestioneLoader()


class TestLoadCurated:

    def test_carica_voce_approvata(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {
                "id": "q1", "formulazione": "Domanda?", "materia": "civile",
                "parole_chiave": ["a", "b"], "norme_pertinenti": ["urn:1"],
                "decisioni_pertinenti": [], "stato": "approvato",
            },
        ])
        questioni = loader.load_curated(registry)
        assert len(questioni) == 1
        assert questioni[0].id == "q1"
        assert questioni[0].norme_pertinenti == ["urn:1"]

    def test_scarta_voce_non_approvata_per_default(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "formulazione": "Domanda?", "materia": "civile", "stato": "proposto"},
        ])
        assert loader.load_curated(registry) == []

    def test_only_approved_false_include_non_approvate(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "formulazione": "Domanda?", "materia": "civile", "stato": "proposto"},
        ])
        questioni = loader.load_curated(registry, only_approved=False)
        assert len(questioni) == 1

    def test_campo_obbligatorio_mancante_alza_errore(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "materia": "civile", "stato": "approvato"},  # manca formulazione
        ])
        with pytest.raises(QuestioneRegistryError):
            loader.load_curated(registry)

    def test_id_duplicato_alza_errore(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "formulazione": "A?", "materia": "civile", "stato": "approvato"},
            {"id": "q1", "formulazione": "B?", "materia": "civile", "stato": "approvato"},
        ])
        with pytest.raises(QuestioneRegistryError):
            loader.load_curated(registry)

    def test_registro_non_lista_alza_errore(self, loader, tmp_path):
        p = tmp_path / "bad.yaml"
        p.write_text(yaml.safe_dump({"non": "una lista"}), encoding="utf-8")
        with pytest.raises(QuestioneRegistryError):
            loader.load_curated(p)

    def test_stato_non_valido_alza_errore(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "formulazione": "D?", "materia": "civile", "stato": "boh"},
        ])
        with pytest.raises(QuestioneRegistryError):
            loader.load_curated(registry, only_approved=False)

    def test_stato_assente_default_proposto(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "formulazione": "D?", "materia": "civile"},
        ])
        questioni = loader.load_curated(registry, only_approved=False)
        assert questioni[0].stato == "proposto"

    def test_stato_rifiutato_escluso_da_only_approved(self, loader, tmp_path):
        registry = _write_registry(tmp_path, [
            {"id": "q1", "formulazione": "D?", "materia": "civile", "stato": "rifiutato"},
        ])
        assert loader.load_curated(registry) == []


class TestWriteToGraph:

    def test_scrive_nodo_e_arco_pertinente_a(self, loader, tmp_path):
        target = nx.DiGraph()
        target.add_node("urn:art1218", **_article("1218"))
        _save_target_graph(target, tmp_path)

        registry = _write_registry(tmp_path, [
            {
                "id": "q1", "formulazione": "Inadempimento?", "materia": "civile",
                "parole_chiave": ["inadempimento"], "norme_pertinenti": ["urn:art1218"],
                "decisioni_pertinenti": [], "stato": "approvato",
            },
        ])
        questioni = loader.load_curated(registry)
        stats = loader.write_to_graph(questioni, workspace_path=str(tmp_path))

        assert stats == {"questioni_scritte": 1, "archi_pertinente_a": 1, "archi_risolve": 0}

        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert G.nodes["q1"]["node_type"] == "questione"
        assert G.nodes["q1"]["formulazione"] == "Inadempimento?"
        assert G.has_edge("urn:art1218", "q1")
        assert G.edges["urn:art1218", "q1"]["edge_type"] == "PERTINENTE_A"

    def test_scrive_arco_risolve_per_decisione(self, loader, tmp_path):
        target = nx.DiGraph()
        target.add_node("sentenza:123", node_type="sentenza", organo="cassazione")
        _save_target_graph(target, tmp_path)

        registry = _write_registry(tmp_path, [
            {
                "id": "q1", "formulazione": "D?", "materia": "civile",
                "norme_pertinenti": [], "decisioni_pertinenti": ["sentenza:123"],
                "stato": "approvato",
            },
        ])
        questioni = loader.load_curated(registry)
        stats = loader.write_to_graph(questioni, workspace_path=str(tmp_path))

        assert stats["archi_risolve"] == 1
        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert G.edges["sentenza:123", "q1"]["edge_type"] == "RISOLVE"

    def test_riferimento_inesistente_alza_errore_e_non_scrive(self, loader, tmp_path):
        target = nx.DiGraph()
        target.add_node("urn:art1218", **_article("1218"))
        _save_target_graph(target, tmp_path)

        registry = _write_registry(tmp_path, [
            {
                "id": "q1", "formulazione": "D?", "materia": "civile",
                "norme_pertinenti": ["urn:art_non_esiste"], "stato": "approvato",
            },
        ])
        questioni = loader.load_curated(registry)
        with pytest.raises(QuestioneRegistryError):
            loader.write_to_graph(questioni, workspace_path=str(tmp_path))

        # Il grafo su disco non deve essere stato toccato dal fallimento parziale
        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert "q1" not in G.nodes

    def test_idempotente_rerun_non_duplica(self, loader, tmp_path):
        target = nx.DiGraph()
        target.add_node("urn:art1218", **_article("1218"))
        _save_target_graph(target, tmp_path)

        registry = _write_registry(tmp_path, [
            {
                "id": "q1", "formulazione": "D?", "materia": "civile",
                "norme_pertinenti": ["urn:art1218"], "stato": "approvato",
            },
        ])
        questioni = loader.load_curated(registry)
        loader.write_to_graph(questioni, workspace_path=str(tmp_path))
        loader.write_to_graph(questioni, workspace_path=str(tmp_path))

        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert G.number_of_nodes() == 2  # urn:art1218 + q1, non triplicato
        assert G.number_of_edges() == 1  # un solo arco PERTINENTE_A, non duplicato
