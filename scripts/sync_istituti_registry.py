"""
Sincronizza il registro degli istituti (aiura_legal/core/istituti/registry.yaml)
con la collection MongoDB istituti_giuridici (CRUD UI, 144 istituti mappati sui
4 codici maggiori).

Il registro esistente resta l'unica fonte usata a runtime (IstitutoRegistry,
match_query() in analyst.py) — questo script non tocca il codice di orchestrazione,
solo il file YAML: aggiunge nuove voci e fonde quelle che si sovrappongono a
istituti già curati a mano, preservando sentenze_pilota e disambigua_da esistenti
(mai fabbricati automaticamente).

norme_urn del registro = campo source_id (URN) del chunk, NON il MongoDB _id.
Gli istituti_giuridici salvano invece source_mongo_id (l'_id) nei loro
articoli_principali: questo script risolve _id -> source_id via lookup su
chunks prima di scrivere nel registro.

Uso:
  python scripts/sync_istituti_registry.py --dry-run   # mostra il diff, non scrive
  python scripts/sync_istituti_registry.py             # scrive registry.yaml
"""
from __future__ import annotations

import argparse
import re
import unicodedata
from pathlib import Path

import pymongo
import yaml
from bson import ObjectId

_REGISTRY_PATH = Path(__file__).resolve().parent.parent / "aiura_legal" / "core" / "istituti" / "registry.yaml"
_MONGO_URI = "mongodb://localhost:27017"
_DB_NAME = "aiura_legal_lab_db"

_CODICE_TO_SETTORE = {
    "CC": "civile",
    "CPC": "civile",
    "CP": "penale",
    "CPP": "penale",
    # Leggi complementari mappate a partire da questa sessione — vedi
    # verifica presenza leggi complementari nella KB.
    "D.LGS. 231/2001": "penale",     # responsabilità amministrativa degli enti da reato
    "D.LGS. 159/2011": "penale",     # codice antimafia — misure di prevenzione
    "D.LGS. 206/2005": "civile",     # codice del consumo
    "D.LGS. 385/1993": "civile",     # TUB — testo unico bancario
    "D.LGS. 58/1998":  "civile",     # TUF — testo unico finanza
    "D.LGS. 196/2003": "civile",     # codice privacy
    "D.P.R. 917/1986": "tributario", # TUIR
    "D.LGS. 30/2005":  "civile",     # codice proprietà industriale
    "D.LGS. 209/2005": "civile",     # codice assicurazioni private
    "D.LGS. 152/2006": "amministrativo",  # codice dell'ambiente
    "D.LGS. 81/2008":  "lavoro",     # testo unico sicurezza sul lavoro
    "D.LGS. 14/2019":  "civile",     # codice della crisi d'impresa e dell'insolvenza
    # Sessione mappatura TUEL/CPA/271-1989 + settore lavoro (2026-07-03).
    "D.LGS. 267/2000": "amministrativo",  # TUEL — testo unico enti locali
    "D.LGS. 104/2010": "amministrativo",  # CPA — codice del processo amministrativo
    "D.LGS. 271/1989": "penale",     # norme di attuazione del c.p.p.
    "L. 300/1970":     "lavoro",     # statuto dei lavoratori
    "D.LGS. 276/2003": "lavoro",     # legge Biagi
    "D.LGS. 81/2015":  "lavoro",     # codice dei contratti di lavoro (Jobs Act)
    "D.LGS. 23/2015":  "lavoro",     # tutele crescenti (Jobs Act)
    "D.LGS. 151/2001": "lavoro",     # T.U. maternità/paternità
    "L. 92/2012":      "lavoro",     # riforma Fornero
    "D.LGS. 66/2003":  "lavoro",     # orario di lavoro
    "L. 68/1999":      "lavoro",     # collocamento disabili
}

