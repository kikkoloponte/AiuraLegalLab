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
  collection chunks:       chunk indicizzati
    campo corpus: "normattiva" | "studio" | "giurisprudenza" | "dottrina"
      — normattiva:     norme da LegalAgentLab
      — studio:         documenti caricati dall'avvocato (atti, contratti)
      — giurisprudenza: sentenze caricate via /jurisprudence/upload
      — dottrina:       manuali, articoli accademici, commentari (/ingest?corpus=dottrina)
  collection jurisprudence: sentenze indicizzate
  collection ingestion_queue (nuovo):
    document_id, job_type, status, tier, priority, created_at
  collection pii_vault (nuovo):
    document_id, entity_map_encrypted, workspace, created_at

## Stack
- MongoDB + motor (async) — source of truth
- BM25 (rank_bm25) — indice file locale costruito da MongoDB
- Qdrant embedded — indice vector locale (sostituisce ChromaDB, 5-10x più veloce)
- NetworkX JSON — grafo legale
- LMStudio / Ollama — inferenza locale (configurabile da UI Settings)
- FastAPI 8765 — API locale per agenti
- Pi Skills (.pi/skills/) — 9 agenti legali (4 fasi Sequential IQRAC)

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

## Comandi
.venv\Scripts\activate
pip install -e ".[dev]"
python -m spacy download it_core_news_lg
pytest tests/ -v

# Indici
python scripts/build_indexes.py --workspace mio-studio          # normattiva + dottrina + studio
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo corte_cost

# Dottrina
python scripts/sync_dottrina.py --no-upload                     # scarica PDF open access
python scripts/upload_dottrina.py                               # carica PDF in API

# API e valutazione
python -m aiura_legal.api
python eval/run_eval.py

# Settings UI: http://localhost:5173/settings (cambio modello LLM senza riavvio manuale)

## Convenzioni
- Path Python: usa / anche su Windows
- Async ovunque: motor per MongoDB, httpx per HTTP
- Sync solo: script CLI e migration tools
- Test: mongomock-motor (zero MongoDB reale)
- PII nei test: solo dati sintetici (mai nomi/CF reali)
- Type hints: ovunque
- Log: loguru (mai print())
