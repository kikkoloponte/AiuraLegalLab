"""
AKN (Akoma Ntoso) Parser per Normattiva — estrae vigenza e abrogazioni
dall'XML AKN dei provvedimenti italiani.

Normattiva pubblica i testi in formato Akoma Ntoso 2.0/3.0.
Questo modulo legge la struttura <meta> per estrarre:
  - Data di inizio vigenza   (<FRBRdate name="generation">)
  - Data di fine vigenza     (<eventRef type="repeal"> o <eventRef type="end">)
  - Modificazioni            (<eventRef type="amendment">)
  - Status incostituzionale  (<eventRef type="annulment">)
  - Articoli con vigenza propria (<article status="...">)

Output principale: VigenzaInfo — dataclass con i campi
  valid_from, valid_to, is_abrogated, status, amendments

I campi valid_from / valid_to usano il formato yyyymmdd, coerente
con il resto del sistema (NormattivaDocAdapter, GraphRetriever).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional
from xml.etree import ElementTree as ET

from loguru import logger


# Namespace Akoma Ntoso (le due versioni principali su Normattiva)
_AKN_NS_2 = "http://www.akomantoso.org/2.0"
_AKN_NS_3 = "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"

# Status rilevanti per l'incostituzionalità
_UNCONSTITUTIONAL_TYPES = frozenset({"annulment", "annulled"})


# ---------------------------------------------------------------------------
# Output dataclass
# ---------------------------------------------------------------------------

@dataclass
class VigenzaInfo:
    """
    Informazioni di vigenza estratte dall'XML AKN.

    Campi date nel formato yyyymmdd (es. "20230101"), coerenti con
    NormattivaDocAdapter.valid_from / valid_to.
    Valore sentinella "99999999" = vigente (nessuna data di fine nota).
    """
    valid_from: Optional[str] = None            # data inizio vigenza (yyyymmdd)
    valid_to: Optional[str] = None              # data fine vigenza   (yyyymmdd)
    is_abrogated: bool = False                  # True se abrogato esplicitamente
    is_unconstitutional: bool = False           # True se dichiarato incostituzionale
    status: str = "vigente"                     # "vigente" | "abrogato" | "incostituzionale"
    abrogated_by: Optional[str] = None         # URN della norma che ha abrogato
    amendments: list[dict] = field(default_factory=list)  # [{date, source}]


@dataclass
class ArticleVigenza:
    """Vigenza di un singolo articolo."""
    article_id: str
    article_num: str
    vigenza: VigenzaInfo


# ---------------------------------------------------------------------------
# AKNParser
# ---------------------------------------------------------------------------

class AKNParser:
    """
    Estrae informazioni di vigenza da XML Akoma Ntoso di Normattiva.

    Utilizzo:
        parser = AKNParser()

        # Vigenza dell'intero provvedimento
        info = parser.parse_vigenza(xml_string)

        # Vigenza dei singoli articoli
        articles = parser.parse_articles(xml_string)
    """

    # ------------------------------------------------------------------
    # Rilevamento namespace
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_namespace(xml_content: str) -> str:
        """Rileva il namespace AKN dalla dichiarazione XML."""
        if _AKN_NS_3 in xml_content[:500]:
            return _AKN_NS_3
        if _AKN_NS_2 in xml_content[:500]:
            return _AKN_NS_2
        # Prova anche senza namespace (alcuni documenti Normattiva non lo dichiarano)
        return ""

    @staticmethod
    def _ns(tag: str, ns: str) -> str:
        """Costruisce il tag qualificato con namespace."""
        return f"{{{ns}}}{tag}" if ns else tag

    # ------------------------------------------------------------------
    # Parsing date AKN
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_akn_date(date_str: str) -> Optional[str]:
        """
        Converte una data AKN (ISO 8601: YYYY-MM-DD) nel formato yyyymmdd.
        Ritorna None se la stringa non è una data valida.

        Esempi:
            "2023-01-15" → "20230115"
            "2023"       → "20230101"  (anno senza mese/giorno → 1 gennaio)
            ""           → None
        """
        if not date_str or not date_str.strip():
            return None
        s = date_str.strip()
        # ISO completo: YYYY-MM-DD
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
        if m:
            return m.group(1) + m.group(2) + m.group(3)
        # Solo anno: YYYY
        m = re.match(r"^(\d{4})$", s)
        if m:
            return m.group(1) + "0101"
        return None

    # ------------------------------------------------------------------
    # parse_vigenza() — vigenza dell'intero provvedimento
    # ------------------------------------------------------------------

    def parse_vigenza(self, xml_content: str) -> VigenzaInfo:
        """
        Estrae la vigenza dell'intero provvedimento dall'XML AKN.

        Args:
            xml_content: stringa XML del documento Normattiva

        Returns:
            VigenzaInfo con valid_from, valid_to, status, ecc.
        """
        if not xml_content or not xml_content.strip():
            return VigenzaInfo()

        try:
            root = ET.fromstring(xml_content.encode("utf-8"))
        except ET.ParseError as exc:
            logger.warning(f"[AKNParser] XML non parsabile: {exc}")
            return VigenzaInfo()

        ns = self._detect_namespace(xml_content)
        return self._extract_vigenza(root, ns)

    def _extract_vigenza(self, root: ET.Element, ns: str) -> VigenzaInfo:
        """Logica di estrazione vigenza dal tree XML."""
        info = VigenzaInfo()

        # ── 1. Data generazione (FRBRdate[@name="generation"]) ──────────
        # Cerca in FRBRWork e FRBRExpression
        for path in [
            f".//{self._ns('FRBRWork', ns)}/{self._ns('FRBRdate', ns)}",
            f".//{self._ns('FRBRExpression', ns)}/{self._ns('FRBRdate', ns)}",
        ]:
            for elem in root.findall(path):
                if elem.get("name") in ("generation", "produzione"):
                    d = self._parse_akn_date(elem.get("date", ""))
                    if d and not info.valid_from:
                        info.valid_from = d

        # ── 2. Lifecycle events ──────────────────────────────────────────
        amendments = []
        for event in root.findall(f".//{self._ns('eventRef', ns)}"):
            evt_type  = (event.get("type") or "").lower()
            evt_date  = self._parse_akn_date(event.get("date", ""))
            evt_src   = event.get("source", "")
            evt_refers = event.get("refers", "")

            if evt_type in ("repeal", "abrogation", "cessation", "end"):
                info.is_abrogated = True
                if evt_date:
                    info.valid_to = evt_date
                if evt_refers:
                    info.abrogated_by = evt_refers.lstrip("#")

            elif evt_type in _UNCONSTITUTIONAL_TYPES:
                info.is_unconstitutional = True
                info.is_abrogated = True
                if evt_date:
                    info.valid_to = evt_date

            elif evt_type == "amendment":
                if evt_date:
                    amendments.append({
                        "date": evt_date,
                        "source": evt_src.lstrip("#"),
                        "refers": evt_refers.lstrip("#"),
                    })

        info.amendments = amendments

        # ── 3. Status complessivo ────────────────────────────────────────
        if info.is_unconstitutional:
            info.status = "incostituzionale"
        elif info.is_abrogated:
            info.status = "abrogato"
        else:
            info.status = "vigente"
            info.valid_to = info.valid_to or "99999999"

        return info

    # ------------------------------------------------------------------
    # parse_articles() — vigenza per articolo
    # ------------------------------------------------------------------

    def parse_articles(self, xml_content: str) -> list[ArticleVigenza]:
        """
        Estrae gli articoli con la loro vigenza dall'XML AKN.

        Per ogni <article> nel body:
          - Legge il numero (<num> o attributo num="...")
          - Verifica status="abrogato" / "incostituzionale" direttamente sull'elemento
          - Cerca <FRBRdate> o <eventRef> nell'<intro> dell'articolo (se presenti)

        Args:
            xml_content: stringa XML del documento Normattiva

        Returns:
            Lista di ArticleVigenza, uno per articolo trovato.
        """
        if not xml_content or not xml_content.strip():
            return []

        try:
            root = ET.fromstring(xml_content.encode("utf-8"))
        except ET.ParseError:
            return []

        ns = self._detect_namespace(xml_content)

        # Vigenza di default per il provvedimento (ereditata dagli articoli)
        doc_vigenza = self._extract_vigenza(root, ns)

        articles: list[ArticleVigenza] = []
        for art_elem in root.findall(f".//{self._ns('article', ns)}"):
            art_id = art_elem.get("eId") or art_elem.get("id", "")

            # Numero articolo da <num> o da attributo
            num_elem = art_elem.find(self._ns("num", ns))
            art_num = ""
            if num_elem is not None and num_elem.text:
                art_num = num_elem.text.strip()
            else:
                art_num = art_elem.get("num", art_id)

            # Vigenza articolo: eredita dal documento, poi sovrascrive con status inline
            art_vigenza = VigenzaInfo(
                valid_from=doc_vigenza.valid_from,
                valid_to=doc_vigenza.valid_to,
                is_abrogated=doc_vigenza.is_abrogated,
                is_unconstitutional=doc_vigenza.is_unconstitutional,
                status=doc_vigenza.status,
                abrogated_by=doc_vigenza.abrogated_by,
            )

            # Sovrascrittura per status inline sull'articolo
            inline_status = (art_elem.get("status") or "").lower()
            if inline_status in ("abrogato", "abrogated", "repealed"):
                art_vigenza.is_abrogated = True
                art_vigenza.status = "abrogato"
            elif inline_status in _UNCONSTITUTIONAL_TYPES or "incostituzionale" in inline_status:
                art_vigenza.is_unconstitutional = True
                art_vigenza.is_abrogated = True
                art_vigenza.status = "incostituzionale"

            articles.append(ArticleVigenza(
                article_id=art_id,
                article_num=art_num,
                vigenza=art_vigenza,
            ))

        return articles

    # ------------------------------------------------------------------
    # Integrazione con NormattivaDocAdapter
    # ------------------------------------------------------------------

    def enrich_doc(self, doc: dict, xml_content: str) -> dict:
        """
        Arricchisce un documento MongoDB con i dati di vigenza estratti dall'AKN.

        Aggiorna/sovrascrive i campi:
          data_inizio_vigenza, data_fine_vigenza, vigenza_status, amendments

        Args:
            doc:         dizionario documento MongoDB (viene modificato in-place)
            xml_content: XML AKN del provvedimento

        Returns:
            Il dizionario doc aggiornato (per comodità).
        """
        info = self.parse_vigenza(xml_content)

        if info.valid_from:
            doc["data_inizio_vigenza"] = info.valid_from
        if info.valid_to:
            doc["data_fine_vigenza"] = info.valid_to
        doc["vigenza_status"]   = info.status
        doc["is_abrogated"]     = info.is_abrogated
        doc["is_unconstitutional"] = info.is_unconstitutional
        if info.abrogated_by:
            doc["abrogated_by"] = info.abrogated_by
        if info.amendments:
            doc["amendments"] = info.amendments

        return doc
