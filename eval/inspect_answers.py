"""
Script temporaneo per ispezionare la qualità delle risposte LLM.
Esegue 5 query rappresentative e stampa answer + analysis_sections.
"""
import asyncio
import httpx

API = "http://127.0.0.1:8765"

QUERIES = [
    ("Q01", "easy",   "cod_civ", "norma_lookup",        "Quali sono i requisiti di forma per la validità del contratto secondo il Codice Civile?"),
    ("Q05", "hard",   "cod_civ", "fattispecie_analysis", "Analizza il rapporto tra azione revocatoria ordinaria (art. 2901 c.c.) e fallimentare, individuando presupposti e differenze."),
    ("Q10", "easy",   "pen",     "norma_lookup",        "Cosa prevede l'art. 612-bis c.p. in materia di atti persecutori (stalking)?"),
    ("Q15", "medium", "amm",     "fattispecie_analysis", "Qual è la disciplina del silenzio-assenso nella L. 241/1990 e le sue eccezioni?"),
    ("Q19", "hard",   "fam",     "fattispecie_analysis", "Quali sono i presupposti e gli effetti dell'assegno divorzile dopo le Sezioni Unite 18287/2018?"),
]


async def run_query(qid: str, difficulty: str, module: str, intent: str, query: str) -> None:
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(f"{API}/query", json={
            "query": query,
            "workspace": "mio-studio",
            "intent": intent,
            "top_k": 7,
            "clarification_turn": 2,
        })
        resp.raise_for_status()
        d = resp.json()

    sep = "=" * 70
    print(f"\n{sep}")
    print(f"  {qid}  [{difficulty}]  modulo={module}  intent={intent}")
    print(f"  Query: {query}")
    print(sep)
    print(f"  Confidence: {d['retrieval_confidence']}  |  Reviewer: {d['reviewer_verdict']}")
    print(f"  LLM model: {d.get('llm_model', '—')}  |  LLM available: {d.get('llm_available')}")
    print(f"  Latency total: {d.get('duration_total_s', 0):.2f}s  "
          f"retrieval: {d.get('duration_retrieval_s', 0):.2f}s  "
          f"llm: {d.get('duration_llm_s', 0):.2f}s")
    print()
    print("  SOURCES:")
    for s in d.get("sources", []):
        print(f"    [{s['rank']}] {s['source_id']}  score={s['score']}")
    print()
    print("  ANSWER:")
    answer = d.get("answer", "")
    if answer:
        for line in answer.splitlines():
            print(f"    {line}")
    else:
        print("    (vuoto)")
    print()

    sections = d.get("analysis_sections", [])
    if sections:
        print("  ANALYSIS SECTIONS:")
        for sec in sections:
            print(f"    [{sec['step']}] {sec['content'][:200]}{'...' if len(sec['content']) > 200 else ''}")
            if sec.get("citations"):
                print(f"      → citazioni: {sec['citations']}")
        print()


async def main() -> None:
    print("Ispezione qualità risposte LLM — 5 query campione")
    for args in QUERIES:
        await run_query(*args)
    print("\nFine ispezione.")


if __name__ == "__main__":
    asyncio.run(main())
