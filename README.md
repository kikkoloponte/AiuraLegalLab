# AiUra LegalLab

Sistema multi-agente per ricerca e analisi legale con **Citation Contract**: ogni risposta cita esclusivamente fonti presenti nel Research Packet, verificate dal Reviewer (S5) prima di raggiungere l'avvocato. Inferenza LLM **interamente in locale** (Ollama / LM Studio) per garantire privacy e riservatezza dei dati dello studio.

**Stack:** MongoDB · BM25 per-corpus · Qdrant · Ollama / LM Studio · FastAPI 8765 · React · Pi Skills

📚 **Documentazione completa: [docs/README.md](docs/README.md)** — features, manuale operativo, setup knowledge base, design specs.

---

## Requisiti

| Componente | Versione minima | Note |
|---|---|---|
| Python | 3.11+ | testato su 3.11 e 3.12 |
| MongoDB | 6.0+ | locale o Atlas |
| Ollama **o** LM Studio | ultimo stabile | con un modello 7B+ scaricato (default `qwen2.5:7b`) |
| Node.js | 20+ | solo per il frontend React |
| RAM | 8 GB | Qdrant + sentence-transformer in memoria |
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
# Edita .env con i tuoi URI MongoDB e le impostazioni del backend LLM

# 5. Scarica il modello LLM (se non già presente)
ollama pull qwen2.5:7b          # oppure carica un modello in LM Studio

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

# Backend LLM: "ollama" oppure "lmstudio" (OpenAI-compatibile)
AIURA_LLM_BACKEND=lmstudio
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_MAIN=qwen2.5:7b
LMSTUDIO_BASE_URL=http://127.0.0.1:1234
LMSTUDIO_MODEL=qwen2.5-7b-instruct

# Qdrant (vuoto = embedded mode locale)
QDRANT_URL=http://localhost:6333

# PII Vault — obbligatoria in produzione (hex, 64 caratteri)
AIURA_PII_KEY=
```

Tutti i parametri LLM (backend, modello, temperatura, max token per fase, top-k retrieval) sono modificabili anche dalla **Settings UI** del frontend, con riavvio automatico dell'API.

---

## Avvio rapido

```bash
# API (porta 8765)
python -m aiura_legal.api

# oppure con uvicorn per il reload automatico in sviluppo
uvicorn aiura_legal.api.app:app --host 127.0.0.1 --port 8765 --reload

# Frontend React (porta 5173)
cd frontend && npm install && npm run dev
```

- Swagger UI: http://127.0.0.1:8765/docs
- Frontend: http://localhost:5173 (Chat, Documenti, Grafo, Storico, Settings, Wiki)

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
# Documento dello studio (default corpus=studio)
curl -X POST http://127.0.0.1:8765/ingest \
  -F "file=@contratto_locazione.pdf" \
  -F "workspace=mio-studio"

# Manuale o articolo accademico (corpus=dottrina)
curl -X POST http://127.0.0.1:8765/ingest \
  -F "file=@manuale_diritto_civile.pdf" \
  -F "workspace=mio-studio" \
  -F "corpus=dottrina"
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
# Risposta sincrona completa
curl -X POST http://127.0.0.1:8765/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Quali sono i requisiti di forma per la locazione ad uso abitativo?",
    "workspace": "mio-studio",
    "intent": "norma_lookup",
    "top_k": 10
  }'

# Sequential IQRAC con streaming SSE (una notifica per fase completata)
curl -N -X POST http://127.0.0.1:8765/query/stream \
  -H "Content-Type: application/json" \
  -d '{"query": "...", "workspace": "mio-studio", "intent": "fattispecie_analysis"}'
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

---

## Knowledge base

```bash
# Indici normattiva + dottrina + studio
python scripts/build_indexes.py --workspace mio-studio

# Giurisprudenza (Cassazione, TAR/CdS, Corte dei Conti)
python scripts/sync_jurisprudence.py --initial-load        # primo caricamento
python scripts/sync_jurisprudence.py                       # sync settimanale
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione

# Dottrina open access
python scripts/sync_dottrina.py --no-upload
python scripts/upload_dottrina.py
```

Guida completa (tempi, fonti, troubleshooting): [docs/KNOWLEDGE_BASE_SETUP.md](docs/KNOWLEDGE_BASE_SETUP.md)

---

## Eval — misura la qualità del retrieval

```bash
# Eval con file di default (tests/script_json/test_aiura_01.jsonl)
python eval/run_eval.py

# File custom
python eval/run_eval.py --queries path/to/queries.jsonl

# Filtra per modulo legislativo
python eval/run_eval.py --module cod_civ

