"""
Test del parser giurisprudenziale con fixture sintetici.
Tutti i testi usano dati inventati — nessun nome/CF reale.
"""
from datetime import date

import io
import pytest
import pdfplumber
from reportlab.pdfgen import canvas as rl_canvas

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza, SourceChannel
from aiura_legal.jurisprudence.parser import parse_html, parse_pdf, _extract_sections, _extract_raw_norme


# ---------------------------------------------------------------------------
# Fixture HTML
# ---------------------------------------------------------------------------

_HTML_COMPLETO = """
<html><body>
<h1>Corte di Cassazione — Sentenza n. 999/2024</h1>
<p>Sezione III Civile</p>
<p>Depositata il 15 marzo 2024</p>

<h2>MASSIMA</h2>
<p>Il danneggiato ha diritto al risarcimento ai sensi dell'art. 2043 c.c.
qualora sussista il nesso causale tra la condotta e il danno.</p>

<h2>FATTO E DIRITTO</h2>
<p>In fatto: Tizio conveniva in giudizio Caio chiedendo il risarcimento.
Il Tribunale di Roma accoglieva la domanda. La Corte d'Appello confermava.
Si applica l'art. 1226 c.c. per la liquidazione equitativa del danno.</p>

<h2>P.Q.M.</h2>
<p>La Corte rigetta il ricorso e condanna il ricorrente alle spese.</p>
</body></html>
"""

_HTML_SENZA_MASSIMA = """
<html><body>
<h2>MOTIVI DELLA DECISIONE</h2>
<p>La questione verte sull'interpretazione dell'art. 1218 c.c.</p>
<h2>P.Q.M.</h2>
<p>Accoglie il ricorso.</p>
</body></html>
"""

_HTML_NO_SEZIONI = """
<html><body>
<p>Sentenza senza sezioni riconoscibili. Testo libero.</p>
</body></html>
"""


def _make_raw_html(html: str, numero: str = "999", anno: int = 2024) -> RawSentenza:
    return RawSentenza(
        numero=numero,
        anno=anno,
        organo=OrganoGiudicante.CASSAZIONE,
        source_url="https://example.com/sentenza/999",
        raw_html=html,
    )


# ---------------------------------------------------------------------------
# Test HTML — sezioni
# ---------------------------------------------------------------------------

def test_parse_html_massima():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert "risarcimento" in doc.massima
    assert "art. 2043" in doc.massima


def test_parse_html_motivazione():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert "Tizio" in doc.motivazione


def test_parse_html_dispositivo():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert "rigetta" in doc.dispositivo.lower()


def test_parse_html_senza_massima_ha_motivazione():
    doc = parse_html(_make_raw_html(_HTML_SENZA_MASSIMA))
    assert doc.massima == ""
    assert "1218" in doc.motivazione


def test_parse_html_no_sezioni_fallback():
    doc = parse_html(_make_raw_html(_HTML_NO_SEZIONI))
    assert doc.massima == ""
    assert doc.dispositivo == ""
    assert "Testo libero" in doc.motivazione


# ---------------------------------------------------------------------------
# Test HTML — metadati
# ---------------------------------------------------------------------------

def test_parse_html_data_estratta():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert doc.data_deposito == date(2024, 3, 15)


def test_parse_html_data_fallback_anno():
    doc = parse_html(_make_raw_html(_HTML_NO_SEZIONI, anno=2022))
    assert doc.data_deposito.year == 2022


def test_parse_html_data_da_raw_sentenza():
    raw = _make_raw_html(_HTML_COMPLETO)
    raw.data_deposito = date(2020, 1, 1)
    doc = parse_html(raw)
    assert doc.data_deposito == date(2020, 1, 1)


def test_parse_html_sezione():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert "III" in doc.sezione or "Civile" in doc.sezione


def test_parse_html_organo():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert doc.organo == OrganoGiudicante.CASSAZIONE


def test_parse_html_source_channel_default():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    assert doc.source_channel == SourceChannel.SCRAPING


def test_parse_html_source_channel_upload():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO), source_channel=SourceChannel.UPLOAD_STUDIO)
    assert doc.source_channel == SourceChannel.UPLOAD_STUDIO


