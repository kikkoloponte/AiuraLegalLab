"""
WikiLinter — health check della wiki.
Genera un LintReport senza modificare dati.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from aiura_legal.wiki.store import WikiPage, WikiStore

_STALE_DAYS = 30
_MIN_BODY_CHARS = 50
_NORMATTIVA_COLLECTION = "normattiva_docs"


@dataclass
class LintReport:
    stale_pages: list[str] = field(default_factory=list)
    empty_bodies: list[str] = field(default_factory=list)
    orphan_urns: list[tuple[str, str]] = field(default_factory=list)
    total_pages: int = 0

    def summary(self) -> str:
        lines = [
            f"Totale pagine: {self.total_pages}",
            f"Pagine stale (>{_STALE_DAYS}gg): {len(self.stale_pages)}",
            f"Pagine con body vuoto: {len(self.empty_bodies)}",
            f"URN orfani: {len(self.orphan_urns)}",
        ]
        return "\n".join(lines)


class WikiLinter:
    def __init__(self, wiki_store: WikiStore, source_db: AsyncIOMotorDatabase) -> None:
        self._store = wiki_store
        self._source_db = source_db

    async def run(self, workspace: str = "default") -> LintReport:
        report = LintReport()
        pages = await self._store.list_all(workspace)
        report.total_pages = len(pages)

        stale = await self._store.list_stale(_STALE_DAYS, workspace)
        report.stale_pages = [p.slug for p in stale]

        report.empty_bodies = [
            p.slug for p in pages if len(p.body_md.strip()) < _MIN_BODY_CHARS
        ]

        report.orphan_urns = await self._find_orphan_urns(pages)

        logger.info(f"WikiLinter completed: {report.summary()}")
        return report

    async def _find_orphan_urns(
        self, pages: list[WikiPage]
    ) -> list[tuple[str, str]]:
        """Trova URN nelle pagine wiki che non esistono in normattiva_docs."""
        all_urns: list[tuple[str, str]] = []
        for page in pages:
            for urn in page.sources:
                exists = await self._source_db[_NORMATTIVA_COLLECTION].find_one(
                    {"urn": urn}, {"_id": 1}
                )
                if exists is None:
                    all_urns.append((page.slug, urn))
        return all_urns
