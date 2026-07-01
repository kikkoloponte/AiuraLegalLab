"""
Test CitationReviewer — fallback su GraphRetriever.is_abrogated() per il
check temporal_validity quando metadata.valid_to è assente. Vedi
docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import networkx as nx
import pytest

from aiura_legal.core.graph.retriever import GraphRetriever
from aiura_legal.core.reviewer.reviewer import CitationReviewer
from aiura_legal.core.types import ResearchPacket, QueryIntent, SearchResult


def _save_graph(G: nx.DiGraph, workspace: Path) -> None:
    (workspace / "indices").mkdir(parents=True, exist_ok=True)
    data = nx.node_link_data(G, edges="edges")
    (workspace / "indices" / "graph.json").write_text(json.dumps(data), encoding="utf-8")


def _article_node(valid_to: str | None = "99999999") -> dict:
    return {
        "node_type": "article",
        "fonte": "codice_civile",
        "titolo": "Codice Civile",
        "articolo_num": "1218",
        "testo_tipo": "normativo",
        "valid_from": "20000101",
        "valid_to": valid_to,
    }


def _make_packet(source_id: str) -> ResearchPacket:
    # Nota: nessun metadata.valid_to — è esattamente il caso che il
    # fallback sul grafo deve coprire.
    return ResearchPacket(
        query_original="test",
        query_intent=QueryIntent.NORMA_LOOKUP,
        sources=[SearchResult(doc_id=source_id, score=1.0, snippet="...", source_id=source_id, metadata={})],
    )


@pytest.fixture(autouse=True)
def _force_networkx_backend(monkeypatch):
    monkeypatch.setenv("AIURA_GRAPH_BACKEND", "networkx")


class TestVigenzaFallbackGrafo:

    def test_norma_abrogata_nel_grafo_senza_metadata_warn(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("CC_ART_1218", **_article_node(valid_to="20100101"))
        _save_graph(G, tmp_path)
        graph = GraphRetriever(str(tmp_path))
        reviewer = CitationReviewer(graph=graph)

        packet = _make_packet("CC_ART_1218")
        result = reviewer.verify(
            "Ai sensi CC_ART_1218.", packet, reference_date=date(2024, 1, 1),
        )

        assert result.checks["temporal_validity"] == "WARN"
        assert "CC_ART_1218" in result.warnings[0]

    def test_norma_vigente_nel_grafo_senza_metadata_pass(self, tmp_path):
        G = nx.DiGraph()
        G.add_node("CC_ART_1218", **_article_node(valid_to="99999999"))
        _save_graph(G, tmp_path)
        graph = GraphRetriever(str(tmp_path))
        reviewer = CitationReviewer(graph=graph)

        packet = _make_packet("CC_ART_1218")
        result = reviewer.verify(
            "Ai sensi CC_ART_1218.", packet, reference_date=date(2024, 1, 1),
        )

        assert result.checks["temporal_validity"] == "PASS"

    def test_senza_grafo_e_senza_metadata_assume_vigente_pass(self):
        """Backward compatible: nessun graph, nessun metadata → comportamento storico (PASS)."""
        reviewer = CitationReviewer(graph=None)
        packet = _make_packet("CC_ART_1218")
        result = reviewer.verify(
            "Ai sensi CC_ART_1218.", packet, reference_date=date(2024, 1, 1),
        )
        assert result.checks["temporal_validity"] == "PASS"

    def test_metadata_presente_ha_priorita_sul_grafo(self, tmp_path):
        """Se metadata.valid_to è presente, il grafo non viene nemmeno interrogato."""
        G = nx.DiGraph()
        G.add_node("CC_ART_1218", **_article_node(valid_to="99999999"))  # vigente nel grafo
        _save_graph(G, tmp_path)
        graph = GraphRetriever(str(tmp_path))
        reviewer = CitationReviewer(graph=graph)

        packet = ResearchPacket(
            query_original="test",
            query_intent=QueryIntent.NORMA_LOOKUP,
            sources=[SearchResult(
                doc_id="CC_ART_1218", score=1.0, snippet="...", source_id="CC_ART_1218",
                metadata={"valid_to": "2020-01-01"},  # scaduta secondo i metadata
            )],
        )
        result = reviewer.verify(
            "Ai sensi CC_ART_1218.", packet, reference_date=date(2024, 1, 1),
        )
        # I metadata (scaduta) vincono sul grafo (vigente) — priorità storica invariata.
        assert result.checks["temporal_validity"] == "WARN"
