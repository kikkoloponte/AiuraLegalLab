"""
Connettori Normattiva — standalone, senza dipendenze da AIura.

NormattivaSearchConnector  → scopre URN per tipo/anno via API REST ufficiale
NormattivaFetcher          → scarica il documento per URN (Open Data API)
NormattivaWebFetcher       → scarica articoli via AJAX dal sito web (per i codici)
"""
from __future__ import annotations

import re
import time
from typing import Iterator, Optional

import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_exception

_BASE = "https://api.normattiva.it/t/normattiva.api/bff-opendata/v1/api/v1"
_WEB  = "https://www.normattiva.it"

_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://dati.normattiva.it",
    "Referer": "https://dati.normattiva.it/",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

_WEB_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ── Codici maggiori — parametri sito web Normattiva ──────────────────────────
# Ogni codice ha: act_urn, codiceRedazionale, dataPubblicazioneGazzetta.
# Usati da NormattivaWebFetcher per navigazione AJAX articolo per articolo.
CODICI_WEB = {
    "cc": {
        "label":           "Codice Civile",
        "titolo":          "REGIO DECRETO 16 marzo 1942, n. 262",
        "act_urn":         "urn:nir:stato:regio.decreto:1942-03-16;262",
        "codiceRedaz":     "042U0262",
        "dataGU":          "1942-04-04",
        "tipo_provvedimento": "REGIO DECRETO",
        "codice_provvedimento": "RDL",
        "numero":          "262",
        "anno":            1942,
        "gazzetta_anno":   1942,
        "gazzetta_numero": "79",
    },
    "cp": {
        "label":           "Codice Penale",
        "titolo":          "REGIO DECRETO 19 ottobre 1930, n. 1398",
        "act_urn":         "urn:nir:stato:regio.decreto:1930-10-19;1398",
        "codiceRedaz":     "030U1398",
        "dataGU":          "1930-10-26",
        "tipo_provvedimento": "REGIO DECRETO",
        "codice_provvedimento": "RDL",
        "numero":          "1398",
        "anno":            1930,
        "gazzetta_anno":   1930,
        "gazzetta_numero": "251",
    },
    "cpc": {
        "label":           "Codice di Procedura Civile",
        "titolo":          "REGIO DECRETO 28 ottobre 1940, n. 1443",
        "act_urn":         "urn:nir:stato:regio.decreto:1940-10-28;1443",
        "codiceRedaz":     "040U1443",
        "dataGU":          "1940-10-28",
        "tipo_provvedimento": "REGIO DECRETO",
        "codice_provvedimento": "RDL",
        "numero":          "1443",
        "anno":            1940,
        "gazzetta_anno":   1941,
        "gazzetta_numero": "28",
    },
    "cpp": {
        "label":           "Codice di Procedura Penale",
        "titolo":          "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447",
        "act_urn":         "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447",
        "codiceRedaz":     "088G0492",
        "dataGU":          "1988-10-24",
        "tipo_provvedimento": "DECRETO DEL PRESIDENTE DELLA REPUBBLICA",
        "codice_provvedimento": "DPR",
        "numero":          "447",
        "anno":            1988,
        "gazzetta_anno":   1988,
        "gazzetta_numero": "250",
    },
}

# Mapping tipo NIR → denominazione API
TIPI = {
    "legge":                  "LEGGE",
    "legge.costituzionale":   "LEGGE COSTITUZIONALE",
    "decreto.legislativo":    "DECRETO LEGISLATIVO",
    "decreto.legge":          "DECRETO-LEGGE",
    "regio.decreto":          "REGIO DECRETO",
    "dpr":                    "DECRETO DEL PRESIDENTE DELLA REPUBBLICA",
    "dpcm":                   "DECRETO DEL PRESIDENTE DEL CONSIGLIO DEI MINISTRI",
    "dm":                     "DECRETO MINISTERIALE",
}

ALIAS = {
    "dlgs": "decreto.legislativo",
    "dl":   "decreto.legge",
    "rd":   "regio.decreto",
    "lc":   "legge.costituzionale",
}

