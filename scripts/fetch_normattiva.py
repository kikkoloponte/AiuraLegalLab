"""
Fetch Normattiva: scarica documenti dall'API pubblica Normattiva e li salva
direttamente in aiura_legal.normattiva_docs.

Uso:
  # Scarica atti per URN specifico (DPR 600/1973, CPA, ecc.)
  python scripts/fetch_normattiva.py --urn \\
      "urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600" \\
      "urn:nir:stato:decreto.legislativo:2010-07-02;104"

  # Scarica tutte le leggi del 2023
  python scripts/fetch_normattiva.py --tipo legge --anno 2023

  # Scarica i 4 codici maggiori via web scraping
  python scripts/fetch_normattiva.py --codici cc cp cpc cpp

  # Dry-run: conta quanti atti ci sono senza scrivere
  python scripts/fetch_normattiva.py --tipo legge --anno 2023 --dry-run

  # Con limite
  python scripts/fetch_normattiva.py --tipo legge --anno 2023 --limit 100

Flags:
  --urn       Uno o più URN atto da scaricare (es. urn:nir:stato:dlgs:2010-07-02;104)
  --tipo      Tipo NIR provvedimento (es. legge, decreto.legislativo, dpr)
  --anno      Anno di emanazione (richiesto con --tipo)
  --codici    Alias codice (cc=Codice Civile, cp=Penale, cpc=Proc. Civile, cpp=Proc. Penale)
  --dry-run   Conta gli atti senza scrivere
  --limit N   Scarica al massimo N articoli per atto
  --delay     Secondi di pausa tra richieste (default: 0.4)

NOTA: Questo script effettua chiamate HTTP a Normattiva.it.
Usa solo se legal_lab.normattiva_docs non ha già i dati necessari.
Per il caso normale usare mirror_normattiva.py che copia il DB esistente.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pymongo
from bs4 import BeautifulSoup
from loguru import logger

from aiura_legal.ingestion.mongodb.client import settings
from aiura_legal.ingestion.normattiva.connector import (
    NormattivaSearchConnector,
    NormattivaFetcher,
    NormattivaWebFetcher,
    CODICI_WEB,
    TIPI,
)


# ---------------------------------------------------------------------------
# Helpers MongoDB
# ---------------------------------------------------------------------------

def _get_dest_col() -> pymongo.collection.Collection:
    """Connessione RW a aiura_legal.normattiva_docs."""
    client = pymongo.MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
    try:
        client.admin.command("ping")
    except Exception as e:
        logger.error(f"MongoDB destinazione non raggiungibile: {e}")
        sys.exit(1)
    col = client[settings.mongodb_database]["normattiva_docs"]
    col.create_index("urn", unique=True, background=True)
    col.create_index("act_urn", background=True)
    col.create_index("testo_tipo", background=True)
    return col


def _upsert_docs(
    col: pymongo.collection.Collection,
    docs: list[dict],
    now_iso: str,
) -> int:
    """Upserta una lista di documenti per URN. Ritorna il conteggio scritto."""
    if not docs:
        return 0
    ops = []
    for doc in docs:
        urn = doc.get("urn", "")
        if not urn:
            continue
        doc_clean = {k: v for k, v in doc.items() if k != "_id"}
        doc_clean["aiura_fetched_at"] = now_iso
        ops.append(
            pymongo.UpdateOne(
                {"urn": urn},
                {"$set": doc_clean},
                upsert=True,
            )
        )
    if not ops:
        return 0
    result = col.bulk_write(ops, ordered=False)
    return result.upserted_count + result.modified_count


# ---------------------------------------------------------------------------
# Helpers: parse URN → metadati atto
# ---------------------------------------------------------------------------

_MESI = [
    "", "gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
    "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre",
]

# Inverso di TIPI (tipo_nir → denominazione API)
_NIR_TO_DENOM: dict[str, str] = {v.lower(): v for v in TIPI.values()}
# Aggiungi gli alias nir (es. "decreto.legislativo" → "DECRETO LEGISLATIVO")
_NIR_TO_DENOM.update({k: TIPI[v] for k, v in {
    "decreto.legislativo":                       "decreto.legislativo",
    "decreto.del.presidente.della.repubblica":   "dpr",
    "legge":                                     "legge",
    "decreto.legge":                             "decreto.legge",
    "regio.decreto":                             "regio.decreto",
    "legge.costituzionale":                      "legge.costituzionale",
    "decreto.ministeriale":                      "dm",
    "decreto.del.presidente.del.consiglio.dei.ministri": "dpcm",
}.items() if v in TIPI})


def _tipo_prov_from_urn(act_urn: str) -> str:
    """Estrae tipo_provvedimento human-readable dall'URN NIR."""
    m = re.search(r"urn:nir:stato:([^:]+):", act_urn)
    if not m:
        return ""
    nir_tipo = m.group(1).lower()
    # Cerca in TIPI (keys sono alias come "dpr", "decreto.legislativo"…)
    for alias, denominazione in TIPI.items():
        if alias == nir_tipo:
            return denominazione
    # Fallback: converti nir_tipo → stringa leggibile
    return nir_tipo.replace(".", " ").upper()


