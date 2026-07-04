"""
Parser TFUE (Trattato sul Funzionamento dell'Unione Europea) — versione
consolidata IT da EUR-Lex (CELEX 02016E/TXT).

Estrae la gerarchia Parte/Titolo/Capo/Sezione/Articolo dal testo visibile
del documento (HTML salvato localmente — EUR-Lex blocca il fetch
automatico via WAF, vedi docs/superpowers/specs) e produce una lista di
TfueArticle, poi adattati in TfueDocAdapter per la creazione dei Chunk.

Si ferma al primo Protocollo/Allegato/Dichiarazione: quelli non fanno
parte dell'articolato del Trattato e possono riusare la numerazione
"Articolo N" da 1, quindi vanno esclusi per non corrompere il parsing.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup

CORPUS_TFUE = "normattiva"
FONTE_TFUE = "trattato_ue"
SOURCE_TFUE = "eurlex_tfue"
SETTORE_TFUE = ["unione_europea"]

#  Case-sensitive apposta: le intestazioni ufficiali EUR-Lex sono sempre in
#  MAIUSCOLO/Title-Case ("Articolo 101", "PARTE PRIMA", "Sezione 1"). Il
#  corpo del testo cita spesso gli stessi termini in minuscolo dentro frasi
#  o elenchi puntati (es. articolo 353 TFUE: "articolo 311, terzo e quarto
#  comma, — articolo 312, paragrafo 2 ..."): con IGNORECASE quelle righe
#  venivano scambiate per nuove intestazioni di articolo, generando
#  duplicati con testo tronco.
_PARTE_RE = re.compile(r"^PARTE\s+(PRIMA|SECONDA|TERZA|QUARTA|QUINTA|SESTA|SETTIMA)\b")
_TITOLO_RE = re.compile(r"^TITOLO\s+([IVXLCDM]+)\b")
_CAPO_RE = re.compile(r"^CAPO\s+(\d+|[IVXLCDM]+)\b")
_SEZIONE_RE = re.compile(r"^Sezione\s+(\d+)\b")
_ARTICOLO_RE = re.compile(r"^Articolo\s+(\d+\s*(?:bis|ter|quater)?)\b")
_STOP_RE = re.compile(r"^(PROTOCOLLO|ALLEGATO|DICHIARAZIONE)\b")


@dataclass
class TfueArticle:
    numero: str                       # es. "101"
    testo: str
    titolo_articolo: str = ""         # rubrica, quasi sempre assente nel TFUE
    parte: str = ""                   # es. "PARTE TERZA"
    titolo_sezione: str = ""          # es. "TITOLO VII" (evita collisione col campo 'titolo' del chunk)
    capo: str = ""                    # es. "CAPO 1"
    sezione: str = ""                 # es. "Sezione 1"

    @property
    def gerarchia(self) -> str:
        parts = [p for p in (self.parte, self.titolo_sezione, self.capo, self.sezione) if p]
        return " — ".join(parts)


def html_to_lines(html: str) -> list[str]:
    """Estrae le righe di testo visibile da un file HTML EUR-Lex."""
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n")
    lines = [re.sub(r"\s+", " ", ln).strip() for ln in text.splitlines()]
    return [ln for ln in lines if ln]


def _body_start_index(lines: list[str]) -> int:
    """
    Individua l'inizio del corpo del trattato, saltando il frontespizio
    EUR-Lex (titolo, avvertenza, tabella "Contiene: Gazzetta ufficiale ..."
    con la cronologia delle modifiche). Quella tabella cita per esteso i
    titoli dei protocolli/decisioni di modifica — incluse righe che iniziano
    per "PROTOCOLLO" — ben prima dell'articolato vero, e farebbero scattare
    _STOP_RE troppo presto se non venissero saltate.
    """
    for i, line in enumerate(lines):
        if _PARTE_RE.match(line):
            return i
    for i, line in enumerate(lines):
        if _ARTICOLO_RE.match(line):
            return i
    return 0


def parse_tfue_lines(lines: list[str]) -> list[TfueArticle]:
    """
    Parsa la gerarchia Parte/Titolo/Capo/Sezione/Articolo da righe di testo
    già normalizzate (una unità logica per riga).
    """
    lines = lines[_body_start_index(lines):]
    articles: list[TfueArticle] = []

    parte = titolo_sezione = capo = sezione = ""
    current: Optional[TfueArticle] = None
    body: list[str] = []

    def _flush() -> None:
        nonlocal current, body
        if current is not None:
            current.testo = " ".join(body).strip()
            if current.testo:
                articles.append(current)
        current = None
        body = []

    for line in lines:
        if _STOP_RE.match(line):
            break

        m = _PARTE_RE.match(line)
        if m:
            _flush()
            parte = line
            titolo_sezione = capo = sezione = ""
            continue

        m = _TITOLO_RE.match(line)
        if m:
            _flush()
            titolo_sezione = line
            capo = sezione = ""
            continue

        m = _CAPO_RE.match(line)
        if m:
            _flush()
            capo = line
            sezione = ""
            continue

        m = _SEZIONE_RE.match(line)
        if m:
            _flush()
            sezione = line
            continue

        m = _ARTICOLO_RE.match(line)
        if m:
            _flush()
            current = TfueArticle(
                numero=m.group(1).strip(),
                testo="",
                parte=parte,
                titolo_sezione=titolo_sezione,
                capo=capo,
                sezione=sezione,
            )
            continue

        if current is not None:
            body.append(line)

    _flush()
    return articles


def parse_tfue_html(html: str) -> list[TfueArticle]:
    return parse_tfue_lines(html_to_lines(html))


# ---------------------------------------------------------------------------
# Adapter: TfueArticle → campi base per Chunk (simmetrico a NormattivaDocAdapter)
# ---------------------------------------------------------------------------

@dataclass
class TfueDocAdapter:
    doc_id: str
    source_id: str
    text: str
    titolo: str
    articolo_num: str
    titolo_articolo: str = ""

    @classmethod
    def from_article(cls, article: TfueArticle) -> "TfueDocAdapter":
        source_id = f"urn:eu:tfue:art{article.numero.replace(' ', '')}"
        titolo = f"TFUE — {article.gerarchia}" if article.gerarchia else "TFUE"
        return cls(
            doc_id=source_id,
            source_id=source_id,
            text=article.testo,
            titolo=titolo,
            articolo_num=f"Art. {article.numero} TFUE",
            titolo_articolo=article.titolo_articolo,
        )

    def to_chunk_base(self, workspace: str) -> dict:
        return {
            "document_id": self.doc_id,
            "source_id": self.source_id,
            "workspace": workspace,
            "doc_type": "TRATTATO",
            "source": SOURCE_TFUE,
            "corpus": CORPUS_TFUE,
            "fonte": FONTE_TFUE,
            "testo_tipo": "normativo",
            "titolo": self.titolo,
            "titolo_articolo": self.titolo_articolo or None,
            "articolo_num": self.articolo_num,
            "settore": SETTORE_TFUE,
            "valid_from": None,
            "valid_to": None,
        }