# Suite completa 130 query su 6 domini
python scripts/run_query_suite.py
```

I report vengono scritti in `eval/results/` e `eval/query_results/` (gitignored):
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
Incoming file                       Fonti pubbliche
     │                                   │
     ▼                                   ▼
Tier1Pipeline                  sync_jurisprudence.py / sync_dottrina.py
  ├── DocumentExtractor          ├── Scrapers (Cassazione, TAR/CdS, C.Conti)
  ├── PII Anonymizer             └── JurisprudenceCoordinator
  ├── MongoDB documents                  │
  └── Chunker → chunks  (corpus=studio|dottrina)   chunks (corpus=giurisprudenza)
                         │
                         ▼
               build_indexes.py
                 ├── BM25Retriever   → indices/bm25_<corpus>.pkl  (per-corpus)
                 ├── VectorRetriever → Qdrant (embedded o server)
                 └── LegalGraphBuilder → graph.json (NetworkX)
                         │
                         ▼
POST /query  ·  POST /query/stream (SSE)
  └── S1 Clarifier → S2 HybridRetriever
       │
       ├─ percorso STANDARD (NORMA_LOOKUP, GIURISPRUDENZA_SEARCH)
       │    └── singolo round RRF → CrossEncoder → ResearchPacket
       │
       └─ percorso BIFASICO (FATTISPECIE_ANALYSIS, RISCHIO_CONTRATTUALE, …)
            ├── Round 1 — normativa  (BM25-heavy, corpus=normattiva)
            └── Round 2 — giurisprudenza (Vector-heavy, corpus=giurisprudenza)
                         │
                         ▼
              S3 Analyst — Sequential IQRAC (4 fasi, una chiamata LLM ciascuna)
                Fase 1 FRAMING        → RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE
                Fase 2 NORMATIVA      → FONTI_NORMATIVE, INTERPRETAZIONE   (re-query normattiva+dottrina)
                Fase 3 GIURISPRUDENZA → GIURISPRUDENZA                     (re-query giurisprudenza)
                Fase 4 SINTESI        → SUSSUNZIONE, OBIEZIONI, CONCLUSIONE
                         │
                         ▼
                S5 CitationReviewer
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
| S3 | Analyst | Ragionamento IQRAC 9-step in 4 fasi sequenziali (framing, normativa, giurisprudenza, sintesi) |
| S4 | Drafter | Generazione atti/pareri |
| S5 | Reviewer | Citation Contract enforcement |
| S6 | Annotator | Document Intelligence asincrona |

---

## Troubleshooting

| Problema | Causa probabile | Soluzione |
|---|---|---|
| `503` su `/query` | Indici non costruiti per il workspace | `python scripts/build_indexes.py --workspace <nome>` |
| `422` su `/query` — intent non valido | Valore `intent` non riconosciuto | Vedi tabella valori intent sopra |
| LLM timeout | Modello non caricato o GPU occupata | `ollama ps` / verifica LM Studio — modello caricato? |
| `MongoDB ping failed` | URI errato o `mongod` non avviato | Controlla `.env` + `mongod --version` |
| Qdrant vuoto dopo build | LegalAgentLab DB non raggiungibile | Verifica `LEGALAGENTLAB_MONGODB_URI` in `.env` |
| `spaCy model not found` | Download spaCy saltato | `python -m spacy download it_core_news_lg` |
| PII non anonimizzate | Testo < 50 caratteri o solo whitespace | Il layer 2 (spaCy) richiede testo di almeno una frase |
| `eval/run_eval.py` — API non raggiungibile | API spenta | `python -m aiura_legal.api` prima di lanciare l'eval |
| Round giurisprudenza vuoto negli intenti bifasici | Chunk indicizzati senza `corpus=giurisprudenza` | Re-indicizzare: `python scripts/build_jurisprudence_indexes.py` |
| Prima query lenta (~20s) | Cold start embeddings | Normale: il warm-up parte in background all'avvio API |

---

## Struttura directory

```
AiUraLegalLab/
├── aiura_legal/
│   ├── agents/          # Orchestrator, Analyst, Clarifier, Drafter, Annotator, client LLM
│   ├── api/             # FastAPI app, routers (jurisprudence, graph, settings), schemas
│   ├── core/
│   │   ├── anonymizer/  # PII Layer 1 (regex) + Layer 2 (spaCy)
│   │   ├── graph/       # LegalGraphBuilder, GraphRetriever
│   │   ├── retrieval/   # BM25 per-corpus, Qdrant, Reranker, Hybrid, PhaseRetriever
│   │   ├── reviewer/    # CitationReviewer (S5)
│   │   └── vault/       # PII Vault AES-256-GCM
│   ├── ingestion/       # extractor, chunker, Tier1Pipeline, watcher, normattiva/, dottrina/
│   ├── jurisprudence/   # scrapers, parser, coordinator, anonymizer bridge
│   ├── prassi/          # scraper Agenzia Entrate
│   ├── wiki/            # wiki auto-generata (store, writer, engine, lint)
│   └── workers/         # Tier 2 embed worker
├── frontend/            # React + TypeScript (Chat, Documents, Graph, History, Settings, Wiki)
├── eval/                # run_eval.py, run_bench.py, results/ (gitignored)
├── scripts/             # build_indexes, sync_*, mirror_normattiva, classify_knowledge_base, …
├── tests/               # 660+ test (mongomock-motor)
├── workspaces/          # dati runtime per-installazione (gitignored)
├── .pi/skills/          # prompt agenti Pi Skills
└── docs/                # documentazione (vedi docs/README.md)
```
