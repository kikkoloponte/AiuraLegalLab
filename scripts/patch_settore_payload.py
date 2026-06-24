#!/usr/bin/env python3
"""patch_settore_payload.py — Aggiorna SOLO il campo `settore` su BM25 + Qdrant v2
esistenti, leggendo il valore corrente da MongoDB.

Perché serve: build_indexes.py / reindex_v2.py / build_jurisprudence_indexes.py
con skip_existing=True (default) saltano interamente i chunk già indicizzati —
niente upsert, niente payload nuovo. Questo script NON fa re-embedding: aggiorna
solo i metadata in-place (BM25: doc_metadata list nel pkl; Qdrant: set_payload,
zero costo GPU).

Uso:
  python scripts/patch_settore_payload.py --workspace mio-studio --corpus giurisprudenza
  python scripts/patch_settore_payload.py --workspace mio-studio --corpus normattiva,dottrina,giurisprudenza --target qdrant
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from bson import ObjectId
from loguru import logger

from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetrieverV2, _to_qdrant_id, _COLLECTION_V2
from aiura_legal.ingestion.mongodb.client import MongoClient

_WORKSPACES_BASE = Path(
    os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
)


def _settore_str(chunk: dict) -> str:
    return ",".join(chunk.get("settore") or [])


async def _fetch_settore_map(corpus: str, ids: list[str]) -> dict[str, str]:
    """Batch lookup settore da MongoDB per una lista di chunk _id (stringa)."""
    mongo = MongoClient.get()
    coll = mongo.db["chunks"]
    obj_ids = [ObjectId(i) for i in ids if ObjectId.is_valid(i)]
    out: dict[str, str] = {}
    BATCH = 2000
    for start in range(0, len(obj_ids), BATCH):
        batch = obj_ids[start:start + BATCH]
        async for doc in coll.find({"_id": {"$in": batch}}, {"_id": 1, "settore": 1}):
            out[str(doc["_id"])] = _settore_str(doc)
    return out


async def patch_bm25(workspace: str, corpus: str) -> None:
    ws_path = _WORKSPACES_BASE / workspace
    bm25 = BM25Retriever(str(ws_path))
    sub = bm25._subs.get(corpus)
    if sub is None:
        logger.warning(f"BM25: nessun sub-indice per corpus={corpus}")
        return
    if sub.index_path.exists() and not sub.doc_ids:
        sub.load()
    if not sub.doc_ids:
        logger.warning(f"BM25[{corpus}]: indice vuoto, niente da patchare")
        return

    logger.info(f"BM25[{corpus}]: {len(sub.doc_ids):,} doc — lookup settore da MongoDB...")
    settore_map = await _fetch_settore_map(corpus, sub.doc_ids)
    logger.info(f"BM25[{corpus}]: {len(settore_map):,} chunk trovati in MongoDB")

    updated = 0
    for i, doc_id in enumerate(sub.doc_ids):
        new_settore = settore_map.get(doc_id, "")
        if sub.doc_metadata[i].get("settore") != new_settore:
            sub.doc_metadata[i]["settore"] = new_settore
            updated += 1

    logger.info(f"BM25[{corpus}]: {updated:,} doc_metadata aggiornati — salvo pkl (no rebuild bm25s)")
    sub._save_state()  # salva senza toccare il modello bm25s tokenizzato (dirty resta invariato)
    logger.success(f"BM25[{corpus}]: patch completata")


async def patch_qdrant_v2(workspace: str, corpus: str) -> None:
    mongo = MongoClient.get()
    coll = mongo.db["chunks"]
    mongo_filter = {"corpus": corpus, "workspace": workspace}
    total = await coll.count_documents(mongo_filter)
    logger.info(f"Qdrant v2[{corpus}]: {total:,} chunk in MongoDB da sincronizzare")
    if total == 0:
        logger.warning(f"Qdrant v2[{corpus}]: nessun chunk con workspace={workspace}, provo senza filtro workspace")
        mongo_filter = {"corpus": corpus}
        total = await coll.count_documents(mongo_filter)
        logger.info(f"Qdrant v2[{corpus}]: {total:,} chunk (senza filtro workspace)")
    if total == 0:
        return

    vector = VectorRetrieverV2(str(_WORKSPACES_BASE / workspace))
    if not vector._client:
        logger.error("Qdrant v2: client non disponibile")
        return

    BATCH = 1000
    # Qdrant ha un bug noto nel motore gridstore (on_disk_payload=true) che può
    # panicare con "New page has just been created" sotto set_payload rapide e
    # ravvicinate. La collection resta sana (status green, nessuna perdita dati),
    # ma la singola richiesta fallisce con 500 — retry con backoff + piccola pausa
    # tra i punti per valore distinto riduce la frequenza del problema.
    import asyncio as _asyncio
    from qdrant_client.http.exceptions import UnexpectedResponse

    corrupted_points: list[tuple[str, str]] = []  # (point_id, errore) — segnalati a fine corpus

    async def _set_payload_with_retry(point_ids: list[str], sval: str, max_retries: int = 5) -> None:
        last_err: Exception | None = None
        for attempt in range(max_retries):
            try:
                vector._client.set_payload(
                    collection_name=_COLLECTION_V2,
                    payload={"settore": sval},
                    points=point_ids,
                )
                return
            except UnexpectedResponse as e:
                msg = str(e)
                last_err = e
                if "Not found" in msg or "404" in msg:
                    # Punto Mongo senza corrispondente in Qdrant v2 (mai embeddato,
                    # es. testo troppo corto in reindex_v2.py). Non è retryable:
                    # bisezione per isolare il/i punto/i mancante/i.
                    if len(point_ids) == 1:
                        logger.debug(f"Qdrant v2[{corpus}]: punto {point_ids[0]} non trovato, skip")
                        return
                    mid = len(point_ids) // 2
                    await _set_payload_with_retry(point_ids[:mid], sval, max_retries)
                    await _set_payload_with_retry(point_ids[mid:], sval, max_retries)
                    return
                if "panicked" not in msg and "500" not in msg:
                    raise
                wait = 0.5 * (2 ** attempt)
                logger.warning(
                    f"Qdrant v2[{corpus}]: set_payload fallito (tentativo {attempt+1}/{max_retries}), "
                    f"retry in {wait:.1f}s — {e}"
                )
                await _asyncio.sleep(wait)
        # Panic persistente dopo tutti i retry: probabile segmento/punto corrotto
        # nello storage Qdrant, non un errore transitorio. Bisezione per isolare
        # il/i punto/i corrotto/i invece di abortire l'intero job — il resto del
        # corpus deve poter completare.
        if len(point_ids) == 1:
            logger.error(
                f"Qdrant v2[{corpus}]: punto {point_ids[0]} PROBABILMENTE CORROTTO "
                f"(panic persistente dopo {max_retries} tentativi) — skip. Errore: {last_err}"
            )
            corrupted_points.append((point_ids[0], str(last_err)))
            return
        mid = len(point_ids) // 2
        await _set_payload_with_retry(point_ids[:mid], sval, max_retries)
        await _set_payload_with_retry(point_ids[mid:], sval, max_retries)

    cursor = coll.find(mongo_filter, {"_id": 1, "settore": 1})
    batch_ids: list[str] = []
    batch_settore: list[str] = []
    patched = 0

    async def _flush() -> None:
        nonlocal patched
        if not batch_ids:
            return
        # set_payload raggruppato per valore di settore (stesso payload → meno chiamate)
        by_value: dict[str, list[str]] = {}
        for cid, sval in zip(batch_ids, batch_settore):
            by_value.setdefault(sval, []).append(_to_qdrant_id(cid))
        for sval, point_ids in by_value.items():
            await _set_payload_with_retry(point_ids, sval)
            # Pausa tra batch: il bug gridstore (on_disk_payload=true) causa WAL
            # inconsistente sotto set_payload rapidi — aumentare se si vedono panic.
            # Con on_disk_payload=False (nuovo default) la pausa non è più necessaria
            # ma la manteniamo per sicurezza contro collection create con vecchio config.
            await _asyncio.sleep(0.2)
        patched += len(batch_ids)
        batch_ids.clear()
        batch_settore.clear()

    async for doc in cursor:
        batch_ids.append(str(doc["_id"]))
        batch_settore.append(_settore_str(doc))
        if len(batch_ids) >= BATCH:
            await _flush()
            if patched % (BATCH * 10) == 0:
                logger.info(f"Qdrant v2[{corpus}]: {patched:,}/{total:,} patchati...")
    await _flush()

    logger.success(f"Qdrant v2[{corpus}]: {patched:,} payload aggiornati")
    if corrupted_points:
        logger.error(
            f"Qdrant v2[{corpus}]: {len(corrupted_points)} punti PROBABILMENTE CORROTTI "
            f"saltati — verifica integrità storage prima di considerare l'indice attendibile:"
        )
        for pid, err in corrupted_points:
            logger.error(f"  {pid}: {err}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Patch payload-only del campo settore (no re-embedding)")
    parser.add_argument("--workspace", default="mio-studio")
    parser.add_argument("--corpus", default="normattiva,dottrina,giurisprudenza",
                         help="Lista corpus separati da virgola")
    parser.add_argument("--target", default="all", choices=["all", "bm25", "qdrant"],
                         help="Cosa patchare (default: all)")
    args = parser.parse_args()

    corpora = [c.strip() for c in args.corpus.split(",") if c.strip()]
    logger.info(f"patch_settore_payload — workspace={args.workspace} corpus={corpora} target={args.target}")

    for corpus in corpora:
        if args.target in ("all", "bm25"):
            await patch_bm25(args.workspace, corpus)
        if args.target in ("all", "qdrant"):
            await patch_qdrant_v2(args.workspace, corpus)

    logger.success("Patch completata per tutti i corpus richiesti.")


if __name__ == "__main__":
    asyncio.run(main())
