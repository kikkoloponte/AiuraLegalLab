"""
Tier 2 EmbedWorker CLI — consuma job EMBED dalla ingestion_queue.

Uso:
    python scripts/run_tier2_worker.py
    python scripts/run_tier2_worker.py --once           # un ciclo e poi esci
    python scripts/run_tier2_worker.py --poll-interval 10
    python scripts/run_tier2_worker.py --batch-size 20
    python scripts/run_tier2_worker.py --workspaces-path C:/project/ws

In modalità loop (default) il worker gira indefinitamente e si ferma con Ctrl+C.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.workers.embed_worker import EmbedWorker


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Tier 2 EmbedWorker — embedding asincrono chunk → ChromaDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--once",
        action="store_true",
        help="Esegui un solo ciclo di elaborazione e poi esci",
    )
    p.add_argument(
        "--poll-interval",
        type=float,
        default=5.0,
        help="Secondi di attesa tra cicli quando la coda è vuota (default: 5)",
    )
    p.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Job da processare per ciclo (default: 50)",
    )
    p.add_argument(
        "--workspaces-path",
        default=str(_ROOT / "workspaces"),
        help="Path base dei workspace (default: ./workspaces)",
    )
    return p.parse_args()


async def main() -> int:
    args = _parse_args()

    try:
        mongo = MongoClient.get()
        ok = await mongo.ping()
        if not ok:
            logger.error("MongoDB non raggiungibile — worker non avviato")
            return 1
    except Exception as e:
        logger.error(f"Connessione MongoDB fallita: {e}")
        return 1

    worker = EmbedWorker(
        mongo_db=mongo.db,
        workspaces_base_path=args.workspaces_path,
        batch_size=args.batch_size,
    )

    if args.once:
        n = await worker.run_once()
        logger.info(f"Job processati: {n}")
        return 0

    # Loop continuo con gestione Ctrl+C
    stop = asyncio.Event()
    try:
        await worker.run_loop(
            poll_interval=args.poll_interval,
            stop_event=stop,
        )
    except KeyboardInterrupt:
        logger.info("[EmbedWorker] Interruzione manuale — arresto graceful")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
