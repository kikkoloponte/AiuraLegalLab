"""
Risolve i 331 chunk lasciati a __URNFIX_TMP__ da fix_normattiva_urn_mismatch.py.

Analisi (sessione 2026-06-22) ha rivelato 3 cause distinte per i 273 URN
originali bloccati, tutte risolvibili senza intervento manuale caso-per-caso:

1. BUG REGEX bis.N: `_ARTICOLO_NUM_RE` in urn_fix.py non cattura il suffisso
   decimale dopo bis/ter/... (es. "Art. 90-bis.1", "Art. 90-bis.2"), quindi
   90-bis, 90-bis.1, 90-bis.2 collassano tutti su "~art90bis" → falsa
   ambiguità a 3 vie. Fix: regex estesa per includere ".N" nel suffisso.

2. STUB ABROGATO vs CONTENUTO REALE: quando 2 originali correggono allo
   stesso URN, in ~44+19 casi uno dei due è uno stub "ARTICOLO ABROGATO
   DALLA L. ..." (nessun valore legale, nessun valore per il retrieval) e
   l'altro ha contenuto normativo reale. Lo stub perde lo slot canonico e
   va archiviato con suffisso "#abrogato" (resta nei chunk, ma source_id
   non valido come URN → invisibile a BM25/Vector, coerente con l'assenza
   di valore giuridico di un articolo abrogato).

3. CATENE LUNGHE (shift sequenziali in Codice Civile/Proc.Civile/Proc.Penale
   dopo abrogazioni, es. L. 218/1995): una volta risolte (1) e (2), molte
   ambiguità si sciolgono e liberano gli slot per la catena successiva.
   Per questo il merge si esegue iterativamente fino a stabilità.

Dopo l'iterazione, i gruppi con >=2 originali ENTRAMBI con contenuto
normativo reale (non stub) sono GENUINE duplicazioni non risolvibili
automaticamente: restano a placeholder e vengono riportati per revisione
manuale (atteso: 0 o pochissimi, da verificare con --dry-run).

Uso:
  python scripts/resolve_urnfix_collisions.py --dry-run
  python scripts/resolve_urnfix_collisions.py --apply
"""
from __future__ import annotations

import argparse
import asyncio
import re
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

_TMP_PREFIX = "__URNFIX_TMP__"
_ABROGATO_RE = re.compile(r"ARTICOLO\s+ABROGAT[OA]", re.IGNORECASE)

_URN_ART_RE = re.compile(r"^(.*~art)(\d+)([a-z]*(?:\.\d+)?)$", re.IGNORECASE)
_ARTICOLO_NUM_RE = re.compile(
    r"art\.?\s*(\d+)\s*[\-\s]?\s*"
    r"(bis(?:\.\d+)?|ter(?:\.\d+)?|quater(?:\.\d+)?|quinquies(?:\.\d+)?|"
    r"sexies(?:\.\d+)?|septies(?:\.\d+)?|octies(?:\.\d+)?)?",
    re.IGNORECASE,
)


_TEXT_HEADER_RE = re.compile(
    r"^\s*\(*\s*Art\.?\s*(\d+)\s*[\-\s]?\s*"
    r"(bis(?:\.\d+)?|ter(?:\.\d+)?|quater(?:\.\d+)?|quinquies(?:\.\d+)?|"
    r"sexies(?:\.\d+)?|septies(?:\.\d+)?|octies(?:\.\d+)?)?",
    re.IGNORECASE,
)


