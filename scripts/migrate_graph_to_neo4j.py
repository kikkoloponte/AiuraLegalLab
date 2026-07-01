"""
migrate_graph_to_neo4j.py — Fase B del piano di migrazione (Opzione C, POC).

Legge indices/graph.json (NetworkX) di un workspace e lo carica in Neo4j,
mappando:
  node_type="article"      → label :Articolo (urn, fonte, titolo, articolo_num,
                              valid_from, valid_to)
  node_type="provvedimento"→ label :Provvedimento (fonte, titolo)
  node_type="sentenza"     → label :Sentenza (organo, numero, anno, materia)
  node_type="massima"      → label :Massima (testo, urn, corpus)
  node_type="questione"    → label :QuestioneGiuridica (formulazione, materia, parole_chiave)
  ogni edge_type           → relazione Cypher omonima (RINVIA, ABROGA, MODIFICA,
                              CONTRASTA, APPARTIENE_A, INTERPRETA, APPLICATA_IN,
                              SINTETIZZA, QUALIFICA, PERTINENTE_A, RISOLVE)

Vedi docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md
per lo schema completo (§3) e ontology/legal_kb_ontology.ttl per la TBox.

Solo lettura sul lato AiUra: non modifica graph.json né alcun path di produzione.
Richiede: pip install -e ".[graph-poc]" e il container docker-compose.neo4j.yml attivo.

Utilizzo:
    python scripts/migrate_graph_to_neo4j.py --workspace mio-studio
    python scripts/migrate_graph_to_neo4j.py --workspace mio-studio --uri bolt://localhost:7687
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import networkx as nx
from loguru import logger

try:
    from neo4j import GraphDatabase
except ImportError:
    logger.error('Driver neo4j non installato. Esegui: pip install -e ".[graph-poc]"')
    sys.exit(1)

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

_BATCH_SIZE = 5000


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migra graph.json in Neo4j (POC)")
    parser.add_argument("--workspace", default="mio-studio")
    parser.add_argument(
        "--workspaces-root",
        default=str(_ROOT / "workspaces"),
    )
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="aiura-poc-pw")
    parser.add_argument(
        "--wipe", action="store_true",
        help="Cancella tutti i nodi/archi esistenti nel DB prima di caricare (POC: ripetibile)",
    )
    return parser.parse_args()


def _create_constraints(session) -> None:
    """Indici univoci — necessari PRIMA del caricamento bulk, altrimenti i MATCH
    per creare gli archi sono O(n) per nodo invece di O(log n)."""
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (a:Articolo) REQUIRE a.urn IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Provvedimento) REQUIRE p.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Sentenza) REQUIRE s.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Massima) REQUIRE m.id IS UNIQUE")
    session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (q:QuestioneGiuridica) REQUIRE q.id IS UNIQUE")


_NODE_TYPE_TO_LABEL = {
    "article": "Articolo",
    "provvedimento": "Provvedimento",
    "sentenza": "Sentenza",
    "massima": "Massima",
    "questione": "QuestioneGiuridica",
}

_MERGE_QUERY_BY_LABEL = {
    "Articolo": (
        "UNWIND $rows AS row "
        "MERGE (a:Articolo {urn: row.id}) "
        "SET a.fonte=row.fonte, a.titolo=row.titolo, a.articolo_num=row.articolo_num, "
        "a.valid_from=row.valid_from, a.valid_to=row.valid_to"
    ),
    "Provvedimento": (
        "UNWIND $rows AS row "
        "MERGE (p:Provvedimento {id: row.id}) "
        "SET p.fonte=row.fonte, p.titolo=row.titolo"
    ),
    "Sentenza": (
        "UNWIND $rows AS row "
        "MERGE (s:Sentenza {id: row.id}) "
        "SET s.organo=row.organo, s.numero=row.numero, s.anno=row.anno, s.materia=row.materia"
    ),
    "Massima": (
        "UNWIND $rows AS row "
        "MERGE (m:Massima {id: row.id}) "
        "SET m.testo=row.testo, m.urn=row.urn, m.corpus=row.corpus"
    ),
    "QuestioneGiuridica": (
        "UNWIND $rows AS row "
        "MERGE (q:QuestioneGiuridica {id: row.id}) "
        "SET q.formulazione=row.formulazione, q.materia=row.materia, q.parole_chiave=row.parole_chiave"
    ),
}


def _load_nodes(session, G: nx.DiGraph) -> dict[str, int]:
    labels = list(_MERGE_QUERY_BY_LABEL.keys())
    counts = {label: 0 for label in labels}
    counts["skipped"] = 0

    batch: dict[str, list[dict]] = {label: [] for label in labels}

    def _flush(label: str) -> None:
        if not batch[label]:
            return
        session.run(_MERGE_QUERY_BY_LABEL[label], rows=batch[label])
        counts[label] += len(batch[label])
        batch[label] = []

    for node_id, attrs in G.nodes(data=True):
        label = _NODE_TYPE_TO_LABEL.get(attrs.get("node_type"))
        if not label:
            counts["skipped"] += 1
            continue
        batch[label].append({"id": str(node_id), **attrs})
        if len(batch[label]) >= _BATCH_SIZE:
            _flush(label)

    for label in labels:
        _flush(label)

    return counts


_LABEL_BY_NODE_TYPE = _NODE_TYPE_TO_LABEL
_KEY_PROP_BY_LABEL = {
    "Articolo": "urn", "Provvedimento": "id", "Sentenza": "id",
    "Massima": "id", "QuestioneGiuridica": "id",
}


def _load_edges(session, G: nx.DiGraph) -> dict[str, int]:
    """
    Raggruppa per (label_src, label_dst, edge_type): permette un MERGE con
    label e proprietà chiave espliciti, che usa l'indice del constraint
    invece di una scansione su tutti i nodi (decisivo a 300k+ nodi — la
    prima versione, label-agnostic via WHERE OR, non terminava in tempi
    utili sul grafo reale).
    """
    node_label: dict[str, str] = {}
    for node_id, attrs in G.nodes(data=True):
        label = _LABEL_BY_NODE_TYPE.get(attrs.get("node_type"))
        if label:
            node_label[str(node_id)] = label

    by_group: dict[tuple[str, str, str], list[dict]] = {}
    skipped_unknown_node = 0
    for u, v, edge_attrs in G.edges(data=True):
        u, v = str(u), str(v)
        label_u, label_v = node_label.get(u), node_label.get(v)
        if not label_u or not label_v:
            skipped_unknown_node += 1
            continue
        et = edge_attrs.get("edge_type", "UNKNOWN")
        by_group.setdefault((label_u, label_v, et), []).append({"src": u, "dst": v})

    counts: dict[str, int] = {}
    if skipped_unknown_node:
        counts["skipped_unknown_node"] = skipped_unknown_node

    for (label_u, label_v, edge_type), rows in by_group.items():
        if not edge_type.replace("_", "").isalnum():
            logger.warning(f"edge_type non sicuro per query letterale, skip: {edge_type!r}")
            continue
        key_u, key_v = _KEY_PROP_BY_LABEL[label_u], _KEY_PROP_BY_LABEL[label_v]
        total = 0
        for i in range(0, len(rows), _BATCH_SIZE):
            chunk = rows[i:i + _BATCH_SIZE]
            session.run(
                "UNWIND $rows AS row "
                f"MATCH (a:{label_u} {{{key_u}: row.src}}) "
                f"MATCH (b:{label_v} {{{key_v}: row.dst}}) "
                f"MERGE (a)-[r:{edge_type}]->(b)",
                rows=chunk,
            )
            total += len(chunk)
        counts[edge_type] = counts.get(edge_type, 0) + total

    return counts


def main() -> None:
    args = _parse_args()
    graph_path = Path(args.workspaces_root) / args.workspace / "indices" / "graph.json"
    if not graph_path.exists():
        logger.error(f"graph.json non trovato: {graph_path}")
        sys.exit(1)

    logger.info(f"Caricamento {graph_path}...")
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    G: nx.DiGraph = nx.node_link_graph(data, edges="edges")
    logger.info(f"Grafo origine: {G.number_of_nodes()} nodi, {G.number_of_edges()} archi")

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    driver.verify_connectivity()
    logger.info(f"Connesso a Neo4j: {args.uri}")

    with driver.session() as session:
        if args.wipe:
            logger.info("Wipe del database richiesto...")
            session.run("MATCH (n) DETACH DELETE n")

        _create_constraints(session)

        t0 = time.monotonic()
        node_counts = _load_nodes(session, G)
        t1 = time.monotonic()
        logger.info(f"Nodi caricati in {t1 - t0:.1f}s: {node_counts}")

        edge_counts = _load_edges(session, G)
        t2 = time.monotonic()
        logger.info(f"Archi caricati in {t2 - t1:.1f}s: {edge_counts}")

        result = session.run("MATCH (n) RETURN count(n) AS n").single()
        node_total = result["n"] if result else 0
        result = session.run("MATCH ()-[r]->() RETURN count(r) AS r").single()
        edge_total = result["r"] if result else 0

    logger.info(
        f"Validazione: Neo4j ha {node_total} nodi / {edge_total} archi "
        f"vs origine {G.number_of_nodes()} nodi / {G.number_of_edges()} archi"
    )
    driver.close()


if __name__ == "__main__":
    main()
