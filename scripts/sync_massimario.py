"""
Scraper Massimari della Corte di Cassazione — scarica le Rassegne annuali
di giurisprudenza (civile/penale) pubblicate gratuitamente dall'Ufficio del
Massimario su cortedicassazione.it e le carica come corpus=massimario.

PERCHÉ:
  La fonte Solr pubblica (italgiure SentenzeWeb, usata da sync_jurisprudence.py)
  espone solo gli ultimi ~5 anni di sentenze. Le sentenze "pilota" più vecchie
  (es. Cass. SS.UU. n.10561/2014 Gubert sul sequestro per equivalente) restano
  fuori dalla finestra → buco strutturale proprio sui principi più consolidati.
  Le Rassegne annuali del Massimario sono digesti ragionati che riportano quei
  principi CON la citazione della sentenza, e coprono anni storici (dal ~2013):
  ingerirle attenua il gap finché non si hanno gli accessi alle banche dati
  ufficiali ad accesso riservato (ItalgiureWeb/Cassa Forense).

STRATEGIA:
  - Pagine indice ufficiali (Rassegne annuali penali/civili) → scopre i link
    PDF in /resources/cms/documents/ sia diretti sia via pagine di dettaglio.
  - Augmenta con un seed di URL noti (sentinella per anni storici), scartati
    automaticamente se non esistono (download valida dimensione e 404).
  - Carica via POST /ingest con corpus="massimario".

Uso:
  python scripts/sync_massimario.py --dry-run            # scopre URL, non scarica
  python scripts/sync_massimario.py --no-upload          # scarica senza caricare
  python scripts/sync_massimario.py                      # scarica + carica tutto
  python scripts/sync_massimario.py --source penale
  python scripts/sync_massimario.py --limit 3

Dopo il caricamento, ricostruisci l'indice del nuovo corpus:
  python scripts/build_indexes.py --workspace mio-studio --corpus massimario
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger

# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------

API_URL      = "http://127.0.0.1:8765"
DOWNLOAD_DIR = Path("download/massimario")
STATE_FILE   = DOWNLOAD_DIR / ".state.json"
RATE_LIMIT_S = 1.2
MAX_RETRIES  = 3
REQUEST_TIMEOUT = 60.0

BASE_CASS = "https://www.cortedicassazione.it"

_scraper_contact = os.environ.get("SCRAPER_CONTACT_EMAIL", "aiura-scraper@localhost")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        f"(KHTML, like Gecko) AiUra-LegalLab-MassimarioScraper/1.0 (research; {_scraper_contact})"
    ),
    "Accept": "text/html,application/pdf,*/*",
}

# Pagine indice ufficiali delle Rassegne annuali (Ufficio del Massimario).
_INDEX_PAGES: dict[str, list[str]] = {
    "penale": [
        f"{BASE_CASS}/it/relazioni_documenti_penale.page?search=annuale",
        f"{BASE_CASS}/it/relazioni_documenti_penale.page?search=rassegna",
    ],
    "civile": [
        f"{BASE_CASS}/it/relazioni_documenti_civile.page?search=rassegna+annuale&it_tipo_doc_copy=Rassegna",
        f"{BASE_CASS}/it/relazioni_documenti_civile.page?search=rassegna",
    ],
}

# Seed di URL PDF noti (sentinella per anni storici): scartati senza errore se
# non esistono. Servono a garantire copertura anche se l'HTML cambia struttura.
_SEED_PDFS: dict[str, list[str]] = {
    "penale": [
        f"{BASE_CASS}/resources/cms/documents/Rassegna_Penale_2013.pdf",
        f"{BASE_CASS}/resources/cms/documents/Volume_I_2017_Massimario_Penale.pdf",
        f"{BASE_CASS}/resources/cms/documents/Rassegna_penale_2020_vol_II.pdf",
        f"{BASE_CASS}/resources/cms/documents/Rassegna_penale_2021_vol_II_.pdf",
    ],
    "civile": [],
}

# Un PDF è una Rassegna/Massimario se il nome file contiene uno di questi token.
_PDF_NAME_HINT = re.compile(r"(rassegn|massimari|volume)", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Tipi / State
# ---------------------------------------------------------------------------

@dataclass
class DocEntry:
    pdf_url: str
    area:    str = ""    # penale | civile
    title:   str = ""


def _load_state() -> set[str]:
    if STATE_FILE.exists():
        try:
            return set(json.loads(STATE_FILE.read_text(encoding="utf-8")).get("done", []))
        except Exception:
            pass
    return set()


def _save_state(done: set[str]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps({"done": sorted(done), "updated_at": datetime.now().isoformat()},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

async def _get(client: httpx.AsyncClient, url: str) -> Optional[bytes]:
    for attempt in range(MAX_RETRIES):
        try:
            r = await client.get(url, follow_redirects=True, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.content
            if r.status_code in (404, 410):
                return None
            logger.debug(f"HTTP {r.status_code} — {url}")
            return None
        except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.warning(f"Fetch fallito ({exc.__class__.__name__}): {url}")
    return None


def _soup(html: bytes) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _safe_name(url: str, prefix: str = "") -> str:
    name = urlparse(url).path.rstrip("/").split("/")[-1]
    name = re.sub(r"[^\w\-.]", "_", name) or "doc.pdf"
    return f"{prefix}__{name}" if prefix else name


def _is_pdf_link(href: str) -> bool:
    return href.lower().split("?")[0].endswith(".pdf")


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------

async def _pdfs_from_page(
    client: httpx.AsyncClient, page_url: str, area: str, depth: int = 1,
) -> list[DocEntry]:
    """
    Estrae i PDF da una pagina: link .pdf diretti + (depth>0) link a pagine di
    dettaglio (.page?contentId=...) da cui estrarre i PDF.
    """
    html = await _get(client, page_url)
    if not html:
        return []
    soup = _soup(html)
    entries: list[DocEntry] = []
    detail_links: list[str] = []
    seen: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(page_url, href)
        if _is_pdf_link(href):
            name = urlparse(full).path.split("/")[-1]
            if _PDF_NAME_HINT.search(name) and full not in seen:
                seen.add(full)
                entries.append(DocEntry(pdf_url=full, area=area, title=a.get_text(strip=True)))
        elif depth > 0 and "/it/" in href and ".page" in href and "contentId" in href:
            if full not in detail_links:
                detail_links.append(full)

    for detail in detail_links:
        await asyncio.sleep(0.4)
        for e in await _pdfs_from_page(client, detail, area, depth=depth - 1):
            if e.pdf_url not in seen:
                seen.add(e.pdf_url)
                entries.append(e)

    return entries


async def discover(area: str, done: set[str]) -> list[DocEntry]:
    entries: list[DocEntry] = []
    seen: set[str] = set()
    async with httpx.AsyncClient(headers=HEADERS) as client:
        # 1) pagine indice ufficiali
        for index_url in _INDEX_PAGES.get(area, []):
            await asyncio.sleep(RATE_LIMIT_S)
            for e in await _pdfs_from_page(client, index_url, area, depth=1):
                if e.pdf_url not in done and e.pdf_url not in seen:
                    seen.add(e.pdf_url)
                    entries.append(e)
        # 2) seed di URL noti (verifica esistenza via HEAD)
        for url in _SEED_PDFS.get(area, []):
            if url in done or url in seen:
                continue
            await asyncio.sleep(0.3)
            try:
                r = await client.head(url, follow_redirects=True, timeout=15)
                if r.status_code == 200:
                    seen.add(url)
                    entries.append(DocEntry(pdf_url=url, area=area, title="(seed)"))
            except Exception:
                pass
    logger.info(f"[{area}] {len(entries)} PDF Rassegna/Massimario scoperti")
    return entries


# ---------------------------------------------------------------------------
# Download + Upload
# ---------------------------------------------------------------------------

async def download_pdf(client: httpx.AsyncClient, entry: DocEntry) -> Optional[Path]:
    filename = _safe_name(entry.pdf_url, f"massimario_{entry.area}")
    dest = DOWNLOAD_DIR / filename
    if dest.exists() and dest.stat().st_size > 2000:
        logger.debug(f"  Già presente: {dest.name}")
        return dest
    content = await _get(client, entry.pdf_url)
    if not content or len(content) < 1000:
        logger.warning(f"  PDF non valido o vuoto: {entry.pdf_url}")
        return None
    if not content[:5].startswith(b"%PDF"):
        logger.warning(f"  Non è un PDF (header errato): {entry.pdf_url}")
        return None
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    logger.info(f"  ✅ {len(content)//1024}KB — {dest.name}")
    return dest


async def upload_pdf(client: httpx.AsyncClient, pdf_path: Path, workspace: str) -> bool:
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    timeout = max(180.0, 60.0 + size_mb * 5)   # rassegne grandi: chunking lungo
    try:
        with open(pdf_path, "rb") as f:
            resp = await client.post(
                f"{API_URL}/ingest",
                data={"workspace": workspace, "corpus": "massimario"},
                files={"file": (pdf_path.name, f, "application/pdf")},
                timeout=timeout,
            )
        if resp.status_code in (200, 201):
            data = resp.json()
            logger.success(f"  ✅ Caricato: chunks={data.get('chunk_count','?')} — {pdf_path.name}")
            return True
        logger.error(f"  ❌ Upload {resp.status_code}: {resp.text[:150]}")
        return False
    except Exception as exc:
        logger.error(f"  ❌ Upload errore: {exc}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(areas: list[str], workspace: str, dry_run: bool, no_upload: bool, limit: int) -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    done = _load_state()
    logger.info(f"State: {len(done)} URL già processati")

    if not no_upload and not dry_run:
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get(f"{API_URL}/health", timeout=5)
                r.raise_for_status()
            logger.info("API online ✅")
        except Exception as exc:
            logger.error(f"API non raggiungibile: {exc} — usa --no-upload per scaricare soltanto")
            return

    found = downloaded = uploaded = errors = 0

    for area in areas:
        logger.info(f"\n{'='*60}\n  RASSEGNE {area.upper()}\n{'='*60}")
        try:
            entries = await discover(area, done)
        except Exception as exc:
            logger.error(f"Discovery {area} fallita: {exc}")
            continue

        if limit > 0:
            entries = entries[:limit]
        found += len(entries)

        if dry_run:
            for e in entries:
                logger.info(f"    {e.pdf_url}  [{e.title[:50]}]")
            continue

        async with httpx.AsyncClient(headers=HEADERS) as client:
            for entry in entries:
                await asyncio.sleep(RATE_LIMIT_S)
                pdf_path = await download_pdf(client, entry)
                if not pdf_path:
                    errors += 1
                    done.add(entry.pdf_url)
                    continue
                downloaded += 1
                done.add(entry.pdf_url)
                if not no_upload and await upload_pdf(client, pdf_path, workspace):
                    uploaded += 1
        _save_state(done)

    _save_state(done)
    logger.info(f"""
{'='*60}
  RIEPILOGO
  Scoperti:   {found}
  Scaricati:  {downloaded}
  Caricati:   {uploaded}
  Errori:     {errors}
{'='*60}""")
    if not no_upload and downloaded > 0:
        logger.info(
            "\nPasso successivo — indicizza il nuovo corpus:\n"
            f"  python scripts/build_indexes.py --workspace {workspace} --corpus massimario"
        )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scraper Massimari/Rassegne Corte di Cassazione")
    p.add_argument("--source", "-s", choices=["penale", "civile"], nargs="+",
                   default=["penale", "civile"], dest="areas")
    p.add_argument("--workspace", "-w", default="mio-studio")
    p.add_argument("--dry-run", action="store_true", help="Scopre gli URL senza scaricare")
    p.add_argument("--no-upload", action="store_true", help="Scarica senza caricare in API")
    p.add_argument("--limit", type=int, default=0, help="Max PDF per area (0=tutti)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(main(
        areas=args.areas,
        workspace=args.workspace,
        dry_run=args.dry_run,
        no_upload=args.no_upload,
        limit=args.limit,
    ))
