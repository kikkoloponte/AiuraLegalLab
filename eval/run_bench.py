"""
AiUra LegalLab — Benchmark qualitativo.

Interroga l'API per ogni domanda in bench_questions.jsonl e produce
un report Markdown strutturato con: domanda, analisi IQRAC, riferimenti, timing.

Uso:
  # API locale con workspace default
  python eval/run_bench.py

  # API remota, workspace personalizzato
  python eval/run_bench.py --api-url http://192.168.1.10:8765 --workspace studio-x

  # Subset di domande
  python eval/run_bench.py --ids bench_01,bench_04,bench_07

  # Solo le domande di una area
  python eval/run_bench.py --area "Diritto Penale"
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class BenchQuestion:
    id: str
    area: str
    query: str


@dataclasses.dataclass
class BenchSource:
    rank: int
    type: str           # normativa | giurisprudenza | studio
    label: str
    source_id: str
    doc_id: str
    url: str
    snippet: str
    metadata: dict


@dataclasses.dataclass
class BenchSection:
    step: str
    content: str
    citations: list


@dataclasses.dataclass
class BenchResult:
    id: str
    area: str
    query: str
    verdict: str
    confidence: str
    sections: list[BenchSection]
    sources: list[BenchSource]
    duration_s: float
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# SSE consumer
# ---------------------------------------------------------------------------

_STEP_LABELS: dict[str, str] = {
    "RICOSTRUZIONE_FATTO": "Ricostruzione del fatto",
    "QUALIFICAZIONE":      "Qualificazione giuridica",
    "QUESTIONE":           "Questione giuridica",
    "FONTI_NORMATIVE":     "Fonti normative",
    "INTERPRETAZIONE":     "Interpretazione",
    "GIURISPRUDENZA":      "Orientamenti giurisprudenziali",
    "SUSSUNZIONE":         "Sussunzione",
    "OBIEZIONI":           "Obiezioni e tesi contrarie",
    "CONCLUSIONE":         "Conclusione",
}

_ORGANO_LABELS: dict[str, str] = {
    "cassazione":     "Cass.",
    "tar":            "TAR",
    "consiglio_stato":"Cons. St.",
    "corte_cost":     "Corte Cost.",
    "corte_conti":    "Corte Conti",
}


def _source_label(s: dict) -> str:
    source_id = s.get("source_id", "")
    meta      = s.get("metadata") or {}
    corpus    = meta.get("corpus", "")

    if corpus == "giurisprudenza" or source_id.startswith("giurisprudenza_"):
        organo = _ORGANO_LABELS.get(meta.get("organo", ""), meta.get("organo", "Sent."))
        num    = f"n.{meta['numero']}" if meta.get("numero") else ""
        yr     = f"/{meta['anno']}"    if meta.get("anno")   else ""
        return f"{organo} {num}{yr}".strip() or source_id

    articolo = meta.get("articolo", "")
    titolo   = meta.get("titolo", "")
    if articolo and titolo:
        return f"{articolo} — {titolo}"[:60]
    if articolo:
        return articolo
    if titolo:
        return titolo[:50]
    if len(source_id) > 40:
        return source_id[source_id.rfind(":") + 1:]
    return source_id


def _source_type(s: dict) -> str:
    meta      = s.get("metadata") or {}
    source_id = s.get("source_id", "")
    corpus    = meta.get("corpus", "")
    if corpus == "giurisprudenza" or source_id.startswith("giurisprudenza_"):
        return "giurisprudenza"
    if corpus == "studio":
        return "studio"
    return "normativa"


def _source_url(s: dict) -> str:
    source_id = s.get("source_id", "")
    meta      = s.get("metadata") or {}
    if source_id.startswith("urn:nir:"):
        return f"https://www.normattiva.it/uri-res/N2Ls?{source_id}"
    return meta.get("source_url", "")


async def _call_stream(
    question: BenchQuestion,
    api_url: str,
    workspace: str,
    timeout: float = 600.0,
) -> BenchResult:
    """Chiama POST /query/stream via SSE e raccoglie la risposta completa."""
    url = f"{api_url.rstrip('/')}/query/stream"
    sections: list[BenchSection] = []
    sources:  list[BenchSource]  = []
    verdict    = "PASS"
    confidence = "MEDIUM"
    duration_s = 0.0

    t_start = time.monotonic()

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST", url,
                json={
                    "query":     question.query,
                    "workspace": workspace,
                    "intent":    "fattispecie_analysis",
                    "mode":      "standard",
                },
                headers={"Accept": "text/event-stream"},
            ) as resp:
                resp.raise_for_status()
                buffer = ""
                async for chunk in resp.aiter_text():
                    buffer += chunk
                    while "\n\n" in buffer:
                        block, buffer = buffer.split("\n\n", 1)
                        data_line = next(
                            (l for l in block.split("\n") if l.startswith("data: ")),
                            None,
                        )
                        if not data_line:
                            continue
                        raw = data_line[6:].strip()
                        if not raw:
                            continue
                        try:
                            event = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        etype = event.get("type", "")

                        if etype == "phase_complete":
                            for s in event.get("sections", []):
                                sections.append(BenchSection(
                                    step=s.get("step", ""),
                                    content=s.get("content", ""),
                                    citations=s.get("citations", []),
                                ))

                        elif etype == "review_done":
                            verdict    = event.get("verdict", "PASS")
                            confidence = event.get("overall_confidence", "MEDIUM")
                            duration_s = float(event.get("duration_total_s", 0))
                            for i, s in enumerate(event.get("sources", [])):
                                sources.append(BenchSource(
                                    rank=i + 1,
                                    type=_source_type(s),
                                    label=_source_label(s),
                                    source_id=s.get("source_id", ""),
                                    doc_id=s.get("doc_id", ""),
                                    url=_source_url(s),
                                    snippet=s.get("snippet", ""),
                                    metadata=s.get("metadata") or {},
                                ))

                        elif etype == "error":
                            raise RuntimeError(event.get("message", "Errore SSE"))

    except Exception as exc:
        elapsed = time.monotonic() - t_start
        logger.error(f"[{question.id}] ERRORE: {exc}")
        return BenchResult(
            id=question.id, area=question.area, query=question.query,
            verdict="ERROR", confidence="LOW",
            sections=[], sources=[],
            duration_s=elapsed,
            error=str(exc),
        )

    if duration_s == 0.0:
        duration_s = time.monotonic() - t_start

    logger.success(f"[{question.id}] {verdict} / {confidence} — {duration_s:.1f}s — {len(sources)} fonti")
    return BenchResult(
        id=question.id, area=question.area, query=question.query,
        verdict=verdict, confidence=confidence,
        sections=sections, sources=sources,
        duration_s=duration_s,
    )


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

_VERDICT_EMOJI = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌", "RE_RETRIEVAL": "🔄", "ERROR": "💥"}
_CONF_EMOJI    = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}
_TYPE_EMOJI    = {"normativa": "📜", "giurisprudenza": "⚖", "studio": "📁"}


def _write_report(results: list[BenchResult], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    report_path = out_dir / "report.md"
    raw_path    = out_dir / "raw_results.json"

    # ── JSON grezzo ──────────────────────────────────────────────────────
    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump([dataclasses.asdict(r) for r in results], f,
                  ensure_ascii=False, indent=2)
    logger.info(f"JSON grezzo → {raw_path}")

    # ── Markdown ─────────────────────────────────────────────────────────
    ts    = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# AiUra LegalLab — Benchmark Qualitativo",
        "",
        f"**Generato:** {ts}  ",
        f"**Domande:** {len(results)}  ",
        f"**Completate senza errori:** {sum(1 for r in results if not r.error)}  ",
        f"**Tempo totale:** {sum(r.duration_s for r in results):.1f}s  ",
        "",
        "---",
        "",
        "## Indice",
        "",
    ]

    # Indice
    for i, r in enumerate(results, 1):
        slug  = r.query[:60].rstrip()
        emoji = _VERDICT_EMOJI.get(r.verdict, "")
        lines.append(f"{i}. [{r.area}] {emoji} {slug}…")
    lines += ["", "---", ""]

    # Sezioni per domanda
    for i, r in enumerate(results, 1):
        v_emoji = _VERDICT_EMOJI.get(r.verdict, r.verdict)
        c_emoji = _CONF_EMOJI.get(r.confidence, "")

        lines += [
            f"## {i}. [{r.area}]",
            "",
            f"**Domanda:** {r.query}",
            "",
            f"**Tempo:** {r.duration_s:.1f}s &nbsp;|&nbsp; "
            f"**Verdict:** {v_emoji} {r.verdict} &nbsp;|&nbsp; "
            f"**Confidenza:** {c_emoji} {r.confidence}",
            "",
        ]

        if r.error:
            lines += [f"> ⛔ **Errore:** {r.error}", "", "---", ""]
            continue

        # Analisi IQRAC
        if r.sections:
            lines += ["### Analisi IQRAC", ""]
            for sec in r.sections:
                label = _STEP_LABELS.get(sec.step.upper(), sec.step)
                lines += [
                    f"#### {label}",
                    "",
                    sec.content.strip(),
                    "",
                ]
        else:
            lines += ["> *Nessuna sezione IQRAC disponibile.*", ""]

        # Riferimenti
        lines += ["### Riferimenti citati", ""]
        if r.sources:
            lines += [
                "| # | Tipo | Riferimento | Organo/Fonte | URL |",
                "|---|------|-------------|--------------|-----|",
            ]
            for s in r.sources:
                t_emoji = _TYPE_EMOJI.get(s.type, "")
                organo  = s.metadata.get("organo", s.metadata.get("fonte", "—"))
                url_cell = f"[apri]({s.url})" if s.url else "—"
                lines.append(
                    f"| {s.rank} | {t_emoji} {s.type} | {s.label} | {organo} | {url_cell} |"
                )
            lines.append("")

            # Snippet di ogni fonte
            lines += ["<details><summary>Snippet fonti</summary>", ""]
            for s in r.sources:
                if s.snippet:
                    lines += [
                        f"**{s.rank}. {s.label}**",
                        f"> {s.snippet[:400]}{'…' if len(s.snippet) > 400 else ''}",
                        "",
                    ]
            lines += ["</details>", ""]
        else:
            lines += ["> *Nessuna fonte citata.*", ""]

        lines += ["---", ""]

    # Tabella riassuntiva finale
    lines += [
        "## Riepilogo",
        "",
        "| # | Area | Verdict | Confidenza | Fonti | Tempo |",
        "|---|------|---------|------------|-------|-------|",
    ]
    for i, r in enumerate(results, 1):
        v = f"{_VERDICT_EMOJI.get(r.verdict, '')} {r.verdict}"
        c = f"{_CONF_EMOJI.get(r.confidence, '')} {r.confidence}"
        lines.append(
            f"| {i} | {r.area} | {v} | {c} | {len(r.sources)} | {r.duration_s:.1f}s |"
        )
    lines += [""]

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    logger.info(f"Report Markdown → {report_path}")
    return report_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _load_questions(
    path: Path,
    ids_filter: set[str] | None,
    area_filter: str | None,
) -> list[BenchQuestion]:
    questions: list[BenchQuestion] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            q = BenchQuestion(
                id=data["id"],
                area=data.get("area", ""),
                query=data["query"],
            )
            if ids_filter and q.id not in ids_filter:
                continue
            if area_filter and area_filter.lower() not in q.area.lower():
                continue
            questions.append(q)
    return questions


async def _run(args: argparse.Namespace) -> None:
    import asyncio

    questions_path = Path(args.questions)
    if not questions_path.exists():
        logger.error(f"File domande non trovato: {questions_path}")
        sys.exit(1)

    ids_filter  = set(args.ids.split(",")) if args.ids else None
    area_filter = args.area or None

    questions = _load_questions(questions_path, ids_filter, area_filter)
    if not questions:
        logger.error("Nessuna domanda caricata (controlla --ids / --area)")
        sys.exit(1)

    logger.info(f"Benchmark: {len(questions)} domande su {args.api_url} (workspace={args.workspace})")

    results: list[BenchResult] = []
    for i, q in enumerate(questions, 1):
        logger.info(f"[{i}/{len(questions)}] {q.id} — {q.area}: {q.query[:70]}…")
        result = await _call_stream(q, args.api_url, args.workspace, timeout=args.timeout)
        results.append(result)

    ts      = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(args.output_dir) / ts
    report  = _write_report(results, out_dir)

    passed  = sum(1 for r in results if r.verdict in ("PASS", "WARN") and not r.error)
    errors  = sum(1 for r in results if r.error)
    avg_s   = sum(r.duration_s for r in results) / len(results) if results else 0

    print()
    print("=" * 60)
    print(f"  Benchmark completato — {len(results)} domande")
    print(f"  Passate:  {passed}/{len(results)}")
    print(f"  Errori:   {errors}")
    print(f"  Tempo medio: {avg_s:.1f}s")
    print(f"  Report:   {report}")
    print("=" * 60)


def main() -> None:
    import asyncio

    here = Path(__file__).parent

    parser = argparse.ArgumentParser(
        description="AiUra LegalLab — Benchmark qualitativo"
    )
    parser.add_argument(
        "--questions",
        default=str(here / "bench_questions.jsonl"),
        help="Path al file JSONL con le domande (default: eval/bench_questions.jsonl)",
    )
    parser.add_argument(
        "--api-url",
        default="http://127.0.0.1:8765",
        help="URL base dell'API AiUra (default: http://127.0.0.1:8765)",
    )
    parser.add_argument(
        "--workspace",
        default="mio-studio",
        help="Workspace da usare (default: mio-studio)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(here / "bench_results"),
        help="Directory output report (default: eval/bench_results/)",
    )
    parser.add_argument(
        "--ids",
        default="",
        help="Filtra per ID domande, separati da virgola (es. bench_01,bench_04)",
    )
    parser.add_argument(
        "--area",
        default="",
        help="Filtra per area (es. 'Diritto Penale')",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=600.0,
        help="Timeout per domanda in secondi (default: 600)",
    )
    args = parser.parse_args()

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
