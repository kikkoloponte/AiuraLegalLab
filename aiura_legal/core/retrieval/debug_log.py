"""
Retrieval debug logger — attivato da AIURA_DEBUG_RETRIEVAL=1.

Scrive un file logs/retrieval_debug.log con il flusso completo del retrieval:
  routing decision → BM25 per sub-indice → Vector → RRF fusion → Reranker I/O → fonti finali.

Uso:
  AIURA_DEBUG_RETRIEVAL=1 python -m aiura_legal.api

Il file viene ruotato a 20 MB, mantiene 5 rotazioni.
Quando la variabile non è settata, rlog() è un no-op a costo zero.
"""
from __future__ import annotations

import os
from pathlib import Path
from loguru import logger

_ENABLED: bool = os.getenv("AIURA_DEBUG_RETRIEVAL", "0") == "1"
_SINK_ID: int | None = None

_LOG_PATH = Path("logs/retrieval_debug.log")

_FORMAT = (
    "{time:HH:mm:ss.SSS} | {level:<5} | "
    "{extra[rtag]:<28} | {message}"
)


def _setup() -> None:
    global _SINK_ID
    if not _ENABLED or _SINK_ID is not None:
        return
    _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SINK_ID = logger.add(
        str(_LOG_PATH),
        level="DEBUG",
        filter=lambda r: "rtag" in r["extra"],
        format=_FORMAT,
        rotation="20 MB",
        retention=5,
        encoding="utf-8",
        enqueue=True,       # thread-safe (il retrieval usa ThreadPoolExecutor)
    )
    logger.info(f"[DebugLog] retrieval trace → {_LOG_PATH.resolve()}")


_setup()


def rlog(tag: str, msg: str) -> None:
    """Scrive una riga di trace nel file di debug. No-op se AIURA_DEBUG_RETRIEVAL != 1."""
    if _ENABLED:
        logger.bind(rtag=tag).debug(msg)


def rlog_sources(tag: str, sources: list, top: int = 10) -> None:
    """Logga la lista di SearchResult in forma compatta (source_id, score, corpus)."""
    if not _ENABLED:
        return
    rows = []
    for i, s in enumerate(sources[:top]):
        corpus = (s.metadata or {}).get("corpus", "?")
        sid = getattr(s, "source_id", "") or getattr(s, "doc_id", "?")
        score = getattr(s, "score", 0.0)
        method = getattr(s, "retrieval_method", "?")
        full = "✓" if getattr(s, "full_text", "") else "·"
        rows.append(f"  #{i+1:>2} [{corpus:<14}] {sid:<55} sc={score:+.4f} via={method} ft={full}")
    logger.bind(rtag=tag).debug("\n" + "\n".join(rows) if rows else "  (vuoto)")
