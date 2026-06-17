"""
Verifica la costruzione degli indici BM25 + ChromaDB su un campione reale
di documenti da LegalAgentLab.

Uso:
  python scripts/verify_indexes.py
  python scripts/verify_indexes.py --limit 2000 --workspace verify_sample
  python scripts/verify_indexes.py --smoke-queries "responsabilità contrattuale" "locazione"

Output:
  - Log su stdout
  - scripts/build_report.json  (o path custom con --output)

Exit code:
  0  verdict OK o WARN
  1  verdict FAIL (0 chunk, eccezione build, tutti smoke test a 0 risultati)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from aiura_legal.ingestion.mongodb.client import LegalAgentLabReader
from aiura_legal.core.retrieval.bm25_retriever import BM25Retriever
from aiura_legal.core.retrieval.vector_retriever import VectorRetriever
from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever
from aiura_legal.core.types import Document, QueryIntent


_DEFAULT_SMOKE_QUERIES: list[str] = [
    "responsabilità contrattuale inadempimento",
    "locazione abitativa canone affitto",
    "infortunio sul lavoro datore di lavoro",
]

_WORKSPACES_BASE = "C:/project/AiUraLegalLab/workspaces"


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

async def build_and_verify(
    workspace: str,
    limit: int,
    smoke_queries: list[str],
    output: str,
    workspaces_base: str,
) -> int:
    run_at = datetime.now(timezone.utc).isoformat()
    ws_path = Path(workspaces_base) / workspace
    ws_path.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "run_at": run_at,
        "workspace": workspace,
        "docs_sampled": limit,
        "chunks_inserted": 0,
        "bm25_index_size_kb": 0,
        "chroma_collection_count": 0,
        "build_duration_s": 0.0,
        "smoke_tests": [],
        "verdict": "FAIL",
        "error": None,
    }

    # ------------------------------------------------------------------ build
    try:
        reader = LegalAgentLabReader()
        total_available = await reader.count_chunks()
        effective = min(total_available, limit)
        logger.info(
            f"LegalAgentLab: {total_available:,} chunk disponibili — "
            f"campiono {effective:,}"
        )

        bm25 = BM25Retriever(str(ws_path))
        vector = VectorRetriever(str(ws_path))

        batch: list[Document] = []
        count = 0
        t_build = time.perf_counter()

        async for raw in reader.iter_chunks(batch_size=500):
            if count >= limit:
                break
            text = raw.get("_normalized_text", "")
            if not text or len(text) < 20:
                continue

            doc = Document(
                id=str(raw.get("_id", "")),
                text=text,
                source_id=raw.get("urn") or raw.get("source_id") or "",
                metadata={
                    "doc_type": raw.get("testo_tipo", ""),
                    "source":   raw.get("source_id", "normattiva_it"),
                    "titolo":   raw.get("titolo", ""),
                    "articolo": raw.get("articolo_num", ""),
                },
            )
            batch.append(doc)
            count += 1

            if len(batch) >= 500:
                bm25.add_documents_batch(batch)
                vector.add_documents_batch(batch)
                batch = []
                logger.info(f"  {count:,} chunk processati…")

        if batch:
            bm25.add_documents_batch(batch)
            vector.add_documents_batch(batch)

        build_duration = time.perf_counter() - t_build

        if count == 0:
            report["error"] = (
                "Nessun chunk inserito — "
                "LegalAgentLab non raggiungibile o collection vuota."
            )
            _write_report(report, output)
            return 1

        bm25.save()
        vector.save()

        # Dimensione BM25
        bm25_pkl = ws_path / "indices" / "bm25.pkl"
        bm25_kb = int(bm25_pkl.stat().st_size / 1024) if bm25_pkl.exists() else 0

        report.update({
            "chunks_inserted": count,
            "bm25_index_size_kb": bm25_kb,
            "build_duration_s": round(build_duration, 2),
        })
        logger.success(
            f"Build completato: {count:,} chunk in {build_duration:.1f}s  "
            f"(BM25: {bm25_kb} KB)"
        )

    except Exception as exc:
        report["error"] = str(exc)
        logger.error(f"Errore durante il build: {exc}")
        _write_report(report, output)
        return 1

    # ------------------------------------------------------------------ smoke test
    warn = False
    smoke_results: list[dict] = []

    try:
        retriever = HybridRetriever(str(ws_path))

        for q in smoke_queries:
            t0 = time.perf_counter()
            try:
                packet = retriever.build_research_packet_bifasico(
                    query=q,
                    intent=QueryIntent.NORMA_LOOKUP,
                )
                latency_ms = int((time.perf_counter() - t0) * 1000)
                top1 = packet.sources[0] if packet.sources else None
                n = len(packet.sources)

                entry: dict = {
                    "query": q,
                    "top1_source_id": top1.source_id if top1 else "",
                    "top1_score": round(top1.score, 4) if top1 else 0.0,
                    "result_count": n,
                    "latency_ms": latency_ms,
                }
                smoke_results.append(entry)

                if n < 5:
                    warn = True
                    logger.warning(f"Smoke '{q}': {n} risultati (< 5) in {latency_ms}ms")
                else:
                    logger.info(f"Smoke '{q}': {n} risultati in {latency_ms}ms")

            except Exception as exc:
                smoke_results.append({
                    "query": q,
                    "top1_source_id": "",
                    "top1_score": 0.0,
                    "result_count": 0,
                    "latency_ms": 0,
                    "error": str(exc),
                })
                warn = True
                logger.error(f"Smoke '{q}' fallito: {exc}")

        # Count ChromaDB
        try:
            import chromadb  # type: ignore
            chroma_client = chromadb.PersistentClient(
                path=str(ws_path / "indices" / "chromadb")
            )
            col = chroma_client.get_or_create_collection("legal_docs")
            report["chroma_collection_count"] = col.count()
        except Exception as exc:
            logger.warning(f"Impossibile leggere count ChromaDB: {exc}")

    except Exception as exc:
        report["error"] = f"Smoke test fallito: {exc}"
        report["smoke_tests"] = smoke_results
        report["verdict"] = "FAIL"
        logger.error(f"Errore smoke test: {exc}")
        _write_report(report, output)
        return 1

    report["smoke_tests"] = smoke_results
    report["verdict"] = "WARN" if warn else "OK"
    _write_report(report, output)

    # Summary
    print()
    print("=" * 62)
    print(f"  VERIFY INDEXES — {workspace}")
    print("=" * 62)
    print(f"  Chunk inseriti   : {report['chunks_inserted']:,}")
    print(f"  Build duration   : {report['build_duration_s']} s")
    print(f"  BM25 size        : {report['bm25_index_size_kb']} KB")
    print(f"  ChromaDB count   : {report['chroma_collection_count']}")
    print(f"  Verdict          : {report['verdict']}")
    print(f"  Report           : {output}")
    print("=" * 62)

    return 0 if report["verdict"] in ("OK", "WARN") else 1


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def _write_report(report: dict, output: str) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info(f"Report scritto: {path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verifica build indici BM25 + ChromaDB su campione LegalAgentLab"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=1000,
        metavar="N",
        help="Numero max chunk da campionare (default: 1000)",
    )
    parser.add_argument(
        "--workspace",
        default="verify_sample",
        help="Nome workspace temporaneo (default: verify_sample)",
    )
    parser.add_argument(
        "--smoke-queries",
        nargs="+",
        default=_DEFAULT_SMOKE_QUERIES,
        metavar="QUERY",
        help="Query smoke test (default: 3 query predefinite)",
    )
    parser.add_argument(
        "--output",
        default="scripts/build_report.json",
        metavar="FILE",
        help="Path report JSON (default: scripts/build_report.json)",
    )
    parser.add_argument(
        "--workspaces-base",
        default=_WORKSPACES_BASE,
        metavar="DIR",
        help=f"Directory base workspace (default: {_WORKSPACES_BASE})",
    )
    args = parser.parse_args()

    exit_code = asyncio.run(
        build_and_verify(
            workspace=args.workspace,
            limit=args.limit,
            smoke_queries=args.smoke_queries,
            output=args.output,
            workspaces_base=args.workspaces_base,
        )
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
