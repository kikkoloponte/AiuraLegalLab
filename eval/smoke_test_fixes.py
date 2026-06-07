"""
Smoke test per le 3 fix:
  1. S5 cattura source_id non nel packet (Q10 — art.612-bis)
  2. Snippet 400→800 (Q15 — silenzio-assenso, eccezioni)
  3. Step name normalizzato (QUALIFICAZIONE senza typo)
"""
import asyncio
import httpx

API = "http://127.0.0.1:8765"


async def query(qid: str, text: str, intent: str = "norma_lookup") -> dict:
    async with httpx.AsyncClient(timeout=120) as c:
        r = await c.post(f"{API}/query", json={
            "query": text,
            "workspace": "normattiva",
            "intent": intent,
            "top_k": 7,
            "clarification_turn": 2,
        })
        r.raise_for_status()
        return r.json()


async def main() -> None:
    # ── Test 1: S5 deve bloccare citazioni non nel packet (Q10) ──────────
    print("=" * 65)
    print("TEST 1 — S5 Reviewer: art.612-bis non nel packet")
    print("=" * 65)
    d = await query(
        "Q10",
        "Cosa prevede l'art. 612-bis c.p. in materia di atti persecutori (stalking)?",
        "norma_lookup",
    )
    verdict = d["reviewer_verdict"]
    action  = d.get("reviewer_action", "?")
    warnings = d.get("warnings", [])
    secs = d.get("analysis_sections", [])
    step0 = secs[0]["step"] if secs else "N/A"

    print(f"  Reviewer verdict : {verdict}  (atteso: FAIL o PASS se model ok)")
    print(f"  Reviewer action  : {action}")
    print(f"  Warnings         : {warnings}")
    print(f"  Step[0] name     : {step0!r}  (atteso: 'QUALIFICAZIONE')")
    print()

    ok_step = step0 == "QUALIFICAZIONE"
    print(f"  ✅ Step normalizzato" if ok_step else f"  ❌ Step ancora sbagliato: {step0!r}")
    # Il verdict dipende da cosa genera il modello — può essere PASS se il
    # modello questa volta non cita source_id fuori packet.
    print()

    # ── Test 2: snippet più lungo → Q15 deve rispondere alle eccezioni ───
    print("=" * 65)
    print("TEST 2 — Snippet 800 char: silenzio-assenso + eccezioni (Q15)")
    print("=" * 65)
    d2 = await query(
        "Q15",
        "Qual è la disciplina del silenzio-assenso nella L. 241/1990 e le sue eccezioni?",
        "fattispecie_analysis",
    )
    answer = d2.get("answer", "")
    sources = d2.get("sources", [])
    secs2   = d2.get("analysis_sections", [])
    step0_2 = secs2[0]["step"] if secs2 else "N/A"

    print(f"  Fonti recuperate : {[s['source_id'] for s in sources]}")
    print(f"  Step[0] name     : {step0_2!r}  (atteso: 'QUALIFICAZIONE')")
    print()
    print("  ANSWER (prime 600 char):")
    for line in answer[:600].splitlines():
        print(f"    {line}")
    # Verifica menzione eccezioni
    has_eccezioni = any(w in answer.lower() for w in ["eccezioni", "eccezion", "comma 4", "ambiente", "salute", "patrimonio"])
    print()
    print(f"  {'✅' if has_eccezioni else '❌'} Mention eccezioni: {has_eccezioni}")
    ok_step2 = step0_2 == "QUALIFICAZIONE"
    print(f"  {'✅' if ok_step2 else '❌'} Step normalizzato: {ok_step2}")
    print()

    print("Fine smoke test.")


if __name__ == "__main__":
    asyncio.run(main())
