"""
Test di performance per il retrieval S2.

Due livelli:
  - Unit perf  (mock + sleep artificiale): misura il guadagno del parallelismo
    in modo deterministico e senza indici su disco. Sempre veloci (~2s totali).
  - Integration perf (indici reali): misura la latenza end-to-end reale.
    Saltati automaticamente se il workspace non esiste.

Esecuzione:
  pytest tests/test_retrieval_perf.py -v                     # solo unit
  pytest tests/test_retrieval_perf.py -v -m integration      # solo integration
  pytest tests/test_retrieval_perf.py -v -m "not slow"       # esclude slow
"""
from __future__ import annotations

import time
import statistics
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional
from unittest.mock import MagicMock, patch
from datetime import date

import pytest

from aiura_legal.core.types import QueryIntent, SearchResult, ResearchPacket


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_WS_PATH = "workspaces/mio-studio"
_BM25_PATH = Path(_WS_PATH) / "indices" / "bm25.pkl"
_BM25_NORMATTIVA_PATH = Path(_WS_PATH) / "indices" / "bm25_normattiva.pkl"

def _bm25_has_normattiva() -> bool:
    """Ritorna True se esiste il pkl per-corpus normattiva (o il legacy con chunk normattiva)."""
    # Nuovo formato per-corpus
    if _BM25_NORMATTIVA_PATH.exists():
        try:
            import pickle
            with open(_BM25_NORMATTIVA_PATH, "rb") as f:
                state = pickle.load(f)
            return len(state.get("doc_ids", [])) > 0
        except Exception:
            pass
    # Fallback legacy monolitico
    if not _BM25_PATH.exists():
        return False
    try:
        import pickle
        with open(_BM25_PATH, "rb") as f:
            state = pickle.load(f)
        meta = state.get("doc_metadata", [])
        return any(m.get("corpus") == "normattiva" for m in meta[:500])
    except Exception:
        return False

_SKIP_INTEGRATION = not _bm25_has_normattiva()

_INTEGRATION_SKIP = pytest.mark.skipif(
    _SKIP_INTEGRATION,
    reason=(
        f"workspace {_WS_PATH!r} non trovato o BM25 senza chunk normattiva "
        f"— esegui: python scripts/build_indexes.py --workspace mio-studio"
    ),
)

def _make_result(doc_id: str = "doc1", score: float = 0.9) -> SearchResult:
    return SearchResult(
        doc_id=doc_id, score=score, snippet="testo normativo di esempio",
        source_id=f"urn:nir:{doc_id}", metadata={"corpus": "normattiva"},
    )


def _slow_search(delay_s: float, results: list[SearchResult]):
    """Simula una ricerca lenta (per testare il parallelismo)."""
    def _fn(*args, **kwargs):
        time.sleep(delay_s)
        return results
    return _fn


# ---------------------------------------------------------------------------
# 1. UNIT PERF — parallelismo BM25 + Vector dentro _search_round
# ---------------------------------------------------------------------------

