"""
test_drafter.py — test per DrafterAgent (S4) e relativo wiring nell'orchestratore.

Copertura:
  TestDetectDocumentType      (6) — keyword matching + default
  TestNormalizeDocumentType   (4) — normalizzazione e fallback
  TestBuildPrompt             (5) — contiene fonti, analisi, struttura, tipo, regole
  TestRenderCitations         (5) — risoluzione marker, non risolto, multipli, case-insensitive
  TestParseResponse           (4) — testo normale, code fence, vuoto, whitespace
  TestDraftMethod             (8) — happy path, Ollama error, empty packet, disclaimer, tipo auto-detect
  TestOrchestratorS4          (5) — draft presente se draft_type, assente se None, S5 vede draft
"""
from __future__ import annotations

from datetime import date
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from aiura_legal.agents.drafter import (
    DISCLAIMER,
    VALID_TYPES,
    DraftResult,
    DrafterAgent,
)
from aiura_legal.agents.orchestrator import LegalOrchestrator, OrchestratorResult
from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_packet(sources: list[SearchResult] | None = None) -> ResearchPacket:
    if sources is None:
        sources = [
            SearchResult(
                doc_id="doc1",
                score=0.9,
                snippet="Il debitore inadempiente è tenuto al risarcimento.",
                source_id="CC_ART_1218",
                retrieval_method="bm25",
                metadata={
                    "fonte": "codice_civile",
                    "titolo": "Codice Civile",
                    "articolo_num": "art. 1218",
                },
            ),
            SearchResult(
                doc_id="doc2",
                score=0.8,
                snippet="La prescrizione ordinaria è di dieci anni.",
                source_id="CC_ART_2946",
                retrieval_method="vector",
                metadata={
                    "fonte": "codice_civile",
                    "titolo": "Codice Civile",
                    "articolo_num": "art. 2946",
                },
            ),
        ]
    return ResearchPacket(
        query_original="Parere inadempimento contrattuale",
        query_intent=QueryIntent.FATTISPECIE_ANALYSIS,
        sources=sources,
        retrieval_confidence="HIGH",
    )


def _mock_ollama(response: str = "Testo documento di prova.") -> MagicMock:
    """OllamaClient mock con generate() asincrono."""
    mock = MagicMock()
    mock.model = "qwen2.5:7b"
    mock.generate = AsyncMock(return_value=response)
    return mock


def _mock_retriever(packet: ResearchPacket | None = None) -> MagicMock:
    """HybridRetriever mock."""
    if packet is None:
        packet = _make_packet()
    mock = MagicMock()
    mock.build_research_packet = MagicMock(return_value=packet)
    return mock


# ---------------------------------------------------------------------------
# TestDetectDocumentType
# ---------------------------------------------------------------------------

class TestDetectDocumentType:
    def setup_method(self):
        self.agent = DrafterAgent(ollama=_mock_ollama())

    def test_detect_parere(self):
        assert self.agent.detect_document_type("Voglio un parere sull'inadempimento") == "parere"

    def test_detect_diffida(self):
        assert self.agent.detect_document_type("Redigi una diffida al condominio") == "diffida"

    def test_detect_messa_in_mora(self):
        assert self.agent.detect_document_type("Lettera di messa in mora") == "diffida"

    def test_detect_citazione(self):
        assert self.agent.detect_document_type("Atto di citazione per danni") == "citazione"

    def test_detect_contratto(self):
        assert self.agent.detect_document_type("Bozza contrattuale di locazione") == "contratto"

    def test_detect_default(self):
        """Nessuna keyword riconosciuta → default 'parere'."""
        assert self.agent.detect_document_type("Come funziona l'art. 1218 cc?") == "parere"


# ---------------------------------------------------------------------------
# TestNormalizeDocumentType
# ---------------------------------------------------------------------------

class TestNormalizeDocumentType:
    def test_valid_type_unchanged(self):
        assert DrafterAgent.normalize_document_type("parere") == "parere"

    def test_uppercase_normalized(self):
        assert DrafterAgent.normalize_document_type("DIFFIDA") == "diffida"

    def test_invalid_type_defaults_to_parere(self):
        assert DrafterAgent.normalize_document_type("letterdisollecito") == "parere"

    def test_empty_defaults_to_parere(self):
        assert DrafterAgent.normalize_document_type("") == "parere"


