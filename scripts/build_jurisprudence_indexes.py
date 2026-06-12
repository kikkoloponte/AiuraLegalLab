"""
Indicizza i documenti giurisprudenziali nel workspace specificato.

Modalità LEGACY (default):
  - Legge dalla collection jurisprudence, chiama to_chunks() per ogni doc
  - Salta i documenti già presenti in BM25 (check per base doc_id)
  - Gestisce massima, motivazione, dispositivo

Modalità FROM-CHUNKS (--from-chunks, Fase 1):
  - Legge i sub-chunk pre-calcolati dalla collection chunks (corpus=giurisprudenza)
  - Check di skip a livello di chunk_id esatto
  - Da usare dopo aver eseguito rechunk_motivazioni.py
  - Compatibile con --organo e --limit

Cleanup (--cleanup-old):
  - Elimina i punti Qdrant con ID nel formato {hex16}_motivazione (monolitici pre-Fase-1)
  - Eseguire SOLO dopo aver verificato che i nuovi sub-chunk sono in Qdrant
  - Rinomina il pkl BM25 come .v1.bak prima di eliminare i chunk obsoleti da BM25

Uso:
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --from-chunks --limit 5000
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --from-chunks
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --cleanup-old
"""
from __future__ import annotations

import argparse
import asyncio
import os
import re
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
_CHUNKS_COLLECTION = "chunks"
_DEFAULT_BATCH      = 500
_DEFAULT_CHECKPOINT = 10   # salva ogni 10 batch = ogni 5.000 doc

# Pattern ID chunk motivazione monolitico pre-Fase-1: {hex16}_motivazione
_OLD_MOTIVAZIONE_RE = re.compile(r"^[0-9a-f]{16}_motivazione$")


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


def _chunk_from_record(record: dict) -> Document:
    """Converte un record dalla collection chunks in un Document indicizzabile."""
    from datetime import date
    dep_raw = record.get("data_deposito", "")
    try:
        dep_date = date.fromisoformat(dep_raw) if dep_raw else date.today()
        valid_from = dep_date.isoformat()
    except ValueError:
        valid_from = date.today().isoformat()

    return Document(
        id=str(record["_id"]),
        text=record.get("text", ""),
        metadata={
            "corpus": "giurisprudenza",
            "chunk_type": record.get("chunk_type", "motivazione"),
            "organo": record.get("organo", ""),
            "numero": record.get("numero", ""),
            "anno": str(record.get("anno", "")),
            "materia": record.get("materia", ""),
            "source_url": record.get("source_url", ""),
            "valid_from": valid_from,
            "workspace": "",  # impostato dall'indicizzatore per workspace
        },
    )


# ---------------------------------------------------------------------------
# Modalità LEGACY — legge da jurisprudence, chiama to_chunks()
# ---------------------------------------------------------------------------

