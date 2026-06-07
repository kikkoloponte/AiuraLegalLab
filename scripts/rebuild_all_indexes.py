"""
Full rebuild di tutti gli indici (BM25 + Qdrant) per un workspace.

Sequenza corretta:
  1. Reset Qdrant collection
  2. normattiva  (~295k chunk, ~15-20 min)
  3. dottrina    (~Xk chunk)
  4. studio      (~Xk chunk)
  5. giurisprudenza (~428k chunk, ~60-90 min)

Uso:
  python scripts/rebuild_all_indexes.py --workspace mio-studio
  python scripts/rebuild_all_indexes.py --workspace mio-studio --skip-giurisprudenza

⚠️  Questo script azzera TUTTO. Usarlo solo quando:
  - Primo setup
  - Il BM25 è corrotto o desincronizzato da MongoDB
  - Si vuole ripartire da zero dopo modifiche strutturali

Per aggiornamenti parziali usa invece:
  python scripts/build_indexes.py --workspace mio-studio --corpus <corpus>
  python scripts/build_jurisprudence_indexes.py --workspace mio-studio
"""
from __future__ import annotations

import argparse
import asyncio
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger


def _run(cmd: list[str], step: str) -> None:
    """Esegue un sotto-processo e termina se fallisce."""
    logger.info(f"\n{'='*60}")
    logger.info(f"  {step}")
    logger.info(f"{'='*60}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        logger.error(f"{step} fallito (exit code {result.returncode}). Rebuild interrotto.")
        sys.exit(result.returncode)
    logger.success(f"{step} completato.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Full rebuild di tutti gli indici per un workspace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--workspace", required=True, help="Nome workspace (es. mio-studio)")
    parser.add_argument(
        "--skip-giurisprudenza", action="store_true",
        help="Salta il rebuild della giurisprudenza (molto più veloce, ~20 min invece di ~90)",
    )
    parser.add_argument(
        "--skip-vector", action="store_true",
        help="Salta Qdrant (solo BM25) — utile se si vuole solo ricostruire il BM25",
    )
    args = parser.parse_args()

    ws = args.workspace
    python = sys.executable
    scripts = Path(__file__).parent

    logger.warning(
        f"\n⚠️  FULL REBUILD per workspace '{ws}'\n"
        f"   Questo azzererà BM25 e Qdrant. Continua? [Ctrl+C per annullare]"
    )
    try:
        input("   Premi INVIO per confermare... ")
    except KeyboardInterrupt:
        logger.info("Annullato.")
        sys.exit(0)

    base_flags = ["--workspace", ws]
    if args.skip_vector:
        base_flags += ["--skip-vector"]

    # ── Step 1: normattiva — resetta BM25 + Qdrant ──────────────────────
    # Il primo corpus usa --reset-qdrant per ripartire da zero su Qdrant.
    # Gli step successivi fanno solo upsert (non toccano Qdrant collection).
    _run(
        [python, str(scripts / "build_indexes.py")] + base_flags
        + ["--corpus", "normattiva"]
        + (["--reset-qdrant"] if not args.skip_vector else []),
        "Step 1/4 — normattiva (BM25 reset + Qdrant reset + indicizzazione)",
    )

    # ── Step 2: dottrina ────────────────────────────────────────────────
    _run(
        [python, str(scripts / "build_indexes.py")] + base_flags
        + ["--corpus", "dottrina"],
        "Step 2/4 — dottrina (BM25 append + Qdrant upsert)",
    )

    # ── Step 3: studio ──────────────────────────────────────────────────
    _run(
        [python, str(scripts / "build_indexes.py")] + base_flags
        + ["--corpus", "studio"],
        "Step 3/4 — studio (BM25 append + Qdrant upsert)",
    )

    # ── Step 4: giurisprudenza ──────────────────────────────────────────
    if args.skip_giurisprudenza:
        logger.info("Step 4/4 — giurisprudenza: SALTATO (--skip-giurisprudenza)")
    else:
        _run(
            [python, str(scripts / "build_jurisprudence_indexes.py"),
             "--workspace", ws],
            "Step 4/4 — giurisprudenza (incrementale — aggiunge tutto da MongoDB)",
        )

    logger.success(
        f"\n✅ Full rebuild completato per workspace '{ws}'.\n"
        f"   Riavvia l'API per caricare i nuovi indici."
    )


if __name__ == "__main__":
    main()
