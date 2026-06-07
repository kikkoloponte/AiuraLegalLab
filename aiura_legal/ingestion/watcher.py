"""
File Watcher per incoming/ — avvia Tier1Pipeline su nuovi file.

Struttura cartelle per workspace:
  workspaces/{workspace}/
    incoming/     ← drop file qui
    processed/    ← file OK
    failed/       ← file con errori
    indices/      ← BM25 + ChromaDB (build_indexes.py)

Uso:
  python -m aiura_legal.ingestion.watcher --workspace mio-studio
"""
from __future__ import annotations

import asyncio
import argparse
from pathlib import Path

from loguru import logger
from watchfiles import awatch, Change

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.ingestion.pipeline import Tier1Pipeline

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}
DEFAULT_BASE = "C:/project/AiUraLegalLab/workspaces"


def _workspace_dirs(workspace: str, base: str = DEFAULT_BASE):
    root = Path(base) / workspace
    dirs = {
        "incoming":  root / "incoming",
        "processed": root / "processed",
        "failed":    root / "failed",
        "indices":   root / "indices",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


async def watch_workspace(
    workspace: str,
    base_path: str = DEFAULT_BASE,
) -> None:
    """
    Loop asincrono: monitora incoming/ e processa i nuovi file.
    Blocca finché non viene interrotto (Ctrl+C).
    """
    dirs = _workspace_dirs(workspace, base_path)
    incoming = dirs["incoming"]

    mongo_client = MongoClient.get()
    pipeline = Tier1Pipeline(
        mongo_db=mongo_client.db,
        workspace=workspace,
    )

    logger.info(f"Watcher avviato su: {incoming}")
    logger.info("Pronto — copia file PDF/DOCX/TXT in incoming/ per avviare l'ingestione.")

    # Processa file già presenti all'avvio
    existing = [
        f for f in incoming.iterdir()
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    if existing:
        logger.info(f"Trovati {len(existing)} file pre-esistenti in incoming/")
        for f in existing:
            await _process_file(f, pipeline, dirs)

    # Watch loop
    async for changes in awatch(str(incoming)):
        for change_type, file_path in changes:
            if change_type not in (Change.added, Change.modified):
                continue
            path = Path(file_path)
            if not path.is_file():
                continue
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                logger.debug(f"Ignorato (estensione non supportata): {path.name}")
                continue
            await _process_file(path, pipeline, dirs)


async def _process_file(
    path: Path,
    pipeline: Tier1Pipeline,
    dirs: dict,
) -> None:
    logger.info(f"Elaborazione: {path.name}")

    # Piccola pausa per assicurarsi che il file sia completamente scritto
    await asyncio.sleep(0.2)

    result = await pipeline.ingest(str(path))

    if result.status == "ok":
        dest = dirs["processed"] / path.name
        try:
            path.rename(dest)
            logger.success(
                f"✓ {path.name} → processed/ "
                f"({result.chunk_count} chunk, {result.duration_s:.1f}s)"
            )
        except Exception as e:
            logger.warning(f"Impossibile spostare {path.name} → processed/: {e}")
    else:
        dest = dirs["failed"] / path.name
        try:
            path.rename(dest)
        except Exception:
            pass
        logger.error(f"✗ {path.name} → failed/: {result.error}")


# ---------------------------------------------------------------------------
# Entry point CLI
# ---------------------------------------------------------------------------

async def _main() -> None:
    parser = argparse.ArgumentParser(description="AiUra LegalLab — File Watcher")
    parser.add_argument("--workspace", required=True, help="Nome workspace")
    parser.add_argument(
        "--base-path",
        default=DEFAULT_BASE,
        help=f"Path base workspaces (default: {DEFAULT_BASE})",
    )
    args = parser.parse_args()
    await watch_workspace(args.workspace, args.base_path)


if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        logger.info("Watcher terminato.")
