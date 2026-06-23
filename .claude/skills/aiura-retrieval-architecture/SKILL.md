---
name: aiura-retrieval-architecture
description: Knowledge of AiUraLegalLab's workspace/retrieval architecture — which workspace is canonical (mio-studio), how BM25 + Qdrant v1/v2 indices relate to MongoDB chunks, and known pitfalls discovered while debugging the Fase 2 gate eval (stale per-domain workspaces, workspace filter not propagated to vector search, LM Studio prompt-cache slowdown). Use this skill whenever working on retrieval recall/groundedness issues, rebuilding BM25/Qdrant indices, running the eval suite (eval/run_eval.py, fase*_gate*), debugging "Hybrid BM25=0" log lines, mirroring normattiva data, or any time a query/workspace mismatch is suspected — even if the user just says "recall is low" or "the eval numbers don't make sense" without naming workspaces explicitly.
---

# AiUraLegalLab — Retrieval & Workspace Architecture

This captures hard-won knowledge from debugging the Fase 2 gate eval (2026-06-15/16):
why `trib` recall barely moved after adding missing fiscal-law corpus, and why eval
latency/groundedness numbers looked inconsistent across domains.

## The one rule that matters: `mio-studio` is the canonical workspace

All real indexing work — `build_indexes.py`, `mirror_normattiva.py`,
`reindex_v2.py` — defaults to and is documented (CLAUDE.md) against workspace
**`mio-studio`**. Other workspace directories under `workspaces/` (`normattiva`,
`normattiva_amministrativo`, `normattiva_civile`, `normattiva_cross`,
`normattiva_penale`) are **leftovers from an earlier per-domain design that was
never fully built** (their `indices/` dirs contain only a stale `chromadb/` stub
or `.v1.bak` backups, no live BM25 pkl). If you find a query JSONL or config
pointing at one of these, it is very likely stale — verify before assuming it's
intentional isolation.

Before trusting any eval result, check what workspace the query files actually
declare:
```bash
grep -o '"workspace":"[^"]*"' tests/script_json/queries_*.jsonl | sort -u
```
If it's not `mio-studio`, that domain's BM25 contribution is probably zero
(see next section) even if the test reports nonzero recall — because vector
search still hits the global Qdrant collection.

## Two independent retrieval backends — they don't fail the same way

| Backend | Storage | Scoped by workspace? |
|---|---|---|
| BM25 | per-workspace `.pkl` files in `workspaces/<ws>/indices/bm25_<corpus>.pkl` | Yes — strictly. Missing/empty pkl → 0 contribution, silently. |
| Qdrant (v1 `legal_docs`, v2 `legal_docs_v2`) | single shared **server** collection (`http://localhost:6333`) regardless of which workspace's `VectorRetriever` instantiated it | Only if a `workspace` filter is actually passed into `HybridRetriever.search()`. |

**Known gap (still present as of 2026-06-16):** `LegalOrchestrator.run()` calls
`build_research_packet_bifasico(query=..., intent=..., valid_on=..., chunk_filter=...)`
**without** a `workspace=` argument (`aiura_legal/agents/orchestrator.py` ~line
237). That means vector search is effectively **unfiltered by workspace** at
that call site — it searches the entire shared Qdrant collection no matter which
workspace's orchestrator instance is running. Meanwhile BM25 for that same
request only sees whatever's in the requested workspace's own pkl files.

Net effect: if you see `Hybrid [intent]: BM25=0, Vector=20, Graph=0` in the API
log, it almost always means *"this workspace has no BM25 corpus, but vector
search just searched everything in Qdrant anyway."* Don't read this as "the
corpus is fine" — it means you're running **vector-only**, missing the
BM25-heavy weighting the design calls for in Fase 2 (CLAUDE.md: 0.65 BM25 /
0.20 vector / 0.15 graph for `corpus=normattiva`).

If you need real per-workspace isolation restored, the fix belongs in
`orchestrator.py`'s call to `build_research_packet_bifasico` (thread `workspace`
through) — don't just patch around it in eval files unless you've confirmed
isolation isn't actually wanted.

## Qdrant v1 vs v2 — check before assuming "the index" means one or the other

- `legal_docs` (v1): 384d, MiniLM, **2.69M points**, accumulated over many build
  runs across workspaces — content provenance is murky, treat as legacy/staging.
- `legal_docs_v2` (v2): 768d, `intfloat/multilingual-e5-base`, built explicitly
  by `reindex_v2.py`. This is what `VectorRetrieverV2` uses when
  `USE_VECTOR_V2=1` in `.env` — which is the production path. **When debugging
  retrieval, always check v2, not v1.**