# ---------------------------------------------------------------------------
# TestBuildPrompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def setup_method(self):
        self.agent = DrafterAgent(ollama=_mock_ollama())
        self.packet = _make_packet()

    def test_prompt_includes_source_ids(self):
        prompt = self.agent._build_prompt(
            "Parere inadempimento", self.packet, "Analisi S3...", "parere"
        )
        assert "CC_ART_1218" in prompt
        assert "CC_ART_2946" in prompt

    def test_prompt_includes_analysis(self):
        prompt = self.agent._build_prompt(
            "Parere inadempimento", self.packet, "Analisi S3: inadempimento grave.", "parere"
        )
        assert "Analisi S3: inadempimento grave." in prompt

    def test_prompt_includes_document_type(self):
        prompt = self.agent._build_prompt(
            "Parere inadempimento", self.packet, "", "diffida"
        )
        assert "DIFFIDA" in prompt

    def test_prompt_includes_cite_instruction(self):
        prompt = self.agent._build_prompt(
            "Parere inadempimento", self.packet, "", "parere"
        )
        assert "{{cite:source_id}}" in prompt

    def test_prompt_no_disclaimer_instruction(self):
        """Il disclaimer non deve essere nel prompt — viene aggiunto in post-processing."""
        prompt = self.agent._build_prompt(
            "Parere inadempimento", self.packet, "", "parere"
        )
        # L'istruzione dice di non includerlo nel documento generato
        assert "viene aggiunto automaticamente" in prompt


# ---------------------------------------------------------------------------
# TestRenderCitations
# ---------------------------------------------------------------------------

class TestRenderCitations:
    def setup_method(self):
        self.agent = DrafterAgent(ollama=_mock_ollama())
        self.packet = _make_packet()

    def test_renders_known_source_id(self):
        text = "Come previsto da {{cite:CC_ART_1218}}, il debitore risponde."
        rendered = self.agent.render_citations(text, self.packet)
        assert "{{cite:" not in rendered
        assert "art. 1218" in rendered or "CC_ART_1218" not in rendered

    def test_renders_unknown_source_id_as_bracket(self):
        text = "Ai sensi di {{cite:UNKNOWN_NORM}}."
        rendered = self.agent.render_citations(text, self.packet)
        assert "[UNKNOWN_NORM]" in rendered

    def test_renders_multiple_citations(self):
        text = "{{cite:CC_ART_1218}} e {{cite:CC_ART_2946}} si applicano."
        rendered = self.agent.render_citations(text, self.packet)
        assert "{{cite:" not in rendered

    def test_case_insensitive_source_id(self):
        """Il matching source_id è case-insensitive."""
        text = "{{cite:cc_art_1218}} si applica."
        rendered = self.agent.render_citations(text, self.packet)
        assert "{{cite:" not in rendered

    def test_no_citations_returns_text_unchanged(self):
        text = "Documento senza citazioni."
        rendered = self.agent.render_citations(text, self.packet)
        assert rendered == text


# ---------------------------------------------------------------------------
# TestParseResponse
# ---------------------------------------------------------------------------

class TestParseResponse:
    def test_normal_text(self):
        text, ok = DrafterAgent._parse_response("Documento legale formale.")
        assert ok is True
        assert text == "Documento legale formale."

    def test_strips_code_fence(self):
        raw = "```\nDocumento.\n```"
        text, ok = DrafterAgent._parse_response(raw)
        assert ok is True
        assert "```" not in text
        assert "Documento." in text

    def test_empty_response(self):
        _, ok = DrafterAgent._parse_response("")
        assert ok is False

    def test_whitespace_only(self):
        _, ok = DrafterAgent._parse_response("   \n\t  ")
        assert ok is False


# ---------------------------------------------------------------------------
# TestDraftMethod
# ---------------------------------------------------------------------------

