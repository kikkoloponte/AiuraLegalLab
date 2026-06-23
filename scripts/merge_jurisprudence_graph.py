"""
merge_jurisprudence_graph.py — Fase 0 del piano KG enrichment (consolidamento grafi).

Importa nodi sentenza e archi INTERPRETA/APPLICATA_IN dal grafo giurisprudenziale
condiviso (workspaces/jurisprudence_graph.json, costruito da JurisprudenceGraphBuilder)
in graph.json del workspace target (quello letto da GraphRetriever nel retrieval RRF).

I nodi "norma" del grafo giurisprudenziale sono stringhe grezze non risolte a URN
(es. "art.380", "art. 380 cod."). Il merge risolve solo per numero di articolo:
se il numero corrisponde a un solo articolo nel workspace target, collega; se
corrisponde a più articoli (fonti diverse, es. art. 380 c.c. vs c.p.c.) o a
nessuno, scarta — precisione alta, recall parziale per design.

Utilizzo:
    python scripts/merge_jurisprudence_graph.py --workspace mio-studio
    python scripts/merge_jurisprudence_graph.py --workspace mio-studio --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import networkx as nx
from loguru import logger

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from aiura_legal.core.graph.builder import LegalGraphBuilder


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge del grafo giurisprudenziale in graph.json del workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--workspace", default="mio-studio", help="Workspace target (default: mio-studio)")
    parser.add_argument(
        "--workspaces-root",
        default=str(_ROOT / "workspaces"),
        help="Root directory dei workspace (default: ./workspaces)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Calcola le statistiche senza scrivere su disco")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    workspaces_root = Path(args.workspaces_root)
    workspace_path = str(workspaces_root / args.workspace)
    jurisprudence_path = workspaces_root / "jurisprudence_graph.json"

    if not jurisprudence_path.exists():
        logger.error(f"Grafo giurisprudenziale non trovato: {jurisprudence_path}")
        sys.exit(1)

    logger.info(f"Caricamento {jurisprudence_path}...")
    data = json.loads(jurisprudence_path.read_text(encoding="utf-8"))
    jurisprudence_graph: nx.DiGraph = nx.node_link_graph(data, directed=True, edges="links")
    logger.info(
        f"Grafo giurisprudenziale: {jurisprudence_graph.number_of_nodes()} nodi, "
        f"{jurisprudence_graph.number_of_edges()} archi"
    )

    builder = LegalGraphBuilder()

    if args.dry_run:
        target_path = Path(workspace_path) / "indices" / "graph.json"
        if not target_path.exists():
            logger.error(f"graph.json target non trovato: {target_path}")
            sys.exit(1)
        target_data = json.loads(target_path.read_text(encoding="utf-8"))
        target_graph: nx.DiGraph = nx.node_link_graph(target_data, edges="edges")
        logger.info(
            f"[DRY RUN] graph.json target ({args.workspace}): "
            f"{target_graph.number_of_nodes()} nodi, {target_graph.number_of_edges()} archi "
            f"— nessuna scrittura, esegui senza --dry-run per applicare"
        )
        return

    stats = builder.merge_jurisprudence_graph(jurisprudence_graph, workspace_path)
    logger.info(f"Merge completato per workspace '{args.workspace}': {stats}")


if __name__ == "__main__":
    main()
