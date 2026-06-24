# Architettura della Knowledge Base — AiUra LegalLab

*Ultimo aggiornamento: 2026-06-18*

Documento tecnico di riferimento sull'intera pipeline di costruzione, struttura e interrogazione della knowledge base legale. Copre BM25, Qdrant, grafo normativo, struttura dei chunk MongoDB, pipeline di ingestion, retrieval ibrido, ragionamento IQRAC e classificazione per settore.

---

## Indice

1. [Overview e stack](#1-overview-e-stack)
2. [Chunk MongoDB — schema e ciclo di vita](#2-chunk-mongodb--schema-e-ciclo-di-vita)
3. [Ingestion pipeline — come entrano i dati](#3-ingestion-pipeline--come-entrano-i-dati)
4. [BM25 — indice full-text per corpus](#4-bm25--indice-full-text-per-corpus)
5. [Qdrant — indice vettoriale](#5-qdrant--indice-vettoriale)
6. [Grafo normativo — NetworkX](#6-grafo-normativo--networkx)
7. [Retrieval ibrido — fusione RRF e reranking](#7-retrieval-ibrido--fusione-rrf-e-reranking)
8. [Settori e classificazione](#8-settori-e-classificazione)
9. [Ragionamento IQRAC — agenti e orchestrazione](#9-ragionamento-iqrac--agenti-e-orchestrazione)
10. [Tipi e strutture dati](#10-tipi-e-strutture-dati)
11. [Dimensioni e caratteristiche produttive](#11-dimensioni-e-caratteristiche-produttive)
12. [Comandi operativi](#12-comandi-operativi)

---

## 1. Overview e stack

```
MongoDB (source of truth)
│
├── normattiva_docs      ← Norme da normattiva.it (READ-ONLY, da LegalAgentLab)
└── chunks               ← Chunk indicizzati (scritto da AiUraLegalLab)
         │
         ├─→ BM25 (bm25s) ─────────────────────────────┐
         ├─→ Qdrant (SentenceTransformer embeddings) ───┤ HybridRetriever
         └─→ Grafo normativo (NetworkX JSON) ────────────┘
                                                         │
                                                    RRF Fusion
                                                         │
                                                   CrossEncoder Rerank
                                                         │
                                                   ResearchPacket (6 fonti)
                                                         │
                                                   IQRAC Agents (S1→S5)
```

**Corpus disponibili nei chunk:**

| Corpus | Descrizione | Sorgente |
|--------|-------------|----------|
| `normattiva` | Norme da normattiva.it | Mirror da `normattiva_docs` |
| `dottrina` | Manuali, riviste, commentari | `/ingest?corpus=dottrina` |
| `giurisprudenza` | Sentenze Cassazione, Corte Cost. | `build_jurisprudence_indexes.py` |
| `studio` | Atti e contratti caricati dall'avvocato | `/ingest` (default) |

---

## 2. Chunk MongoDB — schema e ciclo di vita

**Database:** `aiura_legal_lab_db` — **Collection:** `chunks`

### Schema completo

```javascript
{
    "_id":             ObjectId,   // ID primario (24-hex)
    "source_id":       String,     // URN normattiva o hex16 sentenza — identità logica del chunk
    "workspace":       String,     // workspace (multi-tenancy, default "mio-studio")

    // Testo
    "text":            String,     // testo completo del chunk (full-text, Fase 1)
    "titolo_articolo": String,     // titolo riportato nel documento (opzionale)
    "sommario":        String,     // sommario/abstract (usato in BM25 prefix)

    // Classificazione
    "corpus":          String,     // "normattiva" | "dottrina" | "giurisprudenza" | "studio"
    "fonte":           String,     // "legge" | "dlgs" | "decreto" | "sentenza" | "articolo_rivista" | ...
    "testo_tipo":      String,     // "normativo" | "formula" (per normattiva)
    "settore":         [String],   // ["penale", "civile", ...] — multi-label

    // Riferimento al provvedimento
    "titolo":          String,     // titolo del provvedimento (es. "Codice Penale")
    "articolo_num":    String,     // numero/etichetta articolo (es. "Art. 43")
    "chunk_index":     Integer,    // ordinale progressivo per stesso source_id

    // Vigenza temporale
    "valid_from":      Date,       // data inizio vigenza
    "valid_to":        Date,       // data fine vigenza (null = ancora vigente)

    // Provenienza
    "source":          String,     // "normattiva_mirror" | "dottrina_scraper" | ...
    "urn":             String,     // URN (legacy, fallback per source_id)

    // Timestamp
    "created_at":      Date,
    "updated_at":      Date,
}
```

### Indici MongoDB

```python
# Upsert idempotente (garantisce unicità per provvedimento)
[("source_id", 1), ("chunk_index", 1), ("workspace", 1)]  → UNIQUE

# Ricerca per workspace e corpus
[("workspace", 1)]
[("corpus", 1), ("fonte", 1)]
```

### `source_id` — identità logica

Il `source_id` è la chiave di identità che attraversa tutti e tre gli indici (BM25, Qdrant, grafo). Non è l'`_id` MongoDB:

| Corpus | Formato `source_id` | Esempio |
|--------|---------------------|---------|
| normattiva | URN Normattiva | `urn:nir:stato:legge:2003-06-19;196!art23` |
| giurisprudenza | `hex16_tipo` | `e65a598d71052357_massima` |
| dottrina/studio | ObjectId stringified | `507f1f77bcf86cd799439011` |

---

## 3. Ingestion pipeline — come entrano i dati

### Normattiva

```
normattiva_docs (MongoDB, READ-ONLY)
         ↓
NormattivaDocAdapter.from_mongo_doc()  [parsing AKN, estrae campi]
         ↓
NormattivaChunker (chunking adattivo per lunghezza articolo)
         ↓
chunks collection  (upsert via source_id + chunk_index + workspace)
         ↓
LegalGraphBuilder.update_batch()  [archi rimandi dal testo]
```

**Strategia chunking adattiva (NormattivaChunker):**

```
token_count ≤ 400  →  1 chunk (articolo intero, ~80% dei casi)
token_count ≤ 800  →  Chunker(max=256, overlap=32)
token_count >  800  →  Chunker(max=256, overlap=64)
```

Token contati con tiktoken `cl100k_base`.

### Giurisprudenza

```
Scraper per fonte (cassazione, corte_cost, ...)
         ↓
JurisprudenceCoordinator
         ↓
Chunking per sezione: massima | motivazione | dispositivo
         ↓
Chunker(max=256, overlap=32) per sezione
         ↓
chunk.id = hex16_tipo  (hex16 sentenza + suffisso "_massima" ecc.)
chunk.corpus = "giurisprudenza"
```

Fonti operative: ~317k sentenze da 5 sorgenti (`cassazione`, `corte_cost`, …).

### Dottrina e Studio

```
POST /ingest?corpus=dottrina  (o ometti per default "studio")
         ↓
Tier1Pipeline(corpus=corpus)
         ↓
Chunker(max=512, overlap=64) standard
         ↓
chunks collection
```

Il campo `corpus` determina quale sotto-indice BM25 e quale profilo di retrieval useranno i chunk.

---

## 4. BM25 — indice full-text per corpus

**File:** `aiura_legal/core/retrieval/bm25_retriever.py`
**Engine:** `bm25s` — 220× più veloce di `rank_bm25` (4.6ms vs 1013ms su 500k doc)

### Struttura su disco

```
workspaces/<ws>/indices/
    bm25_normattiva.pkl      ← sub-indice normattiva
    bm25_dottrina.pkl        ← sub-indice dottrina
    bm25_giurisprudenza.pkl  ← sub-indice giurisprudenza
    bm25_studio.pkl          ← sub-indice studio
    bm25_meta.json           ← metadati ispezione KB
```

Ogni `.pkl` è una `_BM25Sub` serializzata (pickle). Prima della Fase 1 esisteva un singolo `bm25.pkl` monolitico; la migrazione avviene automaticamente all'avvio se il file legacy è presente.

### Struttura `_BM25Sub`

```python
@dataclass
class _BM25Sub:
    corpus: str                       # corpus di appartenenza
    ws: Path                          # workspace path

    doc_ids:        list[str]         # ObjectId MongoDB (_id) di ogni doc
    doc_snippets:   list[str]         # text[:300] per snippet
    doc_metadata:   list[dict]        # metadati completi (corpus, fonte, settore, ...)
    doc_source_ids: list[str]         # source_id (URN o hex16)
    tokenized:      list[list[str]]   # token per bm25s (pre-tokenizzati)

    # Array numpy per filtri vettorizzati O(1) senza loop Python
    corpus_arr:     np.ndarray        # shape (n_docs,), dtype object
    fonte_arr:      np.ndarray
    testo_tipo_arr: np.ndarray

    _bm25s_retriever: object          # bm25s.BM25() — lazy build al primo search
    dirty: bool                       # True se doc_ids modificati → rebuild bm25s
```

### Tokenizzazione

```python
ITALIAN_STOPWORDS = {"il", "la", "di", "del", "a", "che", ...}  # 45+ parole

def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"\w+", text.lower())
    return [t for t in tokens if len(t) > 1 and t not in ITALIAN_STOPWORDS]
```

Il testo indicizzato è: `sommario + "\n" + titolo_articolo + "\n" + text` (full-text, introdotto nella Fase 1 — in precedenza solo `text[:200]`).

### Operazioni chiave

**`build(docs)`** — costruisce il sub-indice da zero:
1. Filtra per `corpus` (ogni sub gestisce il suo)
2. Tokenizza testi
3. Marca `dirty=True` → bm25s viene costruito al prossimo `search()`

**`_ensure_bm25s()`** — lazy build (chiamato internamente da `search()`):
```python
if self.dirty or self._bm25s_retriever is None:
    import bm25s
    self._bm25s_retriever = bm25s.BM25()
    self._bm25s_retriever.index(self.tokenized)
    self.dirty = False
```

**`search(query, top_k, chunk_filter)`**:
1. Tokenizza query
2. `bm25s.retrieve(tokens, k=n_docs)` — score su TUTTI i doc
3. Applica filtri azzerando score dei doc non corrispondenti:
   - `corpus` (implicito: ogni sub si occupa del suo)
   - `fonte` (legge, dlgs, ...)
   - `testo_tipo` (normativo, formula)
   - `_source_id_in` (filtro lista source_id, BM25-only — Qdrant non lo vede)
4. Top-k per score
5. Output: `SearchResult(retrieval_method="bm25")`

**`_remove_corpus(corpus)`** — svuota un sub senza toccare gli altri (usato da `build_indexes.py --corpus X`).

**`_reset()`** — svuota tutti i sub (full rebuild; richiede `build_jurisprudence_indexes.py` dopo).

### Schema version e compatibilità

`_BM25_SCHEMA_VERSION = 2`. Al caricamento il pkl viene validato; se versione diversa, il sub è ricreato da zero al prossimo build.

---

## 5. Qdrant — indice vettoriale

**File:** `aiura_legal/core/retrieval/vector_retriever.py`

### Due versioni coesistenti

| | V1 (produzione) | V2 (candidato Fase 2) |
|---|---|---|
| **Collection** | `legal_docs` | `legal_docs_v2` |
| **Modello** | `paraphrase-multilingual-MiniLM-L12-v2` | `intfloat/multilingual-e5-base` |
| **Dimensioni** | 384 | 768 |
| **Prefissi e5** | — | `query: ` / `passage: ` |
| **on_disk_payload** | `False` | `False` |
| **Classe** | `VectorRetriever` | `VectorRetrieverV2` |

Il cutover è atomico: quando `legal_docs_v2` supera il gate eval (Recall > 0.737), aggiornare le costanti `_COLLECTION_NAME` / `_EMBED_MODEL` / `_VECTOR_SIZE` e rimuovere v1.

### Payload di ogni punto Qdrant

```python
payload = {
    # Metadati da Document.metadata (tutti str)
    "corpus":          str,   # "normattiva" | "dottrina" | ...
    "fonte":           str,
    "testo_tipo":      str,
    "titolo":          str,
    "articolo":        str,
    "settore":         str,   # comma-separated: "penale,civile"
    "workspace":       str,   # presente solo se chunk ha workspace (retrocompat Fase 0)

    # ID originale — CRITICO per fusione RRF con BM25 e grafo
    "mongo_id":        str,   # Document.id (ObjectId 24-hex o hex16_tipo)
    "source_id":       str,   # URN o hex16

    # Testo (tronco per risparmio spazio)
    "text":            str,   # text[:1000]

    # Filtri temporali — INTEGER index dichiarati esplicitamente
    "valid_from_int":  int,   # YYYYMMDD (0 se data assente)
    "valid_to_int":    int,   # YYYYMMDD (99999999 se data assente)
}
```

### Payload index dichiarati esplicitamente

```python
# KEYWORD: filtri esatti corpus/workspace (dichiarati prima di qualsiasi upsert)
workspace, corpus

# INTEGER: range filter su date di vigenza
valid_from_int, valid_to_int
```

> **Perché espliciti:** se mancano e Qdrant li ricostruisce lazily al riavvio leggendo il gridstore (`on_disk_payload=true`), un payload parzialmente scritto (es. dopo panic gridstore) provoca `LiteralOutOfBounds` → crash loop. Con `on_disk_payload=False` (RocksDB WAL transazionale) e indici dichiarati prima dell'upsert, la corruzione non è possibile.

### Funzioni di utilità

**`_to_qdrant_id(doc_id: str) -> str`**
- Converte qualsiasi ID stringa in UUID v5 deterministico
- `uuid.uuid5(uuid.NAMESPACE_DNS, doc_id)` → stesso input = stesso UUID sempre
- Permette la fusione RRF: BM25 e Qdrant producono la stessa chiave per lo stesso chunk

**`_date_to_int(d: date) -> int`**
- `date(2024, 1, 15)` → `20240115`

**`_build_qdrant_filter(chunk_filter, valid_on, workspace)`**
- Converte filtri ChromaDB-style in `qdrant_client.models.Filter`
- `valid_on`: `FieldCondition(valid_from_int ≤ d_int)`
- `workspace`: `should` con `workspace == ws` OR `IsEmpty(workspace)` (retrocompat punti pre-Fase 0 senza campo)
- Supporta `$and`, `$or`, `$in`, `$lte`; chiavi `_*` (BM25-only) silenziosamente ignorate

### Modalità connessione

```
QDRANT_URL=http://localhost:6333  →  Server mode (storage in workspaces/qdrant_storage/)
QDRANT_URL=""                     →  Embedded mode (storage in workspaces/<ws>/indices/qdrant/)
```

Server mode preferito: nessun limite di punti, batch_size=512 vs 256 embedded.

### Snapshot e ripristino (VectorRetrieverV2)

Dopo ogni `reindex_v2.py`, viene creato automaticamente uno snapshot Qdrant:

```bash
# Elenca snapshot disponibili
python scripts/reindex_v2.py --list-snapshots

# Ripristino rapido senza re-embedding (~secondi invece di ~ore)
python scripts/reindex_v2.py --restore legal_docs_v2-2026-06-18T...snapshot
```

Gli snapshot sono salvati in `workspaces/qdrant_storage/snapshots/legal_docs_v2/`.

---

## 6. Grafo normativo — NetworkX

**File:** `aiura_legal/core/graph/retriever.py`, `builder.py`
**Storage:** `workspaces/<ws>/indices/graph.json` (NetworkX node-link JSON)

### Tipi di nodo

**Nodo `article`** (un chunk = un nodo):
```python
node_id = source_id   # URN o hex16 sentenza
attrs = {
    "node_type":    "article",
    "fonte":        str,          # "legge" | "dlgs" | "sentenza" | ...
    "titolo":       str,
    "articolo_num": str,
    "testo_tipo":   str,
    "valid_from":   date_str,
    "valid_to":     date_str,
}
```

**Nodo `provvedimento`** (super-nodo aggregatore):
```python
node_id = f"PROV:{fonte}:{titolo}"
attrs = {
    "node_type": "provvedimento",
    "fonte":     str,
    "titolo":    str,
}
```

### Tipi di arco

| Arco | Direzione | Significato |
|------|-----------|-------------|
| `RINVIA` | A → B | A rimanda esplicitamente a B |
| `ABROGA` | X → A | X abroga A |
| `MODIFICA` | X → A | X modifica A |
| `CONTRASTA` | A ↔ B | Conflitto normativo (bidirezionale) |
| `APPARTIENE_A` | article → provvedimento | Raggruppamento |

I rimandi (`RINVIA`) sono estratti automaticamente dal testo degli articoli tramite `ReferenceExtractor` (regex + pattern matching su citazioni normative).

### Navigazione del grafo

**`expand(source_ids, depth=1, edge_types, max_nodes, valid_on)`**
- BFS da `source_ids` per `depth` hop
- Filtra per `edge_types` (default: RINVIA, ABROGA, MODIFICA)
- Se `valid_on`: salta nodi non vigenti alla data
- Score: `1.0 / (1.0 + distanza_hop)`
- Output: `SearchResult(retrieval_method="graph_expansion")`

**`get_conflicts(source_ids)`**
- Trova archi `CONTRASTA` o `ABROGA` tra i source_ids
- Usato dal `CitationReviewer` (S5) per segnalare conflitti nelle citazioni

### Build del grafo

**Prima passata** (nodi): aggiunge tutti gli `article` + `provvedimento` e popola lookup
**Seconda passata** (archi): risolve rimandi → aggiunge `RINVIA`/`MODIFICA`/`ABROGA`

Il grafo cresce incrementalmente: `update_batch(chunks)` aggiorna nodi e archi senza ricostruire da zero.

---

## 7. Retrieval ibrido — fusione RRF e reranking

**File:** `aiura_legal/core/retrieval/hybrid_retriever.py`

### Profili di peso per QueryIntent

```python
_INTENT_WEIGHTS = {
    NORMA_LOOKUP:           (0.55, 0.25, 0.20),   # BM25-heavy: cerca norma specifica
    GIURISPRUDENZA_SEARCH:  (0.20, 0.70, 0.10),   # Vector-heavy: semantica sentenze
    FATTISPECIE_ANALYSIS:   (0.25, 0.60, 0.15),   # Bilanciato verso semantica
    NORMA_EVOLUTION:        (0.40, 0.35, 0.25),   # Graph-heavy: evoluzione storica
    RISCHIO_CONTRATTUALE:   (0.35, 0.55, 0.10),   # Semantico: concetti contrattuali
    PRECEDENTE_INTERNO:     (0.30, 0.60, 0.10),   # Precedenti + semantica
}
# Formato: (w_bm25, w_vector, w_graph)

# Pesi fissi per round bifasico (PhaseRetriever)
_WEIGHTS_NORMATIVA       = (0.65, 0.20, 0.15)   # BM25-heavy (norma precisa)
_WEIGHTS_GIURISPRUDENZA  = (0.15, 0.75, 0.10)   # Vector-heavy (semantica sentenze)
_WEIGHTS_DOTTRINA        = (0.40, 0.50, 0.10)   # Bilanciato verso vector
```

### Algoritmo RRF

```
Per ogni sorgente s ∈ {BM25, Vector, Graph}:
    RRF_s(doc) = w_s × 1 / (60 + rank_s(doc) + 1)

Score_finale(doc) = Σ RRF_s(doc)   per ogni sorgente che ha trovato doc
```

La costante `k = 60` è il valore standard RRF (Cormack et al., 2009).

### Chiave di fusione tra retriever

BM25 e grafo ritornano `doc_id` come stringa originale (ObjectId o hex16). Qdrant può ritornare UUID v5 o l'ID originale (campo `mongo_id` nel payload). Per confrontare documenti da sorgenti diverse:

```python
def _fusion_key(doc_id: str) -> str:
    if UUID_RE.match(doc_id):
        return doc_id.lower()          # già UUID → usa direttamente
    return _to_qdrant_id(doc_id)       # ObjectId/hex16 → converti in UUID v5
```

Stesso chunk da BM25 + Qdrant → stessa chiave → punteggi RRF sommati.

### Pipeline completa retrieval

```
query
  │
  ├─ BM25.search(query, top_k=20, chunk_filter)              [~5ms, CPU]
  ├─ VectorRetriever.search(query, top_k=20, ...)            [~500ms, GPU/CPU]
  └─ GraphRetriever.expand(top_bm25_ids, depth=1)            [<10ms, RAM]
            │
            ▼
       RRF Fusion (w_bm25, w_vec, w_graph)                   [<5ms]
            │ merged: 10-30 doc unici (dedup per fusion_key)
            ▼
       CrossEncoder rerank (top_k_rerank=6)                  [<100ms]
            │ mmarco-mMiniLMv2-L12-H384-v1, max 510 token
            ▼
       ResearchPacket (6 fonti finali)
```

### Retrieval bifasico (PhaseRetriever)

Per intenti che richiedono normativa + giurisprudenza separati:

```
Round 1 — corpus=normattiva + dottrina:
    weights = (0.65, 0.20, 0.15)   BM25-heavy

Round 2 — corpus=giurisprudenza:
    weights = (0.15, 0.75, 0.10)   Vector-heavy

→ Parallelizzati: ThreadPoolExecutor(max_workers=2)
→ Taggati: source_layer = "normativa" | "giurisprudenza" | "dottrina"
```

Questo round separato corrisponde alle Fasi 2 e 3 dell'IQRAC (vedi §9).

### CrossEncoder reranker

```
Modello: cross-encoder/mmarco-mMiniLMv2-L12-H384-v1  (multilingue)
Input:   (query, testo_chunk[:510_token])
Output:  logit (0.0 ≈ 50% relevance, positivo = più rilevante)

Soft bonus settore:
    Se chunk.settore ∩ query_settori → +settore_boost_weight (default 1.0)
    Additivo sul logit cross-encoder (mai esclude, solo premia)
    Attivo se AIURA_SETTORE_SOFT=1
```

**Latenza totale retrieval:** ~500-800ms (BM25 + Vector parallelizzati + rerank seriale).

---

## 8. Settori e classificazione

**File:** `aiura_legal/core/retrieval/settori.py`

### Settori validi

```python
SETTORI_VALIDI = [
    "penale", "civile", "amministrativo", "lavoro",
    "tributario", "processuale", "costituzionale", "altro",
]
```

### Regole keyword condivise

26 regole `(keywords: list[str], settori: list[str], confidence: float)` in `KEYWORD_RULES`. Le stesse regole servono sia per classificare i chunk a ingestion time (`classify_keywords`) sia per classificare la query a retrieval time (`classify_query`).

Esempi:
```python
(["codice penale", "c.p.", "reato", "delitto", "omicidio"], ["penale"], 0.90),
(["codice civile", "contratto", "responsabilità civile"],   ["civile"],  0.90),
(["irpef", "ires", "iva", "imposta sul reddito"],           ["tributario"], 0.90),
(["pubblica amministrazione", "tar", "consiglio di stato"], ["amministrativo"], 0.88),
(["sicurezza sul lavoro", "d.lgs. 81"],                     ["lavoro"], 0.95),
```

### Funzioni

**`classify_keywords(titolo, snippet) -> (list[str], float) | None`**
- Usato a ingestion time per taggare i chunk
- Priorità titolo > snippet (confidence ridotta di 0.1 se match solo snippet)
- Primo match vince (early exit)
- Output: `(["penale", "processuale"], 0.90)` oppure `None`

**`classify_query(query) -> list[tuple[str, float]]`**
- Usato a retrieval time per ogni query
- Multi-label: scansiona TUTTE le 26 regole (no early exit)
- Una query può toccare più settori (es. "reato di evasione fiscale" → penale + tributario)
- Output: `[("penale", 0.90), ("tributario", 0.90)]` (ordinato per confidence)

### Come i settori influenzano il retrieval

```python
# PhaseRetriever — attivazione condizionale

if settore_confidence >= 0.7 and AIURA_SETTORE_FILTER=1:
    # Hard filter: esclude chunk fuori settore
    # Fallback automatico senza filtro se risultati < 3

elif settore_confidence >= 0.4 and AIURA_SETTORE_SOFT=1:
    # Soft filter: penalizza ×0.5 i chunk fuori settore (non li esclude)
    _apply_soft_penalty(results, settori_query)

# Reranker — bonus additivo sempre attivo
logit_finale = cross_encoder_logit + (settore_boost_weight * in_settore)
```

---

## 9. Ragionamento IQRAC — agenti e orchestrazione

**File:** `aiura_legal/agents/orchestrator.py`, `analyst.py`, `clarifier.py`, `query_classifier.py`

### Catena agenti S0 → S5

```
S0 Routing          Programmatico (QueryIntent da query_classifier.py, zero LLM)
       ↓
S1 Clarifier        Valuta ambiguità. Se necessario → exit con domanda chiarificatrice
       ↓
S2 Retrieval        HybridRetriever bifasico → ResearchPacket (6 fonti)
       ↓
Phase 0             QueryTypeClassifier: "case" | "doctrine"  (~150 token, ~0.3s)
       ↓
S3 Analysis IQRAC   4 fasi sequenziali — struttura diversa per "case" e "doctrine"
       ↓
S5 Review           CitationReviewer rule-based (zero LLM) — grounding check
```

### Phase 0 — QueryTypeClassifier

**File:** `aiura_legal/agents/query_classifier.py`

Prima di entrare in S3, una singola LLM call classifica la query:

```
"doctrine" = domanda astratta su istituto giuridico, presupposti normativi,
             orientamenti generali.
             Segnali: "in quali casi", "quando è legittimo", "cosa si intende per",
                      "quali sono i requisiti", "come funziona", "è possibile"

"case"     = domanda su una situazione concreta con fatti specifici da analizzare.
```

Output: `{"query_type": "case"}` oppure `{"query_type": "doctrine"}`.
Fallback: `"case"` in caso di errore — nessuna regressione.

Il `query_type` seleziona il sistema di prompt e la struttura di Fase 1 (le fasi 2-3-4 sono identiche nei due flussi).

---

### Flusso A — Casi reali (`query_type="case"`)

Per domande su una fattispecie concreta: "il mio cliente ha fatto X, può essere accusato di Y?"

**Fase 1 — FRAMING** *(prompt: `legal_analyst_framing.md`)*

| Step | Nome | Scopo |
|------|------|-------|
| 1 | `RICOSTRUZIONE_FATTO` | Distilla i fatti giuridicamente rilevanti dal quesito |
| 2 | `QUALIFICAZIONE` | Qualificazione giuridica della fattispecie |
| 3 | `QUESTIONE` | Formula la questione giuridica precisa |

Output chiave estratti dal JSON di Fase 1:
- `questione_retrieval` → query per il retrieval normativa in Fase 2
- `qualificazione_retrieval` → query per il retrieval giurisprudenza in Fase 3
- `settore_giuridico` → guida il filtro settore nelle fasi successive

**Fase 2 — NORMATIVA** *(identica nei due flussi)*

**Fase 3 — GIURISPRUDENZA** *(identica nei due flussi)*

**Fase 4 — SINTESI** *(prompt: `legal_analyst_sintesi.md`)*

| Step | Nome | Scopo |
|------|------|-------|
| 7 | `SUSSUNZIONE` | Applica le norme al caso concreto |
| 8 | `OBIEZIONI` | Anticipa eccezioni e controtesi |
| 9 | `CONCLUSIONE` | Risposta definitiva con raccomandazione operativa |

---

### Flusso B — Dottrina (`query_type="doctrine"`)

Per domande astratte su istituti giuridici: "quando è possibile revocare una donazione?" o "quali sono i requisiti del licenziamento per giusta causa?"

**Fase 1 — FRAMING_DOTTRINA** *(prompt: `legal_analyst_framing_dottrina.md`)*

| Step | Nome | Scopo |
|------|------|-------|
| 1 | `INQUADRAMENTO_ISTITUTO` | Identificazione e definizione dell'istituto giuridico |
| 2 | `PERIMETRO_DOTTRINALE` | Ambito applicativo, elementi costitutivi, distinzioni |
| 3 | `QUESTIONE_ANALITICA` | Formula la questione analitica per guidare il retrieval |

Output chiave: `questione_retrieval` e `qualificazione_retrieval` (stessi campi del flusso `case`, per compatibilità con le fasi successive).

**Fase 2 — NORMATIVA** *(identica nei due flussi)*

**Fase 3 — GIURISPRUDENZA** *(identica nei due flussi)*

**Fase 4 — SINTESI** *(prompt: `legal_analyst_sintesi.md`)*

| Step | Nome | Scopo |
|------|------|-------|
| 7 | `SUSSUNZIONE` | Riconduce le norme all'istituto inquadrato in Fase 1 |
| 8 | `OBIEZIONI` | Orientamenti minoritari, eccezioni dottrinali |
| 9 | `CONCLUSIONE` | Risposta analitica sull'istituto |

---

### Fasi comuni (identiche per entrambi i flussi)

**Fase 2 — NORMATIVA** *(prompt: `legal_analyst_normativa.md`)*

Re-query mirata su `questione_retrieval` dalla Fase 1:

| Step | Nome | Scopo |
|------|------|-------|
| 4 | `FONTI_NORMATIVE` | Richiama le norme rilevanti dal corpus normattiva |
| 5 | `INTERPRETAZIONE` | Interpreta le norme con eventuale supporto dottrinale |

Retrieval: `(0.65, 0.20, 0.15)` BM25-heavy per normattiva + `(0.40, 0.50, 0.10)` per dottrina.

**Fase 3 — GIURISPRUDENZA** *(prompt: `legal_analyst_giurisprudenza.md`)*

Re-query mirata su `qualificazione_retrieval`:

| Step | Nome | Scopo |
|------|------|-------|
| 6 | `GIURISPRUDENZA` | Analizza gli orientamenti giurisprudenziali rilevanti |

Retrieval: `(0.15, 0.75, 0.10)` Vector-heavy.

> **Invariante:** La norma è fondamento (Fase 2), la giurisprudenza è supporto (Fase 3). Mai invertire.

**SSE streaming:** Il frontend riceve ogni fase via Server-Sent Events man mano che viene completata (`POST /query/stream`). Ogni `PhaseResult` porta `phase.name` (`"FRAMING"` o `"FRAMING_DOTTRINA"`) per permettere al frontend di adattare l'etichetta mostrata.

---

### Schema completo dei due flussi a confronto

```
                    FLUSSO CASI REALI          FLUSSO DOTTRINA
                    (query_type="case")         (query_type="doctrine")
                    ─────────────────────────────────────────────────

Phase 0             QueryTypeClassifier → "case"   → "doctrine"

Fase 1              FRAMING                    FRAMING_DOTTRINA
  Step 1            RICOSTRUZIONE_FATTO        INQUADRAMENTO_ISTITUTO
  Step 2            QUALIFICAZIONE             PERIMETRO_DOTTRINALE
  Step 3            QUESTIONE                  QUESTIONE_ANALITICA
  Prompt            legal_analyst_framing.md   legal_analyst_framing_dottrina.md

Fase 2 (identica)   NORMATIVA — FONTI_NORMATIVE + INTERPRETAZIONE
  Retrieval         re-query su questione_retrieval (normattiva + dottrina)
  Prompt            legal_analyst_normativa.md

Fase 3 (identica)   GIURISPRUDENZA
  Retrieval         re-query su qualificazione_retrieval (giurisprudenza)
  Prompt            legal_analyst_giurisprudenza.md

Fase 4 (identica)   SINTESI — SUSSUNZIONE + OBIEZIONI + CONCLUSIONE
  Prompt            legal_analyst_sintesi.md
                    (il tono della SUSSUNZIONE si adatta: fattuale vs analitico)
```

### OrchestratorResult

```python
@dataclass
class OrchestratorResult:
    query: str
    workspace: str
    intent: str                              # QueryIntent

    packet: ResearchPacket                   # S2: 6 fonti + confidence
    analysis: AnalysisResult                 # S3: risposta IQRAC completa

    # S5 Review
    reviewer_verdict: str = "PASS"           # PASS | WARN | FAIL
    reviewer_action:  str = "DELIVER"        # DELIVER | RE_RETRIEVAL | BLOCK
    reviewer_warnings: list[str] = []

    # S1 Early exit
    clarification_needed:   bool = False
    clarification_question: Optional[str] = None

    # Timing (secondi)
    duration_retrieval_s: float = 0.0
    duration_llm_s:       float = 0.0
    duration_total_s:     float = 0.0
```

### S5 CitationReviewer (Citation Contract)

Verifica rule-based (zero LLM) prima che la risposta raggiunga l'avvocato:

1. **Grounding check**: ogni citazione nell'analisi deve essere tracciabile a una fonte nel ResearchPacket
2. **Vigenza check**: le norme citate sono vigenti alla data corrente (usa `valid_from_int` / `valid_to_int`)
3. **Conflict check**: `get_conflicts(source_ids)` dal grafo — segnala archi CONTRASTA / ABROGA

| Verdict | Action | Significato |
|---------|--------|-------------|
| PASS | DELIVER | Tutte le citazioni grounded, nessun conflitto critico |
| WARN | DELIVER | Avvertimenti non bloccanti (es. norma prossima alla scadenza) |
| FAIL | RE_RETRIEVAL o BLOCK | Citazioni non grounded → re-retrieval, o blocco totale |

---

## 10. Tipi e strutture dati

**File:** `aiura_legal/core/types.py`

```python
class QueryIntent(Enum):
    NORMA_LOOKUP            = "norma_lookup"
    GIURISPRUDENZA_SEARCH   = "giurisprudenza_search"
    FATTISPECIE_ANALYSIS    = "fattispecie_analysis"
    PRECEDENTE_INTERNO      = "precedente_interno"
    NORMA_EVOLUTION         = "norma_evolution"
    RISCHIO_CONTRATTUALE    = "rischio_contrattuale"

@dataclass
class Document:
    id:                str           # MongoDB _id (24-hex)
    text:              str           # testo completo
    metadata:          dict = {}     # corpus, fonte, titolo, settore, valid_*, ...
    source_id:         str = ""      # URN o hex16
    valid_from:        Optional[date] = None
    valid_to:          Optional[date] = None

@dataclass
class SearchResult:
    doc_id:            str           # ID originale (non UUID)
    score:             float         # RRF score oppure cross-encoder logit
    snippet:           str           # text[:300]
    metadata:          dict = {}
    source_id:         str = ""      # per CitationReviewer
    retrieval_method:  str = ""      # "bm25" | "vector" | "graph_expansion" | "hybrid_rrf"
    source_layer:      str = "normativa"   # "normativa" | "giurisprudenza" | "dottrina" | "studio"
    full_text:         str = ""      # testo completo (opzionale)

@dataclass
class ResearchPacket:
    query_original:     str
    query_intent:       QueryIntent
    sources:            list[SearchResult] = []    # 6 fonti reranked
    retrieval_confidence: str = "LOW"              # HIGH | MEDIUM | LOW
    gaps:               list[str] = []
    kb_version:         dict = {}
```

**Confidence dal retrieval:**
```python
strong = sum(1 for s in sources if s.score > RETRIEVAL_SCORE_THRESHOLD)
if strong >= 3:  → "HIGH"
elif len(sources) >= 2:  → "MEDIUM"
else:  → "LOW"
```

---

## 11. Dimensioni e caratteristiche produttive

| Metrica | Valore | Note |
|---------|--------|-------|
| Chunk normattiva | ~278k | Da ~185k articoli normattiva.it |
| Chunk dottrina | ~191k | Articoli riviste, monografie |
| Chunk giurisprudenza | ~500k | ~317k sentenze × sezioni |
| Chunk studio | variabile | Upload avvocato |
| **Totale Qdrant v2** | ~1.8M punti | Al 2026-06-17 |
| BM25 normattiva | 4.6ms query | Su 278k doc, CPU |
| Qdrant query | ~500ms | GPU encoding + ANN search |
| CrossEncoder rerank | ~100ms | Su 6 doc, CPU |
| **Latenza S2 totale** | ~600-800ms | BM25 + Vector parallelizzati |
| Qdrant v1 vettori | 384-dim | ~110MB per 278k |
| Qdrant v2 vettori | 768-dim | ~220MB per 278k |
| Batch upsert Qdrant | 512 (server) / 256 (embedded) | |
| CrossEncoder input max | 510 token | mmarco-mMiniLMv2-L12-H384-v1 |
| RRF k constant | 60 | Standard (Cormack et al.) |
| Graph depth expansion | 1 hop | Vicini diretti |

---

## 12. Comandi operativi

```bash
# Attiva venv
.venv\Scripts\activate

# ── Build indici ────────────────────────────────────────────────────────────

# Rebuild normattiva + dottrina + studio (BM25 + Qdrant v1)
python scripts/build_indexes.py --workspace mio-studio

# Rebuild solo un corpus (preserva gli altri)
python scripts/build_indexes.py --workspace mio-studio --corpus normattiva

# Rebuild giurisprudenza (separato — non in chunks collection)
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo corte_cost

# Rebuild Qdrant v2 (multilingual-e5-base, ~2-4h GPU, snapshot automatico alla fine)
python scripts/reindex_v2.py --workspace mio-studio

# Ripristino rapido Qdrant v2 da snapshot (secondi)
python scripts/reindex_v2.py --list-snapshots
python scripts/reindex_v2.py --restore <snapshot_name>

# Patch settore su Qdrant v2 senza re-embedding (post-reclassificazione)
python scripts/patch_settore_payload.py --workspace mio-studio --corpus normattiva,dottrina,giurisprudenza

# ── Verifica ────────────────────────────────────────────────────────────────

python scripts/verify_indexes.py --workspace mio-studio
python eval/run_eval.py

# ── API ─────────────────────────────────────────────────────────────────────

python -m aiura_legal.api
# http://localhost:8765
# Settings UI: http://localhost:5173/settings
```

### Ordine corretto di rebuild completo

```
1. mirror_normattiva.py          (se nuovi dati da normattiva.it)
2. build_indexes.py              (BM25 + Qdrant v1 + grafo)
3. build_jurisprudence_indexes.py (giurisprudenza — separato)
4. reindex_v2.py                 (Qdrant v2 — lungo, snapshot automatico)
5. patch_settore_payload.py      (solo se settori ri-classificati dopo step 4)
6. verify_indexes.py
7. eval/run_eval.py
```

> **Nota:** Se si resetta Qdrant v1 con `--reset-qdrant`, rieseguire obbligatoriamente `build_jurisprudence_indexes.py` perché la giurisprudenza non è in `aiura_legal_lab_db.chunks`.