def correct_article_urn_v2(urn: str, articolo_num: str, text: str = "") -> str:
    """
    Variante di correct_article_urn che distingue i suffissi decimali bis.N.

    `articolo_num` (estratto dal markup HTML della pagina) tronca spesso il
    suffisso decimale (es. "Art. 270-quater." per un testo che è in realtà
    "270-quater.1") — il caveat originale assumeva fosse affidabile, ma non
    lo è per gli articoli con sotto-numerazione introdotta da riforme
    recenti (es. L. 134/2021 sull'art. 90-bis c.p.p.). La prima riga del
    campo `text` riporta invece l'header originale completo ed è quindi
    la fonte di verità preferita quando disponibile e parsabile.
    """
    m_urn = _URN_ART_RE.match(urn)
    if not m_urn:
        return urn
    prefix, urn_num, urn_suffix = m_urn.groups()

    m_art = _TEXT_HEADER_RE.search((text or "").lstrip()[:50])
    if not m_art:
        m_art = _ARTICOLO_NUM_RE.search(articolo_num or "")
    if not m_art:
        return urn
    real_num, real_suffix_raw = m_art.groups()
    real_suffix = (real_suffix_raw or "").strip().lower().replace(" ", "").replace("-", "")
    urn_suffix_norm = (urn_suffix or "").strip().lower().replace(".", "")
    real_suffix_norm = real_suffix.replace(".", "")

    if real_num == urn_num and real_suffix_norm == urn_suffix_norm:
        return urn
    return f"{prefix}{real_num}{real_suffix}"


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply and not args.dry_run:
        args.dry_run = True

    client = motor.AsyncIOMotorClient(settings.legalagentlab_mongodb_uri)
    coll = client[settings.legalagentlab_mongodb_database]["normattiva_docs"]

    docs_by_urn: dict[str, dict] = {}
    async for doc in coll.find({}, {"urn": 1, "articolo_num": 1, "text": 1, "_id": 0}):
        urn = doc.get("urn", "") or ""
        docs_by_urn[urn] = doc

    target_groups: dict[str, list[str]] = defaultdict(list)
    for urn, doc in docs_by_urn.items():
        corrected = correct_article_urn_v2(urn, doc.get("articolo_num", "") or "", doc.get("text", "") or "")
        target_groups[corrected].append(urn)

    # Risolvi ambiguità: stub abrogato perde, contenuto reale vince.
    final_map: dict[str, str] = {}      # old_urn -> nuovo source_id finale (URN o archiviato)
    unresolved_groups: list[tuple[str, list[str]]] = []
    for corrected, originals in target_groups.items():
        if len(originals) == 1:
            original = originals[0]
            if original != corrected:
                final_map[original] = corrected
            continue

        real_content = [o for o in originals if not _ABROGATO_RE.search(docs_by_urn[o].get("text", "") or "")]
        stubs = [o for o in originals if o not in real_content]

        if len(real_content) == 1:
            final_map[real_content[0]] = corrected
            for s in stubs:
                final_map[s] = f"{corrected}#abrogato"
        elif len(real_content) == 0:
            # tutti stub: nessuna perdita di contenuto, archivia tutti tranne il primo
            final_map[originals[0]] = corrected
            for s in originals[1:]:
                final_map[s] = f"{corrected}#abrogato"
        else:
            unresolved_groups.append((corrected, originals))

    logger.info(
        f"Gruppi totali: {len(target_groups)} | "
        f"correzioni mappate: {len(final_map)} | "
        f"gruppi non risolvibili (duplicazione reale): {len(unresolved_groups)}"
    )
    for corrected, originals in unresolved_groups:
        logger.warning(f"[MANUAL REVIEW] target={corrected} originali={originals}")

    mongo = MongoClient.get()
    chunks = mongo.db["chunks"]

    rows = await chunks.find(
        {"source_id": {"$regex": f"^{_TMP_PREFIX}"}}, {"_id": 1, "source_id": 1}
    ).to_list(length=None)
    stuck_old_urns = {r["source_id"][len(_TMP_PREFIX):] for r in rows}
    logger.info(f"Chunk attualmente a placeholder TMP: {len(rows)} ({len(stuck_old_urns)} URN distinti)")

    # Iterazione: applica le mosse il cui target finale è libero, finché non si stabilizza.
    pending = {u: final_map[u] for u in stuck_old_urns if u in final_map}
    no_map = stuck_old_urns - pending.keys()
    if no_map:
        logger.warning(f"{len(no_map)} URN bloccati senza mappatura calcolata (verificare): {list(no_map)[:10]}")

    applied: dict[str, str] = {}
    rounds = 0
    progress = True
    while progress and pending:
        progress = False
        rounds += 1
        for old_urn, new_id in list(pending.items()):
            occ = await chunks.find_one({"source_id": new_id, "corpus": "normattiva"})
            if occ is None:
                applied[old_urn] = new_id
                del pending[old_urn]
                progress = True
                if not args.dry_run:
                    tmp_id = f"{_TMP_PREFIX}{old_urn}"
                    await chunks.update_many(
                        {"source_id": tmp_id, "corpus": "normattiva"},
                        {"$set": {"source_id": new_id}},
                    )

    logger.success(
        f"{'[DRY-RUN] ' if args.dry_run else ''}Rounds: {rounds} | "
        f"Risolti: {len(applied)} | Ancora bloccati: {len(pending)}"
    )
    for old_urn, new_id in list(pending.items())[:20]:
        occ = await chunks.find_one({"source_id": new_id, "corpus": "normattiva"})
        logger.warning(f"[STILL BLOCKED] {old_urn} -> {new_id} (occupato da chunk reale non in coda)")

    if args.dry_run:
        logger.info("Dry-run completato. Per applicare: --apply")


if __name__ == "__main__":
    asyncio.run(main())
