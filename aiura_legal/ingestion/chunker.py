"""
Chunker sliding window per testi legali.

Chunker standard:      512 token, overlap 64  (corpus studio)
Dottrina/Prassi:       256 token, overlap 32  (Chunker(256, 32))
Normattiva:            adattivo via NormattivaChunker (vedi sotto)

Tokenizzazione: tiktoken cl100k_base (compatibile con molti LLM).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterator
import tiktoken
from loguru import logger

from aiura_legal.ingestion.text_normalizer import normalize_text

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

        text = normalize_text(text)
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


# ---------------------------------------------------------------------------
# Chunker adattivo per corpus normattiva
# ---------------------------------------------------------------------------

# NOTA: modifica chunk size invalida chunk esistenti — richiede rebuild completo
class NormattivaChunker:
    """
    Chunker adattivo per articoli normativi.

    Strategia:
      token_count <= 400  →  1 chunk = articolo intero
      token_count <= 800  →  split(size=256, overlap=32)
      token_count >  800  →  split(size=256, overlap=64)  (articoli molto lunghi)

    ~80% degli articoli rientra nel primo caso (≤ 400 token) e viene
    mantenuto intero per preservare coerenza semantica.
    """

    def __init__(self) -> None:
        self._enc = _ENCODING
        self._chunker_mid = Chunker(max_tokens=256, overlap=32)
        self._chunker_long = Chunker(max_tokens=256, overlap=64)

    def chunk(self, text: str) -> list[TextChunk]:
        """Divide l'articolo in chunk con strategia adattiva."""
        if not text or not text.strip():
            return []
        text = normalize_text(text)
        token_count = len(self._enc.encode(text))
        if token_count <= 400:
            # articolo breve: un singolo chunk
            return [
                TextChunk(
                    index=0,
                    text=text,
                    token_count=token_count,
                    start_token=0,
                    end_token=token_count,
                )
            ]
        elif token_count <= 800:
            return self._chunker_mid.chunk(text)
        else:
            return self._chunker_long.chunk(text)

    def count_tokens(self, text: str) -> int:
        return len(self._enc.encode(text))
