"""
QueryTypeClassifier — Phase 0 del pipeline sequential.

Classifica la query come "case" (domanda su caso concreto)
o "doctrine" (domanda astratta su istituto giuridico).
Chiamata LLM leggera: ~150 token, ~0.3s su qwen2.5-7b.

Fallback a "case" in caso di errore → nessuna regressione.
"""
from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal

from loguru import logger

if TYPE_CHECKING:
    from aiura_legal.agents.openai_compat_client import OpenAICompatClient
    from aiura_legal.agents.ollama_client import OllamaClient

QueryType = Literal["case", "doctrine"]

_SYSTEM = (
    "Classifica la domanda legale italiana.\n"
    '"doctrine" = domanda astratta su un istituto giuridico, presupposti normativi, '
    'orientamenti generali. Segnali tipici: "in quali casi", "quando è legittimo", '
    '"cosa si intende per", "quali sono i requisiti", "come funziona", '
    '"è possibile", "è ammesso".\n'
    '"case" = domanda su una situazione concreta con fatti specifici da analizzare.\n'
    "Output ESCLUSIVAMENTE: {\"query_type\": \"case\"} oppure {\"query_type\": \"doctrine\"}"
)


class QueryTypeClassifier:
    """
    Classifica query in 'case' o 'doctrine' con una singola chiamata LLM.
    Accetta sia OllamaClient che OpenAICompatClient (stessa interfaccia generate()).
    """

    def __init__(self, llm: "OllamaClient | OpenAICompatClient") -> None:
        self._llm = llm

    async def classify(self, query: str) -> QueryType:
        try:
            raw = await self._llm.generate(
                prompt=f"Domanda: {query}",
                system=_SYSTEM,
                temperature=0.0,
                max_tokens=20,
            )
            data = json.loads(raw.strip().strip("`").strip())
            qt = data.get("query_type", "case")
            if qt in ("case", "doctrine"):
                logger.info(f"[QueryClassifier] query_type={qt!r}")
                return qt  # type: ignore[return-value]
            logger.warning(f"[QueryClassifier] valore inatteso: {qt!r} — fallback 'case'")
        except Exception as exc:
            logger.warning(f"[QueryClassifier] errore: {exc} — fallback 'case'")
        return "case"