_HEADER = """# ===========================================================================
# Registro degli istituti giuridici — norme_urn VERIFICATE nel corpus locale.
# Regola: un URN entra in norme_urn solo se confermato in aiura_legal_lab_db.chunks
# (corpus=normattiva). Riferimenti non confermati restano in norme_riferimento.
# Piloti: solo con dati reali; source_id solo se chunk groundabile confermato.
#
# Sezione "sync_istituti_giuridici_ui": voci generate/fuse automaticamente da
# scripts/sync_istituti_registry.py a partire dalla collection MongoDB
# istituti_giuridici (CRUD UI). Le voci curate a mano più vecchie mantengono
# sentenze_pilota/disambigua_da; le nuove nascono con questi campi vuoti finché
# non verificati manualmente — non fabbricare mai un source_id.
# ===========================================================================

"""

_SETTORE_ORDER = ["penale", "civile", "amministrativo", "lavoro", "tributario"]


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text


def _normalize_label(text: str) -> str:
    """Normalizza per il confronto di dedup: minuscolo, senza parentesi, senza accenti."""
    text = re.sub(r"\([^)]*\)", "", text)  # rimuovi parentetiche
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def _dedup_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def _resolve_urn(chunk_id_str: str, chunks_col, cache: dict[str, str | None]) -> str | None:
    if chunk_id_str in cache:
        return cache[chunk_id_str]
    try:
        oid = ObjectId(chunk_id_str)
    except Exception:
        cache[chunk_id_str] = None
        return None
    doc = chunks_col.find_one({"_id": oid}, {"source_id": 1})
    urn = str(doc["source_id"]) if doc and doc.get("source_id") else None
    cache[chunk_id_str] = urn
    return urn


def build_new_entries(istituti_docs: list[dict], chunks_col) -> list[dict]:
    urn_cache: dict[str, str | None] = {}
    entries: list[dict] = []
    for doc in istituti_docs:
        denom = str(doc.get("denominazione", "")).strip()
        if not denom:
            continue
        codice = str(doc.get("codice_riferimento", "")).strip().upper()
        settore = _CODICE_TO_SETTORE.get(codice, "")
        if not settore:
            continue

        articoli = (doc.get("quadro_normativo") or {}).get("articoli_principali") or []
        norme_urn: list[str] = []
        norme_riferimento: list[str] = []
        for art in articoli:
            riferimento = str(art.get("riferimento", "")).strip()
            if riferimento:
                norme_riferimento.append(riferimento)
            chunk_id = art.get("source_mongo_id")
            if chunk_id:
                urn = _resolve_urn(str(chunk_id), chunks_col, urn_cache)
                if urn:
                    norme_urn.append(urn)

        termini_chiave = [denom.lower()]

        entries.append({
            "id": f"{_slugify(denom)}_{_slugify(codice)}",
            "label": f"{denom} ({codice})",
            "settore": settore,
            "norme_urn": _dedup_keep_order(norme_urn),
            "norme_riferimento": _dedup_keep_order(norme_riferimento),
            "termini_chiave": termini_chiave,
            "disambigua_da": {},
            "sentenze_pilota": [],
            "_normalized_label": _normalize_label(denom),
        })
    return entries


def merge_into_existing(existing: list[dict], new_entries: list[dict]) -> tuple[list[dict], list[dict]]:
    """Ritorna (esistenti_aggiornati, nuovi_da_aggiungere). Fonde per label normalizzata."""
    by_norm_label: dict[str, dict] = {
        _normalize_label(e.get("label", "")): e for e in existing
    }
    to_add: list[dict] = []
    for entry in new_entries:
        key = entry["_normalized_label"]
        match = by_norm_label.get(key)
        if match is None:
            entry.pop("_normalized_label")
            to_add.append(entry)
            continue
        match["norme_urn"] = _dedup_keep_order(list(match.get("norme_urn") or []) + entry["norme_urn"])
        match["norme_riferimento"] = _dedup_keep_order(
            list(match.get("norme_riferimento") or []) + entry["norme_riferimento"]
        )
        match["termini_chiave"] = _dedup_keep_order(
            list(match.get("termini_chiave") or []) + entry["termini_chiave"]
        )
    return existing, to_add


def _scalar(value: str) -> str:
    """Dump di un singolo scalare YAML senza il marker di fine documento
    '...' che yaml.safe_dump() aggiunge per documenti scalari puri, e senza
    line-wrap automatico (altrimenti split("\\n",1)[0] tronca le stringhe
    lunghe a metà, prima della chiusura delle virgolette)."""
    return yaml.safe_dump(value, width=float("inf"), allow_unicode=True).split("\n", 1)[0]


