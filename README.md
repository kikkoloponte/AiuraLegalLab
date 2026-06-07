# AiUra LegalLab

Sistema multi-agente per ricerca e analisi legale con **Citation Contract**: ogni risposta cita esclusivamente fonti presenti nel Research Packet, verificate dal Reviewer (S5) prima di raggiungere l'avvocato.

**Stack:** MongoDB · BM25 · ChromaDB · Ollama (qwen2.5:7b) · FastAPI 8765 · 7 Pi Skills

---

## Requisiti

| Componente | Versione minima | Note |
|---|---|---|
| Python | 3.11+ | testato su 3.11 e 3.12 |
| MongoDB | 6.0+ | locale o Atlas |
| Ollama | ultimo stabile | con `qwen2.5:7b` scaricato |
| RAM | 8 GB | ChromaDB + sentence-transformer in memoria |
| LegalAgentLab | — | MongoDB `legal_lab.normattiva_docs` accessibile (READ-ONLY) |

---

## Installazione

```bash
# 1. Clona e crea il venv
git clone <repo>
cd AiUraLegalLab
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Installa le dipendenze
pip install -e ".[dev]"

# 3. Modello linguistico italiano per spaCy (PII anonymizer)
python -m spacy download it_core_news_lg

# 4. Configura l'ambiente
cp .env.example .env
# Edita .env con i tuoi URI MongoDB e le impostazioni Ollama

# 5. Scarica il modello LLM (se non già presente)
ollama pull qwen2.5:7b

# 6. Costruisci gli indici dal corpus LegalAgentLab
python scripts/build_indexes.py --workspace mio-studio
```

### Contenuto `.env`

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=aiura_legal_lab_db

# LegalAgentLab (READ-ONLY)
LEGALAGENTLAB_MONGODB_URI=mongodb://localhost:27017
LEGALAGENTLAB_MONGODB_DATABASE=legal_lab
LEGALAGENTLAB_CHUNKS_COLLECTION=normattiva_docs
LEGALAGENTLAB_TEXT_FIELD=text

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_MAIN=qwen2.5:7b
```

---

## Avvio rapido

```bash
# Avvia l'API (porta 8765)
python -m aiura_legal.api

# oppure con uvicorn per il reload automatico in sviluppo
uvicorn aiura_legal.api.app:app --host 127.0.0.1 --port 8765 --reload
```

Swagger UI disponibile su: http://127.0.0.1:8765/docs

---

## Esempi curl

### Health check

```bash
curl http://127.0.0.1:8765/health
```

```json
{"status": "ok", "mongodb": true, "ollama": true}
```

### Crea un workspace

```bash
curl -X POST http://127.0.0.1:8765/workspace/mio-studio
```

### Ingest documento

```bash
curl -X POST http://127.0.0.1:8765/ingest \
  -F "file=@contratto_locazione.pdf" \
  -F "workspace=mio-studio"
```

```json
{
  "document_id": "68...",
  "filename": "contratto_locazione.pdf",
  "workspace": "mio-studio",
  "status": "ok",
  "chunk_count": 12,
  "pii_stats": {"CF": 2, "EMAIL": 1}
}
```

### Query legale

```bash
curl -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quali sono i requisiti di forma per la locazione ad uso abitativo?",
    "workspace": "mio-studio",
    "intent": "norma_lookup",
    "top_k": 10
  }'
```

**Valori `intent` disponibili:**

| Valore | Retrieval | Ragionamento S3 |
|---|---|---|
| `norma_lookup` | Standard — BM25 dominante | IQRAC 9-step |
| `giurisprudenza_search` | Standard — Vector dominante | IQRAC 9-step |
| `fattispecie_analysis` | **Bifasico** — norme + giurisprudenza | IQRAC 9-step |
| `norma_evolution` | **Bifasico** — norme + giurisprudenza | IQRAC 9-step |
| `rischio_contrattuale` | **Bifasico** — norme + giurisprudenza | IQRAC 9-step |
| `precedente_interno` | **Bifasico** — norme + giurisprudenza | IQRAC 9-step |

Gli intenti **bifasici** eseguono due round di retrieval separati: prima recuperano
le fonti normative (BM25-heavy), poi le fonti giurisprudenziali (Vector-heavy).
S3 riceve le due sezioni distinte e ragiona nell'ordine corretto: norma → interpretazione → giurisprudenza.

### Lista workspace

```bash
curl http://127.0.0.1:8765/workspace
```

---

## Eval — misura la qualità del retrieval

```bash
# Eval con file di default (tests/script_json/test_aiura_01.jsonl)
python eval/run_eval.py

# File custom
python eval/run_eval.py --queries path/to/queries.jsonl

# Filtra per modulo legislativo
python eval/run_eval.py --module cod_civ

# Sovrascrive il workspace definito nel JSONL
python eval/run_eval.py --workspace normattiva
```

I report vengono scritti in `eval/results/`:
- `eval_<timestamp>.json` — dati completi
- `eval_<timestamp>.md`  — tabella summary per modulo

### Formato file JSONL

```jsonc
{
  "id": "cod_civ_001",
  "module": "cod_civ",
  "difficulty": "easy",
  "query": "Quali sono i presupposti per il risarcimento ex art. 1218 c.c.?",
  "workspace": "normattiva",
  "intent": "retrieval",
  "expected_source_ids": ["urn:nir:stato:regio.decreto:1942-03-16;262~art1218"]
}
```

**Valori `intent` nel JSONL** (mapping automatico verso i valori API):

| JSONL | API |
|---|---|
| `retrieval` | `norma_lookup` |
| `reasoning` | `fattispecie_analysis` |
| Tutti i valori API | pass-through |

---

## Verifica indici (campione 1000 doc)

```bash
# Build + smoke test su 1000 chunk da LegalAgentLab
python scripts/verify_indexes.py

