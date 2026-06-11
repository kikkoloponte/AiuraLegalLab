"""
ContextBudgetManager — assembla il prompt RAG rispettando n_ctx=8192.

Budget per corpus (token di testo fonte nel prompt):
  normativa          3 full text × 400 tok + 3 sintesi × 60 tok  ≈ 1380 tok
  giurisprudenza     3 full text × 500 tok + 2 sintesi × 60 tok  ≈ 1620 tok
  dottrina           1 full text × 200 tok + 2 sintesi × 60 tok  ≈  320 tok
  prassi             0 full text          + 2 sintesi × 60 tok  ≈  120 tok

Il resto del contesto (system prompt, framing, domanda, output della fase)
resta entro n_ctx=8192 con margine per max_tokens di generazione.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Union

import tiktoken
from loguru import logger

if TYPE_CHECKING:
    from aiura_legal.core.types import SearchResult
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


def _item_text(item: Union["Chunk", "SearchResult"]) -> str:
    """Testo completo di un Chunk (.text) o SearchResult (.full_text|.snippet)."""
    full = getattr(item, "full_text", "") or ""
    if full:
        return full
    text = getattr(item, "text", "") or ""
    if text:
        return text
    return getattr(item, "snippet", "") or ""


def _item_sommario(item: Union["Chunk", "SearchResult"]) -> str:
    """Sommario di un Chunk (.sommario) o SearchResult (metadata['sommario'])."""
    sommario = getattr(item, "sommario", None)
    if sommario:
        return str(sommario)
    meta = getattr(item, "metadata", None) or {}
    return str(meta.get("sommario", "") or "")


class ContextBudgetManager:
    """
    Assembla il prompt RAG rispettando un budget fisso per n_ctx=8192.

    Per ogni corpus:
      - I primi `full_text_slots` item usano il testo completo (troncato a
        `full_text_tokens` token).
      - I successivi `summary_slots` item usano il sommario (se presente)
        o il testo come fallback, troncato a `summary_tokens` token.

    Accetta sia Chunk (ingestione) che SearchResult (retrieval): per i
    SearchResult usa full_text se popolato (vedi source_texts), altrimenti
    lo snippet.
    """

    BUDGETS: dict[str, dict[str, int]] = {
        "normativa": {
            "full_text_slots":  3,
            "summary_slots":    3,
            "full_text_tokens": 400,
            "summary_tokens":   60,
        },
        "giurisprudenza": {
            "full_text_slots":  3,
            "summary_slots":    2,
            "full_text_tokens": 500,
            "summary_tokens":   60,
        },
        "dottrina": {
            "full_text_slots":  1,
            "summary_slots":    2,
            "full_text_tokens": 200,
            "summary_tokens":   60,
        },
        "prassi": {
            "full_text_slots":  0,
            "summary_slots":    2,
            "full_text_tokens": 0,
            "summary_tokens":   60,
        },
    }

    # Fallback budget se corpus non riconosciuto
    _DEFAULT_BUDGET: dict[str, int] = {
        "full_text_slots":  1,
        "summary_slots":    2,
        "full_text_tokens": 200,
        "summary_tokens":   60,
    }

    def _budget(self, corpus: str) -> dict[str, int]:
        b = self.BUDGETS.get(corpus)
        if b is None:
            logger.warning(f"[ContextBudget] corpus {corpus!r} sconosciuto — uso default")
            return self._DEFAULT_BUDGET
        return b

    def budget_texts(
        self,
        items: list[Union["Chunk", "SearchResult"]],
        corpus: str,
    ) -> list[str]:
        """
        Calcola il testo da inserire nel prompt per ogni item, secondo il
        budget del corpus. Item oltre full_text_slots+summary_slots ricevono
        comunque una sintesi (mai stringa vuota): la selezione top-k spetta
        al retrieval, non al budget manager.
        """
        budget = self._budget(corpus)
        full_slots  = budget["full_text_slots"]
        full_tok    = budget["full_text_tokens"]
        summary_tok = budget["summary_tokens"]

        texts: list[str] = []
        for i, item in enumerate(items):
            if i < full_slots and full_tok > 0:
                texts.append(_truncate_to_tokens(_item_text(item), full_tok))
            else:
                raw_summary = _item_sommario(item)
                if not raw_summary:
                    raw_summary = _item_text(item)[: _FALLBACK_SNIPPET_LEN * 4]
                texts.append(_truncate_to_tokens(raw_summary, summary_tok))
        return texts

    def format_chunks(
        self,
        chunks: list[Union["Chunk", "SearchResult"]],
        corpus: str,
    ) -> str:
        """
        Formatta gli item rispettando il budget di corpus:
        - I top `full_text_slots` ricevono full text (troncato).
        - I restanti ricevono sommario o testo troncato come fallback.

        Ritorna stringa vuota se chunks è vuoto.
        """
        if not chunks:
            return ""

        budget = self._budget(corpus)
        total_slots = budget["full_text_slots"] + budget["summary_slots"]
        selected = chunks[:total_slots]
        texts = self.budget_texts(selected, corpus)

        parts: list[str] = []
        for i, (chunk, text) in enumerate(zip(selected, texts)):
            source_label = getattr(chunk, "source_id", "") or f"chunk-{i+1}"
            if i < budget["full_text_slots"] and budget["full_text_tokens"] > 0:
                parts.append(f"[{i+1}] {source_label}\n{text}")
            else:
                parts.append(f"[{i+1}] {source_label} (sintesi)\n{text}")

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
