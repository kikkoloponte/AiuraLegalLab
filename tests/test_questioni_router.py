"""
Test questioni_router — TestClient isolato (FastAPI minimale, niente app.py
completa: questo router non dipende da MongoDB/orchestratore, monta solo
QuestioniRegistry e GraphRetriever puntati su tmp_path).
"""
from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest
import yaml
from fastapi import FastAPI
from fastapi.testclient import TestClient

import aiura_legal.api.questioni_router as questioni_router_module
from aiura_legal.api.questioni_router import router
from aiura_legal.core.graph.questioni_registry import QuestioniRegistry
from aiura_legal.core.graph.retriever import GraphRetriever


def _write_registry(path: Path, entries: list[dict]) -> None:
    path.write_text(yaml.safe_dump(entries, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _save_target_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def workspace(tmp_path) -> Path:
    ws = tmp_path / "ws"
    G = nx.DiGraph()
    G.add_node("urn:art1218", node_type="article", fonte="codice_civile", titolo="C.C.", articolo_num="1218")
    _save_target_graph(G, ws)
    return ws


@pytest.fixture
def registry_path(tmp_path) -> Path:
    p = tmp_path / "questioni_curate.yaml"
    _write_registry(p, [
        {
            "id": "q1", "formulazione": "Domanda uno?", "materia": "civile",
            "norme_pertinenti": [], "decisioni_pertinenti": [], "stato": "proposto",
        },
        {"id": "q2", "formulazione": "Domanda due?", "materia": "penale", "stato": "approvato"},
    ])
    return p


@pytest.fixture
def client(registry_path, workspace, monkeypatch):
    monkeypatch.setenv("AIURA_GRAPH_BACKEND", "networkx")
    monkeypatch.setattr(
        questioni_router_module, "_registry",
        QuestioniRegistry(path=registry_path, workspace_path=str(workspace)),
    )
    monkeypatch.setattr(questioni_router_module, "_graph", GraphRetriever(str(workspace)))

    app = FastAPI()
    app.include_router(router, prefix="/questioni")
    return TestClient(app)


class TestListQuestioni:

    def test_lista_tutte(self, client):
        resp = client.get("/questioni")
        assert resp.status_code == 200
        body = resp.json()
        ids = {item["id"] for item in body["items"]}
        assert ids == {"q1", "q2"}
        assert body["version"]

    def test_filtro_stato(self, client):
        resp = client.get("/questioni", params={"stato": "approvato"})
        assert resp.status_code == 200
        ids = [item["id"] for item in resp.json()["items"]]
        assert ids == ["q2"]


class TestGetQuestione:

    def test_trova_voce(self, client):
        resp = client.get("/questioni/q1")
        assert resp.status_code == 200
        body = resp.json()
        assert body["questione"]["formulazione"] == "Domanda uno?"
        assert body["version"]

    def test_404_su_id_inesistente(self, client):
        resp = client.get("/questioni/non_esiste")
        assert resp.status_code == 404


class TestUpdateQuestione:

    def test_approva(self, client):
        get_resp = client.get("/questioni/q1")
        version = get_resp.json()["version"]

        put_resp = client.put("/questioni/q1", json={
            "changes": {"stato": "approvato"}, "expected_version": version,
        })
        assert put_resp.status_code == 200
        assert put_resp.json()["questione"]["stato"] == "approvato"

    def test_409_su_versione_obsoleta(self, client):
        get_resp = client.get("/questioni/q1")
        version = get_resp.json()["version"]

        client.put("/questioni/q1", json={"changes": {"formulazione": "Prima"}, "expected_version": version})
        stale_resp = client.put("/questioni/q1", json={
            "changes": {"formulazione": "Seconda"}, "expected_version": version,
        })
        assert stale_resp.status_code == 409

    def test_404_su_id_inesistente(self, client):
        resp = client.put("/questioni/non_esiste", json={
            "changes": {"stato": "approvato"}, "expected_version": "qualunque",
        })
        assert resp.status_code == 404

    def test_400_su_id_norma_inesistente_nel_grafo(self, client):
        get_resp = client.get("/questioni/q1")
        version = get_resp.json()["version"]

        resp = client.put("/questioni/q1", json={
            "changes": {"norme_pertinenti": ["urn:non_esiste"]}, "expected_version": version,
        })
        assert resp.status_code == 400

    def test_200_su_id_norma_valido(self, client):
        get_resp = client.get("/questioni/q1")
        version = get_resp.json()["version"]

        resp = client.put("/questioni/q1", json={
            "changes": {"norme_pertinenti": ["urn:art1218"]}, "expected_version": version,
        })
        assert resp.status_code == 200
        assert resp.json()["questione"]["norme_pertinenti"] == ["urn:art1218"]


class TestSearchNodes:

    def test_trova_articolo(self, client):
        resp = client.get("/questioni/search-nodes", params={"q": "1218", "node_type": "article"})
        assert resp.status_code == 200
        ids = [r["id"] for r in resp.json()["results"]]
        assert ids == ["urn:art1218"]

    def test_query_troppo_corta_422(self, client):
        resp = client.get("/questioni/search-nodes", params={"q": "a", "node_type": "article"})
        assert resp.status_code == 422

    def test_node_type_non_valido_422(self, client):
        resp = client.get("/questioni/search-nodes", params={"q": "1218", "node_type": "altro"})
        assert resp.status_code == 422
