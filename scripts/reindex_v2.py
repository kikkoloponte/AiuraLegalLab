"""
Re-indicizzazione Fase 2 — legal_docs_v2 con intfloat/multilingual-e5-base (768 dim).

Legge aiura_legal_lab_db.chunks e indicizza nella nuova collezione Qdrant
legal_docs_v2 senza toccare legal_docs (v1, produzione).

Caratteristiche:
  - Skip-existing abilitato di default: il processo è idempotente e riprendibile
    in caso di interruzione (~2-4h su CUDA per ~2.9M chunk)
  - Progress checkpoint ogni 10k chunk su stderr (loguru)
  - BM25 non viene toccato: condivide gli indici attuali con v1
  - Solo Qdrant v2 viene aggiornato

Uso:
  python scripts/reindex_v2.py --workspace mio-studio
  python scripts/reindex_v2.py --workspace mio-studio --corpus normattiva
  python scripts/reindex_v2.py --workspace mio-studio --force-reindex   # no skip-existing
  python scripts/reindex_v2.py --workspace mio-studio --dry-run          # solo conta

Prerequisiti:
  pip install torch --index-url https://download.pytorch.org/whl/cu124
  pip install sentence-transformers
  # Il modello multilingual-e5-base (~1.1GB) viene scaricato automaticamente
  # da HuggingFace al primo avvio.
"""
import asyncio
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

from aiura_legal.core.retrieval.vector_retriever import VectorRetrieverV2
from aiura_legal.core.types import Document
from aiura_legal.ingestion.mongodb.client import MongoClient


async def reindex_v2(
    workspace: str,
    corpus: str | None = None,
    limit: int | None = None,
    force_reindex: bool = False,
    dry_run: bool = False,
    all_workspaces: bool = False,
) -> None:
    mongo = MongoClient.get()

    mongo_filter: dict = {}
    if not all_workspaces:
        mongo_filter["workspace"] = workspace
    if corpus:
        mongo_filter["corpus"] = corpus

    total = await mongo.count_chunks(filter_query=mongo_filter or None)
    effective = min(total, limit) if limit else total
    filter_desc = " | ".join(f"{k}={v}" for k, v in mongo_filter.items()) or "nessuno"

    logger.info(f"Chunk in aiura_legal.chunks: {total:,}  (filtro: {filter_desc})")
    logger.info(f"Da indicizzare in legal_docs_v2: {effective:,}")
    logger.info(f"Modello: intfloat/multilingual-e5-base (768 dim)")
    logger.info(f"Skip-existing: {'NO (force-reindex)' if force_reindex else 'SI'}")

    if dry_run:
        logger.info("DRY RUN — nessuna scrittura su Qdrant.")
        return

    _ws_base = os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
    ws_path = Path(_ws_base) / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    vector_v2 = VectorRetrieverV2(str(ws_path))
    current_count = vector_v2.count()
    logger.info(f"Qdrant v2: {current_count:,} punti già presenti in legal_docs_v2")

    batch: list[Document] = []
    count = 0
    upserted_total = 0

    async for chunk in mongo.iter_chunks(
        batch_size=500,
        filter_query=mongo_filter or None,
    ):
        if limit and count >= limit:
            break

        raw_text = chunk.get("text", "")
        if not raw_text or len(raw_text) < 20:
            continue

        titolo_art = chunk.get("titolo_articolo", "")
        titolo = chunk.get("titolo", "")
        prefix_parts = [p for p in [titolo, titolo_art] if p and p not in raw_text]
        text = "\n".join(prefix_parts + [raw_text]) if prefix_parts else raw_text

        doc = Document(
            id=str(chunk.get("_id", "")),
            text=text,
            source_id=chunk.get("source_id") or chunk.get("urn") or "",
            metadata={
                "corpus":     chunk.get("corpus", "studio"),
                "fonte":      chunk.get("fonte", "altro"),
                "testo_tipo": chunk.get("testo_tipo", "normativo"),
                "source":     chunk.get("source", ""),
                "titolo":     chunk.get("titolo", ""),
                "articolo":   chunk.get("articolo_num", ""),
                "valid_from": str(chunk.get("valid_from", "") or ""),
                "valid_to":   str(chunk.get("valid_to", "") or ""),
                "workspace":  chunk.get("workspace", workspace),
                "settore":    ",".join(chunk.get("settore") or []),
            },
        )
        batch.append(doc)
        count += 1

        if len(batch) >= 1000:
            before = vector_v2.count()
            vector_v2.add_documents_batch(batch, skip_existing=not force_reindex)
            after = vector_v2.count()
            upserted_total += (after - before)
            batch = []
            if count % 10_000 == 0:
                logger.info(
                    f"  {count:,}/{effective:,} chunk letti — "
                    f"{upserted_total:,} nuovi vettori in legal_docs_v2"
                )

    if batch:
        before = vector_v2.count()
        vector_v2.add_documents_batch(batch, skip_existing=not force_reindex)
        after = vector_v2.count()
        upserted_total += (after - before)

    vector_v2.save()

    final_count = vector_v2.count()
    logger.info(
        f"Re-indicizzazione completata: {count:,} chunk letti, "
        f"{upserted_total:,} nuovi vettori, "
        f"{final_count:,} totali in legal_docs_v2"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Re-indicizzazione Fase 2: legal_docs_v2 con multilingual-e5-base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python scripts/reindex_v2.py --workspace mio-studio
  python scripts/reindex_v2.py --workspace mio-studio --corpus normattiva
  python scripts/reindex_v2.py --workspace mio-studio --limit 5000 --dry-run
  python scripts/reindex_v2.py --workspace mio-studio --force-reindex
        """,
    )
    parser.add_argument("--workspace", default="mio-studio",
                        help="Nome workspace (default: mio-studio)")
    parser.add_argument("--corpus", default=None,
                        choices=["normattiva", "studio", "giurisprudenza", "dottrina"],
                        help="Limita a un corpus specifico (default: tutti)")
    parser.add_argument("--limit", type=int, default=None,
                        help="Numero massimo di chunk da processare")
    parser.add_argument("--force-reindex", action="store_true",
                        help="Disabilita skip-existing: ricalcola l'embedding di tutti i chunk")
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta i chunk senza scrivere su Qdrant")
    parser.add_argument("--all-workspaces", action="store_true",
                        help="Ignora il filtro workspace (indicizza tutti)")
    args = parser.parse_args()

    asyncio.run(reindex_v2(
        workspace=args.workspace,
        corpus=args.corpus,
        limit=args.limit,
        force_reindex=args.force_reindex,
        dry_run=args.dry_run,
        all_workspaces=args.all_workspaces,
    ))


if __name__ == "__main__":
    main()
