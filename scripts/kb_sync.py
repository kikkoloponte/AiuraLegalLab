"""
Knowledge Base Sync Agent — allinea BM25 e Qdrant con MongoDB.

Confronta quanti chunk ha MongoDB vs BM25 vs Qdrant per ogni corpus.
Ricostruisce automaticamente solo i corpus fuori allineamento.

Uso:
  python scripts/kb_sync.py                    # mostra stato + chiede conferma
  python scripts/kb_sync.py --auto             # allinea senza chiedere
  python scripts/kb_sync.py --dry-run          # solo diagnosi, nessuna azione
  python scripts/kb_sync.py --corpus dottrina  # controlla/allinea solo dottrina
  python scripts/kb_sync.py --workspace altro  # workspace diverso da mio-studio
"""
from __future__ import annotations

import argparse
import asyncio
import pickle
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

import os
from loguru import logger

_DEFAULT_WORKSPACE = "mio-studio"
_WORKSPACES_BASE   = Path(
    os.environ.get("AIURA_WORKSPACES_PATH", "C:/project/AiUraLegalLab/workspaces")
)
_CORPORA           = ["normattiva", "dottrina", "studio"]   # gestiti da build_indexes.py
_DRIFT_THRESHOLD   = 0.02   # 2% di differenza = "in sync"
_DRIFT_MIN_CHUNKS  = 200    # soglia assoluta: sotto i 200 chunk di differenza = "in sync"


# ─────────────────────────────────────────────────────────────────────────────
# Strutture dati
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CorpusState:
    corpus: str
    mongo_count:  int = 0
    bm25_count:   int = 0
    qdrant_count: int = 0
    needs_rebuild: bool = False
    bm25_ok:  bool = True   # True = BM25 in sync con MongoDB
    qdrant_ok: bool = True  # True = Qdrant in sync con MongoDB
    reason: str = ""


# ─────────────────────────────────────────────────────────────────────────────
# Ispezione stato
# ─────────────────────────────────────────────────────────────────────────────

async def _mongo_counts(workspace: str) -> dict[str, int]:
    """Conta i chunk in aiura_legal.chunks per corpus (+ giurisprudenza dalla collection separata)."""
    from aiura_legal.ingestion.mongodb.client import MongoClient
    mongo = MongoClient.get()

    counts: dict[str, int] = {}
    for corpus in _CORPORA:
        counts[corpus] = await mongo.count_chunks(
            filter_query={"workspace": workspace, "corpus": corpus}
        )

    # Giurisprudenza viene dalla collection separata
    counts["giurisprudenza"] = await mongo.db["jurisprudence"].count_documents({})
    return counts


def _bm25_counts(ws_path: Path) -> dict[str, int]:
    """
    Conta i chunk BM25 per corpus leggendo i pkl per-corpus separati.
    Fallback: se esiste ancora bm25.pkl legacy (pre-migrazione), lo legge.
    """
    all_corpora = _CORPORA + ["giurisprudenza"]
    counts: dict[str, int] = {c: 0 for c in all_corpora}

    indices_dir = ws_path / "indices"

    # ── Nuovi pkl per-corpus (bm25_normattiva.pkl, ecc.) ──────────────────
    found_any = False
    for corpus in all_corpora:
        pkl = indices_dir / f"bm25_{corpus}.pkl"
        if not pkl.exists():
            continue
        try:
            with open(pkl, "rb") as f:
                state = pickle.load(f)
            counts[corpus] = len(state.get("doc_ids", []))
            found_any = True
        except Exception as e:
            logger.warning(f"BM25[{corpus}]: impossibile leggere pkl ({e})")

    if found_any:
        return counts

    # ── Fallback: pkl monolitico legacy ───────────────────────────────────
    legacy = indices_dir / "bm25.pkl"
    if not legacy.exists():
        return counts
    try:
        with open(legacy, "rb") as f:
            state = pickle.load(f)
        meta = state.get("doc_metadata", [])
        for m in meta:
            c = m.get("corpus", "studio")
            if c in counts:
                counts[c] += 1
        logger.info("BM25: lettura da pkl legacy (migrazione non ancora avvenuta)")
    except Exception as e:
        logger.warning(f"BM25: impossibile leggere pkl legacy ({e})")
    return counts


