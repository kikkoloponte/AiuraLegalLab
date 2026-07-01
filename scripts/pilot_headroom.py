"""
Pilot di valutazione Headroom per la compressione del research packet.

Vedi: docs/superpowers/specs/2026-06-28-headroom-compression-pilot-design.md

Non modifica alcun file di produzione. `ContextBudgetManager.budget_texts` viene
sostituito solo a runtime (unittest.mock.patch.object) per la durata del Gate 2,
nello stesso processo Python — nessuna modifica su disco.

Richiede la dipendenza opzionale:
  pip install -e ".[headroom]"

Uso:
  python scripts/pilot_headroom.py --sample-size 5          # smoke test
  python scripts/pilot_headroom.py                          # run completo (default 50/corpus)
  python scripts/pilot_headroom.py --skip-gate2             # solo integrità testuale
  python scripts/pilot_headroom.py --module cod_civ         # filtra le query del Gate 2
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent.parent))

from aiura_legal.core.retrieval.context_budget import ContextBudgetManager, _count_tokens  # noqa: E402
from aiura_legal.ingestion.mongodb.client import MongoClient  # noqa: E402
from eval.evaluator import EvalQuery, Evaluator  # noqa: E402

try:
    from headroom import compress as headroom_compress
    _HEADROOM_AVAILABLE = True
except ImportError:
    _HEADROOM_AVAILABLE = False

_CORPORA = ["normattiva", "giurisprudenza", "dottrina"]

# Pattern critici: se presenti nell'originale e assenti nel compresso, è un fail.
_CRITICAL_PATTERNS: dict[str, re.Pattern] = {
    "articolo":          re.compile(r"Art\.\s*\d+"),
    "urn":                re.compile(r"urn:nir:[\w:.\-]+"),
    "data_slash":        re.compile(r"\d{1,2}/\d{1,2}/\d{4}"),
    "data_iso":           re.compile(r"\d{4}-\d{2}-\d{2}"),
    "estremi_sentenza":  re.compile(r"n\.\s*\d+/\d{4}"),
    "citazione":          re.compile(r"\[\d+\]"),
}

_GATE1_THRESHOLD = 0.95
_OUTPUT_DIR = Path(__file__).parent / "output"
_PILOT_API_PORT = 8766


# ---------------------------------------------------------------------------
# Gate 1 — integrità testuale
# ---------------------------------------------------------------------------

@dataclass
class Gate1ChunkResult:
    chunk_id: str
    corpus: str
    ok: bool
    missing_patterns: list[str]
    original_tokens: int
    compressed_tokens: int
    original_text: str = ""
    compressed_text: str = ""


@dataclass
class Gate1CorpusReport:
    corpus: str
    total: int = 0
    passed: int = 0
    avg_tokens_saved_pct: float = 0.0
    failed: list[Gate1ChunkResult] = field(default_factory=list)

    @property
    def integrity_rate(self) -> float:
        return self.passed / self.total if self.total else 0.0


def _check_critical_patterns(original: str, compressed: str) -> list[str]:
    """Ritorna i nomi dei pattern presenti nell'originale ma assenti nel compresso."""
    missing = []
    for name, pattern in _CRITICAL_PATTERNS.items():
        original_matches = set(pattern.findall(original))
        if not original_matches:
            continue
        compressed_matches = set(pattern.findall(compressed))
        if not original_matches.issubset(compressed_matches):
            missing.append(name)
    return missing


def _compress_chunk(text: str, max_tokens: int) -> str:
    """
    Comprime un chunk con Headroom entro un budget di token target.

    headroom.compress() opera su una lista di messaggi (formato chat
    Anthropic/OpenAI) e accetta `target_ratio` (frazione di token da
    rimuovere), non un budget assoluto — qui calcoliamo il target_ratio
    equivalente al budget di ContextBudgetManager. Se il chunk è già entro
    il budget, non comprimiamo (target_ratio 0 → passthrough).
    """
    original_tokens = _count_tokens(text)
    if original_tokens <= max_tokens:
        return text

    target_ratio = min(0.95, 1 - (max_tokens / original_tokens))
    messages = [{"role": "user", "content": text}]
    result = headroom_compress(
        messages,
        model="gpt-4o",
        compress_user_messages=True,
        target_ratio=target_ratio,
    )
    return result.messages[0]["content"]


