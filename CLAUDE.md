# CLAUDE.md — AiUra LegalLab
# C:\project\AiUraLegalLab

## Cosa è questo progetto
Estensione di LegalAgentLab con architettura multi-agente, retrieval
ibrido e Citation Contract. MongoDB è lo storage primario, compatibile
con il database del progetto precedente.

## Progetto sorgente
C:\project\LegalAgentLab
  - Ha già documenti legali scaricati in MongoDB (legal_lab.normattiva_docs)
  - È READ-ONLY per noi: non modificare mai il suo database
  - Usiamo i suoi dati per costruire gli indici BM25/vector

## Schema MongoDB (da LegalAgentLab — aggiorna se diverso)
DATABASE:  legal_lab  (LegalAgentLab, read-only)
  collection normattiva_docs:
    _id:          ObjectId
    text:         string  (campo principale — articolo normativo)
    source_id:    string  (default: "normattiva_it")
    urn:          string  (URN univoco, es. "urn:nir:stato:legge:...")
    titolo:       string
    titolo_articolo: string
    articolo_num: string  (es. "Art. 1")
    testo_tipo:   string  ("normativo"|"formula"|"formula_ridondante"|"formula_unica")

DATABASE:  aiura_legal_lab_db  (AiUraLegalLab, scrive)
  collection documents:    documenti avvocato (post-ingestione)
    ⚠️ is_chunked=True non garantisce chunk indicizzati: 1061 documenti
       studio marcati chunkati ma 0 chunk corpus=studio in KB (verificato
       2026-07-03, vedi docs/wiki/05-backlog.md DT-7)
  collection chunks:       chunk indicizzati
    campo corpus: "normattiva" | "studio" | "giurisprudenza" | "dottrina" | "prassi" | "massimario"
      — normattiva:     norme da LegalAgentLab
      — studio:         documenti caricati dall'avvocato (atti, contratti)
      — giurisprudenza: sentenze caricate via /jurisprudence/upload
      — dottrina:       manuali, articoli accademici, commentari (/ingest?corpus=dottrina)
      — prassi:         circolari/risoluzioni Agenzia Entrate (aiura_legal/prassi/)
      — massimario:     massime Ufficio del Massimario Cassazione (scripts/sync_massimario.py)
  collection jurisprudence: sentenze indicizzate
  collection istituti_giuridici: schede istituto CRUD (193 mappate) — sincronizzate
    non distruttivamente in aiura_legal/core/istituti/registry.yaml via
    scripts/sync_istituti_registry.py (vedi sezione Istituti/Questioni sotto)
  collection wiki_pages:    pagine wiki auto-generate (WikiEngine, aiura_legal/wiki/)
  collection ingestion_queue (nuovo):
    document_id, job_type, status, tier, priority, created_at
  collection pii_vault (nuovo):
    document_id, entity_map_encrypted, workspace, created_at

FILE (non MongoDB):
  ontology/legal_kb_ontology.ttl    — schema RDF/OWL, classi/relazioni astratte
  ontology/questioni_curate.yaml    — QuestioneGiuridica curate (vedi sezione sotto)
  workspaces/mio-studio/indices/graph.json  — grafo legale norma↔norma (RINVIA/ABROGA/MODIFICA)
  workspaces/jurisprudence_graph.json       — grafo sentenza↔norma

## Stack
- MongoDB + motor (async) — source of truth
- BM25 (rank_bm25) — indice file locale costruito da MongoDB
- Qdrant embedded — indice vector locale (sostituisce ChromaDB, 5-10x più veloce)
- NetworkX JSON — grafo legale
- LMStudio / Ollama — inferenza locale (configurabile da UI Settings)
- FastAPI 8765 — API locale per agenti
- Pi Skills (.pi/skills/) — 9 agenti legali (4 fasi Sequential IQRAC)
- React (porta 5173) — pagine: Chat, Dashboard, Documents, Graph, History,
  Settings, Wiki, Istituti, Questioni

