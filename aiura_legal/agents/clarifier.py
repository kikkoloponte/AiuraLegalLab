"""
Legal Clarifier [S1] — valuta se la query ha bisogno di chiarimento prima del retrieval.

Regole (da .pi/skills/legal_clarifier.md):
  - Max 1 domanda per turno (non liste)
  - Max 2 turni totali, poi procedi sempre con defaults
  - Domande specifiche: "Appalto pubblico o privato?" non "Puoi dettagliare?"

Integrazione nel loop:
  turn=0 → prima valutazione della query originale
  turn=1 → seconda valutazione con risposta dell'utente come contesto
  turn≥2 → sempre needs_clarification=False (procedi con retrieval)

Graceful degradation: se Ollama non è disponibile → needs_clarification=False
(si procede direttamente al retrieval senza bloccare l'utente).
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from loguru import logger

from aiura_legal.agents.ollama_client import OllamaClient
from aiura_legal.core.istituti.registry import Istituto, get_registry
from aiura_legal.core.istituti.semantic_match import get_semantic_matcher, suggest_istituto_candidates

_SKILL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_clarifier.md"
)

_DEFAULT_ASSUMPTIONS = {
    "jurisdiction": "IT",
    "normativa": "vigente",
    "parte": "non_specificata",
}


def _load_system_prompt() -> str:
    if not _SKILL_PATH.exists():
        logger.warning(f"[S1] Pi Skill non trovata: {_SKILL_PATH}")
        return (
            "Sei un assistente legale. Valuta se la query di un avvocato italiano "
            "è sufficientemente precisa per un retrieval normativo accurato. "
            "Rispondi in JSON con 'needs_clarification' (bool) e "
            "'question_to_user' (stringa, solo se true)."
        )
    text = _SKILL_PATH.read_text(encoding="utf-8")
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
    return text.strip()


_SYSTEM_PROMPT: str = _load_system_prompt()


# ---------------------------------------------------------------------------
# Tipi
# ---------------------------------------------------------------------------

@dataclass
class ClarificationResult:
    needs_clarification: bool
    question_to_user: Optional[str] = None
    missing_element: Optional[str] = None    # giurisdizione|data|tipo_parte|branca
    turn_number: int = 0
    parse_ok: bool = True
    istituto_candidates: list[str] = field(default_factory=list)  # id proposti a scelta multipla
    enriched_query: Optional[str] = None      # query arricchita dall'istituto scelto dall'avvocato


# ---------------------------------------------------------------------------
# ClarifierAgent
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Pre-filtro: pattern che identificano query già sufficientemente specifiche
# senza chiamare il LLM — risparmia latenza e riduce falsi positivi S1.
# ---------------------------------------------------------------------------

# Articolo normativo esplicito: "art. 52", "art. 2043", "articolo 1350"
_RE_ART_NUM = re.compile(r"\bart(?:icolo)?\.?\s*\d+", re.I)

# Riferimento a legge specifica: "d.lgs. 81/2015", "l. 241/1990", "dpr 600/73"
_RE_LAW_REF = re.compile(
    r"\b(?:d\.?lgs\.?|d\.?p\.?r\.?|legge|l\.|r\.d\.?|d\.?l\.?)\s*\d+[\s/]\d{2,4}\b", re.I
)

# Nomi di istituti giuridici precisi (non esaustivo, ma copre i casi più frequenti)
_LEGAL_INSTITUTES = frozenset({
    "legittima difesa", "prescrizione", "decadenza", "nullità", "annullabilità",
    "responsabilità extracontrattuale", "responsabilità contrattuale", "inadempimento",
    "risoluzione del contratto", "caparra confirmatoria", "caparra penitenziale",
    "usucapione", "pignoramento", "espropriazione", "sequestro preventivo",
    "patteggiamento", "rito abbreviato", "giudizio immediato", "incidente probatorio",
    "concorso di reati", "recidiva", "misura cautelare", "custodia cautelare",
    "autotutela", "silenzio inadempimento", "accesso agli atti",
    "accertamento con adesione", "ravvedimento operoso", "interpello",
    "trasferimento d'azienda", "contratto a termine", "licenziamento",
    "divorzio", "separazione", "affidamento", "assegno divorzile",
    "bancarotta", "concordato preventivo", "fallimento", "liquidazione giudiziale",
    "codice civile", "codice penale", "codice di procedura", "codice del consumo",
})

_LEGAL_INSTITUTES_RE = re.compile(
    "|".join(re.escape(t) for t in sorted(_LEGAL_INSTITUTES, key=len, reverse=True)),
    re.I,
)

# Pattern strutturali: "qual è la disciplina di X", "cosa prevede X", ecc.
# Indicano query con ambito già definito anche senza istituto esplicito.
_RE_LEGAL_QUESTION = re.compile(
    r"\b(?:"
    r"qual[eè]\s+(?:la\s+)?disciplina"
    r"|cosa\s+prev[eia]"
    r"|quali\s+sono\s+(?:i|le|gli)\s+(?:requisiti|presupposti|effetti|elementi|casi|condizioni|limiti|termini)"
    r"|come\s+si\s+(?:configura|applica|calcola|determina|esercita|propone)"
    r"|quando\s+(?:si\s+applica|è\s+possibile|scatta)"
    r"|in\s+quali\s+casi"
    r")\b",
    re.I,
)


def _is_specific_enough(query: str) -> bool:
    """
    Euristico: restituisce True se la query è già sufficientemente specifica
    per procedere al retrieval senza chiedere chiarimenti.
    Soglia conservativa: è preferibile non bloccare (falso negativo).
    """
    q = query.strip()
    # Query molto breve e senza contesto → chiedi
    if len(q.split()) < 5:
        return False
    # Contiene articolo numerato
    if _RE_ART_NUM.search(q):
        return True
    # Contiene riferimento a legge specifica
    if _RE_LAW_REF.search(q):
        return True
    # Contiene istituto giuridico preciso
    if _LEGAL_INSTITUTES_RE.search(q):
        return True
    # Ha struttura di domanda giuridica standard ("qual è la disciplina", ecc.)
    if _RE_LEGAL_QUESTION.search(q):
        return True
    return False


def _resolve_candidate_choice(context: str, candidates: list[Istituto]) -> Optional[Istituto]:
    """
    Risolve la risposta dell'avvocato a una domanda a scelta multipla di istituti.
    Riconosce un numero d'ordine ("2", "opzione 2") o parole della label
    dell'istituto nel testo libero. "Altro"/nessun match → None (l'avvocato
    ha specificato qualcos'altro, si procede con la valutazione normale).
    """
    text = context.strip().lower()
    if not text or "altro" in text:
        return None

    m = re.search(r"\b(\d+)\b", text)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(candidates):
            return candidates[idx]

    for cand in candidates:
        label_words = [w for w in re.findall(r"[a-zàèéìòóù]+", cand.label.lower()) if len(w) > 3]
        if label_words and sum(1 for w in label_words if w in text) >= max(1, len(label_words) // 2):
            return cand

    return None


class ClarifierAgent:
    """
    S1 Legal Clarifier.

    Chiama Ollama per valutare se la query necessita di informazioni
    aggiuntive prima del retrieval. Restituisce sempre un ClarificationResult
    senza sollevare eccezioni.

    Pre-filtro Python: le query con riferimenti normativi espliciti (articolo
    numerato, legge specifica, istituto giuridico noto) vengono classificate
    come specifiche senza chiamare il LLM, risparmiando latenza.
    """

    def __init__(self, ollama: OllamaClient) -> None:
        self._ollama = ollama

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    @staticmethod
    def _build_prompt(query: str, turn_number: int, context: Optional[str]) -> str:
        lines = [
            f"TURNO: {turn_number + 1} di 2",
            f"QUERY AVVOCATO: {query}",
        ]
        if context:
            lines.append(f"RISPOSTA PRECEDENTE: {context}")
        lines += [
            "",
            "Valuta se mancano informazioni critiche che renderebbero impreciso il retrieval.",
            "Se la query è già sufficientemente specifica → needs_clarification: false.",
            "Se manca un'informazione chiave → needs_clarification: true con 1 sola domanda.",
            "Rispondi SOLO in JSON valido, senza testo prima o dopo.",
        ]
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(raw: str, turn_number: int) -> ClarificationResult:
        """Parsa la risposta JSON. Fallback conservativo: needs_clarification=False."""
        for pattern in [
            r"```json\s*(\{.*?\})\s*```",
            r"```\s*(\{.*?\})\s*```",
            r"(\{.*\})",
        ]:
            m = re.search(pattern, raw, re.DOTALL)
            if m:
                try:
                    data = json.loads(m.group(1))
                    needs = bool(data.get("needs_clarification", False))
                    question = str(data["question_to_user"]) if needs and "question_to_user" in data else None
                    missing = data.get("missing_element")
                    return ClarificationResult(
                        needs_clarification=needs,
                        question_to_user=question,
                        missing_element=missing,
                        turn_number=turn_number,
                        parse_ok=True,
                    )
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue

        logger.warning("[S1 Clarifier] JSON non parsabile — procedo senza chiarimento")
        return ClarificationResult(
            needs_clarification=False,
            turn_number=turn_number,
            parse_ok=False,
        )

    # ------------------------------------------------------------------
    # assess()  — entry point
    # ------------------------------------------------------------------

    async def assess(
        self,
        query: str,
        turn_number: int = 0,
        context: Optional[str] = None,
    ) -> ClarificationResult:
        """
        Valuta se la query necessita di chiarimento.

        Args:
            query:       testo della query originale
            turn_number: 0 = prima valutazione, 1 = seconda, ≥2 = procedi sempre
            context:     risposta dell'utente al turno precedente

        Returns:
            ClarificationResult con needs_clarification=False se:
            - turn_number ≥ 2
            - Ollama non disponibile
            - JSON non parsabile
            - La query è già sufficientemente specifica
        """
        # Regola hard: al 3° tentativo procedi sempre
        if turn_number >= 2:
            logger.info("[S1 Clarifier] Turn >= 2 — procedo con defaults")
            return ClarificationResult(
                needs_clarification=False,
                turn_number=turn_number,
            )

        # Turno di risposta a una scelta multipla proposta al turno precedente:
        # i candidati sono ricalcolati deterministicamente sulla query ORIGINALE
        # (non dipendono dal turno), quindi ritroviamo la stessa lista senza
        # doverla far viaggiare nella request.
        if turn_number >= 1 and context:
            candidates = suggest_istituto_candidates(query, get_registry(), get_semantic_matcher())
            if len(candidates) >= 2:
                resolved = _resolve_candidate_choice(context, candidates)
                if resolved is not None:
                    enriched = (
                        f"{query} — con riferimento specifico a: {resolved.label} "
                        f"({'; '.join(resolved.norme_riferimento[:2])})"
                    )
                    logger.info(
                        f"[S1 Clarifier] istituto risolto da scelta multipla: {resolved.id!r}"
                    )
                    return ClarificationResult(
                        needs_clarification=False,
                        turn_number=turn_number,
                        enriched_query=enriched,
                    )
                logger.info(
                    "[S1 Clarifier] risposta scelta multipla non risolta "
                    "('altro' o testo libero) — procedo con valutazione normale"
                )

        # Disambiguazione istituto a scelta multipla: precede il pre-filtro
        # perché una query può già sembrare "specifica" (contiene un nome di
        # istituto riconosciuto, es. "sequestro preventivo") e saltare dritta
        # al retrieval pur essendo ambigua tra istituti vicini che condividono
        # lessico (es. sequestro CPP vs confisca antimafia — il caso che ha
        # originato questo intero filone di fix in questa sessione).
        if turn_number == 0:
            candidates = suggest_istituto_candidates(query, get_registry(), get_semantic_matcher())
            if len(candidates) >= 2:
                options = "\n".join(f"{i + 1}) {c.label}" for i, c in enumerate(candidates))
                question = (
                    "La tua domanda potrebbe riguardare istituti giuridici diversi. "
                    f"A quale ti riferisci?\n{options}\n{len(candidates) + 1}) Altro (specifica tu)"
                )
                logger.info(
                    f"[S1 Clarifier] scelta multipla istituto: {[c.id for c in candidates]!r}"
                )
                return ClarificationResult(
                    needs_clarification=True,
                    question_to_user=question,
                    missing_element="istituto",
                    turn_number=turn_number,
                    istituto_candidates=[c.id for c in candidates],
                )

        # Pre-filtro: query già specifiche non raggiungono il LLM
        if _is_specific_enough(query):
            logger.info("[S1 Clarifier] Pre-filtro: query già specifica — skip LLM")
            return ClarificationResult(
                needs_clarification=False,
                turn_number=turn_number,
            )

        prompt = self._build_prompt(query, turn_number, context)
        t0 = time.monotonic()

        try:
            raw = await self._ollama.generate(
                prompt=prompt,
                temperature=0.15,
                max_tokens=512,
                system=_SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.warning(f"[S1 Clarifier] Ollama non disponibile: {exc} — procedo")
            return ClarificationResult(
                needs_clarification=False,
                turn_number=turn_number,
                parse_ok=False,
            )

        result = self._parse_response(raw, turn_number)
        logger.info(
            f"[S1 Clarifier] turn={turn_number}, "
            f"needs={result.needs_clarification}, "
            f"parse_ok={result.parse_ok}, "
            f"t={time.monotonic() - t0:.2f}s"
        )
        return result
