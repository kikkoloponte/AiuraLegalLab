"""
Legal Analyst [S3] — ragionamento CoT su Research Packet.

Usa Ollama (qwen2.5:7b) con sistema prompt da .pi/skills/legal_analyst.md.
Ogni claim nella risposta DEVE avere source_id presente nel Packet
(Citation Contract). Output strutturato in JSON.

Graceful degradation: se Ollama non è disponibile o risponde con errore,
ritorna AnalysisResult con answer="" e gaps esplicativi — mai eccezioni.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Optional

from loguru import logger
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

from aiura_legal.agents.ollama_client import OllamaClient
from aiura_legal.core.retrieval.context_budget import ContextBudgetManager
from aiura_legal.core.retrieval.source_texts import (
    fetch_full_texts,
    fetch_sources_by_source_id,
    fulltext_enabled,
)
from aiura_legal.core.istituti.registry import get_registry
from aiura_legal.core.types import ResearchPacket, SearchResult


class LlmBehaviorSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    llm_temperature:          float = 0.10
    llm_max_tokens_per_phase: int   = 1800   # legacy fallback per analyze/analyze_deep
    llm_n_ctx:                int   = 8192
    llm_n_batch:              int   = 256
    llm_max_tokens_fase1:     int   = 700
    llm_max_tokens_fase2:     int   = 1100
    llm_max_tokens_fase3:     int   = 900
    llm_max_tokens_fase4:     int   = 1000


_llm_settings = LlmBehaviorSettings()

if TYPE_CHECKING:
    from aiura_legal.core.retrieval.phase_retriever import PhaseRetriever

_SKILL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst.md"
)

# Carica system prompt dalla Pi Skill (rimuove frontmatter YAML)
def _load_system_prompt() -> str:
    if not _SKILL_PATH.exists():
        logger.warning(f"[S3] Pi Skill non trovata: {_SKILL_PATH}")
        return (
            "Sei un assistente legale italiano. Analizza la domanda usando "
            "SOLO le fonti del Research Packet. Ogni claim deve avere source_id. "
            "Rispondi in JSON con campo 'analysis_sections'."
        )
    text = _SKILL_PATH.read_text(encoding="utf-8")
    # Rimuove il blocco frontmatter ---...---
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
    return text.strip()


_SYSTEM_PROMPT: str = _load_system_prompt()

_SKILL_PATH_FASE1 = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_fase1.md"
)
_SKILL_PATH_FASE2 = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_fase2.md"
)

def _load_prompt(path: Path, fallback: str) -> str:
    if not path.exists():
        logger.warning(f"Pi Skill non trovata: {path}")
        return fallback
    text = path.read_text(encoding="utf-8")
    return re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL).strip()

_SYSTEM_PROMPT_FASE1: str = _load_prompt(
    _SKILL_PATH_FASE1,
    "Sei un giurista italiano. Analizza la fattispecie normativa (step 1-5 IQRAC)."
)
_SYSTEM_PROMPT_FASE2: str = _load_prompt(
    _SKILL_PATH_FASE2,
    "Sei un giurista italiano. Completa l'analisi (step 6-9 IQRAC) con la giurisprudenza."
)

# Sequential IQRAC — 4 fasi
_SKILL_PATH_FRAMING = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_framing.md"
)
_SKILL_PATH_FRAMING_DOTTRINA = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_framing_dottrina.md"
)
_SKILL_PATH_NORMATIVA = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_normativa.md"
)
_SKILL_PATH_GIURISPRUDENZA_SEQ = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_giurisprudenza.md"
)
_SKILL_PATH_SINTESI = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_sintesi.md"
)
_SKILL_PATH_SINTESI_DOTTRINA = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_analyst_sintesi_dottrina.md"
)

_SYSTEM_PROMPT_FRAMING: str = _load_prompt(
    _SKILL_PATH_FRAMING,
    "Sei un giurista italiano. Inquadra la fattispecie (RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE)."
)
_SYSTEM_PROMPT_FRAMING_DOTTRINA: str = _load_prompt(
    _SKILL_PATH_FRAMING_DOTTRINA,
    "Sei un giurista italiano. Inquadra l'istituto giuridico (INQUADRAMENTO_ISTITUTO, PERIMETRO_DOTTRINALE, QUESTIONE_ANALITICA)."
)
_SYSTEM_PROMPT_NORMATIVA: str = _load_prompt(
    _SKILL_PATH_NORMATIVA,
    "Sei un giurista italiano. Analizza le fonti normative (FONTI_NORMATIVE, INTERPRETAZIONE)."
)
_SYSTEM_PROMPT_GIURISPRUDENZA_SEQ: str = _load_prompt(
    _SKILL_PATH_GIURISPRUDENZA_SEQ,
    "Sei un giurista italiano. Analizza gli orientamenti giurisprudenziali (GIURISPRUDENZA)."
)
_SYSTEM_PROMPT_SINTESI: str = _load_prompt(
    _SKILL_PATH_SINTESI,
    "Sei un giurista italiano. Concludi l'analisi (SUSSUNZIONE, OBIEZIONI, CONCLUSIONE)."
)
_SYSTEM_PROMPT_SINTESI_DOTTRINA: str = _load_prompt(
    _SKILL_PATH_SINTESI_DOTTRINA,
    "Sei un giurista italiano. Concludi l'analisi teorica di un istituto "
    "(SUSSUNZIONE, OBIEZIONI, CONCLUSIONE) senza presupporre un caso concreto."
)


# ---------------------------------------------------------------------------
# Step normalization (module-level per essere testabile e riusabile)
# ---------------------------------------------------------------------------

_STEP_NORM: dict[str, str] = {
    # Legacy 5-step → IQRAC equivalente (migrazione graceful)
    "NORMA APPLICABILE":   "FONTI_NORMATIVE",
    "VALUTAZIONE":         "SUSSUNZIONE",
    "GAP ANALYSIS":        "CONCLUSIONE",
    # Typo 7B su QUALIFICAZIONE
    "QUALIFICAZIONAZIONE": "QUALIFICAZIONE",
    "QUALIFICAZIZIONE":    "QUALIFICAZIONE",
    # Varianti attese dal 7B per i nuovi step
    "RICOSTRUZIONE FATTO": "RICOSTRUZIONE_FATTO",
    "RICOSTRUZIONE_FATTI": "RICOSTRUZIONE_FATTO",
    "RICOSTRUZIONE":       "RICOSTRUZIONE_FATTO",
    "FONTI NORMATIVE":     "FONTI_NORMATIVE",
    "FONTI_NORMATIVA":     "FONTI_NORMATIVE",
    "FONTE_NORMATIVA":     "FONTI_NORMATIVE",
    "FONTE NORMATIVA":     "FONTI_NORMATIVE",
    "SUSSUZIONE":          "SUSSUNZIONE",
    "OBIEZIONE":           "OBIEZIONI",
    "CONCLUSIONI":         "CONCLUSIONE",
}


def _norm_step(raw: str) -> str:
    upper = raw.strip().upper()
    if upper in _STEP_NORM:
        return _STEP_NORM[upper]
    if upper.startswith("QUALIFICA") and upper != "QUALIFICAZIONE":
        return "QUALIFICAZIONE"
    if upper.startswith("RICOSTRUZ") and upper != "RICOSTRUZIONE_FATTO":
        return "RICOSTRUZIONE_FATTO"
    if upper.startswith("SUSSUN") and upper != "SUSSUNZIONE":
        return "SUSSUNZIONE"
    return raw.strip()


def _fix_missing_commas(text: str) -> str:
    """
    Inserisce virgole mancanti tra proprietà JSON consecutive.

    Artefatto LLM comune: il modello chiude una stringa lunga e inizia la
    proprietà successiva senza virgola:
        "...long content..."
        "citations": [...]
    →
        "...long content...",
        "citations": [...]

    Usa due passate:
    - chiusura stringa seguita da apertura stringa-chiave: `" "key":`
    - chiusura stringa seguita da chiusura array/oggetto poi altra chiave
    """
    # Virgola mancante tra "...valore..." e "prossima-chiave":
    fixed = re.sub(r'(")\s*\n(\s*"[^"]+"\s*:)', r'\1,\n\2', text)
    # Virgola mancante tra true/false/null/numero e "prossima-chiave":
    fixed = re.sub(r'(true|false|null|\d)\s*\n(\s*"[^"]+"\s*:)', r'\1,\n\2', fixed)
    return fixed


def _extract_json_balanced(text: str) -> Optional[dict]:
    """
    Estrae il primo oggetto JSON bilanciato usando un contatore di parentesi.
    Più robusto dei regex per JSON con nesting profondo o stringhe complesse.
    """
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape_next = False
    for i, ch in enumerate(text[start:], start):
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start : i + 1]
                # Prova direttamente
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    pass
                # Prova con fix commas
                fixed = _fix_missing_commas(candidate)
                try:
                    return json.loads(fixed)
                except json.JSONDecodeError:
                    pass
                return _repair_truncated_json(fixed)
    return None


def _repair_truncated_json(text: str) -> Optional[dict]:
    """
    Tenta di riparare un JSON troncato da max_tokens chiudendo le strutture aperte.
    Aggiunge `}` e `]` finché il testo non è parsabile, fino a un max di 10 tentativi.
    Ritorna il dict parsato oppure None.
    """
    # Rimuovi testo parziale dopo l'ultima virgola o stringa aperta
    candidate = text.rstrip()
    # Rimuovi trailing comma prima di chiudere
    candidate = re.sub(r",\s*$", "", candidate)

    for _ in range(10):
        # Conta parentesi aperte
        opens  = candidate.count("{") - candidate.count("}")
        arrays = candidate.count("[") - candidate.count("]")
        if opens <= 0 and arrays <= 0:
            break
        candidate += "]" * max(arrays, 0) + "}" * max(opens, 0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Rimuovi l'ultimo carattere non-whitespace e riprova
            candidate = re.sub(r'[,\s]*$', "", candidate.rstrip("}]"))
            candidate = re.sub(r",\s*$", "", candidate)
    return None


# Budget manager condiviso: decide quanto testo di ogni fonte entra nel prompt
_budget_mgr = ContextBudgetManager()


def _source_texts_for_prompt(sources: list[SearchResult], corpus: str) -> list[str]:
    """
    Testo da mostrare nel prompt per ogni fonte.

    Con AIURA_FULLTEXT_CONTEXT=1 (default): full_text troncato secondo il
    budget per corpus di ContextBudgetManager (fallback snippet se il fetch
    non ha trovato il documento).
    Con AIURA_FULLTEXT_CONTEXT=0: comportamento storico snippet[:400].
    """
    if not fulltext_enabled():
        return [s.snippet[:400] for s in sources]
    return _budget_mgr.budget_texts(sources, corpus)


def _assign_refs(sources: list[SearchResult], start: int = 1) -> tuple[dict[str, str], int]:
    """
    Assegna riferimenti sequenziali "F{n}" alle fonti di UNA chiamata LLM
    (un round di Fase 2 o Fase 3), a partire da `start`.

    Sostituisce il source_id grezzo come token da citare: un modello piccolo
    (qwen2.5-7b) non copia in modo affidabile stringhe opache come URN lunghi
    o hash hex16 — le ricostruisce "a memoria" o le allucina (osservato più
    volte: id reali ma non presenti nel packet corrente). Un riferimento
    corto e progressivo (F1, F2…) è un token che il modello copia in modo
    affidabile; la risoluzione al source_id reale avviene lato sistema
    (vedi PhaseResult.ref_map e CitationReviewer._resolve_ref_citations).

    Lo start prosegue tra Fase 2 e Fase 3 nella stessa analisi (i ref sono
    quindi univoci sull'intera risposta, non solo all'interno di una fase):
    l'orchestrator pool i citations di tutte le fasi in un solo controllo
    Reviewer finale, quindi un F3 non deve poter risolvere a due fonti diverse.

    Ritorna (source_id -> ref, prossimo indice libero).
    """
    refs: dict[str, str] = {}
    i = start
    for s in sources:
        if s.source_id not in refs:
            refs[s.source_id] = f"F{i}"
            i += 1
    return refs, i


def _invert_ref_map(fwd: dict[str, str]) -> dict[str, str]:
    """source_id->ref (usato per il rendering del prompt, vedi _assign_refs)
    → ref->source_id (formato richiesto da CitationReviewer.verify(ref_map=))."""
    return {ref: sid for sid, ref in fwd.items()}


_ORGANO_LABELS = {
    "cassazione": "Cass.", "tar": "TAR", "consiglio_stato": "Cons. St.",
    "corte_cost": "Corte Cost.", "corte_conti": "Corte Conti",
}


def build_source_label(source_id: str, meta: dict | None) -> str:
    """
    Etichetta leggibile per una fonte, stessa logica usata dal frontend per il
    footer "Fonti:" (vedi frontend/src/hooks/useChat.ts mapBackendResponse).
    Centralizzata qui per poterla riusare lato backend in `humanize_refs`,
    che sostituisce i token "(F1)" lasciati nel testo prosa con la fonte
    reale leggibile (vedi humanize_refs).
    """
    meta = meta or {}
    if meta.get("organo") or source_id.startswith("giurisprudenza_"):
        organo = meta.get("organo", "")
        numero = meta.get("numero")
        anno = meta.get("anno")
        if not organo and not numero and not anno:
            # Decisione senza organo/numero/anno in metadata (scraper non li
            # ha estratti per questo doc): "Sent." da solo non è verificabile
            # dall'avvocato — usa titolo/materia se presenti, altrimenti la
            # coda del source_id (meglio di un'etichetta del tutto generica).
            return (
                meta.get("titolo", "")[:50]
                or meta.get("materia", "")
                or (source_id.rsplit("_", 1)[-1] if "_" in source_id else source_id)
            )
        organo_label = _ORGANO_LABELS.get(organo, organo) or "Sent."
        num_yr = (f"n.{numero}" if numero else "") + (f"/{anno}" if anno else "")
        return " ".join(filter(None, [organo_label, num_yr])).strip() or source_id
    articolo = meta.get("articolo") or meta.get("articolo_num")
    titolo = meta.get("titolo")
    if articolo and titolo:
        return f"{articolo} — {titolo}"[:60]
    if articolo:
        return articolo
    if titolo:
        return titolo[:50]
    if len(source_id) > 40:
        return source_id.rsplit(":", 1)[-1]
    return source_id


_FREF_RE = re.compile(r"\bF(\d+)\b")


def humanize_refs(text: str, ref_map: dict[str, str], sources_metadata: dict[str, dict]) -> str:
    """
    Sostituisce i token "F1", "F2"... lasciati dall'LLM nel testo prosa
    (es. "...accetta un rischio noto (F1)...") con l'etichetta leggibile
    della fonte reale (es. "...accetta un rischio noto (Cass. n.250/2025)...").

    Senza questa sostituzione l'avvocato vede "(F1)" nel corpo della risposta
    ma nessuna voce "F1" nell'elenco "Fonti:" finale — il ref_map esiste solo
    lato sistema per il grounding check del Reviewer (vedi
    CitationReviewer.verify(ref_map=)), non viene mai mostrato all'utente.

    Sicuro rispetto al Reviewer: il regex di estrazione citazioni
    (reviewer._CITATION_RE) non matcha mai token "F\\d+", quindi sostituirli
    nel testo prima o dopo la verifica S5 non altera l'esito del grounding
    check (che si basa sulle citations[] strutturate, non sul testo prosa).
    """
    if not text or not ref_map:
        return text

    def _repl(m: re.Match) -> str:
        ref = f"F{m.group(1)}"
        sid = ref_map.get(ref)
        if not sid:
            return m.group(0)
        return build_source_label(sid, sources_metadata.get(sid))

    return _FREF_RE.sub(_repl, text)


def resolve_citation_refs(citations: list[dict], ref_map: dict[str, str]) -> list[dict]:
    """
    Risolve i "F1"/"F2"... grezzi in citations[]["source_id"] al source_id
    reale, stesso ref_map usato da humanize_refs per il testo prosa.

    Senza questa risoluzione il frontend (ResponseCard: sourceMap[c.source_id])
    non trova mai una corrispondenza per un token "F<n>" — sourceMap è
    indicizzato per source_id reali — e mostra il chip in fallback "non
    verificato" con il token grezzo invece della fonte cliccabile.
    """
    if not citations or not ref_map:
        return citations
    resolved = []
    for c in citations:
        if isinstance(c, dict) and isinstance(c.get("source_id"), str):
            sid = ref_map.get(c["source_id"].upper())
            if sid:
                c = {**c, "source_id": sid}
        resolved.append(c)
    return resolved


def _format_source(ref: str, s: SearchResult, text: Optional[str] = None) -> list[str]:
    """
    `ref` è il riferimento da citare (es. "F1"), assegnato da _assign_refs.
    Il source_id reale NON viene mostrato nel prompt: è risolto lato sistema
    dopo la generazione, così il modello non può copiarlo male né ricostruirlo
    dal pretraining (vedi _assign_refs).
    """
    meta = s.metadata or {}
    lines = [
        f"\nFONTE {ref}",
    ]
    # Normativa
    if meta.get("titolo"):
        lines.append(f"    titolo:   {meta['titolo']}")
    if meta.get("fonte"):
        lines.append(f"    fonte:    {meta['fonte']}")
    if meta.get("articolo") or meta.get("articolo_num"):
        lines.append(f"    articolo: {meta.get('articolo') or meta.get('articolo_num')}")
    # Giurisprudenza
    if meta.get("organo"):
        organo_label = {
            "cassazione": "Corte di Cassazione",
            "tar": "TAR",
            "consiglio_stato": "Consiglio di Stato",
            "corte_cost": "Corte Costituzionale",
            "corte_conti": "Corte dei Conti",
        }.get(meta["organo"], meta["organo"].title())
        ref = f"{organo_label}"
        if meta.get("numero") and meta.get("anno"):
            ref += f" n.{meta['numero']}/{meta['anno']}"
        lines.append(f"    sentenza: {ref}")
    if meta.get("materia"):
        lines.append(f"    materia:  {meta['materia']}")
    if meta.get("chunk_type"):
        chunk_label = {"massima": "Massima", "motivazione": "Motivazione", "dispositivo": "Dispositivo"}
        lines.append(f"    estratto: {chunk_label.get(meta['chunk_type'], meta['chunk_type'])}")
    lines.append(f"    testo:    {text if text is not None else s.snippet[:400]}")
    return lines


# ---------------------------------------------------------------------------
# Tipi output
# ---------------------------------------------------------------------------

@dataclass
class AnalysisSection:
    step: str
    content: str
    citations: list[dict] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Risultato dell'analisi CoT di S3."""
    answer: str                                    # testo leggibile per l'avvocato
    analysis_sections: list[AnalysisSection]
    overall_confidence: str = "MEDIUM"             # HIGH | MEDIUM | LOW
    escalation_recommended: bool = False
    gaps: list[str] = field(default_factory=list)
    llm_model: str = ""
    duration_s: float = 0.0
    raw_response: str = ""                         # per debug/audit
    parse_ok: bool = True                          # False se JSON non parsabile
    ref_map: dict[str, str] = field(default_factory=dict)  # F1, F2… → source_id reale


