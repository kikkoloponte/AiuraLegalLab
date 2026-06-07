"""
Scraper Agenzia delle Entrate — Circolari e Risoluzioni.

Meccanismo:
  - Liferay Asset Publisher paginato via httpx (no Playwright)
  - Ogni documento ha un PDF diretto in /portale/documents/
  - Paginazione: ?p_p_id=<portlet>&_<portlet>_cur=N&_<portlet>_delta=20
  - Rate limit: 0.5s/pagina + 1.5s/download PDF

Portlet IDs (fissi, estratti dal codice sorgente della pagina):
  - Circolari:   AssetPublisherPortlet_INSTANCE_mFmHL8QS3lq4
  - Risoluzioni: AssetPublisherPortlet_INSTANCE_oF14ixF85x6o
"""
from __future__ import annotations

import asyncio
import io
import re
from datetime import date, datetime
from typing import Optional

import httpx
import pdfplumber
from bs4 import BeautifulSoup
from loguru import logger

from aiura_legal.prassi.models import (
    EmittentePrassi,
    PrassiDocument,
    RawPrassi,
    TipoPrassi,
)

# ──────────────────────────────────────────────
# Costanti
# ──────────────────────────────────────────────

_BASE = "https://www.agenziaentrate.gov.it"

_SOURCES: dict[TipoPrassi, dict] = {
    TipoPrassi.CIRCOLARE: {
        "url":        _BASE + "/portale/web/guest/normativa-e-prassi/circolari",
        "portlet_id": "com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_mFmHL8QS3lq4",
    },
    TipoPrassi.RISOLUZIONE: {
        "url":        _BASE + "/portale/web/guest/normativa-e-prassi/risoluzioni",
        "portlet_id": "com_liferay_asset_publisher_web_portlet_AssetPublisherPortlet_INSTANCE_oF14ixF85x6o",
    },
}

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9",
    "Referer": _BASE + "/portale/",
}

_PAGE_SIZE    = 20    # documenti per pagina Liferay
_MAX_PAGES    = 50    # max pagine per tipo (cap sicurezza)
_RATE_PAGE    = 0.5   # secondi tra pagine
_RATE_PDF     = 1.5   # secondi tra download PDF
_MAX_PDFS     = 300   # max PDF per run

# Regex per estrarre numero e data dal titolo
_CIRC_RE   = re.compile(
    r"(?:Circolare|Risoluzione|Risposta|Provvedimento)[^\d]*n[.\s]*(\d+(?:[/\w]*)?)"
    r".*?(\d{1,2}[/\s](?:gennaio|febbraio|marzo|aprile|maggio|giugno|"
    r"luglio|agosto|settembre|ottobre|novembre|dicembre|\d{1,2})[/\s]\d{4}"
    r"|\d{1,2}[_./]\d{1,2}[_./]\d{4})",
    re.IGNORECASE,
)
# Pattern 1: "n. 11" o "n.11" con "n" a inizio parola (es. "Circolare n. 2")
_NUMERO_RE_EXPLICIT = re.compile(r"\b[Nn][°.\s]+(\d+)", re.IGNORECASE)
# Pattern 2: "n" preceduta da underscore o spazio (es. "RIS_n_20_del...")
_NUMERO_RE_SEP      = re.compile(r"[_\s][Nn][_.\s]+(\d+)", re.IGNORECASE)
# Pattern 3: primo numero ≤3 cifre non preceduto/seguito da altra cifra
#            usato come fallback per "Risoluzionen. 11" dove n non è word boundary
_NUMERO_RE_FALLBACK = re.compile(r"(?<!\d)(\d{1,3})(?!\d)")
_DATE_PATTERNS = [
    (re.compile(r"(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|"
                r"luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})", re.I),
     "%d %m %Y"),
    (re.compile(r"(\d{1,2})[/_.](\d{1,2})[/_.](\d{4})"), "%d %m %Y"),
    (re.compile(r"(\d{1,2})[/_.](\d{1,2})[/_.](\d{2})$"), "%d %m %y"),
]
_MONTH_MAP = {
    "gennaio": "1", "febbraio": "2", "marzo": "3", "aprile": "4",
    "maggio": "5", "giugno": "6", "luglio": "7", "agosto": "8",
    "settembre": "9", "ottobre": "10", "novembre": "11", "dicembre": "12",
}

