"""
Chunker sliding window per testi legali.
Finestra: 512 token, overlap: 64 token.
Tokenizzazione: tiktoken cl100k_base (compatibile con molti LLM).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator
import tiktoken
from loguru import logger

_ENCODING = tiktoken.get_encoding("cl100k_base")


@dataclass
class TextChunk:
    index: int
    text: str
    token_count: int
    start_token: int
    end_token: int


class Chunker:
    """
    Sliding window chunker.

    Args:
        max_tokens:  dimensione massima di ogni chunk in token (default 512)
        overlap:     token di sovrapposizione tra chunk contigui (default 64)
        min_tokens:  chunk con meno token vengono scartati (default 20)
    """

    def __init__(
        self,
        max_tokens: int = 512,
        overlap: int = 64,
        min_tokens: int = 20,
    ) -> None:
        if overlap >= max_tokens:
            raise ValueError("overlap deve essere < max_tokens")
        self.max_tokens = max_tokens
        self.overlap = overlap
        self.min_tokens = min_tokens
        self._enc = _ENCODING

    def chunk(self, text: str) -> list[TextChunk]:
        """Divide il testo in chunk e ritorna la lista completa."""
        return list(self.iter_chunks(text))

    def iter_chunks(self, text: str) -> Iterator[TextChunk]:
        """Genera i chunk in modo lazy."""
        if not text or not text.strip():
            return

        tokens = self._enc.encode(text)
        total = len(tokens)

        if total == 0:
            return

        stride = self.max_tokens - self.overlap
        start = 0
        idx = 0

        while start < total:
            end = min(start + self.max_tokens, total)
            chunk_tokens = tokens[start:end]
            token_count = len(chunk_tokens)

            if token_count >= self.min_tokens:
                chunk_text = self._enc.decode(chunk_tokens)
                yield TextChunk(
                    index=idx,
                    text=chunk_text,
                    token_count=token_count,
                    start_token=start,
                    end_token=end,
                )
                idx += 1

            if end == total:
                break
            start += stride

    def count_tokens(self, text: str) -> int:
        """Conta i token di un testo senza chunking."""
        return len(self._enc.encode(text))
