"""
Legal Drafter [S4] — genera atti e pareri formali da Research Packet.

Riceve il Research Packet (S2) e l'AnalysisResult (S3) come contesto.
Ogni citazione nel testo usa {{cite:source_id}} — render_citations() risolve
il marker nella citazione formale prima che il documento raggiunga l'avvocato.

Tipi di documento supportati:
    parere, citazione, comparsa, diffida, nota, contratto

Graceful degradation: mai eccezioni — errori Ollama restituiscono DraftResult
con document_text="" e parse_ok=False.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from loguru import logger

from aiura_legal.agents.ollama_client import OllamaClient
from aiura_legal.core.types import ResearchPacket, SearchResult


_SKILL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_drafter.md"
)

DISCLAIMER = (
    "Bozza generata con assistenza AI (AiUra LegalLab).\n"
    "Le citazioni normative sono state verificate sulla KB dello studio.\n"
    "L'avvocato deve verificare la vigenza delle fonti prima dell'uso processuale."
)

# Keyword per auto-detect tipo documento dalla query (ordine: più specifico prima)
_TYPE_KEYWORDS: dict[str, list[str]] = {
    "citazione":  ["atto di citazione", "citare in giudizio", "ricorso al tribunale"],
    "comparsa":   ["comparsa di risposta", "costituzione in giudizio", "comparsa"],
    "diffida":    ["diffida", "messa in mora", "diffidare"],
    "contratto":  ["bozza contrattuale", "schema di contratto", "clausol"],
    "nota":       ["nota legale", "lettera legale", "nota informativa"],
    "parere":     ["parere", "consulenza legale", "opinione legale"],
}

VALID_TYPES: frozenset[str] = frozenset(_TYPE_KEYWORDS)

# Struttura documento per tipo
_DOC_STRUCTURE: dict[str, str] = {
    "parere":    "Intestazione, Oggetto, Quesito, Svolgimento (con sezioni numerate), Conclusioni",
    "citazione": "Intestazione, Premessa in fatto, Motivi di diritto, Conclusioni, Valore della causa",
    "comparsa":  "Intestazione, Premessa, Eccezioni preliminari, Merito, Conclusioni",
    "diffida":   "Intestazione, Premessa, Contestazione, Richiesta, Termine, Avvertenze",
    "nota":      "Intestazione, Oggetto, Testo, Conclusioni",
    "contratto": "Intestazione, Premesse, Definizioni, Obbligazioni delle parti, Clausole finali",
}


# ---------------------------------------------------------------------------
# Caricamento system prompt dalla Pi Skill
# ---------------------------------------------------------------------------

def _load_system_prompt() -> str:
    if not _SKILL_PATH.exists():
        logger.warning(f"[S4] Pi Skill non trovata: {_SKILL_PATH}")
        return (
            "Sei un redattore legale italiano esperto. Genera documenti formali "
            "usando SOLO le fonti del Research Packet. "
            "Usa {{cite:source_id}} per ogni citazione normativa. "
            "Non includere il disclaimer AI — viene aggiunto automaticamente."
        )
    text = _SKILL_PATH.read_text(encoding="utf-8")
    # Rimuove il blocco frontmatter ---...---
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
    return text.strip()


_SYSTEM_PROMPT: str = _load_system_prompt()


# ---------------------------------------------------------------------------
# Tipi di output
# ---------------------------------------------------------------------------

@dataclass
class DraftResult:
    """Risultato della generazione documento di S4 Drafter."""

    document_type: str          # "parere" | "citazione" | "comparsa" | "diffida" | "nota" | "contratto"
    raw_text: str               # testo con {{cite:source_id}} markers
    rendered_text: str          # marker risolti in citazioni formali
    full_document: str          # rendered_text + disclaimer
    llm_model: str
    duration_s: float
    parse_ok: bool
    raw_response: str = field(default="", repr=False)


# ---------------------------------------------------------------------------
# DrafterAgent
# ---------------------------------------------------------------------------

class DrafterAgent:
    """
    S4 Legal Drafter.

    Costruisce il prompt con Research Packet + AnalysisResult come contesto,
    chiama Ollama e post-processa il documento (render citazioni + disclaimer).

    Utilizzo tipico:
        drafter = DrafterAgent()
        result = await drafter.draft(
            query="Parere su inadempimento contrattuale",
            packet=research_packet,
            analysis=analysis_result,
            document_type="parere",
        )
    """

    def __init__(self, ollama: Optional[OllamaClient] = None) -> None:
        self._ollama = ollama or OllamaClient()

    # ------------------------------------------------------------------
    # Rilevamento tipo documento
    # ------------------------------------------------------------------

    def detect_document_type(self, query: str) -> str:
        """
        Rileva il tipo di documento dalla query via keyword matching.
        Default: "parere".
        """
        q = query.lower()
        for dtype, keywords in _TYPE_KEYWORDS.items():
            if any(kw in q for kw in keywords):
                return dtype
        return "parere"

    @staticmethod
    def normalize_document_type(raw: str) -> str:
        """Normalizza e valida il tipo documento. Default 'parere' se non valido."""
        if not raw:
            return "parere"
        t = raw.strip().lower()
        return t if t in VALID_TYPES else "parere"

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def _build_packet_context(self, packet: ResearchPacket) -> str:
        """Serializza le fonti del Research Packet per il prompt S4."""
        if not packet.sources:
            return "RESEARCH PACKET: NESSUNA FONTE DISPONIBILE."

        lines = [
            "RESEARCH PACKET — usa SOLO questi source_id nelle citazioni:",
            "=" * 60,
        ]
        for i, s in enumerate(packet.sources, 1):
            meta = s.metadata or {}
            titolo   = meta.get("titolo", "")
            fonte    = meta.get("fonte", "")
            articolo = meta.get("articolo_num") or meta.get("articolo", "")
            lines.append(f"\n[{i}] source_id: {s.source_id}")
            if titolo:
                lines.append(f"    titolo:   {titolo}")
            if fonte:
                lines.append(f"    fonte:    {fonte}")
            if articolo:
                lines.append(f"    articolo: {articolo}")
            lines.append(f"    testo:    {s.snippet[:300]}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def _build_analysis_context(self, analysis_answer: str) -> str:
        """Serializza la risposta S3 per il contesto del Drafter."""
        if not analysis_answer:
            return "ANALISI S3: Non disponibile."
        # Tronca se troppo lunga (evita context overflow)
        text = analysis_answer[:2000]
        if len(analysis_answer) > 2000:
            text += "\n[... analisi troncata per lunghezza ...]"
        return f"ANALISI GIURIDICA (S3):\n{text}"

    def _build_prompt(
        self,
        query: str,
        packet: ResearchPacket,
        analysis_answer: str,
        document_type: str,
    ) -> str:
        """Assembla il prompt completo per S4."""
        packet_ctx = self._build_packet_context(packet)
        analysis_ctx = self._build_analysis_context(analysis_answer)
        structure = _DOC_STRUCTURE.get(document_type, "Struttura standard per documento legale")

        return (
            f"{packet_ctx}\n\n"
            f"{analysis_ctx}\n\n"
            f"QUESITO ORIGINALE: {query}\n\n"
            f"TIPO DOCUMENTO RICHIESTO: {document_type.upper()}\n"
            f"STRUTTURA: {structure}\n\n"
            "REGOLE OBBLIGATORIE:\n"
            "- Usa SOLO i source_id presenti nel Research Packet sopra\n"
            "- Per ogni citazione normativa nel testo scrivi {{cite:source_id}} "
            "(es: {{cite:CC_ART_1218}})\n"
            "- Non inventare articoli, sentenze o estremi non presenti nel Packet\n"
            "- Non includere il disclaimer AI: viene aggiunto automaticamente\n"
            "- Scrivi in italiano giuridico formale\n\n"
            "Genera il documento direttamente (nessun JSON, nessun commento prima o dopo).\n"
        )

    # ------------------------------------------------------------------
    # Citation rendering
    # ------------------------------------------------------------------

    @staticmethod
    def _format_citation(src: SearchResult) -> str:
        """Formatta una fonte in citazione leggibile per il documento."""
        meta = src.metadata or {}
        fonte    = meta.get("fonte", "")
        titolo   = meta.get("titolo", "")
        articolo = meta.get("articolo_num") or meta.get("articolo", "")

        if articolo and (titolo or fonte):
            label = titolo or fonte
            return f"{articolo} ({label})"
        if fonte:
            return f"({fonte})"
        return f"[{src.source_id}]"

    def render_citations(self, text: str, packet: ResearchPacket) -> str:
        """
        Risolve tutti i marker {{cite:source_id}} nel testo con citazioni formali.

        Esempio:
            {{cite:CC_ART_1218}} → "art. 1218 (Codice Civile)"
            {{cite:UNKNOWN_ID}}  → "[UNKNOWN_ID]"  (marker non in Packet)
        """
        cit_map = {
            src.source_id.upper(): self._format_citation(src)
            for src in packet.sources
        }

        def _replace(m: re.Match) -> str:
            sid = m.group(1).strip().upper()
            return cit_map.get(sid, f"[{m.group(1).strip()}]")

        return re.sub(r"\{\{cite:([^}]+)\}\}", _replace, text)

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_response(raw: str) -> tuple[str, bool]:
        """
        Pulisce la risposta LLM.
        Ritorna (cleaned_text, parse_ok).
        parse_ok=False se il testo risulta vuoto.
        """
        text = raw.strip()
        if not text:
            return "", False

        # Rimuove eventuali code fence markdown accidentali
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text.rstrip())
        text = text.strip()

        return text, bool(text)

    # ------------------------------------------------------------------
    # draft() — entry point
    # ------------------------------------------------------------------

    async def draft(
        self,
        query: str,
        packet: ResearchPacket,
        analysis_answer: str = "",
        document_type: Optional[str] = None,
        temperature: float = 0.30,
        max_tokens: int = 4000,
    ) -> DraftResult:
        """
        Genera il documento legale formale.

        Non solleva mai eccezioni: errori Ollama → DraftResult con parse_ok=False.

        Args:
            query:           quesito originale dell'avvocato
            packet:          Research Packet da S2
            analysis_answer: testo analisi S3 (stringa, può essere vuota)
            document_type:   tipo documento (auto-detect da query se None)
            temperature:     0.30 per stile formale ma vario
            max_tokens:      4000 (documenti possono essere lunghi)
        """
        t0 = time.monotonic()

        # Determina tipo documento
        dtype = self.normalize_document_type(document_type or "")
        if not document_type:
            dtype = self.detect_document_type(query)
        logger.info(f"[S4 Drafter] tipo={dtype}, query={query[:50]!r}")

        # Fallback se nessuna fonte disponibile
        if not packet.sources:
            logger.warning("[S4 Drafter] Research Packet vuoto — draft non possibile")
            return DraftResult(
                document_type=dtype,
                raw_text="",
                rendered_text="",
                full_document="",
                llm_model=self._ollama.model,
                duration_s=round(time.monotonic() - t0, 3),
                parse_ok=False,
            )

        prompt = self._build_prompt(query, packet, analysis_answer, dtype)

        # Chiamata Ollama
        try:
            raw = await self._ollama.generate(
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                system=_SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.warning(f"[S4 Drafter] Ollama non disponibile: {exc}")
            return DraftResult(
                document_type=dtype,
                raw_text="",
                rendered_text="",
                full_document="",
                llm_model=self._ollama.model,
                duration_s=round(time.monotonic() - t0, 3),
                parse_ok=False,
                raw_response="",
            )

        # Post-processing
        raw_text, parse_ok = self._parse_response(raw)
        if not parse_ok:
            logger.warning("[S4 Drafter] Risposta Ollama vuota o non parsabile")

        rendered_text = self.render_citations(raw_text, packet)
        full_document = f"{rendered_text}\n\n---\n{DISCLAIMER}" if rendered_text else ""

        duration = round(time.monotonic() - t0, 3)
        logger.info(
            f"[S4 Drafter] OK: tipo={dtype}, chars={len(rendered_text)}, "
            f"parse_ok={parse_ok}, t={duration:.1f}s"
        )

        return DraftResult(
            document_type=dtype,
            raw_text=raw_text,
            rendered_text=rendered_text,
            full_document=full_document,
            llm_model=self._ollama.model,
            duration_s=duration,
            parse_ok=parse_ok,
            raw_response=raw,
        )
