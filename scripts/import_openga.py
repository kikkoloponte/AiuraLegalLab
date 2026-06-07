"""
Importa sentenze TAR e Consiglio di Stato da OpenGA (openga.giustizia-amministrativa.it)
tramite CKAN API — nessun browser, download CSV diretto.

Copre 31 dataset: tutti i TAR d'Italia + Consiglio di Stato + TRGA Bolzano/Trento.
Ogni CSV ha ~2-20MB per anno, anni disponibili: 2023–2026 (aggiornamento mensile).

Uso:
  python scripts/import_openga.py                    # tutti i dataset, tutti gli anni
  python scripts/import_openga.py --from-year 2022   # solo dal 2022
  python scripts/import_openga.py --dataset cds-sentenze  # solo CdS
  python scripts/import_openga.py --dry-run          # conta senza salvare
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import time
from datetime import date, datetime
from typing import Optional

import httpx
from loguru import logger
from pymongo import MongoClient, UpdateOne

from aiura_legal.ingestion.mongodb.client import settings

_CKAN_BASE  = "https://openga.giustizia-amministrativa.it/api/3/action"
_COLLECTION = "jurisprudence"
_DELAY_S    = 1.0   # cortesia verso il server tra download

# Dataset da scaricare — nell'ordine priorità
_SENTENZE_DATASETS = [
    "cds-sentenze",
    "cga-sicilia-sentenze",
    "tar-lazio-roma-sentenze",
    "tar-lombardia-milano-sentenze",
    "tar-campania-napoli-sentenze",
    "tar-toscana-sentenze",
    "tar-veneto-sentenze",
    "tar-piemonte-sentenze",
    "tar-puglia-bari-sentenze",
    "tar-emilia-romagna-bologna-sentenze",
    "tar-sicilia-palermo-sentenze",
    "tar-sicilia-catania-sentenze",
    "tar-liguria-sentenze",
    "tar-abruzzo-l-aquila-sentenze",
    "tar-sardegna-sentenze",
    "tar-lazio-latina-sentenze",
    "tar-lombardia-brescia-sentenze",
    "tar-calabria-catanzaro-sentenze",
    "tar-calabria-reggio-calabria-sentenze",
    "tar-puglia-lecce-sentenze",
    "tar-campania-salerno-sentenze",
    "tar-marche-sentenze",
    "tar-friuli-venezia-giulia-sentenze",
    "tar-umbria-sentenze",
    "tar-abruzzo-pescara-sentenze",
    "tar-basilicata-sentenze",
    "tar-molise-sentenze",
    "tar-valle-d-aosta-sentenze",
    "tar-emilia-romagna-parma-sentenze",
    "trga-bolzano-sentenze",
    "trga-trento-sentenze",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _organo_from_sede(nome_sede: str, dataset_id: str) -> str:
    """Determina l'organo dal nome sede o dal dataset ID."""
    nome_upper = nome_sede.upper()
    if "CDS" in nome_upper or "CONSIGLIO" in nome_upper:
        return "consiglio_stato"
    if "CGA" in nome_upper:
        return "tar"          # trattato come TAR per semplicità
    return "tar"


def _parse_date(s: str) -> Optional[date]:
    if not s or s.strip() == "":
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _row_to_doc(row: dict, dataset_id: str) -> Optional[dict]:
    """Converte una riga CSV in documento MongoDB. Restituisce None se da saltare."""
    numero     = row.get("NUMERO_PROVVEDIMENTO", "").strip()
    anno_str   = row.get("ANNO_PUBBLICAZIONE",   "").strip()
    nome_sede  = row.get("NOME_SEDE",             "").strip()
    sezione    = row.get("NOME_SEZIONE",          "").strip()
    oggetto    = row.get("OGGETTO_RICORSO",       "").strip()
    esito      = row.get("ESITO_PROVVEDIMENTO",   "").strip()
    tipo       = row.get("TIPO_PROVVEDIMENTO",    "").strip()
    data_pub   = row.get("DATA_PUBBLICAZIONE",    "").strip()

    if not numero or not anno_str:
        return None
    try:
        anno = int(anno_str)
    except ValueError:
        return None

    organo     = _organo_from_sede(nome_sede, dataset_id)
    data_dep   = _parse_date(data_pub) or date(anno, 1, 1)
    materia    = oggetto[:200] if oggetto else tipo

    # Massima = oggetto + esito
    massima_parts = []
    if oggetto:
        massima_parts.append(oggetto)
    if esito:
        massima_parts.append(f"Esito: {esito}")
    massima = " — ".join(massima_parts)

    # ID univoco: organo + numero + anno
    doc_id = f"{organo}_{numero}_{anno}"

    return {
        "_id":              doc_id,
        "organo":           organo,
        "numero":           numero,
        "anno":             anno,
        "data_deposito":    data_dep.isoformat(),
        "sezione":          sezione,
        "materia":          materia,
        "massima":          massima,
        "motivazione":      "",   # non disponibile nell'open data
        "dispositivo":      esito,
        "norme_citate":     [],
        "sentenze_citate":  [],
        "source_url":       f"https://www.giustizia-amministrativa.it",
        "source_channel":   "open_data",
        "is_anonymized":    False,
        "raw_pii_vault_id": None,
        "nome_sede":        nome_sede,
        "tipo_provvedimento": tipo,
    }


