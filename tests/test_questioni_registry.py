"""
Test QuestioniRegistry — vedi
docs/superpowers/specs/2026-06-26-questioni-review-ui-design.md.
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest
import yaml

from aiura_legal.core.graph.questione_loader import QuestioneRegistryError
from aiura_legal.core.graph.questioni_registry import (
    QuestioneNotFoundError,
    QuestioniRegistry,
    VersionConflictError,
)


def _write_registry(path: Path, entries: list[dict]) -> None:
    path.write_text(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _save_target_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def registry_path(tmp_path) -> Path:
    p = tmp_path / "questioni_curate.yaml"
    _write_registry(p, [
        {
            "id": "q1", "formulazione": "Domanda uno?", "materia": "civile",
            "parole_chiave": ["a"], "norme_pertinenti": [], "decisioni_pertinenti": [],
            "stato": "proposto",
        },
        {
            "id": "q2", "formulazione": "Domanda due?", "materia": "penale",
            "stato": "approvato",
        },
    ])
    return p


@pytest.fixture
def registry(registry_path, tmp_path) -> QuestioniRegistry:
    return QuestioniRegistry(path=registry_path, workspace_path=str(tmp_path / "ws"))


class TestList:

    def test_lista_tutte_le_voci(self, registry):
        questioni = registry.list()
        assert {q.id for q in questioni} == {"q1", "q2"}

    def test_filtro_per_stato(self, registry):
        questioni = registry.list(stato="approvato")
        assert [q.id for q in questioni] == ["q2"]

    def test_file_assente_ritorna_lista_vuota(self, tmp_path):
        r = QuestioniRegistry(path=tmp_path / "non_esiste.yaml")
        assert r.list() == []


class TestCurrentVersion:

    def test_coincide_con_versione_da_get(self, registry):
        _, version = registry.get("q1")
        assert registry.current_version() == version

    def test_cambia_dopo_update(self, registry):
        v1 = registry.current_version()
        registry.update("q1", {"formulazione": "Nuova"}, v1)
        v2 = registry.current_version()
        assert v1 != v2

    def test_file_assente_ritorna_stringa_vuota(self, tmp_path):
        r = QuestioniRegistry(path=tmp_path / "non_esiste.yaml")
        assert r.current_version() == ""


class TestGet:

    def test_trova_voce_esistente(self, registry):
        q, version = registry.get("q1")
        assert q.formulazione == "Domanda uno?"
        assert isinstance(version, str) and len(version) > 0

    def test_id_inesistente_alza_errore(self, registry):
        with pytest.raises(QuestioneNotFoundError):
            registry.get("non_esiste")


class TestUpdate:

    def test_aggiorna_formulazione(self, registry):
        _, version = registry.get("q1")
        questione, new_version = registry.update("q1", {"formulazione": "Nuova domanda?"}, version)

        assert questione.formulazione == "Nuova domanda?"
        assert new_version != version
        q_reletta, _ = registry.get("q1")
        assert q_reletta.formulazione == "Nuova domanda?"

    def test_approva_voce(self, registry):
        _, version = registry.get("q1")
        questione, _ = registry.update("q1", {"stato": "approvato"}, version)
        assert questione.stato == "approvato"

    def test_rifiuta_voce_resta_nel_registro(self, registry):
        _, version = registry.get("q1")
        registry.update("q1", {"stato": "rifiutato"}, version)

        questioni = registry.list()
        assert any(q.id == "q1" and q.stato == "rifiutato" for q in questioni)

    def test_versione_obsoleta_alza_conflitto_e_non_scrive(self, registry):
        _, version = registry.get("q1")
        registry.update("q1", {"formulazione": "Prima modifica"}, version)

        with pytest.raises(VersionConflictError):
            registry.update("q1", {"formulazione": "Seconda modifica (stale)"}, version)

        q, _ = registry.get("q1")
        assert q.formulazione == "Prima modifica"

    def test_id_inesistente_alza_errore(self, registry):
        _, version = registry.get("q1")
        with pytest.raises(QuestioneNotFoundError):
            registry.update("id_fantasma", {"formulazione": "x"}, version)

    def test_campo_non_modificabile_alza_errore(self, registry):
        _, version = registry.get("q1")
        with pytest.raises(QuestioneRegistryError):
            registry.update("q1", {"id": "nuovo_id"}, version)

    def test_stato_non_valido_alza_errore(self, registry):
        _, version = registry.get("q1")
        with pytest.raises(QuestioneRegistryError):
            registry.update("q1", {"stato": "boh"}, version)

    def test_norme_pertinenti_con_id_inesistente_nel_grafo_alza_errore(self, registry, tmp_path):
        target = nx.DiGraph()
        _save_target_graph(target, tmp_path / "ws")

        _, version = registry.get("q1")
        with pytest.raises(QuestioneRegistryError):
            registry.update("q1", {"norme_pertinenti": ["urn:non_esiste"]}, version)

    def test_norme_pertinenti_con_id_valido_aggiorna(self, registry, tmp_path):
        target = nx.DiGraph()
        target.add_node("urn:art1218", node_type="article", fonte="codice_civile", articolo_num="1218")
        _save_target_graph(target, tmp_path / "ws")

        _, version = registry.get("q1")
        questione, _ = registry.update("q1", {"norme_pertinenti": ["urn:art1218"]}, version)
        assert questione.norme_pertinenti == ["urn:art1218"]

    def test_grafo_assente_non_blocca_update(self, registry):
        """Se il grafo non esiste ancora, l'update procede comunque (warning, non errore) —
        la validazione referenziale piena avviene comunque al momento di write_to_graph."""
        _, version = registry.get("q1")
        questione, _ = registry.update("q1", {"norme_pertinenti": ["urn:qualunque"]}, version)
        assert questione.norme_pertinenti == ["urn:qualunque"]
