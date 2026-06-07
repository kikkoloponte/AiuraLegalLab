# Design Spec — Completamento Milestone 0
**Data:** 2026-05-28  
**Progetto:** AiUra LegalLab  
**Scope:** Eval script, verifica indici 1000 doc, README installazione  
**Stato:** Approvato

---

## 1. Architettura generale

### Componenti da creare

```
eval/
  evaluator.py          # metriche core (groundedness, recall@k, latenza)
  run_eval.py           # CLI runner
  queries.jsonl         # batteria query di test per modulo legislativo
  results/              # output JSON + Markdown (gitignored)

scripts/
  verify_indexes.py     # build 1000 doc campione + smoke test + build_report.json

README.md               # installazione + curl examples + troubleshooting
```

### Dipendenze tra componenti

```
queries.jsonl ──► evaluator.py ──► run_eval.py ──► eval/results/
                                        │
                              richiede API online (POST /query)

LegalAgentLab (READ-ONLY) ──► verify_indexes.py ──► build_report.json
                                        │
                              usa build_indexes.py logic internamente
```

### Principi architetturali

- `evaluator.py` è puro Python, senza dipendenze da FastAPI — testabile in isolamento
- `run_eval.py` è l'unico punto di I/O (file + HTTP)
- `verify_indexes.py` è sync (come tutti gli script CLI del progetto)
- Nessuna scrittura permanente in `aiura_legal` (workspace `verify_sample` pulibile)
- Exit code semantico: `0` = OK, `1` = FAIL — utile per CI futura

---

## 2. `eval/evaluator.py`

### Data structures

```python
@dataclass
class EvalQuery:
    id: str
    query: str
    workspace: str
    intent: str
    expected_source_ids: list[str]   # URN / source_id attesi (può essere vuoto)
    module: str = ""                  # es. "codice_civile", "diritto_lavoro"
    difficulty: str = "medium"        # "easy" | "medium" | "hard"
    top_k: int = 10

@dataclass
class EvalResult:
    query_id: str
    module: str
    difficulty: str
    query: str
    latency_ms: float
    retrieved_source_ids: list[str]
    groundedness: float               # 0.0–1.0
    recall_at_k: float | None         # None se expected vuoto
    retrieval_confidence: str         # HIGH | MEDIUM | LOW
    reviewer_verdict: str             # PASS | WARN | BLOCK
    error: str | None

@dataclass
class EvalReport:
    run_id: str                       # timestamp ISO
    total: int
    errors: int
    mean_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    mean_groundedness: float
    mean_recall_at_k: float | None
    pass_rate: float                  # % dove reviewer_verdict != BLOCK
    per_module: dict[str, dict]       # metriche aggregate per modulo
    results: list[EvalResult]
```

### Metodo `run_query()`

Chiama `POST /query` tramite `httpx.AsyncClient`. Misura latenza con `time.perf_counter()`.  
Non solleva mai eccezioni: errori catturati in `EvalResult.error`, metriche a `0.0`.

### Metrica `groundedness`

Percentuale di `source_id` ritornati che matchano almeno uno di questi pattern:
- `urn:nir:` (Normattiva)
- `CC_ART_\d+` (Codice Civile interno)
- `CASS_(PEN|CIV|SS_UU)_\d{4}_\d+` (Cassazione)
- Qualsiasi `source_id` non vuoto con lunghezza ≥ 5

```
groundedness = sources_with_valid_id / total_sources_returned
```

### Metrica `recall@k`

```
recall@k = |retrieved_source_ids ∩ expected_source_ids| / |expected_source_ids|
```

Se `expected_source_ids` è vuoto → `None` (escluso dalla media globale).

### Aggregazione `build_report()`

- `mean_*` → media aritmetica sui risultati non-error
- `p50/p95` latenza → `numpy.percentile` (o implementazione pura se numpy non disponibile)
- `pass_rate` → `count(verdict != "BLOCK") / total`
- `per_module` → stesse metriche filtrate per `result.module`