def _titolo_from_urn(act_urn: str) -> str:
    """Genera un titolo human-readable dall'URN dell'atto."""
    m = re.search(r"urn:nir:stato:([^:]+):(\d{4}-\d{2}-\d{2});(\d+\w*)", act_urn)
    if not m:
        return act_urn
    tipo, data, numero = m.group(1), m.group(2), m.group(3)
    tipo_str = _tipo_prov_from_urn(act_urn) or tipo.replace(".", " ").upper()
    parts = data.split("-")
    try:
        data_str = f"{int(parts[2])} {_MESI[int(parts[1])]} {parts[0]}"
    except (IndexError, ValueError):
        data_str = data
    return f"{tipo_str} {data_str}, n. {numero}"


# ---------------------------------------------------------------------------
# Parser HTML → testo + metadati articolo
# ---------------------------------------------------------------------------

def _html_to_doc(art_urn: str, act_urn: str, raw: dict, tipo_prov: str, titolo: str) -> dict | None:
    """
    Converte la risposta grezza dell'API Normattiva in un documento normattiva_docs.
    Ritorna None se non c'è testo valido.
    """
    atto = (raw.get("data") or {}).get("atto") or {}
    html = atto.get("articoloHtml", "") or atto.get("html", "") or atto.get("testo", "")
    if not html:
        return None

    # Testo plain
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return None

    # Numero articolo — prima da CSS class AKN, poi regex sul testo
    num_tag = soup.find(class_="article-num-akn") or soup.find(class_="num-akn")
    articolo_num = num_tag.get_text(strip=True) if num_tag else ""
    if not articolo_num:
        m = re.search(r"(Art(?:icolo)?\.?\s*\d+[a-z\-]*\.?)", text[:200], re.I)
        articolo_num = m.group(1) if m else ""

    # Rubrica articolo
    heading_tag = soup.find(class_=re.compile(r"heading-akn|rubric|heading", re.I))
    titolo_articolo = heading_tag.get_text(strip=True) if heading_tag else ""

    # Data inizio vigenza (campo API, vari formati possibili)
    raw_date = (
        atto.get("dataInizioVigenza")
        or atto.get("dataEmanazione")
        or atto.get("dataVigenza")
        or ""
    )
    data_inizio = ""
    if re.match(r"\d{1,2}-\d{1,2}-\d{4}", str(raw_date)):
        p = str(raw_date).split("-")
        data_inizio = f"{p[2]}{int(p[1]):02d}{int(p[0]):02d}"
    elif re.match(r"\d{4}-\d{2}-\d{2}", str(raw_date)):
        data_inizio = str(raw_date).replace("-", "")[:8]

    return {
        "urn":               art_urn,
        "act_urn":           act_urn,
        "text":              text,
        "titolo":            titolo,
        "titolo_articolo":   titolo_articolo,
        "articolo_num":      articolo_num,
        "testo_tipo":        "normativo",
        "tipo_provvedimento": tipo_prov,
        "source_id":         "normattiva_it",
        "source":            "normattiva_it",
        "data_inizio_vigenza": data_inizio or "",
        "data_fine_vigenza":   "99999999",
    }


# ---------------------------------------------------------------------------
# Fetch per URN atto (nuovo) ─────────────────────────────────────────────────
# ---------------------------------------------------------------------------

