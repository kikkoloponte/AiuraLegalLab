"""
Rimuove completamente un corpus da tutti gli indici (BM25 + Qdrant).

Utile quando MongoDB non ha più documenti per un corpus
ma BM25/Qdrant hanno ancora entries stantie.

Uso:
  python scripts/purge_corpus.py --corpus studio
  python scripts/purge_corpus.py --corpus studio --workspace mio-studio --dry-run
"""
from __future__ import annotations

import argparse
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

_DEFAULT_WORKSPACE = "mio-studio"
_WORKSPACES_BASE = Path(
    os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
)


# ─────────────────────────────────────────────────────────────────────────────
# BM25
# ─────────────────────────────────────────────────────────────────────────────

def purge_bm25_percorpus(ws_path: Path, corpus: str, dry_run: bool) -> int:
    """Elimina il pkl per-corpus se esiste. Ritorna numero doc rimossi."""
    pkl = ws_path / "indices" / f"bm25_{corpus}.pkl"
    if not pkl.exists():
        logger.info(f"BM25: bm25_{corpus}.pkl non trovato — niente da fare")
        return 0
    try:
        with open(pkl, "rb") as f:
            state = pickle.load(f)
        n = len(state.get("doc_ids", []))
        if dry_run:
            logger.info(f"BM25 [DRY-RUN]: eliminerei bm25_{corpus}.pkl ({n:,} doc)")
        else:
            pkl.unlink()
            logger.success(f"BM25: eliminato bm25_{corpus}.pkl ({n:,} doc rimossi)")
        return n
    except Exception as e:
        logger.error(f"BM25: errore lettura bm25_{corpus}.pkl — {e}")
        return 0


def purge_bm25_legacy(ws_path: Path, corpus: str, dry_run: bool) -> int:
    """
    Rimuove le entries del corpus dal pkl legacy monolitico (bm25.pkl).
    Riscrive il file senza quelle entries.
    """
    legacy = ws_path / "indices" / "bm25.pkl"
    if not legacy.exists():
        return 0
    try:
        with open(legacy, "rb") as f:
            state = pickle.load(f)
    except Exception as e:
        logger.error(f"BM25 legacy: errore lettura — {e}")
        return 0

    doc_ids        = state.get("doc_ids", [])
    doc_snippets   = state.get("doc_snippets", [])
    doc_metadata   = state.get("doc_metadata", [])
    doc_source_ids = state.get("doc_source_ids", [])
    tokenized      = state.get("corpus", state.get("tokenized", []))  # legacy compat
    chunk_meta     = state.get("chunk_meta", {})

    # Indici da MANTENERE (tutti tranne il corpus da purgare)
    keep = [
        i for i, m in enumerate(doc_metadata)
        if m.get("corpus", "studio") != corpus
    ]
    removed = len(doc_ids) - len(keep)

    if removed == 0:
        logger.info(f"BM25 legacy: nessuna entry corpus={corpus} trovata")
        return 0

    if dry_run:
        logger.info(
            f"BM25 legacy [DRY-RUN]: rimuoverei {removed:,} entries corpus={corpus} "
            f"(rimangono {len(keep):,})"
        )
        return removed

    new_state = {
        "doc_ids":        [doc_ids[i]        for i in keep],
        "doc_snippets":   [doc_snippets[i]   for i in keep] if doc_snippets   else [],
        "doc_metadata":   [doc_metadata[i]   for i in keep],
        "doc_source_ids": [doc_source_ids[i] for i in keep] if doc_source_ids else [],
        "corpus":         [tokenized[i]      for i in keep] if tokenized      else [],
        "chunk_meta":     {
            k: v for k, v in chunk_meta.items()
            if k in {doc_ids[i] for i in keep}
        },
        "bm25": None,   # BM25Okapi viene rebuildata al primo search
    }
    tmp = legacy.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        pickle.dump(new_state, f, protocol=pickle.HIGHEST_PROTOCOL)
    tmp.replace(legacy)
    logger.success(
        f"BM25 legacy: rimosso corpus={corpus} ({removed:,} entries), "
        f"riscritto bm25.pkl con {len(keep):,} doc"
    )
    return removed


# ─────────────────────────────────────────────────────────────────────────────
# Qdrant
# ─────────────────────────────────────────────────────────────────────────────

def purge_qdrant(corpus: str, dry_run: bool) -> int:
    """Elimina tutti i punti con payload.corpus == corpus da Qdrant."""
    qdrant_url = os.environ.get("QDRANT_URL", "").strip()
    if not qdrant_url:
        logger.warning("QDRANT_URL non impostato — skip Qdrant")
        return -1

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        client = QdrantClient(url=qdrant_url, timeout=30)

        existing = [col.name for col in client.get_collections().collections]
        if "legal_docs" not in existing:
            logger.info("Qdrant: collection 'legal_docs' non trovata — niente da fare")
            return 0

        # Conta prima
        count = client.count(
            "legal_docs",
            count_filter=Filter(must=[
                FieldCondition(key="corpus", match=MatchValue(value=corpus))
            ]),
        ).count

        if count == 0:
            logger.info(f"Qdrant: nessun punto corpus={corpus} trovato")
            return 0

        if dry_run:
            logger.info(f"Qdrant [DRY-RUN]: eliminerei {count:,} punti corpus={corpus}")
            return count

        client.delete(
            collection_name="legal_docs",
            points_selector=Filter(must=[
                FieldCondition(key="corpus", match=MatchValue(value=corpus))
            ]),
        )
        logger.success(f"Qdrant: eliminati {count:,} punti corpus={corpus}")
        return count

    except Exception as e:
        logger.error(f"Qdrant: errore — {e}")
        return -1


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rimuove un corpus da tutti gli indici BM25 + Qdrant",
    )
    parser.add_argument("--corpus", required=True,
                        help="Corpus da purgare (es. studio)")
    parser.add_argument("--workspace", default=_DEFAULT_WORKSPACE)
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa verrebbe rimosso senza toccare nulla")
    args = parser.parse_args()

    ws_path = _WORKSPACES_BASE / args.workspace
    dry = args.dry_run

    logger.info(f"Purge corpus='{args.corpus}' workspace='{args.workspace}'"
                + (" [DRY-RUN]" if dry else ""))

    # 1. pkl per-corpus (creato dalla migrazione)
    n1 = purge_bm25_percorpus(ws_path, args.corpus, dry)

    # 2. pkl legacy monolitico
    n2 = purge_bm25_legacy(ws_path, args.corpus, dry)

    # 3. Qdrant
    n3 = purge_qdrant(args.corpus, dry)

    if not dry:
        total_bm25 = (n1 or 0) + (n2 or 0)
        logger.info(
            f"\nRiepilogo:\n"
            f"  BM25 per-corpus:  {n1:,} doc rimossi\n"
            f"  BM25 legacy:      {n2:,} doc rimossi\n"
            f"  Qdrant:           {n3:,} punti rimossi\n"
            f"  Totale BM25:      {total_bm25:,}"
        )
        if total_bm25 > 0 or (n3 or 0) > 0:
            logger.success(f"Corpus '{args.corpus}' rimosso dagli indici.")
        else:
            logger.info("Niente da rimuovere.")


if __name__ == "__main__":
    main()