def render_yaml(all_entries: list[dict]) -> str:
    by_settore: dict[str, list[dict]] = {s: [] for s in _SETTORE_ORDER}
    for e in all_entries:
        by_settore.setdefault(e.get("settore", ""), []).append(e)

    lines = [_HEADER.rstrip("\n"), "", "istituti:"]
    for settore in _SETTORE_ORDER:
        group = by_settore.get(settore) or []
        if not group:
            continue
        group.sort(key=lambda e: e["id"])
        lines.append("  # " + "=" * 71)
        lines.append(f"  # {settore.upper()}")
        lines.append("  # " + "=" * 71)
        for e in group:
            lines.append(f"  - id: {e['id']}")
            lines.append(f"    label: {_scalar(e['label'])}")
            lines.append(f"    settore: {e['settore']}")
            if e.get("norme_urn"):
                lines.append("    norme_urn:")
                for u in e["norme_urn"]:
                    lines.append(f"      - {_scalar(u)}")
            else:
                lines.append("    norme_urn: []")
            if e.get("norme_riferimento"):
                lines.append("    norme_riferimento:")
                for r in e["norme_riferimento"]:
                    lines.append(f"      - {_scalar(r)}")
            else:
                lines.append("    norme_riferimento: []")
            if e.get("termini_chiave"):
                lines.append("    termini_chiave:")
                for t in e["termini_chiave"]:
                    lines.append(f"      - {_scalar(t)}")
            else:
                lines.append("    termini_chiave: []")
            disambigua = e.get("disambigua_da") or {}
            if disambigua:
                lines.append("    disambigua_da:")
                for other_id, terms in disambigua.items():
                    lines.append(f"      {other_id}:")
                    for t in terms:
                        lines.append(f"        - {_scalar(t)}")
            else:
                lines.append("    disambigua_da: {}")
            piloti = e.get("sentenze_pilota") or []
            if piloti:
                lines.append("    sentenze_pilota:")
                for p in piloti:
                    lines.append(f"      - organo: {_scalar(str(p.get('organo','')))}")
                    lines.append(f"        numero: {_scalar(str(p.get('numero','')))}")
                    lines.append(f"        anno: {_scalar(str(p.get('anno','')))}")
                    if p.get("nome"):
                        lines.append(f"        nome: {_scalar(str(p['nome']))}")
                    if p.get("principio"):
                        lines.append(f"        principio: {_scalar(str(p['principio']))}")
                    if p.get("source_id"):
                        lines.append(f"        source_id: {_scalar(str(p['source_id']))}")
            else:
                lines.append("    sentenze_pilota: []")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    client = pymongo.MongoClient(_MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[_DB_NAME]

    raw = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    existing = raw.get("istituti", [])
    print(f"registro esistente: {len(existing)} istituti")

    istituti_docs = list(db["istituti_giuridici"].find({}))
    print(f"istituti_giuridici (CRUD UI): {len(istituti_docs)} documenti")

    new_entries = build_new_entries(istituti_docs, db["chunks"])
    existing, to_add = merge_into_existing(existing, new_entries)

    merged_count = len(new_entries) - len(to_add)
    print(f"fusi in voci esistenti: {merged_count}")
    print(f"nuove voci da aggiungere: {len(to_add)}")

    all_entries = existing + to_add
    urn_total = sum(len(e.get("norme_urn") or []) for e in all_entries)
    print(f"totale istituti nel registro dopo la sync: {len(all_entries)} (norme_urn totali: {urn_total})")

    output = render_yaml(all_entries)

    if args.dry_run:
        print("\n--dry-run: nessuna scrittura. Anteprima nuove voci (prime 3):")
        for e in to_add[:3]:
            print(f"  - {e['id']} | settore={e['settore']} | norme_urn={len(e['norme_urn'])} | norme_riferimento={len(e['norme_riferimento'])}")
        return

    _REGISTRY_PATH.write_text(output, encoding="utf-8")
    print(f"scritto: {_REGISTRY_PATH}")


if __name__ == "__main__":
    main()