def _fetch_by_urn(
    col: pymongo.collection.Collection,
    act_urns: list[str],
    limit: int | None,
    dry_run: bool,
    delay: float,
) -> int:
    """
    Scarica tutti gli articoli di una lista di atti per URN diretto.

    Usa NormattivaWebFetcher.stream_articles_from_params() che naviga il sito
    Normattiva via AJAX articolo per articolo — funziona per qualsiasi atto,
    non solo i 4 codici maggiori.

    L'URN di ogni articolo è costruito come {act_urn}~art{pos} dove pos è la
    posizione sequenziale nella chain del sito (identico allo schema usato
    dagli altri atti nel sistema).
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    total_written = 0

    for act_urn in act_urns:
        tipo_prov = _tipo_prov_from_urn(act_urn)
        titolo    = _titolo_from_urn(act_urn)
        logger.info(f"Fetch atto: {act_urn}")
        logger.info(f"  tipo: {tipo_prov!r}  |  titolo: {titolo!r}")

        if dry_run:
            logger.info("  [dry-run] Skip.")
            continue

        web = NormattivaWebFetcher(delay=delay, timeout=120)  # timeout alto per atti voluminosi
        docs: list[dict] = []
        count = 0

        try:
            for pos, meta, text in web.stream_articles_from_params(
                act_urn=act_urn,
                codice_id="",   # non usato dalla web fetcher nell'implementazione attuale
                data_gu="",     # idem
            ):
                if limit and count >= limit:
                    logger.info(f"  Limite {limit} raggiunto.")
                    break
                if not text.strip():
                    continue

                art_urn = f"{act_urn}~art{pos}"
                doc = {
                    "urn":               art_urn,
                    "act_urn":           act_urn,
                    "text":              text,
                    "titolo":            titolo,
                    "titolo_articolo":   meta.get("titolo_articolo", ""),
                    "articolo_num":      meta.get("articolo_num", ""),
                    "testo_tipo":        "normativo",
                    "tipo_provvedimento": tipo_prov,
                    "source_id":         "normattiva_it",
                    "source":            "normattiva_it",
                    "data_inizio_vigenza": meta.get("data_inizio_vigenza", ""),
                    "data_fine_vigenza":   "99999999",
                }
                docs.append(doc)
                count += 1

                if count % 50 == 0:
                    logger.info(f"  {count} articoli scaricati…")

        except Exception as e:
            logger.error(f"  Errore su {act_urn}: {e}")
        finally:
            web.close()

        n = _upsert_docs(col, docs, now_iso)
        logger.success(
            f"  {act_urn}: {count} articoli scaricati, {n} scritti/aggiornati"
        )
        total_written += n

    return total_written


# ---------------------------------------------------------------------------
# Fetch per tipo/anno (fix: usa stream_articles invece di fetch_articles)
# ---------------------------------------------------------------------------

def _fetch_by_tipo_anno(
    col: pymongo.collection.Collection,
    tipo: str,
    anno: int,
    limit: int | None,
    dry_run: bool,
    delay: float,
) -> int:
    """Scarica articoli per tipo NIR + anno."""
    now_iso = datetime.now(timezone.utc).isoformat()
    searcher = NormattivaSearchConnector()
    fetcher = NormattivaFetcher(delay_article=delay)

    logger.info(f"Ricerca atti: tipo={tipo!r}, anno={anno}")
    try:
        urns = list(searcher.search_urns(tipo=tipo, anno_da=anno, anno_a=anno))
    except ValueError as e:
        logger.error(f"Tipo non valido: {e}")
        logger.info(f"Tipi disponibili: {sorted(TIPI.keys())}")
        sys.exit(1)

    logger.info(f"  URN trovati: {len(urns):,}")

    if dry_run:
        logger.info("[dry-run] Nessuna scrittura. Fine.")
        return len(urns)

    written = 0
    errors = 0

    for i, act_urn in enumerate(urns, 1):
        tipo_prov = _tipo_prov_from_urn(act_urn)
        titolo    = _titolo_from_urn(act_urn)
        try:
            docs: list[dict] = []
            count = 0
            for art_urn, raw in fetcher.stream_articles(act_urn):
                if limit and count >= limit:
                    break
                doc = _html_to_doc(art_urn, act_urn, raw, tipo_prov, titolo)
                if doc:
                    docs.append(doc)
                    count += 1
            n = _upsert_docs(col, docs, now_iso)
            written += n
            if i % 20 == 0 or i == len(urns):
                logger.info(f"  {i}/{len(urns)} atti ({written} articoli scritti)")
        except Exception as e:
            logger.warning(f"  Errore su {act_urn}: {e}")
            errors += 1
            continue

    logger.success(
        f"Fetch completato: {len(urns)} atti, {written} articoli scritti, {errors} errori"
    )
    return written


# ---------------------------------------------------------------------------
# Fetch codici via web
# ---------------------------------------------------------------------------

def _fetch_codici(
    col: pymongo.collection.Collection,
    codici: list[str],
    limit: int | None,
    dry_run: bool,
    delay: float,
) -> int:
    """Scarica i codici maggiori via NormattivaWebFetcher."""
    now_iso = datetime.now(timezone.utc).isoformat()
    web = NormattivaWebFetcher()

    alias_map = {"cc": "cc", "cp": "cp", "cpc": "cpc", "cpp": "cpp"}
    valid = {alias_map[c] for c in codici if c in alias_map}
    unknown = [c for c in codici if c not in alias_map]
    if unknown:
        logger.warning(f"Alias sconosciuti ignorati: {unknown}. Validi: cc, cp, cpc, cpp")

    total_written = 0

    for key in valid:
        info = CODICI_WEB[key]
        logger.info(f"Scaricamento {info['label']} …")

        if dry_run:
            logger.info(f"  [dry-run] Salta {info['label']}")
            continue

        written = 0
        errors = 0
        count = 0

        try:
            for pos, meta, text in web.stream_articles(key):
                if limit and count >= limit:
                    break

                art_num = pos
                art_urn = f"{info['act_urn']}~art{art_num}"
                doc = {
                    "urn":               art_urn,
                    "act_urn":           info["act_urn"],
                    "text":              text,
                    "titolo":            info["titolo"],
                    "titolo_articolo":   meta.get("titolo_articolo", ""),
                    "articolo_num":      meta.get("articolo_num", ""),
                    "testo_tipo":        "normativo",
                    "tipo_provvedimento": info["tipo_provvedimento"],
                    "source_id":         "normattiva_it",
                    "source":            "normattiva_it",
                    "data_inizio_vigenza": meta.get("data_inizio_vigenza", ""),
                    "data_fine_vigenza":   "99999999",
                }
                n = _upsert_docs(col, [doc], now_iso)
                written += n
                count += 1

        except Exception as e:
            logger.error(f"  Errore su {info['label']}: {e}")
            errors += 1

        logger.success(f"  {info['label']}: {written} articoli scritti ({errors} errori)")
        total_written += written

    return total_written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch da Normattiva API → aiura_legal.normattiva_docs"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--urn", nargs="+", metavar="URN",
        help="URN atto da scaricare (es. urn:nir:stato:decreto.legislativo:2010-07-02;104)",
    )
    group.add_argument(
        "--tipo", default=None,
        help="Tipo NIR provvedimento (es. legge, decreto.legislativo, dpr)",
    )
    group.add_argument(
        "--codici", nargs="+", choices=["cc", "cp", "cpc", "cpp"],
        help="Alias codici (cc=Civile, cp=Penale, cpc=Proc.Civile, cpp=Proc.Penale)",
    )
    parser.add_argument("--anno", type=int, default=None,
                        help="Anno emanazione (richiesto con --tipo)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Conta/mostra senza scrivere")
    parser.add_argument("--limit", type=int, default=None,
                        help="Numero massimo articoli per atto da scaricare")
    parser.add_argument("--delay", type=float, default=0.4,
                        help="Pausa tra richieste HTTP in secondi (default: 0.4)")
    args = parser.parse_args()

    if args.tipo and not args.anno:
        parser.error("--anno è obbligatorio con --tipo")

    col = _get_dest_col()

    if args.urn:
        _fetch_by_urn(
            col=col,
            act_urns=args.urn,
            limit=args.limit,
            dry_run=args.dry_run,
            delay=args.delay,
        )
    elif args.tipo:
        _fetch_by_tipo_anno(
            col=col,
            tipo=args.tipo,
            anno=args.anno,
            limit=args.limit,
            dry_run=args.dry_run,
            delay=args.delay,
        )
    else:
        _fetch_codici(
            col=col,
            codici=args.codici,
            limit=args.limit,
            dry_run=args.dry_run,
            delay=args.delay,
        )


if __name__ == "__main__":
    main()