async def run_gate1(sample_size: int) -> dict[str, Gate1CorpusReport]:
    mongo = MongoClient.get()
    budget_mgr = ContextBudgetManager()
    reports: dict[str, Gate1CorpusReport] = {}

    for corpus in _CORPORA:
        report = Gate1CorpusReport(corpus=corpus)
        full_text_tokens = budget_mgr._budget(corpus)["full_text_tokens"]

        cursor = mongo.chunks.find({"corpus": corpus}).limit(sample_size)
        async for chunk in cursor:
            text = chunk.get("text", "")
            if not text:
                continue
            report.total += 1

            original_tokens = _count_tokens(text)
            compressed = _compress_chunk(text, max_tokens=full_text_tokens)
            compressed_tokens = _count_tokens(compressed)

            missing = _check_critical_patterns(text, compressed)
            chunk_result = Gate1ChunkResult(
                chunk_id=str(chunk.get("_id", "")),
                corpus=corpus,
                ok=not missing,
                missing_patterns=missing,
                original_tokens=original_tokens,
                compressed_tokens=compressed_tokens,
                original_text=text,
                compressed_text=compressed,
            )

            if chunk_result.ok:
                report.passed += 1
            else:
                report.failed.append(chunk_result)

            saved_pct = (
                (original_tokens - compressed_tokens) / original_tokens * 100
                if original_tokens else 0.0
            )
            report.avg_tokens_saved_pct += saved_pct

        if report.total:
            report.avg_tokens_saved_pct /= report.total

        logger.info(
            f"[Gate1] corpus={corpus}  integrity={report.integrity_rate:.1%}  "
            f"({report.passed}/{report.total})  token_saved_avg={report.avg_tokens_saved_pct:.1f}%"
        )
        reports[corpus] = report

    return reports


# ---------------------------------------------------------------------------
# Gate 2 — eval end-to-end
# ---------------------------------------------------------------------------

def _headroom_budget_texts(self: ContextBudgetManager, items: list, corpus: str) -> list[str]:
    """Sostituto runtime di ContextBudgetManager.budget_texts che usa Headroom
    invece del troncamento token-based, mantenendo lo stesso budget per corpus."""
    from aiura_legal.core.retrieval.context_budget import _item_text, _item_sommario, _truncate_to_tokens

    budget = self._budget(corpus)
    full_slots = budget["full_text_slots"]
    full_tok = budget["full_text_tokens"]
    summary_tok = budget["summary_tokens"]

    texts: list[str] = []
    for i, item in enumerate(items):
        if i < full_slots and full_tok > 0:
            texts.append(_compress_chunk(_item_text(item), max_tokens=full_tok))
        else:
            raw_summary = _item_sommario(item) or _item_text(item)
            texts.append(_truncate_to_tokens(raw_summary, summary_tok))
    return texts


@asynccontextmanager
async def _running_api_server(port: int):
    """Avvia l'app FastAPI in-process (stesso processo Python del pilot, così il
    monkeypatch di ContextBudgetManager applicato dal pilot ha effetto anche sulle
    richieste servite). Nessun file di produzione viene modificato su disco."""
    import uvicorn
    from aiura_legal.api.app import app

    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    try:
        for _ in range(100):
            if server.started:
                break
            await asyncio.sleep(0.1)
        else:
            raise RuntimeError("Server pilot non avviato entro 10s")
        yield
    finally:
        server.should_exit = True
        await task


def _load_eval_queries(path: Path, module_filter: str | None) -> list[EvalQuery]:
    queries: list[EvalQuery] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            data = json.loads(line)
            if module_filter and data.get("module", "") != module_filter:
                continue
            queries.append(EvalQuery(
                id=data["id"],
                query=data["query"],
                workspace=data.get("workspace", "default"),
                intent=data.get("intent", "retrieval"),
                expected_source_ids=data.get("expected_source_ids", []),
                module=data.get("module", ""),
                difficulty=data.get("difficulty", "medium"),
                top_k=data.get("top_k", 10),
            ))
    return queries