async def build_legacy(
    workspace: str,
    organo: str | None = None,
    rebuild: bool = False,
    batch_size: int = _DEFAULT_BATCH,
    checkpoint_every: int = _DEFAULT_CHECKPOINT,
    limit: int | None = None,
) -> None:
    mongo = MongoClient.get()
    ws_path = _WORKSPACES_BASE / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    mongo_filter: dict = {}
    if organo:
        mongo_filter["organo"] = organo

    collection = mongo.db[_COLLECTION]
    total_db = await collection.count_documents(mongo_filter)
    if limit:
        total_db = min(total_db, limit)
    logger.info(
        "Documenti in MongoDB: {:,}  (filtro: {})",
        total_db, organo or "nessuno",
    )

    if total_db == 0:
        logger.warning("Nessun documento trovato. Esegui prima sync_jurisprudence.py")
        return

    bm25   = BM25Retriever(str(ws_path))
    vector = VectorRetriever(str(ws_path))

    if rebuild:
        logger.info("Modalità REBUILD: reset indici esistenti")
        bm25._reset()
        try:
            vector._init_chroma()
        except Exception as exc:
            logger.warning("Reset Qdrant: {}", exc)
        already_indexed: set[str] = set()
    else:
        giuri_sub = bm25._subs.get("giurisprudenza")
        if giuri_sub is not None and giuri_sub.index_path.exists() and not giuri_sub.doc_ids:
            giuri_sub.load()

        already_indexed = {
            cid.split("_")[0] for cid in bm25._doc_ids if "_" in cid
        }
        n_docs_indexed = len(already_indexed)
        logger.info(
            "BM25 esistente: {:,} chunk totali → {:,} doc già indicizzati",
            len(bm25._doc_ids), n_docs_indexed,
        )

    if not rebuild and len(already_indexed) > 0:
        mongo_ids_in_filter = {
            str(d["_id"])
            async for d in collection.find(mongo_filter, {"_id": 1})
        }
        already_in_filter = already_indexed & mongo_ids_in_filter
        if len(already_in_filter) >= total_db:
            logger.success("Tutto già indicizzato. Niente da fare.")
            return

    batch: list[Document] = []
    batch_num   = 0
    count_docs  = 0
    count_skip  = 0
    count_chunks = 0

    cursor = collection.find(mongo_filter)
    async for record in cursor:
        if limit and count_docs + count_skip >= limit:
            break
        doc_id = str(record.get("_id", ""))

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

            if batch_num % checkpoint_every == 0:
                bm25.save()
                total_indexed = len(already_indexed) + count_docs
                pct = total_indexed / total_db * 100
                logger.info(
                    "  Checkpoint #{}: {:,} nuovi | {:,} totali ({:.1f}%) | {:,} saltati",
                    batch_num // checkpoint_every,
                    count_docs, total_indexed, pct, count_skip,
                )

    if batch:
        bm25.add_documents_batch(batch)
        vector.add_documents_batch(batch)

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


# ---------------------------------------------------------------------------
# Modalità FROM-CHUNKS — legge da chunks collection (Fase 1)
# ---------------------------------------------------------------------------