# ---------------------------------------------------------------------------
# Test HTML — norme citate
# ---------------------------------------------------------------------------

def test_parse_html_norme_citate():
    doc = parse_html(_make_raw_html(_HTML_COMPLETO))
    testo = " ".join(doc.norme_citate)
    assert any("2043" in n for n in doc.norme_citate)


def test_parse_html_norme_no_duplicati():
    html = "<html><body><p>art. 2043 c.c. e ancora art. 2043 c.c.</p></body></html>"
    doc = parse_html(_make_raw_html(html))
    count_2043 = sum(1 for n in doc.norme_citate if "2043" in n)
    assert count_2043 == 1


# ---------------------------------------------------------------------------
# Test errori
# ---------------------------------------------------------------------------

def test_parse_html_raises_senza_html():
    raw = RawSentenza(
        numero="1", anno=2024,
        organo=OrganoGiudicante.TAR,
        source_url="https://example.com",
    )
    with pytest.raises(ValueError, match="HTML"):
        parse_html(raw)


def test_parse_pdf_raises_senza_pdf():
    raw = RawSentenza(
        numero="1", anno=2024,
        organo=OrganoGiudicante.TAR,
        source_url="https://example.com",
    )
    with pytest.raises(ValueError, match="PDF"):
        parse_pdf(raw)


# ---------------------------------------------------------------------------
# Test PDF sintetico (generato con reportlab)
# ---------------------------------------------------------------------------

def _make_pdf_bytes(text: str) -> bytes:
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf)
    y = 800
    for line in text.split("\n"):
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(50, y, line[:90])
        y -= 15
    c.save()
    return buf.getvalue()


_PDF_TEXT = """\
Corte dei Conti — Sentenza n. 77/2023
Sezione Giurisdizionale

MASSIMA
La responsabilità contabile presuppone il nesso causale con il danno erariale.

MOTIVI DELLA DECISIONE
Il convenuto ha omesso di applicare l'art. 81 della Costituzione.
Il danno erariale ammonta a euro 50.000.

P.Q.M.
Condanna il convenuto al pagamento di euro 50.000.
"""


@pytest.fixture
def raw_pdf() -> RawSentenza:
    return RawSentenza(
        numero="77",
        anno=2023,
        organo=OrganoGiudicante.CORTE_CONTI,
        source_url="https://example.com/cdc/77",
        raw_pdf_bytes=_make_pdf_bytes(_PDF_TEXT),
    )


def test_parse_pdf_massima(raw_pdf):
    doc = parse_pdf(raw_pdf)
    assert "responsabilità" in doc.massima.lower() or "contabile" in doc.massima.lower()


def test_parse_pdf_dispositivo(raw_pdf):
    doc = parse_pdf(raw_pdf)
    assert "condanna" in doc.dispositivo.lower() or "50.000" in doc.dispositivo


def test_parse_pdf_organo(raw_pdf):
    doc = parse_pdf(raw_pdf)
    assert doc.organo == OrganoGiudicante.CORTE_CONTI


def test_parse_pdf_id_stabile(raw_pdf):
    doc1 = parse_pdf(raw_pdf)
    doc2 = parse_pdf(raw_pdf)
    assert doc1.id == doc2.id


# ---------------------------------------------------------------------------
# Test unità helper
# ---------------------------------------------------------------------------

def test_extract_sections_tutti_presenti():
    testo = "MASSIMA\nLa massima qui.\nFATTO E DIRITTO\nMotivazione.\nP.Q.M.\nDispositivo."
    massima, motivazione, dispositivo = _extract_sections(testo)
    assert "massima" in massima.lower()
    assert "motivazione" in motivazione.lower()
    assert "dispositivo" in dispositivo.lower()


def test_extract_sections_fallback_testo_libero():
    massima, motivazione, dispositivo = _extract_sections("testo senza intestazioni")
    assert massima == ""
    assert "testo senza intestazioni" in motivazione
    assert dispositivo == ""


def test_extract_raw_norme():
    testo = "Ai sensi dell'art. 2043 c.c. e dell'art. 1 comma 2 della legge X."
    norme = _extract_raw_norme(testo)
    assert any("2043" in n for n in norme)
    assert any("1" in n for n in norme)
