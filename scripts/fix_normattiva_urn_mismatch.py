"""
Corregge il source_id dei chunk già indicizzati con URN mismatch (vedi
aiura_legal/ingestion/normattiva/urn_fix.py per la causa: scraper LegalAgentLab
usa un contatore sequenziale invece del vero numero d'articolo).

Applica SOLO le correzioni sicure (nessuna collisione — vedi urn_fix.py per
il caveat sulla numerazione che riparte da 1 per sezione in Codice Civile e
affini). I casi ambigui non vengono toccati.

Uso:
  python scripts/fix_normattiva_urn_mismatch.py --dry-run
  python scripts/fix_normattiva_urn_mismatch.py --apply

Dopo --apply, propaga a BM25 + Vector con:
  python scripts/build_indexes.py --workspace mio-studio --corpus normattiva
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from loguru import logger
import motor.motor_asyncio as motor
from pymongo import UpdateOne

from aiura_legal.ingestion.mongodb.client import MongoClient, settings
from aiura_legal.ingestion.normattiva.urn_fix import correct_article_urn


async def _compute_safe_correction_map() -> dict[str, str]:
    """
    Rilegge legal_lab.normattiva_docs (fonte di verità read-only) e calcola
    le correzioni URN sicure: esclude i gruppi target con più di un URN
    originale (collisione di numerazione — vedi urn_fix.py).
    """
    client = motor.AsyncIOMotorClient(settings.legalagentlab_mongodb_uri)
    coll = client[settings.legalagentlab_mongodb_database]["normattiva_docs"]

    target_groups: dict[str, list[str]] = defaultdict(list)
    cursor = coll.find({}, {"urn": 1, "articolo_num": 1})
    async for doc in cursor:
        urn = doc.get("urn", "") or ""
        articolo_num = doc.get("articolo_num", "") or ""
        corrected = correct_article_urn(urn, articolo_num)
        target_groups[corrected].append(urn)

    safe_map: dict[str, str] = {}
    skipped_ambiguous = 0
    for corrected, originals in target_groups.items():
        if len(originals) > 1:
            skipped_ambiguous += len(originals)
            continue
        original = originals[0]
        if original != corrected:
            safe_map[original] = corrected

    logger.info(
        f"Correzioni sicure: {len(safe_map)}  |  "
        f"documenti saltati per ambiguità (collisione numerazione): {skipped_ambiguous}"
    )
    return safe_map


_TMP_PREFIX = "__URNFIX_TMP__"


async def _apply_to_chunks(safe_map: dict[str, str], dry_run: bool) -> None:
    """
    Rename a due fasi via placeholder temporaneo: le correzioni formano catene
    di shift concatenati (es. art68->67, art69->68, art70->69, ...), quindi un
    rename diretto in una sola passata trova quasi sempre il target "già
    occupato" dal record che a sua volta deve spostarsi. Spostando prima tutto
    su un placeholder univoco (derivato dall'old_urn, impossibile collida) e
    poi dal placeholder al target finale, l'ordine di elaborazione non conta
    più: a inizio fase 2 nessuno dei vecchi source_id esiste ancora.
    """
    mongo = MongoClient.get()
    chunks = mongo.db["chunks"]

    # Fase 1: old_urn -> placeholder
    moved_to_tmp: dict[str, list[dict]] = {}
    for old_urn in safe_map:
        rows = await chunks.find(
            {"corpus": "normattiva", "source_id": old_urn},
            {"_id": 1, "chunk_index": 1, "workspace": 1},
        ).to_list(length=None)
        if not rows:
            continue
        moved_to_tmp[old_urn] = rows
        if not dry_run:
            tmp_id = f"{_TMP_PREFIX}{old_urn}"
            ops = [UpdateOne({"_id": r["_id"]}, {"$set": {"source_id": tmp_id}}) for r in rows]
            await chunks.bulk_write(ops, ordered=False)

    total_docs_with_chunks = len(moved_to_tmp)
    total_chunks_affected = sum(len(rows) for rows in moved_to_tmp.values())

    # Fase 2: placeholder -> new_urn, con verifica finale anti-collisione
    docs_completed = 0
    chunks_completed = 0
    skipped_real_collision = 0
    for old_urn, rows in moved_to_tmp.items():
        new_urn = safe_map[old_urn]

        # Collisione reale residua: il target è occupato da un chunk che NON
        # fa parte di questa migrazione. Se new_urn è ESSO STESSO una chiave
        # della mappa (cioè un altro anello della stessa catena di shift,
        # es. art68->67 mentre art67->66), chi occupa quello slot in questo
        # momento è destinato a spostarsi a sua volta in fase 1/2 — non è una
        # collisione reale, e questo vale sia in dry-run (nulla è stato
        # ancora spostato) sia in --apply (a fine fase 1 lo slot è libero).
        if new_urn not in safe_map:
            real_collision = await chunks.find_one({
                "source_id": new_urn,
                "corpus": "normattiva",
            })
            if real_collision:
                logger.warning(
                    f"[SKIP] {old_urn} -> {new_urn}: occupato da un chunk esterno "
                    f"alla migrazione — lascio al placeholder per ispezione manuale."
                )
                skipped_real_collision += 1
                continue

        docs_completed += 1
        chunks_completed += len(rows)
        if not dry_run:
            tmp_id = f"{_TMP_PREFIX}{old_urn}"
            ops = [UpdateOne({"_id": r["_id"]}, {"$set": {"source_id": new_urn}}) for r in rows]
            await chunks.bulk_write(ops, ordered=False)

    logger.success(
        f"{'[DRY-RUN] ' if dry_run else ''}Documenti normativi: {total_docs_with_chunks} candidati, "
        f"{docs_completed} corretti, {skipped_real_collision} lasciati al placeholder per collisione reale  |  "
        f"Chunk candidati: {total_chunks_affected}, chunk corretti: {chunks_completed}"
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Conta senza scrivere (default)")
    parser.add_argument("--apply", action="store_true", help="Applica le correzioni sui chunk")
    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        logger.info("Nessun flag specificato — eseguo in modalità --dry-run.")
        args.dry_run = True

    safe_map = await _compute_safe_correction_map()
    await _apply_to_chunks(safe_map, dry_run=not args.apply)

    if args.dry_run:
        logger.info(
            "Dry-run completato. Per applicare: "
            "python scripts/fix_normattiva_urn_mismatch.py --apply"
        )


if __name__ == "__main__":
    asyncio.run(main())
