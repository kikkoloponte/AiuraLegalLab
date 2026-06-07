"""
WikiMiddleware — FastAPI middleware post-query.
Intercetta le risposte /query con reviewer_verdict PASS|WARN e fila in background.
Non blocca mai la risposta all'avvocato.
"""
from __future__ import annotations

import asyncio
import json
from typing import Callable, Optional

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from aiura_legal.wiki.engine import WikiEngine

_QUERY_PATH = "/query"
_PASS_VERDICTS = {"PASS", "WARN"}


class WikiMiddleware(BaseHTTPMiddleware):
    """
    Aggancia WikiEngine dopo ogni risposta di query approvata (PASS|WARN).

    Usa engine_factory (callable) invece di engine direttamente perché
    WikiEngine viene inizializzato nel lifespan, dopo la creazione del middleware.

    Field attesi nel JSON di risposta (QueryResponse schema):
      reviewer_verdict: "PASS"|"WARN"|"FAIL"
      answer:           testo risposta LLM
      query:            query originale
      workspace:        workspace corrente
      sources:          lista SourceItem (doc_id, source_id, score, snippet, ...)
      retrieval_confidence: HIGH|MEDIUM|LOW
    """

    def __init__(self, app, engine_factory: Callable[[], Optional[WikiEngine]]) -> None:
        super().__init__(app)
        self._engine_factory = engine_factory

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        if request.url.path != _QUERY_PATH or request.method != "POST":
            return response

        # Legge il body della response senza consumarlo (lo ricostruisce)
        body_bytes = b""
        async for chunk in response.body_iterator:
            body_bytes += chunk

        asyncio.create_task(self._try_file(body_bytes))

        return Response(
            content=body_bytes,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    async def _try_file(self, body_bytes: bytes) -> None:
        engine = self._engine_factory()
        if engine is None:
            return

        try:
            data = json.loads(body_bytes)
        except Exception:
            return

        verdict = data.get("reviewer_verdict", "")
        if verdict not in _PASS_VERDICTS:
            return

        query = data.get("query", "")
        response_text = data.get("answer", "")
        workspace = data.get("workspace", "default")
        raw_sources = data.get("sources", [])
        retrieval_confidence = data.get("retrieval_confidence", "LOW")

        if not query or not response_text:
            return

        try:
            from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult

            sources = [
                SearchResult(
                    doc_id=s.get("doc_id", ""),
                    score=s.get("score", 0.0),
                    snippet=s.get("snippet", ""),
                    metadata=s.get("metadata", {}),
                    source_id=s.get("source_id", ""),
                    retrieval_method=s.get("retrieval_method", ""),
                )
                for s in raw_sources
            ]
            packet = ResearchPacket(
                query_original=query,
                query_intent=QueryIntent.NORMA_LOOKUP,
                sources=sources,
                retrieval_confidence=retrieval_confidence,
            )
            await engine.file_response(query, response_text, packet, workspace)
        except Exception as exc:
            logger.warning(f"WikiMiddleware._try_file failed (non-fatal): {exc}")
