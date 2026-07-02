"""
Ri-verifica e corregge i source_mongo_id di quadro_normativo.articoli_principali
nella collection istituti_giuridici.

Motivo: source_mongo_id è un MongoDB _id catturato al momento della mappatura.
Un successivo rebuild dei chunk (NormattivaPipeline.chunk_collection(), upsert
per source_id/chunk_index) può sovrascrivere il contenuto sotto lo stesso _id
con un articolo diverso, perché l'URN del fetcher è posizionale (posizione
nella catena di navigazione) e non un identificatore stabile del vero
articolo legislativo — vedi commit sul fix del fallback N2Ls.

Per ogni articolo principale:
  1. Estrae il numero atteso dal campo "riferimento" (es. "Art. 79 c.c." -> "79")
  2. Cerca nel corpus normattiva il/i chunk con quel articolo_num esatto per
     il codice giusto (titolo regex da codice_riferimento)
  3. Se trova ESATTAMENTE un articolo (eventualmente più chunk per split del
     testo, ma un solo articolo distinto) e il source_mongo_id salvato non
     corrisponde già a quell'articolo, propone la correzione
  4. Se non trova nulla o trova ambiguità, lascia intatto e logga per verifica manuale

Uso:
  python scripts/fix_istituti_source_ids.py --dry-run   # mostra le correzioni, non scrive
  python scripts/fix_istituti_source_ids.py --apply      # applica le correzioni sicure
"""
from __future__ import annotations

import argparse
import asyncio

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from aiura_legal.ingestion.normattiva.chunk_id import normalize_articolo_num

_MONGO_URI = "mongodb://localhost:27017"
_DB_NAME = "aiura_legal_lab_db"

_CODICE_TITOLO_REGEX = {
    "CC": "REGIO DECRETO 16 marzo 1942",
    "CP": "REGIO DECRETO 19 ottobre 1930",
    "CPP": "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988",
    "CPC": "28 ottobre 1940",
}


def _extract_expected_number(riferimento: str) -> str | None:
    """Usa la stessa normalizzazione di compute_deterministic_chunk_id, così
    il confronto con articolo_num del chunk è consistente (stessa gestione
    di -bis/-ter/punteggiatura)."""
    normalized = normalize_articolo_num(riferimento)
    return normalized or None


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        args.dry_run = True

    client = AsyncIOMotorClient(_MONGO_URI)
    db = client[_DB_NAME]
    istituti_coll = db["istituti_giuridici"]
    chunks_coll = db["chunks"]

    total_articoli = 0
    already_ok = 0
    corrected = 0
    unresolved: list[tuple[str, str]] = []
    ambiguous: list[tuple[str, str, int]] = []

    async for ist in istituti_coll.find({}):
        codice = str(ist.get("codice_riferimento", "")).strip().upper()
        titolo_regex = _CODICE_TITOLO_REGEX.get(codice)
        if not titolo_regex:
            continue

        articoli = (ist.get("quadro_normativo") or {}).get("articoli_principali") or []
        changed = False
        for art in articoli:
            riferimento = str(art.get("riferimento", ""))
            current_id = art.get("source_mongo_id")
            expected_num = _extract_expected_number(riferimento)
            if not expected_num or not current_id:
                continue
            total_articoli += 1

            # Verifica lo stato attuale del chunk salvato
            try:
                current_chunk = await chunks_coll.find_one({"_id": ObjectId(current_id)})
            except Exception:
                current_chunk = None
            current_articolo_num = normalize_articolo_num(
                (current_chunk or {}).get("articolo_num", "")
            )
            if current_chunk and current_articolo_num == expected_num:
                already_ok += 1
                continue

            # Cerca il chunk giusto per (fonte, articolo_num atteso)
            cursor = chunks_coll.find(
                {
                    "corpus": "normattiva",
                    "titolo": {"$regex": titolo_regex},
                },
                {"articolo_num": 1},
            )
            matches: set[str] = set()
            match_ids: list[str] = []
            async for c in cursor:
                if normalize_articolo_num(c.get("articolo_num", "")) == expected_num:
                    matches.add(str(c["_id"]))
                    match_ids.append(str(c["_id"]))
            distinct_articles = len(matches)

            if distinct_articles == 0:
                unresolved.append((ist["denominazione"], riferimento))
                continue

            new_id = match_ids[0]
            if new_id == str(current_id):
                already_ok += 1
                continue

            corrected += 1
            print(
                f"[FIX] {ist['denominazione']!r} | {riferimento} | "
                f"{current_id} (era: {current_articolo_num or 'NON TROVATO'}) -> {new_id}"
            )
            if args.apply:
                art["source_mongo_id"] = new_id
                changed = True

        if changed and args.apply:
            await istituti_coll.update_one(
                {"_id": ist["_id"]},
                {"$set": {"quadro_normativo.articoli_principali": articoli}, "$inc": {"version": 1}},
            )

    print()
    print(f"Totale articoli controllati: {total_articoli}")
    print(f"Già corretti: {already_ok}")
    print(f"{'Da correggere' if args.dry_run else 'Corretti'}: {corrected}")
    print(f"Irrisolti (nessun match trovato, richiede verifica manuale): {len(unresolved)}")
    for denom, rif in unresolved[:30]:
        print(f"  - {denom!r}: {rif}")


if __name__ == "__main__":
    asyncio.run(main())