@dataclass
class PhaseResult:
    """Risultato di una singola fase del Sequential IQRAC."""
    phase: int                        # 1=Framing, 2=Normativa, 3=Giurisprudenza, 4=Sintesi
    name: str                         # "FRAMING" | "NORMATIVA" | "GIURISPRUDENZA" | "SINTESI"
    sections: list[AnalysisSection]
    sources_used: list[str]           # source_id delle fonti usate in questa fase
    overall_confidence: str = "MEDIUM"
    escalation_recommended: bool = False
    gaps: list[str] = field(default_factory=list)
    duration_s: float = 0.0
    parse_ok: bool = True
    # Campi estratti dalla Fase 1 per guidare il retrieval delle fasi successive
    questione_retrieval: str = ""       # query per retrieval normativa (da Fase 1)
    qualificazione_retrieval: str = ""  # query per retrieval giurisprudenza (da Fase 1)
    giurisprudenza_retrieval_varianti: list[str] = field(default_factory=list)  # 1-3 formulazioni alternative per retrieve_giurisprudenza_multi
    settore_giuridico: str = ""         # settore estratto dalla Fase 1 (penale|civile|amministrativo|lavoro|tributario)
    # source_id → metadata delle fonti di questa fase (per il Reviewer: permette
    # di normalizzare citazioni in formato alternativo, es. "numero/anno" invece
    # di hex16, su fonti che non sono nel Research Packet S2 iniziale).
    sources_metadata: dict[str, dict] = field(default_factory=dict)
    # ref ("F1", "F2"…) → source_id reale delle fonti mostrate in questa fase.
    # Il modello cita il ref (vedi _assign_refs); il Reviewer lo risolve al
    # source_id reale prima del check di grounding — il modello non vede mai
    # il source_id grezzo, quindi non può copiarlo male né allucinarlo.
    ref_map: dict[str, str] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# AnalystAgent
