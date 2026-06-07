"""
Scraper Corte dei Conti — corteconti.it/Home/Documenti/Sentenze
API diretta CdcWebApi: richiede Settings + IdModulo dalla pagina, poi POST JSON.
Per ogni sentenza reale (titolo "Sentenza n. X" / "Ordinanza n. X") scarica
il PDF dalla pagina di dettaglio — il testo completo è solo lì.
"""
from __future__ import annotations

import asyncio
import re
from datetime import date, datetime, timezone

import httpx
from bs4 import BeautifulSoup
from loguru import logger

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza
from aiura_legal.jurisprudence.scrapers.base import BaseScraper

_BASE_URL = "https://www.corteconti.it"
_SENTENZE_URL = f"{_BASE_URL}/Home/Documenti/Sentenze"
_API_URL = f"{_BASE_URL}/DesktopModules/CdcWebApi/API/document/Search"
_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": _SENTENZE_URL,
    "Content-Type": "application/json; charset=utf-8",
    "X-Requested-With": "XMLHttpRequest",
}
_PAGE_SIZE = 10
_MAX_PAGES = 300          # 3000 doc max per scansione (archivio ~2477/anno)
_MAX_PDFS_PER_RUN = 500   # cap sicurezza per non scaricare troppi PDF in un sync
_SCAN_RATE = 0.3          # secondi tra chiamate lista (leggere, solo JSON)
_PDF_RATE = 1.5           # secondi tra download PDF (più pesanti)

# Solo sentenze/ordinanze/decreti con numero esplicito.
# Esclude: "Comunicato Stampa", "Ruolo udienza", "Concorso pubblico", ecc.
_REAL_SENTENZA_RE = re.compile(
    r"^(Sentenza|Ordinanza|Decreto|Decisione)\s+n\.?\s*(\d+)",
    re.IGNORECASE,
)

# Formato numero: "5/2026/EL" oppure "5/2026" oppure solo "5"
_NUMERO_RE = re.compile(
    r"n\.?\s*(\d+)(?:/(\d{4}))?(?:/([A-Z]+))?",
    re.IGNORECASE,
)


