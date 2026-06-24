"""
Spike bm25s — decision gate per Fase 1 Step 1.0.

Misura su un corpus realistico:
  - tempo di build
  - RAM picco (tracciamento manuale con tracemalloc)
  - latenza query top-20
  - dimensione su disco (bm25s serializza l'indice)

Confronto con rank_bm25 (BM25Okapi) sullo stesso campione.

Uso:
  python scripts/spike_bm25s.py --n 500000       # corpus da 500k testi
  python scripts/spike_bm25s.py --n 2500000      # corpus massimo stimato Fase 1
  python scripts/spike_bm25s.py --mongo --n 200  # usa MongoDB reale (lento a caricare)
"""
from __future__ import annotations

import argparse
import gc
import os
import re
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path
from typing import Iterator

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from loguru import logger

# ---------------------------------------------------------------------------
# Tokenizzatore identico a bm25_retriever.py
# ---------------------------------------------------------------------------

_IT_STOPWORDS = frozenset({
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una",
    "di", "del", "della", "dei", "degli", "delle", "da", "dal", "dalla",
    "dai", "dagli", "dalle", "a", "al", "alla", "ai", "agli", "alle",
    "in", "nel", "nella", "nei", "negli", "nelle", "su", "sul", "sulla",
    "sui", "sugli", "sulle", "con", "per", "tra", "fra", "e", "ed",
    "o", "ma", "se", "non", "che", "chi", "cui", "ne", "ci", "si",
    "è", "sono", "ha", "hanno", "era", "were", "the", "of", "and",
    "quale", "quali", "questo", "questa", "questi", "queste",
    "dopo", "prima", "oltre", "anche", "come", "quando", "dove",
    "all", "dell", "nell",
})


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\w+", text.lower())
    return [t for t in tokens if len(t) >= 2 and t not in _IT_STOPWORDS]


# ---------------------------------------------------------------------------
# Generatore corpus sintetico realistico
# ---------------------------------------------------------------------------

_MOTIVAZIONE_TEMPLATE = """\
Con ricorso notificato il {giorno} {mese} 200{anno}, la parte ricorrente impugnava
la sentenza n. {num} del Tribunale di {citta} con la quale era stato rigettato il
ricorso proposto avverso il provvedimento dell'Agenzia delle Entrate relativo all'
accertamento di maggiori imposte per l'anno di imposta 200{anno2}. Il ricorrente
deduceva la violazione dell'articolo {art} del decreto legislativo n. {dlgs} del
{anno3}, lamentando l'illegittimità dell'avviso di accertamento per difetto di
motivazione e per erronea applicazione dei criteri di determinazione del reddito
imponibile. La Commissione Tributaria Provinciale, con sentenza depositata in data
{data_dep}, rigettava il ricorso ritenendo infondate le censure dedotte e confermando
integralmente l'operato dell'Amministrazione finanziaria. Avverso tale pronuncia il
contribuente proponeva appello alla Commissione Tributaria Regionale, che con sentenza
depositata confermava la decisione di primo grado, ritenendo corretta l'applicazione
dei coefficienti presuntivi e adeguata la motivazione dell'atto impositivo. Il
ricorrente proponeva quindi ricorso per cassazione affidato a {n_motivi} motivi di
ricorso, con i quali deduce violazione di legge, vizio di motivazione e travisamento
dei fatti. Il Procuratore Generale ha depositato conclusioni scritte chiedendo
l'accoglimento parziale del ricorso. Il Collegio, esaminati gli atti e sentiti i
difensori in camera di consiglio, ritiene il ricorso fondato nei termini di seguito
indicati. Il primo motivo di ricorso, con il quale si censura la sentenza impugnata
per violazione dell'art. {art2} del d.lgs. n. {dlgs2}/{anno4}, è infondato. Come
condivisibilmente osservato dalla Corte di merito, la motivazione dell'atto
impositivo deve essere valutata nella sua globalità, e non risulta viziata da
carenza argomentativa quando, come nella specie, richiama per relationem gli atti
istruttori che l'hanno preceduta e che sono stati portati a conoscenza del
contribuente. Il secondo motivo, attinente alla valutazione delle risultanze
documentali, è invece fondato. La Commissione Regionale ha omesso di esaminare la
documentazione prodotta dalla parte appellante, la quale era idonea a fornire la
prova contraria rispetto alle presunzioni utilizzate dall'Ufficio. Tale omissione
integra il vizio di omessa motivazione su un fatto decisivo e controverso, che
impone la cassazione con rinvio della sentenza impugnata. Il ricorso deve pertanto
essere accolto quanto al secondo motivo, con cassazione della sentenza impugnata e
rinvio alla Commissione Tributaria Regionale in diversa composizione, che
provvederà anche sulle spese del presente giudizio.
"""

_MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno",
         "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
_CITTA = ["Roma", "Milano", "Napoli", "Torino", "Bologna", "Firenze",
          "Palermo", "Bari", "Venezia", "Genova", "Trieste", "Catania"]


def _gen_corpus(n: int) -> Iterator[str]:
    """Genera n motivazioni sintetiche con variazione realistica (~2.700 token ciascuna)."""
    for i in range(n):
        yield _MOTIVAZIONE_TEMPLATE.format(
            giorno=1 + (i % 28),
            mese=_MESI[i % 12],
            anno=i % 9,
            anno2=(i % 9) + 1,
            anno3=1990 + (i % 30),
            anno4=2000 + (i % 22),
            num=10000 + i,
            citta=_CITTA[i % len(_CITTA)],
            art=1 + (i % 200),
            art2=2 + (i % 150),
            dlgs=100 + (i % 400),
            dlgs2=150 + (i % 300),
            data_dep=f"2{(i % 9) + 1}.0{(i % 9) + 1}.202{i % 4}",
            n_motivi=2 + (i % 5),
        )


def _load_mongo_corpus(n: int) -> list[str]:
    """Carica n motivazioni reali da MongoDB (lento, per validazione)."""
    from aiura_legal.ingestion.mongodb.client import MongoClient
    import asyncio

    async def _fetch():
        mongo = MongoClient.get()
        docs = []
        async for rec in mongo.db["jurisprudence"].find({}, {"motivazione": 1}).limit(n):
            mot = rec.get("motivazione", "")
            if mot and mot.strip():
                docs.append(mot)
        return docs

    return asyncio.run(_fetch())


# ---------------------------------------------------------------------------
# Peak RAM helper
# ---------------------------------------------------------------------------

def _measure_build(tokenized: list[list[str]], backend: str, tmp_dir: Path) -> dict:
    """
    Misura tempo di build, RAM picco e dimensione su disco per il backend dato.
    backend: "bm25s" | "rank_bm25"
    """
    gc.collect()
    tracemalloc.start()
    t0 = time.perf_counter()

    if backend == "bm25s":
        import bm25s
        corpus_tokens = [" ".join(t) for t in tokenized]
        retriever = bm25s.BM25()
        retriever.index(bm25s.tokenize(corpus_tokens, stopwords=None))
        idx_path = tmp_dir / "bm25s_index"
        retriever.save(str(idx_path))
        disk_bytes = sum(f.stat().st_size for f in idx_path.rglob("*") if f.is_file())
    else:
        from rank_bm25 import BM25Okapi
        retriever = BM25Okapi(tokenized)
        import pickle
        pkl_path = tmp_dir / "rank_bm25.pkl"
        with open(pkl_path, "wb") as f:
            pickle.dump(retriever, f)
        disk_bytes = pkl_path.stat().st_size

    t_build = time.perf_counter() - t0
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "backend":    backend,
        "build_s":    t_build,
        "peak_mb":    peak / 1024**2,
        "disk_mb":    disk_bytes / 1024**2,
        "retriever":  retriever,
        "idx_path":   str(tmp_dir / ("bm25s_index" if backend == "bm25s" else "rank_bm25.pkl")),
    }


