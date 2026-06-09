"""
ContextBudgetManager — assembla il prompt RAG rispettando n_ctx=4096.

Budget fisso:
  system prompt      ~300 tok
  phase prompt IQRAC ~400 tok
  normativa          ~800 tok  (top-1 full text + top-3 sommario)
  giurisprudenza     ~600 tok  (top-1 full text + top-2 sommario)
  dottrina/prassi    ~200 tok  (top-2 sommario)
  risposta           ~700 tok  (da ~200-300 attuali)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import tiktoken
from loguru import logger

if TYPE_CHECKING:
    from aiura_legal.ingestion.mongodb.models import Chunk

_ENCODING = tiktoken.get_encoding("cl100k_base")

_FALLBACK_SNIPPET_LEN = 150  # caratteri, non token


def _count_tokens(text: str) -> int:
    return len(_ENCODING.encode(text))


def _truncate_to_tokens(text: str, max_tokens: int) -> str:
    tokens = _ENCODING.encode(text)
    if len(tokens) <= max_tokens:
        return text
    return _ENCODING.decode(tokens[:max_tokens])


class ContextBudgetManager:
    """
    Assembla il prompt RAG rispettando un budget fisso per n_ctx=4096.

    Per ogni corpus:
      - I primi `full_text_slots` chunk usano il testo completo (troncato a
        `full_text_tokens` token).
      - I successivi `summary_slots` chunk usano chunk.sommario (se presente)
        o text[:150] come fallback, troncato a `summary_tokens` token.
    """

    BUDGETS: dict[str, dict[str, int]] = {
        "normativa": {
            "full_text_slots":  1,
            "summary_slots":    3,
            "full_text_tokens": 300,
            "summary_tokens":   40,
        },
        "giurisprudenza": {
            "full_text_slots":  1,
            "summary_slots":    2,
            "full_text_tokens": 250,
            "summary_tokens":   40,
        },
        "dottrina": {
            "full_text_slots":  0,
            "summary_slots":    2,
            "full_text_tokens": 0,
            "summary_tokens":   40,
        },
        "prassi": {
            "full_text_slots":  0,
            "summary_slots":    2,
            "full_text_tokens": 0,
            "summary_tokens":   40,
        },
    }

    # Fallback budget se corpus non riconosciuto
    _DEFAULT_BUDGET: dict[str, int] = {
        "full_text_slots":  1,
        "summary_slots":    2,
        "full_text_tokens": 200,
        "summary_tokens":   40,
    }

    def _budget(self, corpus: str) -> dict[str, int]:
        b = self.BUDGETS.get(corpus)
        if b is None:
            logger.warning(f"[ContextBudget] corpus {corpus!r} sconosciuto — uso default")
            return self._DEFAULT_BUDGET
        return b

    def format_chunks(self, chunks: list["Chunk"], corpus: str) -> str:
        """
        Formatta i chunk rispettando il budget di corpus:
        - I top `full_text_slots` chunk ricevono full text (troncato).
        - I restanti ricevono sommario o text[:150] come fallback.

        Ritorna stringa vuota se chunks è vuoto.
        """
        if not chunks:
            return ""

        budget = self._budget(corpus)
        full_slots     = budget["full_text_slots"]
        summary_slots  = budget["summary_slots"]
        full_tok       = budget["full_text_tokens"]
        summary_tok    = budget["summary_tokens"]

        total_slots = full_slots + summary_slots
        selected    = chunks[:total_slots]

        parts: list[str] = []
        for i, chunk in enumerate(selected):
            source_label = getattr(chunk, "source_id", "") or f"chunk-{i+1}"
            if i < full_slots and full_tok > 0:
                text = _truncate_to_tokens(chunk.text, full_tok)
                parts.append(f"[{i+1}] {source_label}\n{text}")
            else:
                # Sommario o fallback
                raw_summary = getattr(chunk, "sommario", None)
                if raw_summary:
                    summary = _truncate_to_tokens(raw_summary, summary_tok)
                else:
                    summary = _truncate_to_tokens(
                        chunk.text[:_FALLBACK_SNIPPET_LEN], summary_tok
                    )
                parts.append(f"[{i+1}] {source_label} (sintesi)\n{summary}")

        return "\n\n".join(parts)

    def format_research_packet(
        self,
        normativa_chunks: list["Chunk"],
        giurisprudenza_chunks: list["Chunk"],
        dottrina_chunks: list["Chunk"] = (),
        prassi_chunks: list["Chunk"] = (),
    ) -> str:
        """
        Assembla l'intero research packet come stringa formattata.
        Sezioni separate da marcatori: --- NORMATIVA --- ecc.
        Sezioni vuote (nessun chunk) sono omesse.
        """
        sections: list[str] = []

        norm_text = self.format_chunks(list(normativa_chunks), "normativa")
        if norm_text:
            sections.append(f"--- NORMATIVA ---\n{norm_text}")

        giuri_text = self.format_chunks(list(giurisprudenza_chunks), "giurisprudenza")
        if giuri_text:
            sections.append(f"--- GIURISPRUDENZA ---\n{giuri_text}")

        dott_text = self.format_chunks(list(dottrina_chunks), "dottrina")
        if dott_text:
            sections.append(f"--- DOTTRINA ---\n{dott_text}")

        prassi_text = self.format_chunks(list(prassi_chunks), "prassi")
        if prassi_text:
            sections.append(f"--- PRASSI ---\n{prassi_text}")

        return "\n\n".join(sections)