## Architettura agenti (S0–S6)
Ogni agente ha una classe in aiura_legal/agents/ (S0/S2/S5 non sono LLM) +
skill prompt in .pi/skills/. Catena orchestrata da LegalOrchestrator
(aiura_legal/agents/orchestrator.py).

  S0  Supervisor   routing su QueryIntent, programmatico, zero LLM
  S1  Clarifier    ClarifierAgent (clarifier.py) — max 2 turni, disambiguazione
                    multi-scelta quando la query tocca istituti disambigua_da
  S2  Researcher   HybridRetriever + PhaseRetriever (core/retrieval/) — retrieval,
                    non un agente LLM
  S3  Analyst      AnalystAgent (analyst.py) — Sequential IQRAC 4 fasi (sotto).
                    QueryTypeClassifier (query_classifier.py) classifica
                    "case" vs "doctrine" prima della Fase 1
  S4  Drafter      DrafterAgent (drafter.py) — genera atti/pareri dal Research Packet
  S5  Reviewer     CitationReviewer (core/reviewer/reviewer.py) — rule-based, zero LLM
  S6  Annotator    AnnotatorAgent (annotator.py) — Document Intelligence asincrona

Backend LLM intercambiabile: OllamaClient / OpenAICompatClient (agents/),
stessa interfaccia, switch da Settings UI senza riavvio.

## Principio fondamentale: Citation Contract
Ogni risposta legale cita SOLO fonti nel Research Packet.
Il Reviewer (S5) blocca citazioni non grounded prima che
raggiungano l'avvocato. Nessuna eccezione.

## Ragionamento Sequential IQRAC (S3)
S3 usa il metodo giuridico italiano in 9 step divisi in 4 fasi sequenziali.
Ogni fase è una chiamata LLM separata con retrieval mirato — niente monoblocco.

  Fase 1 — FRAMING      (step 1-3): RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE
    → distilla la QUESTIONE giuridica precisa per guidare il retrieval successivo

  Fase 2 — NORMATIVA    (step 4-5): FONTI_NORMATIVE, INTERPRETAZIONE
    → re-query su corpus=normattiva + corpus=dottrina con la QUESTIONE di Fase 1

  Fase 3 — GIURISPRUDENZA (step 6): GIURISPRUDENZA
    → re-query su corpus=giurisprudenza con QUALIFICAZIONE+QUESTIONE

  Fase 4 — SINTESI       (step 7-9): SUSSUNZIONE, OBIEZIONI, CONCLUSIONE
    → ragiona sull'output delle fasi 1-3, nessun nuovo retrieval

Il frontend riceve ogni fase via SSE man mano che viene completata (POST /query/stream).
La norma è fondamento (Fase 2), la giurisprudenza è supporto (Fase 3). Mai invertire.
La dottrina (Fase 2) supporta l'INTERPRETAZIONE con riferimenti accademici.

## Istituti Giuridici e Questioni (ontologia) — alimentano la Fase 1 di S3
Due strati concettuali distinti sopra il retrieval grezzo, entrambi con CRUD UI:

- **Istituti Giuridici** (collection `istituti_giuridici`, 193 mappate su 4
  codici maggiori + 11 leggi complementari): schede per istituto (norme
  cardine, sentenze pilota, `disambigua_da`). CRUD via
  `aiura_legal/api/istituti_router.py` + frontend `/istituti`. Sincronizzate
  non distruttivamente in `registry.yaml` (`scripts/sync_istituti_registry.py`
  — preserva le voci curate a mano). Classificazione istituto in Fase 1:
  match lessicale primario → fallback LLM sull'`istituto_id` già prodotto
  nella stessa chiamata (nessuna chiamata extra) → match semantico via
  embedding SOLO come segnale secondario per il Clarifier (soglia 0.85, mai
  come classificatore primario — troppi falsi positivi cross-settore
  testati e scartati). ⚠️ Gap noto: 0/193 istituti sul settore "lavoro".
- **Questioni Giuridiche** (`ontology/legal_kb_ontology.ttl` +
  `ontology/questioni_curate.yaml`): livello ontologico separato
  (`QuestioneGiuridica`). `QuestioniRegistry`
  (`core/graph/questioni_registry.py`) per la UI di revisione (vede tutte
  le voci, optimistic concurrency); `QuestioneLoader`
  (`core/graph/questione_loader.py`) legge solo le voci approvate e scrive
  nel grafo legale. CRUD via `questioni_router.py` + frontend `/questioni`.
  Spec: `docs/superpowers/specs/2026-06-26-questioni-review-ui-design.md`.

