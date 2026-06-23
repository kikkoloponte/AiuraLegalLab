"""
Test di regressione — race condition nel lazy-load sotto query concorrenti.

Bug reale osservato: 4 query reali lanciate in parallelo contro l'API hanno
causato 3 caricamenti duplicati di BM25 (~1.6M doc totali) e del grafo
giuridico (150MB), saturando la RAM e bloccando il server per 14+ minuti.
Causa: i guard di lazy-load ("if not loaded: load()") non erano protetti da
lock, quindi più thread (da asyncio.to_thread) o coroutine (cache orchestratore)
superavano il check prima che uno dei due completasse il caricamento.

Questi test forzano artificialmente la finestra di race (load lento) e
verificano che il caricamento avvenga esattamente una volta.
"""
from __future__ import annotations

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import pytest

from aiura_legal.core.retrieval.bm25_retriever import _BM25Sub
from aiura_legal.core.graph.retriever import _NetworkXBackend


# ---------------------------------------------------------------------------
# _BM25Sub.search() — lazy-load di doc_ids
# ---------------------------------------------------------------------------

class TestBM25SubConcurrency:

    def test_load_chiamato_una_sola_volta_sotto_concorrenza(self, tmp_path):
        sub = _BM25Sub(corpus="studio", ws=tmp_path)
        # Simula un pkl esistente (altrimenti search() non tenta nemmeno il load)
        (tmp_path / "indices").mkdir(parents=True, exist_ok=True)
        (tmp_path / "indices" / "bm25_studio.pkl").write_bytes(b"fake")

        call_count = {"n": 0}
        original_load = sub.load

        def _slow_load():
            call_count["n"] += 1
            time.sleep(0.2)  # allarga la finestra di race
            # Non chiama il load reale (pkl finto) — imposta solo lo stato
            # minimo che fa terminare _ensure_bm25s() senza eccezioni.
            sub.doc_ids = ["d1"]
            sub.tokenized = [["token"]]

        with patch.object(sub, "load", side_effect=_slow_load):
            with ThreadPoolExecutor(max_workers=8) as pool:
                futures = [pool.submit(sub.search, "query test") for _ in range(8)]
                for f in futures:
                    f.result()

        assert call_count["n"] == 1, f"load() chiamato {call_count['n']} volte, atteso 1"


# ---------------------------------------------------------------------------
# GraphRetriever (_NetworkXBackend) — lazy-load del grafo
# ---------------------------------------------------------------------------

class TestGraphRetrieverConcurrency:

    def test_load_graph_chiamato_una_sola_volta_sotto_concorrenza(self, tmp_path):
        import json
        import networkx as nx

        indices = tmp_path / "indices"
        indices.mkdir(parents=True, exist_ok=True)
        G = nx.DiGraph()
        G.add_node("urn:test:art1", node_type="article", fonte="legge", titolo="t", articolo_num="1")
        (indices / "graph.json").write_text(
            json.dumps(nx.node_link_data(G, edges="edges")), encoding="utf-8"
        )

        backend = _NetworkXBackend(str(tmp_path))
        call_count = {"n": 0}
        original_unlocked = backend._load_graph_unlocked

        def _slow_load_unlocked():
            call_count["n"] += 1
            time.sleep(0.2)
            return original_unlocked()

        with patch.object(backend, "_load_graph_unlocked", side_effect=_slow_load_unlocked):
            with ThreadPoolExecutor(max_workers=8) as pool:
                futures = [pool.submit(backend.expand, ["urn:test:art1"]) for _ in range(8)]
                for f in futures:
                    f.result()

        assert call_count["n"] == 1, f"_load_graph_unlocked chiamato {call_count['n']} volte, atteso 1"


# ---------------------------------------------------------------------------
# app._get_orchestrator() — cache per-workspace
# ---------------------------------------------------------------------------

class TestOrchestratorCacheConcurrency:

    @pytest.mark.asyncio
    async def test_hybrid_retriever_costruito_una_sola_volta(self):
        from aiura_legal.api import app as app_module

        # Isola lo stato globale per non inquinare altri test
        app_module._orchestrator_cache.clear()
        app_module._orchestrator_locks.clear()

        from unittest.mock import MagicMock

        call_count = {"n": 0}

        def _slow_constructor(*args, **kwargs):
            call_count["n"] += 1
            time.sleep(0.2)
            return MagicMock()

        with patch.object(app_module, "HybridRetriever", side_effect=_slow_constructor):
            results = await asyncio.gather(*[
                app_module._get_orchestrator("test-ws-concurrency") for _ in range(8)
            ])

        assert call_count["n"] == 1, f"HybridRetriever costruito {call_count['n']} volte, atteso 1"
        # Tutte le chiamate concorrenti devono ricevere la stessa istanza cached
        assert all(r is results[0] for r in results)

        app_module._orchestrator_cache.clear()
        app_module._orchestrator_locks.clear()
