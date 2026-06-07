# Architettura di sistema — AiUra LegalLab

## Panoramica

AiUra LegalLab è un sistema **multi-agente per la ricerca e l'analisi legale** con
Citation Contract garantito. L'obiettivo è supportare l'avvocato nella ricerca normativa
e giurisprudenziale, nell'analisi di fattispecie e nella redazione di atti, assicurando
che ogni affermazione sia grounded in una fonte verificata.

Il sistema è strutturato in tre strati:

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT / FRONTEND                    │
│           (Swagger UI oggi, React in roadmap)           │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP REST
┌────────────────────────▼────────────────────────────────┐
│              FASTAPI  :8765  (aiura_legal.api)          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │  S0  │ │  S1  │ │  S2  │ │  S3  │ │  S4  │ │  S5  ││
│  │Route │→│Clarif│→│Retrv │→│Analy │→│Draft │→│Revw  ││
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘│
│                                              ┌──────┐  │
│                                              │  S6  │  │
│                                              │Annot │  │
│                           Wiki layer (async) └──────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   KNOWLEDGE BASE                        │
│  MongoDB: aiura_legal_lab_db                            │
│  ├── normattiva_docs    (166.822 articoli)              │
│  ├── jurisprudence      (316.889 sentenze)              │
│  ├── documents          (documenti studio)              │
│  ├── chunks             (chunk studio indicizzati)      │
│  ├── wiki_pages         (risposte archiviate)           │
│  └── sync_state         (cursori last_sync)             │
│                                                         │
│  Indici locali (workspaces/mio-studio/)                 │
│  ├── indices/bm25.pkl         (~700 MB)                 │
│  ├── indices/qdrant/          (Qdrant embedded)         │
│  └── jurisprudence_graph.json (grafo NetworkX)          │
└─────────────────────────────────────────────────────────┘
```

---

## Agenti (S0–S6)

### S0 — Router (programmatico)

Classifica l'intent della query senza LLM, in base a pattern lessicali.

| Intent | Trigger | Pesi retrieval |
|--------|---------|----------------|
| `NORMA_LOOKUP` | "art.", "D.Lgs.", "legge n." | BM25 60% / Vector 30% / Graph 10% |
| `GIURISPRUDENZA_SEARCH` | "sentenza", "Cassazione", "TAR" | BM25 20% / Vector 70% / Graph 10% |
| `FATTISPECIE_ANALYSIS` | "caso", "fattispecie", "responsabilità" | BM25 40% / Vector 50% / Graph 10% |
| `REDAZIONE_ATTO` | "redigi", "bozza", "atto" | BM25 50% / Vector 40% / Graph 10% |

### S1 — Clarifier

Se la query è ambigua, genera una domanda di chiarimento prima di procedere.
Attivato solo se `clarification_turn=0` e la query è sotto-specificata.

### S2 — HybridRetriever + PhaseRetriever

Il cuore del retrieval. Combina tre segnali con **Reciprocal Rank Fusion (RRF)**:

1. **BM25** (rank_bm25) — ricerca keyword su testo lemmatizzato
2. **Vector** (Qdrant + sentence-transformers MiniLM-L12) — ricerca semantica
3. **Graph** (NetworkX) — traversal sentenza→norma→sentenza correlata

Poi applica un **CrossEncoder** (ms-marco-MiniLM-L-6-v2) per il reranking finale.
Ritorna un `ResearchPacket` con le top-k fonti più rilevanti.

Il **PhaseRetriever** esegue re-query mirate tra le fasi del Sequential IQRAC:
- Dopo Fase 1: re-query `normattiva` + `dottrina` con la QUESTIONE distillata
- Dopo Fase 2: re-query `giurisprudenza` con QUALIFICAZIONE+QUESTIONE

### S3 — Sequential Analyst (4 fasi + SSE streaming)

Genera la risposta IQRAC in **4 chiamate LLM sequenziali**, una per fase,
invece di un unico prompt monoblocco. Ogni fase riceve il contesto delle fasi
precedenti e fonti recuperate ad hoc.

| Fase | Step IQRAC | Retrieval |
|------|-----------|-----------|
| 1 — Framing | RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE | Nessuno |
| 2 — Normativa | FONTI_NORMATIVE, INTERPRETAZIONE | normattiva + dottrina |
| 3 — Giurisprudenza | GIURISPRUDENZA | giurisprudenza |
| 4 — Sintesi | SUSSUNZIONE, OBIEZIONI, CONCLUSIONE | Nessuno |

Il frontend riceve ogni fase via **SSE** (`POST /query/stream`) man mano che viene completata.
Il vecchio endpoint `POST /query` (risposta bloccante) rimane disponibile.

### S4 — Drafter

Su richiesta esplicita (`draft_type`), genera atti legali strutturati:
ricorso, parere, contratto, lettera diffida. Usa il Research Packet come base.

### S5 — CitationReviewer (Citation Contract)

**Componente critico** — verifica che ogni citazione nella risposta sia presente
nel Research Packet. Se trova un URN/ID non grounded → `FAIL → RE_RETRIEVAL`.

```
PASS → DELIVER      citazioni tutte verificate
FAIL → RE_RETRIEVAL citazione non trovata nel packet (possibile allucinazione)
```

Il Reviewer estende il controllo anche alla giurisprudenza:
verifica gli hex ID delle sentenze (pattern `[0-9a-f]{16}`) e i link norma
tramite il grafo sentenza→norma.

### S6 — Annotator (Document Intelligence)

Analisi asincrona di un documento già ingerito:
- Divide il testo in sezioni
- Per ciascuna: recupera fonti rilevanti (S2) e genera annotazioni LLM
- Classifica il rischio per sezione: NESSUNO / BASSO / MEDIO / ALTO / CRITICO
- Suggerisce sostituzioni grounded

---

## Flussi principali

### Workflow A — Query legale (Sequential IQRAC con SSE)

```
POST /query/stream  ← raccomandato (SSE progressivo)
  │
  ├─ S0 Router → classifica intent
  ├─ S1 Clarifier → (opzionale) richiede chiarimenti     [event: clarification_needed]
  ├─ S2 HybridRetriever → BM25 + Qdrant + CrossEncoder   [event: retrieval_done]
  ├─ S3 Fase 1 Framing → RICOSTRUZIONE, QUALIFICAZIONE, QUESTIONE   [event: phase_complete]
  │      └─ PhaseRetriever → re-query normattiva + dottrina
  ├─ S3 Fase 2 Normativa → FONTI_NORMATIVE, INTERPRETAZIONE         [event: phase_complete]
  │      └─ PhaseRetriever → re-query giurisprudenza
  ├─ S3 Fase 3 Giurisprudenza → GIURISPRUDENZA                      [event: phase_complete]
  ├─ S3 Fase 4 Sintesi → SUSSUNZIONE, OBIEZIONI, CONCLUSIONE        [event: phase_complete]
  ├─ S5 CitationReviewer → verifica grounding → PASS/FAIL           [event: review_done]
  └─ Wiki layer (async) → archivia se PASS

