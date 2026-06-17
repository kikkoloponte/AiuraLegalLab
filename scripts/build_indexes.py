"""
Costruisce gli indici di retrieval dai chunk di aiura_legal.

══════════════════════════════════════════════════════════════
  REGOLA D'ORO — leggi prima di eseguire
══════════════════════════════════════════════════════════════

  build_indexes.py gestisce 3 corpus da aiura_legal.chunks:
    normattiva | dottrina | studio

  La giurisprudenza viene da uno script SEPARATO:
    → build_jurisprudence_indexes.py

  ┌─────────────────────────────────────────────────────────┐
  │  USO SICURO — aggiorna un solo corpus (NON resetta)     │
  │                                                         │
  │  python scripts/build_indexes.py \\                     │
  │      --workspace mio-studio --corpus normattiva         │
  │                                                         │
  │  BM25:   rimuove solo corpus=normattiva, reindicizza    │
  │  Qdrant: upsert (gli altri corpus restano intatti)      │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │  FULL REBUILD (richiede --reset-qdrant esplicito)       │
  │                                                         │
  │  Vedi: scripts/rebuild_all_indexes.py                   │
  │  Oppure esegui la sequenza manuale documentata lì.      │
  └─────────────────────────────────────────────────────────┘

  ⚠️  NON eseguire senza --corpus a meno di voler fare un
      full rebuild consapevole. Senza --corpus il BM25 viene
      resettato completamente. Qdrant NON viene mai resettato
      automaticamente: usa --reset-qdrant solo se sai cosa
      stai facendo (richiede poi rebuild_jurisprudence).

Filtraggio subset:
  --corpus normattiva     → solo chunk corpus="normattiva"
  --fonte legge dlgs      → solo chunk con fonte in (legge, dlgs)
  --testo-tipo normativo  → solo chunk testo_tipo="normativo" (esclude formule)
"""
import asyncio
import argparse
import os
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.core.types import Document
from aiura_legal.ingestion.mongodb.client import MongoClient