class CorteContiScraper(BaseScraper):
    organo = OrganoGiudicante.CORTE_CONTI
    rate_limit_seconds = 1.5

    # Override: usa httpx direttamente (no Playwright)
    async def __aenter__(self) -> "CorteContiScraper":
        self._http = httpx.AsyncClient(
            verify=False,
            headers=_HEADERS,
            timeout=httpx.Timeout(60.0),
            follow_redirects=True,
        )
        return self  # type: ignore[return-value]

    async def __aexit__(self, *_: object) -> None:
        if self._http:
            await self._http.aclose()
            self._http = None

    async def fetch_since(self, since: date) -> list[RawSentenza]:
        results: list[RawSentenza] = []

        settings, id_modulo = await self._get_module_params()
        if not settings:
            logger.error("CorteConti: impossibile ottenere Settings dal modulo")
            return results

        pdf_count = 0
        stop = False

        for page_num in range(1, _MAX_PAGES + 1):
            if stop:
                break
            await asyncio.sleep(_SCAN_RATE)

            try:
                payload = self._build_payload(since, page_num, settings, id_modulo)
                resp = await self._http.post(_API_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
            except Exception as exc:
                logger.error("CorteConti API page {}: {}", page_num, exc)
                break

            html_fragment = data.get("Html", "")
            total_rows = data.get("Rows", 0)
            if not html_fragment:
                break

            # Conta i card totali nella pagina (non solo i match) per sapere se è finita
            total_page_cards = html_fragment.count("card-wrapper")
            if total_page_cards == 0:
                break

            matching_cards = self._parse_cards(html_fragment)

            logger.debug(
                "CorteConti: pag {} — {} card totali, {} match sentenze, {} PDF finora",
                page_num, total_page_cards, len(matching_cards), len(results),
            )

            for card in matching_cards:
                title, detail_url, card_anno = card
                # Stop se troviamo doc più vecchi di since
                if card_anno and card_anno < since.year:
                    stop = True
                    break

                if pdf_count >= _MAX_PDFS_PER_RUN:
                    logger.warning("CorteConti: raggiunto limite {} PDF/run", _MAX_PDFS_PER_RUN)
                    stop = True
                    break

                # Scarica PDF dal detail page
                await asyncio.sleep(_PDF_RATE - _SCAN_RATE)  # extra wait per PDF
                raw = await self._fetch_sentenza(title, detail_url)
                if raw:
                    results.append(raw)
                    pdf_count += 1

            # Pagina incompleta = fine dei risultati
            if total_page_cards < _PAGE_SIZE:
                break

        logger.info("CorteConti: {} sentenze con PDF (since {})", len(results), since)
        return results

    # ── Parametri modulo ─────────────────────────────────────────────────

    async def _get_module_params(self) -> tuple[str, str]:
        try:
            resp = await self._http.get(_SENTENZE_URL)
            html = resp.text
            settings_m = re.search(r'id="[^"]*HF_Settings[^"]*"\s+value="([^"]*)"', html)
            idmodulo_m = re.search(r'id="[^"]*HF_IdModulo[^"]*"\s+value="([^"]*)"', html)
            settings = settings_m.group(1) if settings_m else ""
            id_modulo = idmodulo_m.group(1) if idmodulo_m else ""
            return settings, id_modulo
        except Exception as exc:
            logger.error("CorteConti get_module_params: {}", exc)
            return "", ""

    def _build_payload(
        self, since: date, page_num: int, settings: str, id_modulo: str
    ) -> dict:
        dal = datetime(since.year, since.month, since.day, tzinfo=timezone.utc)
        al = datetime.now(timezone.utc)
        return {
            "Filters": [
                {
                    "PropertyName": "DataElemento",
                    "Operation": "GreaterThanOrEqual",
                    "Value": dal.isoformat(),
                    "Predicate": "And",
                },
                {
                    "PropertyName": "DataElemento",
                    "Operation": "LessThanOrEqual",
                    "Value": al.isoformat(),
                    "Predicate": "And",
                },
            ],
            "ResultParams": {
                "pageNumber": page_num,
                "sortField": "DataElemento",
                "idModuleType": 1444,
                "pageSize": _PAGE_SIZE,
            },
            "Settings": settings,
            "IdModulo": id_modulo,
        }

    # ── Parsing card HTML ─────────────────────────────────────────────────

    def _parse_cards(self, html: str) -> list[tuple[str, str, int | None]]:
        """Ritorna lista di (title, detail_url, anno) — solo sentenze reali."""
        cards = []
        soup = BeautifulSoup(html, "html.parser")
        for wrapper in soup.find_all("div", class_="card-wrapper"):
            h3 = wrapper.find("h3")
            if not h3:
                continue
            title = h3.get_text(strip=True)
            if not _REAL_SENTENZA_RE.match(title):
                continue  # salta ruoli, concorsi, comunicati, ecc.

            link = wrapper.find("a", href=lambda h: h and "Dettaglio" in h)
            if not link:
                continue
            detail_url = link["href"]
            if not detail_url.startswith("http"):
                detail_url = _BASE_URL + detail_url

            # Anno dalla data nella card
            date_el = wrapper.find("span", class_="data")
            anno = self._extract_anno(date_el.get_text(strip=True) if date_el else "")

            cards.append((title, detail_url, anno))
        return cards

    # ── Detail page + PDF ─────────────────────────────────────────────────

    async def _fetch_sentenza(self, title: str, detail_url: str) -> RawSentenza | None:
        """Visita il detail page, scarica il PDF, ritorna RawSentenza."""
        try:
            await asyncio.sleep(0.3)
            resp = await self._http.get(detail_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Cerca link PDF (pattern /Download?id=...)
            pdf_url = self._find_pdf_url(soup)
            if not pdf_url:
                logger.debug("CorteConti: nessun PDF in {}", detail_url)
                return None

            # Scarica PDF
            pdf_resp = await self._http.get(pdf_url)
            pdf_resp.raise_for_status()
            pdf_bytes = pdf_resp.content
            if len(pdf_bytes) < 500:
                return None

            # Estrae numero/anno dal titolo "Sentenza n. 5/2026/EL"
            numero, anno = self._parse_numero_anno(title)
            data_dep = self._extract_date_from_detail(soup)

            return RawSentenza(
                numero=numero,
                anno=anno,
                organo=self.organo,
                source_url=detail_url,
                raw_pdf_bytes=pdf_bytes,
                data_deposito=data_dep,
            )

        except Exception as exc:
            logger.warning("CorteConti fetch_sentenza '{}': {}", title, exc)
            return None

    def _find_pdf_url(self, soup: BeautifulSoup) -> str:
        """Trova l'URL del PDF nella pagina di dettaglio."""
        # Pattern principale: /Download?id=<uuid>
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/Download" in href and "id=" in href:
                return href if href.startswith("http") else _BASE_URL + href
        # Fallback: link .pdf diretto
        for a in soup.find_all("a", href=True):
            if a["href"].lower().endswith(".pdf"):
                h = a["href"]
                return h if h.startswith("http") else _BASE_URL + h
        return ""

    def _extract_date_from_detail(self, soup: BeautifulSoup) -> date | None:
        """Estrae data deposito dal detail page."""
        span = soup.find("span", class_="data")
        if span:
            return self._parse_date(span.get_text(strip=True))
        return None

    # ── Helpers ──────────────────────────────────────────────────────────

    def _parse_numero_anno(self, title: str) -> tuple[str, int]:
        """'Sentenza n. 5/2026/EL' → ('5', 2026)."""
        m = _NUMERO_RE.search(title)
        if m:
            numero = m.group(1)
            anno = int(m.group(2)) if m.group(2) else date.today().year
            sezione = m.group(3) or ""
            if sezione:
                numero = f"{numero}/{sezione}"
            return numero, anno
        return re.sub(r"\s+", "_", title[:20]), date.today().year

    def _extract_numero(self, text: str) -> str:
        """Estrae il numero di sentenza da stringhe tipo 'Sentenza n. 789/2024'."""
        m = re.search(r"\b(?:n\.?\s*)?(\d+)\s*/\s*\d{4}\b", text)
        return m.group(1) if m else ""

    def _extract_anno(self, text: str) -> int | None:
        m = re.search(r"\b(20\d{2})\b", text)
        return int(m.group(1)) if m else None

    def _parse_date(self, text: str) -> date | None:
        """Parsa date tipo '20/05/2026' o '2026-05-20'."""
        m = re.search(r"(\d{1,2})[/\-](\d{1,2})[/\-](20\d{2})", text)
        if m:
            try:
                return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
            except ValueError:
                pass
        m2 = re.search(r"(20\d{2})[/\-](\d{1,2})[/\-](\d{1,2})", text)
        if m2:
            try:
                return date(int(m2.group(1)), int(m2.group(2)), int(m2.group(3)))
            except ValueError:
                pass
        return None