def _qdrant_counts() -> dict[str, int]:
    """Conta i punti in Qdrant per corpus via filtro payload."""
    qdrant_url = os.environ.get("QDRANT_URL", "").strip()
    if not qdrant_url:
        return {c: -1 for c in _CORPORA + ["giurisprudenza"]}   # -1 = non disponibile

    try:
        from qdrant_client import QdrantClient
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        c = QdrantClient(url=qdrant_url, timeout=10)

        existing = [col.name for col in c.get_collections().collections]
        if "legal_docs" not in existing:
            return {corpus: 0 for corpus in _CORPORA + ["giurisprudenza"]}

        counts: dict[str, int] = {}
        for corpus in _CORPORA + ["giurisprudenza"]:
            try:
                counts[corpus] = c.count(
                    "legal_docs",
                    count_filter=Filter(must=[
                        FieldCondition(key="corpus", match=MatchValue(value=corpus))
                    ]),
                ).count
            except Exception:
                counts[corpus] = 0
        return counts
    except Exception as e:
        logger.warning(f"Qdrant: impossibile connettersi ({e})")
        return {c: -1 for c in _CORPORA + ["giurisprudenza"]}


def _is_in_sync(mongo: int, index: int) -> bool:
    """True se l'indice è ragionevolmente allineato con MongoDB."""
    if mongo == 0 and index == 0:
        return True
    if mongo == 0:
        return False
    diff = abs(mongo - index)
    if diff <= _DRIFT_MIN_CHUNKS:
        return True
    return (diff / mongo) <= _DRIFT_THRESHOLD


# ─────────────────────────────────────────────────────────────────────────────
# Report
# ─────────────────────────────────────────────────────────────────────────────

def _print_report(states: list[CorpusState]) -> None:
    sep = "+" + "-"*17 + "+" + "-"*15 + "+" + "-"*15 + "+" + "-"*15 + "+" + "-"*15 + "+"
    print()
    print(sep)
    print(f"| {'Corpus':<15}  | {'MongoDB':>13} | {'BM25':>13} | {'Qdrant':>13} | {'Stato':<13} |")
    print(sep)
    for s in states:
        qdrant_str = f"{s.qdrant_count:>13,}" if s.qdrant_count >= 0 else "          N/D"
        if s.mongo_count == 0 and (s.bm25_count > 0 or s.qdrant_count > 0):
            stato = "⚠  STANTIO"
        elif s.needs_rebuild:
            stato = "!! DA REBUILD"
        else:
            stato = "   in sync"
        print(
            f"| {s.corpus:<15}  | {s.mongo_count:>13,} | {s.bm25_count:>13,} | {qdrant_str} | {stato:<13} |"
        )
    print(sep)
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Rebuild
# ─────────────────────────────────────────────────────────────────────────────

def _run_step(cmd: list[str], label: str) -> bool:
    logger.info(f"\n── {label} ──")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        logger.error(f"❌ {label} fallito (exit {result.returncode})")
        return False
    logger.success(f"✅ {label} completato")
    return True


def _rebuild(
    states: list[CorpusState],
    workspace: str,
    skip_vector: bool,
) -> None:
    python = sys.executable
    scripts = Path(__file__).parent
    needs = [s for s in states if s.needs_rebuild]

    if not needs:
        logger.success("Niente da ricostruire — KB già allineata.")
        return

    # Determina se serve un reset Qdrant:
    # Solo se normattiva è fuori sync (è il corpus "base") e Qdrant ha dati stantii.
    qdrant_needs_reset = any(
        s.corpus == "normattiva" and s.needs_rebuild and s.qdrant_count > 0
        for s in states
    )

    for s in needs:
        if s.corpus == "giurisprudenza":
            continue   # gestito separatamente sotto

        flags = ["--workspace", workspace, "--corpus", s.corpus]

        # Passa --skip-bm25 o --skip-vector per evitare rebuild inutili
        # (es. studio BM25 in sync → --skip-bm25, solo Qdrant upsert)
        if skip_vector or s.qdrant_ok:
            flags += ["--skip-vector"]
        if s.bm25_ok:
            flags += ["--skip-bm25"]

        if s.corpus == "normattiva" and qdrant_needs_reset and not s.qdrant_ok:
            flags += ["--reset-qdrant"]

        ok = _run_step(
            [python, str(scripts / "build_indexes.py")] + flags,
            f"Rebuild {s.corpus}",
        )
        if not ok:
            logger.error("Interruzione per errore. Gli altri corpus non verranno aggiornati.")
            sys.exit(1)

    # Giurisprudenza — usa build_jurisprudence_indexes.py (incrementale)
    giuri = next((s for s in needs if s.corpus == "giurisprudenza"), None)
    if giuri:
        ok = _run_step(
            [python, str(scripts / "build_jurisprudence_indexes.py"),
             "--workspace", workspace],
            "Rebuild giurisprudenza (incrementale)",
        )
        if not ok:
            sys.exit(1)

    logger.success("\n✅ KB sync completato. Riavvia l'API per caricare i nuovi indici.")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

