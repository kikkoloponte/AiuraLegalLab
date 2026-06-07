"""
build_graph.py — Build completo del grafo giuridico da MongoDB chunks.

Legge tutti i chunk da aiura_legal.chunks per il workspace specificato,
costruisce il grafo NetworkX e lo salva in {workspace}/indices/graph.json.

Utilizzo:
    python scripts/build_graph.py --workspace default
    python scripts/build_graph.py --workspace default --chunk-filter '{"corpus":"normattiva"}'
    python scripts/build_graph.py --workspace default --dry-run
    python scripts/build_graph.py --workspace default --reset

Per corpus di grandi dimensioni (166k+ documenti) usare questo script invece
dell'update incrementale della pipeline, che è ottimizzato per pochi documenti
alla volta.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from loguru import logger

# Aggiungi la root del progetto al path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from aiura_legal.core.graph.builder import LegalGraphBuilder
from aiura_legal.ingestion.mongodb.client import MongoClient


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build grafo giuridico da MongoDB chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--workspace",
        default="default",
        help="Nome workspace (default: 'default')",
    )
    parser.add_argument(
        "--workspaces-path",
        default=str(_ROOT / "workspaces"),
        help="Path base dei workspace (default: ./workspaces)",
    )
    parser.add_argument(
        "--chunk-filter",
        default=None,
        help='Filtro JSON per subset chunk (es. \'{"corpus":"normattiva"}\')',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Stampa statistiche senza scrivere il file",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Cancella graph.json esistente prima del build",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5000,
        help="Chunk per batch MongoDB (default: 5000)",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

async def _load_chunks(
    workspace: str,
    chunk_filter: dict | None,
    batch_size: int,
) -> list[dict]:
    """Carica tutti i chunk dal MongoDB per il workspace dato."""
    mongo = MongoClient.get()
    query: dict = {"workspace": workspace}
    if chunk_filter:
        query.update(chunk_filter)

    chunks: list[dict] = []
    cursor = mongo.db["chunks"].find(query).batch_size(batch_size)
    async for chunk in cursor:
        # Converti ObjectId in stringa
        if "_id" in chunk:
            chunk["_id"] = str(chunk["_id"])
        chunks.append(chunk)

    return chunks


async def main() -> int:
    args = _parse_args()

    # Parse chunk_filter
    chunk_filter: dict | None = None
    if args.chunk_filter:
        try:
            chunk_filter = json.loads(args.chunk_filter)
        except json.JSONDecodeError as e:
            logger.error(f"--chunk-filter JSON non valido: {e}")
            return 1

    workspace_path = str(Path(args.workspaces_path) / args.workspace)
    builder = LegalGraphBuilder()

    # Reset opzionale
    if args.reset:
        builder.reset(workspace_path)
        logger.info(f"Grafo precedente rimosso per workspace '{args.workspace}'")

    # Carica chunk da MongoDB
    logger.info(
        f"Caricamento chunk da MongoDB — workspace='{args.workspace}', "
        f"filter={chunk_filter}"
    )
    t0 = time.monotonic()
    try:
        chunks = await _load_chunks(args.workspace, chunk_filter, args.batch_size)
    except Exception as e:
        logger.error(f"Errore connessione MongoDB: {e}")
        return 1

    t_load = time.monotonic() - t0
    logger.info(f"{len(chunks)} chunk caricati in {t_load:.1f}s")

    if not chunks:
        logger.warning("Nessun chunk trovato — grafo vuoto non salvato")
        return 0

    if args.dry_run:
        # Dry-run: simula il build in memoria senza scrivere
        logger.info("[dry-run] Build in memoria (nessun file scritto)...")
        t1 = time.monotonic()
        G = builder.build("/tmp/dry_run_ws", chunks)
        t_build = time.monotonic() - t1

        article_nodes = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "article")
        prov_nodes = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "provvedimento")
        edge_types: dict[str, int] = {}
        for _, _, d in G.edges(data=True):
            et = d.get("edge_type", "?")
            edge_types[et] = edge_types.get(et, 0) + 1

        print(f"\n[dry-run] Risultato build:")
        print(f"  Nodi:  {article_nodes} article + {prov_nodes} provvedimento")
        for et, count in sorted(edge_types.items()):
            print(f"  Archi {et}: {count}")
        print(f"  Tempo: {t_build:.1f}s")
        return 0

    # Build reale
    logger.info(f"Build grafo → {workspace_path}/indices/graph.json ...")
    t1 = time.monotonic()
    G = builder.build(workspace_path, chunks)
    t_build = time.monotonic() - t1

    article_nodes = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "article")
    prov_nodes = sum(1 for _, d in G.nodes(data=True) if d.get("node_type") == "provvedimento")
    edge_types: dict[str, int] = {}
    for _, _, d in G.edges(data=True):
        et = d.get("edge_type", "?")
        edge_types[et] = edge_types.get(et, 0) + 1

    graph_file = Path(workspace_path) / "indices" / "graph.json"
    size_mb = graph_file.stat().st_size / (1024 * 1024) if graph_file.exists() else 0

    logger.success(
        f"Build completato in {t_build:.1f}s:\n"
        f"  Nodi: {article_nodes} article + {prov_nodes} provvedimento\n"
        f"  Archi: { {k: v for k,v in sorted(edge_types.items())} }\n"
        f"  File: {graph_file} ({size_mb:.1f} MB)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