---

## 3. `eval/run_eval.py` + `eval/queries.jsonl`

### CLI

```
python eval/run_eval.py \
  --queries eval/queries.jsonl \
  --api-url http://127.0.0.1:8765 \
  --output eval/results/ \
  --top-k 10 \
  [--module codice_civile]   # filtro opzionale per modulo
```

### Flusso

1. Legge `queries.jsonl` → lista `EvalQuery`
2. Filtra per `--module` se specificato
3. Verifica `GET /health` → esce con messaggio leggibile se API non risponde
4. Chiama `Evaluator.run_all()` con progress log (una riga per query: id + latenza + verdict)
5. Scrive `eval/results/eval_<run_id>.json` (report completo)
6. Scrive `eval/results/eval_<run_id>.md` (summary Markdown)
7. Stampa summary su stdout
8. Exit `0` se `pass_rate ≥ 0.80`, `1` altrimenti

### Schema `queries.jsonl`

Una query per riga. Campi:

| Campo | Tipo | Note |
|---|---|---|
| `id` | str | `<modulo_abbr>_NNN` es. `cod_civ_001` |
| `module` | str | Vedi tabella moduli sotto |
| `difficulty` | str | `easy` \| `medium` \| `hard` |
| `query` | str | Testo della query in italiano |
| `workspace` | str | Default `"default"` |
| `intent` | str | `norma_lookup` \| `giurisprudenza` \| `analisi_contratto` |
| `expected_source_ids` | list[str] | URN Normattiva o vuoto `[]` |
| `top_k` | int | Default `10` |

### Moduli legislativi e distribuzione (50 query Golden Test Set)

| Modulo | Codice | Corpus Normattiva | Easy | Medium | Hard | Tot |
|---|---|---|---|---|---|---|
| Codice Civile | `cod_civ` | `urn:nir:stato:regio.decreto:1942-03-16;262` | 3 | 4 | 2 | 9 |
| Diritto del Lavoro | `lav` | L. 300/1970 + D.Lgs. 81/2008 | 2 | 3 | 2 | 7 |
| Diritto Penale | `pen` | R.D. 1930 + D.Lgs. 231/2001 | 2 | 2 | 2 | 6 |
| Diritto Amministrativo | `amm` | L. 241/1990 + D.Lgs. 36/2023 | 2 | 2 | 1 | 5 |
| Diritto Tributario | `trib` | D.P.R. 917/1986 + D.P.R. 633/1972 | 2 | 2 | 1 | 5 |
| Locazioni & Contratti | `loc` | L. 431/1998 | 3 | 3 | 1 | 7 |
| Diritto di Famiglia | `fam` | Cod. Civ. libro I + L. 898/1970 | 2 | 2 | 1 | 5 |
| Cross-modulo | `cross` | Query multi-fonte | — | 4 | 2 | 6 |
| **Totale** | | | **16** | **22** | **12** | **50** |

*Il file `queries.jsonl` include 10 query iniziali (una per modulo) come bootstrap.  
Le restanti 40 saranno aggiunte dopo validazione con l'avvocato (Milestone 1D).*

### Output Markdown (template)

```markdown
# Eval Report — <run_id>

## Summary globale

| Metrica            | Valore  |
|--------------------|---------|
| Query totali       | N       |
| Errori             | N       |
| Pass rate          | 00.0%   |
| Latenza media      | NNN ms  |
| Latenza p95        | NNN ms  |
| Groundedness media | 0.NN    |
| Recall@10 media    | 0.NN    |

## Per-module Summary

| Modulo           | Query | Errori | Groundedness | Recall@10 | Latenza p95 |
|------------------|-------|--------|--------------|-----------|-------------|
| codice_civile    | N     | N      | 0.NN         | 0.NN      | NNN ms      |
| ...              |       |        |              |           |             |

## Query con problemi

(lista di query con verdict BLOCK o error non None)
```

