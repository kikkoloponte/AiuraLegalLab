"""
Test di parità — Fase D del piano migrazione Neo4j (POC).

Verificano che i due backend di GraphRetriever (networkx, neo4j), interrogati
sullo stesso grafo reale (mio-studio, migrato con scripts/migrate_graph_to_neo4j.py),
restituiscano risultati equivalenti per le stesse query. Senza questa parità,
un rollout in produzione rischierebbe regressioni silenziose nel retrieval.

Richiedono: workspaces/mio-studio/indices/graph.json + Neo4j con gli stessi
dati migrati (docker-compose.neo4j.yml). Marcati 'integration'.
"""
from __future__ import annotations

import time

import pytest

from aiura_legal.core.graph.retriever import GraphBackendSettings, GraphRetriever

# Articoli reali con un numero piccolo e noto di sentenze collegate (vedi
# Fase D: query diretta su Neo4j per trovarli, evita di dipendere da nodi
# con migliaia di connessioni dove l'ordine di troncamento può differire).
_LOW_DEGREE_URNS = [
    "urn:nir:stato:regio.decreto:1942-03-16;262~art2424",
    "urn:nir:stato:regio.decreto:1942-03-16;262~art2929",
    "urn:nir:stato:regio.decreto:1942-03-16;262~art1172",
    "urn:nir:stato:regio.decreto:1940-10-28;1443~art360",
]

# Articolo con grado molto alto (>30k sentenze collegate) — qui non testiamo
# l'uguaglianza esatta dei risultati (il troncamento a max_nodes può scegliere
# candidati diversi tra i due backend), solo che entrambi rispettino il limite
# e restituiscano risultati con la stessa "forma" (stesso source_layer atteso).
_HIGH_DEGREE_URN = "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art635"


@pytest.fixture
def networkx_retriever():
    settings = GraphBackendSettings(aiura_graph_backend="networkx")
    retriever = GraphRetriever("workspaces/mio-studio", settings=settings)
    if not retriever.is_available:
        pytest.skip("workspaces/mio-studio/indices/graph.json non trovato")
    return retriever


@pytest.fixture
def neo4j_retriever():
    settings = GraphBackendSettings(aiura_graph_backend="neo4j")
    retriever = GraphRetriever("workspaces/mio-studio", settings=settings)
    if not retriever.is_available:
        pytest.skip("Neo4j non raggiungibile — avvia docker-compose.neo4j.yml")
    return retriever


@pytest.mark.integration
class TestParitaExpand:

    @pytest.mark.parametrize("urn", _LOW_DEGREE_URNS)
    def test_stesso_insieme_di_source_id(self, networkx_retriever, neo4j_retriever, urn):
        """Su nodi a basso grado, i due backend devono trovare esattamente gli stessi vicini."""
        nx_results = networkx_retriever.expand([urn], depth=1, max_nodes=20)
        neo_results = neo4j_retriever.expand([urn], depth=1, max_nodes=20)

        nx_ids = {r.source_id for r in nx_results}
        neo_ids = {r.source_id for r in neo_results}

        assert nx_ids == neo_ids, (
            f"Divergenza su {urn}: networkx={nx_ids - neo_ids} (solo qui), "
            f"neo4j={neo_ids - nx_ids} (solo qui)"
        )

    @pytest.mark.parametrize("urn", _LOW_DEGREE_URNS)
    def test_stesso_source_layer_per_ogni_match(self, networkx_retriever, neo4j_retriever, urn):
        nx_layers = {r.source_id: r.source_layer for r in networkx_retriever.expand([urn], depth=1, max_nodes=20)}
        neo_layers = {r.source_id: r.source_layer for r in neo4j_retriever.expand([urn], depth=1, max_nodes=20)}
        assert nx_layers == neo_layers

    def test_grado_alto_entrambi_rispettano_max_nodes(self, networkx_retriever, neo4j_retriever):
        nx_results = networkx_retriever.expand([_HIGH_DEGREE_URN], depth=1, max_nodes=10)
        neo_results = neo4j_retriever.expand([_HIGH_DEGREE_URN], depth=1, max_nodes=10)

        assert len(nx_results) == 10
        assert len(neo_results) == 10
        # Stessa "forma": tutti risultati di tipo giurisprudenza (l'unico edge_type
        # di espansione da questo nodo nei dati reali è APPLICATA_IN → sentenza)
        assert all(r.source_layer == "giurisprudenza" for r in nx_results)
        assert all(r.source_layer == "giurisprudenza" for r in neo_results)

    def test_source_id_inesistente_entrambi_vuoto(self, networkx_retriever, neo4j_retriever):
        assert networkx_retriever.expand(["urn:non:esiste"]) == []
        assert neo4j_retriever.expand(["urn:non:esiste"]) == []


@pytest.mark.integration
class TestParitaConflicts:

    @pytest.mark.parametrize("urn", _LOW_DEGREE_URNS)
    def test_stesso_risultato_conflitti(self, networkx_retriever, neo4j_retriever, urn):
        # Nei dati reali attuali non ci sono archi CONTRASTA — questo test
        # documenta la parità per quando (Fase 1 KG-LLM) ce ne saranno.
        nx_conf = set(networkx_retriever.get_conflicts([urn]))
        neo_conf = set(neo4j_retriever.get_conflicts([urn]))
        assert nx_conf == neo_conf


@pytest.mark.integration
class TestParitaHealth:

    def test_conteggi_nodi_e_archi_identici(self, networkx_retriever, neo4j_retriever):
        nx_health = networkx_retriever.get_health()
        neo_health = neo4j_retriever.get_health()
        assert nx_health.node_count == neo_health.node_count
        assert nx_health.edge_count == neo_health.edge_count


@pytest.mark.integration
class TestLatenzaComparativa:
    """
    Non un'asserzione di parità — un report di latenza per la decisione di
    rollout (Fase E). networkx paga il caricamento una sola volta per processo
    (qui già scaldato dalle fixture precedenti), neo4j paga ogni query
    indipendentemente ma non richiede mai un re-load completo in RAM.
    """

    def test_latenza_expand_sotto_soglia_accettabile(self, networkx_retriever, neo4j_retriever):
        urn = _LOW_DEGREE_URNS[0]

        t0 = time.monotonic()
        networkx_retriever.expand([urn], depth=1, max_nodes=20)
        nx_latency = time.monotonic() - t0

        t0 = time.monotonic()
        neo4j_retriever.expand([urn], depth=1, max_nodes=20)
        neo_latency = time.monotonic() - t0

        print(f"\n[latenza expand() a caldo] networkx={nx_latency*1000:.1f}ms neo4j={neo_latency*1000:.1f}ms")

        # Soglia larga: questo è un report per decidere il rollout, non un
        # gate di regressione stretto — sotto carico concorrente reale (10-50
        # utenti) il confronto andrebbe ripetuto con query parallele.
        assert neo_latency < 2.0