def _measure_query(stats: dict, tokenized: list[list[str]], n_queries: int = 20) -> dict:
    """Misura latenza media per n_queries su top-20."""
    backend = stats["backend"]
    retriever = stats["retriever"]
    queries = [
        "responsabilità contrattuale risarcimento danni inadempimento",
        "licenziamento giusta causa giustificato motivo reintegra",
        "accertamento fiscale evasione imposte reddito imponibile",
        "concorso reati continuazione pena unificazione",
        "nullità contratto causa illecita forma scritta",
        "procedimento disciplinare pubblica amministrazione sanzione",
        "espropriazione pubblica utilità indennizzo valutazione",
        "divorzio mantenimento figli affidamento separazione",
        "lesione personale danno biologico liquidazione medico-legale",
        "frode fiscale evasione IVA responsabilità penale tributaria",
        "appalto pubblico offerta anomala esclusione gara aggiudicazione",
        "usucapione possesso animo domini acquisto proprietà",
        "successione testamento eredi legittimari quota",
        "diffamazione stampa internet risarcimento reputazione",
        "bancarotta fraudolenta fallimento reato societario",
        "infortunio lavoro responsabilità datore sicurezza",
        "abuso ufficio corruzione funzionario pubblico",
        "matrimonio annullamento impedimenti vizi consenso",
        "locazione sfratto morosità procedimento risoluzione",
        "fideiussione garanzia obbligazione accessoria escussione",
    ][:n_queries]

    latencies = []
    for q in queries:
        q_tokens = _tokenize(q)
        t0 = time.perf_counter()
        if backend == "bm25s":
            import bm25s
            q_str = " ".join(q_tokens)
            results, _ = retriever.retrieve(
                bm25s.tokenize([q_str], stopwords=None), k=20
            )
        else:
            retriever.get_scores(q_tokens)
        latencies.append(time.perf_counter() - t0)

    stats["query_avg_ms"] = sum(latencies) / len(latencies) * 1000
    stats["query_max_ms"] = max(latencies) * 1000
    return stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Spike bm25s vs rank_bm25")
    parser.add_argument("--n", type=int, default=500_000, help="Numero testi nel corpus")
    parser.add_argument("--mongo", action="store_true", help="Usa motivazioni reali da MongoDB")
    args = parser.parse_args()

    n = args.n
    logger.info(f"Caricamento corpus {n:,} testi...")
    t0 = time.perf_counter()
    if args.mongo:
        texts = _load_mongo_corpus(n)
        n = len(texts)
    else:
        texts = list(_gen_corpus(n))
    logger.info(f"  {n:,} testi caricati in {time.perf_counter()-t0:.1f}s")

    logger.info("Tokenizzazione corpus...")
    t0 = time.perf_counter()
    tokenized = [_tokenize(t) for t in texts]
    avg_tokens = sum(len(t) for t in tokenized) / len(tokenized)
    t_tokenize = time.perf_counter() - t0
    logger.info(f"  Tokenizzato in {t_tokenize:.1f}s — media {avg_tokens:.0f} token/doc")

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for backend in ("bm25s", "rank_bm25"):
            logger.info(f"--- BUILD: {backend} su {n:,} doc ---")
            try:
                stats = _measure_build(tokenized, backend, tmp_path)
                stats = _measure_query(stats, tokenized)
                results.append(stats)
                logger.info(
                    f"  build={stats['build_s']:.1f}s  "
                    f"peak_ram={stats['peak_mb']:.0f}MB  "
                    f"disk={stats['disk_mb']:.0f}MB  "
                    f"query_avg={stats['query_avg_ms']:.1f}ms  "
                    f"query_max={stats['query_max_ms']:.1f}ms"
                )
            except Exception as exc:
                logger.error(f"  FALLITO: {exc}")
                results.append({"backend": backend, "error": str(exc)})

    # Decisione
    print("\n" + "=" * 60)
    print(f"SPIKE bm25s — corpus {n:,} doc, avg {avg_tokens:.0f} tok/doc")
    print("=" * 60)
    for s in results:
        if "error" in s:
            print(f"  {s['backend']:12s}  ERRORE: {s['error']}")
        else:
            print(
                f"  {s['backend']:12s}  "
                f"build={s['build_s']:.1f}s  "
                f"ram={s['peak_mb']:.0f}MB  "
                f"disk={s['disk_mb']:.0f}MB  "
                f"q_avg={s['query_avg_ms']:.1f}ms  "
                f"q_max={s['query_max_ms']:.1f}ms"
            )
    print()

    # Valutazione automatica
    bm25s_r   = next((s for s in results if s["backend"] == "bm25s"    and "error" not in s), None)
    rank_bm25 = next((s for s in results if s["backend"] == "rank_bm25" and "error" not in s), None)

    if bm25s_r:
        ram_ok     = bm25s_r["peak_mb"] < 8192
        latency_ok = bm25s_r["query_avg_ms"] < 200
        esito = "A" if (ram_ok and latency_ok) else "B"
        print(f"  RAM < 8 GB:      {'✓' if ram_ok     else '✗'} ({bm25s_r['peak_mb']:.0f} MB)")
        print(f"  Latency < 200ms: {'✓' if latency_ok else '✗'} ({bm25s_r['query_avg_ms']:.1f} ms)")
    else:
        esito = "B"
        print("  bm25s non disponibile")

    print(f"\n  → ESITO {esito}")
    if esito == "A":
        print("     bm25s regge: migra _BM25Sub a bm25s (Fase 1 step 1.2)")
    else:
        print("     bm25s NON regge o fallito: mantieni rank_bm25,")
        print("     BM25 full-text solo su normattiva+dottrina (457k)")
    print("=" * 60)

    return esito


if __name__ == "__main__":
    main()
