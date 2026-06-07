"""
WikiStore — CRUD async su MongoDB collection wiki_pages.
Zero logica di business: solo lettura/scrittura.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase


@dataclass
class WikiPage:
    slug: str
    title: str
    body_md: str
    sources: list[str] = field(default_factory=list)
    query_count: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 0
    workspace: str = "default"


_COLLECTION = "wiki_pages"


class WikiStore:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._col = db[_COLLECTION]

    async def ensure_indexes(self) -> None:
        await self._col.create_index(
            [("slug", 1), ("workspace", 1)], unique=True
        )
        await self._col.create_index("last_updated")
        await self._col.create_index("sources")
        logger.debug("WikiStore indexes ensured")

    async def get_page(self, slug: str, workspace: str) -> Optional[WikiPage]:
        doc = await self._col.find_one({"slug": slug, "workspace": workspace})
        if doc is None:
            return None
        return _doc_to_page(doc)

    async def save_page(self, page: WikiPage) -> None:
        doc = _page_to_doc(page)
        await self._col.update_one(
            {"slug": page.slug, "workspace": page.workspace},
            {"$set": doc},
            upsert=True,
        )
        logger.debug(f"WikiStore saved page slug={page.slug} v={page.version}")

    async def list_stale(self, days: int, workspace: str) -> list[WikiPage]:
        cutoff = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        from datetime import timedelta
        cutoff = cutoff - timedelta(days=days)
        cursor = self._col.find(
            {"workspace": workspace, "last_updated": {"$lt": cutoff}}
        )
        return [_doc_to_page(d) async for d in cursor]

    async def search_by_urn(self, urn: str, workspace: str) -> list[WikiPage]:
        cursor = self._col.find({"workspace": workspace, "sources": urn})
        return [_doc_to_page(d) async for d in cursor]

    async def list_all(self, workspace: str) -> list[WikiPage]:
        cursor = self._col.find({"workspace": workspace})
        return [_doc_to_page(d) async for d in cursor]


def _page_to_doc(page: WikiPage) -> dict:
    return {
        "slug": page.slug,
        "title": page.title,
        "body_md": page.body_md,
        "sources": page.sources,
        "query_count": page.query_count,
        "last_updated": page.last_updated,
        "version": page.version,
        "workspace": page.workspace,
    }


def _doc_to_page(doc: dict) -> WikiPage:
    return WikiPage(
        slug=doc["slug"],
        title=doc["title"],
        body_md=doc["body_md"],
        sources=doc.get("sources", []),
        query_count=doc.get("query_count", 0),
        last_updated=doc.get("last_updated", datetime.now(timezone.utc)),
        version=doc.get("version", 0),
        workspace=doc.get("workspace", "default"),
    )
