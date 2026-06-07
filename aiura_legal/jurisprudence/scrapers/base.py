"""
Contratto base per tutti gli scraper giurisprudenziali.
Usa Playwright (browser headless) per portali con bot protection, JS rendering,
VIEWSTATE e altri meccanismi che rendono inefficace il semplice HTTP.
"""
from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from datetime import date

from loguru import logger
from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from aiura_legal.jurisprudence.models import OrganoGiudicante, RawSentenza


class ScraperError(Exception):
    pass


class BaseScraper(ABC):
    organo: OrganoGiudicante
    rate_limit_seconds: float = 1.5
    _headless: bool = True

    def __init__(self) -> None:
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    async def __aenter__(self) -> "BaseScraper":
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self._headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="it-IT",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            ignore_https_errors=True,
        )
        return self

    async def __aexit__(self, *_: object) -> None:
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._pw:
            await self._pw.stop()
        self._context = self._browser = self._pw = None

    async def new_page(self) -> Page:
        if self._context is None:
            raise RuntimeError("Usare come context manager: async with scraper:")
        return await self._context.new_page()

    @abstractmethod
    async def fetch_since(self, since: date) -> list[RawSentenza]:
        """Scarica tutte le sentenze pubblicate dopo `since`."""

    async def _navigate(self, page: Page, url: str, wait_for: str = "domcontentloaded") -> None:
        await asyncio.sleep(self.rate_limit_seconds)
        try:
            await page.goto(url, wait_until=wait_for, timeout=30_000)
        except Exception as exc:
            raise ScraperError(f"Navigazione fallita: {url} — {exc}") from exc

    async def _safe_text(self, page: Page, selector: str, default: str = "") -> str:
        try:
            el = await page.query_selector(selector)
            return (await el.inner_text()).strip() if el else default
        except Exception:
            return default

    async def _safe_attr(self, page: Page, selector: str, attr: str, default: str = "") -> str:
        try:
            el = await page.query_selector(selector)
            val = await el.get_attribute(attr) if el else None
            return val.strip() if val else default
        except Exception:
            return default