# Regex norme citate
_NORME_RE = re.compile(
    r"(?:art(?:icolo)?\.?\s*\d+(?:[,\s]+(?:comma|bis|ter|quater|quinquies)\s*\d*)*"
    r"(?:\s+(?:del\s+)?(?:D\.?Lgs\.?|D\.?P\.?R\.?|L\.|Legge)\s+[\d/]+)?)",
    re.IGNORECASE,
)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _parse_date(title: str) -> Optional[date]:
    """Estrae la data dal titolo del documento."""
    for pattern, fmt in _DATE_PATTERNS:
        m = pattern.search(title)
        if m:
            groups = list(m.groups())
            if fmt == "%d %m %Y":
                # Converti mese testuale → numero
                if any(c.isalpha() for c in groups[1]):
                    groups[1] = _MONTH_MAP.get(groups[1].lower(), groups[1])
                try:
                    return datetime.strptime(f"{groups[0]} {groups[1]} {groups[2]}", "%d %m %Y").date()
                except ValueError:
                    pass
    return None


def _extract_numero(title: str) -> str:
    """
    Estrae il numero del documento dal titolo.
    Gestisce formati eterogenei AdE:
      - "Circolare n. 2 del ..."       → "2"
      - "Risoluzione n. 20 del ..."    → "20"
      - "Risoluzionen. 11 del ..."     → "11"  (no spazio prima di n.)
      - "RIS_n_20_del_..."             → "20"
      - "Circolare n. 2/E del ..."     → "2"   (ignora suffisso /E)
    """
    m = _NUMERO_RE_EXPLICIT.search(title)
    if m:
        return m.group(1)
    m = _NUMERO_RE_SEP.search(title)
    if m:
        return m.group(1)
    # Fallback: primo numero ≤ 3 cifre (esclude anni 4 cifre)
    m = _NUMERO_RE_FALLBACK.search(title)
    return m.group(1) if m else "?"


def _extract_anno(title: str, fallback: int = 0) -> int:
    """Estrae l'anno dal titolo."""
    m = re.search(r"\b(20\d{2})\b", title)
    return int(m.group(1)) if m else fallback


def _extract_norme(testo: str) -> list[str]:
    """Estrae riferimenti normativi dal testo."""
    found = _NORME_RE.findall(testo)
    unique = list(dict.fromkeys(n.strip() for n in found))
    return unique[:50]  # cap


