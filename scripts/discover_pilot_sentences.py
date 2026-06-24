"""
Scoperta data-driven delle sentenze pilota per istituto — proposta di candidati
da confermare a mano nel registro (aiura_legal/core/istituti/registry.yaml).

Una sentenza "pilota" non è deducibile da una sola regola: è un giudizio in parte
editoriale. Questo tool propone candidati ordinandoli per segnali oggettivi:
  - SEZIONI UNITE (segnale più forte): la sezione contiene "unite"/"sez. u".
  - FREQUENZA DI CITAZIONE: quante altre sentenze del corpus la richiamano
    (n.<numero>/<anno> nel testo) → più è citata, più è nomofilattica.
  - PRESENZA NEL MASSIMARIO: l'Ufficio del Massimario digesta i principi pilota.

Due modi:
  # 1) candidati pilota per un istituto (usa i suoi termini_chiave dal registro)
  python scripts/discover_pilot_sentences.py --istituto dolo_eventuale_colpa_cosciente

  # 2) risolve il source_id GROUNDABILE di un pilota noto (massimario preferito):
  #    serve a riempire il campo source_id vuoto nel registro.
  python scripts/discover_pilot_sentences.py --pilota 10561/2014 --nome Gubert

Output: tabella di candidati con id chunk e segnali. La conferma (cosa è davvero
pilota e quale source_id usare) resta all'avvocato/curatore.
"""
from __future__ import annotations

import argparse
import asyncio
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import motor.motor_asyncio as motor
from loguru import logger

from aiura_legal.ingestion.mongodb.client import settings
from aiura_legal.core.istituti.registry import get_registry

_SSUU_RE = re.compile(r"(sez(?:ione|\.)?\s*unite|sezioni\s+unite|sez\.?\s*u\b)", re.IGNORECASE)
_MAX_CANDIDATES = 40   # cap per limitare i conteggi di citazione (costosi su 1.17M)


def _db():
    client = motor.AsyncIOMotorClient(settings.mongodb_uri)
    return client[settings.mongodb_database]


async def _count_citazioni(db, numero: str, anno: str) -> int:
    """Quante (altre) sentenze citano 'n.<numero>/<anno>' o '<numero> del ...<anno>'."""
    rx = re.compile(rf"\b{re.escape(numero)}\b[\s/.,]*(?:del\s+\d{{1,2}}/\d{{1,2}}/)?{re.escape(anno)}\b")
    return await db["chunks"].count_documents({
        "corpus": "giurisprudenza",
        "numero": {"$ne": numero},        # esclude i chunk della sentenza stessa
        "text": {"$regex": rx},
    })


async def _in_massimario(db, numero: str, anno: str) -> int:
    rx = re.compile(rf"\b{re.escape(numero)}\b.{{0,30}}{re.escape(anno)}")
    return await db["chunks"].count_documents({"corpus": "massimario", "text": {"$regex": rx}})


async def discover_for_istituto(istituto_id: str) -> None:
    reg = get_registry()
    ist = reg.by_id(istituto_id)
    if not ist:
        logger.error(f"Istituto sconosciuto: {istituto_id!r}. Disponibili: {[i.id for i in reg.all()]}")
        return
    if not ist.termini_chiave:
        logger.error(f"L'istituto {istituto_id!r} non ha termini_chiave per la ricerca.")
        return

    db = _db()
    # Candidati: chunk giurisprudenza SS.UU. che matchano i termini dell'istituto.
    term_rx = re.compile("|".join(re.escape(t) for t in ist.termini_chiave), re.IGNORECASE)
    cursor = db["chunks"].find(
        {"corpus": "giurisprudenza", "text": {"$regex": term_rx}, "sezione": {"$regex": _SSUU_RE}},
        {"source_id": 1, "numero": 1, "anno": 1, "sezione": 1, "text": 1},
    ).limit(400)

    # Deduplica per (numero, anno): una sentenza = molti chunk.
    seen: dict[tuple[str, str], dict] = {}
    async for c in cursor:
        key = (str(c.get("numero", "")), str(c.get("anno", "")))
        if key == ("", "") or key in seen:
            continue
        seen[key] = c
        if len(seen) >= _MAX_CANDIDATES:
            break

    logger.info(f"Istituto {istituto_id!r}: {len(seen)} sentenze SS.UU. candidate — calcolo segnali...")
    rows = []
    for (numero, anno), c in seen.items():
        cit = await _count_citazioni(db, numero, anno)
        mass = await _in_massimario(db, numero, anno)
        rows.append((cit, mass, numero, anno, c.get("source_id", ""), (c.get("sezione") or "")))

    rows.sort(key=lambda r: (r[0] + r[1] * 5), reverse=True)   # massimario pesa di più
    print(f"\n=== Candidati pilota per '{istituto_id}' (ordinati per rilevanza nomofilattica) ===")
    print(f"{'citaz':>6} {'mass':>5}  {'sentenza':<16} {'source_id':<22} sezione")
    for cit, mass, numero, anno, sid, sez in rows[:20]:
        print(f"{cit:>6} {mass:>5}  Cass. {numero}/{anno:<8} {sid:<22} {sez[:30]}")
    print("\nConferma i veri piloti nel registro (registry.yaml). Per il source_id "
          "groundabile usa: --pilota <numero>/<anno>")


async def resolve_source(pilota: str, nome: str = "") -> None:
    """Trova i chunk GROUNDABILI (massimario preferito) che riportano il pilota,
    da incollare come source_id nel registro."""
    numero, _, anno = pilota.partition("/")
    numero, anno = numero.strip(), anno.strip()
    db = _db()
    rx_terms = [rf"\b{re.escape(numero)}\b.{{0,30}}{re.escape(anno)}"]
    if nome:
        rx_terms.append(re.escape(nome))
    rx = re.compile("|".join(rx_terms), re.IGNORECASE)

    for corpus in ("massimario", "giurisprudenza"):
        cursor = db["chunks"].find(
            {"corpus": corpus, "text": {"$regex": rx}},
            {"source_id": 1, "text": 1},
        ).limit(8)
        print(f"\n=== {corpus.upper()} — chunk groundabili per Cass. {numero}/{anno}"
              + (f" ({nome})" if nome else "") + " ===")
        found = False
        async for c in cursor:
            found = True
            snippet = (c.get("text") or "")[:150].replace("\n", " ")
            print(f"  source_id: {c.get('source_id')!r}\n     {snippet!r}")
        if not found:
            print("  (nessun chunk)")


async def main(args: argparse.Namespace) -> None:
    if args.pilota:
        await resolve_source(args.pilota, args.nome or "")
    elif args.istituto:
        await discover_for_istituto(args.istituto)
    else:
        reg = get_registry()
        print("Istituti nel registro:")
        for i in reg.all():
            n_piloti = len(i.sentenze_pilota)
            print(f"  {i.id}  ({i.settore})  piloti={n_piloti}")
        print("\nUsa --istituto <id> per scoprire candidati, o --pilota <numero>/<anno> per il source_id.")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Scoperta data-driven delle sentenze pilota")
    p.add_argument("--istituto", help="id istituto dal registro (registry.yaml)")
    p.add_argument("--pilota", help="numero/anno di un pilota noto, es. 10561/2014")
    p.add_argument("--nome", help="nome del pilota (es. Gubert) per allargare la ricerca")
    asyncio.run(main(p.parse_args()))
