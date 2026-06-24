"""
Test LegalGraphBuilder.merge_jurisprudence_graph — Fase 0 consolidamento grafi
(vedi core/graph/builder.py). Costruisce in memoria un grafo normativa target
e un grafo giurisprudenziale grezzo (nodi norma = stringhe non risolte a URN),
verifica che il merge risolva solo i casi non ambigui.
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


def _article(urn: str, art_num: str, fonte: str = "codice_civile") -> dict:
    return {
        "node_type": "article",
        "fonte": fonte,
        "titolo": fonte,
        "articolo_num": art_num,
        "testo_tipo": "normativo",
        "valid_from": None,
        "valid_to": None,
    }


def _target_graph_with_articles(*urns_and_nums: tuple[str, str, str]) -> nx.DiGraph:
    G: nx.DiGraph = nx.DiGraph()
    for urn, num, fonte in urns_and_nums:
        G.add_node(urn, **_article(urn, num, fonte))
    return G


def _jurisprudence_graph(edges: list[tuple[str, str]]) -> nx.DiGraph:
    """edges: [(sentenza_id, raw_norma_string), ...] — tutti tipo 'interpreta'."""
    G: nx.DiGraph = nx.DiGraph()
    for sid, raw_norma in edges:
        if not G.has_node(sid):
            G.add_node(sid, type="sentenza", organo="cassazione", numero="123", anno=2021, materia="civile")
        if not G.has_node(raw_norma):
            G.add_node(raw_norma, type="norma", urn=raw_norma)
        G.add_edge(sid, raw_norma, type="interpreta")
    return G


@pytest.fixture
def builder() -> LegalGraphBuilder:
    return LegalGraphBuilder()


class TestMergeJurisprudenceGraph:

    def test_match_univoco_crea_archi(self, builder, tmp_path):
        """Un solo articolo con quel numero → match, crea INTERPRETA + APPLICATA_IN."""
        target = _target_graph_with_articles(("urn:nir:art2119", "2119", "codice_civile"))
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 2119")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_added"] == 2
        assert stats["sentenza_nodes_added"] == 1
        assert stats["edges_skipped_ambiguous"] == 0
        assert stats["edges_skipped_no_match"] == 0

        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert G.has_edge("a1b2c3d4e5f60718", "urn:nir:art2119")
        assert G.has_edge("urn:nir:art2119", "a1b2c3d4e5f60718")
        assert G.nodes["a1b2c3d4e5f60718"]["node_type"] == "sentenza"

    def test_articolo_ambiguo_scartato(self, builder, tmp_path):
        """Due articoli con lo stesso numero in fonti diverse → ambiguo, nessun arco."""
        target = _target_graph_with_articles(
            ("urn:nir:cc:art380", "380", "codice_civile"),
            ("urn:nir:cpc:art380", "380", "codice_procedura_civile"),
        )
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art.380")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_added"] == 0
        assert stats["edges_skipped_ambiguous"] == 1
        assert stats["sentenza_nodes_added"] == 0

    def test_ambiguo_risolto_da_hint_fonte_proc_civ(self, builder, tmp_path):
        """L'hint 'cod. proc. civ.' nella stringa grezza disambigua tra c.c. e c.p.c."""
        target = _target_graph_with_articles(
            ("urn:nir:cc:art380", "380", "codice_civile"),
            ("urn:nir:cpc:art380", "380", "codice_proc_civile"),
        )
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 380 cod. proc. civ.")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_resolved_via_fonte_hint"] == 1
        assert stats["edges_added"] == 2
        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert G.has_edge("a1b2c3d4e5f60718", "urn:nir:cpc:art380")
        assert not G.has_edge("a1b2c3d4e5f60718", "urn:nir:cc:art380")

    def test_ambiguo_risolto_da_hint_fonte_civ_generico(self, builder, tmp_path):
        """L'hint 'cod. civ.' (senza 'proc.') punta al codice civile, non a quello penale."""
        target = _target_graph_with_articles(
            ("urn:nir:cc:art2729", "2729", "codice_civile"),
            ("urn:nir:cp:art2729", "2729", "codice_penale"),
        )
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art.2729 cod. civ.")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_resolved_via_fonte_hint"] == 1
        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        G = nx.node_link_graph(merged, edges="edges")
        assert G.has_edge("a1b2c3d4e5f60718", "urn:nir:cc:art2729")

    def test_hint_assente_resta_ambiguo(self, builder, tmp_path):
        """Senza hint riconoscibile (es. 'dello stesso codice') resta ambiguo."""
        target = _target_graph_with_articles(
            ("urn:nir:cc:art111", "111", "codice_civile"),
            ("urn:nir:cpc:art111", "111", "codice_proc_civile"),
        )
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 111 dello stesso codice")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_resolved_via_fonte_hint"] == 0
        assert stats["edges_skipped_ambiguous"] == 1
        assert stats["edges_added"] == 0

    def test_hint_che_non_matcha_nessuna_fonte_resta_ambiguo(self, builder, tmp_path):
        """Hint riconosciuto ma nessun candidato ha quella fonte → resta ambiguo, non sceglie a caso."""
        target = _target_graph_with_articles(
            ("urn:nir:legge:art5", "5", "legge"),
            ("urn:nir:dlgs:art5", "5", "dlgs"),
        )
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 5 cod. civ.")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_resolved_via_fonte_hint"] == 0
        assert stats["edges_skipped_ambiguous"] == 1
        assert stats["edges_added"] == 0

    def test_nessun_match_scartato(self, builder, tmp_path):
        """Numero articolo non presente nel grafo target → nessun arco creato."""
        target = _target_graph_with_articles(("urn:nir:art2119", "2119", "codice_civile"))
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 9999")])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["edges_added"] == 0
        assert stats["edges_skipped_no_match"] == 1

    def test_formati_diversi_stesso_articolo_risolvono_uguale(self, builder, tmp_path):
        """'art.380', 'art. 380', 'art. 380 cod.' normalizzano allo stesso numero."""
        target = _target_graph_with_articles(("urn:nir:art380", "380", "codice_civile"))
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([
            ("sentenza1", "art.380"),
            ("sentenza2", "art. 380"),
            ("sentenza3", "art. 380 cod."),
        ])
        stats = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats["sentenza_nodes_added"] == 3
        assert stats["edges_added"] == 6  # 3 sentenze × (INTERPRETA + APPLICATA_IN)

    def test_built_at_aggiornato_dopo_merge(self, builder, tmp_path):
        target = _target_graph_with_articles(("urn:nir:art2119", "2119", "codice_civile"))
        _save_target_graph(target, tmp_path)

        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 2119")])
        builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        merged = json.loads((tmp_path / "indices" / "graph.json").read_text(encoding="utf-8"))
        assert merged["graph"].get("built_at") is not None

    def test_no_duplicazione_su_merge_ripetuto(self, builder, tmp_path):
        """Eseguire il merge due volte non duplica nodi/archi (idempotente)."""
        target = _target_graph_with_articles(("urn:nir:art2119", "2119", "codice_civile"))
        _save_target_graph(target, tmp_path)
        jur_graph = _jurisprudence_graph([("a1b2c3d4e5f60718", "art. 2119")])

        builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))
        stats2 = builder.merge_jurisprudence_graph(jur_graph, str(tmp_path))

        assert stats2["edges_added"] == 0
        assert stats2["sentenza_nodes_added"] == 0


