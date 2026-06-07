"""
wiki_export.py — esporta wiki_pages da MongoDB come file markdown su disco.

Struttura output:
    workspaces/<workspace>/wiki/
        index.md                  ← catalogo di tutte le pagine
        <slug>.md                 ← una pagina per concetto

Uso:
    python scripts/wiki_export.py --workspace mio-studio
    python scripts/wiki_export.py --workspace mio-studio --out-dir C:/mia/cartella
    python scripts/wiki_export.py --workspace mio-studio --clean
"""
from __future__ import annotations

import argparse
import asyncio
import shutil
from datetime import datetime, timezone
from pathlib import Path

import motor.motor_asyncio
from loguru import logger

from aiura_legal.wiki.store import WikiPage, WikiStore

_TARGET_URI = "mongodb://localhost:27017"
_TARGET_DB = "aiura_legal"
_DEFAULT_BASE = "C:/project/AiUraLegalLab/workspaces"


def _page_to_markdown(page: WikiPage) -> str:
    """Wrappa body_md con frontmatter YAML minimale."""
    updated = page.last_updated.strftime("%Y-%m-%d %H:%M UTC")
    return (
        f"---\n"
        f"slug: {page.slug}\n"
        f"title: {page.title}\n"
        f"version: {page.version}\n"
        f"query_count: {page.query_count}\n"
        f"last_updated: {updated}\n"
        f"sources:\n"
        + "".join(f"  - {u}\n" for u in page.sources)
        + f"---\n\n"
        f"# {page.title}\n\n"
        f"{page.body_md}\n"
    )


def _build_index(pages: list[WikiPage], workspace: str, exported_at: str) -> str:
    lines = [
        f"# Wiki Index — {workspace}",
        f"",
        f"Esportato il {exported_at}  ",
        f"Pagine totali: {len(pages)}",
        f"",
        f"---",
        f"",
        f"| Pagina | Versione | Query | Aggiornata |",
        f"|--------|----------|-------|------------|",
    ]
    for p in sorted(pages, key=lambda x: x.slug):
        updated = p.last_updated.strftime("%Y-%m-%d")
        lines.append(
            f"| [{p.title}]({p.slug}.md) | v{p.version} | {p.query_count} | {updated} |"
        )
    return "\n".join(lines) + "\n"


async def export(workspace: str, out_dir: Path, clean: bool) -> int:
    client = motor.motor_asyncio.AsyncIOMotorClient(_TARGET_URI)
    store = WikiStore(client[_TARGET_DB])

    pages = await store.list_all(workspace)
    client.close()

    if not pages:
        logger.warning(f"Nessuna pagina trovata per workspace='{workspace}'")
        return 0

    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
        logger.info(f"Cartella pulita: {out_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    exported_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for page in pages:
        md_path = out_dir / f"{page.slug}.md"
        md_path.write_text(_page_to_markdown(page), encoding="utf-8")

    index_path = out_dir / "index.md"
    index_path.write_text(_build_index(pages, workspace, exported_at), encoding="utf-8")

    logger.success(
        f"Esportate {len(pages)} pagine + index.md in {out_dir}"
    )
    return len(pages)


def main() -> None:
    parser = argparse.ArgumentParser(description="Esporta wiki MongoDB → file markdown")
    parser.add_argument("--workspace", default="default", help="Workspace da esportare")
    parser.add_argument(
        "--out-dir",
        default=None,
        help=f"Cartella di output (default: {_DEFAULT_BASE}/<workspace>/wiki)",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Cancella la cartella di output prima di esportare",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else Path(_DEFAULT_BASE) / args.workspace / "wiki"

    logger.info(f"Avvio export: workspace={args.workspace} → {out_dir}")
    count = asyncio.run(export(args.workspace, out_dir, args.clean))
    if count:
        print(f"\nExport completato: {count} pagine in {out_dir}")
        print(f"Indice: {out_dir / 'index.md'}")


if __name__ == "__main__":
    main()
