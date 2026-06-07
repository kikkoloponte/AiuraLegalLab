"""
wiki_bootstrap.py — seed one-shot della wiki da normattiva_docs.

Legge gli articoli normativi da legal_lab (READ-ONLY) e crea una pagina
wiki per ogni articolo con testo_tipo=normativo. Non chiama Ollama:
il body_md iniziale è il testo verbatim dell'articolo.

Uso:
    python scripts/wiki_bootstrap.py --workspace mio-studio --limit 500
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

import motor.motor_asyncio
from loguru import logger

from aiura_legal.wiki.store import WikiPage, WikiStore
from aiura_legal.wiki.writer import slugify

_SOURCE_URI = "mongodb://localhost:27017"
_SOURCE_DB = "legal_lab"
_TARGET_DB = "aiura_legal"
_SOURCE_COLLECTION = "normattiva_docs"


async def bootstrap(workspace: str, limit: int) -> None:
    client = motor.motor_asyncio.AsyncIOMotorClient(_SOURCE_URI)
    source_db = client[_SOURCE_DB]
    target_db = client[_TARGET_DB]

    store = WikiStore(target_db)
    await store.ensure_indexes()

    query = {"testo_tipo": "normativo"}
    cursor = source_db[_SOURCE_COLLECTION].find(query).limit(limit)

    created = 0
    skipped = 0

    async for doc in cursor:
        titolo = doc.get("titolo_articolo") or doc.get("titolo") or doc.get("articolo_num", "")
        if not titolo:
            skipped += 1
            continue

        slug = slugify(titolo)
        if not slug:
            skipped += 1
            continue

        existing = await store.get_page(slug, workspace)
        if existing is not None:
            skipped += 1
            continue

        urn = doc.get("urn", "")
        body_md = _build_initial_body(doc)

        page = WikiPage(
            slug=slug,
            title=titolo,
            body_md=body_md,
            sources=[urn] if urn else [],
            query_count=0,
            last_updated=datetime.now(timezone.utc),
            version=1,
            workspace=workspace,
        )
        await store.save_page(page)
        created += 1

        if created % 50 == 0:
            logger.info(f"Bootstrap progress: {created} created, {skipped} skipped")

    logger.info(f"Bootstrap done: {created} pages created, {skipped} skipped")
    client.close()


def _build_initial_body(doc: dict) -> str:
    titolo = doc.get("titolo", "")
    titolo_art = doc.get("titolo_articolo", "")
    art_num = doc.get("articolo_num", "")
    testo = doc.get("text", "")
    urn = doc.get("urn", "")

    header = " — ".join(filter(None, [titolo, art_num, titolo_art]))

    body = f"""\
## Sintesi
{header}

## Testo normativo
{testo}

## Principi chiave
- Da definire tramite query

## Evoluzione normativa
- Da definire tramite query

## Casi applicativi
- Da definire tramite query

## Fonti
"""
    if urn:
        body += f"- {urn}\n"

    return body.strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed wiki da normattiva_docs")
    parser.add_argument("--workspace", default="default", help="Workspace target")
    parser.add_argument("--limit", type=int, default=500, help="Max documenti da processare")
    args = parser.parse_args()

    logger.info(f"Starting wiki bootstrap: workspace={args.workspace} limit={args.limit}")
    asyncio.run(bootstrap(args.workspace, args.limit))


if __name__ == "__main__":
    main()
