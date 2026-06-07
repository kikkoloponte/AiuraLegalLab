"""
PII Anonymizer per testi legali italiani.
Layer 1: regex (CF, PIVA, IBAN, email, telefono)
Layer 2: spaCy it_core_news_lg (PER, ORG con confidence > 0.80)

CRITICO: NON anonimizza riferimenti normativi/giurisprudenziali.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Optional
from loguru import logger


# ---------------------------------------------------------------------------
# Pattern da NON anonimizzare mai (whitelist normativa)
# ---------------------------------------------------------------------------

_WHITELIST_PATTERNS = [
    # articoli di codice
    r"\bart\.\s*\d+[\w\s,./]*c\.c\.",
    r"\bart\.\s*\d+[\w\s,./]*c\.p\.",
    r"\bart\.\s*\d+[\w\s,./]*c\.p\.c\.",
    # D.Lgs, D.P.R., L., ecc.
    r"\bD\.?\s*Lgs\.?\s*\d+/\d{4}\b",
    r"\bD\.?\s*P\.?\s*R\.?\s*\d+/\d{4}\b",
    r"\bL\.\s*\d+/\d{4}\b",
    # Corti istituzionali
    r"\bCorte\s+di\s+Cassazione\b",
    r"\bCorte\s+Costituzionale\b",
    r"\bCorte\s+d['i]\s+Appello\b",
    r"\bConsiglio\s+di\s+Stato\b",
    r"\bCorte\s+EDU\b",
    r"\bCEDU\b",
    # Cass. Sez. ...
    r"\bCass\.?\s+(?:Sez\.|Plen\.|SS\.?\s*UU\.?)\s*[A-Z]{0,3}\.?\s*n?\.\s*\d+/?\d*",
    # Comuni (es. "Comune di Milano")
    r"\bComune\s+di\s+\w+",
    # Riferimenti GU
    r"\bG\.?\s*U\.?\s*n\.\s*\d+",
]

_WHITELIST_RE = re.compile(
    "|".join(f"(?:{p})" for p in _WHITELIST_PATTERNS),
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Pattern PII da anonimizzare (Layer 1)
# ---------------------------------------------------------------------------

_PII_PATTERNS = {
    "CF": re.compile(
        r"\b[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z]\d{3}[A-Z]\b",
        re.IGNORECASE,
    ),
    "PIVA": re.compile(
        r"(?:P\.?\s*IVA[\s:]*|partita\s+IVA[\s:]*)(\d{11})\b",
        re.IGNORECASE,
    ),
    "IBAN": re.compile(
        r"\bIT\d{2}[A-Z]\d{10}\d{12}\b",
        re.IGNORECASE,
    ),
    "EMAIL": re.compile(
        r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b",
        re.IGNORECASE,
    ),
    "TEL": re.compile(
        r"(?:\+39[\s.-]?)?(?:0\d{1,4}[\s.-]?\d{6,8}|3\d{2}[\s.-]?\d{6,7})\b"
    ),
}


@dataclass
class AnonymizationResult:
    anonymized_text: str
    entity_map: dict[str, str] = field(default_factory=dict)  # "[TAG_001]" → valore originale
    stats: dict = field(default_factory=dict)
    residual_pii_warnings: list[str] = field(default_factory=list)


class LegalAnonymizer:
    """
    Anonimizza PII in testi legali italiani.
    Preserva sempre i riferimenti normativi e giurisprudenziali.
    """

    def __init__(self, spacy_model: str = "it_core_news_lg", use_spacy: bool = True):
        self._use_spacy = use_spacy
        self._nlp = None
        if use_spacy:
            self._load_spacy(spacy_model)

    def _load_spacy(self, model: str) -> None:
        try:
            import spacy
            self._nlp = spacy.load(model)
            logger.info(f"spaCy model caricato: {model}")
        except Exception as e:
            logger.warning(f"spaCy non disponibile ({e}). Solo Layer 1 attivo.")
            self._nlp = None

    # ------------------------------------------------------------------
    # API pubblica
    # ------------------------------------------------------------------

    def anonymize(self, text: str, doc_id: str = "") -> AnonymizationResult:
        """
        Anonimizza il testo in due layer:
          L1: regex (CF, PIVA, IBAN, email, telefono)
          L2: spaCy (PER, ORG con score > 0.80)
        """
        entity_map: dict[str, str] = {}
        stats: dict[str, int] = {}
        counters: dict[str, int] = {k: 0 for k in _PII_PATTERNS}
        counters["PERSONA"] = 0
        counters["ORG"] = 0

        # 1. Maschera la whitelist per non toccarla
        protected, text_masked = self._mask_whitelist(text)

        # 2. Layer 1 — Regex
        text_masked, entity_map, counters = self._apply_regex(
            text_masked, entity_map, counters
        )

        # 3. Layer 2 — spaCy
        if self._nlp:
            text_masked, entity_map, counters = self._apply_spacy(
                text_masked, entity_map, counters
            )

        # 4. Ripristina whitelist
        final_text = self._restore_whitelist(text_masked, protected)

        stats = {k: v for k, v in counters.items() if v > 0}
        return AnonymizationResult(
            anonymized_text=final_text,
            entity_map=entity_map,
            stats=stats,
        )

    def restore(self, anonymized_text: str, entity_map: dict[str, str]) -> str:
        """Ripristina il testo originale dall'entity_map."""
        text = anonymized_text
        # Sostituisce dal più lungo al più corto per evitare conflitti
        for placeholder, original in sorted(
            entity_map.items(), key=lambda x: len(x[0]), reverse=True
        ):
            text = text.replace(placeholder, original)
        return text

    # ------------------------------------------------------------------
    # Layer 1 — Regex
    # ------------------------------------------------------------------

    def _apply_regex(
        self,
        text: str,
        entity_map: dict,
        counters: dict,
    ):
        for tag, pattern in _PII_PATTERNS.items():
            def _replacer(m, _tag=tag):
                matched = m.group(0)
                # Riusa il placeholder se il valore è già stato visto
                reverse = {v: k for k, v in entity_map.items()}
                if matched in reverse:
                    return reverse[matched]
                # Crea un placeholder indicizzato univoco (stesso nel testo e nella map)
                placeholder = f"[{_tag}_REDACTED_{counters[_tag]}]"
                entity_map[placeholder] = matched
                counters[_tag] += 1
                return placeholder
            text = pattern.sub(_replacer, text)
        return text, entity_map, counters

    # ------------------------------------------------------------------
    # Layer 2 — spaCy
    # ------------------------------------------------------------------

    def _apply_spacy(
        self,
        text: str,
        entity_map: dict,
        counters: dict,
        min_score: float = 0.80,
    ):
        doc = self._nlp(text)
        # Processa da destra per non spostare gli offset
        replacements = []
        for ent in doc.ents:
            if ent.label_ == "PER":
                score = ent._.get("score") if ent._.has("score") else 1.0
                if score is None or score >= min_score:
                    tag = "PERSONA"
                    n = counters[tag]
                    placeholder = f"[{tag}_{n:03d}]"
                    entity_map[placeholder] = ent.text
                    counters[tag] += 1
                    replacements.append((ent.start_char, ent.end_char, placeholder))
            elif ent.label_ == "ORG":
                score = ent._.get("score") if ent._.has("score") else 1.0
                if score is None or score >= min_score:
                    tag = "ORG"
                    n = counters[tag]
                    placeholder = f"[{tag}_{n:03d}]"
                    entity_map[placeholder] = ent.text
                    counters[tag] += 1
                    replacements.append((ent.start_char, ent.end_char, placeholder))

        # Applica in ordine inverso
        for start, end, placeholder in sorted(replacements, key=lambda x: x[0], reverse=True):
            text = text[:start] + placeholder + text[end:]

        return text, entity_map, counters

    # ------------------------------------------------------------------
    # Whitelist (protezione riferimenti normativi)
    # ------------------------------------------------------------------

    def _mask_whitelist(self, text: str) -> tuple[list[str], str]:
        """Sostituisce i match whitelist con token PROTECTED_N."""
        protected: list[str] = []
        def _repl(m):
            idx = len(protected)
            protected.append(m.group(0))
            return f"__PROT_{idx}__"
        masked = _WHITELIST_RE.sub(_repl, text)
        return protected, masked

    def _restore_whitelist(self, text: str, protected: list[str]) -> str:
        for i, original in enumerate(protected):
            text = text.replace(f"__PROT_{i}__", original)
        return text