class TestExtractArticoloNumber:

    @pytest.mark.parametrize("raw,expected", [
        ("art. 380", "380"),
        ("art.380", "380"),
        ("art. 380 cod.", "380"),
        ("art. 391 cod.", "391"),
        ("articolo 18-bis", "18-bis"),
        ("nessun articolo qui", ""),
    ])
    def test_extract(self, raw, expected):
        assert LegalGraphBuilder._extract_articolo_number(raw) == expected


class TestExtractFonteHint:

    @pytest.mark.parametrize("raw,expected", [
        ("art. 391 cod. proc. civ.", "codice_proc_civile"),
        ("art. 391 cod. proc. civ", "codice_proc_civile"),
        ("art. 274 cod. proc. pen.", "codice_proc_penale"),
        ("art. 2729 cod. civ.", "codice_civile"),
        ("articolo 1163 del codice civile", "codice_civile"),
        ("art.416 bis cod. pen.", "codice_penale"),
        ("art. 309 codice di rito", ""),  # ambiguo, "rito" da solo non specifica civ/pen
        ("art. 111 dello stesso codice", ""),
        ("art. 132 del codice di", ""),
        ("nessun hint qui", ""),
    ])
    def test_extract(self, raw, expected):
        assert LegalGraphBuilder._extract_fonte_hint(raw) == expected