## Retrieval trifasico per fase (S2 + PhaseRetriever)
S2 esegue il retrieval iniziale bifasico (normattiva + giurisprudenza).
PhaseRetriever esegue re-query mirate dopo Fase 1:
  Fase 2: corpus=normattiva (BM25-heavy 0.65/0.20/0.15) + corpus=dottrina (0.40/0.50/0.10)
  Fase 3: corpus=giurisprudenza (Vector-heavy 0.15/0.75/0.10)

I chunk DEVONO avere corpus corretto:
  normattiva:     impostato da mirror_normattiva/build_indexes
  giurisprudenza: impostato da JurisprudenceCoordinator
  dottrina:       impostato da Tier1Pipeline(corpus="dottrina") — POST /ingest
  studio:         impostato da Tier1Pipeline(corpus="studio") — POST /ingest (default)
  prassi:         impostato da prassi/coordinator.py
  massimario:     impostato da scripts/sync_massimario.py

Componenti concreti dietro il retrieval:
  HybridRetriever    (core/retrieval/hybrid_retriever.py) — orchestratore bifasico
  BM25Retriever      (core/retrieval/bm25_retriever.py)   — pkl separato per corpus
  VectorRetrieverV2  (core/retrieval/vector_retriever.py) — Qdrant embedded/server
  GraphRetriever     (core/graph/retriever.py)            — neighbor expansion + conflict
                       detection. ⚠️ NON applica il filtro settore (rumore cross-settore noto)
  reranker.py        — CrossEncoder finale + _settore_boost() (soft boost per settore)
  settori.py         — classify_query()/classify_keywords(), classificatore settore zero-LLM
  ContextBudgetManager (core/retrieval/context_budget.py) — esiste, testato, NON collegato:
                       l'LLM vede oggi solo ~300-400 caratteri per fonte, non il contesto pieno

## Privacy e PII
- LegalAnonymizer (core/anonymizer/anonymizer.py): regex (CF, P.IVA, IBAN,
  email, telefono) + spaCy NER italiano a 2 layer, whitelist che protegge i
  riferimenti normativi/giurisprudenziali dall'anonimizzazione.
- PiiVault (core/vault/vault.py): entity map cifrata AES-256-GCM, chiave da
  AIURA_PII_KEY, storage isolato per workspace.
- ⚠️ Wiring incompleto in alcuni percorsi (es. ingest studio usa
  `use_spacy=False`, entity map giurisprudenza salvata in chiaro) — vedi
  roadmap hardening in docs/FEATURES.md.

## Comandi
.venv\Scripts\activate
pip install -e ".[dev]"
python -m spacy download it_core_news_lg
pytest tests/ -v

# Indici
python scripts/build_indexes.py --workspace mio-studio          # normattiva + dottrina + studio
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo corte_cost

# Dottrina / prassi / massimario
python scripts/sync_dottrina.py --no-upload                     # scarica PDF open access
python scripts/upload_dottrina.py                               # carica PDF in API
python scripts/sync_prassi.py                                   # circolari/risoluzioni Agenzia Entrate
python scripts/sync_massimario.py                                # massime Ufficio del Massimario

# Istituti Giuridici e grafo
python scripts/sync_istituti_registry.py                        # MongoDB → registry.yaml (merge non distruttivo)
python scripts/build_graph.py --rebuild                         # grafo legale norma↔norma
python scripts/build_jurisprudence_graph.py --rebuild            # grafo sentenza↔norma

# API e valutazione
python -m aiura_legal.api
python eval/run_eval.py
python scripts/run_query_suite.py                                # query suite multi-dominio

# Settings UI: http://localhost:5173/settings (cambio modello LLM senza riavvio manuale)

## Convenzioni
- Path Python: usa / anche su Windows
- Async ovunque: motor per MongoDB, httpx per HTTP
- Sync solo: script CLI e migration tools
- Test: mongomock-motor (zero MongoDB reale)
- PII nei test: solo dati sintetici (mai nomi/CF reali)
- Type hints: ovunque
- Log: loguru (mai print())
