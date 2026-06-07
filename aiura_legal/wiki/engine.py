"""
WikiEngine — orchestra WikiStore e WikiWriter.
Punto di ingresso unico per la logica di filing post-query.
"""
from __future__ import annotations

from datetime import datetime, timezone

from loguru import logger

from aiura_legal.core.types import ResearchPacket
from aiura_legal.wiki.store import WikiPage, WikiStore
from aiura_legal.wiki.writer import WikiWriter, slugify


class WikiEngine:
    def __init__(self, store: WikiStore, writer: WikiWriter) -> None:
        self._store = store
        self._writer = writer

    async def file_response(
        self,
        query: str,
        response_text: str,
        research_packet: ResearchPacket,
        workspace: str = "default",
    ) -> None:
        """
        Fila una risposta approvata dal CitationReviewer nella wiki.
        Chiamato in fire-and-forget — non solleva eccezioni verso il chiamante.
        """
        try:
            await self._do_file(query, response_text, research_packet, workspace)
        except Exception as exc:
            logger.warning(f"WikiEngine.file_response failed (non-fatal): {exc}")

    async def _do_file(
        self,
        query: str,
        response_text: str,
        research_packet: ResearchPacket,
        workspace: str,
    ) -> None:
        concepts = await self._writer.extract_concepts(query, response_text)
        if not concepts:
            logger.debug("WikiEngine: no concepts extracted, skipping")
            return

        urns = [s.source_id for s in research_packet.sources if s.source_id]

        new_evidence = (
            f"Domanda: {query}\n\n"
            f"Risposta:\n{response_text}\n\n"
            f"Confidence: {research_packet.retrieval_confidence}"
        )

        for concept in concepts:
            slug = slugify(concept)
            if not slug:
                continue

            page = await self._store.get_page(slug, workspace)
            if page is None:
                page = WikiPage(
                    slug=slug,
                    title=concept.title(),
                    body_md="",
                    sources=[],
                    query_count=0,
                    workspace=workspace,
                )

            merged_body = await self._writer.merge_knowledge(page, new_evidence, urns)

            merged_sources = list(set(page.sources) | set(urns))

            page.body_md = merged_body
            page.sources = merged_sources
            page.query_count += 1
            page.last_updated = datetime.now(timezone.utc)
            page.version += 1

            await self._store.save_page(page)
            logger.info(
                f"WikiEngine filed: slug={slug} version={page.version} "
                f"sources={len(merged_sources)}"
            )