# ---------------------------------------------------------------------------

class AnalystAgent:
    """
    S3 Legal Analyst.

    Costruisce il prompt con il Research Packet come contesto, chiama Ollama
    e parsa la risposta JSON strutturata. Se il JSON è malformato usa il testo
    grezzo come unica sezione ANALISI.
    """

    def __init__(self, ollama: Optional[OllamaClient] = None) -> None:
        self._ollama = ollama or OllamaClient()

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    @staticmethod
    def _effective_layer(s: SearchResult) -> str:
        """
        Determina il layer effettivo di una fonte.
        source_id ha priorità su source_layer: se il source_id inizia con
        "giurisprudenza_" la fonte è giurisprudenziale anche se source_layer
        non è stato impostato correttamente (es. ChromaDB con corpus="" non
        ancora patchato).
        """
        if s.source_id.startswith("giurisprudenza_"):
            return "giurisprudenza"
        return s.source_layer

    def _build_context(self, packet: ResearchPacket) -> tuple[str, dict[str, str]]:
        """Serializza le fonti del Research Packet in due sezioni per layer."""
        if not packet.sources:
            return "NESSUNA FONTE DISPONIBILE NEL RESEARCH PACKET.", {}

        norm  = [s for s in packet.sources if self._effective_layer(s) == "normativa"]
        giuri = [s for s in packet.sources if self._effective_layer(s) == "giurisprudenza"]

        lines = [
            "RESEARCH PACKET — cita SOLO il riferimento FN mostrato accanto a ciascuna fonte:",
            "=" * 60,
        ]
        ref_map_norm, _next = _assign_refs(norm)
        if norm:
            norm_texts = _source_texts_for_prompt(norm, "normattiva")
            lines.append("\n## FONTI NORMATIVE\n")
            for s, t in zip(norm, norm_texts):
                lines.extend(_format_source(ref_map_norm[s.source_id], s, t))
        ref_map_giuri, _ = _assign_refs(giuri, start=_next)
        if giuri:
            giuri_texts = _source_texts_for_prompt(giuri, "giurisprudenza")
            lines.append("\n## GIURISPRUDENZA\n")
            for s, t in zip(giuri, giuri_texts):
                lines.extend(_format_source(ref_map_giuri[s.source_id], s, t))
        lines.append("=" * 60)
        return "\n".join(lines), {**ref_map_norm, **ref_map_giuri}

    def _build_prompt(self, query: str, packet: ResearchPacket) -> tuple[str, dict[str, str]]:
        context, ref_map = self._build_context(packet)
        prompt = (
            f"{context}\n\n"
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            "Analizza secondo lo schema IQRAC italiano in 9 passi:\n"
            "RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE, FONTI_NORMATIVE, "
            "INTERPRETAZIONE, GIURISPRUDENZA, SUSSUNZIONE, OBIEZIONI, CONCLUSIONE.\n"
            "Per FONTI_NORMATIVE e INTERPRETAZIONE usa SOLO fonti dalla sezione "
            "'## FONTI NORMATIVE' del Packet.\n"
            "Per GIURISPRUDENZA usa SOLO fonti dalla sezione '## GIURISPRUDENZA' del Packet.\n"
            "Ogni claim fattuale DEVE citare il riferimento FN (es. F1) mostrato accanto "
            "alla fonte — NON inventare o ricostruire altri identificatori.\n"
            "Rispondi ESCLUSIVAMENTE in JSON valido, senza testo prima o dopo il JSON.\n"
        )
        return prompt, ref_map

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _extract_json(self, raw: str) -> Optional[dict]:
        """
        Estrae il primo oggetto JSON valido dalla risposta LLM.

        Strategia a cascata:
        1. Estrae il blocco tra ```json ... ``` (greedy — cattura l'intero oggetto)
        2. Prova tutto il testo con regex greedy {.*}
        3. Per ogni candidato: prova json.loads, poi fix-commas, poi repair-truncation
        4. Ultimo fallback: bracket counter per estrarre JSON bilanciato
        """
        candidates: list[str] = []

        # 1. Dentro blocco ```json ... ``` (greedy, non .*? che ferma al primo })
        for pat in [r"```json\s*(\{.*\})\s*```", r"```\s*(\{.*\})\s*```"]:
            m = re.search(pat, raw, re.DOTALL)
            if m:
                candidates.append(m.group(1))

        # 2. Tutto il testo: da { a ultima }
        m = re.search(r"(\{.*\})", raw, re.DOTALL)
        if m:
            candidates.append(m.group(1))

        # 3. JSON troncato (manca la chiusura)
        m = re.search(r"(\{.*)", raw, re.DOTALL)
        if m:
            candidates.append(m.group(1))

        # 4. Bracket counter come fallback finale
        candidates.append(raw)  # cerca in tutto il testo

        for candidate in candidates:
            # a) JSON così com'è
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
            # b) Fix virgole mancanti tra proprietà (artefatto LLM comune)
            fixed = _fix_missing_commas(candidate)
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass
            # c) Repair troncamento (aggiunge } ] mancanti)
            repaired = _repair_truncated_json(fixed)
            if repaired is not None:
                return repaired

        # d) Bracket counter: estrae JSON bilanciato ignorando testo circostante
        return _extract_json_balanced(raw)

    def _parse_response(
        self, raw: str
    ) -> tuple[list[AnalysisSection], str, bool, bool]:
        """
        Parsa risposta S3.
        Ritorna (sections, confidence, escalation_recommended, parse_ok).
        """
        data = self._extract_json(raw)
        if data is None:
            # Fallback: risposta grezza come sezione unica
            return (
                [AnalysisSection(step="ANALISI", content=raw.strip())],
                "LOW",
                False,
                False,
            )

        sections_raw = data.get("analysis_sections", [])
        if not isinstance(sections_raw, list):
            sections_raw = []

        sections = [
            AnalysisSection(
                step=_norm_step(str(s.get("step", ""))),
                content=str(s.get("content", "")),
                citations=s.get("citations", []) if isinstance(s.get("citations"), list) else [],
            )
            for s in sections_raw
            if isinstance(s, dict)
        ]

        if not sections:
            # JSON parsato ma vuoto: usa risposta grezza
            sections = [AnalysisSection(step="ANALISI", content=raw.strip())]

        confidence = str(data.get("overall_confidence", "MEDIUM")).upper()
        if confidence not in ("HIGH", "MEDIUM", "LOW"):
            confidence = "MEDIUM"

        escalation = bool(data.get("escalation_recommended", False))
        return sections, confidence, escalation, True

    # ------------------------------------------------------------------
    # Generazione testo leggibile
    # ------------------------------------------------------------------

    @staticmethod
    def _sections_to_answer(sections: list[AnalysisSection]) -> str:
        """Converte le sezioni CoT in testo leggibile per l'avvocato."""
        parts = []
        for s in sections:
            if not s.content:
                continue
            header = f"**{s.step}**\n" if s.step else ""
            parts.append(f"{header}{s.content}")
        return "\n\n".join(parts)

    # ------------------------------------------------------------------
    # Deep mode helpers
    # ------------------------------------------------------------------

    def _build_context_normativa(self, packet: ResearchPacket) -> tuple[str, dict[str, str]]:
        norm = [s for s in packet.sources if self._effective_layer(s) == "normativa"]
        if not norm:
            return "NESSUNA FONTE NORMATIVA NEL RESEARCH PACKET.", {}
        texts = _source_texts_for_prompt(norm, "normattiva")
        ref_map, _ = _assign_refs(norm)
        lines = ["FONTI NORMATIVE — cita SOLO il riferimento FN mostrato:", "=" * 60]
        for s, t in zip(norm, texts):
            lines.extend(_format_source(ref_map[s.source_id], s, t))
        lines.append("=" * 60)
        return "\n".join(lines), ref_map

    def _build_context_giurisprudenza(self, packet: ResearchPacket, start: int = 1) -> tuple[str, dict[str, str]]:
        giuri = [s for s in packet.sources if self._effective_layer(s) == "giurisprudenza"]
        if not giuri:
            return "NESSUNA GIURISPRUDENZA NEL RESEARCH PACKET.", {}
        texts = _source_texts_for_prompt(giuri, "giurisprudenza")
        ref_map, _ = _assign_refs(giuri, start=start)
        lines = ["GIURISPRUDENZA — cita SOLO il riferimento FN mostrato:", "=" * 60]
        for s, t in zip(giuri, texts):
            lines.extend(_format_source(ref_map[s.source_id], s, t))
        lines.append("=" * 60)
        return "\n".join(lines), ref_map

    @staticmethod
    def _build_fase2_summary(sections: list[AnalysisSection]) -> str:
        """Sintesi compatta della Fase 1 da passare come contesto alla Fase 2."""
        parts = ["ANALISI NORMATIVA (Fase 1) — non ripetere questi step:", "─" * 50]
        for s in sections:
            if s.content:
                parts.append(f"{s.step}: {s.content[:400]}")
        parts.append("─" * 50)
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # analyze_deep()  — entry point modalità deep (due chiamate LLM)
    # ------------------------------------------------------------------

    async def analyze_deep(
        self,
        query: str,
        packet: ResearchPacket,
        temperature: float = 0.10,
        max_tokens: int = 3000,
    ) -> tuple["AnalysisResult", Optional["AnalysisResult"]]:
        """
        Modalità deep: due chiamate LLM sequenziali.
        Fase 1 — normativa (step 1-5)
        Fase 2 — giurisprudenza + conclusione (step 6-9), costruita su Fase 1.

        Ritorna (fase1_result, fase2_result).
        Se Fase 2 fallisce ritorna (fase1_result, None) — risposta parziale.
        """
        # ── Fase 1 ────────────────────────────────────────────────────
        ctx_norm, ref_map_f1 = self._build_context_normativa(packet)
        prompt_f1 = (
            f"{ctx_norm}\n\n"
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            "Produci i 5 step normativi IQRAC: RICOSTRUZIONE_FATTO, QUALIFICAZIONE, "
            "QUESTIONE, FONTI_NORMATIVE, INTERPRETAZIONE.\n"
            "Ogni claim fattuale DEVE citare il riferimento FN (es. F1) mostrato accanto "
            "alla fonte — NON inventare o ricostruire altri identificatori.\n"
            "Rispondi ESCLUSIVAMENTE in JSON valido.\n"
        )
        t0 = time.monotonic()
        try:
            raw_f1 = await self._ollama.generate(
                prompt=prompt_f1, temperature=temperature,
                max_tokens=max_tokens, system=_SYSTEM_PROMPT_FASE1,
            )
        except Exception as exc:
            logger.warning(f"[S3 Fase1] Ollama non disponibile: {exc}")
            empty = AnalysisResult(
                answer="", analysis_sections=[], overall_confidence="LOW",
                gaps=[f"LLM non disponibile ({type(exc).__name__})."],
                llm_model=self._ollama.model, parse_ok=False,
            )
            return empty, None

        sections_f1, conf_f1, _, ok_f1 = self._parse_response(raw_f1)
        result_f1 = AnalysisResult(
            answer=self._sections_to_answer(sections_f1),
            analysis_sections=sections_f1,
            overall_confidence=conf_f1,
            gaps=[],
            llm_model=self._ollama.model,
            duration_s=time.monotonic() - t0,
            raw_response=raw_f1,
            parse_ok=ok_f1,
            ref_map=_invert_ref_map(ref_map_f1),
        )
        logger.info(
            f"[S3 Fase1] {len(sections_f1)} sezioni, "
            f"confidence={conf_f1}, parse_ok={ok_f1}, t={result_f1.duration_s:.1f}s"
        )

        # ── Fase 2 ────────────────────────────────────────────────────
        # I ref proseguono da dove è arrivata la Fase 1: F1/F2 univoci su
        # tutta l'analisi, non solo all'interno della singola chiamata LLM.
        _next_ref = max((int(r[1:]) for r in ref_map_f1.values()), default=0) + 1
        ctx_giuri, ref_map_f2 = self._build_context_giurisprudenza(packet, start=_next_ref)
        summary_f1 = self._build_fase2_summary(sections_f1)
        prompt_f2 = (
            f"{summary_f1}\n\n"
            f"{ctx_giuri}\n\n"
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            "Costruisci i 4 step finali IQRAC: GIURISPRUDENZA, SUSSUNZIONE, "
            "OBIEZIONI, CONCLUSIONE.\n"
            "Basati sull'analisi normativa sopra. Sii dettagliato e operativo.\n"
            "Ogni citazione giurisprudenziale DEVE citare il riferimento FN (es. F2) "
            "mostrato accanto alla fonte — NON inventare o ricostruire altri identificatori.\n"
            "Rispondi ESCLUSIVAMENTE in JSON valido.\n"
        )
        t1 = time.monotonic()
        try:
            raw_f2 = await self._ollama.generate(
                prompt=prompt_f2, temperature=temperature,
                max_tokens=max_tokens, system=_SYSTEM_PROMPT_FASE2,
            )
        except Exception as exc:
            logger.warning(f"[S3 Fase2] Ollama non disponibile: {exc} — risposta parziale")
            return result_f1, None

        sections_f2, conf_f2, escalation_f2, ok_f2 = self._parse_response(raw_f2)
        result_f2 = AnalysisResult(
            answer=self._sections_to_answer(sections_f2),
            analysis_sections=sections_f2,
            overall_confidence=conf_f2,
            escalation_recommended=escalation_f2,
            gaps=[],
            llm_model=self._ollama.model,
            duration_s=time.monotonic() - t1,
            raw_response=raw_f2,
            parse_ok=ok_f2,
            ref_map=_invert_ref_map({**ref_map_f1, **ref_map_f2}),
        )
        logger.info(
            f"[S3 Fase2] {len(sections_f2)} sezioni, "
            f"confidence={conf_f2}, parse_ok={ok_f2}, t={result_f2.duration_s:.1f}s"
        )
        return result_f1, result_f2

    # ------------------------------------------------------------------
    # analyze_sequential()  — Sequential IQRAC (4 fasi + retrieval per fase)
    # ------------------------------------------------------------------

    @staticmethod
    def _build_framing_summary(sections: list[AnalysisSection], data: dict) -> str:
        """Riassunto compatto della Fase 1 da passare come contesto alle fasi successive."""
        parts = ["FRAMING GIURIDICO (Fase 1) — non ripetere questi step:", "─" * 50]
        for s in sections:
            if s.content:
                content = s.content[:300]
                if len(s.content) > 300:
                    content += "…"
                parts.append(f"{s.step}: {content}")
        # Aggiungi settore giuridico se disponibile (guida retrieval e coerenza)
        if data.get("settore_giuridico"):
            parts.append(f"settore_giuridico: {data['settore_giuridico']}")
        parts.append("─" * 50)
        return "\n".join(parts)

    @staticmethod
    def _build_phase_context(phase_results: list["PhaseResult"], max_chars_per_section: int = 250) -> str:
        """Riassunto compatto di tutte le fasi precedenti.

        Limita ogni sezione a `max_chars_per_section` caratteri per contenere
        il contesto entro limiti gestibili per il modello.
        """
        parts = ["ANALISI PRECEDENTE — non ripetere questi step:", "─" * 50]
        for pr in phase_results:
            parts.append(f"\n[Fase {pr.phase}: {pr.name}]")
            for s in pr.sections:
                if s.content:
                    content = s.content[:max_chars_per_section]
                    if len(s.content) > max_chars_per_section:
                        content += "…"
                    parts.append(f"{s.step}: {content}")
        parts.append("─" * 50)
        return "\n".join(parts)

    @staticmethod
    def _format_phase_sources(
        sources: list[SearchResult], corpus: str = "normattiva", start: int = 1,
    ) -> tuple[str, dict[str, str]]:
        """Serializza fonti di fase in formato leggibile per il prompt.

        `corpus` seleziona il budget token di ContextBudgetManager
        (full_text_slots/summary_slots) quando AIURA_FULLTEXT_CONTEXT=1.
        `start` è il primo indice di riferimento FN libero (prosegue da fonti
        già mostrate in altri blocchi della stessa chiamata LLM).
        Ritorna (testo, ref_map: source_id → "FN").
        """
        if not sources:
            return "NESSUNA FONTE DISPONIBILE PER QUESTA FASE.", {}
        texts = _source_texts_for_prompt(sources, corpus)
        ref_map, _ = _assign_refs(sources, start=start)
        lines = ["FONTI PER QUESTA FASE — cita SOLO il riferimento FN mostrato:", "=" * 60]
        for s, t in zip(sources, texts):
            lines.extend(_format_source(ref_map[s.source_id], s, t))
        lines.append("=" * 60)
        return "\n".join(lines), ref_map

    async def analyze_sequential(
        self,
        query: str,
        packet: ResearchPacket,
        phase_retriever: Optional["PhaseRetriever"] = None,
        max_tokens_per_phase: int = 0,  # 0 = usa valore da env (LLM_MAX_TOKENS_PER_PHASE)
        query_type: str = "case",       # "case" | "doctrine" — seleziona Fase 1
    ) -> AsyncGenerator["PhaseResult", None]:
        """
        Sequential IQRAC: 4 fasi sequenziali con retrieval mirato per fase.

        Async generator: yielda ogni PhaseResult appena completato,
        permettendo lo streaming SSE fase per fase.

        Fasi:
          1. Framing (RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE) — no fonti
             oppure Inquadramento Dottrinale se query_type=="doctrine"
          2. Normativa (FONTI_NORMATIVE, INTERPRETAZIONE) — re-query normattiva
          3. Giurisprudenza (GIURISPRUDENZA) — re-query giurisprudenza
          4. Sintesi (SUSSUNZIONE, OBIEZIONI, CONCLUSIONE) — no nuovo retrieval

        Tutte e 4 le fasi usano temperature=0.0 (deterministico). Prima di questo
        fix solo la Fase 2 era deterministica: Fase 1/3/4 usavano il default da
        env (~0.10), introducendo varianza pura di sampling che si propagava a
        valle (Fase 1 genera la QUESTIONE usata per il re-retrieval di Fase 2/3 —
        un framing leggermente diverso a ogni run cambiava le fonti recuperate e
        quindi il verdetto finale, anche a parità di domanda).
        """
        if max_tokens_per_phase == 0:
            max_tokens_per_phase = _llm_settings.llm_max_tokens_per_phase

        completed_phases: list[PhaseResult] = []

        # ── Fase 1: Framing (IQRAC) o Inquadramento Dottrinale ───────
        t0 = time.monotonic()
        _is_doctrine = query_type == "doctrine"
        _budget_f1 = _llm_settings.llm_max_tokens_fase1 - 50

        if _is_doctrine:
            _prompt_f1_steps = (
                "Produci i 3 step dottrinali: INQUADRAMENTO_ISTITUTO, PERIMETRO_DOTTRINALE, QUESTIONE_ANALITICA.\n"
            )
            _system_f1 = _SYSTEM_PROMPT_FRAMING_DOTTRINA
            _phase1_name = "FRAMING_DOTTRINA"
        else:
            _prompt_f1_steps = (
                "Produci i 3 step di framing IQRAC: RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE.\n"
            )
            _system_f1 = _SYSTEM_PROMPT_FRAMING
            _phase1_name = "FRAMING"

        prompt_f1 = (
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            f"{_prompt_f1_steps}"
            "OGNI sezione: massimo 80 parole nel campo content. citations[] = array vuoto.\n"
            f"BUDGET TOKEN: la risposta JSON DEVE terminare entro {_budget_f1} token. "
            "Chiudi subito il JSON all'ultimo step.\n"
            "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido e completo.\n"
        )
        raw_f1 = ""
        data_f1: dict = {}
        try:
            raw_f1 = await self._ollama.generate(
                prompt=prompt_f1, temperature=0.0,           # deterministico: vedi docstring
                max_tokens=_llm_settings.llm_max_tokens_fase1,
                system=_system_f1,
                n_ctx=_llm_settings.llm_n_ctx,
                n_batch=_llm_settings.llm_n_batch,
            )
            data_f1 = self._extract_json(raw_f1) or {}
        except Exception as exc:
            logger.warning(f"[S3 Seq Fase1] Ollama errore: {exc}")

        sections_f1, conf_f1, _, ok_f1 = self._parse_response(raw_f1 or "")
        questione_retrieval = str(data_f1.get("questione_retrieval", "")).strip()
        qualificazione_retrieval = str(data_f1.get("qualificazione_retrieval", "")).strip()

        # Fallback: usa query originale se il modello non ha estratto le query di retrieval
        if not questione_retrieval:
            questione_retrieval = query
        if not qualificazione_retrieval:
            qualificazione_retrieval = query

        # Varianti opzionali per il retrieval giurisprudenza multi-query (max 3,
        # vedi PhaseRetriever.retrieve_giurisprudenza_multi). Se il modello non
        # le produce, fallback alla singola qualificazione_retrieval — comportamento
        # identico a prima dell'introduzione di questo campo.
        _varianti_raw = data_f1.get("giurisprudenza_retrieval_varianti", [])
        giurisprudenza_retrieval_varianti = [
            str(v).strip() for v in _varianti_raw
            if isinstance(v, str) and str(v).strip()
        ][:3] if isinstance(_varianti_raw, list) else []
        if not giurisprudenza_retrieval_varianti:
            giurisprudenza_retrieval_varianti = [qualificazione_retrieval]

        # Visibilità di debug: le varianti dovrebbero derivare dalle sotto-questioni
        # già enumerate in PERIMETRO_DOTTRINALE/QUALIFICAZIONE — log affiancato per
        # verificare a colpo d'occhio se il modello le ha effettivamente derivate da
        # lì o se ha solo riparafrasato la domanda originale.
        _sottoquestioni_content = next(
            (s.content for s in sections_f1 if s.step in ("PERIMETRO_DOTTRINALE", "QUALIFICAZIONE")), ""
        )
        logger.info(
            f"[S3 Seq] sotto-questioni enumerate ({_phase1_name}): {_sottoquestioni_content!r}"
        )
        logger.info(
            f"[S3 Seq] giurisprudenza_retrieval_varianti ({len(giurisprudenza_retrieval_varianti)}): "
            f"{giurisprudenza_retrieval_varianti!r}"
        )

        # Estrai settore_giuridico dalla Fase 1 (tassonomia: penale|civile|amministrativo|lavoro|tributario)
        #
        # settore_confidence alimenta il filtro settore di PhaseRetriever
        # (AIURA_SETTORE_FILTER/AIURA_SETTORE_SOFT — vedi phase_retriever.py):
        # prima era hardcoded a 0.0, quindi il filtro non scattava MAI a
        # prescindere dai flag env, lasciando passare rumore cross-ramo nel
        # retrieval (es. art. 2905 c.c. — sequestro conservativo CIVILE —
        # per una domanda di sequestro preventivo PENALE). Distinguiamo:
        #   0.8 — il modello ha classificato direttamente un valore valido
        #         (soglia hard=0.7 superata: filtro attivo se
        #         AIURA_SETTORE_FILTER=1)
        #   0.5 — inferito dal fallback lessicale su QUALIFICAZIONE/query
        #         (soglia soft: penalizza senza escludere, se
        #         AIURA_SETTORE_SOFT=1)
        #   0.0 — nessun settore riconosciuto, nessun filtro
        _SETTORI_VALIDI = frozenset({"penale", "civile", "amministrativo", "lavoro", "tributario"})
        settore_giuridico = str(data_f1.get("settore_giuridico", "")).strip().lower()
        settore_confidence = 0.0
        if settore_giuridico in _SETTORI_VALIDI:
            settore_confidence = 0.8
        else:
            # Fallback: inferisci dal testo della QUALIFICAZIONE
            _qualificazione_content = next(
                (s.content for s in sections_f1 if s.step == "QUALIFICAZIONE"), ""
            ).lower()
            _full_text = _qualificazione_content + " " + query.lower()
            if any(kw in _full_text for kw in ("penale", "reato", "dolo", "colpa", "imputabil")):
                settore_giuridico = "penale"
            elif any(kw in _full_text for kw in ("licenziamento", "rapporto di lavoro", "ccnl", "inps")):
                settore_giuridico = "lavoro"
            elif any(kw in _full_text for kw in ("appalto pubblic", "atto amministrativ", "tar ", "autotutela")):
                settore_giuridico = "amministrativo"
            elif any(kw in _full_text for kw in ("tribut", "fiscal", "iva ", "irpef", "accertament")):
                settore_giuridico = "tributario"
            elif any(kw in _full_text for kw in ("contratt", "obbligaz", "risarciment", "inadempiment")):
                settore_giuridico = "civile"
            else:
                settore_giuridico = ""
            if settore_giuridico:
                settore_confidence = 0.5
        if settore_giuridico:
            logger.info(
                f"[S3 Seq] settore_giuridico estratto da Fase 1: {settore_giuridico!r} "
                f"(confidence={settore_confidence})"
            )
        else:
            logger.info("[S3 Seq] settore_giuridico non riconosciuto — retrieval senza filtro settore")

        # Classificazione ISTITUTO dal registro (vocabolario chiuso, deterministico).
        # Serve a (a) iniettare la norma cardine in Fase 2 — separando istituti che
        # condividono il lessico (es. sequestro penale ex 321 c.p.p. vs confisca
        # antimafia ex 25 d.lgs. 159) — e (b) iniettare le sentenze pilota
        # groundabili in Fase 3.
        istituto = None
        try:
            _ist_matches = get_registry().match_query(
                f"{query} {questione_retrieval} {qualificazione_retrieval}"
            )
            istituto = _ist_matches[0][0] if _ist_matches else None
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"[S3 Seq] classificazione istituto fallita: {exc}")
        if istituto:
            logger.info(f"[S3 Seq] istituto classificato: {istituto.id!r} ({istituto.settore})")

        phase1 = PhaseResult(
            phase=1, name=_phase1_name,
            sections=sections_f1,
            sources_used=[],
            overall_confidence=conf_f1,
            gaps=data_f1.get("gaps", []),
            duration_s=time.monotonic() - t0,
            parse_ok=ok_f1,
            questione_retrieval=questione_retrieval,
            qualificazione_retrieval=qualificazione_retrieval,
            giurisprudenza_retrieval_varianti=giurisprudenza_retrieval_varianti,
            settore_giuridico=settore_giuridico,
        )
        completed_phases.append(phase1)
        logger.info(
            f"[S3 Seq] Fase 1 {_phase1_name}: {len(sections_f1)} sezioni, "
            f"ok={ok_f1}, t={phase1.duration_s:.1f}s"
        )
        yield phase1

        # ── Retrieval per Fase 2 (normativa + dottrina) ──────────────
        norm_sources: list[SearchResult] = []
        dott_sources: list[SearchResult] = []
        if phase_retriever is not None:
            import asyncio as _asyncio
            # Per query dottrinali, la dottrina interpretativa pesa di più nel
            # mix dei risultati (più top_k) — la norma resta comunque il
            # fondamento (Fase 2), non si inverte la priorità, si cambia solo
            # quanto supporto interpretativo viene raccolto.
            _dott_top_k = 6 if query_type == "doctrine" else 4
            try:
                norm_sources = await _asyncio.to_thread(
                    phase_retriever.retrieve_normativa,
                    questione_retrieval, 6, settore_giuridico, settore_confidence, query_type,
                )
            except Exception as exc:
                logger.warning(f"[S3 Seq] retrieval normativa fallito: {exc}")
            try:
                dott_sources = await _asyncio.to_thread(
                    phase_retriever.retrieve_dottrina,
                    questione_retrieval, _dott_top_k, settore_giuridico, settore_confidence, query_type,
                )
            except Exception as exc:
                logger.warning(f"[S3 Seq] retrieval dottrina fallito: {exc}")

        # Fallback: usa fonti normative dal packet iniziale S2
        if not norm_sources:
            norm_sources = [
                s for s in packet.sources
                if self._effective_layer(s) == "normativa"
            ]

        # Iniezione norma cardine dell'istituto (garantita, in cima): evita che
        # la norma di un istituto confondibile (es. art. 25 antimafia) scalzi
        # quella corretta (es. art. 321 c.p.p.) per collisione lessicale.
        if istituto and istituto.norme_urn:
            import asyncio as _asyncio
            _inj = await _asyncio.to_thread(
                fetch_sources_by_source_id, list(istituto.norme_urn), "normativa",
            )
            _existing = {s.source_id for s in norm_sources}
            _new = [s for s in _inj if s.source_id not in _existing]
            if _new:
                logger.info(
                    f"[S3 Seq] iniettate {len(_new)} norme cardine istituto {istituto.id!r}"
                )
                norm_sources = _new + norm_sources

        # Testo pieno per le fonti di fase (no-op se AIURA_FULLTEXT_CONTEXT=0
        # o se le fonti sono già arricchite dall'orchestrator dopo S2)
        await fetch_full_texts(norm_sources)
        await fetch_full_texts(dott_sources)

        # ── Fase 2: Normativa + Dottrina ──────────────────────────────
        t1 = time.monotonic()
        ctx_norm, ref_map_norm = self._format_phase_sources(norm_sources, corpus="normattiva")
        framing_summary = self._build_framing_summary(sections_f1, data_f1)

        # Sezione dottrina opzionale — presente solo se ci sono fonti.
        # I ref proseguono da quelli già usati per ctx_norm: univoci nel
        # prompt di questa chiamata (vedi _assign_refs).
        ctx_dott = ""
        ref_map_dott: dict[str, str] = {}
        if dott_sources:
            dott_texts = _source_texts_for_prompt(dott_sources, "dottrina")
            _next = max((int(r[1:]) for r in ref_map_norm.values()), default=0) + 1
            ref_map_dott, _ = _assign_refs(dott_sources, start=_next)
            dott_lines = ["DOTTRINA — cita SOLO il riferimento FN mostrato per l'INTERPRETAZIONE:", "=" * 60]
            for s, t in zip(dott_sources, dott_texts):
                dott_lines.extend(_format_source(ref_map_dott[s.source_id], s, t))
            dott_lines.append("=" * 60)
            ctx_dott = "\n".join(dott_lines) + "\n\n"

        ref_map_f2 = {**ref_map_norm, **ref_map_dott}
        _budget_f2 = _llm_settings.llm_max_tokens_fase2 - 80
        prompt_f2 = (
            f"{framing_summary}\n\n"
            f"{ctx_norm}\n\n"
            f"{ctx_dott}"
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            "Sulla base del framing sopra, produci FONTI_NORMATIVE e INTERPRETAZIONE.\n"
            "Per FONTI_NORMATIVE usa SOLO fonti dalla sezione FONTI PER QUESTA FASE.\n"
            "Per INTERPRETAZIONE puoi citare anche la DOTTRINA (se presente) a supporto "
            "dei criteri ermeneutici, con il relativo riferimento FN.\n"
            "Ogni claim DEVE citare il riferimento FN (es. F1) mostrato accanto alla "
            "fonte — NON inventare o ricostruire altri identificatori (URN, numeri, hash).\n"
            "VINCOLI STRINGENTI:\n"
            "- OGNI sezione: massimo 100 parole nel campo content\n"
            "- citations[]: massimo 3 elementi per sezione\n"
            f"- BUDGET TOKEN: genera il JSON in meno di {_budget_f2} token totali\n"
            "- NON annidare JSON dentro stringhe, NON usare blocchi ```json\n"
            "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido e completo, niente testo prima/dopo.\n"
        )
        raw_f2 = ""
        try:
            raw_f2 = await self._ollama.generate(
                prompt=prompt_f2, temperature=0.0,          # deterministico: riduce deriva sintattica
                max_tokens=_llm_settings.llm_max_tokens_fase2,
                system=_SYSTEM_PROMPT_NORMATIVA,
                n_ctx=_llm_settings.llm_n_ctx,
                n_batch=_llm_settings.llm_n_batch,
            )
        except Exception as exc:
            logger.warning(f"[S3 Seq Fase2] Ollama errore: {exc}")

        sections_f2, conf_f2, _, ok_f2 = self._parse_response(raw_f2 or "")
        phase2 = PhaseResult(
            phase=2, name="NORMATIVA",
            sections=sections_f2,
            sources_used=[s.source_id for s in norm_sources + dott_sources],
            overall_confidence=conf_f2,
            gaps=[],
            duration_s=time.monotonic() - t1,
            parse_ok=ok_f2,
            sources_metadata={s.source_id: s.metadata for s in norm_sources + dott_sources},
            ref_map=_invert_ref_map(ref_map_f2),
        )
        completed_phases.append(phase2)
        logger.info(
            f"[S3 Seq] Fase 2 NORMATIVA: {len(sections_f2)} sezioni, "
            f"fonti={len(norm_sources)}, ok={ok_f2}, t={phase2.duration_s:.1f}s"
        )
        yield phase2

        # ── Retrieval per Fase 3 ──────────────────────────────────────
        giuri_sources: list[SearchResult] = []
        if phase_retriever is not None:
            try:
                import asyncio as _asyncio
                giuri_sources = await _asyncio.to_thread(
                    phase_retriever.retrieve_giurisprudenza_multi,
                    phase1.giurisprudenza_retrieval_varianti,   # 1-3 formulazioni, vedi Fase 1
                    6,
                    settore_giuridico,
                    settore_confidence,
                )
            except Exception as exc:
                logger.warning(f"[S3 Seq] retrieval giurisprudenza fallito: {exc}")
        if not giuri_sources:
            giuri_sources = [
                s for s in packet.sources
                if self._effective_layer(s) == "giurisprudenza"
            ]

        # Round DEDICATO e separato per il massimario (digesti dei principi
        # delle sentenze pilota). Blocco proprio nel prompt — non compete per
        # gli slot della giurisprudenza (simmetrico a dottrina in Fase 2).
        mass_sources: list[SearchResult] = []
        if phase_retriever is not None:
            try:
                import asyncio as _asyncio
                mass_sources = await _asyncio.to_thread(
                    phase_retriever.retrieve_massimario,
                    qualificazione_retrieval, 3, settore_giuridico, settore_confidence,
                )
            except Exception as exc:
                logger.warning(f"[S3 Seq] retrieval massimario fallito: {exc}")

        # Iniezione sentenze pilota groundabili dell'istituto: il principio
        # cardine (es. Gubert sul terzo estraneo) con source_id REALE → citabile
        # senza allucinazione. Confluiscono nel blocco MASSIMARIO (in cima).
        if istituto:
            _pilot_ids = [p.source_id for p in istituto.sentenze_pilota if p.source_id]
            if _pilot_ids:
                import asyncio as _asyncio
                _inj = await _asyncio.to_thread(
                    fetch_sources_by_source_id, _pilot_ids, "massimario",
                )
                _existing = {s.source_id for s in giuri_sources + mass_sources}
                _new = [s for s in _inj if s.source_id not in _existing]
                if _new:
                    logger.info(
                        f"[S3 Seq] iniettati {len(_new)} piloti istituto {istituto.id!r}"
                    )
                    mass_sources = _new + mass_sources

        await fetch_full_texts(giuri_sources)
        await fetch_full_texts(mass_sources)

        # ── Fase 3: Giurisprudenza + Massimario ───────────────────────
        t2 = time.monotonic()
        # I ref proseguono da quelli già usati in Fase 2 (ref_map_f2): senza
        # questo "start=", _format_phase_sources riparte da F1 e collide con
        # i riferimenti di Fase 2 già mostrati all'avvocato — stesso token
        # "F1" risolve a fonti diverse in fasi diverse (bug scoperto perché
        # rompeva la sostituzione "F1"→fonte leggibile in humanize_refs).
        _next_f3 = max((int(r[1:]) for r in ref_map_f2.values()), default=0) + 1
        ctx_giuri, ref_map_giuri = self._format_phase_sources(
            giuri_sources, corpus="giurisprudenza", start=_next_f3,
        )

        # Blocco MASSIMARIO opzionale — presente solo se ci sono fonti.
        # I ref proseguono da quelli già usati per ctx_giuri.
        ctx_mass = ""
        ref_map_mass: dict[str, str] = {}
        if mass_sources:
            mass_texts = _source_texts_for_prompt(mass_sources, "massimario")
            _next = max((int(r[1:]) for r in ref_map_giuri.values()), default=0) + 1
            ref_map_mass, _ = _assign_refs(mass_sources, start=_next)
            mass_lines = [
                "MASSIMARIO — digesti dei principi consolidati (con la citazione "
                "della sentenza pilota); cita SOLO il riferimento FN a supporto del principio:",
                "=" * 60,
            ]
            for s, t in zip(mass_sources, mass_texts):
                mass_lines.extend(_format_source(ref_map_mass[s.source_id], s, t))
            mass_lines.append("=" * 60)
            ctx_mass = "\n".join(mass_lines) + "\n\n"

        ref_map_f3 = {**ref_map_giuri, **ref_map_mass}
        phase_context = self._build_phase_context(completed_phases)
        # Budget token più alto quando deve produrre anche lo step MASSIMARIO
        # (due step separati, non un riassunto unico — vedi _step_istruzione).
        _max_tokens_f3 = (
            int(_llm_settings.llm_max_tokens_fase3 * 1.4) if ctx_mass
            else _llm_settings.llm_max_tokens_fase3
        )
        _budget_f3 = _max_tokens_f3 - 80

        # GIURISPRUDENZA e MASSIMARIO sono due STEP separati con budget di
        # citazione indipendenti — non un unico step che li riassume insieme.
        # Altrimenti il modello, vincolato a poche citations[] totali, sceglie
        # le sentenze (più numerose) e il massimario/pilota dell'istituto
        # (spesso la sostanza della risposta su istituti confondibili, es.
        # il principio Gubert sul terzo estraneo) resta fuori per budget,
        # non per irrilevanza.
        if ctx_mass:
            _step_istruzione = (
                "Produci DUE step separati: GIURISPRUDENZA (analizza le sentenze) "
                "e MASSIMARIO (riporta il principio consolidato del blocco MASSIMARIO). "
                "Sono due fonti diverse con budget di citazione indipendenti: produci "
                "SEMPRE entrambi gli step, anche se hai già citato a sufficienza "
                "nell'altro — non saltare MASSIMARIO per aver già citato GIURISPRUDENZA.\n"
            )
            _vincoli_step = (
                "- GIURISPRUDENZA: massimo 120 parole, citations[] massimo 2 elementi\n"
                "- MASSIMARIO: massimo 100 parole, citations[] massimo 2 elementi\n"
            )
        else:
            _step_istruzione = "Produci il passo GIURISPRUDENZA analizzando le sentenze nel Packet.\n"
            _vincoli_step = "- GIURISPRUDENZA: massimo 120 parole nel campo content, citations[] massimo 3 elementi\n"

        prompt_f3 = (
            f"{phase_context}\n\n"
            f"{ctx_giuri}\n\n"
            f"{ctx_mass}"
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            f"{_step_istruzione}"
            "Ogni fonte citata DEVE citare il riferimento FN (es. F2) mostrato accanto "
            "alla fonte — NON inventare o ricostruire altri identificatori (URN, numeri, hash).\n"
            "VINCOLI:\n"
            f"{_vincoli_step}"
            f"- BUDGET TOKEN: il JSON DEVE terminare entro {_budget_f3} token\n"
            "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido e completo.\n"
        )
        raw_f3 = ""
        try:
            raw_f3 = await self._ollama.generate(
                prompt=prompt_f3, temperature=0.0,           # deterministico: vedi docstring
                max_tokens=_max_tokens_f3,
                system=_SYSTEM_PROMPT_GIURISPRUDENZA_SEQ,
                n_ctx=_llm_settings.llm_n_ctx,
                n_batch=_llm_settings.llm_n_batch,
            )
        except Exception as exc:
            logger.warning(f"[S3 Seq Fase3] Ollama errore: {exc}")

        sections_f3, conf_f3, _, ok_f3 = self._parse_response(raw_f3 or "")
        phase3_sources = giuri_sources + mass_sources
        phase3 = PhaseResult(
            phase=3, name="GIURISPRUDENZA",
            sections=sections_f3,
            sources_used=[s.source_id for s in phase3_sources],
            overall_confidence=conf_f3,
            gaps=[],
            duration_s=time.monotonic() - t2,
            parse_ok=ok_f3,
            sources_metadata={s.source_id: s.metadata for s in phase3_sources},
            ref_map=_invert_ref_map(ref_map_f3),
        )
        completed_phases.append(phase3)
        logger.info(
            f"[S3 Seq] Fase 3 GIURISPRUDENZA: {len(sections_f3)} sezioni, "
            f"fonti={len(giuri_sources)} giuri + {len(mass_sources)} massimario, "
            f"ok={ok_f3}, t={phase3.duration_s:.1f}s"
        )
        yield phase3

        # ── Fase 4: Sintesi ───────────────────────────────────────────
        phase4 = await self._generate_fase4(query, packet, completed_phases, query_type=query_type)
        yield phase4

    async def _generate_fase4(
        self,
        query: str,
        packet: ResearchPacket,
        completed_phases: list["PhaseResult"],
        corrective_note: str = "",
        query_type: str = "case",
    ) -> "PhaseResult":
        """
        Genera la Fase 4 (Sintesi). Estratto come metodo riusabile da
        analyze_sequential() per permettere un retry mirato (vedi
        regenerate_fase4) quando il Reviewer segnala citazioni ungrounded
        confinate a questa fase — senza richiedere un nuovo giro di
        retrieval né rigenerare le fasi precedenti, già corrette.

        query_type=="doctrine": usa lo skill di sintesi dottrinale — niente
        "nel caso concreto"/"rischio processuale"/"prove necessarie", che
        presuppongono un procedimento reale assente in una domanda teorica
        sull'istituto (es. "in quali casi è legittimo X").
        """
        t3 = time.monotonic()
        full_context = self._build_phase_context(completed_phases)
        _budget_f4 = _llm_settings.llm_max_tokens_fase4 - 80
        _is_doctrine = query_type == "doctrine"

        # Costruisce whitelist source_id dal packet per vincolare Fase 4
        _packet_source_ids = sorted({s.source_id for s in packet.sources if s.source_id})
        _source_ids_block = (
            "SOURCE_ID AMMESSI NEL CAMPO citations[] (usa SOLO questi — nessun altro):\n"
            + "\n".join(f"  - {sid}" for sid in _packet_source_ids)
        ) if _packet_source_ids else ""

        _istruzione_f4 = (
            "Sulla base dell'analisi sopra, produci SUSSUNZIONE, OBIEZIONI, CONCLUSIONE "
            "come regola generale dell'istituto — NON inventare un caso concreto: "
            "la domanda è teorica.\n"
            if _is_doctrine else
            "Sulla base dell'analisi sopra, produci SUSSUNZIONE, OBIEZIONI, CONCLUSIONE.\n"
            "Sii operativo e preciso. Usa 'VALUTAZIONE PERSONALE:' per valutazioni non grounded.\n"
        )
        prompt_f4 = (
            f"{full_context}\n\n"
            f"DOMANDA DELL'AVVOCATO: {query}\n\n"
            f"{corrective_note}"
            f"{_istruzione_f4}"
            "VINCOLI:\n"
            "- OGNI sezione: massimo 100 parole nel campo content\n"
            "- citations[]: massimo 2 elementi per sezione\n"
            "- Nel campo citations[] usa ESCLUSIVAMENTE i source_id della lista sotto\n"
            "- NON inventare source_id: se non è nella lista, ometti la citation\n"
            f"- BUDGET TOKEN: il JSON DEVE terminare entro {_budget_f4} token totali\n"
            f"{_source_ids_block}\n"
            "Rispondi ESCLUSIVAMENTE con un oggetto JSON valido e completo.\n"
        )
        raw_f4 = ""
        try:
            raw_f4 = await self._ollama.generate(
                prompt=prompt_f4, temperature=0.0,           # deterministico: vedi docstring
                max_tokens=_llm_settings.llm_max_tokens_fase4,
                system=_SYSTEM_PROMPT_SINTESI_DOTTRINA if _is_doctrine else _SYSTEM_PROMPT_SINTESI,
                n_ctx=_llm_settings.llm_n_ctx,
                n_batch=_llm_settings.llm_n_batch,
            )
        except Exception as exc:
            logger.warning(f"[S3 Seq Fase4] Ollama errore: {exc}")

        sections_f4, conf_f4, escalation_f4, ok_f4 = self._parse_response(raw_f4 or "")
        phase4 = PhaseResult(
            phase=4, name="SINTESI",
            sections=sections_f4,
            sources_used=[],
            overall_confidence=conf_f4,
            escalation_recommended=escalation_f4,
            gaps=[],
            duration_s=time.monotonic() - t3,
            parse_ok=ok_f4,
        )
        logger.info(
            f"[S3 Seq] Fase 4 SINTESI: {len(sections_f4)} sezioni, "
            f"escalation={escalation_f4}, ok={ok_f4}, t={phase4.duration_s:.1f}s"
        )
        return phase4

    async def regenerate_fase4(
        self,
        query: str,
        packet: ResearchPacket,
        completed_phases: list["PhaseResult"],
        ungrounded_ids: list[str],
        query_type: str = "case",
    ) -> "PhaseResult":
        """
        Retry mirato della Fase 4 dopo un verdetto RE_RETRIEVAL del Reviewer
        con citazioni ungrounded confinate alla Fase 4 (vedi orchestrator:
        chiamato solo quando nessuna citazione ungrounded proviene da Fase 2/3).

        Non ri-esegue retrieval: rigenera solo la sintesi con un'istruzione
        correttiva esplicita che elenca i source_id rifiutati dal Reviewer
        all'ultimo giro — a parità di temperature=0.0 e prompt identico la
        risposta sarebbe identica, quindi la correzione deve cambiare il
        prompt, non solo "riprovare".
        """
        corrective_note = (
            "ATTENZIONE — CORREZIONE OBBLIGATORIA: nel tentativo precedente hai "
            f"citato questi source_id NON validi (rifiutati dal Reviewer): "
            f"{', '.join(ungrounded_ids)}. Non riutilizzarli. Ometti la citation "
            "se non trovi un source_id valido in lista per quella claim.\n\n"
        )
        return await self._generate_fase4(
            query, packet, completed_phases, corrective_note, query_type=query_type,
        )

    # ------------------------------------------------------------------
    # analyze()  — entry point
    # ------------------------------------------------------------------

    async def analyze(
        self,
        query: str,
        packet: ResearchPacket,
        temperature: float = 0.10,
        max_tokens: int = 4500,
    ) -> AnalysisResult:
        """
        Genera analisi CoT sul Research Packet.

        Non solleva mai eccezioni: in caso di errore Ollama ritorna
        AnalysisResult vuoto con gaps esplicativi.
        """
        t0 = time.monotonic()

        if not packet.sources:
            return AnalysisResult(
                answer="",
                analysis_sections=[],
                overall_confidence="LOW",
                gaps=["Nessuna fonte nel Research Packet: impossibile analizzare."],
                llm_model=self._ollama.model,
                duration_s=time.monotonic() - t0,
                parse_ok=False,
            )

        prompt, ref_map = self._build_prompt(query, packet)

        try:
            raw = await self._ollama.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system=_SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.warning(f"[S3 Analyst] Ollama non disponibile: {exc}")
            return AnalysisResult(
                answer="",
                analysis_sections=[],
                overall_confidence="LOW",
                gaps=[f"LLM non disponibile ({type(exc).__name__}). Retrieval disponibile."],
                llm_model=self._ollama.model,
                duration_s=time.monotonic() - t0,
                parse_ok=False,
            )

        sections, confidence, escalation, parse_ok = self._parse_response(raw)
        answer = self._sections_to_answer(sections)

        if not parse_ok:
            logger.warning("[S3 Analyst] JSON non parsabile — risposta grezza usata")

        logger.info(
            f"[S3 Analyst] {len(sections)} sezioni, confidence={confidence}, "
            f"escalation={escalation}, parse_ok={parse_ok}, "
            f"t={time.monotonic() - t0:.1f}s"
        )

        return AnalysisResult(
            answer=answer,
            analysis_sections=sections,
            overall_confidence=confidence,
            escalation_recommended=escalation,
            gaps=[],
            llm_model=self._ollama.model,
            duration_s=time.monotonic() - t0,
            raw_response=raw,
            parse_ok=parse_ok,
            ref_map=_invert_ref_map(ref_map),
        )
