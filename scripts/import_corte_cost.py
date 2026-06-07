"""
Importa le pronunce della Corte Costituzionale dagli archivi ZIP scaricati da
dati.cortecostituzionale.it in MongoDB (collection: jurisprudence).

Struttura attesa in download/:
  CC_OpenPronunce_1956_1980.zip  → zip per anno → XML con <elenco_pronunce>
  CC_OpenPronunce_1981_2000.zip
  CC_OpenPronunce_2001_oggi.zip
  CC_OpenMassime_1956_1980.zip   → zip per anno → XML con massime (testo breve)
  CC_OpenMassime_1981_2000.zip
  CC_OpenMassime_2001_oggi.zip

Le massime vengono unite alle pronunce per arricchire il campo `massima`.

Uso:
  python scripts/import_corte_cost.py
  python scripts/import_corte_cost.py --dry-run        # mostra statistiche senza salvare
  python scripts/import_corte_cost.py --from-year 2000 # solo dal 2000 in poi
  python scripts/import_corte_cost.py --only-sentenze  # salta le ordinanze (tipologia O)
"""
from __future__ import annotations

import argparse
import io
import re
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from loguru import logger
from pymongo import MongoClient, UpdateOne

from aiura_legal.ingestion.mongodb.client import settings

_DOWNLOAD_DIR = Path("download")
_COLLECTION    = "jurisprudence"

# Outer ZIP → lista degli inner ZIP per anno
_PRONUNCE_ZIPS = [
    "CC_OpenPronunce_1956_1980.zip",
    "CC_OpenPronunce_1981_2000.zip",
    "CC_OpenPronunce_2001_oggi.zip",
]
_MASSIME_ZIPS = [
    "CC_OpenMassime_1956_1980.zip",
    "CC_OpenMassime_1981_2000.zip",
    "CC_OpenMassime_2001_oggi.zip",
]


# ---------------------------------------------------------------------------
# Helpers XML
# ---------------------------------------------------------------------------

def _text(el, path: str, default: str = "") -> str:
    """Estrae il testo di un sotto-elemento, rimuovendo caratteri di controllo."""
    node = el.find(path)
    if node is None or not node.text:
        return default
    return node.text.strip()


def _inner_text(el) -> str:
    """Testo completo di un elemento inclusi tutti i figli (ricorsivo)."""
    parts = []
    if el.text:
        parts.append(el.text)
    for child in el:
        parts.append(_inner_text(child))
        if child.tail:
            parts.append(child.tail)
    return " ".join(p.strip() for p in parts if p.strip())


def _parse_date(s: str) -> date:
    """Converte DD/MM/YYYY → date. Fallback a 2000-01-01."""
    try:
        d, m, y = s.strip().split("/")
        return date(int(y), int(m), int(d))
    except Exception:
        return date(2000, 1, 1)


# ---------------------------------------------------------------------------
# Caricamento massime in memoria (anno, numero) → testo massima
# ---------------------------------------------------------------------------

def _load_massime(from_year: int) -> dict[tuple[int, int], str]:
    """
    Legge tutti i file massime e restituisce una mappa
    (anno, numero) → testo massima concatenato.
    """
    massime: dict[tuple[int, int], str] = {}

    for outer_name in _MASSIME_ZIPS:
        outer_path = _DOWNLOAD_DIR / outer_name
        if not outer_path.exists():
            continue
        with zipfile.ZipFile(outer_path) as z_outer:
            for inner_name in sorted(z_outer.namelist()):
                # Estrai anno dal nome file (es. Cc_OpenData_Massime_2010.zip)
                m = re.search(r"(\d{4})", inner_name)
                if not m or int(m.group(1)) < from_year:
                    continue
                try:
                    with zipfile.ZipFile(io.BytesIO(z_outer.read(inner_name))) as z_inner:
                        xml_name = z_inner.namelist()[0]
                        root = ET.fromstring(
                            z_inner.read(xml_name).decode("utf-8", errors="replace")
                        )
                    for pronuncia in root.findall("pronuncia"):
                        anno   = int(_text(pronuncia, "pronuncia_testata/anno_pronuncia", "0"))
                        numero = int(_text(pronuncia, "pronuncia_testata/numero_pronuncia", "0"))
                        testi = []
                        for massima in pronuncia.findall("massime/massima"):
                            titolo = _text(massima, "titolo")
                            testo  = _text(massima, "testo")
                            if titolo:
                                testi.append(titolo)
                            if testo:
                                testi.append(testo)
                        if testi:
                            massime[(anno, numero)] = "\n".join(testi)
                except Exception as e:
                    logger.warning(f"Massime: errore in {inner_name}: {e}")

    logger.info(f"Massime caricate: {len(massime):,}")
    return massime


