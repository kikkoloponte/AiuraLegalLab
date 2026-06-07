"""
Test strutturali degli scraper Playwright.
Non lanciano il browser reale — verificano interfaccia, metodi di parsing
e comportamento del context manager.
I test di integrazione end-to-end (browser live) vanno in tests/integration/.
"""
from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza
from aiura_legal.jurisprudence.scrapers.base import BaseScraper, ScraperError
from aiura_legal.jurisprudence.scrapers.cassazione import CassazioneScraper
from aiura_legal.jurisprudence.scrapers.corte_cost import CorteCostScraper
from aiura_legal.jurisprudence.scrapers.corte_conti import CorteContiScraper
from aiura_legal.jurisprudence.scrapers.giustizia_amm import GiustiziaAmmScraper

_SINCE = date(2024, 1, 1)


# ---------------------------------------------------------------------------
# Interfaccia BaseScraper
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_context_manager_required():
    scraper = CassazioneScraper()
    with pytest.raises(RuntimeError, match="context manager"):
        await scraper.new_page()


def test_scrapers_hanno_organo():
    assert CassazioneScraper.organo == OrganoGiudicante.CASSAZIONE
    assert GiustiziaAmmScraper.organo == OrganoGiudicante.TAR
    assert CorteCostScraper.organo == OrganoGiudicante.CORTE_COST
    assert CorteContiScraper.organo == OrganoGiudicante.CORTE_CONTI


def test_scrapers_sono_subclass_base():
    for cls in [CassazioneScraper, GiustiziaAmmScraper, CorteCostScraper, CorteContiScraper]:
        assert issubclass(cls, BaseScraper)


def test_scrapers_hanno_fetch_since():
    for cls in [CassazioneScraper, GiustiziaAmmScraper, CorteCostScraper, CorteContiScraper]:
        assert callable(getattr(cls, "fetch_since", None))


def test_scrapers_rate_limit_positivo():
    for cls in [CassazioneScraper, GiustiziaAmmScraper, CorteCostScraper, CorteContiScraper]:
        assert cls.rate_limit_seconds > 0


# ---------------------------------------------------------------------------
# Parsing helpers — Cassazione (Solr API)
# ---------------------------------------------------------------------------

def test_cassazione_doc_to_raw_valido():
    scraper = CassazioneScraper()
    doc = {
        "sicId": ["sic2024100012345O001"],
        "numdec": "012345",
        "datdec": "20241015",
        "pd": "20241020",
        "kind": "snciv",
        "materia": ["RESPONSABILITA CIVILE"],
        "szdec": "3",
        "ocr": ["In fatto e in diritto la Corte osserva..."],
        "ocrdis": ["La Corte rigetta il ricorso."],
    }
    raw = scraper._doc_to_raw(doc)
    assert raw is not None
    assert raw.numero == "12345"
    assert raw.anno == 2024
    assert raw.organo == OrganoGiudicante.CASSAZIONE
    assert raw.data_deposito is not None


def test_cassazione_doc_to_raw_numdec_con_zeri():
    scraper = CassazioneScraper()
    doc = {"numdec": "00042", "datdec": "20240301", "sicId": [], "kind": "snpen",
           "ocr": [], "ocrdis": [], "materia": [], "szdec": "1", "pd": ""}
    raw = scraper._doc_to_raw(doc)
    assert raw is not None
    assert raw.numero == "42"


def test_cassazione_doc_to_raw_doc_vuoto():
    scraper = CassazioneScraper()
    raw = scraper._doc_to_raw({})
    # anno fallback a oggi, numero "0"
    assert raw is not None
    assert raw.organo == OrganoGiudicante.CASSAZIONE


# ---------------------------------------------------------------------------
# Parsing helpers — Corte Costituzionale
# ---------------------------------------------------------------------------

def test_corte_cost_extract_numero():
    scraper = CorteCostScraper()
    assert scraper._extract_numero("Sentenza n. 42 del 2024") == "42"
    assert scraper._extract_numero("  100  ") == "100"
    assert scraper._extract_numero("") == ""


def test_corte_cost_row_to_raw():
    scraper = CorteCostScraper()
    row = {"text": "42 15/03/2024 Sentenza", "href": "/detail/42"}
    raw = scraper._row_to_raw(row, 2024, _SINCE)
    assert raw is not None
    assert raw.numero == "42"
    assert raw.anno == 2024
    assert raw.organo == OrganoGiudicante.CORTE_COST


def test_corte_cost_row_to_raw_senza_numero():
    scraper = CorteCostScraper()
    row = {"text": "", "href": ""}
    raw = scraper._row_to_raw(row, 2024, _SINCE)
    assert raw is None


# ---------------------------------------------------------------------------
# Parsing helpers — Giustizia Amministrativa
# ---------------------------------------------------------------------------

def test_ga_extract_numero_da_provv():
    scraper = GiustiziaAmmScraper()
    assert scraper._extract_numero("numero provv.: 202610170") == "202610170"
    assert scraper._extract_numero("202610169 (ROMA, SEZIONE 1)") == "202610169"
    assert scraper._extract_numero("testo senza numero") == ""


def test_ga_extract_anno_da_numero():
    scraper = GiustiziaAmmScraper()
    # anno embedded nel numero provvedimento (2026XXXXX)
    assert scraper._extract_anno("202610170 (ROMA, SEZIONE 1)") == 2026
    assert scraper._extract_anno("testo senza anno") is None


def test_ga_item_to_raw_tar():
    scraper = GiustiziaAmmScraper()
    item = {
        "text": "202610170 (ROMA, SEZIONE 1)\nSENTENZA sede di ROMA, numero provv.: 202610170",
        "href": "/web/guest/-/sentenza-123",
        "html": "<p>TAR Roma</p>",
    }
    raw = scraper._item_to_raw(item)
    assert raw is not None
    assert raw.organo == OrganoGiudicante.TAR
    assert raw.numero == "202610170"


def test_ga_item_to_raw_consiglio_stato():
    scraper = GiustiziaAmmScraper()
    item = {
        "text": "202610050 (CDS)\nSENTENZA Consiglio di Stato, numero provv.: 202610050",
        "href": "",
        "html": "",
    }
    raw = scraper._item_to_raw(item)
    assert raw is not None
    assert raw.organo == OrganoGiudicante.CONSIGLIO_STATO


# ---------------------------------------------------------------------------
# Parsing helpers — Corte dei Conti
# ---------------------------------------------------------------------------

def test_corte_conti_extract_numero():
    scraper = CorteContiScraper()
    assert scraper._extract_numero("Sentenza n. 789/2024") == "789"
    assert scraper._extract_numero("") == ""


def test_corte_conti_extract_anno():
    scraper = CorteContiScraper()
    assert scraper._extract_anno("delibera 2023") == 2023
    assert scraper._extract_anno("nessun anno") is None
