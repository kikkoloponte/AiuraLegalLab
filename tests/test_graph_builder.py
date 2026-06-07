"""
Test graph_builder con grafo sintetico (5 norme + 3 sentenze).
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from aiura_legal.jurisprudence.graph_builder import JurisprudenceGraphBuilder
from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante

_URN_2043 = "urn:nir:stato:codice.civile:art2043"
_URN_1218 = "urn:nir:stato:codice.civile:art1218"
_URN_81 = "urn:nir:stato:costituzione:art81"
_URN_97 = "urn:nir:stato:costituzione:art97"
_URN_111 = "urn:nir:stato:costituzione:art111"


def _make_doc(numero: str, norme: list[str], cita: list[str] | None = None) -> JurisprudenceDocument:
    return JurisprudenceDocument(
        organo=OrganoGiudicante.CASSAZIONE,
        numero=numero,
        anno=2024,
        data_deposito=date(2024, 1, 1),
        sezione="III",
        materia="civile",
        massima="Massima.",
        motivazione="Motivazione.",
        dispositivo="Dispositivo.",
        norme_citate=norme,
        sentenze_citate=cita or [],
    )


@pytest.fixture
def builder(tmp_path):
    return JurisprudenceGraphBuilder(tmp_path / "test_graph.json")


@pytest.fixture
def populated_builder(tmp_path):
    b = JurisprudenceGraphBuilder(tmp_path / "pop_graph.json")
    doc1 = _make_doc("1", [_URN_2043, _URN_1218])
    doc2 = _make_doc("2", [_URN_81, _URN_97])
    doc3 = _make_doc("3", [_URN_2043, _URN_111], cita=[doc1.id])
    b.add_documents_batch([doc1, doc2, doc3])
    return b, doc1, doc2, doc3


# ---------------------------------------------------------------------------
# Nodi
# ---------------------------------------------------------------------------

def test_add_document_crea_nodo_sentenza(builder):
    doc = _make_doc("1", [_URN_2043])
    builder.add_document(doc)
    assert builder.sentenza_exists(doc.id)


def test_add_document_crea_nodo_norma(builder):
    doc = _make_doc("1", [_URN_2043])
    builder.add_document(doc)
    assert _URN_2043 in builder.graph.nodes
    assert builder.graph.nodes[_URN_2043]["type"] == "norma"


def test_sentenza_node_attributi(builder):
    doc = _make_doc("42", [_URN_2043])
    builder.add_document(doc)
    node = builder.graph.nodes[doc.id]
    assert node["organo"] == "cassazione"
    assert node["numero"] == "42"
    assert node["anno"] == 2024


# ---------------------------------------------------------------------------
# Archi
# ---------------------------------------------------------------------------

def test_arco_interpreta(builder):
    doc = _make_doc("1", [_URN_2043])
    builder.add_document(doc)
    assert builder.graph.has_edge(doc.id, _URN_2043)
    assert builder.graph[doc.id][_URN_2043]["type"] == "interpreta"


def test_arco_applicata_in(builder):
    doc = _make_doc("1", [_URN_2043])
    builder.add_document(doc)
    assert builder.graph.has_edge(_URN_2043, doc.id)
    assert builder.graph[_URN_2043][doc.id]["type"] == "applicata_in"


def test_arco_cita(populated_builder):
    b, doc1, _, doc3 = populated_builder
    assert b.graph.has_edge(doc3.id, doc1.id)
    assert b.graph[doc3.id][doc1.id]["type"] == "cita"


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------

def test_get_sentenze_per_norma(populated_builder):
    b, doc1, _, doc3 = populated_builder
    sentenze = b.get_sentenze_per_norma(_URN_2043)
    assert doc1.id in sentenze
    assert doc3.id in sentenze


def test_get_sentenze_per_norma_vuoto(builder):
    assert builder.get_sentenze_per_norma("urn:nir:inesistente") == []


def test_get_norme_per_sentenza(populated_builder):
    b, doc1, _, _ = populated_builder
    norme = b.get_norme_per_sentenza(doc1.id)
    assert _URN_2043 in norme
    assert _URN_1218 in norme


def test_5_norme_3_sentenze(populated_builder):
    b, *_ = populated_builder
    norma_nodes = [n for n, d in b.graph.nodes(data=True) if d.get("type") == "norma"]
    sent_nodes = [n for n, d in b.graph.nodes(data=True) if d.get("type") == "sentenza"]
    assert len(norma_nodes) == 5
    assert len(sent_nodes) == 3


# ---------------------------------------------------------------------------
# Persistenza
# ---------------------------------------------------------------------------

def test_save_and_reload(tmp_path):
    path = tmp_path / "graph.json"
    doc = _make_doc("1", [_URN_2043, _URN_1218])

    b1 = JurisprudenceGraphBuilder(path)
    b1.add_document(doc)
    b1.save()

    b2 = JurisprudenceGraphBuilder(path)
    assert b2.sentenza_exists(doc.id)
    assert _URN_2043 in b2.graph.nodes


def test_reload_empty_se_file_assente(tmp_path):
    b = JurisprudenceGraphBuilder(tmp_path / "nonexistent.json")
    assert b.graph.number_of_nodes() == 0


def test_idempotente_add(builder):
    doc = _make_doc("1", [_URN_2043])
    builder.add_document(doc)
    n_before = builder.graph.number_of_nodes()
    builder.add_document(doc)
    assert builder.graph.number_of_nodes() == n_before


# ---------------------------------------------------------------------------
# Remove
# ---------------------------------------------------------------------------

def test_remove_document(builder):
    doc = _make_doc("1", [_URN_2043])
    builder.add_document(doc)
    builder.remove_document(doc.id)
    assert not builder.sentenza_exists(doc.id)
