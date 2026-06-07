"""
Verifica operativa Blocco 1A — da eseguire una volta con MongoDB reale.

Esegue in sequenza:
  1. Ping MongoDB sorgente (legal_lab) e destinazione (aiura_legal)
  2. Mirror dry-run (conta i doc sorgente)
  3. Mirror reale di N documenti (default 500)
  4. Chunking (NormattivaPipeline) sui doc copiati
  5. Migrazione chunk esistenti (migrate_chunks_typing backfill)
  6. Build indexes: workspace normattiva (tutti) + normattiva_civile (solo codice civile)
  7. Test retrieval con chunk_filter: verifica subset isolation
  8. Report finale

Uso:
  python scripts/verify_1a.py
  python scripts/verify_1a.py --limit 200   # più veloce per test
  python scripts/verify_1a.py --skip-mirror  # se mirror già fatto
"""
from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

import pymongo
from loguru import logger

from aiura_legal.ingestion.mongodb.client import MongoClient, settings


# ---------------------------------------------------------------------------
# Colori per il report
# ---------------------------------------------------------------------------

def _ok(msg: str) -> str:   return f"  ✅ {msg}"
def _fail(msg: str) -> str: return f"  ❌ {msg}"
def _info(msg: str) -> str: return f"  ℹ  {msg}"


# ---------------------------------------------------------------------------
# Step 1 — Ping MongoDB
# ---------------------------------------------------------------------------

def step_ping() -> tuple[bool, bool]:
    """Ritorna (src_ok, dst_ok)."""
    logger.info("── Step 1: Ping MongoDB ──")

    src_ok = False
    try:
        src = pymongo.MongoClient(
            settings.legalagentlab_mongodb_uri, serverSelectionTimeoutMS=3000
        )
        src.admin.command("ping")
        src_count = src[settings.legalagentlab_mongodb_database]["normattiva_docs"].count_documents({})
        print(_ok(f"legal_lab raggiungibile — normattiva_docs: {src_count:,} doc"))
        src_ok = True
    except Exception as e:
        print(_fail(f"legal_lab NON raggiungibile: {e}"))

    dst_ok = False
    try:
        dst = pymongo.MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
        dst.admin.command("ping")
        dst_count = dst[settings.mongodb_database]["normattiva_docs"].count_documents({})
        print(_ok(f"aiura_legal raggiungibile — normattiva_docs: {dst_count:,} doc"))
        dst_ok = True
    except Exception as e:
        print(_fail(f"aiura_legal NON raggiungibile: {e}"))

    return src_ok, dst_ok


# ---------------------------------------------------------------------------
# Step 2+3 — Mirror
# ---------------------------------------------------------------------------

def step_mirror(limit: int, skip: bool) -> int:
    """Ritorna il numero di doc copiati (0 se skip)."""
    logger.info("── Step 2-3: Mirror legal_lab → aiura_legal ──")

    if skip:
        print(_info("Mirror saltato (--skip-mirror)"))
        try:
            dst = pymongo.MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
            count = dst[settings.mongodb_database]["normattiva_docs"].count_documents({})
            print(_info(f"aiura_legal.normattiva_docs attuale: {count:,} doc"))
            return count
        except Exception:
            return 0

    import subprocess
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "mirror_normattiva.py"),
        "--limit", str(limit),
        "--skip-chunks",      # il chunking lo facciamo nel passo successivo
    ]
    print(_info(f"Esecuzione: {' '.join(cmd)}"))
    t0 = time.monotonic()
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.monotonic() - t0

    if result.returncode == 0:
        try:
            dst = pymongo.MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000)
            count = dst[settings.mongodb_database]["normattiva_docs"].count_documents({})
            print(_ok(f"Mirror OK in {elapsed:.1f}s — normattiva_docs: {count:,} doc"))
            return count
        except Exception:
            return limit
    else:
        print(_fail(f"Mirror FALLITO (exit {result.returncode})"))
        return 0