# ---------------------------------------------------------------------------
# CKAN API helpers
# ---------------------------------------------------------------------------

def _get_csv_resources(client: httpx.Client, dataset_id: str, from_year: int) -> list[dict]:
    """Restituisce la lista di risorse CSV per un dataset, filtrate per anno."""
    try:
        r = client.get(f"{_CKAN_BASE}/package_show", params={"id": dataset_id}, timeout=30)
        r.raise_for_status()
        resources = r.json()["result"]["resources"]
    except Exception as e:
        logger.error(f"Errore metadata {dataset_id}: {e}")
        return []

    csv_resources = []
    for res in resources:
        if res.get("format", "").upper() != "CSV":
            continue
        # Estrai anno dal nome risorsa (es. "TAR Lazio - 2024")
        m = re.search(r"\b(20\d{2})\b", res.get("name", ""))
        if not m:
            continue
        year = int(m.group(1))
        if year < from_year:
            continue
        csv_resources.append({"url": res["url"], "year": year, "name": res["name"]})

    return sorted(csv_resources, key=lambda x: x["year"])


def _download_csv(client: httpx.Client, url: str) -> list[dict]:
    """Scarica un CSV e restituisce le righe come lista di dict."""
    try:
        r = client.get(url, timeout=120, follow_redirects=True)
        r.raise_for_status()
        # Prova UTF-8, fallback latin-1
        try:
            text = r.content.decode("utf-8")
        except UnicodeDecodeError:
            text = r.content.decode("latin-1")
        reader = csv.DictReader(io.StringIO(text))
        return list(reader)
    except Exception as e:
        logger.error(f"Download fallito {url}: {e}")
        return []


# ---------------------------------------------------------------------------
# Import principale
# ---------------------------------------------------------------------------

def run_import(
    datasets: list[str],
    from_year: int = 2020,
    dry_run: bool = False,
) -> None:
    logger.info(f"Import OpenGA — {len(datasets)} dataset, from_year={from_year}, dry_run={dry_run}")

    mongo = MongoClient(settings.mongodb_uri)
    db    = mongo[settings.mongodb_database]
    coll  = db[_COLLECTION]

    # ID già presenti (TAR + CdS) per idempotenza
    existing = set(
        doc["_id"]
        for doc in coll.find({"organo": {"$in": ["tar", "consiglio_stato"]}}, {"_id": 1})
    )
    logger.info(f"Già presenti: {len(existing):,} sentenze TAR/CdS")

    total_inserted = total_skipped = total_errors = 0
    BATCH = 500

    with httpx.Client(headers={"User-Agent": "AiUraLegalLab/1.0 (research)"}) as client:
        for dataset_id in datasets:
            resources = _get_csv_resources(client, dataset_id, from_year)
            if not resources:
                logger.warning(f"  {dataset_id}: nessun CSV disponibile per from_year={from_year}")
                continue

            ds_inserted = ds_skipped = 0
            bulk_ops: list[UpdateOne] = []

            def _flush():
                nonlocal ds_inserted
                if not bulk_ops or dry_run:
                    return
                result = coll.bulk_write(bulk_ops, ordered=False)
                ds_inserted += result.upserted_count
                bulk_ops.clear()

            for res in resources:
                logger.info(f"  {dataset_id} — {res['name']} ({res['year']})...")
                rows = _download_csv(client, res["url"])
                if not rows:
                    continue

                for row in rows:
                    doc = _row_to_doc(row, dataset_id)
                    if doc is None:
                        ds_skipped += 1
                        continue
                    if doc["_id"] in existing:
                        ds_skipped += 1
                        continue

                    if dry_run:
                        ds_inserted += 1
                        existing.add(doc["_id"])
                        continue

                    bulk_ops.append(UpdateOne(
                        {"_id": doc["_id"]},
                        {"$setOnInsert": doc},
                        upsert=True,
                    ))
                    existing.add(doc["_id"])   # previene duplicati tra dataset

                    if len(bulk_ops) >= BATCH:
                        _flush()

                logger.info(f"    → {res['year']}: {len(rows)} righe elaborate")
                time.sleep(_DELAY_S)

            _flush()
            logger.success(f"  {dataset_id}: {ds_inserted} nuove | {ds_skipped} già presenti")
            total_inserted += ds_inserted
            total_skipped  += ds_skipped

    mongo.close()
    label = "[DRY RUN] " if dry_run else ""
    logger.success(
        f"{label}Completato: {total_inserted:,} inserite | "
        f"{total_skipped:,} già presenti | {total_errors} errori"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Importa sentenze TAR/CdS da OpenGA (CKAN API, no browser)"
    )
    parser.add_argument(
        "--from-year", type=int, default=2020,
        help="Importa solo sentenze da questo anno in poi (default: 2020)"
    )
    parser.add_argument(
        "--dataset", default=None,
        help="Importa solo questo dataset (es. cds-sentenze). Default: tutti."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Conta senza scrivere su MongoDB"
    )
    args = parser.parse_args()

    datasets = [args.dataset] if args.dataset else _SENTENZE_DATASETS

    run_import(
        datasets=datasets,
        from_year=args.from_year,
        dry_run=args.dry_run,
    )
