"""
rebuild_knowledge_base.py — orchestratore reset + reload KB da MongoDB.

Esegue 7 fasi sequenziali per ricostruire completamente il knowledge base
con il nuovo schema Chunk V2 (campo settore + metadati dottrina).

══════════════════════════════════════════════════════════════
  AVVERTENZE
══════════════════════════════════════════════════════════════

  - Il database legal_lab (LegalAgentLab) è READ-ONLY.
    Questo script legge da legal_lab.normattiva_docs ma scrive
    SOLO in aiura_legal_lab_db.chunks.

  - Fase 1 DROP è IRREVERSIBILE per il workspace specificato.
    Usa --dry-run per vedere cosa farebbe prima di eseguire.

  - Tempo stimato: ~50 min (normattiva 20 min + dottrina 5 min
    + indexing 25 min). Usa --from-phase per riprendere.

══════════════════════════════════════════════════════════════
  USO
══════════════════════════════════════════════════════════════

  # Run completo
  python scripts/rebuild_knowledge_base.py --workspace mio-studio

  # Dry-run (nessuna scrittura)
  python scripts/rebuild_knowledge_base.py --workspace mio-studio --dry-run

  # Riprendi dalla fase 4 (dopo crash durante indexing)
  python scripts/rebuild_knowledge_base.py --workspace mio-studio --from-phase 4

  # Salta fase 7 (nessuna giurisprudenza)
  python scripts/rebuild_knowledge_base.py --workspace mio-studio --skip-phase 7

  # Dopo rebuild: attiva filtro settore
  export AIURA_SETTORE_FILTER=1

══════════════════════════════════════════════════════════════
  FASI
══════════════════════════════════════════════════════════════

  0  Backup pkl BM25 (rinomina con timestamp)
  1  Drop aiura_legal_lab_db.chunks (filtro workspace)
  2  NormattivaPipeline: rechunk da legal_lab.normattiva_docs
     con settore + titolo_articolo su ogni chunk
  3  DottrinaMetadataExtractor: $set metadati su chunk dottrina
  4  build_indexes.py --corpus normattiva
  5  build_indexes.py --corpus dottrina
  6  build_indexes.py --corpus studio (se esistono doc)
  7  build_jurisprudence_indexes.py (se esistono sentenze)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

PROJECT_ROOT = Path(__file__).parent.parent
CHECKPOINT_FILE = PROJECT_ROOT / "rebuild_state.json"
BM25_DIR = PROJECT_ROOT / "data" / "bm25"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

PHASE_NAMES = {
    0: "Backup BM25 pkl",
    1: "Drop chunks (workspace)",
    2: "NormattivaPipeline rechunk",
    3: "DottrinaMetadataExtractor $set",
    4: "build_indexes normattiva",
    5: "build_indexes dottrina",
    6: "build_indexes studio",
    7: "build_jurisprudence_indexes",
}


# ---------------------------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------------------------

def _load_checkpoint() -> dict:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_checkpoint(state: dict) -> None:
    CHECKPOINT_FILE.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _update_phase(state: dict, phase: int, status: str, detail: str = "") -> None:
    state[str(phase)] = {
        "phase": phase,
        "name": PHASE_NAMES[phase],
        "status": status,
        "detail": detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _save_checkpoint(state)


# ---------------------------------------------------------------------------
# Fase 0: Backup BM25 pkl
# ---------------------------------------------------------------------------

def phase0_backup_bm25(dry_run: bool, state: dict) -> None:
    logger.info("[Fase 0] Backup BM25 pkl esistenti...")
    if not BM25_DIR.exists():
        logger.info("[Fase 0] Nessuna directory BM25 trovata — skip backup")
        _update_phase(state, 0, "completed", "nessun pkl da backuppare")
        return

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    pkl_files = list(BM25_DIR.glob("*.pkl"))

    if not pkl_files:
        logger.info("[Fase 0] Nessun file pkl trovato — skip backup")
        _update_phase(state, 0, "completed", "nessun pkl da backuppare")
        return

    backup_dir = BM25_DIR.parent / f"bm25_backup_{ts}"
    if not dry_run:
        backup_dir.mkdir(parents=True, exist_ok=True)
        for pkl in pkl_files:
            shutil.copy2(pkl, backup_dir / pkl.name)
            logger.info(f"[Fase 0] Backup: {pkl.name} -> {backup_dir}")
    else:
        logger.info(f"[DRY-RUN] Copierebbe {len(pkl_files)} pkl in {backup_dir}")

    _update_phase(state, 0, "completed", f"{len(pkl_files)} pkl in {backup_dir}")


# ---------------------------------------------------------------------------
# Fase 1: Drop chunks
# ---------------------------------------------------------------------------

async def phase1_drop_chunks(
    workspace: str | None,
    dry_run: bool,
    state: dict,
) -> None:
    logger.info("[Fase 1] Drop chunks in aiura_legal_lab_db...")
    from aiura_legal.ingestion.mongodb.client import MongoClient

    client = MongoClient()
    db = client.db

    query: dict = {}
    if workspace:
        query["workspace"] = workspace

    if dry_run:
        count = await db.chunks.count_documents(query)
        logger.info(f"[DRY-RUN] Eliminerebbe {count} chunk (query: {query})")
        _update_phase(state, 1, "completed", f"dry-run: {count} chunk")
        return

    result = await db.chunks.delete_many(query)
    deleted = result.deleted_count
    logger.info(f"[Fase 1] Eliminati {deleted} chunk")
    _update_phase(state, 1, "completed", f"{deleted} chunk eliminati")


# ---------------------------------------------------------------------------
# Fase 2: NormattivaPipeline rechunk
# ---------------------------------------------------------------------------

async def phase2_normattiva_pipeline(
    workspace: str,
    dry_run: bool,
    state: dict,
) -> None:
    logger.info("[Fase 2] NormattivaPipeline rechunk da legal_lab.normattiva_docs...")
    from aiura_legal.ingestion.normattiva.pipeline import NormattivaPipeline
    from aiura_legal.ingestion.mongodb.client import MongoClient

    if dry_run:
        # Conta solo i doc sorgente (legge da legal_lab — read-only)
        from motor.motor_asyncio import AsyncIOMotorClient
        import os
        mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        src_client = AsyncIOMotorClient(mongo_uri)
        count = await src_client["legal_lab"]["normattiva_docs"].count_documents({})
        logger.info(f"[DRY-RUN] Rechunkerebbe {count} documenti normattiva")
        src_client.close()
        _update_phase(state, 2, "completed", f"dry-run: {count} doc sorgente")
        return

    client = MongoClient()
    pipeline = NormattivaPipeline(mongo_db=client.db, workspace=workspace)
    result = await pipeline.chunk_collection()

    logger.info(
        f"[Fase 2] Completato: {result.docs_processed} doc, "
        f"{result.chunks_created} chunk, {result.errors} errori"
    )
    _update_phase(
        state, 2, "completed",
        f"{result.docs_processed} doc, {result.chunks_created} chunk"
    )


# ---------------------------------------------------------------------------
# Fase 3: DottrinaMetadataExtractor
# ---------------------------------------------------------------------------

async def phase3_dottrina_metadata(
    workspace: str | None,
    dry_run: bool,
    state: dict,
) -> None:
    logger.info("[Fase 3] DottrinaMetadataExtractor — arricchimento metadati dottrina...")
    from aiura_legal.ingestion.dottrina.metadata_extractor import DottrinaMetadataExtractor
    from aiura_legal.ingestion.mongodb.client import MongoClient

    client = MongoClient()

    # Verifica se ci sono chunk dottrina
    count = await client.db.chunks.count_documents({"corpus": "dottrina"})
    if count == 0:
        logger.info("[Fase 3] Nessun chunk dottrina trovato — skip")
        _update_phase(state, 3, "skipped", "nessun chunk dottrina")
        return

    extractor = DottrinaMetadataExtractor(client.db)
    stats = await extractor.run(workspace=workspace, dry_run=dry_run)

    logger.info(f"[Fase 3] Stats: {stats}")
    _update_phase(
        state, 3, "completed",
        f"updated={stats['updated']} skipped={stats['skipped']} errors={stats['errors']}"
    )


# ---------------------------------------------------------------------------
# Fasi 4-7: build_indexes via subprocess
# ---------------------------------------------------------------------------

def _run_build_indexes(
    corpus: str,
    workspace: str,
    dry_run: bool,
    state: dict,
    phase: int,
) -> bool:
    """Esegue build_indexes.py per un corpus via subprocess. Ritorna True se OK."""
    if dry_run:
        logger.info(f"[DRY-RUN] Eseguirebbe: build_indexes.py --corpus {corpus}")
        _update_phase(state, phase, "completed", f"dry-run: {corpus}")
        return True

    cmd = [
        sys.executable,
        str(SCRIPTS_DIR / "build_indexes.py"),
        "--workspace", workspace,
        "--corpus", corpus,
    ]
    logger.info(f"[Fase {phase}] {' '.join(cmd)}")
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=False)
    elapsed = time.time() - t0

    if result.returncode != 0:
        logger.error(f"[Fase {phase}] FALLITA (returncode={result.returncode})")
        _update_phase(state, phase, "failed", f"returncode={result.returncode}")
        return False

    logger.info(f"[Fase {phase}] Completata in {elapsed:.0f}s")
    _update_phase(state, phase, "completed", f"{elapsed:.0f}s")
    return True


async def phase4_index_normattiva(workspace: str, dry_run: bool, state: dict) -> bool:
    logger.info("[Fase 4] build_indexes --corpus normattiva...")
    return _run_build_indexes("normattiva", workspace, dry_run, state, 4)


async def phase5_index_dottrina(
    workspace: str, dry_run: bool, state: dict
) -> bool:
    logger.info("[Fase 5] build_indexes --corpus dottrina...")
    from aiura_legal.ingestion.mongodb.client import MongoClient
    client = MongoClient()
    count = await client.db.chunks.count_documents({"corpus": "dottrina"})
    if count == 0:
        logger.info("[Fase 5] Nessun chunk dottrina — skip")
        _update_phase(state, 5, "skipped", "nessun chunk dottrina")
        return True
    return _run_build_indexes("dottrina", workspace, dry_run, state, 5)


async def phase6_index_studio(workspace: str, dry_run: bool, state: dict) -> bool:
    logger.info("[Fase 6] build_indexes --corpus studio...")
    from aiura_legal.ingestion.mongodb.client import MongoClient
    client = MongoClient()
    count = await client.db.chunks.count_documents({"corpus": "studio"})
    if count == 0:
        logger.info("[Fase 6] Nessun chunk studio — skip")
        _update_phase(state, 6, "skipped", "nessun chunk studio")
        return True
    return _run_build_indexes("studio", workspace, dry_run, state, 6)


async def phase7_index_giurisprudenza(
    workspace: str,
    dry_run: bool,
    state: dict,
    organi: list[str],
) -> bool:
    logger.info("[Fase 7] build_jurisprudence_indexes...")
    from aiura_legal.ingestion.mongodb.client import MongoClient
    client = MongoClient()
    count = await client.db.chunks.count_documents({"corpus": "giurisprudenza"})
    if count == 0:
        logger.info("[Fase 7] Nessun chunk giurisprudenza — skip")
        _update_phase(state, 7, "skipped", "nessun chunk giurisprudenza")
        return True

    if dry_run:
        logger.info(f"[DRY-RUN] Eseguirebbe: build_jurisprudence_indexes.py --organo {organi}")
        _update_phase(state, 7, "completed", "dry-run")
        return True

    ok = True
    for organo in organi:
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "build_jurisprudence_indexes.py"),
            "--workspace", workspace,
            "--organo", organo,
        ]
        logger.info(f"[Fase 7] {' '.join(cmd)}")
        t0 = time.time()
        result = subprocess.run(cmd, capture_output=False)
        elapsed = time.time() - t0
        if result.returncode != 0:
            logger.error(f"[Fase 7] FALLITA per organo={organo}")
            ok = False
        else:
            logger.info(f"[Fase 7] organo={organo} completato in {elapsed:.0f}s")

    _update_phase(state, 7, "completed" if ok else "failed", f"organi={organi}")
    return ok


# ---------------------------------------------------------------------------
# Orchestratore principale
# ---------------------------------------------------------------------------

async def main(args: argparse.Namespace) -> None:
    workspace = args.workspace
    dry_run = args.dry_run
    from_phase = args.from_phase
    skip_phases: set[int] = set(args.skip_phase or [])
    organi = args.organi or ["cassazione", "corte_cost"]

    logger.info("=" * 60)
    logger.info("AiUra LegalLab — rebuild_knowledge_base")
    logger.info(f"  workspace  : {workspace}")
    logger.info(f"  dry_run    : {dry_run}")
    logger.info(f"  from_phase : {from_phase}")
    logger.info(f"  skip_phases: {skip_phases}")
    logger.info("=" * 60)

    state = _load_checkpoint()

    # Determina da quale fase partire
    start_phase = from_phase
    if start_phase is None:
        # Riprendi automaticamente dall'ultima fase fallita o non eseguita
        completed = {int(k) for k, v in state.items() if v.get("status") == "completed"}
        failed = {int(k) for k, v in state.items() if v.get("status") == "failed"}
        if failed:
            start_phase = min(failed)
            logger.info(f"[Checkpoint] Riprendo dalla fase fallita: {start_phase}")
        else:
            start_phase = max(completed) + 1 if completed else 0
            if completed:
                logger.info(
                    f"[Checkpoint] Ultime fasi completate: {sorted(completed)}. "
                    f"Riprendo da fase {start_phase}."
                )

    t_total = time.time()

    for phase in range(start_phase, 8):
        if phase in skip_phases:
            logger.info(f"[Fase {phase}] SKIP (--skip-phase)")
            _update_phase(state, phase, "skipped", "--skip-phase")
            continue

        phase_name = PHASE_NAMES[phase]
        logger.info(f"\n{'─' * 50}")
        logger.info(f"  Fase {phase}: {phase_name}")
        logger.info(f"{'─' * 50}")
        t0 = time.time()

        try:
            if phase == 0:
                phase0_backup_bm25(dry_run, state)
            elif phase == 1:
                await phase1_drop_chunks(workspace, dry_run, state)
            elif phase == 2:
                await phase2_normattiva_pipeline(workspace or "default", dry_run, state)
            elif phase == 3:
                await phase3_dottrina_metadata(workspace, dry_run, state)
            elif phase == 4:
                ok = await phase4_index_normattiva(workspace or "default", dry_run, state)
                if not ok:
                    logger.error(f"Fase {phase} fallita — interruzione. Usa --from-phase {phase} per riprendere.")
                    sys.exit(1)
            elif phase == 5:
                ok = await phase5_index_dottrina(workspace or "default", dry_run, state)
                if not ok:
                    logger.error(f"Fase {phase} fallita — interruzione.")
                    sys.exit(1)
            elif phase == 6:
                ok = await phase6_index_studio(workspace or "default", dry_run, state)
                if not ok:
                    logger.error(f"Fase {phase} fallita — interruzione.")
                    sys.exit(1)
            elif phase == 7:
                ok = await phase7_index_giurisprudenza(
                    workspace or "default", dry_run, state, organi
                )
                if not ok:
                    logger.warning("Fase 7 parzialmente fallita — continua comunque.")

        except Exception as exc:
            logger.exception(f"[Fase {phase}] Eccezione inattesa: {exc}")
            _update_phase(state, phase, "failed", str(exc))
            logger.error(f"Usa --from-phase {phase} per riprendere dopo aver risolto il problema.")
            sys.exit(1)

        elapsed = time.time() - t0
        logger.info(f"[Fase {phase}] Durata: {elapsed:.1f}s")

    total_elapsed = time.time() - t_total
    logger.info("\n" + "=" * 60)
    logger.info(f"  Rebuild completato in {total_elapsed/60:.1f} min")
    if not dry_run:
        logger.info("  Prossimo passo: impostare AIURA_SETTORE_FILTER=1 nel .env")
        logger.info("  per attivare il filtraggio settore nel PhaseRetriever.")
    logger.info("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Rebuild completo del knowledge base AiUra LegalLab",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--workspace",
        default=None,
        help="Filtra per workspace (default: tutti)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra cosa farebbe senza scrivere nulla",
    )
    p.add_argument(
        "--from-phase",
        type=int,
        default=None,
        metavar="N",
        help="Riprendi dalla fase N (0-7). Default: legge da rebuild_state.json",
    )
    p.add_argument(
        "--skip-phase",
        type=int,
        nargs="+",
        metavar="N",
        help="Salta le fasi specificate (es. --skip-phase 6 7)",
    )
    p.add_argument(
        "--organi",
        nargs="+",
        default=["cassazione", "corte_cost"],
        metavar="ORGANO",
        help="Organi giurisdizionali per fase 7 (default: cassazione corte_cost)",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(main(args))