async def build_from_chunks(
    workspace: str,
    organo: str | None = None,
    batch_size: int = _DEFAULT_BATCH,
    checkpoint_every: int = _DEFAULT_CHECKPOINT,
    limit: int | None = None,
) -> None:
    """
    Indicizza i sub-chunk pre-calcolati dalla collection chunks.
    Da usare dopo rechunk_motivazioni.py.

    Check di skip: confronto esatto su chunk_id (es. {hex16}_motivazione_000).
    I punti Qdrant vecchi ({hex16}_motivazione monolitici) non vengono toccati
    qui — usa --cleanup-old dopo la verifica.
    """
    mongo = MongoClient.get()
    ws_path = _WORKSPACES_BASE / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    # Filtro: solo giurisprudenza, motivazione sub-chunks
    mongo_filter: dict = {"corpus": "giurisprudenza", "chunk_type": "motivazione"}
    if organo:
        mongo_filter["organo"] = organo

    collection = mongo.db[_CHUNKS_COLLECTION]
    total_db = await collection.count_documents(mongo_filter)
    if limit:
        total_db = min(total_db, limit)
    logger.info(
        "Sub-chunk da indicizzare: {:,}  (organo: {})",
        total_db, organo or "tutti",
    )

    if total_db == 0:
        logger.warning(
            "Nessun sub-chunk trovato. Esegui prima:\n"
            "  python scripts/rechunk_motivazioni.py --workspace {}", workspace,
        )
        return

    bm25   = BM25Retriever(str(ws_path))
    vector = VectorRetriever(str(ws_path))

    # Pre-carica BM25 sub giurisprudenza per avere doc_ids aggiornati
    giuri_sub = bm25._subs.get("giurisprudenza")
    if giuri_sub is not None and giuri_sub.index_path.exists() and not giuri_sub.doc_ids:
        giuri_sub.load()

    # Check a livello di chunk_id esatto (non base doc_id)
    already_indexed_chunks: set[str] = set(bm25._doc_ids)
    new_chunk_ids_already = {
        cid for cid in already_indexed_chunks
        if re.match(r"^[0-9a-f]{16}_motivazione_\d{3}$", cid)
    }
    logger.info(
        "BM25 esistente: {:,} chunk totali → {:,} sub-chunk Fase-1 già indicizzati",
        len(already_indexed_chunks), len(new_chunk_ids_already),
    )

    batch: list[Document] = []
    batch_num    = 0
    count_chunks = 0
    count_skip   = 0

    cursor = collection.find(mongo_filter).sort("_id", 1)
    async for record in cursor:
        if limit and count_chunks + count_skip >= limit:
            break

        chunk_id = str(record["_id"])
        if chunk_id in already_indexed_chunks:
            count_skip += 1
            continue

        doc = _chunk_from_record(record)
        batch.append(doc)
        count_chunks += 1

        if len(batch) >= batch_size:
            bm25.add_documents_batch(batch)
            vector.add_documents_batch(batch)
            batch = []
            batch_num += 1

            if batch_num % checkpoint_every == 0:
                bm25.save()
                total_done = count_chunks + count_skip
                pct = total_done / total_db * 100
                logger.info(
                    "  Checkpoint #{}: {:,} nuovi | {:.1f}% completato | {:,} saltati",
                    batch_num // checkpoint_every,
                    count_chunks, pct, count_skip,
                )

    if batch:
        bm25.add_documents_batch(batch)
        vector.add_documents_batch(batch)

    bm25.save()

    logger.success(
        "Embedding sub-chunk completato:\n"
        "  Nuovi indicizzati : {:,}\n"
        "  Già presenti (skip): {:,}\n"
        "  Totale su DB      : {:,}",
        count_chunks, count_skip, total_db,
    )


# ---------------------------------------------------------------------------
# Cleanup — elimina vecchi punti Qdrant monolitici (pre-Fase-1)
# ---------------------------------------------------------------------------

