"""
Ingestione TFUE (Trattato sul Funzionamento dell'Unione Europea) — versione
consolidata IT, CELEX 02016E/TXT.

EUR-Lex blocca il fetch automatico (AWS WAF bot-challenge su
eur-lex.europa.eu e sull'endpoint content-negotiation del Publications
Office) — questo script legge un file HTML scaricato manualmente dal
browser, non effettua scraping.

Download manuale:
  https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:02016E/TXT-20240901
  Salvare come: download/tfue/tfue_consolidato_it.html

Uso:
  python scripts/ingest_tfue.py --file download/tfue/tfue_consolidato_it.html --dry-run
  python scripts/ingest_tfue.py --file download/tfue/tfue_consolidato_it.html
  python scripts/ingest_tfue.py --file download/tfue/tfue_consolidato_it.html --workspace mio-studio --limit 5

I chunk risultanti hanno corpus="normattiva" (è normativa, solo di livello
sovranazionale — riusa i pesi/filtri BM25-heavy di Fase 2 senza modifiche a
PhaseRetriever) e fonte="trattato_ue" per distinguerli nella UI/telemetria.
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from loguru import logger

from aiura_legal.ingestion.eu_treaties.parser import parse_tfue_html
from aiura_legal.ingestion.eu_treaties.pipeline import TfuePipeline
from aiura_legal.ingestion.mongodb.client import MongoClient


async def _run(file_path: Path, workspace: str, dry_run: bool, limit: int | None) -> None:
    if not file_path.exists():
        logger.error(
            f"File non trovato: {file_path}\n"
            "Scarica manualmente il testo consolidato IT da EUR-Lex:\n"
            "  https://eur-lex.europa.eu/legal-content/IT/TXT/HTML/?uri=CELEX:02016E/TXT-20240901"
        )
        sys.exit(1)

    html = file_path.read_text(encoding="utf-8", errors="replace")
    articles = parse_tfue_html(html)
    logger.info(f"Articoli TFUE estratti: {len(articles)}")

    if not articles:
        logger.error("Nessun articolo estratto — verificare il formato del file scaricato")
        sys.exit(1)

    if limit:
        articles = articles[:limit]
        logger.info(f"Limite applicato: {len(articles)} articoli")

    if dry_run:
        for a in articles[:5]:
            logger.info(f"  Art. {a.numero} — {a.gerarchia or '(nessuna gerarchia)'} — {len(a.testo)} char")
        if len(articles) > 5:
            logger.info(f"  ... e altri {len(articles) - 5}")
        logger.info("[dry-run] Nessuna scrittura su MongoDB.")
        return

    mongo = MongoClient.get()
    ok = await mongo.ping()
    if not ok:
        logger.error("MongoDB non raggiungibile")
        sys.exit(1)

    pipeline = TfuePipeline(mongo_db=mongo.db, workspace=workspace)
    result = await pipeline.chunk_articles(articles)
    logger.success(
        f"Ingestione completata: {result.articles_processed} articoli → "
        f"{result.chunks_created} chunk (workspace={workspace})"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingestione TFUE da file EUR-Lex locale")
    parser.add_argument("--file", required=True, type=Path,
                        help="Path al file HTML consolidato IT scaricato da EUR-Lex")
    parser.add_argument("--workspace", default="mio-studio")
    parser.add_argument("--dry-run", action="store_true",
                        help="Parsa e conta gli articoli senza scrivere su MongoDB")
    parser.add_argument("--limit", type=int, default=None,
                        help="Numero massimo di articoli da processare (test)")
    args = parser.parse_args()

    asyncio.run(_run(
        file_path=args.file,
        workspace=args.workspace,
        dry_run=args.dry_run,
        limit=args.limit,
    ))


if __name__ == "__main__":
    main()
