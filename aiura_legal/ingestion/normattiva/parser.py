"""
AiUra LegalLab — Normattiva parser e classificatore fonte.

fonte_from_doc(doc)       → classifica un documento Normattiva nella tassonomia
                            corpus/fonte usata nei Chunk per il filtraggio subset.
settore_from_doc(doc)     → classifica il settore giuridico (lista) del documento.
NormattivaDocAdapter      → converte un documento aiura_legal.normattiva_docs
                            nei campi necessari per la creazione di Chunk tipizzati.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Tassonomia fonte (SPEC §16.4)
# ---------------------------------------------------------------------------

#: Mapping frammento act_urn → fonte (priorità assoluta: codici maggiori)
_CODICI_FRAGMENTS: list[tuple[str, str]] = [
    ("regio.decreto:1942-03-16;262",                                      "codice_civile"),
    ("regio.decreto:1930-10-19;1398",                                     "codice_penale"),
    ("regio.decreto:1940-10-28;1443",                                     "codice_proc_civile"),
    ("decreto.del.presidente.della.repubblica:1988-09-22;447",            "codice_proc_penale"),
]

#: Mapping tipo_provvedimento (uppercase, match esatto) → fonte
_TIPO_EXACT: dict[str, str] = {
    "LEGGE COSTITUZIONALE":                        "legge_costituzionale",
    "LEGGE":                                       "legge",
    "DECRETO LEGISLATIVO":                         "dlgs",
    "DECRETO-LEGGE":                               "dl",
    "REGIO DECRETO":                               "rd",
    "DECRETO MINISTERIALE":                        "dm",
    "DECRETO DEL PRESIDENTE DELLA REPUBBLICA":     "dpr",
    "DECRETO DEL PRESIDENTE DEL CONSIGLIO DEI MINISTRI": "dpcm",
}

#: Fallback per match parziale (contains)
_TIPO_PARTIAL: list[tuple[str, str]] = [
    ("PRESIDENTE DELLA REPUBBLICA", "dpr"),
    ("CONSIGLIO DEI MINISTRI",      "dpcm"),
    ("MINISTERIALE",                "dm"),
    ("MINISTERO",                   "dm"),
]


# ---------------------------------------------------------------------------
# Tassonomia settore giuridico (Chunk Schema V2)
# ---------------------------------------------------------------------------

#: Mapping fonte → settore (livello 1: codici maggiori, certezza assoluta)
_FONTE_TO_SETTORE: dict[str, list[str]] = {
    "codice_penale":        ["penale"],
    "codice_proc_penale":   ["penale", "processuale"],
    "codice_civile":        ["civile"],
    "codice_proc_civile":   ["civile", "processuale"],
    "legge_costituzionale": ["costituzionale"],
}

#: Keyword nel titolo → settore (livello 2: leggi/dlgs/dl generiche)
#: Ogni tupla: (lista keyword, settore)  — ricerca case-insensitive nel titolo
_TITLE_KEYWORDS_SETTORE: list[tuple[list[str], list[str]]] = [
    (["codice penale", "codice di procedura penale"], ["penale"]),   # sicurezza assoluta
    (["penale", "reato", " pena ", "delitto", "imputab", "antigiurid"], ["penale"]),
    (["lavoro", "lavorator", "previdenz", "pensioni", "sicurezza sul lavoro",
      "infortun sul lavoro", "cassa integr"], ["lavoro"]),
    (["tribut", "fiscal", "impost", " iva ", "irpef", "ires", "accise",
      "agenzie delle entrate", "catasto"], ["amministrativo"]),
    (["appalto", "pubblica amministr", "pubblica amm", "concessione",
      "permesso di costruir", "edilizia", "urbanistic"], ["amministrativo"]),
    (["processo", "procedur", "giurisdiz", "esecuzione forzata",
      "fallimento"], ["processuale"]),
    (["civile", "contratt", "obbligaz", "societ", "commercio",
      "consumator", "privacy", "dati personali"], ["civile"]),
    (["costituzion", "parlamento", "ordinamento republic",
      "regioni", "autonomie"], ["costituzionale"]),
]


def settore_from_doc(doc: dict, fonte: str | None = None) -> list[str]:
    """
    Classifica il settore giuridico di un documento Normattiva.

    Ritorna una lista di valori tra:
    "penale", "civile", "amministrativo", "lavoro",
    "processuale", "costituzionale", "altro"

    Logica a 3 livelli:
      1. fonte già nota → _FONTE_TO_SETTORE (certezza assoluta, codici maggiori)
      2. keyword nel titolo → _TITLE_KEYWORDS_SETTORE (~70% leggi/dlgs)
      3. fallback → ["altro"]

    Args:
        doc:   documento MongoDB (normattiva_docs)
        fonte: risultato di fonte_from_doc(doc) — se None viene ricalcolato
    """
    if fonte is None:
        fonte = fonte_from_doc(doc)

    # Livello 1: fonte nota (codici maggiori)
    if fonte in _FONTE_TO_SETTORE:
        return _FONTE_TO_SETTORE[fonte]

    # Livello 2: keyword nel titolo
    titolo = (doc.get("titolo") or "").lower()
    if titolo:
        for keywords, settore in _TITLE_KEYWORDS_SETTORE:
            if any(kw in titolo for kw in keywords):
                return settore

    # Livello 3: fallback
    return ["altro"]


def fonte_from_doc(doc: dict) -> str:
    """
    Classifica un documento Normattiva nella tassonomia 'fonte'.

    Priorità:
      1. Match su act_urn o urn (identifica i 4 codici maggiori)
      2. Match esatto su tipo_provvedimento normalizzato
      3. Match parziale su tipo_provvedimento (fallback)
      4. "altro"

    Args:
        doc: documento MongoDB (aiura_legal.normattiva_docs o legal_lab.normattiva_docs)

    Returns:
        Stringa fonte: "codice_civile" | "codice_penale" | "codice_proc_civile" |
                       "codice_proc_penale" | "legge_costituzionale" | "legge" |
                       "dlgs" | "dl" | "dpr" | "dpcm" | "rd" | "dm" | "altro"
    """
    # Cerca sia in act_urn che in urn (per supportare entrambi gli schemi)
    urn = (doc.get("act_urn") or doc.get("urn") or "").lower()

    # 1. Codici maggiori: match su frammento URN
    for fragment, fonte in _CODICI_FRAGMENTS:
        if fragment in urn:
            return fonte

    # 2. tipo_provvedimento — match esatto (case-insensitive)
    tipo_raw = (doc.get("tipo_provvedimento") or doc.get("doc_type") or "").strip()
    tipo = tipo_raw.upper()

    if tipo in _TIPO_EXACT:
        return _TIPO_EXACT[tipo]

    # 3. Match parziale
    for fragment, fonte in _TIPO_PARTIAL:
        if fragment in tipo:
            return fonte

    return "altro"


# ---------------------------------------------------------------------------
# Adapter: normattiva_docs dict → Chunk fields
# ---------------------------------------------------------------------------

@dataclass
class NormattivaDocAdapter:
    """
    Adatta un documento aiura_legal.normattiva_docs per la creazione di Chunk.

    Calcola i campi di tipizzazione (corpus, fonte, testo_tipo, settore) e
    normalizza i campi di metadato (source_id, titolo, articolo_num,
    titolo_articolo, valid_from, valid_to).
    """

    doc_id: str             # _id del documento in normattiva_docs (usato come document_id)
    source_id: str          # URN articolo (chiave univoca)
    text: str               # testo normativo
    corpus: str             # sempre "normattiva"
    fonte: str              # calcolato da fonte_from_doc
    testo_tipo: str         # propagato da normattiva_docs.testo_tipo
    titolo: str
    titolo_articolo: str    # es. "Elemento psicologico del reato" — da normattiva_docs.titolo_articolo
    articolo_num: str
    tipo_provvedimento: str
    settore: list[str] = field(default_factory=list)  # calcolato da settore_from_doc
    valid_from: Optional[str] = None  # data_inizio_vigenza (formato yyyymmdd o None)
    valid_to: Optional[str] = None    # data_fine_vigenza   (formato yyyymmdd, "99999999"=vigente, o None)

    @classmethod
    def from_mongo_doc(cls, doc: dict) -> "NormattivaDocAdapter":
        """
        Costruisce un NormattivaDocAdapter da un documento MongoDB.

        Funziona con entrambi gli schemi:
          - aiura_legal.normattiva_docs (ha _id come ObjectId/str)
          - legal_lab.normattiva_docs   (schema identico)
        """
        raw_id = doc.get("_id")
        doc_id = str(raw_id) if raw_id is not None else doc.get("urn", "")
        fonte = fonte_from_doc(doc)

        # NOTA: source_id usa l'urn grezzo, NON corretto qui. La correzione
        # (vedi urn_fix.py) richiede visibilità GLOBALE sull'intera collection
        # per individuare le catene di shift concatenati (es. ~art380→~art321
        # mentre contemporaneamente un altro articolo ha ~art321 come proprio
        # urn sbagliato) — un fix per-documento senza quel contesto rischia di
        # creare nuove collisioni silenziose nell'upsert dei chunk. La
        # correzione va applicata SOLO da scripts/fix_normattiva_urn_mismatch.py,
        # che calcola la mappa sicura una volta per l'intera collection.
        return cls(
            doc_id=doc_id,
            source_id=doc.get("urn", ""),
            text=doc.get("text", ""),
            corpus="normattiva",
            fonte=fonte,
            testo_tipo=doc.get("testo_tipo", "normativo"),
            titolo=doc.get("titolo", ""),
            titolo_articolo=doc.get("titolo_articolo", ""),
            articolo_num=doc.get("articolo_num", ""),
            tipo_provvedimento=doc.get("tipo_provvedimento", ""),
            settore=settore_from_doc(doc, fonte=fonte),
            valid_from=doc.get("data_inizio_vigenza"),
            valid_to=doc.get("data_fine_vigenza"),
        )

    def to_chunk_base(self, workspace: str) -> dict:
        """
        Ritorna i campi base comuni a tutti i chunk generati da questo documento.
        Il chiamante aggiunge chunk_index, text, token_count.
        """
        return {
            "document_id": self.doc_id,
            "source_id": self.source_id,
            "workspace": workspace,
            "doc_type": self.tipo_provvedimento,
            "source": "normattiva_it",
            "corpus": self.corpus,
            "fonte": self.fonte,
            "testo_tipo": self.testo_tipo,
            "titolo": self.titolo,
            "titolo_articolo": self.titolo_articolo or None,
            "articolo_num": self.articolo_num,
            "settore": self.settore,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
        }
