"""
ReferenceExtractor — estrae rimandi inter-articolo da testo normativo italiano.

Dato il testo grezzo di un articolo, restituisce una lista di ReferenceMatch
(articolo_num_target, edge_type, context).

Tipi di arco riconosciuti:
  ABROGA   — "abrogato/a dall'art. X"
  MODIFICA — "modificato/a dall'art. X"
  RINVIA   — "ai sensi dell'art. X", "di cui all'art. X", "art. X" generico

Limitazioni:
  - Lavora su articolo_num (numero articolo), non su URN completo.
    La risoluzione a source_id avviene nel LegalGraphBuilder.
  - Può produrre falsi positivi su "articolo di giornale", "art." abbreviato
    in contesti non normativi. Il LegalGraphBuilder filtra i num non risolvibili.
  - Il tipo di arco è inferito dal contesto locale (±80 caratteri):
    non è accurato al 100%, ma coprela grande maggioranza dei casi reali.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator


# ---------------------------------------------------------------------------
# Tipi
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ReferenceMatch:
    articolo_num: str   # numero articolo target, es. "1218", "2-bis"
    edge_type: str      # "RINVIA" | "ABROGA" | "MODIFICA"
    context: str        # frammento testuale che ha originato il match (debug)


# ---------------------------------------------------------------------------
# Pattern — ordine di priorità (più specifici prima)
# ---------------------------------------------------------------------------

# Apostrofo curvo (') e dritto (') sono entrambi ammessi
_APO = r"['’]"

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # ABROGA — "abrogato/a dall'art. X"
    (
        re.compile(
            r"abrogat[oa]\s+dall" + _APO + r"art\.?\s*(\d+[a-z\-]*(?:\s*-\s*(?:bis|ter|quater|quinquies))?)",
            re.IGNORECASE,
        ),
        "ABROGA",
    ),
    # MODIFICA — "modificato/a dall'art. X" o "come modificato dall'art. X"
    (
        re.compile(
            r"modificat[oa]\s+dall" + _APO + r"art\.?\s*(\d+[a-z\-]*(?:\s*-\s*(?:bis|ter|quater|quinquies))?)",
            re.IGNORECASE,
        ),
        "MODIFICA",
    ),
    # RINVIA esplicito — formule standard di rinvio
    (
        re.compile(
            r"(?:"
            r"ai\s+sensi\s+dell" + _APO + r"art"
            r"|di\s+cui\s+all" + _APO + r"art"
            r"|previsto\s+dall" + _APO + r"art"
            r"|fermo\s+restando\s+(?:quanto\s+)?(?:disposto\s+)?dall" + _APO + r"art"
            r"|(?:come\s+)?(?:disciplinato|regolato|stabilito)\s+dall" + _APO + r"art"
            r")"
            r"\.?\s*(\d+[a-z\-]*(?:\s*-\s*(?:bis|ter|quater|quinquies))?)",
            re.IGNORECASE,
        ),
        "RINVIA",
    ),
    # RINVIA generico — "art. X" fallback
    # I match sovrapposti con ABROGA/MODIFICA vengono già eliminati da _iter_matches
    # tramite il controllo posizionale (last_end), quindi nessun lookbehind necessario.
    (
        re.compile(
            r"\bart\.?\s*(\d+[a-z\-]*(?:\s*-\s*(?:bis|ter|quater|quinquies))?)\b",
            re.IGNORECASE,
        ),
        "RINVIA",
    ),
]

# Parole che indicano che "art." si riferisce a qualcosa di non normativo
_FALSE_POSITIVE_CONTEXT = re.compile(
    r"(?:articolo\s+di\s+|art(?:icolo)?\s+(?:giornale|stampa|pubblicazione|rivista))",
    re.IGNORECASE,
)

# Contesto locale da estrarre attorno al match (caratteri prima e dopo)
_CONTEXT_WINDOW = 60


# ---------------------------------------------------------------------------
# ReferenceExtractor
# ---------------------------------------------------------------------------

class ReferenceExtractor:
    """
    Estrae riferimenti normativi da testo italiano.

    Utilizzo:
        extractor = ReferenceExtractor()
        refs = extractor.extract(text, fonte="codice_civile")

    Il parametro `fonte` è opzionale: se fornito viene usato per filtrare
    i rimandi interni allo stesso provvedimento (non li scarta, li marca).
    """

    def extract(
        self,
        text: str,
        fonte: str = "",
    ) -> list[ReferenceMatch]:
        """
        Estrae tutti i riferimenti normativi dal testo.

        Args:
            text:  testo grezzo dell'articolo
            fonte: fonte del documento corrente (per il contesto, non filtra)

        Returns:
            Lista di ReferenceMatch deduplicata per (articolo_num, edge_type).
            Un articolo può essere referenziato più volte con tipo diverso
            (es. RINVIA e ABROGA) — in tal caso entrambi i match sono restituiti.
        """
        seen: set[tuple[str, str]] = set()
        results: list[ReferenceMatch] = []

        for match, edge_type in self._iter_matches(text):
            art_num = self._normalize_num(match.group(1))
            if not art_num:
                continue

            # Estrai contesto locale
            start = max(0, match.start() - _CONTEXT_WINDOW)
            end = min(len(text), match.end() + _CONTEXT_WINDOW)
            ctx = text[start:end].strip()

            # Salta falsi positivi ovvi
            if _FALSE_POSITIVE_CONTEXT.search(ctx):
                continue

            key = (art_num, edge_type)
            if key not in seen:
                seen.add(key)
                results.append(ReferenceMatch(
                    articolo_num=art_num,
                    edge_type=edge_type,
                    context=ctx,
                ))

        return results

    # ------------------------------------------------------------------
    # Privati
    # ------------------------------------------------------------------

    @staticmethod
    def _iter_matches(text: str) -> Iterator[tuple[re.Match[str], str]]:
        """Itera su tutti i match in ordine di posizione, dal pattern più specifico."""
        # Raccoglie match da tutti i pattern con relativo tipo
        all_matches: list[tuple[int, re.Match[str], str]] = []
        for pattern, edge_type in _PATTERNS:
            for m in pattern.finditer(text):
                all_matches.append((m.start(), m, edge_type))

        # Ordina per posizione; a parità di posizione il pattern più specifico
        # è già in testa perché _PATTERNS è ordinato dal più specifico
        all_matches.sort(key=lambda x: x[0])

        # Emette solo il match a priorità più alta per ogni posizione sovrapposta
        last_end = -1
        for pos, match, edge_type in all_matches:
            if pos >= last_end:
                yield match, edge_type
                last_end = match.end()

    @staticmethod
    def _normalize_num(raw: str) -> str:
        """
        Normalizza il numero articolo estratto dalla regex.

        Esempi:
          "1218"     → "1218"
          "2 -bis"   → "2-bis"
          "1  "      → "1"
          ""         → ""  (filtrato a monte)
        """
        return re.sub(r"\s*-\s*", "-", raw.strip()).lower()