# Campione più grande
python scripts/verify_indexes.py --limit 5000

# Query smoke personalizzate
python scripts/verify_indexes.py \
  --smoke-queries "responsabilità medica" "appalto pubblico" "successione testamentaria"
```

Produce `scripts/build_report.json` con verdict `OK` / `WARN` / `FAIL`.

---

## Test

```bash
# Suite completa (zero MongoDB reale — mongomock-motor)
pytest tests/ -v

# Solo un modulo
pytest tests/test_retrieval.py -v
```

---

## Architettura

```
Incoming file
     │
     ▼
Tier1Pipeline
  ├── DocumentExtractor  (PDF/DOCX/TXT)
  ├── PII Anonymizer     (regex + spaCy)
  ├── MongoDB documents
  └── Chunker  →  MongoDB chunks  (corpus="studio")
                         │
               Giurisprudenza (upload PDF sentenza)
                 └── JurisprudenceCoordinator → chunks (corpus="giurisprudenza")
                         │
                         ▼
               build_indexes.py
                 ├── BM25Retriever   → workspaces/<ws>/indices/bm25.pkl
                 └── VectorRetriever → workspaces/<ws>/indices/chromadb/
                         │
                         ▼
POST /query
  └── HybridRetriever
       │
       ├─ percorso STANDARD (NORMA_LOOKUP, GIURISPRUDENZA_SEARCH)
       │    └── singolo round RRF → CrossEncoder → ResearchPacket
       │
       └─ percorso BIFASICO (FATTISPECIE_ANALYSIS, RISCHIO_CONTRATTUALE, …)
            ├── Round 1 — normativa  (BM25-heavy, corpus=normattiva)
            └── Round 2 — giurisprudenza (Vector-heavy, corpus=giurisprudenza)
                 fonti normativa first → ResearchPacket (source_layer taggato)
                         │
                         ▼
                  AnalystAgent S3
                  schema IQRAC 9-step
                    RICOSTRUZIONE_FATTO → QUALIFICAZIONE → QUESTIONE
                    → FONTI_NORMATIVE → INTERPRETAZIONE → GIURISPRUDENZA
                    → SUSSUNZIONE → OBIEZIONI → CONCLUSIONE
                         │
                         ▼
                CitationReviewer S5
                  verdict: PASS / WARN / BLOCK
                         │
                         ▼
                  QueryResponse  →  avvocato
```

**Agenti Pi Skills** (`.pi/skills/`):

| ID | Nome | Ruolo |
|---|---|---|
| S0 | Supervisor | Routing e orchestrazione |
| S1 | Clarifier | Chiarimento query (max 2 turni) |
| S2 | Researcher | Retrieval bifasico — Research Packet con layer normativa/giurisprudenza |
| S3 | Analyst | Ragionamento IQRAC 9-step (metodologia giuridica italiana) |
| S4 | Drafter | Generazione atti/pareri |
| S5 | Reviewer | Citation Contract enforcement |
| S6 | Annotator | Document Intelligence asincrona |

---

## Troubleshooting

| Problema | Causa probabile | Soluzione |
|---|---|---|
| `503` su `/query` | Indici non costruiti per il workspace | `python scripts/build_indexes.py --workspace <nome>` |
| `422` su `/query` — intent non valido | Valore `intent` non riconosciuto | Vedi tabella valori intent sopra |
| Ollama timeout (120s) | Modello non caricato o GPU occupata | `ollama pull qwen2.5:7b` — verifica `ollama ps` |
| `MongoDB ping failed` | URI errato o `mongod` non avviato | Controlla `.env` + `mongod --version` |
| ChromaDB vuoto dopo build | LegalAgentLab DB non raggiungibile | Verifica `LEGALAGENTLAB_MONGODB_URI` in `.env` |
| `spaCy model not found` | Download spaCy saltato | `python -m spacy download it_core_news_lg` |
| PII non anonimizzate | Testo < 50 caratteri o solo whitespace | Il layer 2 (spaCy) richiede testo di almeno una frase |
| `eval/run_eval.py` — API non raggiungibile | API spenta | `python -m aiura_legal.api` prima di lanciare l'eval |
| Round giurisprudenza vuoto negli intenti bifasici | Chunk indicizzati prima della v2 (senza `corpus=giurisprudenza`) | Re-indicizzare: `python scripts/build_indexes.py --workspace <nome>` |

---

## Struttura directory

```
AiUraLegalLab/
├── aiura_legal/
│   ├── agents/          # OllamaClient
│   ├── api/             # FastAPI app, schemas
│   ├── core/
│   │   ├── anonymizer/  # PII Layer 1+2
│   │   ├── retrieval/   # BM25, Vector, Reranker, Hybrid
│   │   └── reviewer/    # CitationReviewer
│   ├── ingestion/
│   │   ├── mongodb/     # client, models
│   │   ├── extractor.py
│   │   ├── chunker.py
│   │   ├── pipeline.py
│   │   └── watcher.py
│   └── core/types.py
├── eval/
│   ├── evaluator.py     # metriche core
│   ├── run_eval.py      # CLI runner
│   └── results/         # output JSON + Markdown
├── scripts/
│   ├── build_indexes.py
│   └── verify_indexes.py
├── tests/
│   └── script_json/     # file JSONL per l'eval
├── workspaces/          # indici BM25 + ChromaDB per workspace
├── .pi/skills/          # 7 agenti Pi Skills
└── docs/
```
