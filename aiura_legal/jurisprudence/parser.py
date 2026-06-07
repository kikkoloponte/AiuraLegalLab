"""
Parser per sentenze grezze (HTML e PDF) → JurisprudenceDocument parziale.
Le norme_citate vengono risolte a URN dal graph_builder, non qui.
"""
from __future__ import annotations

import io
import re
from datetime import date
from typing import Optional

import pdfplumber
from bs4 import BeautifulSoup
from loguru import logger

from aiura_legal.jurisprudence.models import (
    JurisprudenceDocument,
    OrganoGiudicante,
    RawSentenza,
    SourceChannel,
)

# Pattern per estrarre riferimenti normativi grezzi (es. "art. 2043 c.c.")
_NORMA_RAW_RE = re.compile(
    r"\bart(?:icolo)?\.?\s*\d+(?:\s*(?:bis|ter|quater|quinquies))?"
    r"(?:\s*(?:comma|co\.?)\s*\d+)?(?:\s+\w+\.?){0,3}",
    re.IGNORECASE,
)

# Intestazioni di sezione nelle sentenze italiane
_SECTION_MASSIMA = re.compile(
    r"(?:MASSIMA|Massima|massima)[:\s]*", re.IGNORECASE
)
_SECTION_FATTO = re.compile(
    r"(?:FATTO\s+E\s+DIRITTO|IN\s+FATTO\s+E\s+IN\s+DIRITTO"
    r"|MOTIVI\s+DELLA\s+DECISIONE|MOTIVAZIONE|Svolgimento del processo)[:\s]*",
    re.IGNORECASE,
)
_SECTION_DISPOSITIVO = re.compile(
    r"(?:P\.?\s*Q\.?\s*M\.?|DISPOSITIVO|Per questi motivi)[:\s]*",
    re.IGNORECASE,
)


def _extract_sections(text: str) -> tuple[str, str, str]:
    """
    Restituisce (massima, motivazione, dispositivo) da testo grezzo.
    Se una sezione non è individuabile usa fallback progressivo.
    """
    massima = ""
    motivazione = ""
    dispositivo = ""

    m_massima = _SECTION_MASSIMA.search(text)
    m_fatto = _SECTION_FATTO.search(text)
    m_disp = _SECTION_DISPOSITIVO.search(text)

    if m_massima and m_fatto:
        massima = text[m_massima.end():m_fatto.start()].strip()
    elif m_massima and m_disp:
        massima = text[m_massima.end():m_disp.start()].strip()
    elif m_massima:
        # prende le prime 500 caratteri dopo "MASSIMA"
        massima = text[m_massima.end():m_massima.end() + 500].strip()

    if m_fatto and m_disp:
        motivazione = text[m_fatto.end():m_disp.start()].strip()
    elif m_fatto:
        motivazione = text[m_fatto.end():].strip()

    if m_disp:
        dispositivo = text[m_disp.end():].strip()

    # Fallback: se non si trovano sezioni usa tutto il testo come motivazione
    if not massima and not motivazione and not dispositivo:
        motivazione = text.strip()

    return massima or "", motivazione or "", dispositivo or ""


def _extract_raw_norme(text: str) -> list[str]:
    """Estrae riferimenti normativi grezzi — la risoluzione URN è del graph_builder."""
    found = _NORMA_RAW_RE.findall(text)
    return list(dict.fromkeys(ref.strip() for ref in found))


def _parse_data(text: str) -> Optional[date]:
    """Prova a estrarre la data di deposito dal testo (formato italiano)."""
    pattern = re.compile(
        r"\b(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno"
        r"|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})\b",
        re.IGNORECASE,
    )
    mesi = {
        "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
        "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
        "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12,
    }
    m = pattern.search(text)
    if m:
        try:
            return date(int(m.group(3)), mesi[m.group(2).lower()], int(m.group(1)))
        except ValueError:
            pass
    return None


def _extract_sezione(text: str) -> str:
    pattern = re.compile(
        r"(Sezione\s+[A-Za-z]+(?:\s+[A-Za-z]+)?|Sez\.\s*\w+)", re.IGNORECASE
    )
    m = pattern.search(text)
    return m.group(0).strip() if m else ""


def _text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)


def _text_from_pdf(pdf_bytes: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def _build_document(raw: RawSentenza, text: str, source_channel: SourceChannel) -> JurisprudenceDocument:
    massima, motivazione, dispositivo = _extract_sections(text)
    norme_raw = _extract_raw_norme(text)
    data = raw.data_deposito or _parse_data(text) or date(raw.anno, 1, 1)
    sezione = _extract_sezione(text)

    return JurisprudenceDocument(
        organo=raw.organo,
        numero=raw.numero,
        anno=raw.anno,
        data_deposito=data,
        sezione=sezione,
        materia="",
        massima=massima,
        motivazione=motivazione,
        dispositivo=dispositivo,
        norme_citate=norme_raw,
        source_url=raw.source_url,
        source_channel=source_channel,
    )


def parse_html(raw: RawSentenza, source_channel: SourceChannel = SourceChannel.SCRAPING) -> JurisprudenceDocument:
    if not raw.raw_html:
        raise ValueError(f"RawSentenza {raw.numero}/{raw.anno} non contiene HTML")
    text = _text_from_html(raw.raw_html)
    logger.debug("parse_html: {}/{} — {} chars", raw.numero, raw.anno, len(text))
    return _build_document(raw, text, source_channel)


def parse_pdf(raw: RawSentenza, source_channel: SourceChannel = SourceChannel.SCRAPING) -> JurisprudenceDocument:
    if not raw.raw_pdf_bytes:
        raise ValueError(f"RawSentenza {raw.numero}/{raw.anno} non contiene PDF")
    text = _text_from_pdf(raw.raw_pdf_bytes)
    logger.debug("parse_pdf: {}/{} — {} chars", raw.numero, raw.anno, len(text))
    return _build_document(raw, text, source_channel)
