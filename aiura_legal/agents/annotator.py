"""
Legal Annotator [S6] — Document Intelligence asincrona (Workflow B).

Analizza un documento già ingerito e produce annotazioni strutturate per sezione.
Usa Ollama (qwen2.5:7b) con sistema prompt da .pi/skills/legal_annotator.md.

Tipi di annotazione:
    COMMENTO_NORMATIVO   — clausola collegata a norma specifica
    RISCHIO_RILEVATO     — rischio legale ALTO/MEDIO/BASSO con fonte
    SUGGERIMENTO         — testo alternativo più tutelante
    CROSS_REF_INTERNO    — conflitto tra sezioni dello stesso documento
    LACUNA_NORMATIVA     — norma non trovata in KB, verifica manuale

Citation Contract: ogni annotazione con norma/sentenza usa source_id dal
Research Packet. Se non trovata → usa LACUNA_NORMATIVA (mai invenzione).

Graceful degradation: mai eccezioni — errori Ollama → AnnotationResult
con parse_ok=False e annotazioni vuote.
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
from aiura_legal.core.types import ResearchPacket


_SKILL_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / ".pi" / "skills" / "legal_annotator.md"
)

# Tipi di annotazione validi
ANNOTATION_TYPES = frozenset({
    "COMMENTO_NORMATIVO",
    "RISCHIO_RILEVATO",
    "SUGGERIMENTO",
    "CROSS_REF_INTERNO",
    "LACUNA_NORMATIVA",
})

# Livelli di rischio validi
RISK_LEVELS = frozenset({"ALTO", "MEDIO", "BASSO"})

# Lunghezza massima di ogni sezione (caratteri) inviata a Ollama
_SECTION_MAX_CHARS = 1200

# Testo minimo per considerare una sezione "significativa"
_SECTION_MIN_CHARS = 50


# ---------------------------------------------------------------------------
# Caricamento system prompt dalla Pi Skill
# ---------------------------------------------------------------------------

def _load_system_prompt() -> str:
    if not _SKILL_PATH.exists():
        logger.warning(f"[S6] Pi Skill non trovata: {_SKILL_PATH}")
        return (
            "Sei un analista legale italiano. Annota i documenti usando SOLO le "
            "fonti del Research Packet. Citation Contract inviolabile: "
            "se manca la fonte usa LACUNA_NORMATIVA."
        )
    text = _SKILL_PATH.read_text(encoding="utf-8")
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.DOTALL)
    return text.strip()


_SYSTEM_PROMPT: str = _load_system_prompt()


# ---------------------------------------------------------------------------
# Tipi di output
# ---------------------------------------------------------------------------

@dataclass
class Annotation:
    """Singola annotazione su una sezione del documento."""
    section: str                          # es. "§1", "§3"
    annotation_type: str                  # uno di ANNOTATION_TYPES
    text: str                             # descrizione dell'annotazione
    level: str = ""                       # ALTO | MEDIO | BASSO (solo RISCHIO_RILEVATO)
    source_citations: list[str] = field(default_factory=list)
    suggested_replacement: str = ""       # solo per SUGGERIMENTO


@dataclass
class AnnotationResult:
    """Risultato completo dell'annotazione S6 su un documento."""
    document_id: str
    annotations: list[Annotation]
    summary: dict[str, int]               # {tipo: count}
    overall_risk: str                     # ALTO | MEDIO | BASSO | NESSUNO
    sections_processed: int
    llm_model: str
    duration_s: float
    parse_ok: bool
    raw_responses: list[str] = field(default_factory=list, repr=False)


# ---------------------------------------------------------------------------
# AnnotatorAgent
# ---------------------------------------------------------------------------

