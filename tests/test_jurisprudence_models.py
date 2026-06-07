from datetime import date

import pytest

from aiura_legal.jurisprudence.models import (
    JurisprudenceDocument,
    OrganoGiudicante,
    RawSentenza,
    SourceChannel,
)


def _make_doc(**kwargs) -> JurisprudenceDocument:
    defaults = dict(
        organo=OrganoGiudicante.CASSAZIONE,
        numero="12345",
        anno=2024,
        data_deposito=date(2024, 3, 15),
        sezione="III Sezione Civile",
        materia="responsabilità civile",
        massima="La responsabilità extracontrattuale richiede il nesso causale.",
        motivazione="In fatto e in diritto...",
        dispositivo="La Corte rigetta il ricorso.",
    )
    defaults.update(kwargs)
    return JurisprudenceDocument(**defaults)


def test_id_is_deterministic():
    doc1 = _make_doc()
    doc2 = _make_doc()
    assert doc1.id == doc2.id


def test_id_changes_with_organo():
    doc_cass = _make_doc(organo=OrganoGiudicante.CASSAZIONE)
    doc_tar = _make_doc(organo=OrganoGiudicante.TAR)
    assert doc_cass.id != doc_tar.id


def test_id_changes_with_numero():
    doc1 = _make_doc(numero="1")
    doc2 = _make_doc(numero="2")
    assert doc1.id != doc2.id


def test_id_changes_with_anno():
    doc1 = _make_doc(anno=2023)
    doc2 = _make_doc(anno=2024)
    assert doc1.id != doc2.id


def test_id_length():
    doc = _make_doc()
    assert len(doc.id) == 16


def test_default_source_channel():
    doc = _make_doc()
    assert doc.source_channel == SourceChannel.SCRAPING


def test_default_not_anonymized():
    doc = _make_doc()
    assert doc.is_anonymized is False


def test_default_pii_vault_id_none():
    doc = _make_doc()
    assert doc.raw_pii_vault_id is None


def test_default_empty_lists():
    doc = _make_doc()
    assert doc.norme_citate == []
    assert doc.sentenze_citate == []


def test_norme_citate():
    doc = _make_doc(norme_citate=["urn:nir:stato:codice.civile:art2043"])
    assert len(doc.norme_citate) == 1


def test_upload_studio_channel():
    doc = _make_doc(
        source_channel=SourceChannel.UPLOAD_STUDIO,
        is_anonymized=True,
        raw_pii_vault_id="vault-abc123",
    )
    assert doc.source_channel == SourceChannel.UPLOAD_STUDIO
    assert doc.is_anonymized is True
    assert doc.raw_pii_vault_id == "vault-abc123"


def test_raw_sentenza_fields():
    raw = RawSentenza(
        numero="99",
        anno=2023,
        organo=OrganoGiudicante.CORTE_COST,
        source_url="https://example.com/sentenza/99",
        raw_html="<html></html>",
    )
    assert raw.raw_pdf_bytes is None
    assert raw.data_deposito is None


def test_organo_giudicante_values():
    assert OrganoGiudicante.CASSAZIONE.value == "cassazione"
    assert OrganoGiudicante.TAR.value == "tar"
    assert OrganoGiudicante.CONSIGLIO_STATO.value == "consiglio_stato"
    assert OrganoGiudicante.CORTE_COST.value == "corte_cost"
    assert OrganoGiudicante.CORTE_CONTI.value == "corte_conti"
