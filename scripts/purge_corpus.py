"""
Rimuove un corpus stantio da Qdrant e dai pkl BM25 per-corpus.

Strategia rapida:
  1. Qdrant     → delete by filter corpus=X         (~1 secondo)
  2. bm25_X.pkl → cancella il file se esiste        (istantaneo)
  3. bm25.pkl   → NON toccato: verrà sostituito
                  dai pkl per-corpus alla prossima
                  migrazione (avviata da build_indexes
                  o build_jurisprudence_indexes)

Uso:
  python scripts/purge_corpus.py --corpus studio
  python scripts/purge_corpus.py --corpus studio --dry-run
  python scripts/purge_corpus.py --corpus studio --workspace mio-studio
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import pickle

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

_DEFAULT_WORKSPACE = "mio-studio"
_WORKSPACES_BASE = Path(
    os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
)


# ─────────────────────────────────────────────────────────────────────────────
# BM25 per-corpus pkl
# ─────────────────────────────────────────────────────────────────────────────

def _write_tombstone(pkl: Path) -> None:
    """Scrive un pkl vuoto (tombstone). La migrazione lo vede e salta il corpus."""
    state = {
        "doc_ids": [], "doc_snippets": [], "doc_metadata": [],
        "doc_source_ids": [], "tokenized": [], "chunk_meta": {},
        "bm25": None, "_tombstone": True,
    }
    pkl.parent.mkdir(parents=True, exist_ok=True)
    with open(pkl, "wb") as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)


def purge_bm25_percorpus(ws_path: Path, corpus: str, dry_run: bool) -> int:
    """
    Svuota bm25_{corpus}.pkl scrivendone uno vuoto (tombstone).
    Il tombstone impedisce alla migrazione di ricreare il corpus dal legacy bm25.pkl.
    Il legacy bm25.pkl non viene mai toccato.
    """
    pkl = ws_path / "indices" / f"bm25_{corpus}.pkl"

    if dry_run:
        if pkl.exists():
            logger.info(f"BM25 [DRY-RUN]: sovrascriverei {pkl.name} con tombstone vuoto")
        else:
            logger.info(f"BM25 [DRY-RUN]: creerei tombstone {pkl.name} (vuoto)")
        return 1

    _write_tombstone(pkl)
    if pkl.stat().st_size > 0:
        logger.success(f"BM25: tombstone scritto in {pkl.name} — corpus={corpus} bloccato dalla migrazione")
    return 1


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
        description="Rimuove un corpus stantio da Qdrant e dai pkl BM25 per-corpus",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python scripts/purge_corpus.py --corpus studio
  python scripts/purge_corpus.py --corpus studio --dry-run
        """,
    )
    parser.add_argument("--corpus", required=True,
                        help="Corpus da purgare (es. studio)")
    parser.add_argument("--workspace", default=_DEFAULT_WORKSPACE)
    parser.add_argument("--dry-run", action="store_true",
                        help="Mostra cosa verrebbe rimosso senza fare nulla")
    args = parser.parse_args()

    ws_path = _WORKSPACES_BASE / args.workspace
    dry = args.dry_run

    logger.info(
        f"Purge corpus='{args.corpus}' workspace='{args.workspace}'"
        + (" [DRY-RUN]" if dry else "")
    )

    n_bm25   = purge_bm25_percorpus(ws_path, args.corpus, dry)
    n_qdrant = purge_qdrant(args.corpus, dry)

    if not dry:
        logger.info(
            f"\nRiepilogo purge corpus='{args.corpus}':\n"
            f"  BM25 tombstone:  scritto ({args.corpus}.pkl vuoto — migrazione bloccata)\n"
            f"  Qdrant punti:    {n_qdrant if n_qdrant >= 0 else 'N/D (Qdrant non raggiungibile)'}\n"
            f"\n"
            f"  Il corpus '{args.corpus}' è ora a zero in tutti gli indici.\n"
            f"  La migrazione da bm25.pkl legacy non lo ricreera' mai piu'."
        )


if __name__ == "__main__":
    main()
