"""
Scraper Giustizia Amministrativa — giustizia-amministrativa.it
Portale Liferay: portlet Decisioni e Pareri su /web/guest/dcsnprr.
Gestisce TAR e Consiglio di Stato nella stessa interfaccia.

Meccanismo: riempie il campo di testo del portlet (ricerca broad) + click Cerca
→ navigazione SPA → risultati in <article> con "numero provv.".
"""
from __future__ import annotations

import asyncio
import re
from datetime import date

from loguru import logger
from playwright.async_api import Page

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza
from aiura_legal.jurisprudence.scrapers.base import BaseScraper, ScraperError

_BASE_URL = "https://www.giustizia-amministrativa.it"
_SEARCH_URL = f"{_BASE_URL}/web/guest/dcsnprr"
_P = "_decisioni_pareri_web_DecisioniPareriWebPortlet_INSTANCE_XKc17mrB8J10_"
_MAX_PAGES = 200   # aumentato per caricamento storico (era 50)

# Termini per coprire le principali materie del diritto amministrativo italiano.
# Ogni termine produce una ricerca separata paginata — il dedup avviene
# nel coordinator tramite hash id (organo+numero+anno).
_SEARCH_TERMS = [
    "ricorso",           # termine più broad — copre la maggior parte
    "appalti",           # contratti pubblici, gare
    "urbanistica",       # permessi di costruire, piani regolatori
    "personale",         # pubblico impiego, concorsi
    "espropriazione",    # procedimenti espropriativi
    "silenzio",          # silenzio-inadempimento, silenzio-assenso
    "annullamento",      # annullamento in autotutela
    "accesso",           # accesso agli atti (legge 241/1990)
    "immigrazione",      # protezione internazionale, permessi soggiorno
    "ambiente",          # VIA, AIA, autorizzazioni ambientali
]


class GiustiziaAmmScraper(BaseScraper):
    organo = OrganoGiudicante.TAR
    rate_limit_seconds = 2.0

    async def fetch_since(self, since: date) -> list[RawSentenza]:
        all_results: list[RawSentenza] = []
        # Dedup per id (organo+numero+anno) tra termini diversi
        seen_ids: set[str] = set()

        for term in _SEARCH_TERMS:
            try:
                term_results = await asyncio.wait_for(
                    self._fetch_term(term, since, seen_ids),
                    timeout=300,  # 5 minuti max per termine
                )
            except asyncio.TimeoutError:
                logger.warning("GiustiziaAmm term='{}': timeout 5min — saltato", term)
                term_results = []
            all_results.extend(term_results)
            logger.info("GiustiziaAmm term='{}': {} sentenze", term, len(term_results))

        logger.info("GiustiziaAmm totale: {} sentenze uniche (since {})", len(all_results), since)
        return all_results

    async def _fetch_term(
        self, term: str, since: date, seen_ids: set[str]
    ) -> list[RawSentenza]:
        results: list[RawSentenza] = []
        page = await self.new_page()

        try:
            await self._navigate(page, _SEARCH_URL, wait_for="domcontentloaded")
            await page.wait_for_timeout(2000)
            await self._fill_and_search(page, term)

            for _ in range(_MAX_PAGES):
                items = await self._extract_items(page)
                if not items:
                    break

                any_older = False
                for item in items:
                    raw = self._item_to_raw(item)
                    if raw:
                        if raw.anno < since.year:
                            any_older = True
                            continue
                        raw_key = f"{raw.organo.value}:{raw.numero}:{raw.anno}"
                        if raw_key not in seen_ids:
                            seen_ids.add(raw_key)
                            results.append(raw)

                if any_older:
                    break
                if not await self._next_page(page):
                    break

        except ScraperError as exc:
            logger.error("GiustiziaAmm term='{}': {}", term, exc)
        except Exception as exc:
            logger.error("GiustiziaAmm term='{}' inatteso: {}", term, exc)
        finally:
            await page.close()

        return results

    async def _fill_and_search(self, page: Page, term: str = _SEARCH_TERMS[0]) -> None:
        try:
            field_id = f"{_P}searchtextProvvedimenti"
            await page.fill(f"input[id='{field_id}']", term)
            await page.evaluate("""
                () => {
                    var cerca = Array.from(document.querySelectorAll('button'))
                        .find(b => b.textContent.trim() === 'Cerca');
                    if (cerca) cerca.click();
                }
            """)
            # Attende navigazione SPA con i risultati
            await page.wait_for_url(
                lambda url: "javax.portlet.action=search" in url,
                timeout=15_000,
            )
            await page.wait_for_timeout(2000)
        except Exception as exc:
            logger.debug("GiustiziaAmm fill_and_search: {}", exc)

    async def _extract_items(self, page: Page) -> list[dict]:
        items = []
        try:
            articles = await page.query_selector_all("article")
            for art in articles:
                text = await art.inner_text()
                if not text.strip():
                    continue
                link_el = await art.query_selector("a[href*='web/guest']")
                href = await link_el.get_attribute("href") if link_el else ""
                items.append({"text": text.strip(), "href": href or "", "html": await art.inner_html()})
        except Exception:
            pass
        return items

    def _item_to_raw(self, item: dict) -> RawSentenza | None:
        text = item["text"]
        href = item["href"]

        # Formato: "202610170 (ROMA, SEZIONE 1) html\nSENTENZA sede di ROMA..."
        # oppure: "numero provv.: 202610170"
        numero = self._extract_numero(text)
        anno = self._extract_anno(text) or date.today().year
        if not numero:
            return None

        organo = OrganoGiudicante.CONSIGLIO_STATO if "consiglio" in text.lower() else OrganoGiudicante.TAR
        url = href if href.startswith("http") else (_BASE_URL + href if href else _SEARCH_URL)

        return RawSentenza(
            numero=numero,
            anno=anno,
            organo=organo,
            source_url=url,
            raw_html=f"<article>{item['html']}</article>",
        )

    def _extract_numero(self, text: str) -> str:
        # "numero provv.: 202610170" oppure "202610170 (ROMA"
        m = re.search(r"numero\s+provv\.?:?\s*(\d{6,10})", text, re.IGNORECASE)
        if m:
            return m.group(1)
        m2 = re.search(r"^(\d{6,10})\s*\(", text)
        if m2:
            return m2.group(1)
        return ""

    def _extract_anno(self, text: str) -> int | None:
        # Il numero provvedimento inizia con l'anno (20261234 → 2026)
        m = re.search(r"\b(20\d{2})\d{4,}\b", text)
        if m:
            return int(m.group(1))
        m2 = re.search(r"\b(20\d{2})\b", text)
        return int(m2.group(1)) if m2 else None

    async def _next_page(self, page: Page) -> bool:
        try:
            # Liferay portlet: paginazione via link "Successiva" o freccia destra
            btn = await page.query_selector(
                f"a[href*='{_P}cur='], "
                "a:has-text('Successiva'), "
                ".pagination li:last-child a:not([aria-disabled='true']), "
                "a[rel='next']"
            )
            if btn:
                disabled = await btn.get_attribute("aria-disabled") or ""
                if disabled.lower() == "true":
                    return False
                href = await btn.get_attribute("href") or ""
                if href:
                    # Navigazione diretta all'URL pagina successiva
                    full_url = href if href.startswith("http") else _BASE_URL + href
                    await self._navigate(page, full_url, wait_for="domcontentloaded")
                    await page.wait_for_timeout(2000)
                else:
                    await btn.click()
                    await page.wait_for_timeout(3000)
                return True
        except Exception:
            pass
        return False
