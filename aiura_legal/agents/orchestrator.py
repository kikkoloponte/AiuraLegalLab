"""
LegalOrchestrator — catena S1 → S2 → S3 → S5.

S0  Routing:      programmatico su QueryIntent (nessun LLM overhead)
S1  Clarifier:    ClarifierAgent — valuta se la query è ambigua (max 2 turni)
S2  Retrieval:    HybridRetriever — BM25 + Vector + CrossEncoder
S3  Analysis:     AnalystAgent — CoT via Ollama qwen2.5:7b
S5  Review:       CitationReviewer — rule-based grounding check

Graceful degradation:
  Se Ollama non disponibile → S1 salta (proceeds), S3 returns answer=""
  Se clarification_turn ≥ 2  → S1 salta sempre (proceed)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from loguru import logger

from aiura_legal.agents.analyst import AnalysisResult, AnalysisSection, AnalystAgent, PhaseResult
from aiura_legal.agents.clarifier import ClarificationResult, ClarifierAgent
from aiura_legal.agents.drafter import DraftResult, DrafterAgent
from aiura_legal.agents.ollama_client import OllamaClient
from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever, _BIFASICO_INTENTS
from aiura_legal.core.retrieval.phase_retriever import PhaseRetriever
from aiura_legal.core.reviewer.reviewer import CitationReviewer
from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult


# ---------------------------------------------------------------------------
# Helper: strutture vuote per early-return da S1
# ---------------------------------------------------------------------------

def _empty_packet(query: str, intent: QueryIntent) -> ResearchPacket:
    return ResearchPacket(
        query_original=query,
        query_intent=intent,
        sources=[],
        retrieval_confidence="LOW",
        gaps=["In attesa di chiarimento dalla query."],
    )


def _empty_analysis(llm_model: str = "") -> AnalysisResult:
    return AnalysisResult(
        answer="",
        analysis_sections=[],
        overall_confidence="LOW",
        gaps=["Analisi non eseguita: in attesa di chiarimento."],
        llm_model=llm_model,
        parse_ok=False,
    )


# ---------------------------------------------------------------------------
# Risultato orchestratore
# ---------------------------------------------------------------------------

@dataclass
class OrchestratorResult:
    """Risultato completo della catena S1→S2→S3→S5."""

    # ── Input ──────────────────────────────────────────────────────────
    query: str
    workspace: str
    intent: str

    # ── S2 ─────────────────────────────────────────────────────────────
    packet: ResearchPacket

    # ── S3 ─────────────────────────────────────────────────────────────
    analysis: AnalysisResult

    # ── Mode ──────────────────────────────────────────────────────────
    mode: str = "standard"

    # ── S3 deep (opzionale) ────────────────────────────────────────────
    analysis_fase_1: Optional[AnalysisResult] = None
    analysis_fase_2: Optional[AnalysisResult] = None

    # ── S4 Drafter (opzionale) ─────────────────────────────────────────
    draft: Optional[DraftResult] = None

    # ── S5 ─────────────────────────────────────────────────────────────
    reviewer_verdict: str = "PASS"
    reviewer_action: str = "DELIVER"
    reviewer_warnings: list[str] = field(default_factory=list)

    # ── S1 Clarification ───────────────────────────────────────────────
    clarification_needed: bool = False
    clarification_question: Optional[str] = None
    clarification_missing_element: Optional[str] = None

    # ── Timing ─────────────────────────────────────────────────────────
    duration_s1_s: float = 0.0
    duration_retrieval_s: float = 0.0
    duration_llm_s: float = 0.0
    duration_total_s: float = 0.0

    # ── Properties ─────────────────────────────────────────────────────
    @property
    def answer(self) -> str:
        return self.analysis.answer

    @property
    def sources(self) -> list[SearchResult]:
        return self.packet.sources

    @property
    def llm_available(self) -> bool:
        return bool(self.analysis.answer)

    @property
    def retrieval_confidence(self) -> str:
        return self.packet.retrieval_confidence

    @property
    def gaps(self) -> list[str]:
        return self.packet.gaps + self.analysis.gaps


# ---------------------------------------------------------------------------
# Orchestratore
# ---------------------------------------------------------------------------

class LegalOrchestrator:
    """
    Coordina la catena degli agenti AiUra per una singola query legale.

    Costruzione tipica (in FastAPI):
        orch = LegalOrchestrator(retriever, ollama, enable_clarifier=True)
        result = await orch.run(query="...", workspace="normattiva")

    Se enable_clarifier=False (o Ollama assente): S1 viene saltato.
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        ollama: Optional[OllamaClient] = None,
        reviewer: Optional[CitationReviewer] = None,
        enable_clarifier: bool = True,
        enable_drafter: bool = True,
    ) -> None:
        _ollama = ollama or OllamaClient()
        self._analyst = AnalystAgent(_ollama)
        self._clarifier: Optional[ClarifierAgent] = (
            ClarifierAgent(_ollama) if enable_clarifier else None
        )
        self._drafter: Optional[DrafterAgent] = (
            DrafterAgent(_ollama) if enable_drafter else None
        )
        self._retriever = retriever
        self._phase_retriever = PhaseRetriever(retriever)
        self._reviewer = reviewer or CitationReviewer()

    # ------------------------------------------------------------------
    # run()
    # ------------------------------------------------------------------

    async def run(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        valid_on: Optional[date] = None,
        chunk_filter: Optional[dict] = None,
        workspace: str = "default",
        # S1 Clarifier
        clarification_turn: int = 0,
        clarification_context: Optional[str] = None,
        # S4 Drafter
        draft_type: Optional[str] = None,
        # Mode
        mode: str = "standard",
    ) -> OrchestratorResult:
        """
        Esegue la catena S1 → S2 → S3 → S5.
        Non solleva mai eccezioni — gestisce tutti gli errori internamente.

        Args:
            query:                testo della query
            intent:               QueryIntent classificato dal client
            valid_on:             data di riferimento per vigenza norme
            chunk_filter:         filtro subset chunk (es. {"corpus": "normattiva"})
            workspace:            nome workspace (per logging e response)
            clarification_turn:   0=prima volta, 1=con contesto, ≥2=procedi sempre
            clarification_context: risposta dell'utente al turno precedente
        """
        t_total = time.monotonic()
        llm_model = self._analyst._ollama.model

        # ── S1 Clarifier ───────────────────────────────────────────────
        duration_s1 = 0.0
        if self._clarifier and clarification_turn < 2:
            t0 = time.monotonic()
            logger.info(
                f"[Orchestrator] S1 clarifier — turn={clarification_turn}, "
                f"query={query[:50]!r}"
            )
            clarification = await self._clarifier.assess(
                query=query,
                turn_number=clarification_turn,
                context=clarification_context,
            )
            duration_s1 = time.monotonic() - t0

            if clarification.needs_clarification:
                logger.info(
                    f"[Orchestrator] S1 → chiarimento richiesto: "
                    f"missing={clarification.missing_element!r}, "
                    f"question={clarification.question_to_user!r}"
                )
                return OrchestratorResult(
                    query=query,
                    workspace=workspace,
                    intent=intent.value,
                    packet=_empty_packet(query, intent),
                    analysis=_empty_analysis(llm_model),
                    clarification_needed=True,
                    clarification_question=clarification.question_to_user,
                    clarification_missing_element=clarification.missing_element,
                    duration_s1_s=round(duration_s1, 3),
                    duration_total_s=round(time.monotonic() - t_total, 3),
                )
            else:
                logger.info("[Orchestrator] S1 → query sufficiente, procedo con S2")
        elif clarification_turn >= 2:
            logger.info("[Orchestrator] S1 saltato (turn >= 2 — defaults applicati)")

        # ── S2 Retrieval ───────────────────────────────────────────────
        t0 = time.monotonic()
        logger.info(
            f"[Orchestrator] S2 retrieval — intent={intent.value}, "
            f"query={query[:60]!r}"
        )
        import asyncio as _asyncio
        if intent in _BIFASICO_INTENTS:
            packet = await _asyncio.to_thread(
                self._retriever.build_research_packet_bifasico,
                query=query,
                intent=intent,
                valid_on=valid_on,
            )
        else:
            packet = await _asyncio.to_thread(
                self._retriever.build_research_packet,
                query=query,
                intent=intent,
                valid_on=valid_on,
                chunk_filter=chunk_filter,
            )
        duration_retrieval = time.monotonic() - t0
        logger.info(
            f"[Orchestrator] S2 done: {len(packet.sources)} fonti, "
            f"confidence={packet.retrieval_confidence}, t={duration_retrieval:.2f}s"
        )

        # ── S3 Analysis ────────────────────────────────────────────────
        analysis_fase_1: Optional[AnalysisResult] = None
        analysis_fase_2: Optional[AnalysisResult] = None

        if mode == "deep":
            logger.info("[Orchestrator] S3 deep mode (Fase 1 + Fase 2) …")
            analysis_fase_1, analysis_fase_2 = await self._analyst.analyze_deep(
                query, packet
            )
            # analysis principale = fase1 + fase2 merged (per backward compat S5)
            merged_sections = (
                (analysis_fase_1.analysis_sections if analysis_fase_1 else []) +
                (analysis_fase_2.analysis_sections if analysis_fase_2 else [])
            )
            merged_answer = "\n\n".join(filter(None, [
                analysis_fase_1.answer if analysis_fase_1 else "",
                analysis_fase_2.answer if analysis_fase_2 else "",
            ]))
            analysis = AnalysisResult(
                answer=merged_answer,
                analysis_sections=merged_sections,
                overall_confidence=(
                    analysis_fase_2.overall_confidence if analysis_fase_2
                    else (analysis_fase_1.overall_confidence if analysis_fase_1 else "LOW")
                ),
                escalation_recommended=(
                    analysis_fase_2.escalation_recommended if analysis_fase_2 else False
                ),
                gaps=(
                    (analysis_fase_1.gaps if analysis_fase_1 else []) +
                    (analysis_fase_2.gaps if analysis_fase_2 else [])
                ),
                llm_model=self._analyst._ollama.model,
                duration_s=(
                    (analysis_fase_1.duration_s if analysis_fase_1 else 0) +
                    (analysis_fase_2.duration_s if analysis_fase_2 else 0)
                ),
                parse_ok=(
                    (analysis_fase_1.parse_ok if analysis_fase_1 else False) or
                    (analysis_fase_2.parse_ok if analysis_fase_2 else False)
                ),
            )
            logger.info(
                f"[Orchestrator] S3 deep done: "
                f"fase1={len(analysis_fase_1.analysis_sections) if analysis_fase_1 else 0} sezioni, "
                f"fase2={len(analysis_fase_2.analysis_sections) if analysis_fase_2 else 0} sezioni"
            )
        else:
            logger.info("[Orchestrator] S3 analysis (Ollama CoT) …")
            analysis = await self._analyst.analyze(query, packet)
            logger.info(
                f"[Orchestrator] S3 done: llm_ok={analysis.parse_ok}, "
                f"sections={len(analysis.analysis_sections)}, t={analysis.duration_s:.1f}s"
            )

        # ── S4 Drafter (opzionale) ────────────────────────────────────
        draft: Optional[DraftResult] = None
        duration_draft = 0.0
        if draft_type and self._drafter:
            logger.info(f"[Orchestrator] S4 drafter — tipo={draft_type!r}")
            t_d = time.monotonic()
            try:
                draft = await self._drafter.draft(
                    query=query,
                    packet=packet,
                    analysis_answer=analysis.answer,
                    document_type=draft_type,
                )
            except Exception as exc:
                logger.warning(f"[Orchestrator] S4 Drafter errore: {exc}")
                draft = None
            duration_draft = time.monotonic() - t_d
            logger.info(
                f"[Orchestrator] S4 done: parse_ok={draft.parse_ok if draft else False}, "
                f"t={duration_draft:.1f}s"
            )

        # ── S5 Review ──────────────────────────────────────────────────
        # Se esiste un draft, S5 verifica il testo renderizzato del documento;
        # altrimenti verifica la risposta S3 (comportamento originale).
        if draft and draft.rendered_text:
            text_to_review = draft.rendered_text
        else:
            text_to_review = analysis.answer or " ".join(
                s.source_id for s in packet.sources
            )

        # Aggiunge i source_id citati nelle analysis_sections (struttura JSON).
        # Il testo dell'answer non li contiene esplicitamente, ma S5 deve
        # comunque verificare che ogni source_id usato nelle citations sia
        # presente nel Research Packet.
        cited_section_ids = [
            cit["source_id"]
            for sec in analysis.analysis_sections
            for cit in sec.citations
            if isinstance(cit, dict) and cit.get("source_id")
        ]
        if cited_section_ids:
            text_to_review = text_to_review + "\n" + " ".join(cited_section_ids)

        review = self._reviewer.verify(
            response_text=text_to_review,
            research_packet=packet,
            reference_date=valid_on,
        )
        logger.info(
            f"[Orchestrator] S5 review: verdict={review.verdict}, "
            f"action={review.action}, warnings={len(review.warnings)}"
        )

        return OrchestratorResult(
            query=query,
            workspace=workspace,
            intent=intent.value,
            mode=mode,
            packet=packet,
            analysis=analysis,
            analysis_fase_1=analysis_fase_1,
            analysis_fase_2=analysis_fase_2,
            draft=draft,
            reviewer_verdict=review.verdict,
            reviewer_action=review.action,
            reviewer_warnings=review.warnings,
            clarification_needed=False,
            duration_s1_s=round(duration_s1, 3),
            duration_retrieval_s=round(duration_retrieval, 3),
            duration_llm_s=round(analysis.duration_s + duration_draft, 3),
            duration_total_s=round(time.monotonic() - t_total, 3),
        )

    # ------------------------------------------------------------------
    # run_sequential()  — async generator per SSE streaming fase per fase
    # ------------------------------------------------------------------

    async def run_sequential(
        self,
        query: str,
        intent: QueryIntent = QueryIntent.FATTISPECIE_ANALYSIS,
        valid_on: Optional[date] = None,
        chunk_filter: Optional[dict] = None,
        workspace: str = "default",
        clarification_turn: int = 0,
        clarification_context: Optional[str] = None,
    ):
        """
        Esegue il Sequential IQRAC emettendo eventi man mano che ogni fase completa.

        Yields dict con tipo evento:
          {"event": "clarification_needed", "question": str}
          {"event": "retrieval_done", "sources_count": int, "confidence": str}
          {"event": "phase_complete", "phase": PhaseResult}
          {"event": "review_done", "verdict": str, "action": str, "warnings": list}
          {"event": "error", "message": str}

        Non solleva mai eccezioni — tutti gli errori vengono emessi come event="error".
        """
        import asyncio as _asyncio

        t_total = time.monotonic()

        # ── S1 Clarifier ───────────────────────────────────────────────
        if self._clarifier and clarification_turn < 2:
            try:
                clarification = await self._clarifier.assess(
                    query=query,
                    turn_number=clarification_turn,
                    context=clarification_context,
                )
                if clarification.needs_clarification:
                    yield {
                        "event": "clarification_needed",
                        "question": clarification.question_to_user,
                        "missing_element": clarification.missing_element,
                    }
                    return
            except Exception as exc:
                logger.warning(f"[Orchestrator Seq] S1 errore: {exc} — procedo")

        # ── S2 Retrieval bifasico ──────────────────────────────────────
        try:
            if intent in _BIFASICO_INTENTS:
                packet = await _asyncio.to_thread(
                    self._retriever.build_research_packet_bifasico,
                    query=query, intent=intent, valid_on=valid_on,
                )
            else:
                packet = await _asyncio.to_thread(
                    self._retriever.build_research_packet,
                    query=query, intent=intent, valid_on=valid_on,
                    chunk_filter=chunk_filter,
                )
        except Exception as exc:
            logger.error(f"[Orchestrator Seq] S2 retrieval errore: {exc}")
            yield {"event": "error", "message": f"Retrieval fallito: {exc}"}
            return

        yield {
            "event": "retrieval_done",
            "sources_count": len(packet.sources),
            "confidence": packet.retrieval_confidence,
        }
        await _asyncio.sleep(0)  # cede il controllo → flush immediato
        logger.info(
            f"[Orchestrator Seq] S2 done: {len(packet.sources)} fonti, "
            f"confidence={packet.retrieval_confidence}"
        )

        # ── S3 Sequential IQRAC ────────────────────────────────────────
        all_sections: list[AnalysisSection] = []
        last_phase: Optional[PhaseResult] = None

        async for phase in self._analyst.analyze_sequential(
            query=query,
            packet=packet,
            phase_retriever=self._phase_retriever,
        ):
            all_sections.extend(phase.sections)
            last_phase = phase
            yield {"event": "phase_complete", "phase": phase}
            await _asyncio.sleep(0)  # cede il controllo → flush immediato

        # ── S5 Reviewer ────────────────────────────────────────────────
        merged_answer = "\n\n".join(
            f"**{s.step}**\n{s.content}"
            for s in all_sections if s.content
        )
        cited_ids = [
            cit["source_id"]
            for s in all_sections
            for cit in s.citations
            if isinstance(cit, dict) and cit.get("source_id")
        ]
        text_to_review = merged_answer + ("\n" + " ".join(cited_ids) if cited_ids else "")

        try:
            review = self._reviewer.verify(
                response_text=text_to_review or " ",
                research_packet=packet,
                reference_date=valid_on,
            )
        except Exception as exc:
            logger.error(f"[Orchestrator Seq] S5 CitationReviewer errore: {exc}")
            from aiura_legal.core.reviewer.reviewer import ReviewResult
            review = ReviewResult(
                verdict="WARN",
                action="DELIVER",
                warnings=[f"Reviewer non disponibile: {exc}"],
            )

        # Serializza le fonti del Research Packet per il frontend
        serialized_sources = [
            {
                "rank":             i + 1,
                "doc_id":           s.doc_id,
                "source_id":        s.source_id,
                "score":            round(s.score, 4),
                "snippet":          s.snippet[:500],
                "retrieval_method": s.retrieval_method,
                "metadata":         s.metadata,
            }
            for i, s in enumerate(packet.sources)
        ]

        yield {
            "event": "review_done",
            "verdict": review.verdict,
            "action": review.action,
            "warnings": review.warnings,
            "overall_confidence": last_phase.overall_confidence if last_phase else "LOW",
            "duration_total_s": round(time.monotonic() - t_total, 3),
            "sources": serialized_sources,
            "gaps": list(dict.fromkeys(
                g for phase in (last_phase,) if phase for g in phase.gaps
            )),
        }