async def run_gate2(queries_path: Path, module_filter: str | None) -> dict:
    queries = _load_eval_queries(queries_path, module_filter)
    if not queries:
        logger.warning(f"[Gate2] nessuna query trovata in {queries_path} (modulo={module_filter})")
        return {}

    evaluator = Evaluator(api_base_url=f"http://127.0.0.1:{_PILOT_API_PORT}")

    async with _running_api_server(_PILOT_API_PORT):
        logger.info(f"[Gate2] run BASELINE ({len(queries)} query)")
        baseline_results = await evaluator.run_all(queries)
        baseline_report = Evaluator.build_report(baseline_results, "pilot-baseline", str(queries_path))

        logger.info(f"[Gate2] run HEADROOM ({len(queries)} query)")
        with patch.object(ContextBudgetManager, "budget_texts", _headroom_budget_texts):
            headroom_results = await evaluator.run_all(queries)
        headroom_report = Evaluator.build_report(headroom_results, "pilot-headroom", str(queries_path))

    logger.info(
        f"[Gate2] pass_rate baseline={baseline_report.pass_rate:.1%}  "
        f"headroom={headroom_report.pass_rate:.1%}"
    )
    logger.info(
        f"[Gate2] groundedness baseline={baseline_report.mean_groundedness:.2f}  "
        f"headroom={headroom_report.mean_groundedness:.2f}"
    )

    return {"baseline": baseline_report, "headroom": headroom_report}


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _write_report(gate1: dict[str, Gate1CorpusReport], gate2: dict, out_path: Path) -> None:
    lines = ["# Pilot Headroom — report\n"]

    lines.append("## Gate 1 — integrità testuale\n")
    lines.append("| Corpus | Integrità | Chunk testati | Token risparmiati (media) |")
    lines.append("|---|---|---|---|")
    for corpus, report in gate1.items():
        lines.append(
            f"| {corpus} | {report.integrity_rate:.1%} | {report.total} | "
            f"{report.avg_tokens_saved_pct:.1f}% |"
        )

    any_failures = any(r.failed for r in gate1.values())
    if any_failures:
        lines.append("\n### Chunk falliti (pattern critici persi)\n")
        for corpus, report in gate1.items():
            for f in report.failed:
                lines.append(f"- `{f.chunk_id}` ({corpus}): mancano {f.missing_patterns}")

    if gate2:
        baseline, headroom = gate2["baseline"], gate2["headroom"]
        lines.append("\n## Gate 2 — eval end-to-end\n")
        lines.append("| Metrica | Baseline | Headroom |")
        lines.append("|---|---|---|")
        lines.append(f"| pass_rate | {baseline.pass_rate:.1%} | {headroom.pass_rate:.1%} |")
        lines.append(
            f"| mean_groundedness | {baseline.mean_groundedness:.2f} | "
            f"{headroom.mean_groundedness:.2f} |"
        )
        rb = f"{baseline.mean_recall_at_k:.2f}" if baseline.mean_recall_at_k is not None else "N/A"
        rh = f"{headroom.mean_recall_at_k:.2f}" if headroom.mean_recall_at_k is not None else "N/A"
        lines.append(f"| mean_recall_at_k | {rb} | {rh} |")
    else:
        lines.append("\n## Gate 2 — non eseguito\n")
        lines.append("(soglia Gate 1 non raggiunta per nessun corpus, oppure `--skip-gate2`)")

    lines.append("\n## Raccomandazione\n")
    avg_integrity = (
        sum(r.integrity_rate for r in gate1.values()) / len(gate1) if gate1 else 0.0
    )
    if avg_integrity >= _GATE1_THRESHOLD:
        lines.append(
            "Gate 1 superato: la compressione preserva i pattern critici. "
            + ("Procedere con l'integrazione reale se anche il Gate 2 confirma pass_rate stabile."
               if gate2 else "Eseguire il Gate 2 per confermare prima di integrare.")
        )
    else:
        lines.append(
            "Gate 1 non superato per uno o più corpus: scartare l'integrazione, oppure "
            "limitarla ai soli corpus che superano la soglia (verificare la tabella sopra)."
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.success(f"Report scritto in {out_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(args: argparse.Namespace) -> None:
    if not _HEADROOM_AVAILABLE:
        logger.error(
            "headroom-ai non installato. Esegui: pip install -e \".[headroom]\""
        )
        sys.exit(1)

    gate1 = await run_gate1(args.sample_size)
    avg_integrity = sum(r.integrity_rate for r in gate1.values()) / len(gate1) if gate1 else 0.0

    gate2: dict = {}
    if args.skip_gate2:
        logger.info("[Gate2] saltato (--skip-gate2)")
    elif avg_integrity < _GATE1_THRESHOLD:
        logger.warning(
            f"[Gate2] saltato: integrità media {avg_integrity:.1%} < soglia {_GATE1_THRESHOLD:.0%}"
        )
    else:
        gate2 = await run_gate2(Path(args.queries), args.module)

    _write_report(gate1, gate2, _OUTPUT_DIR / "pilot_headroom_report.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pilot di valutazione Headroom")
    parser.add_argument("--sample-size", type=int, default=50,
                         help="Numero di chunk per corpus da campionare (default 50)")
    parser.add_argument("--queries", default="tests/script_json/test_aiura_01.jsonl",
                         help="File JSONL di query per il Gate 2")
    parser.add_argument("--module", default=None,
                         help="Filtra le query del Gate 2 per modulo (es. cod_civ)")
    parser.add_argument("--skip-gate2", action="store_true",
                         help="Esegue solo il Gate 1 (integrità testuale)")
    parsed = parser.parse_args()
    asyncio.run(main(parsed))
