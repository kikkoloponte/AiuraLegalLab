"""
run_golden_queries.py — Esegue le 10 query del Golden Test Set (penale tributario)
e salva i risultati in golden_results.json + golden_results.md

Uso:
    python run_golden_queries.py
    python run_golden_queries.py --api-url http://127.0.0.1:8765
    python run_golden_queries.py --workspace normattiva
    python run_golden_queries.py --scheda 7        # esegue solo la scheda 7
"""
import argparse
import json
import time
from datetime import datetime
from pathlib import Path

import httpx

# ── Le 10 query del Golden Test Set ──────────────────────────────────────────

QUERIES = [
    {
        "scheda": 1,
        "tema": "Dichiarazione fraudolenta con fatture false",
        "difficolta": "Facile",
        "norma_cardine": "D.Lgs. 74/2000 art. 2",
        "query": (
            "Quali sono gli elementi costitutivi del reato di dichiarazione fraudolenta "
            "mediante uso di fatture o altri documenti per operazioni inesistenti "
            "ai sensi dell'art. 2 del D.Lgs. 74/2000?"
        ),
        "intent": "norma_lookup",
    },
    {
        "scheda": 2,
        "tema": "Dichiarazione infedele: soglia di punibilità",
        "difficolta": "Media",
        "norma_cardine": "D.Lgs. 74/2000 art. 4",
        "query": (
            "Quali sono le soglie di punibilità previste dall'art. 4 del D.Lgs. 74/2000 "
            "per il reato di dichiarazione infedele e come si calcola l'imposta evasa?"
        ),
        "intent": "norma_lookup",
    },
    {
        "scheda": 3,
        "tema": "Omesso versamento IVA: soglia e termine",
        "difficolta": "Facile",
        "norma_cardine": "D.Lgs. 74/2000 art. 10-ter",
        "query": (
            "Qual è la soglia di rilevanza penale e il termine entro cui deve avvenire "
            "il versamento IVA per evitare il reato di omesso versamento "
            "ex art. 10-ter D.Lgs. 74/2000?"
        ),
        "intent": "norma_lookup",
    },
    {
        "scheda": 4,
        "tema": "Indebita compensazione con crediti non spettanti",
        "difficolta": "Media",
        "norma_cardine": "D.Lgs. 74/2000 art. 10-quater",
        "query": (
            "Qual è la differenza tra crediti inesistenti e crediti non spettanti "
            "nella fattispecie di indebita compensazione ex art. 10-quater D.Lgs. 74/2000 "
            "e quali sono le rispettive soglie di punibilità?"
        ),
        "intent": "fattispecie_analysis",
    },
    {
        "scheda": 5,
        "tema": "Cause di non punibilità: ravvedimento operoso",
        "difficolta": "Media",
        "norma_cardine": "D.Lgs. 74/2000 artt. 13-13-bis",
        "query": (
            "Quando il ravvedimento operoso e il pagamento del debito tributario "
            "costituiscono causa di non punibilità dei reati tributari "
            "ai sensi degli artt. 13 e 13-bis del D.Lgs. 74/2000?"
        ),
        "intent": "norma_lookup",
    },
    {
        "scheda": 6,
        "tema": "Confisca per equivalente in materia tributaria",
        "difficolta": "Difficile",
        "norma_cardine": "D.Lgs. 74/2000 art. 12-bis",
        "query": (
            "Quali sono i presupposti e il regime della confisca obbligatoria "
            "per equivalente nei reati tributari ai sensi dell'art. 12-bis D.Lgs. 74/2000 "
            "e quali beni possono essere aggrediti?"
        ),
        "intent": "norma_lookup",
    },
    {
        "scheda": 7,
        "tema": "Responsabilità degli enti per reati tributari",
        "difficolta": "Difficile",
        "norma_cardine": "D.Lgs. 231/2001 art. 25-quinquiesdecies",
        "query": (
            "Quando una societa risponde ai sensi del D.Lgs. 231/2001 "
            "per i reati tributari commessi nel suo interesse o vantaggio "
            "da soggetti apicali o sottoposti? "
            "Quali reati sono presupposto e quali sanzioni si applicano "
            "ex art. 25-quinquiesdecies?"
        ),
        "intent": "fattispecie_analysis",
    },
    {
        "scheda": 8,
        "tema": "Cumulo sanzioni amministrative e penali (ne bis in idem)",
        "difficolta": "Difficile",
        "norma_cardine": "D.Lgs. 472/1997 + D.Lgs. 74/2000 art. 19",
        "query": (
            "Come si coordinano le sanzioni amministrative tributarie e le sanzioni penali "
            "per i reati tributari? "
            "Quando opera il principio di specialita ex art. 19 D.Lgs. 74/2000 "
            "e quando invece si applica il cumulo con le sanzioni del D.Lgs. 472/1997?"
        ),
        "intent": "fattispecie_analysis",
    },
    {
        "scheda": 9,
        "tema": "Sequestro preventivo: presupposti in reato tributario",
        "difficolta": "Media",
        "norma_cardine": "D.Lgs. 74/2000 + c.p.p.",
        "query": (
            "Quali sono i presupposti per disporre il sequestro preventivo finalizzato "
            "alla confisca in un procedimento per reato tributario? "
            "Quale e il rapporto tra sequestro penale e misure cautelari fiscali?"
        ),
        "intent": "norma_lookup",
    },
    {
        "scheda": 10,
        "tema": "Base imponibile TUIR e dichiarazione infedele [CROSS-MODULO]",
        "difficolta": "Difficile",
        "norma_cardine": "TUIR DPR 917/1986 + D.Lgs. 74/2000 art. 4",
        "query": (
            "Come si determina la base imponibile IRPEF/IRES ai fini del calcolo "
            "dell'imposta evasa nel reato di dichiarazione infedele ex art. 4 D.Lgs. 74/2000? "
            "Quali componenti reddituali del TUIR rilevano per la soglia di punibilita?"
        ),
        "intent": "fattispecie_analysis",
    },
]

