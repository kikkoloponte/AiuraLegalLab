"""
test_akn_parser.py — test per AKNParser (Normattiva AKN XML).

Copertura:
  TestParseDateAKN     (5) — ISO completo, solo anno, formato errato, vuoto
  TestParseVigenza     (7) — vigente, abrogato con data, incostituzionale,
                              FRBRdate generation, lifecycle events, XML vuoto
  TestParseArticles    (5) — articoli estratti, status inline abrogato/incost., ereditarietà
  TestEnrichDoc        (3) — aggiornamento dict documento
  TestDetectNamespace  (3) — AKN 2.0, AKN 3.0, senza namespace
"""
from __future__ import annotations

import pytest

from aiura_legal.ingestion.normattiva.akn_parser import AKNParser, VigenzaInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

AKN_NS2 = "http://www.akomantoso.org/2.0"
AKN_NS3 = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"


def _xml(body: str, ns: str = AKN_NS3) -> str:
    """Wrappa il body in un documento AKN minimale."""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<akomaNtoso xmlns="{ns}">
  <act name="legge">
    <meta>
      <identification source="#autore">
        <FRBRWork>
          <FRBRdate date="2023-03-15" name="generation"/>
        </FRBRWork>
        <FRBRExpression>
          <FRBRdate date="2023-03-15" name="generation"/>
        </FRBRExpression>
      </identification>
      <lifecycle source="#test">
        {body}
      </lifecycle>
    </meta>
    <body/>
  </act>
</akomaNtoso>'''


def _xml_with_articles(articles_xml: str, lifecycle: str = "", ns: str = AKN_NS3) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<akomaNtoso xmlns="{ns}">
  <act name="legge">
    <meta>
      <identification source="#autore">
        <FRBRWork><FRBRdate date="2020-01-01" name="generation"/></FRBRWork>
      </identification>
      <lifecycle source="#test">{lifecycle}</lifecycle>
    </meta>
    <body>
      {articles_xml}
    </body>
  </act>
</akomaNtoso>'''


# ---------------------------------------------------------------------------
# TestParseDateAKN
# ---------------------------------------------------------------------------

class TestParseDateAKN:
    def test_iso_full_date(self):
        assert AKNParser._parse_akn_date("2023-01-15") == "20230115"

    def test_year_only(self):
        assert AKNParser._parse_akn_date("2023") == "20230101"

    def test_invalid_returns_none(self):
        assert AKNParser._parse_akn_date("non-una-data") is None

    def test_empty_returns_none(self):
        assert AKNParser._parse_akn_date("") is None

    def test_none_like_returns_none(self):
        assert AKNParser._parse_akn_date("   ") is None


# ---------------------------------------------------------------------------
# TestParseVigenza
# ---------------------------------------------------------------------------

class TestParseVigenza:
    def setup_method(self):
        self.p = AKNParser()

    def test_vigente_no_events(self):
        xml = _xml("")
        info = self.p.parse_vigenza(xml)
        assert info.status == "vigente"
        assert info.is_abrogated is False
        assert info.valid_from == "20230315"
        assert info.valid_to == "99999999"

    def test_abrogated_with_repeal_event(self):
        events = '<eventRef date="2024-06-01" type="repeal" source="#l100" refers="#urn:nir:legge:2024"/>'
        xml = _xml(events)
        info = self.p.parse_vigenza(xml)
        assert info.is_abrogated is True
        assert info.status == "abrogato"
        assert info.valid_to == "20240601"

    def test_abrogated_stores_abrogated_by(self):
        events = '<eventRef date="2024-01-01" type="repeal" refers="#urn:nir:legge:2024;100"/>'
        xml = _xml(events)
        info = self.p.parse_vigenza(xml)
        assert info.abrogated_by == "urn:nir:legge:2024;100"

    def test_unconstitutional_event(self):
        events = '<eventRef date="2022-05-20" type="annulment" source="#cost"/>'
        xml = _xml(events)
        info = self.p.parse_vigenza(xml)
        assert info.is_unconstitutional is True
        assert info.status == "incostituzionale"

    def test_amendment_events_collected(self):
        events = '''
          <eventRef date="2021-01-01" type="amendment" source="#l50"/>
          <eventRef date="2022-06-15" type="amendment" source="#l80"/>
        '''
        xml = _xml(events)
        info = self.p.parse_vigenza(xml)
        assert len(info.amendments) == 2
        assert info.amendments[0]["date"] == "20210101"

    def test_empty_xml_returns_default(self):
        info = self.p.parse_vigenza("")
        assert info.status == "vigente"
        assert info.valid_from is None

    def test_malformed_xml_returns_default(self):
        info = self.p.parse_vigenza("<broken xml")
        assert isinstance(info, VigenzaInfo)


