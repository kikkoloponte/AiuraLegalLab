"""
Indicizza i documenti giurisprudenziali nel workspace specificato.

Modalità INCREMENTALE (default):
  - Legge i doc_ids già presenti nel BM25
  - Salta i documenti già indicizzati
  - Salva BM25 + ChromaDB ogni --checkpoint-every batch
  - Riprendibile: se interrotto, riprende esattamente da dove si era fermato

Uso:
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --rebuild
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Carica .env prima di tutto — necessario per QDRANT_URL e MONGODB_URI
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.core.types import Document
from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.jurisprudence.coordinator import to_chunks
from aiura_legal.jurisprudence.models import JurisprudenceDocument, OrganoGiudicante

_WORKSPACES_BASE = Path(
    os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
)
_COLLECTION = "jurisprudence"
_DEFAULT_BATCH      = 500
_DEFAULT_CHECKPOINT = 10   # salva ogni 10 batch = ogni 5.000 doc


def _mongo_to_jdoc(record: dict) -> JurisprudenceDocument | None:
    try:
        from datetime import date
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


async def build(
    workspace: str,
    organo: str | None = None,
    rebuild: bool = False,
    batch_size: int = _DEFAULT_BATCH,
    checkpoint_every: int = _DEFAULT_CHECKPOINT,
) -> None:
    mongo = MongoClient.get()
    ws_path = _WORKSPACES_BASE / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    # Filtro MongoDB
    mongo_filter: dict = {}
    if organo:
        mongo_filter["organo"] = organo

    collection = mongo.db[_COLLECTION]
    total_db = await collection.count_documents(mongo_filter)
    logger.info(
        "Documenti in MongoDB: {:,}  (filtro: {})",
        total_db, organo or "nessuno",
    )

    if total_db == 0:
        logger.warning("Nessun documento trovato. Esegui prima sync_jurisprudence.py")
        return

    # Carica indici esistenti
    bm25   = BM25Retriever(str(ws_path))
    vector = VectorRetriever(str(ws_path))

    if rebuild:
        logger.info("Modalità REBUILD: reset indici esistenti")
        bm25._reset()
        try:
            vector._init_chroma()  # stub Qdrant: cancella e ricrea la collection
        except Exception as exc:
            logger.warning("Reset Qdrant: {}", exc)
        already_indexed: set[str] = set()
    else:
        # BUGFIX: i sub-indici BM25 sono lazy-loaded (caricati solo al primo search()).
        # build_jurisprudence_indexes.py non chiama mai search(), quindi _doc_ids
        # sarebbe sempre vuoto senza questo caricamento esplicito. Carichiamo solo
        # il sub "giurisprudenza" per non allocare memoria inutile per normattiva/studio.
        giuri_sub = bm25._subs.get("giurisprudenza")
        if giuri_sub is not None and giuri_sub.index_path.exists() and not giuri_sub.doc_ids:
            giuri_sub.load()

        # BM25 salva chunk_id nel formato "{doc_id}_{tipo_chunk}"
        # (es. "1b87b6fbcf64a881_motivazione").
        # I chunk normativi NON hanno underscore nel loro ID (sono ObjectId plain).
        # Filtriamo solo i chunk giurisprudenziali per non contare erroneamente
        # i chunk normativi già presenti nel BM25 condiviso.
        already_indexed = {
            cid.split("_")[0] for cid in bm25._doc_ids if "_" in cid
        }
        n_docs_indexed = len(already_indexed)
        logger.info(
            "BM25 esistente: {:,} chunk totali → {:,} chunk giurisprudenziali già indicizzati — ne mancano {:,}",
            len(bm25._doc_ids),
            n_docs_indexed,
            total_db - n_docs_indexed,
        )

    # Conta quanti dei doc già in BM25 appartengono al filtro corrente
    # (quando --organo è attivo, already_indexed può contenere doc di altri organi)
    if not rebuild and len(already_indexed) > 0:
        mongo_ids_in_filter = {
            str(d["_id"])
            async for d in collection.find(mongo_filter, {"_id": 1})
        }
        already_in_filter = already_indexed & mongo_ids_in_filter
        if len(already_in_filter) >= total_db:
            logger.success("Tutto già indicizzato. Niente da fare.")
            return
    elif not rebuild and len(already_indexed) == 0 and total_db == 0:
        logger.success("Nessun documento. Niente da fare.")
        return

    batch: list[Document] = []
    batch_num   = 0
    count_docs  = 0   # nuovi doc aggiunti in questa sessione
    count_skip  = 0   # doc già presenti saltati
    count_chunks = 0

    cursor = collection.find(mongo_filter)
    async for record in cursor:
        doc_id = str(record.get("_id", ""))

        # Skip se già indicizzato
        if doc_id in already_indexed:
            count_skip += 1
            continue

        jdoc = _mongo_to_jdoc(record)
        if not jdoc:
            continue

        chunks = to_chunks(jdoc)
        if not chunks:
            continue

        batch.extend(chunks)
        count_docs  += 1
        count_chunks += len(chunks)

        if len(batch) >= batch_size:
            bm25.add_documents_batch(batch)
            vector.add_documents_batch(batch)
            batch = []
            batch_num += 1

            # Salvataggio periodico (checkpoint)
            if batch_num % checkpoint_every == 0:
                bm25.save()
                # ChromaDB persiste già in tempo reale (upsert)
                total_indexed = len(already_indexed) + count_docs
                pct = total_indexed / total_db * 100
                logger.info(
                    "  Checkpoint #{}: {:,} nuovi | {:,} totali ({:.1f}%) | {:,} saltati",
                    batch_num // checkpoint_every,
                    count_docs, total_indexed, pct, count_skip,
                )

    # Flush batch residuo
    if batch:
        bm25.add_documents_batch(batch)
        vector.add_documents_batch(batch)

    # Salvataggio finale
    bm25.save()

    total_indexed = len(already_indexed) + count_docs
    logger.success(
        "Indicizzazione completata:\n"
        "  Nuovi indicizzati : {:,}\n"
        "  Già presenti (skip): {:,}\n"
        "  Totale in indice  : {:,} / {:,}\n"
        "  Chunk totali      : {:,}",
        count_docs, count_skip,
        total_indexed, total_db,
        count_chunks,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Indicizza giurisprudenza nel workspace (incrementale, riprendibile)"
    )
    parser.add_argument("--workspace", required=True)
    parser.add_argument(
        "--organo", default=None,
        help="Filtra: cassazione|tar|consiglio_stato|corte_cost|corte_conti",
    )
    parser.add_argument(
        "--rebuild", action="store_true",
        help="Ricostruisce tutto da zero (lento, ~4 ore)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=_DEFAULT_BATCH,
        help=f"Doc per batch (default: {_DEFAULT_BATCH})",
    )
    parser.add_argument(
        "--checkpoint-every", type=int, default=_DEFAULT_CHECKPOINT,
        help=f"Salva ogni N batch (default: {_DEFAULT_CHECKPOINT} = ogni 5.000 doc)",
    )
    args = parser.parse_args()
    asyncio.run(build(
        workspace=args.workspace,
        organo=args.organo,
        rebuild=args.rebuild,
        batch_size=args.batch_size,
        checkpoint_every=args.checkpoint_every,
    ))