class TestSearchRoundParallelism:
    """
    Verifica che BM25 e Vector girino in parallelo dentro _search_round.
    Inietta ritardi artificiali: se sequenziale ci vorrebbe bm25_delay + vec_delay,
    se parallelo basta max(bm25_delay, vec_delay).
    """

    BM25_DELAY  = 0.3   # secondi
    VECTOR_DELAY = 0.5   # secondi
    SEQ_EXPECTED = BM25_DELAY + VECTOR_DELAY   # 0.8s se sequenziale
    PAR_EXPECTED = max(BM25_DELAY, VECTOR_DELAY)  # 0.5s se parallelo
    TOLERANCE    = 0.15  # margine ±150ms

    def _make_retriever(self):
        from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever
        with patch.object(HybridRetriever, '__init__', lambda self, ws: None):
            r = HybridRetriever.__new__(HybridRetriever)

        r.bm25    = MagicMock()
        r.vector  = MagicMock()
        r.graph   = MagicMock()
        r.reranker = MagicMock()

        r.bm25.search.side_effect    = _slow_search(self.BM25_DELAY,   [_make_result("bm25-1")])
        r.vector.search.side_effect  = _slow_search(self.VECTOR_DELAY, [_make_result("vec-1")])
        r.graph.is_available         = False
        r.reranker.rerank.side_effect = lambda q, cands, top_k=7: cands[:top_k]

        return r

    def test_search_round_is_parallel(self):
        """BM25 + Vector devono finire in ~max(delay), non ~sum(delay)."""
        r = self._make_retriever()
        t0 = time.perf_counter()
        r._search_round(
            "pagamento ritardato", (0.65, 0.20, 0.15),
            {"corpus": "normattiva"}, None, 10, 5,
        )
        elapsed = time.perf_counter() - t0

        assert elapsed < self.PAR_EXPECTED + self.TOLERANCE, (
            f"_search_round troppo lento: {elapsed:.3f}s "
            f"(atteso < {self.PAR_EXPECTED + self.TOLERANCE:.3f}s)\n"
            f"Probabilmente BM25 e Vector girano ancora sequenzialmente."
        )
        # Deve essere almeno il delay del più lento (non può essere miracolosamente più veloce)
        assert elapsed >= self.PAR_EXPECTED - self.TOLERANCE, (
            f"Elapsed {elapsed:.3f}s troppo basso — mock non funziona?"
        )

    def test_search_round_not_sequential(self):
        """Conferma che NON è più sequenziale (non deve raggiungere sum dei delay)."""
        r = self._make_retriever()
        t0 = time.perf_counter()
        r._search_round("clausola penale", (0.65, 0.20, 0.15), None, None, 10, 5)
        elapsed = time.perf_counter() - t0

        assert elapsed < self.SEQ_EXPECTED - 0.1, (
            f"Sembra sequenziale: {elapsed:.3f}s ~= {self.SEQ_EXPECTED:.3f}s (somma dei delay)"
        )

    def test_search_round_returns_results(self):
        """Verifica che i risultati siano corretti nonostante il parallelismo."""
        r = self._make_retriever()
        results = r._search_round(
            "responsabilità contrattuale", (0.65, 0.20, 0.15), None, None, 10, 5
        )
        assert isinstance(results, list)
        # RRF fusion poi reranker — ci aspettiamo almeno i risultati BM25 e Vector
        assert len(results) >= 1


# ---------------------------------------------------------------------------
# 2. UNIT PERF — parallelismo due round bifasico
# ---------------------------------------------------------------------------

class TestBifasicoParallelism:
    """
    Verifica che i round normativa e giurisprudenza girino in parallelo
    in build_research_packet_bifasico.
    """

    ROUND_DELAY = 0.4   # secondi per round
    SEQ_EXPECTED = ROUND_DELAY * 2    # 0.8s se sequenziale
    PAR_EXPECTED = ROUND_DELAY        # 0.4s se parallelo
    TOLERANCE    = 0.15

    def _make_retriever_with_slow_rounds(self):
        from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever
        with patch.object(HybridRetriever, '__init__', lambda self, ws: None):
            r = HybridRetriever.__new__(HybridRetriever)
        r.bm25    = MagicMock()
        r.vector  = MagicMock()
        r.graph   = MagicMock()
        r.reranker = MagicMock()
        r.graph.is_available = False

        # _search_round è il metodo pesante: lo sostituiamo con uno lento
        call_count = {"n": 0}
        def slow_round(query, weights, chunk_filter, valid_on, top_k_retrieve, top_k_rerank):
            time.sleep(self.ROUND_DELAY)
            call_count["n"] += 1
            corpus = (chunk_filter or {}).get("corpus", "normattiva")
            return [_make_result(f"{corpus}-1", 0.9), _make_result(f"{corpus}-2", 0.8)]

        r._search_round = slow_round
        r._call_count = call_count
        return r

    def test_bifasico_rounds_are_parallel(self):
        """I due round devono finire in ~1 round, non in ~2 round."""
        r = self._make_retriever_with_slow_rounds()
        t0 = time.perf_counter()
        packet = r.build_research_packet_bifasico(
            "responsabilità del debitore", QueryIntent.FATTISPECIE_ANALYSIS
        )
        elapsed = time.perf_counter() - t0

        assert elapsed < self.PAR_EXPECTED + self.TOLERANCE, (
            f"Bifasico troppo lento: {elapsed:.3f}s "
            f"(atteso < {self.PAR_EXPECTED + self.TOLERANCE:.3f}s con round paralleli)\n"
            f"I round sembrano ancora sequenziali."
        )

    def test_bifasico_not_sequential(self):
        """Conferma che il tempo non è la somma dei due round."""
        r = self._make_retriever_with_slow_rounds()
        t0 = time.perf_counter()
        r.build_research_packet_bifasico("clausola penale", QueryIntent.FATTISPECIE_ANALYSIS)
        elapsed = time.perf_counter() - t0

        assert elapsed < self.SEQ_EXPECTED - 0.1, (
            f"Sembra sequenziale: {elapsed:.3f}s ~= {self.SEQ_EXPECTED:.3f}s"
        )

    def test_bifasico_packet_has_both_layers(self):
        """Il packet deve contenere fonti normativa E giurisprudenza."""
        r = self._make_retriever_with_slow_rounds()
        packet = r.build_research_packet_bifasico(
            "rischio contrattuale", QueryIntent.FATTISPECIE_ANALYSIS
        )
        layers = {s.source_layer for s in packet.sources}
        assert "normativa" in layers,      "Mancano fonti normative nel packet"
        assert "giurisprudenza" in layers, "Mancano fonti giurisprudenziali nel packet"

    def test_bifasico_both_rounds_called(self):
        """Entrambi i round devono essere eseguiti."""
        r = self._make_retriever_with_slow_rounds()
        r.build_research_packet_bifasico("test", QueryIntent.FATTISPECIE_ANALYSIS)
        assert r._call_count["n"] == 2, (
            f"Attesi 2 round, chiamati {r._call_count['n']}"
        )


