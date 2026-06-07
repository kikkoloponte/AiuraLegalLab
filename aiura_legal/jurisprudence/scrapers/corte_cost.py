"""
Scraper Corte Costituzionale — cortecostituzionale.it
Bot protection attiva: richiede browser reale.
Ricerca per anno con paginazione.
"""
from __future__ import annotations

import re
from datetime import date

from loguru import logger
from playwright.async_api import Page

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza
from aiura_legal.jurisprudence.scrapers.base import BaseScraper, ScraperError

_SEARCH_URL = "https://www.cortecostituzionale.it/actionPronuncia.do"
_BASE_URL = "https://www.cortecostituzionale.it"
_MAX_PAGES = 30


class CorteCostScraper(BaseScraper):
    organo = OrganoGiudicante.CORTE_COST
    rate_limit_seconds = 2.0

    async def fetch_since(self, since: date) -> list[RawSentenza]:
        results: list[RawSentenza] = []

        for anno in range(since.year, date.today().year + 1):
            page = await self.new_page()
            try:
                year_results = await self._fetch_year(page, anno, since)
                results.extend(year_results)
                logger.info("CorteCost {}: {} pronunce", anno, len(year_results))
            except ScraperError as exc:
                logger.error("CorteCost {}: {}", anno, exc)
            finally:
                await page.close()

        logger.info("CorteCost totale: {} pronunce (since {})", len(results), since)
        return results

    async def _fetch_year(self, page: Page, anno: int, since: date) -> list[RawSentenza]:
        results: list[RawSentenza] = []
        await self._navigate(page, _SEARCH_URL)

        # Compila form ricerca per anno
        try:
            await page.select_option("select[name='annoDecisione'], #annoDecisione", str(anno))
        except Exception:
            try:
                await page.fill("input[name='annoDecisione']", str(anno))
            except Exception:
                logger.debug("CorteCost: campo anno non trovato per {}", anno)
                return results

        try:
            await page.select_option("select[name='tipoProvvedimento']", "S")
        except Exception:
            pass

        # Submit
        try:
            await page.click("input[type='submit'], button[type='submit']")
            await page.wait_for_selector("table, .result, .pronunce-list", timeout=15_000)
        except Exception as exc:
            logger.debug("CorteCost {}: submit fallito — {}", anno, exc)
            return results

        # Pagina per pagina
        for _ in range(_MAX_PAGES):
            rows = await self._extract_rows(page)
            for row in rows:
                raw = self._row_to_raw(row, anno, since)
                if raw:
                    results.append(raw)

            if not await self._next_page(page):
                break

        return results

    async def _extract_rows(self, page: Page) -> list[dict]:
        rows = []
        try:
            # Cerca righe tabella risultati
            tr_list = await page.query_selector_all("table tr:not(:first-child), .result-row, li.pronunce")
            for tr in tr_list:
                text = await tr.inner_text()
                link_el = await tr.query_selector("a[href]")
                href = await link_el.get_attribute("href") if link_el else ""
                rows.append({"text": text.strip(), "href": href or ""})
        except Exception:
            pass
        return rows

    def _row_to_raw(self, row: dict, anno: int, since: date) -> RawSentenza | None:
        text = row["text"]
        href = row["href"]
        if not text:
            return None

        numero = self._extract_numero(text)
        if not numero:
            return None

        url = href if href.startswith("http") else (_BASE_URL + href if href else _SEARCH_URL)
        return RawSentenza(
            numero=numero,
            anno=anno,
            organo=self.organo,
            source_url=url,
            raw_html=text,
        )

    def _extract_numero(self, text: str) -> str:
        m = re.search(r"\b(\d{1,4})\b", text)
        return m.group(1) if m else ""

    async def _next_page(self, page: Page) -> bool:
        try:
            btn = await page.query_selector(
                "a:has-text('Successivo'), a:has-text('>'), .pagination-next:not(.disabled), "
                "a[rel='next']"
            )
            if btn and await btn.is_enabled():
                await btn.click()
                await page.wait_for_selector("table tr, .result-row", timeout=8_000)
                return True
        except Exception:
            pass
        return False