# Mapping idSottoArticolo → suffisso NIR (bis, ter, …)
# Alcuni TU compilati usano idSottoArticolo > 1 per articoli inseriti
# successivamente (art. 7-bis, art. 7-ter, ecc.).
_SOTTO_SUFFIXES: dict[int, str] = {
    1: "",
    2: "bis",
    3: "ter",
    4: "quater",
    5: "quinquies",
    6: "sexies",
    7: "septies",
    8: "octies",
    9: "novies",
    10: "decies",
}

# Soglia di errori AJAX-500 consecutivi prima di passare al fallback N2Ls.
# Valore 1 = switch immediato al primo 500 (consigliato: i 500 su Normattiva
# sono bug server deterministici, non errori transitori → non vale la pena
# aspettare i retry dell'exponential backoff).
_AJAX_500_FALLBACK_THRESHOLD = 1


def _art_suffix_from_params(params: dict) -> str:
    """
    Costruisce il suffisso NIR ~artXxx dai parametri caricaArticolo della sidebar.

    Es.:  idArticolo=8,  idSottoArticolo=1  →  "art8"
          idArticolo=7,  idSottoArticolo=2  →  "art7bis"
          idArticolo=52, idSottoArticolo=2  →  "art52bis"
    """
    art_id = params.get("art.idArticolo", "")
    sotto  = int(params.get("art.idSottoArticolo", "1") or "1")
    suf    = _SOTTO_SUFFIXES.get(sotto, f"_{sotto}")
    return f"art{art_id}{suf}"


def resolve_tipo(tipo: str) -> str:
    return ALIAS.get(tipo, tipo)


# ── Search connector ──────────────────────────────────────────────────────────

class NormattivaSearchConnector:
    """Scopre URN disponibili su Normattiva per tipo e intervallo di anni."""

    def __init__(self, delay: float = 1.2, timeout: int = 30):
        self._delay = delay
        self._timeout = timeout
        self._client = httpx.Client(headers=_HEADERS, timeout=timeout)

    def search_urns(
        self,
        tipo: str,
        anno_da: int,
        anno_a: int,
        max_per_anno: int = 500,
    ) -> list[str]:
        denominazione = TIPI.get(tipo)
        if not denominazione:
            raise ValueError(f"Tipo '{tipo}' non valido. Tipi: {sorted(TIPI)}")

        all_urns: list[str] = []
        seen: set[str] = set()

        for anno in range(anno_da, anno_a + 1):
            page, year_count = 1, 0
            while year_count < max_per_anno:
                try:
                    items, total_pages = self._search_page(denominazione, anno, page)
                except Exception as e:
                    print(f"  [WARN] anno {anno} pag.{page}: {e}")
                    break

                for item in items:
                    urn = self._extract_urn(item, tipo)
                    if urn and urn not in seen:
                        seen.add(urn)
                        all_urns.append(urn)
                        year_count += 1

                if page >= total_pages or not items:
                    break
                page += 1
                time.sleep(self._delay)

            print(f"  Anno {anno}: {year_count} URN")
            time.sleep(self._delay)

        return all_urns

    def _search_page(self, denominazione: str, anno: int, page: int) -> tuple[list, int]:
        body = {
            "denominazioneAtto": denominazione,
            "annoProvvedimento": str(anno),
            "orderType": "vecchio",
            "paginazione": {"paginaCorrente": page, "numeroElementiPerPagina": 100},
        }
        r = self._client.post(f"{_BASE}/ricerca/avanzata", json=body)
        r.raise_for_status()
        data = r.json()
        items = (data.get("listaAtti")
                 or data.get("data", {}).get("listaAtti")
                 or [])
        pages = int(data.get("numeroPagine")
                    or data.get("data", {}).get("numeroPagine")
                    or 1)
        return items, pages

    def _extract_urn(self, item: dict, tipo: str) -> Optional[str]:
        for field in ("urn", "uri", "nir", "urnNir"):
            val = item.get(field, "")
            if val and "urn:nir:" in str(val):
                m = re.search(r"urn:nir:[^\s\"'<>]+", str(val))
                if m:
                    return m.group(0)

        # Costruzione da campo strutturati
        anno   = item.get("annoProvvedimento") or item.get("anno", "")
        numero = item.get("numeroProvvedimento") or item.get("numero", "")
        data   = item.get("dataProvvedimento") or item.get("dataEmanazione") or f"{anno}-01-01"

        if re.match(r"\d{4}-\d{2}-\d{2}", str(data)):
            data_str = str(data)[:10]
        elif anno:
            data_str = f"{anno}-01-01"
        else:
            return None

        if not numero:
            return None

        return f"urn:nir:stato:{tipo}:{data_str};{numero}"