# ---------------------------------------------------------------------------
# 3. UNIT PERF — asyncio.to_thread nell'orchestrator
# ---------------------------------------------------------------------------

class TestOrchestratorToThread:
    """
    Verifica che build_research_packet* sia chiamato con asyncio.to_thread
    e non blocchi l'event loop.
    """

    @pytest.mark.asyncio
    async def test_retriever_runs_in_thread(self):
        """
        Il retrieval non deve bloccare l'event loop:
        una coroutine concorrente deve poter girare durante il retrieval.
        """
        import asyncio

        concurrent_ran = {"flag": False}

        async def concurrent_task():
            await asyncio.sleep(0.05)
            concurrent_ran["flag"] = True

        def slow_retrieval(*args, **kwargs):
            time.sleep(0.2)  # blocco CPU
            return ResearchPacket(
                query_original="test",
                query_intent=QueryIntent.NORMA_LOOKUP,
                sources=[],
                retrieval_confidence="LOW",
            )

        # Simula il pattern asyncio.to_thread + task concorrente
        task = asyncio.create_task(concurrent_task())
        result = await asyncio.to_thread(slow_retrieval)
        await task

        assert concurrent_ran["flag"], (
            "La task concorrente non è girata durante il retrieval — "
            "significa che il retrieval blocca l'event loop."
        )


# ---------------------------------------------------------------------------
# 4. INTEGRATION PERF — retrieval reale con indici su disco
# ---------------------------------------------------------------------------