# ---------------------------------------------------------------------------
# Parser principale XML pronunce
# ---------------------------------------------------------------------------

def _parse_pronuncia(
    el: ET.Element,
    massime_map: dict[tuple[int, int], str],
    only_sentenze: bool,
) -> dict | None:
    """
    Converte un elemento <pronuncia> in un documento MongoDB.
    Restituisce None se da saltare.
    """
    testata = el.find("pronuncia_testata")
    if testata is None:
        return None

    tipo = _text(testata, "tipologia_pronuncia")  # S=Sentenza, O=Ordinanza
    if only_sentenze and tipo != "S":
        return None

    try:
        anno   = int(_text(testata, "anno_pronuncia",  "0"))
        numero = int(_text(testata, "numero_pronuncia", "0"))
    except ValueError:
        return None

    if anno == 0 or numero == 0:
        return None

    ecli          = _text(testata, "ecli")
    presidente    = _text(testata, "presidente")
    relatore      = _text(testata, "relatore_pronuncia")
    data_decisione = _parse_date(_text(testata, "data_decisione", "01/01/2000"))
    data_deposito  = _parse_date(_text(testata, "data_deposito",  "01/01/2000"))

    testo_el = el.find("pronuncia_testo")
    fatto        = ""
    diritto      = ""
    dispositivo  = ""
    motivazione  = ""

    if testo_el is not None:
        # <testo> contiene <fatto> e <diritto>
        testo_node = testo_el.find("testo")
        if testo_node is not None:
            fatto   = _inner_text(testo_node.find("fatto"))   if testo_node.find("fatto")   is not None else ""
            diritto = _inner_text(testo_node.find("diritto")) if testo_node.find("diritto") is not None else ""
        dispositivo = _inner_text(testo_el.find("dispositivo")) if testo_el.find("dispositivo") is not None else ""

        motivazione = " ".join(filter(None, [fatto, diritto])) or _inner_text(testo_el)

    massima = massime_map.get((anno, numero), "")

    # Tipo pronuncia → materia di massima
    tipo_label = {
        "S": "Sentenza",
        "O": "Ordinanza",
        "D": "Decreto",
    }.get(tipo, tipo)

    return {
        "_id":            f"corte_cost_{numero}_{anno}",
        "organo":         "corte_cost",
        "numero":         str(numero),
        "anno":           anno,
        "data_deposito":  data_deposito.isoformat(),
        "sezione":        "",
        "materia":        tipo_label,
        "massima":        massima,
        "motivazione":    motivazione[:50_000],   # taglia testi molto lunghi
        "dispositivo":    dispositivo[:10_000],
        "norme_citate":   [],
        "sentenze_citate": [],
        "source_url":     f"https://www.cortecostituzionale.it/scheda-pronuncia/{anno}/{numero}",
        "source_channel": "open_data",
        "is_anonymized":  False,
        "raw_pii_vault_id": None,
        "ecli":           ecli,
        "presidente":     presidente,
        "relatore":       relatore,
        "tipo_pronuncia": tipo,
    }


# ---------------------------------------------------------------------------
# Import principale
# ---------------------------------------------------------------------------