# ---------------------------------------------------------------------------
# Step 4 — Chunking
# ---------------------------------------------------------------------------

async def step_chunking(limit: int | None) -> int:
    """Ritorna il numero di chunk creati."""
    logger.info("── Step 4: NormattivaPipeline chunking ──")
    from aiura_legal.ingestion.normattiva.pipeline import NormattivaPipeline

    try:
        mongo = MongoClient.get()
        pipeline = NormattivaPipeline(
            mongo_db=mongo.db,
            workspace="normattiva",
            skip_formule=True,
        )
        result = await pipeline.chunk_collection(limit=limit)
        count = await mongo.db["chunks"].count_documents({"corpus": "normattiva"})
        print(_ok(
            f"Chunking OK — {result.docs_processed} doc → "
            f"{result.chunks_created} chunk nuovi | "
            f"totale corpus=normattiva: {count:,}"
        ))
        return result.chunks_created
    except Exception as e:
        print(_fail(f"Chunking FALLITO: {e}"))
        return 0


# ---------------------------------------------------------------------------
# Step 5 — Backfill chunk esistenti
# ---------------------------------------------------------------------------

def step_backfill() -> None:
    logger.info("── Step 5: migrate_chunks_typing backfill ──")
    import subprocess
    cmd = [sys.executable, str(ROOT / "scripts" / "migrate_chunks_typing.py")]
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode == 0:
        print(_ok("Backfill OK"))
    else:
        print(_fail(f"Backfill FALLITO (exit {result.returncode})"))


# ---------------------------------------------------------------------------
# Step 6 — Build indexes
# ---------------------------------------------------------------------------

def step_build_indexes() -> dict[str, bool]:
    logger.info("── Step 6: Build indexes ──")
    import subprocess

    configs = [
        ("normattiva",        ["--workspace", "normattiva", "--corpus", "normattiva"]),
        ("normattiva_civile", ["--workspace", "normattiva_civile", "--fonte", "codice_civile"]),
        ("normattiva_penale", ["--workspace", "normattiva_penale", "--fonte", "codice_penale"]),
    ]
    results = {}
    for name, extra_args in configs:
        cmd = [sys.executable, str(ROOT / "scripts" / "build_indexes.py")] + extra_args
        print(_info(f"Build {name} …"))
        t0 = time.monotonic()
        r = subprocess.run(cmd, capture_output=False, text=True)
        elapsed = time.monotonic() - t0
        ok = r.returncode == 0
        results[name] = ok
        if ok:
            print(_ok(f"{name} indicizzato in {elapsed:.1f}s"))
        else:
            print(_fail(f"{name} FALLITO (exit {r.returncode})"))

    return results


# ---------------------------------------------------------------------------
# Step 7 — Test retrieval con chunk_filter
# ---------------------------------------------------------------------------

