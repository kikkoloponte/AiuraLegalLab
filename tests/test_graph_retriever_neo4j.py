"""
Test backend Neo4j di GraphRetriever — Fase C del piano migrazione (POC).

Richiedono il container docker-compose.neo4j.yml attivo con i dati reali
caricati (scripts/migrate_graph_to_neo4j.py). Marcati 'integration': esclusi
di default (pyproject.toml: addopts = "-m \"not integration\""), eseguire con:

    pytest -m integration tests/test_graph_retriever_neo4j.py -v
"""
from __future__ import annotations

import pytest

from aiura_legal.core.graph.retriever import GraphBackendSettings, GraphRetriever


@pytest.fixture
def neo4j_retriever():
    settings = GraphBackendSettings(aiura_graph_backend="neo4j")
    retriever = GraphRetriever("workspaces/mio-studio", settings=settings)
    if not retriever.is_available:
        pytest.skip("Neo4j non raggiungibile — avvia docker-compose.neo4j.yml")
    return retriever


@pytest.mark.integration
class TestNeo4jBackend:

    def test_is_available(self, neo4j_retriever):
        assert neo4j_retriever.is_available

    def test_get_health_conteggi_coerenti_con_migrazione(self, neo4j_retriever):
        health = neo4j_retriever.get_health()
        assert health.available
        assert health.backend == "neo4j"
        assert health.node_count == 307325
        assert health.edge_count == 666291

    def test_expand_trova_sentenza_collegata(self, neo4j_retriever):
        results = neo4j_retriever.expand(
            ["urn:nir:stato:regio.decreto:1942-03-16;262~art2119"],
            depth=1, max_nodes=5,
        )
        assert len(results) >= 1
        assert all(r.retrieval_method == "graph_expansion" for r in results)
        assert any(r.source_layer == "giurisprudenza" for r in results)

    def test_expand_source_id_assente_ritorna_vuoto(self, neo4j_retriever):
        results = neo4j_retriever.expand(["urn:nir:non:esiste:art1"], depth=1)
        assert results == []

    def test_expand_lista_vuota_ritorna_vuoto(self, neo4j_retriever):
        assert neo4j_retriever.expand([]) == []

    def test_get_conflicts_nessun_conflitto_ritorna_vuoto(self, neo4j_retriever):
        # Non ci sono archi CONTRASTA nei dati reali migrati (verificato in Fase C)
        conflicts = neo4j_retriever.get_conflicts(
            ["urn:nir:stato:regio.decreto:1942-03-16;262~art2119"]
        )
        assert conflicts == []


@pytest.mark.integration
def test_unreachable_neo4j_graceful_degradation():
    """Se Neo4j non risponde (porta sbagliata), is_available=False senza eccezioni."""
    settings = GraphBackendSettings(aiura_graph_backend="neo4j", neo4j_uri="bolt://localhost:19999")
    retriever = GraphRetriever("workspaces/mio-studio", settings=settings)
    assert retriever.is_available is False
    assert retriever.expand(["x"]) == []
    assert retriever.get_conflicts(["x"]) == []
    assert retriever.get_health().available is False