class AnnotatorAgent:
    """
    S6 Legal Annotator.

    Divide il documento in sezioni, chiama Ollama su ciascuna (fino a
    max_sections), aggrega le annotazioni e calcola il rischio complessivo.

    Utilizzo tipico:
        agent = AnnotatorAgent()
        result = await agent.annotate(
            document_text=text,
            document_id=doc_id,
            packet=research_packet,
            max_sections=10,
        )
    """

    def __init__(self, ollama: Optional[OllamaClient] = None) -> None:
        self._ollama = ollama or OllamaClient()

    # ------------------------------------------------------------------
    # Splitting del documento in sezioni
    # ------------------------------------------------------------------

    @staticmethod
    def split_sections(
        text: str,
        max_sections: int = 10,
        max_chars: int = _SECTION_MAX_CHARS,
    ) -> list[tuple[str, str]]:
        """
        Divide il testo in sezioni etichettate (§1, §2, …).

        Strategia:
          1. Split su doppio-newline (paragrafi naturali)
          2. Raggruppa paragrafi finché non superano max_chars
          3. Tronca a max_sections

        Returns:
            Lista di tuple (section_id, text)
        """
        # Normalizza fine riga e split su paragrafi
        paragraphs = [p.strip() for p in re.split(r"\n{2,}", text.strip()) if p.strip()]

        sections: list[tuple[str, str]] = []
        current_chunks: list[str] = []
        current_len = 0

        for para in paragraphs:
            if current_len + len(para) > max_chars and current_chunks:
                # Chiudi la sezione corrente
                label = f"§{len(sections) + 1}"
                sections.append((label, "\n\n".join(current_chunks)))
                current_chunks = []
                current_len = 0

            current_chunks.append(para)
            current_len += len(para)

        # Flush dell'ultima sezione
        if current_chunks:
            label = f"§{len(sections) + 1}"
            sections.append((label, "\n\n".join(current_chunks)))

        # Filtra sezioni troppo corte + limita a max_sections
        sections = [
            (sid, txt) for sid, txt in sections
            if len(txt) >= _SECTION_MIN_CHARS
        ][:max_sections]

        return sections

    # ------------------------------------------------------------------
    # Prompt building
    # ------------------------------------------------------------------

    def _build_packet_context(self, packet: ResearchPacket) -> str:
        """Serializza le fonti del Research Packet per il prompt."""
        if not packet.sources:
            return "RESEARCH PACKET: NESSUNA FONTE DISPONIBILE."

        lines = ["RESEARCH PACKET — usa SOLO questi source_id nelle annotazioni:"]
        for i, s in enumerate(packet.sources[:10], 1):   # al massimo 10 fonti
            meta = s.metadata or {}
            titolo   = meta.get("titolo", "")
            articolo = meta.get("articolo_num") or meta.get("articolo", "")
            lines.append(f"  [{i}] {s.source_id}" +
                         (f" — {articolo}" if articolo else "") +
                         (f" ({titolo})" if titolo else ""))
        return "\n".join(lines)

    def _build_prompt(
        self,
        section_id: str,
        section_text: str,
        packet: ResearchPacket,
    ) -> str:
        """Assembla il prompt per l'annotazione di una singola sezione."""
        packet_ctx = self._build_packet_context(packet)
        return (
            f"{packet_ctx}\n\n"
            f"SEZIONE {section_id} DEL DOCUMENTO:\n"
            "─" * 40 + "\n"
            f"{section_text}\n"
            "─" * 40 + "\n\n"
            "Analizza questa sezione e genera annotazioni.\n"
            "Usa SOLO i source_id presenti nel Research Packet sopra.\n"
            "Se identifichi un rischio/norma senza fonte → usa LACUNA_NORMATIVA.\n\n"
            "Rispondi ESCLUSIVAMENTE in JSON valido:\n"
            '{"annotations": [\n'
            '  {"section": "' + section_id + '",\n'
            '   "type": "RISCHIO_RILEVATO|COMMENTO_NORMATIVO|SUGGERIMENTO|CROSS_REF_INTERNO|LACUNA_NORMATIVA",\n'
            '   "level": "ALTO|MEDIO|BASSO",\n'
            '   "text": "...",\n'
            '   "source_citations": ["source_id_dal_packet"],\n'
            '   "suggested_replacement": "..."\n'
            '  }\n'
            "]}\n"
            'Se la sezione non contiene nulla di rilevante → {"annotations": []}.\n'
            "Nessun testo prima o dopo il JSON.\n"
        )

    # ------------------------------------------------------------------
    # Response parsing
    # ------------------------------------------------------------------

    def _extract_json(self, raw: str) -> Optional[dict]:
        """Estrae il primo oggetto JSON valido dalla risposta LLM."""
        for pattern in [
            r"```json\s*(\{.*?\})\s*```",
            r"```\s*(\{.*?\})\s*```",
            r"(\{.*\})",
        ]:
            m = re.search(pattern, raw, re.DOTALL)
            if m:
                try:
                    return json.loads(m.group(1))
                except json.JSONDecodeError:
                    continue
        return None

    def _parse_section_response(
        self, raw: str, section_id: str
    ) -> list[Annotation]:
        """
        Parsa la risposta Ollama per una sezione.
        Ritorna lista di Annotation (vuota se JSON malformato o nessuna annotazione).
        """
        data = self._extract_json(raw)
        if data is None:
            logger.warning(f"[S6] JSON non parsabile per {section_id}")
            return []

        raw_annotations = data.get("annotations", [])
        if not isinstance(raw_annotations, list):
            return []

        annotations: list[Annotation] = []
        for item in raw_annotations:
            if not isinstance(item, dict):
                continue

            ann_type = str(item.get("type", "")).upper()
            if ann_type not in ANNOTATION_TYPES:
                continue

            text = str(item.get("text", "")).strip()
            if not text:
                continue

            level = str(item.get("level", "")).upper()
            if level not in RISK_LEVELS:
                level = ""

            citations = item.get("source_citations", [])
            if not isinstance(citations, list):
                citations = []
            citations = [str(c) for c in citations if c]

            annotations.append(Annotation(
                section=str(item.get("section", section_id)),
                annotation_type=ann_type,
                text=text,
                level=level,
                source_citations=citations,
                suggested_replacement=str(item.get("suggested_replacement", "")),
            ))

        return annotations

    # ------------------------------------------------------------------
    # Calcolo rischio complessivo
    # ------------------------------------------------------------------

    @staticmethod
    def compute_overall_risk(annotations: list[Annotation]) -> str:
        """
        Calcola il rischio complessivo del documento.
        - ALTO se almeno un RISCHIO_RILEVATO di livello ALTO
        - MEDIO se RISCHIO_RILEVATO MEDIO (e nessun ALTO)
        - BASSO se solo BASSO
        - NESSUNO se nessun RISCHIO_RILEVATO
        """
        risk_levels_found: set[str] = set()
        for ann in annotations:
            if ann.annotation_type == "RISCHIO_RILEVATO" and ann.level in RISK_LEVELS:
                risk_levels_found.add(ann.level)

        if "ALTO" in risk_levels_found:
            return "ALTO"
        if "MEDIO" in risk_levels_found:
            return "MEDIO"
        if "BASSO" in risk_levels_found:
            return "BASSO"
        return "NESSUNO"

    @staticmethod
    def compute_summary(annotations: list[Annotation]) -> dict[str, int]:
        """Conta le annotazioni per tipo."""
        summary: dict[str, int] = {}
        for ann in annotations:
            summary[ann.annotation_type] = summary.get(ann.annotation_type, 0) + 1
        return summary

    # ------------------------------------------------------------------
    # annotate() — entry point
    # ------------------------------------------------------------------

    async def annotate(
        self,
        document_text: str,
        document_id: str,
        packet: ResearchPacket,
        max_sections: int = 10,
        temperature: float = 0.15,
        max_tokens: int = 3000,
    ) -> AnnotationResult:
        """
        Annota un documento intero.

        Divide il testo in sezioni, chiama Ollama per ciascuna (≤ max_sections),
        aggrega le annotazioni e calcola il rischio complessivo.

        Non solleva mai eccezioni: errori Ollama → AnnotationResult con
        parse_ok=False e liste vuote.

        Args:
            document_text:  testo completo del documento
            document_id:    identificatore del documento (per il risultato)
            packet:         Research Packet con le fonti validate da S2
            max_sections:   numero massimo di sezioni da processare (default 10)
            temperature:    0.15 per annotazioni precise e coerenti
            max_tokens:     3000 per sezione
        """
        t0 = time.monotonic()

        if not document_text.strip():
            logger.warning(f"[S6] Documento vuoto: {document_id}")
            return AnnotationResult(
                document_id=document_id,
                annotations=[],
                summary={},
                overall_risk="NESSUNO",
                sections_processed=0,
                llm_model=self._ollama.model,
                duration_s=round(time.monotonic() - t0, 3),
                parse_ok=False,
            )

        sections = self.split_sections(document_text, max_sections=max_sections)
        logger.info(
            f"[S6] Annotazione documento={document_id!r}: "
            f"{len(sections)} sezioni (max={max_sections})"
        )

        all_annotations: list[Annotation] = []
        raw_responses: list[str] = []
        parse_errors = 0

        for section_id, section_text in sections:
            prompt = self._build_prompt(section_id, section_text, packet)
            try:
                raw = await self._ollama.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system=_SYSTEM_PROMPT,
                )
            except Exception as exc:
                logger.warning(f"[S6] Ollama errore su {section_id}: {exc}")
                parse_errors += 1
                raw = ""

            raw_responses.append(raw)
            section_annotations = self._parse_section_response(raw, section_id)
            all_annotations.extend(section_annotations)

            logger.debug(
                f"[S6] {section_id}: {len(section_annotations)} annotazioni"
            )

        summary = self.compute_summary(all_annotations)
        overall_risk = self.compute_overall_risk(all_annotations)
        parse_ok = parse_errors < len(sections)  # ok se almeno una sezione ok

        duration = round(time.monotonic() - t0, 3)
        logger.info(
            f"[S6] Completato: {len(all_annotations)} annotazioni, "
            f"rischio={overall_risk}, t={duration:.1f}s, "
            f"parse_errors={parse_errors}/{len(sections)}"
        )

        return AnnotationResult(
            document_id=document_id,
            annotations=all_annotations,
            summary=summary,
            overall_risk=overall_risk,
            sections_processed=len(sections),
            llm_model=self._ollama.model,
            duration_s=duration,
            parse_ok=parse_ok,
            raw_responses=raw_responses,
        )
