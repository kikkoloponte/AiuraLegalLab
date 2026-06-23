"""
Test QueryTypeClassifier.

LLM mockato — zero chiamate HTTP.
"""
from __future__ import annotations

import json
import pytest
from unittest.mock import AsyncMock

from aiura_legal.agents.query_classifier import QueryTypeClassifier


def _make_llm(response: str) -> AsyncMock:
    llm = AsyncMock()
    llm.generate = AsyncMock(return_value=response)
    return llm


@pytest.mark.asyncio
async def test_classify_doctrine():
    llm = _make_llm('{"query_type": "doctrine"}')
    clf = QueryTypeClassifier(llm)
    result = await clf.classify("In quali casi è legittimo un sequestro preventivo?")
    assert result == "doctrine"


@pytest.mark.asyncio
async def test_classify_case():
    llm = _make_llm('{"query_type": "case"}')
    clf = QueryTypeClassifier(llm)
    result = await clf.classify("Il mio cliente ha ricevuto un avviso di garanzia, cosa fare?")
    assert result == "case"


@pytest.mark.asyncio
async def test_fallback_on_invalid_json():
    llm = _make_llm("risposta non json")
    clf = QueryTypeClassifier(llm)
    result = await clf.classify("qualsiasi domanda")
    assert result == "case"


@pytest.mark.asyncio
async def test_fallback_on_llm_error():
    llm = AsyncMock()
    llm.generate = AsyncMock(side_effect=Exception("connessione rifiutata"))
    clf = QueryTypeClassifier(llm)
    result = await clf.classify("qualsiasi domanda")
    assert result == "case"


@pytest.mark.asyncio
async def test_fallback_on_unknown_value():
    llm = _make_llm('{"query_type": "unknown_value"}')
    clf = QueryTypeClassifier(llm)
    result = await clf.classify("qualsiasi domanda")
    assert result == "case"
