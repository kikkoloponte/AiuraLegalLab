"""
Test ClarifierAgent (S1).

Strategia:
  - OllamaClient mockato → zero Ollama reale
  - Verifica: parsing JSON, turn counting, graceful degradation, edge cases
  - Zero PII reali, fixture sintetiche
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

from aiura_legal.agents.clarifier import ClarificationResult, ClarifierAgent


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_ollama():
    o = MagicMock()
    o.model = "qwen2.5:7b"
    return o


@pytest.fixture
def clarifier(mock_ollama):
    return ClarifierAgent(ollama=mock_ollama)


def _json_needs_clarification(question: str = "Appalto pubblico o privato?",
                               missing: str = "tipo_appalto") -> str:
    return json.dumps({
        "needs_clarification": True,
        "question_to_user": question,
        "missing_element": missing,
    })


def _json_no_clarification() -> str:
    return json.dumps({
        "needs_clarification": False,
        "question_to_user": None,
    })


# ---------------------------------------------------------------------------
# _build_prompt
# ---------------------------------------------------------------------------

class TestBuildPrompt:

    def test_prompt_includes_query(self, clarifier):
        p = clarifier._build_prompt("inadempimento contrattuale", 0, None)
        assert "inadempimento contrattuale" in p

    def test_prompt_includes_turn_number(self, clarifier):
        p = clarifier._build_prompt("query test", 0, None)
        assert "TURNO: 1 di 2" in p

    def test_prompt_turn_1_shows_second(self, clarifier):
        p = clarifier._build_prompt("query test", 1, None)
        assert "TURNO: 2 di 2" in p

    def test_prompt_includes_context_when_given(self, clarifier):
        p = clarifier._build_prompt("query test", 1, "appalto privato di costruzione")
        assert "appalto privato di costruzione" in p
        assert "RISPOSTA PRECEDENTE" in p

    def test_prompt_no_context_section_when_absent(self, clarifier):
        p = clarifier._build_prompt("query test", 0, None)
        assert "RISPOSTA PRECEDENTE" not in p

    def test_prompt_asks_for_json(self, clarifier):
        p = clarifier._build_prompt("query test", 0, None)
        assert "JSON" in p.upper()


# ---------------------------------------------------------------------------
# _parse_response
# ---------------------------------------------------------------------------

class TestParseResponse:

    def test_parse_needs_clarification_true(self, clarifier):
        raw = _json_needs_clarification(
            question="Appalto pubblico o privato?",
            missing="tipo_appalto",
        )
        result = clarifier._parse_response(raw, turn_number=0)
        assert result.needs_clarification is True
        assert result.question_to_user == "Appalto pubblico o privato?"
        assert result.missing_element == "tipo_appalto"
        assert result.parse_ok is True
        assert result.turn_number == 0

    def test_parse_needs_clarification_false(self, clarifier):
        raw = _json_no_clarification()
        result = clarifier._parse_response(raw, turn_number=1)
        assert result.needs_clarification is False
        assert result.question_to_user is None
        assert result.parse_ok is True
        assert result.turn_number == 1

    def test_parse_json_in_markdown_block(self, clarifier):
        raw = (
            "Ecco la mia valutazione:\n"
            "```json\n"
            + _json_needs_clarification() + "\n"
            "```\n"
        )
        result = clarifier._parse_response(raw, turn_number=0)
        assert result.parse_ok is True
        assert result.needs_clarification is True

    def test_parse_json_in_generic_code_block(self, clarifier):
        raw = "```\n" + _json_no_clarification() + "\n```"
        result = clarifier._parse_response(raw, turn_number=0)
        assert result.parse_ok is True
        assert result.needs_clarification is False

    def test_parse_invalid_json_fallback_proceed(self, clarifier):
        """Testo non JSON → fallback conservativo: needs_clarification=False."""
        raw = "Non posso rispondere in JSON. Procedo senza chiarimento."
        result = clarifier._parse_response(raw, turn_number=0)
        assert result.needs_clarification is False
        assert result.parse_ok is False

    def test_parse_empty_string_fallback(self, clarifier):
        result = clarifier._parse_response("", turn_number=0)
        assert result.needs_clarification is False
        assert result.parse_ok is False

    def test_parse_no_question_when_needs_is_false(self, clarifier):
        """needs_clarification=false → question_to_user deve essere None."""
        raw = json.dumps({
            "needs_clarification": False,
            "question_to_user": "Domanda inutile?",
        })
        result = clarifier._parse_response(raw, turn_number=0)
        assert result.needs_clarification is False
        assert result.question_to_user is None

    def test_parse_missing_question_field(self, clarifier):
        """needs_clarification=true ma senza question_to_user → question=None."""
        raw = json.dumps({
            "needs_clarification": True,
            # question_to_user mancante
        })
        result = clarifier._parse_response(raw, turn_number=0)
        assert result.needs_clarification is True
        assert result.question_to_user is None

    def test_parse_preserves_turn_number(self, clarifier):
        result = clarifier._parse_response(_json_no_clarification(), turn_number=1)
        assert result.turn_number == 1


# ---------------------------------------------------------------------------
# assess() — async
# ---------------------------------------------------------------------------

class TestAssess:

    @pytest.mark.asyncio
    async def test_assess_turn_ge_2_always_proceed(self, clarifier, mock_ollama):
        """turn_number >= 2 → sempre needs_clarification=False, nessuna chiamata Ollama."""
        mock_ollama.generate = AsyncMock(return_value=_json_needs_clarification())
        result = await clarifier.assess("query test", turn_number=2)
        assert result.needs_clarification is False
        mock_ollama.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_assess_turn_3_also_proceeds(self, clarifier, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value=_json_needs_clarification())
        result = await clarifier.assess("query test", turn_number=3)
        assert result.needs_clarification is False
        mock_ollama.generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_assess_needs_clarification(self, clarifier, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value=_json_needs_clarification(
            question="Si tratta di un appalto pubblico o privato?",
            missing="tipo_appalto",
        ))
        result = await clarifier.assess("appalto inadempimento", turn_number=0)
        assert result.needs_clarification is True
        assert "appalto" in result.question_to_user.lower()
        assert result.missing_element == "tipo_appalto"
        assert result.parse_ok is True

    @pytest.mark.asyncio
    async def test_assess_no_clarification_needed(self, clarifier, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value=_json_no_clarification())
        result = await clarifier.assess(
            "inadempimento contratto di locazione appartamento Roma",
            turn_number=0,
        )
        assert result.needs_clarification is False
        assert result.parse_ok is True

    @pytest.mark.asyncio
    async def test_assess_ollama_unavailable_graceful(self, clarifier, mock_ollama):
        """Se Ollama fallisce → needs_clarification=False (mai blocca l'utente)."""
        mock_ollama.generate = AsyncMock(side_effect=ConnectionError("Ollama offline"))
        result = await clarifier.assess("query test", turn_number=0)
        assert result.needs_clarification is False
        assert result.parse_ok is False

    @pytest.mark.asyncio
    async def test_assess_any_exception_graceful(self, clarifier, mock_ollama):
        """Qualsiasi eccezione → graceful degradation."""
        mock_ollama.generate = AsyncMock(side_effect=RuntimeError("errore generico"))
        result = await clarifier.assess("query test", turn_number=0)
        assert result.needs_clarification is False

    @pytest.mark.asyncio
    async def test_assess_json_parse_fail_proceeds(self, clarifier, mock_ollama):
        """JSON non parsabile → procede senza chiarimento."""
        mock_ollama.generate = AsyncMock(return_value="Testo libero non JSON.")
        result = await clarifier.assess("query test", turn_number=0)
        assert result.needs_clarification is False
        assert result.parse_ok is False

    @pytest.mark.asyncio
    async def test_assess_turn_1_with_context(self, clarifier, mock_ollama):
        """Turno 1 con contesto: viene incluso nel prompt e la valutazione procede."""
        mock_ollama.generate = AsyncMock(return_value=_json_no_clarification())
        result = await clarifier.assess(
            query="responsabilità appalto",
            turn_number=1,
            context="Si tratta di appalto privato di ristrutturazione",
        )
        # Verifica che il prompt includa il contesto
        call_kwargs = mock_ollama.generate.call_args.kwargs
        prompt = call_kwargs.get("prompt", "")
        assert "appalto privato di ristrutturazione" in prompt
        assert result.needs_clarification is False

    @pytest.mark.asyncio
    async def test_assess_returns_clarification_result_type(self, clarifier, mock_ollama):
        mock_ollama.generate = AsyncMock(return_value=_json_no_clarification())
        result = await clarifier.assess("test", turn_number=0)
        assert isinstance(result, ClarificationResult)

    @pytest.mark.asyncio
    async def test_assess_calls_ollama_with_system_prompt(self, clarifier, mock_ollama):
        """Ollama deve essere chiamato con system= (skill prompt)."""
        mock_ollama.generate = AsyncMock(return_value=_json_no_clarification())
        await clarifier.assess("test query", turn_number=0)
        call_kwargs = mock_ollama.generate.call_args.kwargs
        assert "system" in call_kwargs
        assert len(call_kwargs["system"]) > 0

    @pytest.mark.asyncio
    async def test_assess_temperature_conservative(self, clarifier, mock_ollama):
        """Temperatura bassa per output deterministico."""
        mock_ollama.generate = AsyncMock(return_value=_json_no_clarification())
        await clarifier.assess("test query", turn_number=0)
        call_kwargs = mock_ollama.generate.call_args.kwargs
        assert call_kwargs.get("temperature", 1.0) <= 0.3
