"""
Esegue le 10 query del golden test set v2 (con giurisprudenza)
e salva i risultati in JSON per la generazione del documento.
"""
import asyncio, sys, json, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from loguru import logger

API = "http://127.0.0.1:8765"
WORKSPACE = "mio-studio"
OUT = Path("C:/project/AiUraLegalLab/docs/golden_v2_results.json")

QUERIES = [
    {"id": 1, "difficolta": "Facile", "norma": "D.Lgs. 74/2000 art. 2",
     "modulo": "Penale Tributario",
     "query": "Quali sono gli elementi costitutivi del reato di dichiarazione fraudolenta mediante uso di fatture o altri documenti per operazioni inesistenti ai sensi dell'art. 2 del D.Lgs. 74/2000?"},
    {"id": 2, "difficolta": "Media", "norma": "D.Lgs. 74/2000 art. 4",
     "modulo": "Penale Tributario",
     "query": "Quali sono le soglie di punibilità previste dall'art. 4 del D.Lgs. 74/2000 per il reato di dichiarazione infedele e come si calcola l'imposta evasa?"},
    {"id": 3, "difficolta": "Facile", "norma": "D.Lgs. 74/2000 art. 10-ter",
     "modulo": "Penale Tributario",
     "query": "Qual è la soglia di rilevanza penale e il termine entro cui deve avvenire il versamento IVA per evitare il reato di omesso versamento ex art. 10-ter D.Lgs. 74/2000?"},
    {"id": 4, "difficolta": "Media", "norma": "D.Lgs. 74/2000 art. 10-quater",
     "modulo": "Penale Tributario",
     "query": "Qual è la differenza tra crediti inesistenti e crediti non spettanti nella fattispecie di indebita compensazione ex art. 10-quater D.Lgs. 74/2000 e quali sono le rispettive soglie di punibilità?"},
    {"id": 5, "difficolta": "Media", "norma": "D.Lgs. 74/2000 artt. 13-13bis",
     "modulo": "Penale Tributario",
     "query": "Quando il ravvedimento operoso e il pagamento del debito tributario costituiscono causa di non punibilità dei reati tributari ai sensi degli artt. 13 e 13-bis del D.Lgs. 74/2000?"},
    {"id": 6, "difficolta": "Difficile", "norma": "D.Lgs. 74/2000 art. 12-bis",
     "modulo": "Penale Tributario",
     "query": "Quali sono i presupposti e il regime della confisca obbligatoria per equivalente nei reati tributari ai sensi dell'art. 12-bis D.Lgs. 74/2000 e quali beni possono essere aggrediti?"},
    {"id": 7, "difficolta": "Difficile", "norma": "D.Lgs. 231/2001 art. 25-quinquiesdecies",
     "modulo": "Penale Tributario / 231",
     "query": "Quando una società risponde ai sensi del D.Lgs. 231/2001 per i reati tributari commessi nel suo interesse o vantaggio da soggetti apicali o sottoposti? Quali reati sono presupposto e quali sanzioni si applicano ex art. 25-quinquiesdecies?"},
    {"id": 8, "difficolta": "Difficile", "norma": "D.Lgs. 74/2000 art. 19",
     "modulo": "Penale Tributario",
     "query": "Come si coordinano le sanzioni amministrative tributarie e le sanzioni penali per i reati tributari? Quando opera il principio di specialità ex art. 19 D.Lgs. 74/2000 e quando invece si applica il cumulo con le sanzioni del D.Lgs. 472/1997?"},
    {"id": 9, "difficolta": "Difficile", "norma": "c.p.p. / D.Lgs. 74/2000",
     "modulo": "Penale Tributario / Processuale",
     "query": "Quali sono i presupposti per disporre il sequestro preventivo finalizzato alla confisca in un procedimento per reato tributario? Quale è il rapporto tra sequestro penale e misure cautelari fiscali?"},
    {"id": 10, "difficolta": "Molto difficile", "norma": "D.Lgs. 74/2000 art. 4 / TUIR",
     "modulo": "Penale Tributario",
     "query": "Come si determina la base imponibile IRPEF/IRES ai fini del calcolo dell'imposta evasa nel reato di dichiarazione infedele ex art. 4 D.Lgs. 74/2000? Quali componenti reddituali del TUIR rilevano per la soglia di punibilità?"},
]


async def run_query(client: httpx.AsyncClient, q: dict) -> dict:
    logger.info("Query {}/10: {}", q["id"], q["query"][:70])
    t0 = time.monotonic()
    try:
        resp = await client.post(
            f"{API}/query",
            json={"query": q["query"], "workspace": WORKSPACE},
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        elapsed = time.monotonic() - t0
        logger.success("  Query {}: {} in {:.0f}s", q["id"], data.get("verdict", "?"), elapsed)
        return {**q, "response": data, "elapsed_s": round(elapsed, 1)}
    except Exception as e:
        logger.error("  Query {} fallita: {}", q["id"], e)
        return {**q, "response": None, "error": str(e)}


async def main():
    logger.info("Golden Test Set v2 — {} query", len(QUERIES))
    async with httpx.AsyncClient() as client:
        results = []
        for q in QUERIES:
            r = await run_query(client, q)
            results.append(r)
            await asyncio.sleep(2)  # pausa tra query

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.success("Risultati salvati in {}", OUT)

    ok = sum(1 for r in results if r.get("response"))
    logger.info("Completate: {}/{}", ok, len(QUERIES))


asyncio.run(main())
