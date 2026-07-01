"""
Normalizzazione whitespace/tipografia per il testo dei chunk in ingestione.

Vedi: docs/superpowers/specs/2026-06-28-chunk-text-normalizer-design.md

Il testo estratto da PDF (normattiva, giurisprudenza, dottrina) contiene newline
che frammentano le frasi a metà, spazi multipli e punteggiatura tipografica
(apostrofi/virgolette curve). normalize_text() pulisce questo rumore prima della
tokenizzazione usata per determinare i confini dei chunk.
"""
from __future__ import annotations

import re

_WHITESPACE_RE = re.compile(r"\s+")
_SPACE_BEFORE_PUNCT_RE = re.compile(r"\s+([;:,.!?])")

_TYPOGRAPHIC_MAP = {
    "’": "'",  # '
    "‘": "'",  # '
    "“": '"',  # "
    "”": '"',  # "
}


def normalize_text(text: str) -> str:
    """
    Collassa whitespace/newline interni, rimuove spazi prima della punteggiatura
    e normalizza apostrofi/virgolette tipografiche. Idempotente.
    """
    if not text:
        return text

    normalized = _WHITESPACE_RE.sub(" ", text)
    normalized = _SPACE_BEFORE_PUNCT_RE.sub(r"\1", normalized)
    for curly, straight in _TYPOGRAPHIC_MAP.items():
        normalized = normalized.replace(curly, straight)
    return normalized.strip()
