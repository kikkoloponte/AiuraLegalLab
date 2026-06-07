"""
Costruisce il grafo sentenza→norma da tutti i documenti in MongoDB.

Legge aiura_legal.jurisprudence, per ogni documento aggiunge:
  - nodo sentenza
  - nodi norma (da norme_citate)
  - archi interpreta / applicata_in / cita

Uso:
  python scripts/build_jurisprudence_graph.py
  python scripts/build_jurisprudence_graph.py --rebuild   # ricomincia da zero
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.jurisprudence.graph_builder import JurisprudenceGraphBuilder
from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante

_GRAPH_PATH = Path("C:/project/AiUraLegalLab/workspaces/jurisprudence_graph.json")
_BATCH_SAVE = 1000   # salva ogni N documenti


def _mongo_to_jdoc(record: dict) -> JurisprudenceDocument | None:
    try:
        dep_raw = record.get("data_deposito", "")
        dep = date.fromisoformat(dep_raw) if dep_raw else date.today()
        return JurisprudenceDocument(
            organo=OrganoGiudicante(record["organo"]),
            numero=record["numero"],
            anno=int(record["anno"]),
            data_deposito=dep,
            sezione=record.get("sezione", ""),
            materia=record.get("materia", ""),
            massima=record.get("massima", ""),
            motivazione=record.get("motivazione", ""),
            dispositivo=record.get("dispositivo", ""),
            norme_citate=record.get("norme_citate", []),
            sentenze_citate=record.get("sentenze_citate", []),
            source_url=record.get("source_url", ""),
            is_anonymized=record.get("is_anonymized", False),
        )
    except Exception as exc:
        logger.debug("Conversione record fallita: {}", exc)
        return None


async def build(rebuild: bool = False) -> None:
    mongo = MongoClient.get()
    jur = mongo.db["jurisprudence"]

    total = await jur.count_documents({})
    logger.info("Documenti in MongoDB: {:,}", total)

    if total == 0:
        logger.warning("Nessun documento. Esegui prima sync_jurisprudence.py")
        return

    _GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)

    if rebuild and _GRAPH_PATH.exists():
        _GRAPH_PATH.unlink()
        logger.info("Grafo precedente rimosso (--rebuild)")

    builder = JurisprudenceGraphBuilder(_GRAPH_PATH)
    logger.info(
        "Grafo caricato: {} nodi, {} archi",
        builder.graph.number_of_nodes(),
        builder.graph.number_of_edges(),
    )

    count = 0
    skipped = 0

    async for record in jur.find({}):
        jdoc = _mongo_to_jdoc(record)
        if not jdoc:
            skipped += 1
            continue

        builder.add_document(jdoc)
        count += 1

        if count % _BATCH_SAVE == 0:
            builder.save()
            logger.info(
                "  {:,} doc processati — nodi: {:,}  archi: {:,}",
                count,
                builder.graph.number_of_nodes(),
                builder.graph.number_of_edges(),
            )

    builder.save()

    g = builder.graph
    sentenze = [n for n, d in g.nodes(data=True) if d.get("type") == "sentenza"]
    norme = [n for n, d in g.nodes(data=True) if d.get("type") == "norma"]

    logger.success("Grafo costruito:")
    logger.success("  Nodi sentenza: {:,}", len(sentenze))
    logger.success("  Nodi norma:    {:,}", len(norme))
    logger.success("  Archi totali:  {:,}", g.number_of_edges())
    logger.success("  Salvato in:    {}", _GRAPH_PATH)
    if skipped:
        logger.warning("  Doc saltati:   {:,}", skipped)

    # Top 5 norme più citate
    from collections import Counter
    norme_cit = Counter(
        nbr for s in sentenze
        for nbr in g.successors(s)
        if g.nodes[nbr].get("type") == "norma"
    )
    if norme_cit:
        logger.info("Top 5 norme citate:")
        for urn, cnt in norme_cit.most_common(5):
            logger.info("  {:3d}  {}", cnt, urn[:70])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Costruisce grafo sentenza→norma")
    parser.add_argument("--rebuild", action="store_true", help="Ricomincia da zero")
    args = parser.parse_args()
    asyncio.run(build(rebuild=args.rebuild))
