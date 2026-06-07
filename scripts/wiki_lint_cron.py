"""
wiki_lint_cron.py — esegue WikiLinter e stampa il report.

Progettato per essere richiamato come cron job o task schedulato.

Uso:
    python scripts/wiki_lint_cron.py --workspace mio-studio
    python scripts/wiki_lint_cron.py --workspace mio-studio --fail-on-issues

Exit codes:
    0 — nessun problema rilevato
    1 — errore di esecuzione
    2 -- problemi rilevati (solo con --fail-on-issues)
"""
from __future__ import annotations

import argparse
import asyncio
import sys

import motor.motor_asyncio
from loguru import logger

from aiura_legal.wiki.lint import WikiLinter
from aiura_legal.wiki.store import WikiStore

_TARGET_URI = "mongodb://localhost:27017"
_TARGET_DB = "aiura_legal"
_SOURCE_DB = "legal_lab"


async def run_lint(workspace: str, fail_on_issues: bool) -> int:
    client = motor.motor_asyncio.AsyncIOMotorClient(_TARGET_URI)
    wiki_db = client[_TARGET_DB]
    source_db = client[_SOURCE_DB]

    store = WikiStore(wiki_db)
    linter = WikiLinter(store, source_db)

    report = await linter.run(workspace)
    client.close()

    print(f"\n{'='*50}")
    print(f"  Wiki Lint Report — workspace: {workspace}")
    print(f"{'='*50}")
    print(report.summary())

    if report.stale_pages:
        print(f"\nPagine stale:")
        for slug in report.stale_pages:
            print(f"  - {slug}")

    if report.empty_bodies:
        print(f"\nPageine con body vuoto:")
        for slug in report.empty_bodies:
            print(f"  - {slug}")

    if report.orphan_urns:
        print(f"\nURN orfani (non in normattiva_docs):")
        for slug, urn in report.orphan_urns:
            print(f"  - {slug}: {urn}")

    print(f"{'='*50}\n")

    has_issues = bool(
        report.stale_pages or report.empty_bodies or report.orphan_urns
    )

    if fail_on_issues and has_issues:
        return 2
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="WikiLinter — health check wiki legale")
    parser.add_argument("--workspace", default="default", help="Workspace da analizzare")
    parser.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Exit code 2 se vengono rilevati problemi (utile per CI/cron alert)",
    )
    args = parser.parse_args()

    logger.info(f"WikiLinter avviato: workspace={args.workspace}")
    exit_code = asyncio.run(run_lint(args.workspace, args.fail_on_issues))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