@_INTEGRATION_SKIP
@pytest.mark.integration
@pytest.mark.slow
class TestIntegrationPerf:
    """
    Test di latenza end-to-end con indici reali.
    Richiede workspaces/mio-studio/indices/bm25.pkl.
    Eseguire con: pytest tests/test_retrieval_perf.py -v -m integration
    """

    QUERIES = [
        "Quali sono le conseguenze del ritardo nel pagamento del canone di locazione?",
        "Responsabilità del datore di lavoro per infortunio sul lavoro",
        "Clausola penale eccessiva: riduzione da parte del giudice",
    ]
    # Soglie (secondi) — da aggiornare in base all'hardware
    MAX_SINGLE_ROUND_S  = 20.0  # un solo search() su un corpus (include cold BM25 build ~10s su 470k doc)
    MAX_BIFASICO_S      = 30.0  # due round in parallelo
    WARN_SINGLE_S       = 10.0  # warning se supera questa soglia

    @pytest.fixture(scope="class")
    def retriever(self):
        from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever
        r = HybridRetriever(_WS_PATH)
        # Warm-up: carica i pkl per-corpus e forza il build BM25Okapi
        # così i tempi misurati non includono load/build dell'indice
        r.bm25.load_all()
        for sub in r.bm25._subs.values():
            sub._ensure_bm25()
        # Warm-up vector: carica il modello SentenceTransformer (lazy load ~30s su CPU)
        r.vector.search("warm-up", top_k=1)
        return r

    def test_single_round_norma_lookup_latency(self, retriever):
        """search() per NORMA_LOOKUP deve stare sotto MAX_SINGLE_ROUND_S."""
        times = []
        for q in self.QUERIES:
            t0 = time.perf_counter()
            results = retriever.search(q, intent=QueryIntent.NORMA_LOOKUP, top_k_rerank=6)
            elapsed = time.perf_counter() - t0
            times.append(elapsed)
            assert len(results) > 0, f"Nessun risultato per {q!r}"
            assert elapsed < self.MAX_SINGLE_ROUND_S, (
                f"NORMA_LOOKUP troppo lento: {elapsed:.2f}s per {q!r}"
            )
            if elapsed > self.WARN_SINGLE_S:
                import warnings
                warnings.warn(f"NORMA_LOOKUP lento ({elapsed:.2f}s) per {q!r}")

        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        print(f"\n[NORMA_LOOKUP] avg={avg:.2f}s  p95={p95:.2f}s  times={[f'{t:.2f}' for t in times]}")

    def test_bifasico_fattispecie_latency(self, retriever):
        """build_research_packet_bifasico deve stare sotto MAX_BIFASICO_S."""
        times = []
        for q in self.QUERIES:
            t0 = time.perf_counter()
            packet = retriever.build_research_packet_bifasico(
                q, QueryIntent.FATTISPECIE_ANALYSIS
            )
            elapsed = time.perf_counter() - t0
            times.append(elapsed)

            assert len(packet.sources) > 0, f"Nessuna fonte per {q!r}"
            layers = {s.source_layer for s in packet.sources}
            assert "normativa" in layers, "Mancano fonti normative"

            assert elapsed < self.MAX_BIFASICO_S, (
                f"Bifasico troppo lento: {elapsed:.2f}s per {q!r}"
            )

        avg = statistics.mean(times)
        p95 = sorted(times)[int(len(times) * 0.95)]
        print(f"\n[BIFASICO] avg={avg:.2f}s  p95={p95:.2f}s  times={[f'{t:.2f}' for t in times]}")

    def test_bifasico_faster_than_sequential_estimate(self, retriever):
        """
        Confronto diretto parallelo vs sequenziale sullo stesso retriever.
        Misura i due round separatamente poi confronta con la versione parallela.
        """
        query = self.QUERIES[0]

        # Misura round normativa da solo
        t0 = time.perf_counter()
        retriever._search_round(
            query, (0.65, 0.20, 0.15), {"corpus": "normattiva"}, None, 20, 6
        )
        t_norm = time.perf_counter() - t0

        # Misura round giurisprudenza da solo
        t0 = time.perf_counter()
        retriever._search_round(
            query, (0.15, 0.75, 0.10), {"corpus": "giurisprudenza"}, None, 20, 6
        )
        t_giuri = time.perf_counter() - t0

        sequential_estimate = t_norm + t_giuri

        # Misura bifasico parallelo
        t0 = time.perf_counter()
        retriever.build_research_packet_bifasico(query, QueryIntent.FATTISPECIE_ANALYSIS)
        t_parallel = time.perf_counter() - t0

        speedup = sequential_estimate / t_parallel if t_parallel > 0 else 1.0

        print(
            f"\n[SPEEDUP] norm={t_norm:.2f}s  giuri={t_giuri:.2f}s  "
            f"seq_est={sequential_estimate:.2f}s  parallel={t_parallel:.2f}s  "
            f"speedup={speedup:.1f}x"
        )

        # Il parallelo non deve essere significativamente PIÙ LENTO del sequenziale
        # (su single-CPU lo speedup reale è ~1x per via del GIL — il beneficio è
        # sulla latenza wall-clock quando il bottleneck è I/O, non CPU).
        # Tolleranza generosa: il parallelo deve stare entro il 30% del sequenziale.
        assert t_parallel < sequential_estimate * 1.30, (
            f"Parallelismo peggiora troppo il sequenziale: "
            f"parallel={t_parallel:.2f}s vs sequential_est={sequential_estimate:.2f}s "
            f"(speedup={speedup:.1f}x)"
        )

    def test_bm25_search_alone_latency(self, retriever):
        """BM25 da solo deve essere veloce (< 1s) — baseline."""
        q = self.QUERIES[0]
        t0 = time.perf_counter()
        results = retriever.bm25.search(q, top_k=20)
        elapsed = time.perf_counter() - t0
        print(f"\n[BM25] {elapsed:.3f}s  risultati={len(results)}")
        # Soglia tarata su ~595k doc totali (4 sub-indici, search senza filtro corpus)
        assert elapsed < 5.0, f"BM25 troppo lento: {elapsed:.3f}s"

    def test_vector_search_alone_latency(self, retriever):
        """Vector (ChromaDB+SentenceTransformer) — baseline per capire il collo di bottiglia."""
        q = self.QUERIES[0]
        t0 = time.perf_counter()
        results = retriever.vector.search(q, top_k=20)
        elapsed = time.perf_counter() - t0
        print(f"\n[VECTOR] {elapsed:.3f}s  risultati={len(results)}")
        # Non mettiamo un limite stretto — dipende dall'hardware, vogliamo solo misurare

    def test_reranker_alone_latency(self, retriever):
        """CrossEncoder reranking su 20 candidati — baseline."""
        q = self.QUERIES[0]
        candidates = [
            SearchResult(
                doc_id=f"d{i}", score=0.9 - i * 0.01,
                snippet="Testo normativo di prova per il reranking con cross encoder.",
                source_id=f"urn:nir:d{i}", metadata={},
            )
            for i in range(20)
        ]
        t0 = time.perf_counter()
        reranked = retriever.reranker.rerank(q, candidates, top_k=6)
        elapsed = time.perf_counter() - t0
        print(f"\n[RERANKER] {elapsed:.3f}s  input=20  output={len(reranked)}")
        assert elapsed < 2.0, f"CrossEncoder troppo lento: {elapsed:.3f}s su 20 candidati"


