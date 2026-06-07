"""
Test di retrieval giurisprudenziale end-to-end.

Verifica:
  1. MongoDB — conta documenti per organo
  2. BM25 + Vector — ricerca ibrida su query legali reali
  3. Citation Contract — grounding delle sentenze nei risultati
  4. Grafo — link sentenza → norma

Uso:
  python scripts/test_jurisprudence_retrieval.py --workspace mio-studio
  python scripts/test_jurisprudence_retrieval.py --workspace mio-studio --verbose
"""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever
from aiura_legal.core.reviewer.reviewer import CitationReviewer
from aiura_legal.core.types import QueryIntent, ResearchPacket, SearchResult
from aiura_legal.ingestion.mongodb.client import MongoClient
from aiura_legal.jurisprudence.graph_builder import JurisprudenceGraphBuilder

_WORKSPACES_BASE = Path("C:/project/AiUraLegalLab/workspaces")
_GRAPH_PATH = Path("C:/project/AiUraLegalLab/workspaces/jurisprudence_graph.json")

# Query di test — copre diversi intent giurisprudenziali
_TEST_QUERIES = [
    {
        "query": "responsabilità extracontrattuale nesso causale danno",
        "intent": QueryIntent.GIURISPRUDENZA_SEARCH,
        "desc": "Ricerca giurisprudenza su responsabilità civile",
    },
    {
        "query": "illegittimità provvedimento amministrativo eccesso di potere TAR",
        "intent": QueryIntent.GIURISPRUDENZA_SEARCH,
        "desc": "Ricerca sentenze TAR su vizi provvedimento",
    },
    {
        "query": "danno erariale responsabilità contabile Corte dei Conti",
        "intent": QueryIntent.GIURISPRUDENZA_SEARCH,
        "desc": "Ricerca giurisprudenza Corte dei Conti",
    },
    {
        "query": "art. 2043 codice civile responsabilità aquiliana",
        "intent": QueryIntent.NORMA_LOOKUP,
        "desc": "Lookup norma + giurisprudenza correlata",
    },
    {
        "query": "appalti pubblici bando gara illegittimo",
        "intent": QueryIntent.FATTISPECIE_ANALYSIS,
        "desc": "Analisi fattispecie appalti",
    },
]