---

## 4. `scripts/verify_indexes.py`

### Scopo

Costruire gli indici BM25 + ChromaDB su un campione reale di 1000+ documenti da LegalAgentLab e verificarne la qualità con smoke test.

### CLI

```
python scripts/verify_indexes.py \
  --limit 1000 \
  --workspace verify_sample \
  --smoke-queries "responsabilità contrattuale" "locazione abitativa" "infortunio lavoro" \
  --output scripts/build_report.json
```

### Flusso

1. Connetti a LegalAgentLab MongoDB (READ-ONLY via `LegalAgentLabReader`)
2. Campiona `--limit` documenti da `normattiva_docs` (cursor con `limit()`)
3. Inserisci come chunks in `aiura_legal.chunks` (workspace `verify_sample`)
4. Istanzia `HybridRetriever` su workspace temporaneo → build BM25 + ChromaDB
5. Esegui smoke test: per ogni `--smoke-queries` chiama `retriever.build_research_packet()`
6. Calcola verdict: `OK` | `WARN` | `FAIL`
7. Scrivi `build_report.json`
8. Log summary su stdout
9. Exit `0` = OK/WARN, `1` = FAIL

### Schema `build_report.json`

```json
{
  "run_at": "2026-05-28T14:00:00Z",
  "workspace": "verify_sample",
  "docs_sampled": 1000,
  "chunks_inserted": 1000,
  "bm25_index_size_kb": 0,
  "chroma_collection_count": 0,
  "build_duration_s": 0.0,
  "smoke_tests": [
    {
      "query": "responsabilità contrattuale",
      "top1_source_id": "",
      "top1_score": 0.0,
      "result_count": 0,
      "latency_ms": 0
    }
  ],
  "verdict": "OK"
}
```

### Logica verdict

| Condizione | Verdict |
|---|---|
| Eccezione durante build o 0 chunks inseriti | `FAIL` |
| Almeno uno smoke test restituisce < 5 risultati | `WARN` |
| Tutti smoke test ≥ 5 risultati | `OK` |

---

## 5. README.md

### Struttura

```
# AiUra LegalLab
(3 righe: cosa fa, stack, Citation Contract)

## Requisiti
## Installazione
## Avvio rapido
## Esempi curl
  - GET /health
  - POST /ingest
  - POST /query
  - GET /workspace
## Eval
## Verifica indici
## Architettura (diagramma testuale ASCII)
## Troubleshooting
```

### Tabella Troubleshooting

| Problema | Causa | Soluzione |
|---|---|---|
| `503` su /query | Indici non costruiti | Eseguire `build_indexes.py` |
| Ollama timeout | Modello non caricato | `ollama pull qwen2.5:7b` |
| MongoDB ping failed | URI errato o `mongod` spento | Verificare `.env` |
| ChromaDB vuoto dopo build | LegalAgentLab DB non raggiungibile | Verificare `LEGALAGENTLAB_MONGODB_URI` |
| spaCy model missing | Download saltato | `python -m spacy download it_core_news_lg` |
| `422` su /query intent | Valore intent non valido | Valori: `norma_lookup`, `giurisprudenza`, `analisi_contratto`, `generic` |

---

## 6. File non modificati

I seguenti file esistenti NON vengono toccati da questa implementazione:

- `aiura_legal/` — tutta la logica applicativa
- `tests/` — suite esistente (120 test pass)
- `scripts/build_indexes.py` — usato da `verify_indexes.py` come libreria
- `BACKLOG.md` — aggiornato solo a fine implementazione

---

## 7. Aggiornamenti BACKLOG.md a fine implementazione

Marcare come `[x]`:
- `[P0] README installazione e primo utilizzo`
- `[P1] Eval script: groundedness, latenza, citation precision` (anticipato a M0)
- `[P1] Verifica build indici su campione reale (1000+ doc mirror)`