def run_import(
    from_year: int = 1956,
    only_sentenze: bool = False,
    dry_run: bool = False,
) -> None:
    logger.info(f"Import Corte Costituzionale — from_year={from_year}, only_sentenze={only_sentenze}, dry_run={dry_run}")

    # 1. Carica le massime in memoria
    logger.info("Caricamento massime in memoria...")
    massime_map = _load_massime(from_year)

    # 2. Connessione MongoDB
    client = MongoClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]
    coll = db[_COLLECTION]

    # Set di ID già presenti per idempotenza
    existing = set(
        doc["_id"] for doc in coll.find({"organo": "corte_cost"}, {"_id": 1})
    )
    logger.info(f"Già presenti in MongoDB: {len(existing):,} pronunce Corte Cost.")

    # 3. Parse e inserimento
    inserted = skipped = errors = 0
    bulk_ops: list[UpdateOne] = []
    BATCH = 500

    def _flush():
        nonlocal inserted
        if not bulk_ops:
            return
        result = coll.bulk_write(bulk_ops, ordered=False)
        inserted += result.upserted_count + result.modified_count
        bulk_ops.clear()

    for outer_name in _PRONUNCE_ZIPS:
        outer_path = _DOWNLOAD_DIR / outer_name
        if not outer_path.exists():
            logger.warning(f"File non trovato: {outer_path}")
            continue

        with zipfile.ZipFile(outer_path) as z_outer:
            inner_names = sorted(z_outer.namelist())
            logger.info(f"Apro {outer_name} ({len(inner_names)} anni)...")

            for inner_name in inner_names:
                m = re.search(r"(\d{4})", inner_name)
                if not m:
                    continue
                year = int(m.group(1))
                if year < from_year:
                    continue

                try:
                    with zipfile.ZipFile(io.BytesIO(z_outer.read(inner_name))) as z_inner:
                        xml_name = z_inner.namelist()[0]
                        root = ET.fromstring(
                            z_inner.read(xml_name).decode("utf-8", errors="replace")
                        )
                except Exception as e:
                    logger.error(f"Errore apertura {inner_name}: {e}")
                    errors += 1
                    continue

                pronunce = root.findall("pronuncia")
                year_new = 0

                for el in pronunce:
                    try:
                        doc = _parse_pronuncia(el, massime_map, only_sentenze)
                    except Exception as e:
                        logger.debug(f"Parse error: {e}")
                        errors += 1
                        continue

                    if doc is None:
                        skipped += 1
                        continue

                    if doc["_id"] in existing:
                        skipped += 1
                        continue

                    if dry_run:
                        year_new += 1
                        inserted += 1
                        continue

                    bulk_ops.append(UpdateOne(
                        {"_id": doc["_id"]},
                        {"$setOnInsert": doc},
                        upsert=True,
                    ))
                    year_new += 1

                    if len(bulk_ops) >= BATCH:
                        _flush()

                logger.info(f"  {year}: {len(pronunce)} pronunce — {year_new} nuove")

    if not dry_run:
        _flush()

    client.close()

    label = "[DRY RUN] " if dry_run else ""
    logger.success(
        f"{label}Completato: {inserted:,} inserite | {skipped:,} già presenti/saltate | {errors:,} errori"
    )
    if dry_run:
        logger.info("Riesegui senza --dry-run per salvare i dati.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Importa pronunce Corte Costituzionale da archivi ZIP open data"
    )
    parser.add_argument(
        "--from-year", type=int, default=1956,
        help="Importa solo pronunce da questo anno in poi (default: 1956)"
    )
    parser.add_argument(
        "--only-sentenze", action="store_true",
        help="Importa solo le Sentenze (tipo S), salta le Ordinanze (tipo O)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simula l'importazione senza scrivere su MongoDB"
    )
    args = parser.parse_args()

    run_import(
        from_year=args.from_year,
        only_sentenze=args.only_sentenze,
        dry_run=args.dry_run,
    )