Quick health check:
```python
from qdrant_client import QdrantClient
c = QdrantClient(url='http://localhost:6333')
for name in ['legal_docs', 'legal_docs_v2']:
    print(name, c.get_collection(name).points_count)
```

To see what's actually inside v2 by workspace/corpus (payload indexes on
`workspace`, `corpus`, `source_id`, `valid_from_int`, `valid_to_int` already
exist — filtered queries are fast, no need to scroll the whole collection):
```python
from qdrant_client.models import Filter, FieldCondition, MatchValue
c.count('legal_docs_v2', count_filter=Filter(must=[
    FieldCondition(key='workspace', match=MatchValue(value='mio-studio')),
    FieldCondition(key='corpus', match=MatchValue(value='normattiva')),
]))
```

## MongoDB chunks: always check workspace × corpus distribution first

`aiura_legal_lab_db.chunks` is the single source both BM25 and Qdrant v2 get
rebuilt from. Before debugging *why* retrieval is missing something, check
where the chunks actually live — workspace mismatches (e.g. a mirror run
without `--workspace mio-studio` defaults to workspace=`"normattiva"`, a
different bucket entirely) are the most common silent failure mode:
```python
from pymongo import MongoClient
db = MongoClient('mongodb://localhost:27017')['aiura_legal_lab_db']
for r in db.chunks.aggregate([
    {'$group': {'_id': {'ws': {'$ifNull': ['$workspace','__NULL__']},
                         'corp': {'$ifNull': ['$corpus','__NULL__']}}},
                'n': {'$sum': 1}}},
    {'$sort': {'n': -1}},
]):
    print(r)
```
`mirror_normattiva.py --workspace` defaults to `"normattiva"`, **not**
`"mio-studio"` — always pass `--workspace mio-studio` explicitly or you'll
silently create a second, disconnected copy of the corpus.

## Pipeline for adding new normattiva content to the live index

1. Ingest into `legal_lab.normattiva_docs` (LegalAgentLab side — read-only for
   us, but its own ingest scripts write there; the public REST API at
   `api.normattiva.it/.../atto/dettaglio-atto-urn` returns HTTP 400 for DPR-type
   acts specifically — DPR texts (TUIR, IVA, DPR 600/602, etc.) must go through
   `NormattivaWebFetcher` web-AJAX scraping instead, using `codiceRedazionale` +
   `dataGU` looked up via `/ricerca/avanzata`).
2. `python scripts/mirror_normattiva.py --workspace mio-studio [--filter-urn ...]`
   — copies + chunks into `aiura_legal.chunks`. Note: `--filter-urn` only
   filters the *mirror* step; the chunking step re-chunks **everything**
   currently in `aiura_legal.normattiva_docs` for that workspace (it's not
   incremental per-URN), so this is slower than it looks but harmless/idempotent
   (upsert by URN).
3. `python scripts/build_indexes.py --workspace mio-studio --corpus normattiva --skip-vector`
   — rebuilds BM25 only (fast, seconds-to-minutes per 100k+ docs).
4. `python scripts/reindex_v2.py --workspace mio-studio --corpus normattiva`
   — embeds into Qdrant v2. **Idempotent** via `skip_existing=True` (default) —
   safe to re-run after an interruption (e.g. PC shutdown mid-run); it'll skip
   already-embedded points and resume. Don't run two instances concurrently —
   they'll both load the embedding model onto the same GPU and can OOM (check
   `Get-CimInstance Win32_Process -Filter "Name='python.exe'"` for duplicate
   `reindex_v2.py` command lines before launching).

`build_indexes.py` (no `--corpus`) does a **full BM25 reset** across all
corpora — only use deliberately, always with `--corpus` for incremental
updates in normal operation.

## Running the eval suite

`eval/run_eval.py` default HTTP timeout is 60s (`eval/evaluator.py`) — too
short once LLM generation slows down (see below) or `RE_RETRIEVAL` retries
kick in from reviewer FAILs; bump it if you see `errore API` entries that
correspond to queries that *would* have succeeded given more time (check the
API/LM Studio logs for the matching request to confirm it was a timeout, not
a real failure).

LM Studio's prompt cache grows across unrelated queries within one server
session and can saturate the shared KV-cache budget (e.g. 8192 MiB across 4
slots), causing token generation to drop from ~100 t/s to a ~27-29 t/s plateau
partway through a long eval run (this is a GPU-bound prefix-cache management
cost, not thermal throttling — check `nvidia-smi` clocks/temp to rule
throttling out). **Restart LM Studio between eval files**, not just once at
the start, to keep generation speed up over a multi-file run.

The query files (`tests/script_json/queries_*.jsonl`, `test_aiura_01.jsonl`)
each declare their own `"workspace"` field per query — always grep-check this
matches `mio-studio` (see top of this doc) before trusting a recall regression
or improvement.
