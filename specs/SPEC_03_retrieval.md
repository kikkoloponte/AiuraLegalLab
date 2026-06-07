# SPEC 03 — Retrieval Ibrido (aiura_legal/core/retrieval/)

## SearchResult

```python
@dataclass
class SearchResult:
    doc_id: str
    score: float
    snippet: str
    metadata: dict = field(default_factory=dict)
    source_id: str = ""
    retrieval_method: str = ""
    source_layer: str = "normativa"   # "normativa" | "giurisprudenza"
```

`source_layer` indica il livello epistemologico della fonte:
- `"normativa"` — norme (codici, leggi, regolamenti, Cost., UE/CEDU)
- `"giurisprudenza"` — sentenze (Cassazione, Corte Cost., Corti europee, merito)

Default `"normativa"` garantisce backward compatibility con codice esistente.

## BM25Retriever (bm25_retriever.py)

```python
class BM25Retriever:
    def __init__(self, workspace_path: str): ...
    def build(self, documents: list[Document]) -> None: ...
    def add_documents_batch(self, docs: list[Document]) -> None: ...
    def search(self, query: str, top_k: int = 15,
               chunk_filter: dict | None = None) -> list[SearchResult]: ...
    def save(self) -> None:   # pickle → workspace/indices/bm25.pkl
    def load(self) -> None:
```

Libreria: rank_bm25 (BM25Okapi). Thread-safe. Auto-load se file esiste.

`chunk_filter` supporta:
- Filtri esatti su `corpus`, `fonte`, `testo_tipo`  
  es. `{"corpus": "normattiva", "fonte": "codice_civile"}`
- Chiave speciale `_source_id_in`: lista sottostringhe (substring match)  
  es. `{"_source_id_in": ["giurisprudenza_"]}`

## VectorRetriever (vector_retriever.py)

```python
class VectorRetriever:
    def __init__(self, workspace_path: str): ...
    def build(self, documents: list[Document]) -> None: ...
    def add_documents_batch(self, docs: list[Document]) -> None: ...
    def search(self, query: str, top_k: int = 15,
               valid_on: date = None,
               chunk_filter: dict | None = None) -> list[SearchResult]: ...
    def save(self) -> None:
```

Backend: ChromaDB embedded. Model: paraphrase-multilingual-mpnet-base-v2.  
`chunk_filter` viene passato come clausola `where` a ChromaDB (supporta operatori `$and`, `$or`, `$in`).

## CrossEncoderReranker (reranker.py)

```python
class CrossEncoderReranker:
    def rerank(self, query: str, candidates: list[SearchResult],
               top_k: int = 7) -> list[SearchResult]: ...
```

Model: cross-encoder/ms-marco-MiniLM-L-6-v2. Target: < 300ms su CPU.

## HybridRetriever (hybrid_retriever.py)

Orchestra BM25 + Vector + Graph con RRF fusion, reranking CrossEncoder e
weight profiles per intent. Espone due percorsi di retrieval.

### Percorso standard — `build_research_packet()`

Usato per intenti mono-layer (`NORMA_LOOKUP`, `GIURISPRUDENZA_SEARCH`).  
Singolo round, pesi da `_INTENT_WEIGHTS`, `chunk_filter` opzionale dal chiamante.  
Tutte le fonti hanno `source_layer = "normativa"` (default).

### Percorso bifasico — `build_research_packet_bifasico()`

Usato per intenti misti: `FATTISPECIE_ANALYSIS`, `RISCHIO_CONTRATTUALE`,
`NORMA_EVOLUTION`, `PRECEDENTE_INTERNO`.

Due round separati:

| Round | Pesi BM25/Vec/Graph | Filtro corpus | Layer tag |
|-------|---------------------|---------------|-----------|
| 1 — normativa | 0.65 / 0.20 / 0.15 | `corpus=normattiva` | `"normativa"` |
| 2 — giurisprudenza | 0.15 / 0.75 / 0.10 | `corpus=giurisprudenza` | `"giurisprudenza"` |

Il `ResearchPacket` risultante contiene le fonti normative prima di quelle
giurisprudenziali. Se round 2 è vuoto (workspace senza giurisprudenza indicizzata)
il packet contiene solo fonti normative — degradazione graceful.

**Requisito di indicizzazione**: i chunk giurisprudenziali devono avere
`metadata["corpus"] = "giurisprudenza"` (impostato da `JurisprudenceCoordinator.to_chunks()`
dalla v2 in poi). Chunk indicizzati con versioni precedenti vanno re-indicizzati con
`build_indexes.py` per beneficiare del round 2.

```python
class HybridRetriever:
    def search(self, query, intent, top_k_retrieve=20, top_k_rerank=10,
               valid_on=None, chunk_filter=None) -> list[SearchResult]: ...
    def build_research_packet(self, query, intent, valid_on=None,
                              chunk_filter=None) -> ResearchPacket: ...
    def build_research_packet_bifasico(self, query, intent, valid_on=None,
                                       top_k_rerank=6) -> ResearchPacket: ...
```

### Weight profiles (percorso standard)

| Intent | BM25 | Vector | Graph |
|--------|------|--------|-------|
| NORMA_LOOKUP | 0.55 | 0.25 | 0.20 |
| GIURISPRUDENZA_SEARCH | 0.20 | 0.70 | 0.10 |
| FATTISPECIE_ANALYSIS | 0.25 | 0.60 | 0.15 |
| NORMA_EVOLUTION | 0.40 | 0.35 | 0.25 |
| RISCHIO_CONTRATTUALE | 0.35 | 0.55 | 0.10 |
| PRECEDENTE_INTERNO | 0.30 | 0.60 | 0.10 |

## Routing nell'Orchestratore

```python
_BIFASICO_INTENTS = {FATTISPECIE_ANALYSIS, RISCHIO_CONTRATTUALE,
                     NORMA_EVOLUTION, PRECEDENTE_INTERNO}

if intent in _BIFASICO_INTENTS:
    packet = retriever.build_research_packet_bifasico(query, intent, valid_on)
else:
    packet = retriever.build_research_packet(query, intent, valid_on, chunk_filter)
```

## Test

  1. BM25 build/search/persist/reload
  2. Vector semantic search
  3. Reranker cambia l'ordine di BM25 raw
  4. Hybrid end-to-end con 20 doc sintetici
  5. `build_research_packet_bifasico()` — due round separati, layer corretti,
     normativa prima di giurisprudenza nel packet
  6. `SearchResult()` senza `source_layer` → default `"normativa"`
