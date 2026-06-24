"""
Correzione del numero d'articolo nell'URN Normattiva.

Causa nota (vedi LegalAgentLab src/connectors/normattiva.py, stream_articles):
lo scraper costruisce l'URN con un contatore sequenziale di richieste
(~art1, ~art2, ... ~artN) e non verifica che il contenuto restituito
dall'API Normattiva corrisponda davvero al numero richiesto. Per atti con
articoli bis/ter/quater o abrogati, l'API Normattiva può servire una pagina
diversa da quella richiesta (es. l'ultimo articolo navigato in sessione)
senza errore — il contatore sequenziale diverge dal vero numero d'articolo.

Verificato su legal_lab.normattiva_docs (sessione 2026-06-22): 6.521/167.027
chunk con mismatch URN↔contenuto, concentrati al 99,9%/99,7% in Codice Civile,
Codice Procedura Civile, Codice Penale e Codice Procedura Penale (DPR 447/1988).

Il campo `articolo_num` è invece corretto: estratto direttamente dall'HTML
della pagina ricevuta (non dal contatore del loop), quindi è la fonte di
verità per ricostruire l'URN canonico.

CAVEAT — numerazione che riparte da 1 per sezione: in atti come il Codice
Civile, lo stesso `articolo_num` (es. "Art. 1") può comparire fino a 3 volte
nello stesso decreto — articolo del decreto stesso, articolo delle
"disposizioni sulla legge in generale", articolo del corpo del codice —
perché ciascuna sezione ha la propria numerazione indipendente. Correggere
ciecamente per numero da solo farebbe collidere articoli realmente distinti
sullo stesso URN. Verificato: 119 gruppi/366 documenti su legal_lab
(sessione 2026-06-22). Questa funzione NON risolve l'ambiguità di sezione —
il chiamante deve individuare ed escludere i casi di collisione (vedi
scripts/fix_normattiva_urn_mismatch.py, che calcola i gruppi target prima di
applicare la correzione e salta quelli con più di un URN sorgente).
"""
from __future__ import annotations

import re

# Suffisso URN dopo "~art": numero + eventuale lettera (bis/ter/quater/...)
_URN_ART_RE = re.compile(r"^(.*~art)(\d+)([a-z\-]*)$", re.IGNORECASE)

# "Art. 321" | "Art. 2645-bis" | "Art. 2645 bis." | "art.321." → numero + suffisso lettera
_ARTICOLO_NUM_RE = re.compile(
    r"art\.?\s*(\d+)\s*[\-\s]?\s*(bis|ter|quater|quinquies|sexies|septies|octies)?",
    re.IGNORECASE,
)


def _normalize_letter_suffix(raw: str | None) -> str:
    if not raw:
        return ""
    return raw.strip().lower()


def correct_article_urn(urn: str, articolo_num: str) -> str:
    """
    Ricostruisce l'URN usando il numero reale d'articolo (da `articolo_num`,
    estratto dall'HTML) al posto del contatore sequenziale dello scraper.

    Ritorna l'URN originale invariato se:
      - non è un URN di articolo (niente suffisso "~artN")
      - `articolo_num` non è parsabile (nessun numero estratto)
      - il numero reale coincide già con quello nell'URN (no-op sicuro:
        la stragrande maggioranza degli articoli NON è affetta dal bug)

    Esempio del caso reale che ha innescato questa fix:
      urn="urn:nir:...;447~art380", articolo_num="Art. 321"
      → "urn:nir:...;447~art321"
    """
    m_urn = _URN_ART_RE.match(urn)
    if not m_urn:
        return urn

    prefix, urn_num, urn_suffix = m_urn.groups()

    m_art = _ARTICOLO_NUM_RE.search(articolo_num or "")
    if not m_art:
        return urn

    real_num, real_suffix_raw = m_art.groups()
    real_suffix = _normalize_letter_suffix(real_suffix_raw)

    if real_num == urn_num and real_suffix == _normalize_letter_suffix(urn_suffix):
        return urn

    return f"{prefix}{real_num}{real_suffix}"