# ── Fetcher ───────────────────────────────────────────────────────────────────

class NormattivaFetcher:
    """Scarica documenti da Normattiva per URN."""

    def __init__(self, delay: float = 1.0, delay_article: float = 0.3, timeout: int = 30):
        self._delay = delay                    # ritardo tra atti diversi
        self._delay_article = delay_article    # ritardo tra articoli dello stesso atto
        self._timeout = timeout
        self._client = httpx.Client(headers=_HEADERS, timeout=timeout)

    @retry(
        retry=retry_if_exception_type((httpx.TransportError, httpx.TimeoutException)),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def fetch(self, urn: str) -> dict:
        """
        Scarica un singolo atto o articolo.
        Ritenta fino a 3 volte su errori di rete (connection reset, timeout).
        """
        r = self._client.post(
            f"{_BASE}/atto/dettaglio-atto-urn",
            json={"urn": urn},
        )
        r.raise_for_status()
        return r.json()

    def stream(self, urns: list[str]) -> Iterator[tuple[str, dict]]:
        """Genera (urn, raw_json) per ogni URN base (un atto = un item), con rate limiting."""
        for urn in urns:
            try:
                yield urn, self.fetch(urn)
                time.sleep(self._delay)
            except Exception as e:
                print(f"  [ERR] {urn}: {e}")
                time.sleep(self._delay * 2)

    def stream_articles(
        self,
        act_urn: str,
        max_articles: int = 5000,
        max_consecutive_empty: int = 10,
    ) -> Iterator[tuple[str, dict]]:
        """
        Scarica tutti gli articoli di un atto iterando ~art1, ~art2, ...

        Segnali di FINE reale (stop):
          - success is None / null  → l'articolo non esiste nel DB Normattiva
          - HTTP 404                → idem
          - max_consecutive_empty articoli con html vuoto di fila → fine documento

        Segnali di GAP (skip, non stop):
          - success=True ma html=""  → articolo abrogato o heading di sezione
            senza testo (comune nei codici: Libro I, Titolo II, ecc.)
            Si salta e si continua la scansione.

        Yields: (article_urn, raw_json) solo per articoli con html non vuoto.

        max_consecutive_empty: quanti articoli vuoti consecutivi tollerare
        prima di dichiarare la fine del documento (default 10 — sufficiente
        per i codici con sezioni/titoli privi di testo).
        """
        consecutive_empty = 0

        for i in range(1, max_articles + 1):
            art_urn = f"{act_urn}~art{i}"
            try:
                raw = self.fetch(art_urn)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    break                               # fine reale
                print(f"  [WARN] {art_urn}: HTTP {e.response.status_code}")
                # Errore transitorio (429, 500, 503): tratta come gap e continua
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    break
                time.sleep(self._delay_article)
                continue
            except Exception as e:
                print(f"  [WARN] {art_urn}: {e}")
                # Connection reset / errore di rete: ricrea il client e tratta come gap
                self._client = httpx.Client(headers=_HEADERS, timeout=self._timeout)
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    break
                time.sleep(self._delay_article * 3)
                continue

            success = raw.get("success")
            atto    = (raw.get("data") or {}).get("atto") or {}
            html    = atto.get("articoloHtml", "") if atto else ""

            if success is None:
                break                                   # articolo non esiste → fine reale

            if not html:
                # GAP: heading di sezione o articolo abrogato senza testo
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    break                               # troppi gap = fine documento
                time.sleep(self._delay_article)
                continue

            # Articolo con testo → reset contatore gap e yield
            consecutive_empty = 0
            yield art_urn, raw
            time.sleep(self._delay_article)


# ── Web Fetcher (codici maggiori) ─────────────────────────────────────────────

class NormattivaWebFetcher:
    """
    Scarica articoli dei codici maggiori (CC, CP, CPC, CPP) dal sito
    www.normattiva.it tramite chain-navigation AJAX articolo per articolo.

    Motivazione: l'Open Data API restituisce solo la formula promulgatoria
    (~art1) per questi atti — il sito web espone invece tutti gli articoli
    tramite l'endpoint /atto/caricaArticolo con cookie di sessione.

    Utilizzo tipico::

        fetcher = NormattivaWebFetcher()
        for pos, meta, text in fetcher.stream_articles("cc"):
            ...  # meta: dict con articolo_num, titolo_articolo, data_vigenza, …

    Oppure con le info del codice già note::

        for pos, meta, text in fetcher.stream_articles_from_params(
            act_urn   = "urn:nir:stato:regio.decreto:1942-03-16;262",
            codice_id = "042U0262",
            data_gu   = "1942-04-04",
        ):
            ...
    """

    def __init__(self, delay: float = 0.5, timeout: int = 45):
        self._delay   = delay
        self._timeout = timeout
        self._client: Optional[httpx.Client] = None

    # ── session ──────────────────────────────────────────────────────────────

    def _ensure_session(self, referer: str) -> None:
        if self._client is None:
            self._client = httpx.Client(
                follow_redirects=True,
                timeout=self._timeout,
                headers=_WEB_HEADERS,
            )
            # 1) homepage → cookies di sessione
            self._client.get(_WEB + "/")
        # 2) pagina atto → aggiorna sessione e stato server
        self._client.get(referer, headers={"Accept": "text/html,*/*"})

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    # ── seed parameters ───────────────────────────────────────────────────────

    def _extract_seed_params(self, page_html: str) -> dict:
        """
        Estrae i parametri per il primo articolo dalla sidebar della pagina N2Ls.
        Cerca il primo onclick su caricaArticolo senza 'imUpdate=true'.
        """
        for m in re.finditer(r"caricaArticolo\?([^'\"]+)", page_html):
            qs = m.group(1)
            if "imUpdate=true" not in qs:
                params = {}
                for part in qs.rstrip("&").split("&"):
                    if "=" in part:
                        k, v = part.split("=", 1)
                        params[k.strip()] = v.strip()
                if params.get("art.idArticolo"):
                    return params
        raise ValueError("Nessun parametro caricaArticolo trovato nella pagina")

    def _extract_sidebar_params(self, page_html: str) -> list[dict]:
        """
        Estrae dalla sidebar N2Ls la lista COMPLETA dei parametri di ogni articolo,
        in ordine di catena (posizione 1 = primo articolo).

        Deduplica per (idGruppo, idArticolo) tenendo il link principale
        (senza imUpdate=true). Utile per la resumption rapida: possiamo
        saltare direttamente alla prima posizione non ancora salvata senza
        scaricare i precedenti.
        """
        seen: set[tuple] = set()
        chain: list[dict] = []

        for m in re.finditer(r"caricaArticolo\?([^'\"]+)", page_html):
            qs = m.group(1)
            if "imUpdate=true" in qs:
                continue
            params = {}
            for part in qs.rstrip("&").split("&"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    params[k.strip()] = v.strip()
            if not params.get("art.idArticolo"):
                continue
            key = (params.get("art.idGruppo",""), params.get("art.idArticolo",""))
            if key not in seen:
                seen.add(key)
                chain.append(params)

        return chain

    # ── single article fetch ──────────────────────────────────────────────────

    @retry(
        retry=(
            retry_if_exception_type((httpx.TransportError, httpx.TimeoutException))
            | retry_if_exception(lambda e: isinstance(e, httpx.HTTPStatusError) and e.response.status_code >= 500)
        ),
        wait=wait_exponential(multiplier=1, min=3, max=60),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _fetch_article(self, params: dict, referer: str) -> str:
        """HTTP GET su /atto/caricaArticolo, ritorna il body XML grezzo."""
        r = self._client.get(
            _WEB + "/atto/caricaArticolo",
            params=params,
            headers={
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": referer,
            },
        )
        r.raise_for_status()
        return r.text

    # ── response parsing ──────────────────────────────────────────────────────

    @staticmethod
    def _parse_article_response(xml_text: str) -> tuple[str, dict, Optional[dict]]:
        """
        Analizza la risposta XML di caricaArticolo.

        Ritorna (text, article_meta, next_params) dove:
          text         – testo pulito (strip tag, newline normalizzati)
          article_meta – dict con: articolo_num, titolo_articolo,
                         data_inizio_vigenza, descrizione, progressivo
          next_params  – dict params per il prossimo articolo, o None se ultimo
        """
        soup = BeautifulSoup(xml_text, "html.parser")

        # ── testo ────────────────────────────────────────────────────────────
        body = soup.find(class_="bodyTesto")
        if body:
            content = (
                body.find(class_="attachment-just-text")
                or body.find(class_="art-just-text-akn")
                or body
            )
            raw_text = content.get_text(separator="\n", strip=True)
        else:
            raw_text = soup.get_text(separator="\n", strip=True)

        # normalizza spazi bianchi eccessivi
        text = re.sub(r"\n{3,}", "\n\n", raw_text).strip()

        # ── metadati dall'HTML commentato ────────────────────────────────────
        meta_raw: dict[str, str] = {}
        for m in re.finditer(r"<p>\s*([\w]+)\s*:\s*([^<]+)</p>", xml_text):
            meta_raw[m.group(1).strip()] = m.group(2).strip()

        descrizione = meta_raw.get("descrizione", "")  # e.g. "Disposizioni…-art. 3"

        # ── numero articolo e rubrica ─────────────────────────────────────────
        # 1) da article-num-akn / num-akn CSS class (Akoma Ntoso)
        num_tag = soup.find(class_="article-num-akn") or soup.find(class_="num-akn")
        articolo_num = num_tag.get_text(strip=True) if num_tag else ""

        # 2) fallback: primo "Art. N." nel testo
        if not articolo_num:
            m = re.search(r"(Art(?:icolo)?\.?\s*\d+[a-z-]*(?:\s*-[a-z]+)?\.?)", text, re.I)
            articolo_num = m.group(1) if m else ""

        # ── rubrica ──────────────────────────────────────────────────────────
        heading_tag = soup.find(class_=re.compile(r"heading-akn", re.I))
        if not heading_tag:
            heading_tag = soup.find(class_=re.compile(r"rubric|heading|title", re.I))
        titolo_articolo = heading_tag.get_text(strip=True) if heading_tag else ""

        # ── data_inizio_vigenza ───────────────────────────────────────────────
        inizio_el = soup.find(id="artInizio")
        data_inizio = ""
        if inizio_el:
            raw_date = inizio_el.get_text(strip=True)  # e.g. "19-4-1942"
            m = re.match(r"(\d{1,2})-(\d{1,2})-(\d{4})", raw_date)
            if m:
                data_inizio = f"{m.group(3)}{int(m.group(2)):02d}{int(m.group(1)):02d}"

        # flagTipoArticolo=0 → preamble/promulgation (no normative content)
        # flagTipoArticolo=1 → regular article (normative)
        # flagTipoArticolo=2 → original (historical) version
        flag_tipo = meta_raw.get("flagTipoArticolo", "")

        article_meta = {
            "articolo_num":      articolo_num,
            "titolo_articolo":   titolo_articolo,
            "data_inizio_vigenza": data_inizio or "99999999",
            "descrizione":       descrizione,
            "progressivo":       meta_raw.get("progressivo", ""),
            "flag_tipo_articolo": flag_tipo,   # "0"=preamble, "1"=normative, "2"=orig
        }

        # ── prossimo articolo ─────────────────────────────────────────────────
        next_params = None
        for a in soup.find_all("a"):
            if "successivo" in a.get_text(strip=True):
                m2 = re.search(r"caricaArticolo\?([^'\"]+)", a.get("onclick", ""))
                if m2:
                    qs = m2.group(1).rstrip("&")
                    next_params = {}
                    for part in qs.split("&"):
                        if "=" in part:
                            k, v = part.split("=", 1)
                            next_params[k.strip()] = v.strip()
                break

        return text, article_meta, next_params

    # ── N2Ls page parser (pagina completa, non risposta AJAX) ────────────────

    @staticmethod
    def _parse_n2ls_page(html: str) -> tuple[str, dict]:
        """
        Parsa una pagina N2Ls completa (/uri-res/N2Ls?{urn}~artN) ed estrae
        (text, article_meta).

        Differisce da _parse_article_response perché:
        - La pagina è completa (nav, header, footer) — non solo il fragment AJAX
        - Non ha il puntatore "articolo successivo" — non serve perché iteriamo
          con la lista ricavata dalla sidebar
        """
        soup = BeautifulSoup(html, "html.parser")

        # ── testo ────────────────────────────────────────────────────────────
        body = soup.find(class_="bodyTesto") or soup.find(id="corpo")
        if body:
            content = (
                body.find(class_="art-just-text-akn")
                or body.find(class_="attachment-just-text")
                or body
            )
            raw_text = content.get_text(separator="\n", strip=True)
        else:
            raw_text = soup.get_text(separator="\n", strip=True)

        text = re.sub(r"\n{3,}", "\n\n", raw_text).strip()

        # ── numero articolo ───────────────────────────────────────────────────
        num_tag = (
            soup.find(class_="article-num-akn")
            or soup.find(class_="num-akn")
        )
        articolo_num = num_tag.get_text(strip=True) if num_tag else ""
        if not articolo_num:
            m = re.search(r"(Art(?:icolo)?\.?\s*\d+[a-z-]*(?:\s*-[a-z]+)?\.?)", text, re.I)
            articolo_num = m.group(1) if m else ""

        # ── rubrica ──────────────────────────────────────────────────────────
        heading_tag = soup.find(class_=re.compile(r"heading-akn", re.I))
        if not heading_tag:
            heading_tag = soup.find(class_=re.compile(r"rubric|heading|title", re.I))
        titolo_articolo = heading_tag.get_text(strip=True) if heading_tag else ""

        # ── data_inizio_vigenza ───────────────────────────────────────────────
        inizio_el  = soup.find(id="artInizio")
        data_inizio = ""
        if inizio_el:
            raw_date = inizio_el.get_text(strip=True)
            m = re.match(r"(\d{1,2})-(\d{1,2})-(\d{4})", raw_date)
            if m:
                data_inizio = f"{m.group(3)}{int(m.group(2)):02d}{int(m.group(1)):02d}"

        article_meta = {
            "articolo_num":        articolo_num,
            "titolo_articolo":     titolo_articolo,
            "data_inizio_vigenza": data_inizio or "99999999",
            "descrizione":         "",
            "progressivo":         "",
            "flag_tipo_articolo":  "1",
        }
        return text, article_meta

    # ── N2Ls streaming (fallback per atti con caricaArticolo rotto) ──────────

    def stream_articles_n2ls(
        self,
        act_urn:              str,
        sidebar_params:       Optional[list[dict]] = None,
        start_position:       int = 1,
        max_articles:         int = 2000,
        max_consecutive_miss: int = 15,
    ) -> Iterator[tuple[int, dict, str]]:
        """
        Scarica articoli via URI-resolver N2Ls invece di caricaArticolo AJAX.

        Usato come fallback quando caricaArticolo restituisce HTTP 500 persistente
        (noto su DPR 327/2001, DPR 602/1973, D.Lgs. 267/2000 e altri TU compilati).

        Se sidebar_params è fornito (da _extract_sidebar_params), costruisce i
        suffissi ~artXxx corretti — inclusi bis/ter/quater — usando
        _art_suffix_from_params(). Altrimenti itera sequenzialmente ~art1, ~art2, …

        start_position: salta i primi (start_position - 1) entry della lista —
        utile per continuare dopo articoli già scaricati via AJAX.

        Yields: (position, article_meta, text)
        """
        referer = f"{_WEB}/uri-res/N2Ls?{act_urn}"
        self._ensure_session(referer)

        # Costruisce la lista di suffissi da scaricare
        if sidebar_params:
            suffixes = [_art_suffix_from_params(p) for p in sidebar_params]
        else:
            suffixes = [f"art{i}" for i in range(1, max_articles + 1)]

        consecutive_miss = 0
        position         = 0

        for idx, suffix in enumerate(suffixes):
            if idx + 1 < start_position:
                continue

            url = f"{_WEB}/uri-res/N2Ls?{act_urn}~{suffix}"

            try:
                r = self._client.get(
                    url,
                    headers={"Accept": "text/html,application/xhtml+xml,*/*"},
                    follow_redirects=True,
                )
            except Exception as e:
                print(f"  [WARN] n2ls {suffix}: {e}")
                consecutive_miss += 1
                if consecutive_miss >= max_consecutive_miss:
                    break
                time.sleep(self._delay)
                continue

            if r.status_code == 404:
                consecutive_miss += 1
                if consecutive_miss >= max_consecutive_miss:
                    break
                time.sleep(self._delay)
                continue

            if r.status_code != 200:
                print(f"  [WARN] n2ls {suffix}: HTTP {r.status_code}")
                time.sleep(self._delay)
                continue

            consecutive_miss = 0

            text, article_meta = self._parse_n2ls_page(r.text)
            if not text.strip():
                time.sleep(self._delay)
                continue

            position += 1
            yield position, article_meta, text
            time.sleep(self._delay)

    # ── public streaming API ──────────────────────────────────────────────────

    def stream_articles(
        self,
        codice_key: str,
        skip_positions: Optional[set[int]] = None,
    ) -> Iterator[tuple[int, dict, str]]:
        """
        Scarica tutti gli articoli di un codice maggiore via chain-navigation.

        Parametri:
          codice_key     – chiave in CODICI_WEB ("cc", "cp", "cpc", "cpp")
          skip_positions – set di posizioni (1-based) già salvate, da saltare

        Yields: (position, article_meta, text)
          position     – posizione sequenziale nella chain (1 = primo articolo)
          article_meta – dict con articolo_num, titolo_articolo,
                         data_inizio_vigenza, descrizione, progressivo
          text         – testo pulito
        """
        info = CODICI_WEB.get(codice_key)
        if not info:
            raise ValueError(f"Codice '{codice_key}' non noto. Disponibili: {list(CODICI_WEB)}")

        yield from self.stream_articles_from_params(
            act_urn   = info["act_urn"],
            codice_id = info["codiceRedaz"],
            data_gu   = info["dataGU"],
            skip_positions = skip_positions,
        )

    def stream_articles_from_params(
        self,
        act_urn:   str,
        codice_id: str,
        data_gu:   str,
        skip_positions: Optional[set[int]] = None,
    ) -> Iterator[tuple[int, dict, str]]:
        """
        Versione low-level: parametri espliciti invece di codice_key.

        act_urn   – URN NIR dell'atto (e.g. "urn:nir:stato:regio.decreto:1942-03-16;262")
        codice_id – codiceRedazionale (e.g. "042U0262")
        data_gu   – data GU in formato YYYY-MM-DD (e.g. "1942-04-04")
        """
        referer = f"{_WEB}/uri-res/N2Ls?{act_urn}"
        self._ensure_session(referer)

        # Carica la pagina N2Ls; ne estraiamo tutta la catena dalla sidebar
        r_page = self._client.get(referer, headers={"Accept": "text/html,*/*"})
        sidebar_chain = self._extract_sidebar_params(r_page.text)

        skip_positions = skip_positions or set()

        if sidebar_chain:
            # FAST PATH: sidebar contiene l'intera catena → possiamo iniziare
            # direttamente dalla prima posizione non ancora salvata.
            start_pos = 1
            if skip_positions:
                # Trova la prima lacuna (posizione non in skip)
                for pos in range(1, len(sidebar_chain) + 1):
                    if pos not in skip_positions:
                        start_pos = pos
                        break
                else:
                    # Tutto già salvato
                    return

            # Naviga con chain-following a partire da start_pos
            # Le posizioni 1..start_pos-1 vengono saltate senza HTTP call
            position = start_pos - 1
            # Inizia dalla posizione target direttamente dalla sidebar
            # Nota: sidebar_chain[i] = params per posizione i+1
            if start_pos - 1 < len(sidebar_chain):
                current_params: Optional[dict] = sidebar_chain[start_pos - 1]
            else:
                current_params = None
        else:
            # FALLBACK: sidebar non disponibile → chain-navigation classica
            try:
                current_params = self._extract_seed_params(r_page.text)
            except ValueError as e:
                print(f"  [WARN] {act_urn}: {e}")
                return
            position = 0

        consecutive_ajax_5xx = 0  # Conta 500/503 consecutivi → trigger fallback N2Ls

        while current_params:
            position += 1

            if position in skip_positions:
                # Non dovrebbe accadere nel fast path, ma per sicurezza
                position_in_sidebar = position - 1
                if sidebar_chain and position_in_sidebar < len(sidebar_chain):
                    current_params = sidebar_chain[position_in_sidebar]
                else:
                    try:
                        xml_text = self._fetch_article(current_params, referer)
                        _, _, next_params = self._parse_article_response(xml_text)
                        current_params = next_params
                        time.sleep(self._delay * 0.2)
                    except Exception as e:
                        print(f"  [WARN] pos {position} (skip): {e}")
                        break
                continue

            try:
                xml_text = self._fetch_article(current_params, referer)
                consecutive_ajax_5xx = 0  # reset su successo
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500:
                    consecutive_ajax_5xx += 1
                    print(f"  [WARN] pos {position}: {e}")
                    if consecutive_ajax_5xx >= _AJAX_500_FALLBACK_THRESHOLD and sidebar_chain:
                        # Troppi 500 consecutivi → passa al fetch N2Ls per il resto
                        print(
                            f"  [INFO] {consecutive_ajax_5xx} errori AJAX-500 consecutivi — "
                            f"switch a N2Ls fallback dalla posizione {position}"
                        )
                        remaining = sidebar_chain[position - 1:]  # da pos corrente in poi
                        for n2ls_pos, n2ls_meta, n2ls_text in self.stream_articles_n2ls(
                            act_urn        = act_urn,
                            sidebar_params = remaining,
                            start_position = 1,
                        ):
                            yield position + n2ls_pos - 1, n2ls_meta, n2ls_text
                        return
                    if sidebar_chain and position < len(sidebar_chain):
                        current_params = sidebar_chain[position]
                        continue
                    break
                else:
                    print(f"  [WARN] pos {position}: {e}")
                    if sidebar_chain and position < len(sidebar_chain):
                        current_params = sidebar_chain[position]
                        continue
                    break
            except Exception as e:
                print(f"  [WARN] pos {position}: {e}")
                consecutive_ajax_5xx += 1
                if consecutive_ajax_5xx >= _AJAX_500_FALLBACK_THRESHOLD and sidebar_chain:
                    print(
                        f"  [INFO] {consecutive_ajax_5xx} errori consecutivi — "
                        f"switch a N2Ls fallback dalla posizione {position}"
                    )
                    remaining = sidebar_chain[position - 1:]
                    for n2ls_pos, n2ls_meta, n2ls_text in self.stream_articles_n2ls(
                        act_urn        = act_urn,
                        sidebar_params = remaining,
                        start_position = 1,
                    ):
                        yield position + n2ls_pos - 1, n2ls_meta, n2ls_text
                    return
                if sidebar_chain and position < len(sidebar_chain):
                    current_params = sidebar_chain[position]
                    continue
                break

            text, article_meta, next_params = self._parse_article_response(xml_text)

            if text:
                yield position, article_meta, text

            # Per la navigazione, usa la chain-following (next_params dal response)
            # che è più affidabile della sidebar per gestire variazioni di versione.
            if next_params is not None:
                current_params = next_params
            elif sidebar_chain and position < len(sidebar_chain):
                # next_params assente ma sidebar ha altri articoli: continua da sidebar
                current_params = sidebar_chain[position]  # indice base-0 = posizione+1
            else:
                current_params = None

            time.sleep(self._delay)