# ---------------------------------------------------------------------------
# TestParseArticles
# ---------------------------------------------------------------------------

class TestParseArticles:
    def setup_method(self):
        self.p = AKNParser()

    def test_extracts_articles(self):
        arts = '''
          <article eId="art1"><num>1</num><content>Testo articolo 1.</content></article>
          <article eId="art2"><num>2</num><content>Testo articolo 2.</content></article>
        '''
        xml = _xml_with_articles(arts)
        articles = self.p.parse_articles(xml)
        assert len(articles) == 2
        assert articles[0].article_num == "1"
        assert articles[1].article_num == "2"

    def test_article_inherits_doc_vigenza(self):
        arts = '<article eId="art1"><num>1</num></article>'
        xml = _xml_with_articles(arts)
        articles = self.p.parse_articles(xml)
        assert articles[0].vigenza.valid_from == "20200101"

    def test_article_inline_abrogated_status(self):
        arts = '<article eId="art3" status="abrogato"><num>3</num></article>'
        xml = _xml_with_articles(arts)
        articles = self.p.parse_articles(xml)
        assert articles[0].vigenza.is_abrogated is True
        assert articles[0].vigenza.status == "abrogato"

    def test_article_inline_unconstitutional(self):
        arts = '<article eId="art5" status="annulment"><num>5</num></article>'
        xml = _xml_with_articles(arts)
        articles = self.p.parse_articles(xml)
        assert articles[0].vigenza.is_unconstitutional is True

    def test_empty_xml_returns_empty_list(self):
        assert self.p.parse_articles("") == []


# ---------------------------------------------------------------------------
# TestEnrichDoc
# ---------------------------------------------------------------------------

class TestEnrichDoc:
    def setup_method(self):
        self.p = AKNParser()

    def test_enrich_adds_vigenza_fields(self):
        xml = _xml("")
        doc = {"titolo": "Test"}
        result = self.p.enrich_doc(doc, xml)
        assert result["data_inizio_vigenza"] == "20230315"
        assert result["vigenza_status"] == "vigente"

    def test_enrich_marks_abrogated(self):
        events = '<eventRef date="2024-01-01" type="repeal" source="#x"/>'
        xml = _xml(events)
        doc = {}
        result = self.p.enrich_doc(doc, xml)
        assert result["is_abrogated"] is True
        assert result["data_fine_vigenza"] == "20240101"

    def test_enrich_returns_same_dict(self):
        xml = _xml("")
        doc = {"titolo": "X"}
        result = self.p.enrich_doc(doc, xml)
        assert result is doc   # stessa istanza


# ---------------------------------------------------------------------------
# TestDetectNamespace
# ---------------------------------------------------------------------------

class TestDetectNamespace:
    def setup_method(self):
        self.p = AKNParser()

    def test_detects_ns3(self):
        xml = f'<akomaNtoso xmlns="{AKN_NS3}"/>'
        ns = self.p._detect_namespace(xml)
        assert ns == AKN_NS3

    def test_detects_ns2(self):
        xml = f'<akomaNtoso xmlns="{AKN_NS2}"/>'
        ns = self.p._detect_namespace(xml)
        assert ns == AKN_NS2

    def test_no_namespace(self):
        xml = "<akomaNtoso/>"
        ns = self.p._detect_namespace(xml)
        assert ns == ""