async def build(
    workspace: str,
    limit: int | None = None,
    corpus: str | None = None,
    fonti: list[str] | None = None,
    testo_tipo: str | None = None,
    skip_vector: bool = False,
    skip_bm25: bool = False,
    all_workspaces: bool = False,
    reset_qdrant: bool = False,
    force_reindex: bool = False,
) -> None:
    mongo = MongoClient.get()

    # Costruisce il filtro MongoDB
    mongo_filter: dict = {}
    if not all_workspaces:
        mongo_filter["workspace"] = workspace
    if corpus:
        mongo_filter["corpus"] = corpus
    if fonti:
        mongo_filter["fonte"] = {"$in": fonti}
    if testo_tipo:
        mongo_filter["testo_tipo"] = testo_tipo

    total = await mongo.count_chunks(filter_query=mongo_filter or None)
    effective = min(total, limit) if limit else total
    filter_desc = " | ".join(f"{k}={v}" for k, v in mongo_filter.items()) or "nessuno"
    logger.info(f"Chunk in aiura_legal.chunks: {total:,}  (filtro: {filter_desc})")
    logger.info(f"Da indicizzare: {effective:,}")

    if effective == 0:
        logger.warning(
            "Nessun chunk trovato. Esegui prima mirror_normattiva.py "
            "oppure verifica i filtri."
        )
        return

    _ws_base = os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
    ws_path = Path(_ws_base) / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    bm25   = BM25Retriever(str(ws_path)) if not skip_bm25   else None
    vector = VectorRetriever(str(ws_path)) if not skip_vector else None

    # ── BM25 reset strategy ──────────────────────────────────────────────
    #   Con --corpus X : rimuove solo i chunk di quel corpus, gli altri restano
    #   Senza --corpus  : reset completo (tutti i corpus spariscono — usa solo
    #                     per full rebuild, poi esegui anche build_jurisprudence)
    if bm25:
        if corpus:
            bm25._remove_corpus(corpus)
            logger.info(f"BM25: rimossi chunk corpus='{corpus}' (altri corpora conservati)")
        else:
            bm25._reset()
            logger.warning(
                "BM25: RESET COMPLETO — tutti i corpus rimossi. "
                "Ricorda di eseguire build_jurisprudence_indexes.py dopo."
            )

    # ── Qdrant reset strategy ────────────────────────────────────────────
    #   Di default Qdrant NON viene mai resettato automaticamente.
    #   Solo --reset-qdrant lo azzera esplicitamente.
    #   ⚠️  Se resetti Qdrant devi poi eseguire build_jurisprudence_indexes.py
    #       perché la giurisprudenza non è in aiura_legal.chunks.
    if vector:
        if reset_qdrant:
            try:
                vector._init_chroma()   # stub: cancella e ricrea collection
                logger.warning(
                    "Qdrant: collection RICREATA DA ZERO (--reset-qdrant). "
                    "Esegui build_jurisprudence_indexes.py per ripristinare la giurisprudenza."
                )
            except Exception as e:
                logger.warning(f"Reset Qdrant: {e}")
                vector._init_qdrant()
        else:
            logger.info(
                f"Qdrant: modalità UPSERT"
                + (f" corpus='{corpus}'" if corpus else " (tutti i corpus)")
                + " — collection esistente conservata"
            )

    if skip_vector:
        logger.info("Qdrant: SKIP (--skip-vector)")
    if skip_bm25:
        logger.info("BM25: SKIP (--skip-bm25)")

    batch: list[Document] = []
    count = 0

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
                "settore":    ",".join(chunk.get("settore") or []),
            },
        )
        batch.append(doc)
        count += 1

        if len(batch) >= 1000:
            if bm25:
                bm25.add_documents_batch(batch)
            if vector:
                vector.add_documents_batch(batch, skip_existing=not force_reindex)
            batch = []
            logger.info(f"  {count:,} chunk processati...")

    if batch:
        if bm25:
            bm25.add_documents_batch(batch)
        if vector:
            vector.add_documents_batch(batch, skip_existing=not force_reindex)

    if bm25:
        bm25.save()
    if vector:
        vector.save()

    logger.success(f"Build completato: {count:,} chunk indicizzati")
    if not skip_bm25:
        if corpus:
            logger.info(f"  BM25:    {ws_path}/indices/bm25_{corpus}.pkl")
        else:
            logger.info(f"  BM25:    {ws_path}/indices/bm25_{{normattiva,dottrina,studio,giurisprudenza}}.pkl")
    logger.info(f"  Meta:    {ws_path}/indices/bm25_meta.json")
    logger.info(f"  Vector:  {ws_path}/indices/qdrant/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build indexes da aiura_legal.chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Uso sicuro (aggiorna UN corpus senza toccare gli altri):
  python scripts/build_indexes.py --workspace mio-studio --corpus normattiva
  python scripts/build_indexes.py --workspace mio-studio --corpus dottrina
  python scripts/build_indexes.py --workspace mio-studio --corpus studio

Full rebuild (usa rebuild_all_indexes.py che gestisce l'ordine corretto):
  python scripts/rebuild_all_indexes.py --workspace mio-studio
        """,
    )
    parser.add_argument("--workspace", required=True, help="Nome workspace")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limita numero chunk (test)")
    parser.add_argument("--corpus", default=None,
                        choices=["normattiva", "studio", "dottrina", "giurisprudenza"],
                        help="Corpus da aggiornare (CONSIGLIATO — non tocca gli altri)")
    parser.add_argument("--fonte", nargs="+", default=None,
                        help="Filtra per fonte (es. --fonte legge dlgs)")
    parser.add_argument("--testo-tipo", default=None,
                        choices=["normativo", "formula"],
                        help="Filtra per testo_tipo")
    parser.add_argument("--skip-vector", action="store_true",
                        help="Salta Qdrant (solo BM25)")
    parser.add_argument("--skip-bm25", action="store_true",
                        help="Salta BM25 (solo Qdrant)")
    parser.add_argument("--all-workspaces", action="store_true",
                        help="Indicizza chunk di tutti i workspace")
    parser.add_argument("--reset-qdrant", action="store_true",
                        help=(
                            "⚠️  DISTRUTTIVO: azzera la collection Qdrant prima del rebuild. "
                            "Richiede poi build_jurisprudence_indexes.py per ripristinare "
                            "la giurisprudenza (non è in aiura_legal.chunks)."
                        ))
    parser.add_argument("--force-reindex", action="store_true",
                        help=(
                            "Forza re-embedding Qdrant anche per chunk già presenti. "
                            "Usare solo dopo un cambio del modello embedding. "
                            "Default: False (salta i chunk già in Qdrant per velocità)."
                        ))
    args = parser.parse_args()
    asyncio.run(build(
        workspace=args.workspace,
        limit=args.limit,
        corpus=args.corpus,
        fonti=args.fonte,
        testo_tipo=args.testo_tipo,
        skip_vector=args.skip_vector,
        skip_bm25=args.skip_bm25,
        all_workspaces=args.all_workspaces,
        reset_qdrant=args.reset_qdrant,
        force_reindex=args.force_reindex,
    ))