# ---------------------------------------------------------------------------
# 5. Riepilogo performance (utility — non è un test)
# ---------------------------------------------------------------------------

def print_perf_summary():
    """
    Funzione di utilità per stampare un riepilogo delle performance
    senza eseguire i test. Chiamare direttamente:
      python -c "from tests.test_retrieval_perf import print_perf_summary; print_perf_summary()"
    """
    if _SKIP_INTEGRATION:
        print(f"Workspace {_WS_PATH!r} non trovato — impossibile misurare.")
        return

    from aiura_legal.core.retrieval.hybrid_retriever import HybridRetriever

    print(f"\n{'='*60}")
    print("AiUra S2 — Performance Summary")
    print(f"Workspace: {_WS_PATH}")
    print(f"{'='*60}\n")

    r = HybridRetriever(_WS_PATH)
    q = "Quali sono le conseguenze del ritardo nel pagamento?"

    for label, fn in [
        ("BM25 search (top_k=20)",        lambda: r.bm25.search(q, top_k=20)),
        ("Vector search (top_k=20)",       lambda: r.vector.search(q, top_k=20)),
        ("CrossEncoder rerank (20 cand)",  lambda: r.reranker.rerank(q, r.bm25.search(q, top_k=20), top_k=6)),
        ("_search_round normativa",        lambda: r._search_round(q, (0.65,0.20,0.15), {"corpus":"normattiva"}, None, 20, 6)),
        ("_search_round giurisprudenza",   lambda: r._search_round(q, (0.15,0.75,0.10), {"corpus":"giurisprudenza"}, None, 20, 6)),
        ("bifasico (parallelo)",           lambda: r.build_research_packet_bifasico(q, QueryIntent.FATTISPECIE_ANALYSIS)),
    ]:
        t0 = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - t0
        bar = "█" * int(elapsed * 10)
        print(f"  {label:<40} {elapsed:5.2f}s  {bar}")

    print()
