"""
Scraper dottrina giuridica italiana — scarica PDF da fonti open access
e li carica automaticamente in AiUra LegalLab come corpus=dottrina.

Strategia per fonte:
  - DPC Archivio:     fascicoli completi PDF (/pdf-fascicoli/DPC_N_YYYY.pdf) — 2010-2019
  - DPC Trimestrale:  PDF per articolo da pagine fascicolo — 2019-oggi
  - Federalismi.it:   PDF per articolo da pagine numero
  - Diritti Fondamentali: PDF per articolo da pagine fascicolo
  - Questione Giustizia:  PDF per articolo da pagine rivista

Uso:
  python scripts/sync_dottrina.py                            # tutte le fonti
  python scripts/sync_dottrina.py --source dpc_archivio dpc_trimestrale
  python scripts/sync_dottrina.py --dry-run                  # conta senza scaricare
  python scripts/sync_dottrina.py --no-upload                # scarica senza caricare API
  python scripts/sync_dottrina.py --workspace mio-studio
  python scripts/sync_dottrina.py --limit 5                  # max 5 PDF per fonte
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass, field
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
DOWNLOAD_DIR = Path("download/dottrina")
STATE_FILE   = DOWNLOAD_DIR / ".state.json"
RATE_LIMIT_S = 1.2
MAX_RETRIES  = 3
REQUEST_TIMEOUT = 30.0

_scraper_contact = os.environ.get("SCRAPER_CONTACT_EMAIL", "aiura-scraper@localhost")
HEADERS = {"User-Agent": f"AiUra-LegalLab-DocScraper/2.0 (research; {_scraper_contact})"}


# ---------------------------------------------------------------------------
# Tipi
# ---------------------------------------------------------------------------

@dataclass
class DocEntry:
    pdf_url: str
    title:  str = ""
    source: str = ""
    area:   str = ""
    year:   str = ""


@dataclass
class ScrapeStats:
    found:      int = 0
    downloaded: int = 0
    skipped:    int = 0
    errors:     int = 0
    uploaded:   int = 0


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

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
# HTTP
# ---------------------------------------------------------------------------

async def _get(client: httpx.AsyncClient, url: str) -> Optional[bytes]:
    for attempt in range(MAX_RETRIES):
        try:
            r = await client.get(url, follow_redirects=True, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.content
            if r.status_code in (404, 410):
                return None          # non esiste, non riprovare
            logger.debug(f"HTTP {r.status_code} — {url}")
            return None
        except (httpx.TimeoutException, httpx.ConnectError) as exc:
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


# ---------------------------------------------------------------------------
# FONTE 1: DPC Archivio (2010-2019) — fascicoli PDF completi
# ---------------------------------------------------------------------------
# Pattern URL: https://archiviodpc.dirittopenaleuomo.org/pdf-fascicoli/DPC_N_YYYY.pdf
# I fascicoli hanno numeri 1-12 per anno. Non tutti esistono (es. no n.8 in alcuni anni).

BASE_DPC = "https://archiviodpc.dirittopenaleuomo.org"


def _dpc_fascicolo_urls() -> list[DocEntry]:
    """Genera tutti i possibili URL di fascicoli DPC 2010-2019."""
    entries = []
    for year in range(2010, 2020):
        for num in range(1, 13):
            url = f"{BASE_DPC}/pdf-fascicoli/DPC_{num}_{year}.pdf"
            entries.append(DocEntry(
                pdf_url=url,
                title=f"DPC Fascicolo {num}/{year}",
                source="dpc_archivio",
                area="penale",
                year=str(year),
            ))
    return entries


async def scrape_dpc_archivio(done: set[str]) -> list[DocEntry]:
    """
    Verifica l'esistenza di ogni fascicolo PDF e restituisce quelli disponibili.
    Usa HEAD request per non scaricare il contenuto in questa fase.
    """
    candidates = _dpc_fascicolo_urls()
    valid = []
    logger.info(f"[DPC Archivio] Verifica {len(candidates)} fascicoli possibili...")

    async with httpx.AsyncClient(headers=HEADERS) as client:
        for entry in candidates:
            if entry.pdf_url in done:
                continue
            await asyncio.sleep(0.3)  # HEAD è leggero, rate limit più basso
            try:
                r = await client.head(entry.pdf_url, follow_redirects=True, timeout=10)
                if r.status_code == 200:
                    valid.append(entry)
                    logger.debug(f"  ✓ {entry.title}")
            except Exception:
                pass

    logger.info(f"[DPC Archivio] {len(valid)} fascicoli disponibili")
    return valid


# ---------------------------------------------------------------------------
# FONTE 2: DPC Trimestrale (2019-oggi) — PDF per articolo
# ---------------------------------------------------------------------------

BASE_DPC_TRIM = "https://dpc-rivista-trimestrale.criminaljusticenetwork.eu"


async def _dpc_trim_fascicoli(client: httpx.AsyncClient) -> list[str]:
    """
    Trova URL fascicoli nell'archivio DPC Trimestrale.
    Pattern reale: /it/archivio/rivista-trimestrale-N-YYYY
    """
    html = await _get(client, f"{BASE_DPC_TRIM}/it/archivio")
    if not html:
        return []
    soup = _soup(html)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/archivio/rivista-trimestrale-" in href:
            full = urljoin(BASE_DPC_TRIM, href)
            if full not in links:
                links.append(full)
    return links


async def _dpc_trim_pdfs_from_fascicolo(
    client: httpx.AsyncClient, fasc_url: str
) -> list[DocEntry]:
    """
    Estrae PDF da una pagina fascicolo DPC Trimestrale.
    Pattern PDF: /pdf/DPC_Riv._Trim._N_YYYY[_autore].pdf
    Dedup per URL PDF (stesso PDF appare spesso due volte per duplicati di link).
    """
    html = await _get(client, fasc_url)
    if not html:
        return []
    soup = _soup(html)
    entries = []
    seen_urls: set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf") and "/pdf/" in href:
            pdf_url = urljoin(BASE_DPC_TRIM, href)
            if pdf_url in seen_urls:
                continue
            seen_urls.add(pdf_url)
            year_m = re.search(r"[_\s](\d{4})[_.]", href)
            year = year_m.group(1) if year_m else ""
            author_m = re.search(r"_(\d{4})_([a-zA-Z]+)\.pdf$", href, re.IGNORECASE)
            author = author_m.group(2).title() if author_m else ""
            entries.append(DocEntry(
                pdf_url=pdf_url,
                title=f"DPC Trim. — {author} ({year})" if author else f"DPC Trim. ({year})",
                source="dpc_trimestrale",
                area="penale",
                year=year,
            ))
    return entries


async def scrape_dpc_trimestrale(done: set[str]) -> list[DocEntry]:
    entries: list[DocEntry] = []
    seen_pdf_urls: set[str] = set()
    async with httpx.AsyncClient(headers=HEADERS) as client:
        fascicoli = await _dpc_trim_fascicoli(client)
        logger.info(f"[DPC Trimestrale] {len(fascicoli)} fascicoli trovati")
        for fasc_url in fascicoli:
            await asyncio.sleep(RATE_LIMIT_S)
            for e in await _dpc_trim_pdfs_from_fascicolo(client, fasc_url):
                if e.pdf_url not in done and e.pdf_url not in seen_pdf_urls:
                    seen_pdf_urls.add(e.pdf_url)
                    entries.append(e)
    logger.info(f"[DPC Trimestrale] {len(entries)} PDF nuovi")
    return entries


# ---------------------------------------------------------------------------
# FONTE 3: Federalismi.it — diritto pubblico/costituzionale/europeo
# ---------------------------------------------------------------------------

BASE_FED = "https://www.federalismi.it"


async def _fed_get_issue_article_urls(
    client: httpx.AsyncClient, issue_url: str
) -> list[str]:
    html = await _get(client, issue_url)
    if not html:
        return []
    soup = _soup(html)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "homepage.cfm?nrS=" in href:
            full = urljoin(BASE_FED, href)
            if full not in links:
                links.append(full)
    return links


async def _fed_get_pdf_from_article(
    client: httpx.AsyncClient, article_url: str
) -> Optional[str]:
    html = await _get(client, article_url)
    if not html:
        return None
    soup = _soup(html)
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            return urljoin(BASE_FED, href)
    return None


async def _fed_get_issue_urls(client: httpx.AsyncClient) -> list[str]:
    html = await _get(client, f"{BASE_FED}/nv14/archivio-rivista.cfm")
    if not html:
        return []
    soup = _soup(html)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "archivio-editoriale.cfm" in href or ("homepage.cfm" in href and "nrRivista" in href):
            full = urljoin(BASE_FED, href)
            if full not in links:
                links.append(full)
    # Ultime 60 edizioni (~3 anni)
    return links[:60]


async def scrape_federalismi(done: set[str]) -> list[DocEntry]:
    """
    Federalismi.it pubblica articoli in HTML — i PDF non sono liberamente
    scaricabili per articolo (solo eventualmente per convegni/focus).
    La fonte è disabilitata per evitare scraping inutile.
    """
    logger.info("[Federalismi] Fonte disabilitata: articoli HTML-only, nessun PDF libero per articolo")
    return []


# ---------------------------------------------------------------------------
# FONTE 4: Diritti Fondamentali
# ---------------------------------------------------------------------------

BASE_DF = "https://www.dirittifondamentali.it"


async def _df_fascicoli(client: httpx.AsyncClient) -> list[str]:
    html = await _get(client, f"{BASE_DF}/fascicoli/")
    if not html:
        return []
    soup = _soup(html)
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/fascicoli/" in href and href.rstrip("/") != "/fascicoli":
            full = urljoin(BASE_DF, href)
            if full not in links:
                links.append(full)
    return links


async def _df_pdfs_from_fascicolo(
    client: httpx.AsyncClient, fasc_url: str
) -> list[DocEntry]:
    html = await _get(client, fasc_url)
    if not html:
        return []
    soup = _soup(html)
    entries = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            pdf_url = urljoin(BASE_DF, href)
            year_m = re.search(r"/(\d{4})/", fasc_url)
            entries.append(DocEntry(
                pdf_url=pdf_url,
                source="diritti_fondamentali",
                area="diritti_fondamentali",
                year=year_m.group(1) if year_m else "",
            ))
    return entries


async def scrape_diritti_fondamentali(done: set[str]) -> list[DocEntry]:
    entries: list[DocEntry] = []
    seen_pdf_urls: set[str] = set()  # dedup: stesso PDF può apparire in più fascicoli
    async with httpx.AsyncClient(headers=HEADERS) as client:
        fascicoli = await _df_fascicoli(client)
        logger.info(f"[Diritti Fondamentali] {len(fascicoli)} fascicoli trovati")
        for fasc_url in fascicoli:
            await asyncio.sleep(RATE_LIMIT_S)
            for e in await _df_pdfs_from_fascicolo(client, fasc_url):
                if e.pdf_url not in done and e.pdf_url not in seen_pdf_urls:
                    seen_pdf_urls.add(e.pdf_url)
                    entries.append(e)
    logger.info(f"[Diritti Fondamentali] {len(entries)} PDF nuovi")
    return entries


# ---------------------------------------------------------------------------
# FONTE 5: Questione Giustizia
# ---------------------------------------------------------------------------

BASE_QG = "https://www.questionegiustizia.it"


async def _qg_article_slugs(client: httpx.AsyncClient) -> list[str]:
    """
    Raccoglie tutti gli slug articolo dalla pagina /rivistes.
    Pattern: /rivista/slug-articolo  oppure /rivista/YYYY-N.php (vecchi)
    """
    html = await _get(client, f"{BASE_QG}/riviste")
    if not html:
        return []
    soup = _soup(html)
    slugs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Articolo nuovo: /rivista/qualcosa (non /page/rivista/...)
        if re.match(r"^/rivista/[^/]+$", href) and "/page/" not in href:
            if href not in slugs:
                slugs.append(href)
    return slugs


async def _qg_pdf_from_article(
    client: httpx.AsyncClient, article_path: str
) -> Optional[str]:
    """
    Dalla pagina articolo QG estrae il PDF principale del fascicolo.
    Pattern: /data/rivista/pdf/N/filename.pdf  (PDF fascicolo completo)
    Preferisce il PDF con 'qg' nel nome (fascicolo completo, non singolo articolo).
    """
    url = urljoin(BASE_QG, article_path)
    html = await _get(client, url)
    if not html:
        return None
    soup = _soup(html)
    pdfs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/data/rivista/pdf/" in href and href.lower().endswith(".pdf"):
            full = urljoin(BASE_QG, href)
            pdfs.append(full)
    if not pdfs:
        return None
    # Preferisce PDF con 'qg' nel nome (fascicolo completo)
    for p in pdfs:
        if "_qg_" in p.lower() or "-qg-" in p.lower():
            return p
    return pdfs[0]


async def scrape_questione_giustizia(done: set[str]) -> list[DocEntry]:
    """
    Scrape Questione Giustizia dalla pagina /rivistes.
    Ogni articolo-slug ha una pagina con PDF del fascicolo completo.
    """
    entries: list[DocEntry] = []
    seen_pdfs: set[str] = set()
    async with httpx.AsyncClient(headers=HEADERS) as client:
        slugs = await _qg_article_slugs(client)
        logger.info(f"[Questione Giustizia] {len(slugs)} fascicoli/articoli trovati")
        for slug in slugs:
            if slug in done:
                continue
            await asyncio.sleep(RATE_LIMIT_S)
            pdf_url = await _qg_pdf_from_article(client, slug)
            if not pdf_url or pdf_url in done or pdf_url in seen_pdfs:
                done.add(slug)
                continue
            seen_pdfs.add(pdf_url)
            year_m = re.search(r"(\d{4})", slug)
            entries.append(DocEntry(
                pdf_url=pdf_url,
                source="questione_giustizia",
                area="processo_magistratura",
                year=year_m.group(1) if year_m else "",
            ))
    logger.info(f"[Questione Giustizia] {len(entries)} PDF nuovi")
    return entries


# ---------------------------------------------------------------------------
# Download + Upload
# ---------------------------------------------------------------------------

async def download_pdf(
    client: httpx.AsyncClient,
    entry: DocEntry,
    dest_dir: Path,
) -> Optional[Path]:
    filename = _safe_name(entry.pdf_url, entry.source)
    dest = dest_dir / filename

    if dest.exists() and dest.stat().st_size > 2000:
        logger.debug(f"  Già presente: {dest.name}")
        return dest

    content = await _get(client, entry.pdf_url)
    if not content or len(content) < 1000:
        logger.warning(f"  PDF non valido o vuoto: {entry.pdf_url}")
        return None

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    size_kb = len(content) // 1024
    logger.info(f"  ✅ {size_kb}KB — {dest.name}")
    return dest


async def upload_pdf(
    client: httpx.AsyncClient,
    pdf_path: Path,
    workspace: str,
) -> bool:
    # Timeout dinamico: 120s base + 3s per MB (file grandi come 73MB richiedono ~350s)
    size_mb = pdf_path.stat().st_size / (1024 * 1024)
    timeout = max(120.0, 60.0 + size_mb * 4)
    try:
        with open(pdf_path, "rb") as f:
            resp = await client.post(
                f"{API_URL}/ingest",
                data={"workspace": workspace, "corpus": "dottrina"},
                files={"file": (pdf_path.name, f, "application/pdf")},
                timeout=timeout,
            )
        if resp.status_code in (200, 201):
            data = resp.json()
            logger.success(
                f"  ✅ Caricato: chunks={data.get('chunk_count','?')} — {pdf_path.name}"
            )
            return True
        logger.error(f"  ❌ Upload {resp.status_code}: {resp.text[:150]}")
        return False
    except Exception as exc:
        logger.error(f"  ❌ Upload errore: {exc}")
        return False


# ---------------------------------------------------------------------------
# Registro fonti
# ---------------------------------------------------------------------------

SOURCES: dict[str, any] = {
    "dpc_archivio":           scrape_dpc_archivio,
    "dpc_trimestrale":        scrape_dpc_trimestrale,
    "federalismi":            scrape_federalismi,
    "diritti_fondamentali":   scrape_diritti_fondamentali,
    "questione_giustizia":    scrape_questione_giustizia,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(
    sources: list[str],
    workspace: str,
    dry_run: bool,
    no_upload: bool,
    limit: int,
) -> None:
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
    done = _load_state()
    logger.info(f"State: {len(done)} URL già processati")

    if not no_upload and not dry_run:
        try:
            async with httpx.AsyncClient() as c:
                r = await c.get(f"{API_URL}/health", timeout=5)
                r.raise_for_status()
                logger.info(f"API online ✅")
        except Exception as exc:
            logger.error(f"API non raggiungibile: {exc}")
            logger.info("Suggerimento: usa --no-upload per scaricare senza caricare")
            return

    stats = ScrapeStats()

    for source_name in sources:
        if source_name not in SOURCES:
            logger.error(f"Fonte non valida: {source_name}. Disponibili: {list(SOURCES)}")
            continue

        logger.info(f"\n{'='*60}\n  Fonte: {source_name.upper()}\n{'='*60}")
        scraper_fn = SOURCES[source_name]

        try:
            entries = await scraper_fn(done)
        except Exception as exc:
            logger.error(f"Errore scraping {source_name}: {exc}")
            continue

        if limit > 0:
            entries = entries[:limit]

        stats.found += len(entries)
        logger.info(f"  → {len(entries)} PDF da scaricare")

        if dry_run:
            for e in entries[:5]:
                logger.info(f"    {e.pdf_url}")
            if len(entries) > 5:
                logger.info(f"    ... e altri {len(entries)-5}")
            continue

        async with httpx.AsyncClient(headers=HEADERS) as client:
            for entry in entries:
                await asyncio.sleep(RATE_LIMIT_S)
                pdf_path = await download_pdf(client, entry, DOWNLOAD_DIR)

                if not pdf_path:
                    stats.errors += 1
                    done.add(entry.pdf_url)
                    continue

                stats.downloaded += 1
                done.add(entry.pdf_url)

                if not no_upload:
                    if await upload_pdf(client, pdf_path, workspace):
                        stats.uploaded += 1

        _save_state(done)
        logger.info(
            f"  Fonte completata: scaricati={stats.downloaded} "
            f"caricati={stats.uploaded} errori={stats.errors}"
        )

    _save_state(done)
    logger.info(f"""
{'='*60}
  RIEPILOGO FINALE
  Trovati:    {stats.found}
  Scaricati:  {stats.downloaded}
  Caricati:   {stats.uploaded}
  Errori:     {stats.errors}
  State URL:  {len(done)}
{'='*60}""")

    if not no_upload and stats.downloaded > 0:
        logger.info(
            "\nPasso successivo — ricostruisci gli indici:\n"
            "  python scripts/build_jurisprudence_indexes.py --workspace mio-studio\n"
            "  (oppure build_indexes.py per rigenerare tutto)"
        )


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scraper dottrina giuridica italiana")
    p.add_argument("--source", "-s", choices=list(SOURCES), nargs="+",
                   default=list(SOURCES))
    p.add_argument("--workspace", "-w", default="mio-studio")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-upload", action="store_true")
    p.add_argument("--limit", type=int, default=0,
                   help="Max PDF per fonte (0=tutti)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(main(
        sources=args.source,
        workspace=args.workspace,
        dry_run=args.dry_run,
        no_upload=args.no_upload,
        limit=args.limit,
    ))