POST /query  ← backward compat (risposta bloccante completa)
```

Tempo tipico: 3–8 minuti con LLM 14B locale (4 fasi sequenziali).

### Workflow B — Documento studio

```
POST /ingest (upload PDF/DOCX/TXT)
  │
  ├─ DocumentExtractor → estrae testo raw
  ├─ LegalAnonymizer (spaCy) → sostituisce PII con placeholder
  ├─ MongoDB.documents → salva testo anonimizzato
  ├─ MongoDB.pii_vault → salva entity_map cifrata AES
  ├─ Chunker (sliding window) → genera chunk
  └─ MongoDB.chunks → salva chunk

POST /annotate/{document_id}  (asincrono → 202 Accepted)
  │
  ├─ S2 retrieval → fonti rilevanti per il documento
  ├─ S6 Annotator (LLM) → analisi per sezione
  └─ MongoDB.annotations → salva risultato

GET /annotate/{document_id}   → recupera risultato (queued/completed/error)
```

---

## Stack tecnologico

| Layer | Tecnologia | Versione |
|-------|-----------|---------|
| API | FastAPI + Uvicorn | ≥0.111 |
| Database | MongoDB + Motor (async) | ≥6.0 / ≥3.4 |
| BM25 | rank_bm25 | ≥0.2.2 |
| Vector DB | Qdrant (embedded) | ≥1.9.0 |
| Embeddings | sentence-transformers | ≥3.0.0 |
| CrossEncoder | ms-marco-MiniLM-L-6-v2 | HuggingFace |
| Grafo | NetworkX (JSON) | ≥3.3 |
| NLP/PII | spaCy it_core_news_lg | ≥3.7.0 |
| LLM | Ollama qwen2.5:7b / LMStudio | locale |
| Scraping | httpx + Playwright | async |
| PDF parsing | pdfminer.six + pdfplumber | — |
| Crittografia | cryptography (AES) | ≥42.0.0 |

---

## Struttura directory

```
C:\project\AiUraLegalLab\
├── aiura_legal/
│   ├── agents/          # S0-S6: orchestrator, analyst, drafter, annotator...
│   ├── api/             # FastAPI app, router, schemas
│   ├── core/
│   │   ├── retrieval/   # HybridRetriever, BM25, Vector, CrossEncoder
│   │   ├── reviewer/    # CitationReviewer (S5)
│   │   ├── types.py     # QueryIntent, ResearchPacket, SearchResult...
│   │   └── graph/       # LegalGraphBuilder
│   ├── ingestion/       # Tier1Pipeline, Chunker, Extractor
│   ├── jurisprudence/   # Scrapers, Parser, Coordinator, GraphBuilder
│   ├── wiki/            # WikiEngine, WikiStore, WikiWriter
│   └── core/vault/      # PII Vault, LegalAnonymizer
├── scripts/             # CLI: sync, build_indexes, build_graph, visualize...
├── workspaces/
│   └── mio-studio/
│       └── indices/
│           ├── bm25.pkl
│           ├── bm25_meta.json
│           └── qdrant/
├── workspaces/
│   └── jurisprudence_graph.json
├── docs/
│   └── wiki/            # questa documentazione
├── tests/
├── .env
└── pyproject.toml
```