# ── Helpers ───────────────────────────────────────────────────────────────────

SEPARATOR = "=" * 72


def call_query(client: httpx.Client, api_url: str, q: dict, workspace: str) -> dict:
    payload = {
        "query": q["query"],
        "workspace": workspace,
        "intent": q["intent"],
        "top_k": 10,
        "clarification_turn": 2,   # salta S1 Clarifier per esecuzione batch
    }
    t0 = time.perf_counter()
    try:
        resp = client.post(f"{api_url}/query", json=payload, timeout=120)
        latency_ms = (time.perf_counter() - t0) * 1000
        resp.raise_for_status()
        data = resp.json()
        data["_latency_ms"] = round(latency_ms)
        data["_error"] = None
    except Exception as e:
        latency_ms = (time.perf_counter() - t0) * 1000
        data = {"_latency_ms": round(latency_ms), "_error": str(e)}
    return data


def format_scheda(q: dict, result: dict) -> str:
    lines = [
        SEPARATOR,
        f"SCHEDA {q['scheda']} DI 10 — {q['tema'].upper()}",
        f"Difficolta: {q['difficolta']}  |  Norma cardine: {q['norma_cardine']}",
        f"Intent: {q['intent']}  |  Latenza: {result.get('_latency_ms', '?')} ms",
        SEPARATOR,
        "",
        "[ SCENARIO / QUERY ]",
        q["query"],
        "",
    ]

    if result.get("_error"):
        lines += [
            "[ ERRORE ]",
            result["_error"],
            "",
        ]
        return "\n".join(lines)

    # Risposta del sistema
    answer = result.get("answer", result.get("response", ""))
    reviewer = result.get("reviewer", {})
    verdict = reviewer.get("verdict", "?") if isinstance(reviewer, dict) else "?"
    action  = reviewer.get("action", "?")  if isinstance(reviewer, dict) else "?"

    lines += [
        f"[ RISPOSTA DEL SISTEMA ]  (reviewer: {verdict} → {action})",
        answer or "(nessuna risposta)",
        "",
        "[ FONTI CITATE DAL SISTEMA ]",
    ]

    sources = result.get("sources", [])
    if sources:
        for s in sources:
            rank      = s.get("rank", "?")
            source_id = s.get("source_id", s.get("doc_id", "?"))
            score     = s.get("score", 0)
            snippet   = s.get("snippet", "")[:120].replace("\n", " ")
            lines.append(f"  [{rank}] {source_id}  (score={score:.3f})")
            lines.append(f"      {snippet}...")
    else:
        lines.append("  (nessuna fonte restituita)")

    lines += ["", "[ NORME ATTESE — da compilare in videocall ]", "", ""]
    return "\n".join(lines)