class TestDraftMethod:
    @pytest.mark.asyncio
    async def test_happy_path_returns_draft_result(self):
        mock_ol = _mock_ollama("Parere: inadempimento contrattuale ai sensi {{cite:CC_ART_1218}}.")
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft(
            "Parere inadempimento", packet, "Analisi S3...", document_type="parere"
        )

        assert isinstance(result, DraftResult)
        assert result.parse_ok is True
        assert result.document_type == "parere"
        assert result.raw_text != ""
        assert result.rendered_text != ""

    @pytest.mark.asyncio
    async def test_disclaimer_in_full_document(self):
        mock_ol = _mock_ollama("Testo del parere.")
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft("Parere inadempimento", packet, "", document_type="parere")

        assert DISCLAIMER in result.full_document

    @pytest.mark.asyncio
    async def test_ollama_error_graceful_degradation(self):
        mock_ol = MagicMock()
        mock_ol.model = "qwen2.5:7b"
        mock_ol.generate = AsyncMock(side_effect=ConnectionError("Ollama non disponibile"))
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft("Parere inadempimento", packet, "", document_type="parere")

        assert result.parse_ok is False
        assert result.raw_text == ""
        assert result.full_document == ""

    @pytest.mark.asyncio
    async def test_empty_packet_graceful_degradation(self):
        agent = DrafterAgent(ollama=_mock_ollama())
        empty_packet = _make_packet(sources=[])

        result = await agent.draft("Parere inadempimento", empty_packet, "", document_type="parere")

        assert result.parse_ok is False
        assert result.raw_text == ""

    @pytest.mark.asyncio
    async def test_auto_detect_document_type(self):
        mock_ol = _mock_ollama("Diffida formale.")
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft(
            "Redigi una diffida per mora del debitore", packet, ""
            # document_type=None → auto-detect
        )

        assert result.document_type == "diffida"

    @pytest.mark.asyncio
    async def test_cite_markers_resolved_in_rendered_text(self):
        mock_ol = _mock_ollama("Art. {{cite:CC_ART_1218}} prevede la responsabilità.")
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft("Parere inadempimento", packet, "", document_type="parere")

        assert "{{cite:" not in result.rendered_text
        assert "{{cite:" not in result.full_document

    @pytest.mark.asyncio
    async def test_raw_text_contains_cite_markers(self):
        """raw_text deve conservare i marker non risolti (audit trail)."""
        mock_ol = _mock_ollama("Ai sensi {{cite:CC_ART_1218}} il debitore.")
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft("Parere", packet, "", document_type="parere")

        assert "{{cite:CC_ART_1218}}" in result.raw_text

    @pytest.mark.asyncio
    async def test_invalid_document_type_normalized_to_parere(self):
        mock_ol = _mock_ollama("Documento.")
        agent = DrafterAgent(ollama=mock_ol)
        packet = _make_packet()

        result = await agent.draft("Query", packet, "", document_type="lettoni_vari")

        assert result.document_type == "parere"


# ---------------------------------------------------------------------------
# TestOrchestratorS4
# ---------------------------------------------------------------------------

class TestOrchestratorS4:
    """Test di integrazione S4 nell'orchestratore."""

    def _build_orchestrator(self, draft_response: str = "Documento generato.") -> LegalOrchestrator:
        mock_ol = _mock_ollama(draft_response)
        mock_ol.generate = AsyncMock(return_value=draft_response)
        retriever = _mock_retriever()
        return LegalOrchestrator(
            retriever=retriever,
            ollama=mock_ol,
            enable_clarifier=False,
        )

    @pytest.mark.asyncio
    async def test_draft_present_when_draft_type_set(self):
        """Se draft_type è passato, result.draft non è None."""
        orch = self._build_orchestrator("Parere formale.")

        result = await orch.run(
            query="Parere su inadempimento",
            intent=QueryIntent.FATTISPECIE_ANALYSIS,
            draft_type="parere",
        )

        assert result.draft is not None
        assert result.draft.document_type == "parere"

    @pytest.mark.asyncio
    async def test_draft_none_when_draft_type_not_set(self):
        """Se draft_type non è passato, result.draft rimane None."""
        orch = self._build_orchestrator()

        result = await orch.run(
            query="Parere su inadempimento",
            intent=QueryIntent.FATTISPECIE_ANALYSIS,
            # draft_type non passato
        )

        assert result.draft is None

    @pytest.mark.asyncio
    async def test_draft_none_when_drafter_disabled(self):
        """Se enable_drafter=False, S4 non viene mai eseguito."""
        mock_ol = _mock_ollama()
        retriever = _mock_retriever()
        orch = LegalOrchestrator(
            retriever=retriever,
            ollama=mock_ol,
            enable_clarifier=False,
            enable_drafter=False,
        )

        result = await orch.run(
            query="Parere su inadempimento",
            intent=QueryIntent.FATTISPECIE_ANALYSIS,
            draft_type="parere",
        )

        assert result.draft is None

    @pytest.mark.asyncio
    async def test_orchestrator_result_has_draft_field(self):
        """OrchestratorResult espone il campo draft nel tipo."""
        orch = self._build_orchestrator("Testo documento.")

        result = await orch.run(
            query="Parere",
            intent=QueryIntent.FATTISPECIE_ANALYSIS,
            draft_type="parere",
        )

        assert hasattr(result, "draft")

    @pytest.mark.asyncio
    async def test_s5_reviews_draft_rendered_text_when_available(self):
        """Se draft esiste, S5 riceve il testo renderizzato del documento."""
        packet = _make_packet()
        retriever = _mock_retriever(packet)
        mock_ol = _mock_ollama("Ai sensi {{cite:CC_ART_1218}} l'obbligazione.")
        orch = LegalOrchestrator(
            retriever=retriever,
            ollama=mock_ol,
            enable_clarifier=False,
        )

        result = await orch.run(
            query="Parere inadempimento",
            intent=QueryIntent.FATTISPECIE_ANALYSIS,
            draft_type="parere",
        )

        # S5 deve aver valutato il testo — il verdict deve essere presente
        assert result.reviewer_verdict in ("PASS", "WARN", "FAIL")