def _separator(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


async def check_mongodb() -> dict:
    """Conta i documenti in MongoDB per organo."""
    _separator("1. MongoDB — conteggio documenti")
    mongo = MongoClient.get()
    collection = mongo.db["jurisprudence"]

    totale = await collection.count_documents({})
    print(f"\nTotale documenti in jurisprudence: {totale:,}")

    per_organo = {}
    for organo in ["cassazione", "tar", "consiglio_stato", "corte_cost", "corte_conti"]:
        count = await collection.count_documents({"organo": organo})
        if count > 0:
            per_organo[organo] = count
            print(f"  {organo:20s}: {count:,}")

    # Mostra esempio
    sample = await collection.find_one({}, sort=[("ingested_at", -1)])
    if sample:
        print(f"\nUltimo inserito: {sample.get('organo')} n.{sample.get('numero')}/{sample.get('anno')}")
        print(f"  massima ({len(sample.get('massima',''))} chars): {sample.get('massima','')[:120]}...")

    return {"totale": totale, "per_organo": per_organo}


def check_indexes(workspace: str) -> dict:
    """Verifica che gli indici esistano e abbiano documenti."""
    _separator("2. Indici BM25 + Vector")
    ws_path = _WORKSPACES_BASE / workspace

    bm25_pkl = ws_path / "indices" / "bm25.pkl"
    chroma_dir = ws_path / "indices" / "chromadb"

    bm25_ok = bm25_pkl.exists()
    vector_ok = chroma_dir.exists()

    print(f"\nWorkspace: {ws_path}")
    print(f"  BM25:   {'✓ OK' if bm25_ok else '✗ MANCANTE'} ({bm25_pkl})")
    print(f"  Vector: {'✓ OK' if vector_ok else '✗ MANCANTE'} ({chroma_dir})")

    if not bm25_ok or not vector_ok:
        print("\n  ⚠ Indici mancanti. Esegui:")
        print(f"    python scripts/build_jurisprudence_indexes.py --workspace {workspace}")

    return {"bm25_ok": bm25_ok, "vector_ok": vector_ok}


def run_retrieval_queries(workspace: str, verbose: bool = False) -> list[dict]:
    """Esegue le query di test e mostra i risultati."""
    _separator("3. Retrieval — query di test")

    ws_path = str(_WORKSPACES_BASE / workspace)
    try:
        retriever = HybridRetriever(ws_path)
    except Exception as exc:
        print(f"\n  ✗ Impossibile caricare HybridRetriever: {exc}")
        return []

    results_summary = []

    for test in _TEST_QUERIES:
        query = test["query"]
        intent = test["intent"]
        desc = test["desc"]

        print(f"\n{'─'*55}")
        print(f"  [{intent.value}]")
        print(f"  Query: {query}")
        print(f"  {desc}")

        try:
            results = retriever.search(
                query=query,
                intent=intent,
                top_k_retrieve=15,
                top_k_rerank=5,
            )
        except Exception as exc:
            print(f"  ✗ Errore retrieval: {exc}")
            results_summary.append({"query": query, "error": str(exc)})
            continue

        jur_results = [r for r in results if r.metadata.get("chunk_type") in ("massima", "motivazione", "dispositivo")]
        norm_results = [r for r in results if r.metadata.get("chunk_type") not in ("massima", "motivazione", "dispositivo")]

        print(f"\n  Risultati totali: {len(results)}  (giurisp: {len(jur_results)}  norme: {len(norm_results)})")

        for i, r in enumerate(results[:3], 1):
            chunk_type = r.metadata.get("chunk_type", "norma")
            organo = r.metadata.get("organo", "")
            jdoc_id = r.metadata.get("jdoc_id", "")
            label = f"{organo} [{chunk_type}]" if organo else chunk_type
            print(f"\n  [{i}] score={r.score:.3f}  {label}")
            if verbose:
                print(f"      doc_id: {r.doc_id}")
                print(f"      source: {r.source_id}")
            print(f"      {r.snippet[:150]}...")

        results_summary.append({
            "query": query,
            "total": len(results),
            "jurisprudence": len(jur_results),
            "norme": len(norm_results),
        })

    return results_summary


def check_citation_contract(workspace: str) -> None:
    """Verifica che il Reviewer blocchi citazioni non grounded."""
    _separator("4. Citation Contract — test grounding")

    ws_path = str(_WORKSPACES_BASE / workspace)
    try:
        retriever = HybridRetriever(ws_path)
        results = retriever.search(
            "responsabilità civile danno ingiusto",
            intent=QueryIntent.GIURISPRUDENZA_SEARCH,
            top_k_retrieve=10,
            top_k_rerank=5,
        )
    except Exception as exc:
        print(f"\n  ✗ Retrieval fallito: {exc}")
        return

    # Costruisce ResearchPacket dai risultati
    packet = ResearchPacket(
        query_original="responsabilità civile danno ingiusto",
        query_intent=QueryIntent.GIURISPRUDENZA_SEARCH,
        sources=results,
    )

    reviewer = CitationReviewer()

    # Test A: draft con citazione grounded
    grounded_ids = [r.doc_id for r in results[:2]]
    draft_ok = f"Come risulta dalla sentenza {grounded_ids[0]} il nesso causale è essenziale."
    result_ok = reviewer.verify(draft_ok, packet)
    print(f"\n  Test A (citazione grounded):")
    print(f"    Draft: ...sentenza {grounded_ids[0][:8]}...")
    print(f"    Verdict: {result_ok.verdict}  Action: {result_ok.action}  {'✓ OK' if result_ok.verdict == 'PASS' else '✗ FAIL'}")

    # Test B: draft con ID inventato
    draft_fail = "Come da sentenza abcdef1234567890 il danno è provato."
    result_fail = reviewer.verify(draft_fail, packet)
    print(f"\n  Test B (citazione NON grounded):")
    print(f"    Draft: ...sentenza abcdef1234567890...")
    print(f"    Verdict: {result_fail.verdict}  Action: {result_fail.action}  {'✓ OK' if result_fail.verdict == 'FAIL' else '✗ FAIL'}")

    ok_a = result_ok.verdict == "PASS"
    ok_b = result_fail.verdict == "FAIL"
    print(f"\n  Risultato: {'✓ Citation Contract funzionante' if ok_a and ok_b else '✗ Problemi rilevati'}")


def check_graph() -> None:
    """Verifica il grafo sentenza → norma."""
    _separator("5. Grafo — link sentenza → norma")

    if not _GRAPH_PATH.exists():
        print(f"\n  ✗ Grafo non trovato: {_GRAPH_PATH}")
        print("  Verrà costruito al prossimo sync.")
        return

    try:
        builder = JurisprudenceGraphBuilder(_GRAPH_PATH)
        g = builder.graph
        sentenze = [n for n, d in g.nodes(data=True) if d.get("type") == "sentenza"]
        norme = [n for n, d in g.nodes(data=True) if d.get("type") == "norma"]
        edges = g.number_of_edges()

        print(f"\n  Nodi sentenza: {len(sentenze):,}")
        print(f"  Nodi norma:    {len(norme):,}")
        print(f"  Archi totali:  {edges:,}")

        # Mostra norma più citata
        from collections import Counter
        norme_citazioni = Counter(
            nbr for s in sentenze
            for nbr in g.successors(s)
            if g.nodes[nbr].get("type") == "norma"
        )
        if norme_citazioni:
            top = norme_citazioni.most_common(3)
            print("\n  Norme più citate:")
            for urn, count in top:
                print(f"    {urn[:60]}  ({count} sentenze)")
    except Exception as exc:
        print(f"\n  ✗ Errore lettura grafo: {exc}")


async def main(workspace: str, verbose: bool) -> None:
    print(f"\nTest retrieval giurisprudenziale — workspace: {workspace}")

    mongo_stats = await check_mongodb()

    if mongo_stats["totale"] == 0:
        print("\n✗ Nessun documento in MongoDB. Esegui prima:")
        print("  python scripts/sync_jurisprudence.py --initial-load")
        return

    idx_stats = check_indexes(workspace)

    if idx_stats["bm25_ok"] and idx_stats["vector_ok"]:
        run_retrieval_queries(workspace, verbose=verbose)
        check_citation_contract(workspace)
    else:
        print("\n⚠ Retrieval saltato — indici mancanti.")
        print(f"  python scripts/build_jurisprudence_indexes.py --workspace {workspace}")

    check_graph()

    print(f"\n{'='*60}")
    print(f"  Test completato.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test retrieval giurisprudenziale")
    parser.add_argument("--workspace", default="mio-studio", help="Nome workspace")
    parser.add_argument("--verbose", action="store_true", help="Mostra doc_id e source")
    args = parser.parse_args()
    asyncio.run(main(args.workspace, args.verbose))
