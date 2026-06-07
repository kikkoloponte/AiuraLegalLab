"""
run_query_suite.py — Esegue tutte le query JSONL e salva un MD per query.

Uso:
  python scripts/run_query_suite.py
  python scripts/run_query_suite.py --jsonl tests/script_json/queries_civ.jsonl
  python scripts/run_query_suite.py --workspace normattiva   # forza workspace
  python scripts/run_query_suite.py --out-dir eval/runs/mia_sessione

Output:
  eval/query_results/YYYYMMDD_HHMMSS/
      <file>/
          <id>.md       ← un file per query
          _summary.md   ← riepilogo per file JSONL
      _global_summary.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

API_URL = "http://127.0.0.1:8765"
DEFAULT_JSONL_DIR = Path("tests/script_json")
DEFAULT_OUT_BASE = Path("eval/query_results")

# Workspace fallback: se il workspace richiesto non ha indici costruiti,
# usa "normattiva" che ha tutto il corpus indicizzato.
WORKSPACE_FALLBACK = "normattiva"
INDEXED_WORKSPACES: set[str] = {"normattiva"}  # aggiorna se buildi altri

# ---------------------------------------------------------------------------
# Domain filter — BM25 source_id patterns per dominio
# Limita il retrieval BM25 agli atti fiscali per le query tributarie,
# evitando che CPC/CC/Costituzione (3000+ chunk) soffochino gli atti tributari.
# ---------------------------------------------------------------------------

_TRIB_SOURCE_ID_PATTERNS: list[str] = [
    "legge:2000-07-27;212",         # Statuto Contribuente L.212/2000
    "1973-09-29;600",                # DPR 600/1973 Accertamento IRPEF
    "1973-09-29;602",                # DPR 602/1973 Riscossione
    "1972-10-26;633",                # DPR 633/1972 IVA
    "1986-12-22;917",                # DPR 917/1986 TUIR
    "decreto.legislativo:1997-12-18;471",  # D.Lgs.471/1997 Sanzioni
    "decreto.legislativo:1997-12-18;472",  # D.Lgs.472/1997 Sanzioni proc.
    "decreto.legislativo:1997-06-19;218",  # D.Lgs.218/1997 Accertamento adesione
    "decreto.legislativo:1997-07-09;241",  # D.Lgs.241/1997 Compensazione
    "decreto.legislativo:2000-03-10;74",   # D.Lgs.74/2000 Reati tributari
    "decreto.legislativo:1992-12-31;546",  # D.Lgs.546/1992 Processo trib. (abrogato)
    "decreto.legislativo:2024-11-14;175",  # D.Lgs.175/2024 Codice processo trib.
    "legge:1990-08-07;241",          # L.241/1990 Procedimento amm. (rilevante x trib.)
    "decreto.legislativo:2001-03-30;165",  # D.Lgs.165/2001 Dipendenti PA (rilevante)
    "decreto.legislativo:2019-01-12;14",   # D.Lgs.14/2019 Codice Crisi (proc. fall.)
]


def _domain_chunk_filter(original_workspace: str) -> Optional[dict]:
    """
    Chunk filter domain-aware basato sul workspace originale della query.
    Per 'tributario': restringe BM25 agli atti fiscali per evitare
    corpus dilution da CPC/CC/Costituzione.
    Per 'cross' e altri: nessun filtro (corpus completo).
    """
    if "tributario" in original_workspace:
        return {"_source_id_in": _TRIB_SOURCE_ID_PATTERNS}
    return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _recall(expected: list[str], sources: list[dict]) -> tuple[float, list[str], list[str]]:
    """Calcola recall@k. Ritorna (score, found_ids, missing_ids)."""
    retrieved_ids = {s.get("source_id", s.get("doc_id", "")) for s in sources}

    def _matches(exp: str, retrieved: set[str]) -> bool:
        # tollerante: strip ~artN suffix per confronto atto
        exp_base = re.sub(r"~art[\w-]+$", "", exp)
        for r in retrieved:
            r_base = re.sub(r"~art[\w-]+$", "", r)
            if r == exp or r_base == exp_base or r == exp_base or r_base == exp:
                return True
        return False

    found = [e for e in expected if _matches(e, retrieved_ids)]
    missing = [e for e in expected if not _matches(e, retrieved_ids)]
    score = len(found) / len(expected) if expected else 1.0
    return score, found, missing


def _snippet(text: str, max_chars: int = 300) -> str:
    text = text.replace("\n", " ").strip()
    return text[:max_chars] + "…" if len(text) > max_chars else text


def _safe_md(text: str) -> str:
    """Escapa caratteri problematici per le tabelle Markdown."""
    return text.replace("|", "\\|").replace("\n", " ")


# ---------------------------------------------------------------------------
# Chiamata API
# ---------------------------------------------------------------------------

def call_api(
    query_obj: dict,
    workspace_override: Optional[str],
    timeout: int = 120,
    clarification_turn: int = 2,
) -> dict:
    original_ws = query_obj["workspace"]
    ws = workspace_override or (
        original_ws if original_ws in INDEXED_WORKSPACES
        else WORKSPACE_FALLBACK
    )
    # Domain filter: restringe BM25 per query tributarie (evita corpus dilution)
    domain_filter = _domain_chunk_filter(original_ws)
    payload = {
        "query": query_obj["query"],
        "workspace": ws,
        "intent": _map_intent(query_obj.get("intent", "retrieval")),
        "top_k": 10,
        "clarification_turn": clarification_turn,
    }
    if domain_filter:
        payload["chunk_filter"] = domain_filter
    ws_remapped = ws != original_ws

    t0 = time.monotonic()
    resp = httpx.post(f"{API_URL}/query", json=payload, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()
    data["_elapsed_s"] = time.monotonic() - t0
    data["_workspace_used"] = ws
    data["_workspace_remapped"] = ws_remapped
    data["_workspace_original"] = query_obj["workspace"]
    return data


def _map_intent(raw: str) -> str:
    mapping = {
        "retrieval": "norma_lookup",
        "norma_lookup": "norma_lookup",
        "reasoning": "fattispecie_analysis",
        "fattispecie_analysis": "fattispecie_analysis",
        "giurisprudenza": "giurisprudenza_search",
        "evolution": "norma_evolution",
        "contrattuale": "rischio_contrattuale",
    }
    return mapping.get(raw.lower(), "fattispecie_analysis")


# ---------------------------------------------------------------------------
# Generazione MD
# ---------------------------------------------------------------------------

def _render_md(query_obj: dict, resp: dict) -> str:
    qid = query_obj["id"]
    module = query_obj.get("module", "?")
    difficulty = query_obj.get("difficulty", "?")
    expected = query_obj.get("expected_source_ids", [])
    sources = resp.get("sources", [])
    answer = resp.get("answer", "").strip()
    sections = resp.get("analysis_sections", [])
    verdict = resp.get("reviewer_verdict", "?")
    action = resp.get("reviewer_action", "?")
    warnings = resp.get("warnings", [])
    confidence = resp.get("overall_confidence", "?")
    ret_confidence = resp.get("retrieval_confidence", "?")
    gaps = resp.get("gaps", [])
    dur_ret = resp.get("duration_retrieval_s", 0)
    dur_llm = resp.get("duration_llm_s", 0)
    dur_tot = resp.get("duration_total_s", 0)
    ws_used = resp.get("_workspace_used", "?")
    ws_orig = resp.get("_workspace_original", "?")
    ws_remapped = resp.get("_workspace_remapped", False)
    elapsed = resp.get("_elapsed_s", 0)

    recall_score, found_ids, missing_ids = _recall(expected, sources)

    # Header emoji
    recall_icon = "✅" if recall_score >= 1.0 else ("⚠️" if recall_score > 0 else "❌")
    verdict_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(verdict, "❓")

    lines: list[str] = []
    lines.append(f"# {qid} — {module}")
    lines.append("")
    lines.append("| Campo | Valore |")
    lines.append("|---|---|")
    lines.append(f"| **Data** | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} |")
    lines.append(f"| **Difficoltà** | {difficulty} |")
    lines.append(f"| **Intent** | {query_obj.get('intent','?')} → {_map_intent(query_obj.get('intent',''))} |")
    ws_note = f"{ws_used} *(remappato da {ws_orig})*" if ws_remapped else ws_used
    lines.append(f"| **Workspace** | {ws_note} |")
    lines.append(f"| **Recall@10** | {recall_score:.2f} {recall_icon} ({len(found_ids)}/{len(expected)}) |")
    lines.append(f"| **Reviewer** | {verdict_icon} {verdict} / {action} |")
    lines.append(f"| **Confidenza retrieval** | {ret_confidence} |")
    lines.append(f"| **Confidenza analisi** | {confidence} |")
    lines.append(f"| **Latenza** | {elapsed:.1f}s (ret {dur_ret:.1f}s + llm {dur_llm:.1f}s) |")
    lines.append("")

    # Query
    lines.append("## Query")
    lines.append("")
    lines.append(f"> {query_obj['query']}")
    lines.append("")

    # Risposta LLM
    lines.append("## Risposta")
    lines.append("")
    if answer:
        lines.append(answer)
    else:
        lines.append("*Nessuna risposta generata (LLM non disponibile o skip).*")
    lines.append("")

    # CoT sections
    if sections:
        lines.append("## Analisi (Chain of Thought)")
        lines.append("")
        for sec in sections:
            step = sec.get("step", "")
            content = sec.get("content", "").strip()
            cits = sec.get("citations", [])
            lines.append(f"### {step}")
            lines.append("")
            lines.append(content)
            if cits:
                lines.append("")
                lines.append(f"*Citazioni: {', '.join(str(c) for c in cits[:5])}*")
            lines.append("")

    # Fonti
    lines.append("## Fonti recuperate")
    lines.append("")
    if sources:
        lines.append("| # | URN | Score | Metodo | Attesa |")
        lines.append("|---|---|---|---|---|")
        retrieved_set = {s.get("source_id", s.get("doc_id", "")) for s in sources}
        for s in sources:
            sid = s.get("source_id", s.get("doc_id", ""))
            score = s.get("score", 0)
            method = s.get("retrieval_method", "?")
            rank = s.get("rank", "?")
            # check se è attesa
            def _is_expected(sid: str, exp_list: list[str]) -> bool:
                sid_base = re.sub(r"~art\d+$", "", sid)
                for e in exp_list:
                    e_base = re.sub(r"~art\d+$", "", e)
                    if sid == e or sid_base == e_base or sid == e_base or sid_base == e:
                        return True
                return False
            attesa = "✅" if _is_expected(sid, expected) else ""
            lines.append(f"| {rank} | `{sid}` | {score:.4f} | {method} | {attesa} |")
        lines.append("")

        # Recall riepilogo
        if expected:
            lines.append(f"**Recall@10**: {recall_score:.2f} — trovate {len(found_ids)}/{len(expected)}")
            if missing_ids:
                lines.append("")
                lines.append("**Fonti attese non trovate:**")
                for m in missing_ids:
                    lines.append(f"- `{m}`")
        lines.append("")

        # Snippet per ogni fonte
        lines.append("### Snippet fonti")
        lines.append("")
        for s in sources:
            sid = s.get("source_id", s.get("doc_id", ""))
            snippet = s.get("snippet", "").strip()
            meta = s.get("metadata", {})
            titolo_art = meta.get("titolo_articolo", "") or meta.get("articolo_num", "")
            label = f"{titolo_art} — " if titolo_art else ""
            lines.append(f"**[{s.get('rank','?')}]** `{sid}`")
            if label:
                lines.append(f"*{label.strip(' —')}*")
            lines.append("")
            lines.append(f"> {_snippet(snippet, 350)}")
            lines.append("")
    else:
        lines.append("*Nessuna fonte recuperata.*")
        lines.append("")

    # Gaps
    if gaps:
        lines.append("## Gap identificati")
        lines.append("")
        for g in gaps:
            lines.append(f"- {g}")
        lines.append("")

    # CitationReviewer
    lines.append("## CitationReviewer")
    lines.append("")
    lines.append(f"| Campo | Valore |")
    lines.append("|---|---|")
    lines.append(f"| Verdict | {verdict_icon} {verdict} |")
    lines.append(f"| Action | {action} |")
    if warnings:
        lines.append(f"| Warnings | {'; '.join(warnings[:3])} |")
    else:
        lines.append("| Warnings | — |")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Summary MD per file JSONL
# ---------------------------------------------------------------------------

def _render_file_summary(
    jsonl_name: str,
    results: list[tuple[dict, dict]],
) -> str:
    lines = [f"# Riepilogo — {jsonl_name}", ""]
    lines.append(f"**Query totali**: {len(results)}")
    lines.append("")

    # Tabella
    lines.append("| ID | Difficoltà | Recall@10 | Reviewer | Latenza |")
    lines.append("|---|---|---|---|---|")
    recall_sum = 0.0
    for q, r in results:
        expected = q.get("expected_source_ids", [])
        sources = r.get("sources", [])
        recall, _, _ = _recall(expected, sources)
        recall_sum += recall
        recall_icon = "✅" if recall >= 1.0 else ("⚠️" if recall > 0 else "❌")
        verdict = r.get("reviewer_verdict", "?")
        verdict_icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(verdict, "❓")
        elapsed = r.get("_elapsed_s", 0)
        lines.append(
            f"| {q['id']} | {q.get('difficulty','?')} | {recall:.2f} {recall_icon} "
            f"| {verdict_icon} {verdict} | {elapsed:.1f}s |"
        )

    avg_recall = recall_sum / len(results) if results else 0.0
    lines.append("")
    lines.append(f"**Recall@10 medio**: {avg_recall:.3f}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Global summary MD
# ---------------------------------------------------------------------------

def _render_global_summary(
    all_results: dict[str, list[tuple[dict, dict]]],
    run_dir: Path,
) -> str:
    lines = [
        "# Global Summary — AiUra LegalLab Query Suite",
        "",
        f"**Data**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Output**: `{run_dir}`",
        "",
        "| File | Query | Recall medio | Pass% |",
        "|---|---|---|---|",
    ]
    total_q = 0
    total_recall = 0.0
    for fname, results in all_results.items():
        recalls = []
        for q, r in results:
            expected = q.get("expected_source_ids", [])
            sources = r.get("sources", [])
            rec, _, _ = _recall(expected, sources)
            recalls.append(rec)
        avg = sum(recalls) / len(recalls) if recalls else 0.0
        pct = sum(1 for r in recalls if r >= 1.0) / len(recalls) * 100 if recalls else 0.0
        lines.append(f"| {fname} | {len(results)} | {avg:.3f} | {pct:.0f}% |")
        total_q += len(results)
        total_recall += sum(recalls)

    avg_total = total_recall / total_q if total_q else 0.0
    lines.append("")
    lines.append(f"**Totale query**: {total_q}  |  **Recall medio globale**: {avg_total:.3f}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Run query suite → MD files per query")
    parser.add_argument("--jsonl", nargs="+", default=None,
                        help="Uno o più file JSONL (default: tutti in tests/script_json/)")
    parser.add_argument("--workspace", default=None,
                        help="Forza workspace per tutte le query (default: auto)")
    parser.add_argument("--out-dir", default=None,
                        help="Directory output (default: eval/query_results/TIMESTAMP)")
    parser.add_argument("--api-url", default=API_URL,
                        help=f"URL API (default: {API_URL})")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Timeout per query in secondi (default: 120)")
    parser.add_argument("--enable-s1", action="store_true",
                        help="Abilita S1 Clarifier (default: bypass per batch)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Stampa query senza chiamare API")
    args = parser.parse_args()

    # Verifica API
    try:
        health = httpx.get(f"{args.api_url}/health", timeout=5).json()
        if health.get("status") != "ok":
            print(f"WARN: API health={health.get('status')}")
    except Exception as e:
        print(f"ERRORE: API non raggiungibile a {args.api_url}: {e}", file=sys.stderr)
        sys.exit(1)

    # Raccoglie file JSONL
    if args.jsonl:
        jsonl_files = [Path(f) for f in args.jsonl]
    else:
        jsonl_files = sorted(DEFAULT_JSONL_DIR.glob("*.jsonl"))

    if not jsonl_files:
        print("Nessun file JSONL trovato.", file=sys.stderr)
        sys.exit(1)

    # Directory output
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(args.out_dir) if args.out_dir else DEFAULT_OUT_BASE / ts
    run_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output: {run_dir}")
    print(f"File JSONL: {[f.name for f in jsonl_files]}")
    print()

    all_results: dict[str, list[tuple[dict, dict]]] = {}

    for jf in jsonl_files:
        queries = [json.loads(l) for l in jf.read_text(encoding="utf-8").splitlines() if l.strip()]
        fname = jf.stem
        file_dir = run_dir / fname
        file_dir.mkdir(exist_ok=True)
        file_results: list[tuple[dict, dict]] = []

        print(f"=== {jf.name} ({len(queries)} query) ===")

        for i, q in enumerate(queries, 1):
            qid = q["id"]
            print(f"  [{i:>2}/{len(queries)}] {qid}  ", end="", flush=True)

            if args.dry_run:
                print(f"(dry-run)")
                continue

            try:
                clarif_turn = 0 if args.enable_s1 else 2
                resp = call_api(q, args.workspace, timeout=args.timeout,
                                clarification_turn=clarif_turn)
                recall, _, _ = _recall(q.get("expected_source_ids", []), resp.get("sources", []))
                elapsed = resp.get("_elapsed_s", 0)
                verdict = resp.get("reviewer_verdict", "?")
                print(f"R={recall:.2f}  {elapsed:.1f}s  {verdict}")

                # Salva MD
                md_content = _render_md(q, resp)
                md_path = file_dir / f"{qid}.md"
                md_path.write_text(md_content, encoding="utf-8")

                file_results.append((q, resp))

            except Exception as e:
                print(f"ERRORE: {e}")
                file_results.append((q, {"sources": [], "reviewer_verdict": "ERROR",
                                         "reviewer_action": "BLOCK", "warnings": [str(e)],
                                         "answer": "", "_elapsed_s": 0,
                                         "_workspace_used": "?", "_workspace_remapped": False,
                                         "_workspace_original": q.get("workspace", "?")}))

        # Summary per file
        if not args.dry_run:
            summary_md = _render_file_summary(jf.name, file_results)
            (file_dir / "_summary.md").write_text(summary_md, encoding="utf-8")
            all_results[fname] = file_results

        print()

    # Global summary
    if not args.dry_run and all_results:
        global_md = _render_global_summary(all_results, run_dir)
        (run_dir / "_global_summary.md").write_text(global_md, encoding="utf-8")
        print(f"\nRiepilogo globale: {run_dir / '_global_summary.md'}")

    print("Fine.")


if __name__ == "__main__":
    main()