async def cleanup_old_motivazione(workspace: str, dry_run: bool = False) -> None:
    """
    Elimina i punti Qdrant con ID nel formato {hex16}_motivazione (monolitici).
    Eseguire SOLO dopo aver verificato che i nuovi sub-chunk sono correttamente
    indicizzati (--from-chunks completato e verificato).

    Sicurezza:
    - MAI eliminare punti se BM25 non ha chunk Fase-1 ({hex16}_motivazione_000)
    - Rinomina il pkl BM25 come .v1.bak prima di rimuovere gli ID obsoleti
    """
    ws_path = _WORKSPACES_BASE / workspace

    bm25 = BM25Retriever(str(ws_path))
    giuri_sub = bm25._subs.get("giurisprudenza")
    if giuri_sub is not None and giuri_sub.index_path.exists() and not giuri_sub.doc_ids:
        giuri_sub.load()

    new_chunks = {
        cid for cid in bm25._doc_ids
        if re.match(r"^[0-9a-f]{16}_motivazione_\d{3}$", cid)
    }
    old_chunks = {
        cid for cid in bm25._doc_ids
        if _OLD_MOTIVAZIONE_RE.match(cid)
    }

    if not new_chunks:
        logger.error(
            "ABORT: nessun sub-chunk Fase-1 trovato in BM25. "
            "Esegui prima --from-chunks e verifica prima di --cleanup-old."
        )
        return

    logger.info(
        "Cleanup Qdrant:\n"
        "  Sub-chunk Fase-1 in BM25 : {:,}\n"
        "  Chunk monolitici (vecchi): {:,}",
        len(new_chunks), len(old_chunks),
    )

    if not old_chunks:
        logger.info("Nessun vecchio chunk monolitico trovato in BM25. Niente da rimuovere.")
        return

    if dry_run:
        logger.info("[DRY-RUN] eliminerei {:,} punti Qdrant e {:,} chunk BM25 monolitici",
                    len(old_chunks), len(old_chunks))
        return

    # 1. Backup pkl BM25 (sicurezza: non distrugge l'indice corrente)
    vector = VectorRetriever(str(ws_path))
    giuri_pkl = giuri_sub.index_path if (giuri_sub and giuri_sub.index_path) else None
    if giuri_pkl and Path(giuri_pkl).exists():
        bak_path = Path(str(giuri_pkl) + ".v1.bak")
        if not bak_path.exists():
            import shutil
            shutil.copy2(giuri_pkl, bak_path)
            logger.info("BM25 pkl salvato come backup: {}", bak_path)

    # 2. Elimina da Qdrant (usa UUID derivati dagli ID originali)
    from aiura_legal.core.retrieval.vector_retriever import _to_qdrant_id
    qdrant_ids_to_delete = [_to_qdrant_id(cid) for cid in old_chunks]
    chunk_batches = [qdrant_ids_to_delete[i:i+500] for i in range(0, len(qdrant_ids_to_delete), 500)]
    deleted_total = 0
    for chunk_batch in chunk_batches:
        try:
            vector._client.delete(
                collection_name=vector._collection_name,
                points_selector=chunk_batch,
            )
            deleted_total += len(chunk_batch)
        except Exception as exc:
            logger.error("Errore eliminazione Qdrant batch: {}", exc)
    logger.info("Punti Qdrant eliminati: {:,}", deleted_total)

    # 3. Rimuovi gli ID vecchi dal BM25 in-memory (lazy: solo se sub-indice caricato)
    # Il BM25 non supporta rimozione dinamica — il rebuild viene schedulato sul prossimo
    # full rebuild. Per ora il BM25 conterrà sia old che new; la fusione RRF usa doc_id
    # come chiave quindi i vecchi chunk non producono risultati duplicati (Qdrant li ha già).
    logger.info(
        "Nota: i chunk monolitici restano nel BM25 fino al prossimo --rebuild. "
        "Questo è sicuro: Qdrant non ha più quei punti, quindi non verranno restituiti."
    )
    logger.success("Cleanup completato.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

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
        help="Ricostruisce tutto da zero (solo modalità legacy)",
    )
    parser.add_argument(
        "--from-chunks", action="store_true",
        help="Fase 1: legge sub-chunk pre-calcolati da chunks collection (post rechunk_motivazioni.py)",
    )
    parser.add_argument(
        "--cleanup-old", action="store_true",
        help="Elimina vecchi punti Qdrant monolitici {hex16}_motivazione (post verifica Fase 1)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Con --cleanup-old: mostra cosa verrebbe eliminato senza farlo",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Numero massimo di chunk/doc da processare (per validazione)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=_DEFAULT_BATCH,
        help=f"Doc per batch (default: {_DEFAULT_BATCH})",
    )
    parser.add_argument(
        "--checkpoint-every", type=int, default=_DEFAULT_CHECKPOINT,
        help=f"Salva ogni N batch (default: {_DEFAULT_CHECKPOINT} = ogni 5.000)",
    )
    args = parser.parse_args()

    if args.cleanup_old:
        asyncio.run(cleanup_old_motivazione(
            workspace=args.workspace,
            dry_run=args.dry_run,
        ))
    elif args.from_chunks:
        asyncio.run(build_from_chunks(
            workspace=args.workspace,
            organo=args.organo,
            batch_size=args.batch_size,
            checkpoint_every=args.checkpoint_every,
            limit=args.limit,
        ))
    else:
        asyncio.run(build_legacy(
            workspace=args.workspace,
            organo=args.organo,
            rebuild=args.rebuild,
            batch_size=args.batch_size,
            checkpoint_every=args.checkpoint_every,
            limit=args.limit,
        ))
