"""
Test LegalOrchestrator + AnalystAgent.

Strategia:
  - OllamaClient.generate mockato → controllo output LLM senza Ollama
  - HybridRetriever mockato → nessun indice su disco
  - CitationReviewer reale → verifica Citation Contract
  - Zero PII reali, zero chiamate HTTP
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from aiura_legal.agents.analyst import AnalystAgent, AnalysisResult, AnalysisSection, PhaseResult
from aiura_legal.agents.orchestrator import LegalOrchestrator, OrchestratorResult
from aiura_legal.core.reviewer.reviewer import CitationReviewer
from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_source(doc_id: str, snippet: str = "Testo normativo sintetico.", score: float = 1.0) -> SearchResult:
    return SearchResult(
        doc_id=doc_id,
        score=score,
        snippet=snippet,
        source_id=doc_id,
        retrieval_method="hybrid_rrf",
        metadata={"fonte": "codice_civile", "corpus": "normattiva", "titolo": "Titolo sintetico"},
    )


def _make_packet(sources: list[SearchResult] | None = None) -> ResearchPacket:
    if sources is None:
        sources = [_make_source("CC_ART_1218"), _make_source("CC_ART_1453")]
    return ResearchPacket(
        query_original="query test",
        query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
        sources=sources,
        retrieval_confidence="HIGH",
    )


@pytest.fixture
def mock_retriever():
    r = MagicMock()
    r.build_research_packet.return_value = _make_packet()
    r.build_research_packet_bifasico.return_value = _make_packet()
    return r


@pytest.fixture
def mock_ollama():
    o = MagicMock()
    o.model = "qwen2.5:7b"
    return o


@pytest.fixture
def analyst(mock_ollama):
    return AnalystAgent(ollama=mock_ollama)


@pytest.fixture
def orchestrator(mock_retriever, mock_ollama):
    return LegalOrchestrator(
        retriever=mock_retriever,
        ollama=mock_ollama,
        reviewer=CitationReviewer(),
    )


# ---------------------------------------------------------------------------
# AnalystAgent — build_context
# ---------------------------------------------------------------------------

class TestAnalystContextBuilding:

    def test_context_includes_source_ids(self, analyst):
        packet = _make_packet([
            _make_source("CC_ART_1218", "Testo art. 1218"),
            _make_source("CC_ART_1453", "Testo art. 1453"),
        ])
        ctx = analyst._build_context(packet)
        assert "CC_ART_1218" in ctx
        assert "CC_ART_1453" in ctx

    def test_context_empty_packet(self, analyst):
        packet = _make_packet([])
        ctx = analyst._build_context(packet)
        assert "NESSUNA FONTE" in ctx.upper()

    def test_prompt_contains_query(self, analyst):
        packet = _make_packet()
        prompt = analyst._build_prompt("contratto inadempimento", packet)
        assert "contratto inadempimento" in prompt

    def test_prompt_contains_source_id(self, analyst):
        packet = _make_packet([_make_source("CC_ART_1218")])
        prompt = analyst._build_prompt("query test", packet)
        assert "CC_ART_1218" in prompt


# ---------------------------------------------------------------------------
# AnalystAgent — parse_response
# ---------------------------------------------------------------------------

class TestAnalystParsing:

    def test_parse_valid_json(self, analyst):
        raw = json.dumps({
            "analysis_sections": [
                {"step": "QUALIFICAZIONE", "content": "Il caso...", "citations": []},
                {"step": "VALUTAZIONE", "content": "VALUTAZIONE PERSONALE: ...", "citations": []},
            ],
            "overall_confidence": "HIGH",
            "escalation_recommended": False,
            "gaps": [],
        })
        sections, conf, escalation, ok = analyst._parse_response(raw)
        assert ok is True
        assert len(sections) == 2
        assert sections[0].step == "QUALIFICAZIONE"
        assert conf == "HIGH"
        assert escalation is False

    def test_parse_json_in_markdown_block(self, analyst):
        raw = (
            "Ecco la risposta:\n"
            "```json\n"
            '{"analysis_sections": [{"step": "ANALISI", "content": "testo", "citations": []}],'
            '"overall_confidence": "MEDIUM", "escalation_recommended": false, "gaps": []}\n'
            "```"
        )
        sections, conf, escalation, ok = analyst._parse_response(raw)
        assert ok is True
        assert len(sections) == 1
        assert conf == "MEDIUM"

    def test_parse_invalid_json_fallback(self, analyst):
        raw = "Non riesco a rispondere in JSON. Testo libero."
        sections, conf, escalation, ok = analyst._parse_response(raw)
        assert ok is False
        assert len(sections) == 1
        assert sections[0].step == "ANALISI"
        assert conf == "LOW"

    def test_parse_truncated_json_repaired(self, analyst):
        """JSON troncato da max_tokens: repair chiude array e oggetto aperti."""
        truncated = (
            '{"analysis_sections": ['
            '{"step": "QUALIFICAZIONE", "content": "testo", "citations": []},'
            '{"step": "CONCLUSIONE", "content": "fine'
            # mancano: ", "citations": []}], "overall_confidence": "MEDIUM", ...}
        )
        sections, conf, escalation, ok = analyst._parse_response(truncated)
        assert ok is True
        assert len(sections) >= 1
        assert sections[0].step == "QUALIFICAZIONE"

    def test_parse_empty_sections_uses_raw(self, analyst):
        raw = json.dumps({
            "analysis_sections": [],
            "overall_confidence": "LOW",
        })
        sections, conf, escalation, ok = analyst._parse_response(raw)
        # Con sezioni vuote usa raw come fallback
        assert len(sections) >= 1

    def test_sections_to_answer(self, analyst):
        from aiura_legal.agents.analyst import AnalysisSection
        sections = [
            AnalysisSection(step="QUALIFICAZIONE", content="Testo A"),
            AnalysisSection(step="VALUTAZIONE", content="Testo B"),
        ]
        answer = analyst._sections_to_answer(sections)
        assert "Testo A" in answer
        assert "Testo B" in answer
        assert "QUALIFICAZIONE" in answer


# ---------------------------------------------------------------------------
# AnalystAgent — analyze() async
# ---------------------------------------------------------------------------

class TestAnalystAnalyze:

    @pytest.mark.asyncio
    async def test_analyze_returns_result(self, analyst, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value=json.dumps({
            "analysis_sections": [
                {"step": "QUALIFICAZIONE", "content": "Il contratto...", "citations": [
                    {"source_id": "CC_ART_1218", "claim": "inadempimento"}
                ]},
            ],
            "overall_confidence": "HIGH",
            "escalation_recommended": False,
            "gaps": [],
        }))
        packet = _make_packet()
        result = await analyst.analyze("contratto inadempimento", packet)
        assert isinstance(result, AnalysisResult)
        assert result.parse_ok is True
        assert len(result.answer) > 0
        assert result.overall_confidence == "HIGH"
        assert result.llm_model == "qwen2.5:7b"

    @pytest.mark.asyncio
    async def test_analyze_empty_packet_returns_low_confidence(self, analyst):
        result = await analyst.analyze("query", _make_packet([]))
        assert result.overall_confidence == "LOW"
        assert result.answer == ""
        assert result.parse_ok is False
        assert len(result.gaps) > 0

    @pytest.mark.asyncio
    async def test_analyze_ollama_error_graceful(self, analyst, mock_ollama):
        """Se Ollama fallisce → AnalysisResult con answer='' senza eccezione."""
        mock_ollama.generate = AsyncMock(side_effect=ConnectionError("Ollama offline"))
        result = await analyst.analyze("query", _make_packet())
        assert result.answer == ""
        assert result.parse_ok is False
        assert any("ConnectionError" in g for g in result.gaps)

    @pytest.mark.asyncio
    async def test_analyze_parse_error_uses_raw(self, analyst, mock_ollama):
        """Se JSON non parsabile → risposta grezza come answer."""
        mock_ollama.generate = AsyncMock(return_value="Risposta non JSON valida.")
        result = await analyst.analyze("query", _make_packet())
        assert result.parse_ok is False
        assert "Risposta non JSON valida" in result.answer

    @pytest.mark.asyncio
    async def test_analyze_duration_recorded(self, analyst, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value='{"analysis_sections": [], "overall_confidence": "LOW"}')
        result = await analyst.analyze("query", _make_packet())
        assert result.duration_s >= 0


# ---------------------------------------------------------------------------
# LegalOrchestrator — run()
# ---------------------------------------------------------------------------

class TestOrchestrator:

    @pytest.mark.asyncio
    async def test_run_returns_orchestrator_result(self, orchestrator, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value=json.dumps({
            "analysis_sections": [
                {"step": "QUALIFICAZIONE", "content": "Il caso integra...", "citations": []},
            ],
            "overall_confidence": "MEDIUM",
            "escalation_recommended": False,
            "gaps": [],
        }))
        result = await orchestrator.run(
            query="inadempimento contrattuale",
            intent=QueryIntent.FATTISPECIE_ANALYSIS,
            workspace="test-ws",
        )
        assert isinstance(result, OrchestratorResult)
        assert result.query == "inadempimento contrattuale"
        assert result.workspace == "test-ws"

    @pytest.mark.asyncio
    async def test_run_calls_retriever(self, orchestrator, mock_retriever, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value='{"analysis_sections": [], "overall_confidence": "LOW"}')
        # FATTISPECIE_ANALYSIS (default) usa il percorso bifasico
        await orchestrator.run(query="test", workspace="ws")
        mock_retriever.build_research_packet_bifasico.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_norma_lookup_calls_bifasico_retriever(self, orchestrator, mock_retriever, mock_ollama):
        """NORMA_LOOKUP deve usare build_research_packet_bifasico (corpus=normattiva filtrato)."""
        mock_ollama.generate = AsyncMock(return_value='{"analysis_sections": [], "overall_confidence": "LOW"}')
        await orchestrator.run(query="test", intent=QueryIntent.NORMA_LOOKUP, workspace="ws")
        mock_retriever.build_research_packet_bifasico.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_s5_review_pass(self, orchestrator, mock_ollama):
        """S5 deve dare PASS su risposta grounded."""
        mock_ollama.generate = AsyncMock(return_value=json.dumps({
            "analysis_sections": [
                {
                    "step": "QUALIFICAZIONE",
                    "content": "La fattispecie integra un inadempimento.",
                    "citations": [{"source_id": "CC_ART_1218"}],
                }
            ],
            "overall_confidence": "HIGH",
            "escalation_recommended": False,
        }))
        result = await orchestrator.run(query="test", workspace="ws")
        assert result.reviewer_verdict in ("PASS", "WARN")
        assert result.reviewer_action in ("DELIVER", "RE_RETRIEVAL")

    @pytest.mark.asyncio
    async def test_run_timing_fields_populated(self, orchestrator, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value='{"analysis_sections": [], "overall_confidence": "LOW"}')
        result = await orchestrator.run(query="test", workspace="ws")
        assert result.duration_retrieval_s >= 0
        assert result.duration_llm_s >= 0
        assert result.duration_total_s >= 0

    @pytest.mark.asyncio
    async def test_run_graceful_when_ollama_offline(self, orchestrator, mock_ollama):
        """Senza Ollama: fonti disponibili, analisi vuota, verdict PASS."""
        mock_ollama.generate = AsyncMock(side_effect=Exception("offline"))
        result = await orchestrator.run(query="test", workspace="ws")
        assert result.answer == ""
        assert result.llm_available is False
        assert len(result.sources) > 0         # retrieval funziona ancora

    @pytest.mark.asyncio
    async def test_run_with_chunk_filter(self, orchestrator, mock_retriever, mock_ollama):
        """NORMA_LOOKUP usa build_research_packet_bifasico che applica il filtro corpus internamente."""
        mock_ollama.generate = AsyncMock(return_value='{"analysis_sections": [], "overall_confidence": "LOW"}')
        await orchestrator.run(
            query="test",
            workspace="ws",
            intent=QueryIntent.NORMA_LOOKUP,
            chunk_filter={"corpus": "normattiva"},
        )
        # Con il fix routing, NORMA_LOOKUP va sempre su bifasico (corpus filtrato internamente)
        mock_retriever.build_research_packet_bifasico.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_sources_from_packet(self, orchestrator, mock_retriever, mock_ollama):
        """Le fonti nella risposta vengono dal Research Packet."""
        mock_ollama.generate = AsyncMock(return_value='{"analysis_sections": [], "overall_confidence": "LOW"}')
        custom_packet = _make_packet([_make_source("URN_CUSTOM", "Testo custom")])
        mock_retriever.build_research_packet_bifasico.return_value = custom_packet

        result = await orchestrator.run(query="test", workspace="ws")
        assert len(result.sources) >= 1
        assert result.sources[0].source_id == "URN_CUSTOM"


# ---------------------------------------------------------------------------
# Citation Contract — S5 blocca citazioni non grounded
# ---------------------------------------------------------------------------

class TestCitationContract:

    @pytest.mark.asyncio
    async def test_s5_fails_ungrounded_citation(self, mock_retriever, mock_ollama):
        """S5 deve dare FAIL se S3 cita un source_id non nel Packet."""
        # Packet ha solo CC_ART_1218
        packet = _make_packet([_make_source("CC_ART_1218")])
        mock_retriever.build_research_packet_bifasico.return_value = packet

        # S3 cita CC_ART_9999 che NON è nel packet
        mock_ollama.generate = AsyncMock(return_value=json.dumps({
            "analysis_sections": [
                {
                    "step": "QUALIFICAZIONE",
                    "content": "Vedi art. CC_ART_9999 per la definizione.",
                    "citations": [{"source_id": "CC_ART_9999"}],
                }
            ],
            "overall_confidence": "LOW",
            "escalation_recommended": False,
        }))

        orch = LegalOrchestrator(
            retriever=mock_retriever,
            ollama=mock_ollama,
            reviewer=CitationReviewer(),
        )
        result = await orch.run(query="test", workspace="ws")
        # CC_ART_9999 non è nel packet → S5 deve segnalare problema
        # (FAIL o WARN a seconda della severità)
        assert result.reviewer_verdict in ("FAIL", "WARN")


# ---------------------------------------------------------------------------
# Bug #5 — RE_RETRIEVAL confinato a Fase 4: retry mirato della Sintesi
# invece di BLOCK secco. Se le citazioni ungrounded provengono da Fase 2/3
# (non rigenerate) il comportamento resta BLOCK come prima (nessuna regressione).
# ---------------------------------------------------------------------------

def _phase(phase: int, name: str, sections: list) -> PhaseResult:
    return PhaseResult(phase=phase, name=name, sections=sections, sources_used=[])


def _section(step: str, source_id: str | None = None) -> AnalysisSection:
    citations = [{"source_id": source_id}] if source_id else []
    return AnalysisSection(step=step, content=f"Contenuto {step}.", citations=citations)


class TestRetryFase4ReRetrieval:

    @pytest.mark.asyncio
    async def test_retry_fase4_risolve_citazione_ungrounded_confinata(
        self, mock_retriever, mock_ollama,
    ):
        """Fase 4 cita un source_id ungrounded ("CC_ART_9999") in CONCLUSIONE.
        Il retry mirato rigenera solo la Fase 4 con istruzione correttiva e la
        nuova versione cita solo fonti valide → verdetto finale DELIVER, non BLOCK."""
        packet = _make_packet([_make_source("CC_ART_1218")])
        mock_retriever.build_research_packet_bifasico.return_value = packet

        orch = LegalOrchestrator(retriever=mock_retriever, ollama=mock_ollama, reviewer=CitationReviewer())

        bad_phase4 = _phase(4, "SINTESI", [
            _section("SUSSUNZIONE", "CC_ART_1218"),
            _section("CONCLUSIONE", "CC_ART_9999"),  # ungrounded
        ])
        phases = [
            _phase(1, "FRAMING", [_section("QUESTIONE")]),
            _phase(2, "NORMATIVA", [_section("FONTI_NORMATIVE", "CC_ART_1218")]),
            _phase(3, "GIURISPRUDENZA", [_section("GIURISPRUDENZA")]),
            bad_phase4,
        ]
        orch._analyst.analyze_sequential = lambda **kw: _async_iter(phases)

        fixed_phase4 = _phase(4, "SINTESI", [
            _section("SUSSUNZIONE", "CC_ART_1218"),
            _section("CONCLUSIONE", "CC_ART_1218"),
        ])
        orch._analyst.regenerate_fase4 = AsyncMock(return_value=fixed_phase4)

        events = [e async for e in orch.run_sequential(query="test", workspace="ws")]
        review_done = next(e for e in events if e["event"] == "review_done")

        orch._analyst.regenerate_fase4.assert_awaited_once()
        assert "CC_ART_9999" in orch._analyst.regenerate_fase4.call_args.kwargs["ungrounded_ids"]
        assert review_done["action"] == "DELIVER"
        assert review_done["verdict"] in ("PASS", "WARN")

    @pytest.mark.asyncio
    async def test_retry_non_tentato_se_ungrounded_in_fase2(
        self, mock_retriever, mock_ollama,
    ):
        """Se la citazione ungrounded proviene da Fase 2 (non rigenerabile dal
        retry di Fase 4), il retry NON deve essere tentato e l'azione resta
        BLOCK — stesso comportamento di prima di questo fix."""
        packet = _make_packet([_make_source("CC_ART_1218")])
        mock_retriever.build_research_packet_bifasico.return_value = packet

        orch = LegalOrchestrator(retriever=mock_retriever, ollama=mock_ollama, reviewer=CitationReviewer())

        phases = [
            _phase(1, "FRAMING", [_section("QUESTIONE")]),
            _phase(2, "NORMATIVA", [_section("FONTI_NORMATIVE", "CC_ART_9999")]),  # ungrounded
            _phase(3, "GIURISPRUDENZA", [_section("GIURISPRUDENZA")]),
            _phase(4, "SINTESI", [_section("CONCLUSIONE", "CC_ART_1218")]),
        ]
        orch._analyst.analyze_sequential = lambda **kw: _async_iter(phases)
        orch._analyst.regenerate_fase4 = AsyncMock()

        events = [e async for e in orch.run_sequential(query="test", workspace="ws")]
        review_done = next(e for e in events if e["event"] == "review_done")

        orch._analyst.regenerate_fase4.assert_not_awaited()
        assert review_done["action"] == "BLOCK"

    @pytest.mark.asyncio
    async def test_retry_fase4_esaurito_resta_block(
        self, mock_retriever, mock_ollama,
    ):
        """Se il retry di Fase 4 produce di nuovo una citazione ungrounded,
        non si ritenta una seconda volta — budget di un solo retry — e
        l'azione finale resta BLOCK."""
        packet = _make_packet([_make_source("CC_ART_1218")])
        mock_retriever.build_research_packet_bifasico.return_value = packet

        orch = LegalOrchestrator(retriever=mock_retriever, ollama=mock_ollama, reviewer=CitationReviewer())

        phases = [
            _phase(1, "FRAMING", [_section("QUESTIONE")]),
            _phase(2, "NORMATIVA", [_section("FONTI_NORMATIVE", "CC_ART_1218")]),
            _phase(3, "GIURISPRUDENZA", [_section("GIURISPRUDENZA")]),
            _phase(4, "SINTESI", [_section("CONCLUSIONE", "CC_ART_8888")]),  # ungrounded
        ]
        orch._analyst.analyze_sequential = lambda **kw: _async_iter(phases)

        still_bad_phase4 = _phase(4, "SINTESI", [_section("CONCLUSIONE", "CC_ART_7777")])  # ancora ungrounded
        orch._analyst.regenerate_fase4 = AsyncMock(return_value=still_bad_phase4)

        events = [e async for e in orch.run_sequential(query="test", workspace="ws")]
        review_done = next(e for e in events if e["event"] == "review_done")

        orch._analyst.regenerate_fase4.assert_awaited_once()
        assert review_done["action"] == "BLOCK"


async def _async_iter(items: list):
    for item in items:
        yield item