def format_markdown(q: dict, result: dict) -> str:
    lines = [
        f"## Scheda {q['scheda']} — {q['tema']}",
        f"**Difficolta:** {q['difficolta']} | **Norma cardine:** `{q['norma_cardine']}` | "
        f"**Intent:** `{q['intent']}` | **Latenza:** {result.get('_latency_ms', '?')} ms",
        "",
        f"**Query:** {q['query']}",
        "",
    ]

    if result.get("_error"):
        lines += [f"> ⛔ ERRORE: {result['_error']}", ""]
        return "\n".join(lines)

    answer  = result.get("answer", result.get("response", ""))
    reviewer = result.get("reviewer", {})
    verdict  = reviewer.get("verdict", "?") if isinstance(reviewer, dict) else "?"
    action   = reviewer.get("action", "?")  if isinstance(reviewer, dict) else "?"

    lines += [
        f"**Reviewer:** `{verdict}` → `{action}`",
        "",
        "**Risposta:**",
        "",
        answer or "*(nessuna risposta)*",
        "",
        "**Fonti citate:**",
        "",
        "| # | Source ID | Score | Snippet |",
        "|---|-----------|-------|---------|",
    ]

    for s in result.get("sources", []):
        rank      = s.get("rank", "?")
        source_id = s.get("source_id", s.get("doc_id", "?"))
        score     = s.get("score", 0)
        snippet   = s.get("snippet", "")[:80].replace("\n", " ").replace("|", "/")
        lines.append(f"| {rank} | `{source_id}` | {score:.3f} | {snippet}... |")

    lines += ["", "---", ""]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Golden Test Set — esegui le 10 schede")
    parser.add_argument("--api-url",   default="http://127.0.0.1:8765")
    parser.add_argument("--workspace", default="mio-studio")
    parser.add_argument("--scheda",    type=int, default=None,
                        help="Esegui solo la scheda N (1-10)")
    parser.add_argument("--output-dir", default=".",
                        help="Directory dove salvare i risultati (default: root progetto)")
    args = parser.parse_args()

    queries = QUERIES if args.scheda is None else [q for q in QUERIES if q["scheda"] == args.scheda]
    if not queries:
        print(f"Scheda {args.scheda} non trovata (valori: 1-10)")
        return

    # Verifica API attiva
    try:
        resp = httpx.get(f"{args.api_url}/health", timeout=5)
        resp.raise_for_status()
        print(f"API attiva: {args.api_url}")
    except Exception as e:
        print(f"\nERRORE: API non raggiungibile — {e}")
        print("Avvia prima l'API con:  python -m aiura_legal.api")
        return

    print(f"Workspace: {args.workspace}")
    print(f"Schede da eseguire: {[q['scheda'] for q in queries]}\n")

    results_raw  = []
    text_parts   = [f"GOLDEN TEST SET — Penale Tributario\nEseguito: {datetime.now():%Y-%m-%d %H:%M}\n\n"]
    md_parts     = [f"# Golden Test Set — Penale Tributario\n**Eseguito:** {datetime.now():%Y-%m-%d %H:%M}\n\n"]

    with httpx.Client() as client:
        for q in queries:
            print(f"  Scheda {q['scheda']:2d}/10  {q['tema'][:50]}...", end=" ", flush=True)
            result = call_query(client, args.api_url, q, args.workspace)
            ms = result.get("_latency_ms", "?")
            err = result.get("_error")
            status = f"ERROR: {err[:50]}" if err else f"OK ({ms} ms)"
            print(status)

            results_raw.append({"scheda": q["scheda"], "tema": q["tema"],
                                 "query": q["query"], "result": result})
            text_parts.append(format_scheda(q, result))
            md_parts.append(format_markdown(q, result))

    # Salva output
    out = Path(args.output_dir)
    ts  = datetime.now().strftime("%Y%m%d_%H%M")

    json_path = out / f"golden_results_{ts}.json"
    txt_path  = out / f"golden_results_{ts}.txt"
    md_path   = out / f"golden_results_{ts}.md"

    json_path.write_text(json.dumps(results_raw, ensure_ascii=False, indent=2), encoding="utf-8")
    txt_path.write_text("\n".join(text_parts), encoding="utf-8")
    md_path.write_text("\n".join(md_parts), encoding="utf-8")

    print(f"\nRisultati salvati in:")
    print(f"  {json_path}  (dati completi)")
    print(f"  {txt_path}   (testo leggibile per le schede)")
    print(f"  {md_path}    (Markdown per documentazione)")
    print("\nCopia il contenuto del .txt nelle schede Word prima di inviare all'avvocato.")


if __name__ == "__main__":
    main()
