"""
Carica i PDF dalla cartella download/ nell'API AiUra LegalLab.

Sentenze → POST /jurisprudence/upload
Dottrina  → POST /ingest (corpus studio)

Uso:
  python scripts/upload_download_pdfs.py
"""
from __future__ import annotations
import httpx
from pathlib import Path
from loguru import logger

API = "http://127.0.0.1:8765"
DOWNLOAD = Path("download")

# Sentenze da caricare come giurisprudenza
SENTENZE = [
    {
        "file":   "SSUU-Thyssenkrupp.pdf",
        "organo": "cassazione",
        "numero": "38343",
        "anno":   2014,
        "desc":   "Cass. SS.UU. n. 38343/2014 — ThyssenKrupp (dolo eventuale)",
    },
]

# Dottrina da caricare come documenti studio
DOTTRINA = [
    {
        "file": "1363694180CANESTRARI 2013a.pdf",
        "desc": "Canestrari — La distinzione tra dolo eventuale e colpa cosciente",
    },
    {
        "file": "1371296055AIMI 2013_03.pdf",
        "desc": "Aimi — Dolo eventuale e colpa cosciente al banco di prova",
    },
    {
        "file": "DALLA COLPA COSCIENTE AL DOLO EVENTUALE - Zecca.pdf",
        "desc": "Zecca — Dalla colpa cosciente al dolo eventuale",
    },
]


def upload_sentenza(client: httpx.Client, item: dict) -> bool:
    path = DOWNLOAD / item["file"]
    if not path.exists():
        logger.warning(f"File non trovato: {path}")
        return False
    logger.info(f"Caricamento sentenza: {item['desc']}")
    with open(path, "rb") as f:
        resp = client.post(
            f"{API}/jurisprudence/upload",
            data={
                "organo": item["organo"],
                "numero": item["numero"],
                "anno":   str(item["anno"]),
            },
            files={"file": (path.name, f, "application/pdf")},
            timeout=120,
        )
    if resp.status_code in (200, 201):
        data = resp.json()
        logger.success(
            f"  ✅ Caricata: organo={data.get('organo')} "
            f"n.{data.get('numero')}/{data.get('anno')} "
            f"status={data.get('status')}"
        )
        return True
    else:
        logger.error(f"  ❌ Errore {resp.status_code}: {resp.text[:200]}")
        return False


def upload_dottrina(client: httpx.Client, item: dict, workspace: str = "mio-studio") -> bool:
    path = DOWNLOAD / item["file"]
    if not path.exists():
        logger.warning(f"File non trovato: {path}")
        return False
    logger.info(f"Caricamento dottrina: {item['desc']}")
    with open(path, "rb") as f:
        resp = client.post(
            f"{API}/ingest",
            data={"workspace": workspace, "corpus": "dottrina"},
            files={"file": (path.name, f, "application/pdf")},
            timeout=120,
        )
    if resp.status_code in (200, 201):
        data = resp.json()
        logger.success(f"  ✅ Caricata: document_id={data.get('document_id')}")
        return True
    else:
        logger.error(f"  ❌ Errore {resp.status_code}: {resp.text[:200]}")
        return False


def main():
    # Verifica API raggiungibile
    try:
        r = httpx.get(f"{API}/health", timeout=5)
        r.raise_for_status()
        logger.info(f"API online: {r.json()}")
    except Exception as exc:
        logger.error(f"API non raggiungibile: {exc}")
        logger.error("Avvia prima l'API con: python -m aiura_legal.api")
        return

    ok = 0
    fail = 0

    with httpx.Client() as client:
        logger.info("=== Upload sentenze ===")
        for item in SENTENZE:
            if upload_sentenza(client, item):
                ok += 1
            else:
                fail += 1

        logger.info("\n=== Upload dottrina (corpus studio) ===")
        for item in DOTTRINA:
            if upload_dottrina(client, item):
                ok += 1
            else:
                fail += 1

    logger.info(f"\nCompletato: {ok} OK, {fail} errori")
    if ok > 0:
        logger.info(
            "\nPasso successivo — indicizza la giurisprudenza in BM25/ChromaDB:\n"
            "  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione\n"
            "  python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo corte_cost"
        )


if __name__ == "__main__":
    main()