def _parse_pdf_text(pdf_bytes: bytes) -> str:
    """Estrae testo da PDF con pdfplumber."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            pages_text = []
            for page in pdf.pages[:30]:  # max 30 pagine
                txt = page.extract_text() or ""
                pages_text.append(txt)
            return "\n\n".join(pages_text).strip()
    except Exception as exc:
        logger.warning("PDF parse error: {}", exc)
        return ""


def _make_page_url(base_url: str, portlet_id: str, cur: int, delta: int = _PAGE_SIZE) -> str:
    p = portlet_id
    return (
        f"{base_url}"
        f"?p_p_id={p}"
        f"&p_p_lifecycle=0"
        f"&_{p}_cur={cur}"
        f"&_{p}_delta={delta}"
    )


# ──────────────────────────────────────────────
# Scraper
# ──────────────────────────────────────────────

class AgenziaEntrateScraper:
    """
    Scarica circolari e risoluzioni dall'Agenzia delle Entrate.
    Usa httpx diretto (no Playwright) — la paginazione è server-side.
    """

    def __init__(self) -> None:
        self._http: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "AgenziaEntrateScraper":
        self._http = httpx.AsyncClient(
            headers=_HEADERS,
            verify=False,
            follow_redirects=True,
            timeout=httpx.Timeout(30.0),
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    # ── Public API ──────────────────────────────

    async def fetch_since(
        self,
        since: date,
        tipi: list[TipoPrassi] | None = None,
        max_pdfs: int = _MAX_PDFS,
    ) -> list[PrassiDocument]:
        """
        Scarica tutti i documenti pubblicati dopo `since`.

        Args:
            since:    data di taglio (incluso)
            tipi:     tipi di documento da scaricare (default: circolari + risoluzioni)
            max_pdfs: cap sul numero di PDF da scaricare
        """
        if tipi is None:
            tipi = [TipoPrassi.CIRCOLARE, TipoPrassi.RISOLUZIONE]

        results: list[PrassiDocument] = []
        pdf_count = 0

        for tipo in tipi:
            if tipo not in _SOURCES:
                logger.warning("Tipo {} non supportato — skip", tipo.value)
                continue

            logger.info("AgE {}: scarico dal {}", tipo.value, since)
            raws = await self._fetch_list(tipo, since)
            logger.info("AgE {}: {} documenti nella lista", tipo.value, len(raws))

            for raw in raws:
                if pdf_count >= max_pdfs:
                    logger.warning("AgE: cap max_pdfs={} raggiunto", max_pdfs)
                    break

                doc = await self._download_and_parse(raw)
                if doc and doc.testo:
                    results.append(doc)
                    pdf_count += 1
                    logger.debug(
                        "AgE {}: {} → {} chars testo, {} norme",
                        tipo.value, doc.riferimento, len(doc.testo), len(doc.norme_citate),
                    )

        logger.success("AgE: {} documenti totali scaricati (pdf_count={})", len(results), pdf_count)
        return results

    # ── Internal ────────────────────────────────

    async def _fetch_list(self, tipo: TipoPrassi, since: date) -> list[RawPrassi]:
        """Recupera la lista paginata di documenti per il tipo dato."""
        source = _SOURCES[tipo]
        base_url    = source["url"]
        portlet_id  = source["portlet_id"]
        raws: list[RawPrassi] = []
        seen_ids: set[str] = set()

        for page_num in range(1, _MAX_PAGES + 1):
            await asyncio.sleep(_RATE_PAGE)
            url = _make_page_url(base_url, portlet_id, cur=page_num)

            try:
                resp = await self._http.get(url)
                resp.raise_for_status()
            except Exception as exc:
                logger.error("AgE {}: fetch pagina {} fallito — {}", tipo.value, page_num, exc)
                break

            page_raws, stop = self._parse_list_page(resp.text, tipo, since, seen_ids)
            raws.extend(page_raws)

            if stop:
                logger.debug("AgE {}: data di taglio raggiunta a pagina {}", tipo.value, page_num)
                break
            if not page_raws:
                logger.debug("AgE {}: pagina {} vuota — fine lista", tipo.value, page_num)
                break

        return raws

    def _parse_list_page(
        self,
        html: str,
        tipo: TipoPrassi,
        since: date,
        seen_ids: set[str],
    ) -> tuple[list[RawPrassi], bool]:
        """
        Parsa una pagina di lista.
        Restituisce (lista_raws, stop) dove stop=True se abbiamo superato `since`.
        """
        soup = BeautifulSoup(html, "html.parser")
        raws: list[RawPrassi] = []
        stop = False

        for el in soup.find_all(attrs={"data-analytics-asset-id": True}):
            asset_id = el.get("data-analytics-asset-id", "")
            title    = el.get("data-analytics-asset-title", "").strip()

            # Salta elementi non-documento (es. "Le ultime circolari", "hr")
            if not title or not any(c.isdigit() for c in title):
                continue
            if asset_id in seen_ids:
                continue
            seen_ids.add(asset_id)

            # Estrai data dal titolo
            doc_date = _parse_date(title)
            if doc_date and doc_date < since:
                stop = True
                continue  # continua a parsare la pagina (ordine non garantito)

            # Trova PDF link
            pdf_url: Optional[str] = None
            for a in el.find_all("a", href=True):
                href = a["href"]
                if ".pdf" in href.lower() or "/documents/" in href.lower():
                    pdf_url = href if href.startswith("http") else f"https://www.agenziaentrate.gov.it{href}"
                    break

            numero = _extract_numero(title)
            anno   = doc_date.year if doc_date else _extract_anno(title)

            raw = RawPrassi(
                tipo=tipo,
                emittente=EmittentePrassi.AGENZIA_ENTRATE,
                numero=numero,
                anno=anno,
                titolo=title,
                source_url=_SOURCES[tipo]["url"],
                pdf_url=pdf_url,
                data_emissione=doc_date,
                asset_id=asset_id,
            )
            raws.append(raw)

        return raws, stop

    async def _download_and_parse(self, raw: RawPrassi) -> Optional[PrassiDocument]:
        """Scarica il PDF e restituisce un PrassiDocument."""
        from datetime import datetime as dt

        if not raw.pdf_url:
            logger.debug("AgE: nessun PDF per '{}' — skip", raw.titolo[:40])
            return None

        await asyncio.sleep(_RATE_PDF)
        try:
            resp = await self._http.get(raw.pdf_url)
            resp.raise_for_status()
            pdf_bytes = resp.content
        except Exception as exc:
            logger.warning("AgE: download PDF fallito '{}' — {}", raw.titolo[:40], exc)
            return None

        testo = _parse_pdf_text(pdf_bytes)
        if not testo:
            logger.warning("AgE: PDF vuoto per '{}'", raw.titolo[:40])
            return None

        norme = _extract_norme(testo)
        data  = raw.data_emissione or date.today()

        return PrassiDocument(
            tipo=raw.tipo,
            emittente=raw.emittente,
            numero=raw.numero,
            anno=raw.anno,
            data_emissione=data,
            titolo=raw.titolo,
            testo=testo,
            norme_citate=norme,
            source_url=raw.source_url,
            pdf_url=raw.pdf_url or "",
            ingested_at=dt.utcnow().isoformat(),
        )