async def main_async(
    workspace: str,
    corpus_filter: str | None,
    auto: bool,
    dry_run: bool,
    skip_vector: bool,
) -> None:
    ws_path = _WORKSPACES_BASE / workspace
    logger.info(f"KB Sync — workspace: {workspace}")

    # Raccoglie stato
    logger.info("Lettura stato MongoDB...")
    mongo_c = await _mongo_counts(workspace)

    logger.info("Lettura stato BM25...")
    bm25_c  = _bm25_counts(ws_path)

    logger.info("Lettura stato Qdrant...")
    qdrant_c = _qdrant_counts()

    # Analizza drift per ogni corpus
    all_corpora = _CORPORA + ["giurisprudenza"]
    if corpus_filter:
        all_corpora = [corpus_filter]

    states: list[CorpusState] = []
    for corpus in all_corpora:
        mc = mongo_c.get(corpus, 0)
        bc = bm25_c.get(corpus, 0)
        qc = qdrant_c.get(corpus, -1)

        # Corpus vuoto in MongoDB ma presente negli indici → purge automatica
        if mc == 0 and (bc > 0 or (qc > 0)):
            logger.warning(
                f"Corpus '{corpus}': MongoDB=0 ma BM25={bc:,}, Qdrant={qc:,} → "
                f"esegui: python scripts/purge_corpus.py --corpus {corpus}"
            )
            states.append(CorpusState(
                corpus=corpus,
                mongo_count=mc,
                bm25_count=bc,
                qdrant_count=qc,
                needs_rebuild=False,   # non è un rebuild, è un purge
                bm25_ok=True,
                qdrant_ok=True,
                reason=f"⚠ stantio (MongoDB vuoto) — usa purge_corpus.py",
            ))
            continue

        bm25_ok_flag  = _is_in_sync(mc, bc)
        qdrant_ok_flag = skip_vector or qc < 0 or _is_in_sync(mc, qc)

        needs = not bm25_ok_flag or not qdrant_ok_flag
        reasons = []
        if not bm25_ok_flag:
            reasons.append(f"BM25 {bc:,} vs MongoDB {mc:,}")
        if not qdrant_ok_flag:
            reasons.append(f"Qdrant {qc:,} vs MongoDB {mc:,}")

        states.append(CorpusState(
            corpus=corpus,
            mongo_count=mc,
            bm25_count=bc,
            qdrant_count=qc,
            needs_rebuild=needs,
            bm25_ok=bm25_ok_flag,
            qdrant_ok=qdrant_ok_flag,
            reason=" | ".join(reasons),
        ))

    # Report
    _print_report(states)

    needs_rebuild = [s for s in states if s.needs_rebuild]
    if not needs_rebuild:
        logger.success("KB completamente allineata. Nessuna azione necessaria.")
        return

    print(f"Corpus da ricostruire: {', '.join(s.corpus for s in needs_rebuild)}")
    for s in needs_rebuild:
        skips = []
        if s.bm25_ok:   skips.append("BM25 OK -> skip-bm25")
        if s.qdrant_ok: skips.append("Qdrant OK -> skip-vector")
        skip_note = f" [{', '.join(skips)}]" if skips else ""
        print(f"  * {s.corpus}: {s.reason}{skip_note}")
    print()

    if dry_run:
        logger.info("--dry-run: nessuna azione eseguita.")
        return

    if not auto:
        try:
            answer = input("Procedere con il rebuild? [s/N] ").strip().lower()
        except KeyboardInterrupt:
            print()
            logger.info("Annullato.")
            return
        if answer not in ("s", "si", "sì", "y", "yes"):
            logger.info("Annullato.")
            return

    _rebuild(states, workspace, skip_vector)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Knowledge Base Sync — allinea BM25 e Qdrant con MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python scripts/kb_sync.py                     # diagnosi + rebuild interattivo
  python scripts/kb_sync.py --auto              # allinea tutto senza chiedere
  python scripts/kb_sync.py --dry-run           # solo diagnosi
  python scripts/kb_sync.py --corpus dottrina   # solo dottrina
  python scripts/kb_sync.py --auto --skip-vector  # solo BM25
        """,
    )
    parser.add_argument("--workspace", default=_DEFAULT_WORKSPACE,
                        help=f"Nome workspace (default: {_DEFAULT_WORKSPACE})")
    parser.add_argument("--corpus", default=None,
                        choices=_CORPORA + ["giurisprudenza"],
                        help="Controlla/allinea solo questo corpus")
    parser.add_argument("--auto", action="store_true",
                        help="Rebuild automatico senza chiedere conferma")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo diagnosi — nessuna azione")
    parser.add_argument("--skip-vector", action="store_true",
                        help="Salta Qdrant (solo BM25)")
    args = parser.parse_args()

    asyncio.run(main_async(
        workspace=args.workspace,
        corpus_filter=args.corpus,
        auto=args.auto,
        dry_run=args.dry_run,
        skip_vector=args.skip_vector,
    ))


if __name__ == "__main__":
    main()
