"""
AiUra LegalLab — Eval CLI runner.

Uso:
  # file di default (tests/script_json/test_aiura_01.jsonl)
  python eval/run_eval.py

  # file custom
  python eval/run_eval.py --queries path/to/queries.jsonl

  # filtra per modulo
  python eval/run_eval.py --module cod_civ

  # API remota
  python eval/run_eval.py --api-url http://192.168.1.10:8765

Exit code:
  0  pass_rate >= 80%  (oppure --no-threshold)
  1  pass_rate <  80%  o errore fatale
"""
from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from loguru import logger

# Garantisce che il root del progetto sia in sys.path anche quando
# lo script viene invocato come "python eval/run_eval.py"
sys.path.insert(0, str(Path(__file__).parent.parent))

from eval.evaluator import EvalQuery, EvalReport, EvalResult, Evaluator  # noqa: E402


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def _load_queries(
    path: str,
    module_filter: str | None = None,
    workspace_override: str | None = None,
) -> list[EvalQuery]:
    """Carica le query da un file JSONL, una per riga."""
    queries: list[EvalQuery] = []
    p = Path(path)
    if not p.exists():
        logger.error(f"File JSONL non trovato: {path}")
        return []

    with open(p, encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                data = json.loads(line)
                q = EvalQuery(
                    id=data["id"],
                    query=data["query"],
                    workspace=workspace_override or data.get("workspace", "default"),
                    intent=data.get("intent", "retrieval"),
                    expected_source_ids=data.get("expected_source_ids", []),
                    module=data.get("module", ""),
                    difficulty=data.get("difficulty", "medium"),
                    top_k=data.get("top_k", 10),
                )
                if module_filter is None or q.module == module_filter:
                    queries.append(q)
            except KeyError as e:
                logger.warning(f"Riga {line_no}: campo mancante {e} — ignorata")
            except json.JSONDecodeError as e:
                logger.warning(f"Riga {line_no}: JSON non valido ({e}) — ignorata")

    return queries


def _write_json(report: EvalReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(report), f, ensure_ascii=False, indent=2)
    logger.info(f"Report JSON   → {path}")


def _write_markdown(report: EvalReport, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    rec_global = (
        f"{report.mean_recall_at_k:.3f}"
        if report.mean_recall_at_k is not None
        else "N/A"
    )

    lines: list[str] = [
        f"# Eval Report — {report.run_id}",
        "",
        f"**File query:** `{report.queries_file}`",
        "",
        "## Summary globale",
        "",
        "| Metrica | Valore |",
        "|---|---|",
        f"| Query totali | {report.total} |",
        f"| Errori | {report.errors} |",
        f"| Pass rate | {report.pass_rate * 100:.1f}% |",
        f"| Latenza media | {report.mean_latency_ms:.0f} ms |",
        f"| Latenza p50 | {report.p50_latency_ms:.0f} ms |",
        f"| Latenza p95 | {report.p95_latency_ms:.0f} ms |",
        f"| Groundedness media | {report.mean_groundedness:.3f} |",
        f"| Recall@k media | {rec_global} |",
        "",
    ]

    if report.per_module:
        lines += [
            "## Per-module summary",
            "",
            "| Modulo | Query | Errori | Groundedness | Recall@k | Lat. media | Lat. p95 | Pass rate |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for mod, stats in sorted(report.per_module.items()):
            rec = (
                f"{stats.mean_recall_at_k:.3f}"
                if stats.mean_recall_at_k is not None
                else "N/A"
            )
            lines.append(
                f"| {mod} | {stats.total} | {stats.errors} | "
                f"{stats.mean_groundedness:.3f} | {rec} | "
                f"{stats.mean_latency_ms:.0f} ms | {stats.p95_latency_ms:.0f} ms | "
                f"{stats.pass_rate * 100:.1f}% |"
            )
        lines.append("")

    # Query con problemi
    problems: list[EvalResult] = [
        r for r in report.results
        if r.error or r.reviewer_verdict == "BLOCK"
    ]
    if problems:
        lines += ["## Query con problemi", ""]
        for r in problems:
            tag = f"ERROR: {r.error}" if r.error else "BLOCK"
            snippet = r.query[:80] + ("…" if len(r.query) > 80 else "")
            lines.append(f"- **[{r.query_id}]** `{tag}` — {snippet}")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info(f"Report Markdown → {path}")


# ---------------------------------------------------------------------------
# Verbose chunk printer
# ---------------------------------------------------------------------------

def _print_chunks(q: "EvalQuery", r: "EvalResult") -> None:
    sep = "-" * 62
    expected = q.expected_source_ids

    print()
    print(sep)
    rec_str = f"{r.recall_at_k:.2f}" if r.recall_at_k is not None else "N/A"
    print(f"  [{r.query_id}] {q.module}/{q.difficulty}  "
          f"G={r.groundedness:.2f}  R={rec_str}  "
          f"{r.latency_ms:.0f}ms  {r.reviewer_verdict or '-'}")
    print(f"  Query: {q.query[:90]}")
    if expected:
        print(f"  Attesi: {', '.join(expected)}")
    print(sep)

    if r.error:
        print(f"  ERRORE: {r.error}")
        return

    from eval.evaluator import Evaluator
    for s in r.sources:
        sid = s.get("source_id", "")
        matched = any(Evaluator._source_matches(sid, exp) for exp in expected)
        marker = " HIT" if matched else "    "
        meta = s.get("metadata", {})
        titolo = meta.get("titolo", "")[:55]
        articolo = meta.get("articolo", "")
        snippet = s.get("snippet", "")[:180].replace("\n", " ")
        print(
            f"{marker} [{s.get('rank')}] "
            f"score={s.get('score', 0):.4f}  {s.get('retrieval_method', '')}  "
            f"tipo={meta.get('doc_type', '')}"
        )
        print(f"       source_id : {sid}")
        if titolo or articolo:
            print(f"       norma     : {titolo}  {articolo}")
        print(f"       snippet   : {snippet}")
    print()


# ---------------------------------------------------------------------------
# Main async runner
# ---------------------------------------------------------------------------

async def _run(args: argparse.Namespace) -> int:
    queries = _load_queries(
        args.queries,
        module_filter=args.module,
        workspace_override=args.workspace,
    )
    if not queries:
        logger.error(
            "Nessuna query caricata. "
            "Controlla il file JSONL e il filtro --module."
        )
        return 1

    logger.info(
        f"Query caricate: {len(queries)}"
        + (f" (modulo: {args.module})" if args.module else "")
    )

    # Health check
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{args.api_url}/health")
            resp.raise_for_status()
            health = resp.json()
        status = health.get("status", "unknown")
        mongo_ok = health.get("mongodb", False)
        ollama_ok = health.get("ollama", False)
        logger.info(
            f"API health: {status}  "
            f"(MongoDB={'✓' if mongo_ok else '✗'}  "
            f"Ollama={'✓' if ollama_ok else '✗'})"
        )
    except Exception as e:
        logger.error(f"API non raggiungibile a {args.api_url}: {e}")
        logger.error("Avvia l'API con:  python -m aiura_legal.api")
        return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evaluator = Evaluator(api_base_url=args.api_url)

    logger.info("Avvio eval…")
    results = []
    for q in queries:
        r = await evaluator.run_query(q)
        results.append(r)
        if args.verbose:
            _print_chunks(q, r)

    report = Evaluator.build_report(
        results,
        run_id=run_id,
        queries_file=str(Path(args.queries).resolve()),
    )

    # Scrivi output
    out = Path(args.output)
    _write_json(report, out / f"eval_{run_id}.json")
    _write_markdown(report, out / f"eval_{run_id}.md")

    # Summary su stdout
    rec_str = (
        f"{report.mean_recall_at_k:.3f}"
        if report.mean_recall_at_k is not None
        else "N/A"
    )
    print()
    print("=" * 62)
    print(f"  EVAL REPORT — {run_id}")
    print("=" * 62)
    print(f"  Query       : {report.total}  |  Errori: {report.errors}")
    print(f"  Pass rate   : {report.pass_rate * 100:.1f}%")
    print(f"  Lat. media  : {report.mean_latency_ms:.0f} ms  "
          f"  p50: {report.p50_latency_ms:.0f} ms  "
          f"  p95: {report.p95_latency_ms:.0f} ms")
    print(f"  Groundedness: {report.mean_groundedness:.3f}")
    print(f"  Recall@k    : {rec_str}")
    print("=" * 62)

    if args.no_threshold:
        return 0

    if report.pass_rate < 0.80:
        logger.warning(
            f"Pass rate {report.pass_rate * 100:.1f}% < 80% → exit 1"
        )
        return 1
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    _default_queries = str(
        Path(__file__).parent.parent
        / "tests"
        / "script_json"
        / "test_aiura_01.jsonl"
    )

    parser = argparse.ArgumentParser(
        description="AiUra LegalLab — Eval runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--queries",
        default=_default_queries,
        metavar="FILE",
        help=(
            "File JSONL con le query di valutazione "
            f"(default: tests/script_json/test_aiura_01.jsonl)"
        ),
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8765",
        metavar="URL",
        help="URL base dell'API (default: http://127.0.0.1:8765)",
    )
    parser.add_argument(
        "--output",
        default="eval/results",
        metavar="DIR",
        help="Directory output per i report (default: eval/results)",
    )
    parser.add_argument(
        "--module",
        default=None,
        metavar="MOD",
        help="Filtra per modulo (es. cod_civ, pen, lav, amm, trib, fam, cross)",
    )
    parser.add_argument(
        "--workspace",
        default=None,
        metavar="WS",
        help="Sovrascrive il workspace definito nel JSONL",
    )
    parser.add_argument(
        "--no-threshold",
        action="store_true",
        help="Ritorna sempre exit 0 (disabilita la soglia pass_rate 80%%)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostra i chunk recuperati (source_id, snippet, score) per ogni query",
    )
    args = parser.parse_args()
    sys.exit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