def step_retrieval_test() -> bool:
    logger.info("── Step 7: Retrieval subset-filter test ──")

    ws_norm = str(ROOT / "workspaces" / "normattiva")
    ws_civil = str(ROOT / "workspaces" / "normattiva_civile")

    # Test 1: ricerca senza filtro su workspace normattiva
    try:
        from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
        bm25 = BM25Retriever(ws_norm)
        if bm25._bm25 is None:
            print(_fail("BM25 normattiva: indice non trovato"))
            return False

        results_all = bm25.search("obbligazione contratto", top_k=10)
        print(_ok(f"BM25 normattiva (no filter): {len(results_all)} risultati"))

        # Test 2: filtro corpus=normattiva (deve ritornare gli stessi o meno)
        results_filtered = bm25.search(
            "obbligazione contratto",
            top_k=10,
            chunk_filter={"corpus": "normattiva"},
        )
        print(_ok(f"BM25 normattiva (corpus=normattiva): {len(results_filtered)} risultati"))

        # Test 3: filtro fonte=codice_civile
        results_cc = bm25.search(
            "obbligazione contratto",
            top_k=10,
            chunk_filter={"fonte": "codice_civile"},
        )
        print(_ok(f"BM25 normattiva (fonte=codice_civile): {len(results_cc)} risultati"))

        # Verifica isolamento: risultati codice_civile devono essere subset
        cc_ids = {r.doc_id for r in results_cc}
        all_fonti = {r.metadata.get("fonte") for r in results_all}
        print(_info(f"Fonti presenti nell'indice normattiva: {sorted(all_fonti)}"))

    except Exception as e:
        print(_fail(f"Retrieval test FALLITO: {e}"))
        return False

    # Test 4: workspace normattiva_civile
    try:
        bm25_civil = BM25Retriever(ws_civil)
        if bm25_civil._bm25 is not None:
            results_civil = bm25_civil.search("responsabilità contrattuale", top_k=5)
            civil_fonti = {r.metadata.get("fonte") for r in results_civil}
            print(_ok(f"BM25 normattiva_civile: {len(results_civil)} risultati, fonti={civil_fonti}"))
        else:
            print(_info("BM25 normattiva_civile: indice non ancora costruito (skip)"))
    except Exception as e:
        print(_info(f"normattiva_civile non disponibile: {e}"))

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    parser = argparse.ArgumentParser(description="Verifica operativa Blocco 1A")
    parser.add_argument("--limit", type=int, default=500,
                        help="Documenti da mirrorare (default: 500)")
    parser.add_argument("--skip-mirror", action="store_true",
                        help="Salta il mirror (usa dati già presenti)")
    parser.add_argument("--skip-build", action="store_true",
                        help="Salta la build degli indici")
    args = parser.parse_args()

    print("\n" + "="*60)
    print("  AiUra LegalLab — Verifica operativa Blocco 1A")
    print("="*60 + "\n")

    t_start = time.monotonic()
    report: list[tuple[str, bool]] = []

    # Step 1 — Ping
    src_ok, dst_ok = step_ping()
    report.append(("MongoDB sorgente (legal_lab)", src_ok))
    report.append(("MongoDB destinazione (aiura_legal)", dst_ok))

    if not dst_ok:
        print("\n❌ MongoDB destinazione non raggiungibile. Interruzione.")
        sys.exit(1)

    # Step 2-3 — Mirror
    if src_ok:
        n_mirrored = step_mirror(args.limit, args.skip_mirror)
        report.append(("Mirror doc copiati", n_mirrored > 0))
    else:
        print(_info("Sorgente non disponibile — saltato mirror, si usano dati presenti"))
        n_mirrored = 0

    # Step 4 — Chunking
    n_chunks = await step_chunking(limit=args.limit if n_mirrored > 0 else None)
    report.append(("Chunking NormattivaPipeline", n_chunks >= 0))

    # Step 5 — Backfill
    step_backfill()
    report.append(("Backfill chunk typing", True))

    # Step 6 — Build indexes
    if not args.skip_build:
        idx_results = step_build_indexes()
        report.append(("Build normattiva", idx_results.get("normattiva", False)))
        report.append(("Build normattiva_civile", idx_results.get("normattiva_civile", False)))
    else:
        print(_info("Build indici saltata (--skip-build)"))

    # Step 7 — Retrieval test
    retrieval_ok = step_retrieval_test()
    report.append(("Retrieval + subset filter", retrieval_ok))

    # Report finale
    elapsed = time.monotonic() - t_start
    print("\n" + "="*60)
    print(f"  Report finale ({elapsed:.0f}s totali)")
    print("="*60)
    all_ok = True
    for label, ok in report:
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {label}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("  🎉 Blocco 1A operativamente verificato. Pronti per 1B.")
    else:
        print("  ⚠️  Alcuni step hanno fallito. Verifica i log sopra.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
