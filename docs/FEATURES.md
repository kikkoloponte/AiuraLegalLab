# AiUra LegalLab — Features

> Stato al 2026-07-03 (aggiornato da 2026-06-10). Documento di riferimento per
> le funzionalità implementate e per la roadmap futura. Per l'installazione
> vedi [README.md](../README.md), per il backlog operativo dettagliato vedi
> [BACKLOG.md](../BACKLOG.md).
>
> **Novità principale dall'ultimo aggiornamento**: mappatura sistematica di
> **193 istituti giuridici** con CRUD UI dedicata (sezione 15, non presente
> nella versione precedente di questo documento), 3 nuove leggi scaricate,
> fix strutturali al filtro settore nel retrieval. Numeri di questo documento
> verificati contro MongoDB il 2026-07-03, non riportati da memoria.

## Visione

Laboratorio di assistenza per studi legali italiani basato su **LLM in locale**
(Ollama / LM Studio): nessun dato del cliente lascia la macchina dello studio.
Tre principi fondanti:

1. **Citation Contract** — ogni risposta cita solo fonti presenti nel Research
   Packet, verificate meccanicamente dal Reviewer prima di raggiungere l'avvocato.
2. **Metodo giuridico italiano** — il ragionamento segue lo schema IQRAC in 9
   step: la norma è fondamento, la giurisprudenza è supporto, mai il contrario.
3. **Privacy by design** — anonimizzazione PII in ingestione, entity map cifrata
   (AES-256-GCM), inferenza esclusivamente locale.

---

## Features implementate

### 1. Architettura multi-agente (S0–S6)

Catena orchestrata da `LegalOrchestrator` ([orchestrator.py](../aiura_legal/agents/orchestrator.py)),
con prompt definiti come Pi Skills in `.pi/skills/`:

| ID | Agente | Ruolo | Stato |
|----|--------|-------|-------|
| S0 | Supervisor | Routing intent (programmatico, zero LLM) | ✅ |
| S1 | Clarifier | Valuta ambiguità query, max 2 turni di chiarimento | ✅ |
| S2 | Researcher | Retrieval ibrido bifasico → Research Packet | ✅ |
| S3 | Analyst | Ragionamento IQRAC 9-step (Sequential a 4 fasi) | ✅ |
| S4 | Drafter | Generazione atti e pareri dal Research Packet | ✅ |
| S5 | Reviewer | Citation Contract enforcement (rule-based, zero LLM) | ✅ |
| S6 | Annotator | Document Intelligence asincrona su documenti ingeriti | ✅ |

Graceful degradation ovunque: se l'LLM non è raggiungibile la catena restituisce
comunque il Research Packet (`llm_available=false`), mai eccezioni verso l'utente.

### 2. Sequential IQRAC con streaming SSE

Il ragionamento S3 non è un monoblocco: 4 chiamate LLM separate, ognuna con
retrieval mirato, trasmesse al frontend man mano che completano
(`POST /query/stream`):

1. **FRAMING** (step 1-3) — ricostruzione fatto, qualificazione, questione
   giuridica. Distilla la QUESTIONE che guida il retrieval delle fasi successive.
2. **NORMATIVA** (step 4-5) — re-query su `corpus=normattiva` (BM25-heavy) +
   `corpus=dottrina` per l'interpretazione.
3. **GIURISPRUDENZA** (step 6) — re-query su `corpus=giurisprudenza`
   (Vector-heavy) con qualificazione + questione.
4. **SINTESI** (step 7-9) — sussunzione, obiezioni, conclusione. Nessun nuovo
   retrieval.

Il `PhaseRetriever` ([phase_retriever.py](../aiura_legal/core/retrieval/phase_retriever.py))
esegue le re-query per fase con pesi e filtri corpus dedicati, incluso il filtro
soft/hard per settore giuridico (penale | civile | amministrativo | lavoro | tributario)
estratto dalla Fase 1.

### 3. Retrieval ibrido trifasico

- **BM25 per-corpus** ([bm25_retriever.py](../aiura_legal/core/retrieval/bm25_retriever.py)) —
  un indice pkl separato per corpus (`bm25_normattiva.pkl`, `bm25_dottrina.pkl`,
  `bm25_studio.pkl`, `bm25_giurisprudenza.pkl`): aggiornare la dottrina non
  ricostruisce normattiva. Migrazione automatica dal pkl monolitico legacy.
  Filtri vettorizzati numpy su corpus/fonte/testo_tipo.
- **Vector search con Qdrant** ([vector_retriever.py](../aiura_legal/core/retrieval/vector_retriever.py)) —
  embedded o server mode (`QDRANT_URL`), indicizzazione incrementale.
  Ha sostituito ChromaDB (5-10× più veloce).
- **Graph expansion** — espansione dei vicini sul grafo legale (RINVIA /
  ABROGA / MODIFICA) con filtro di vigenza temporale `valid_on`.
- **Fusione RRF pesata** per intent (es. `norma_lookup` BM25-heavy,
  `giurisprudenza_search` Vector-heavy) + reranking **CrossEncoder** finale.
- **Retrieval bifasico** per gli intent di analisi: round normativa
  (0.65/0.20/0.15) e round giurisprudenza (0.15/0.75/0.10) in parallelo,
  fonti taggate per `source_layer`.

### 4. Citation Contract (S5 Reviewer)

[reviewer.py](../aiura_legal/core/reviewer/reviewer.py) — interamente rule-based:

- **Citation grounding**: ogni source_id citato deve esistere nel Packet,
  altrimenti `FAIL` → azione `RE_RETRIEVAL`.
- **Grounding giurisprudenziale**: gli ID sentenza (hash hex) citati devono
  essere nel Packet.
- **Vigenza temporale**: warning su norme scadute rispetto a `valid_on`.
- **Conflict disclosure**: warning su norme in conflitto/abrogazione via grafo.
- **Incostituzionalità**: citare come vigente una norma `INCOSTITUZIONALE` è
  FAIL CRITICO → azione `BLOCK` (la risposta non raggiunge l'avvocato).

### 5. Knowledge base normativa

- Mirror da LegalAgentLab (`legal_lab.normattiva_docs`, read-only) +
  fetch diretto da Normattiva con fallback automatico N2Ls per gli HTTP 500
  ([connector.py](../aiura_legal/ingestion/normattiva/connector.py)).
- Corpus attuale: **170.857 documenti** in `normattiva_docs` (verificato
  2026-07-03), **453.458 chunk** `corpus=normattiva` — Codici (CC, CP, CPC,
  CPP), Costituzione, TUIR, IVA, Codice Ambiente, T.U. Sicurezza, Privacy,
  statuto lavoratori/contribuente, e altri atti mirati + base completa da
  LegalAgentLab.
- **Aggiunte 2026-07-03**: Codice dei Contratti Pubblici 2023 (D.Lgs.
  36/2023, sostituisce il D.Lgs. 50/2016 abrogato già in KB), Legge
  Fallimentare previgente (R.D. 267/1942), Codice della Navigazione (R.D.
  327/1942) — 2.226 articoli, 3.591 chunk totali.
- Parser AKN per vigenza e abrogazioni ([akn_parser.py](../aiura_legal/ingestion/normattiva/akn_parser.py)).
- Classificazione per settore giuridico della KB
  ([classify_knowledge_base.py](../scripts/classify_knowledge_base.py)):
  pre-classificazione keyword + batch LLM con checkpoint/resume.
- Recall sulla query suite (gate Fase 2+3, 2026-06-17): **G=0.780 R=0.767,
  pass 100% (20/20)** — superata la misura R=0.721 precedente, non ancora
  rimisurata dopo le aggiunte del 3 luglio.
- **Gap noto**: nessun istituto giuridico (vedi §15) è mappato sul settore
  "lavoro" (0/193) — coerente con l'assenza di un dominio "lavoro" anche
  nella query suite di valutazione (`eval/`, domini disponibili:
  `amm, civ, cross, pen, trib`). La normativa di base (Statuto Lavoratori
  e altre leggi lavoristiche) non è confermata presente in KB — da
  verificare prima di assumere sia solo un gap di mappatura istituti.

### 6. Pipeline giurisprudenza

Scraper, parser, anonymizer bridge e coordinator dedicati
([jurisprudence/](../aiura_legal/jurisprudence/)). Sync batch:
`scripts/sync_jurisprudence.py` (`--initial-load` per il primo caricamento,
default ultimi 7 giorni).

| Fonte | Meccanismo | Sentenze in KB | Stato |
|-------|-----------|----------------|-------|
| Cassazione | API Solr diretta (httpx, no browser) | ~249.500 | ✅ |
| TAR | OpenGA CKAN API (`import_openga.py`) | ~30.100 | ✅ |
| Consiglio di Stato | OpenGA CKAN API | ~14.700 | ✅ |
| Corte Costituzionale | Open data ZIP, 1956–oggi (`import_corte_cost.py`) | ~22.300 | ✅ |
| Corte dei Conti | API CdcWebApi | ~270 | ✅ |

Totale: **~316.900 sentenze** in `aiura_legal_lab_db.jurisprudence`.

Upload manuale via `POST /jurisprudence/upload` con anonimizzazione
obbligatoria per il canale studio. Grafo giurisprudenziale norma↔sentenza
con viewer nel frontend.

### 7. Corpus dottrina e prassi

- **Dottrina**: download PDF open access (`scripts/sync_dottrina.py`),
  estrazione metadati accademici, chunk più piccoli (256/32) per precisione
  semantica, `corpus=dottrina`. Usata nella fase INTERPRETAZIONE dell'IQRAC.
- **Prassi**: scraper Agenzia delle Entrate
  ([prassi/](../aiura_legal/prassi/)), `corpus=prassi`,
  sync via `scripts/sync_prassi.py`.

### 8. Ingestione documenti studio

Tier 1 sincrona ([pipeline.py](../aiura_legal/ingestion/pipeline.py)):
estrazione testo (PDF/DOCX/TXT) → anonimizzazione PII → MongoDB
`documents`+`chunks` → coda `ingestion_queue`. Tier 2 asincrona:
worker embedding ([embed_worker.py](../aiura_legal/workers/embed_worker.py)).
File watcher su `incoming/` per ingestione automatica.

⚠️ **Anomalia scoperta 2026-07-03, non ancora investigata**: la collection
`documents` contiene 1.061 documenti (`workspace=mio-studio`,
`is_chunked=True`), ma `chunks` non ha alcun documento con `corpus=studio`
(i valori esistenti sono solo `normattiva`, `dottrina`, `giurisprudenza`,
`massimario`). I documenti risultano marcati come chunkati ma sono
invisibili al retrieval — richiede una sessione dedicata per capire se è un
bug della pipeline o un disallineamento di campo `corpus` da correggere.

### 9. Privacy e PII

- **LegalAnonymizer** a 2 layer ([anonymizer.py](../aiura_legal/core/anonymizer/anonymizer.py)):
  regex (CF, P.IVA, IBAN, email, telefono) + spaCy NER italiano (PER/ORG,
  confidence > 0.80). Whitelist che protegge i riferimenti normativi e
  giurisprudenziali dall'anonimizzazione (art., D.Lgs., Cass., Corti…).
- **PII Vault** ([vault.py](../aiura_legal/core/vault/vault.py)): cifratura
  AES-256-GCM dell'entity map, chiave da `AIURA_PII_KEY`, storage MongoDB
  isolato per workspace. ⚠️ *Vedi roadmap: il wiring del vault nei percorsi di
  produzione è incompleto.*
- **Inferenza locale**: Ollama o LM Studio (qualsiasi endpoint
  OpenAI-compatibile), nessuna chiamata cloud.

### 10. Grafo legale

- **LegalGraphBuilder** ([builder.py](../aiura_legal/core/graph/builder.py)):
  estrazione riferimenti RINVIA/ABROGA/MODIFICA via regex+euristiche, build
  completo e update incrementale post-ingestione →
  `workspaces/mio-studio/indices/graph.json` (NetworkX). Stato verificato
  2026-07-03: **307.325 nodi, 666.291 archi** (molto cresciuto dal dato
  ~11.700/4.569 riportato in precedenza).
- **Grafo giurisprudenziale** (sentenza↔norma) — file separato
  `workspaces/jurisprudence_graph.json`: **464.603 nodi, 2.302.324 archi**
  (verificato 2026-07-03; superiore ai 733.598 archi dell'ultimo snapshot
  di backlog, quindi risulta più aggiornato di quanto documentato finora —
  da confermare con chi ha lanciato l'ultimo rebuild).
- **GraphRetriever**: neighbor expansion con filtro vigenza + conflict
  detection (alimenta sia il retrieval sia il check `conflict_disclosure` di S5).
  **Limite noto**: l'espansione grafo non applica il filtro settore
  giuridico applicato invece a BM25/Vector — può reiniettare rumore
  cross-settore (es. norme civili in risposte penali) anche dopo i fix
  del filtro settore di giugno-luglio.
- Endpoint `/graph/*` + viewer interattivo nel frontend.

### 11. API FastAPI (porta 8765)

| Endpoint | Funzione |
|----------|----------|
| `POST /query` | Catena completa S1→S5, risposta sincrona |
| `POST /query/stream` | Sequential IQRAC con eventi SSE per fase |
| `POST /ingest` | Upload documento (corpus studio o dottrina) |
| `POST /jurisprudence/upload` | Upload sentenza con anonimizzazione |
| `GET/POST /workspace` | Gestione workspace multi-studio |
| `POST /annotate/{id}` + `GET` | Document Intelligence asincrona (S6) |
| `GET /history`, `POST /feedback` | Storico query + feedback avvocato |
| `GET /graph/*` | Esplorazione grafo legale |
| `GET/POST /settings` | Configurazione LLM da UI con riavvio automatico |
| `GET /wiki/*` | Pagine wiki auto-generate |
| `GET /health` | Stato MongoDB + backend LLM |

### 12. Frontend React (porta 5173)

Pagine: **Chat** (streaming per fase IQRAC, fonti citate),
**Dashboard**, **Documents** (upload, cartelle, spostamento),
**Graph** (viewer grafo), **History** (storico con feedback),
**Settings** (backend LLM, modello, temperatura, max token per fase, top-k —
senza riavvio manuale), **Wiki**, **Istituti** (CRUD schede istituto
giuridico, route `/istituti` — vedi §15).

### 13. Backend LLM intercambiabile

- `OllamaClient` (nativo) e `OpenAICompatClient` (LM Studio, vLLM, LocalAI)
  con la stessa interfaccia — switch da `.env`/Settings UI.
- Circuit breaker su connection error, timeout configurabile, strip automatico
  dei blocchi `<think>` dei modelli reasoning (Qwen3/QwQ), fallback su
  `reasoning_content`, supporto `/no_think`.
- Warm-up indici in background all'avvio (elimina il cold start ~20s della
  prima query).

### 14. Wiki auto-generata

Layer wiki ([wiki/](../aiura_legal/wiki/)): pagine di conoscenza generate e
aggiornate da middleware sulle query, con store MongoDB, writer, lint.

### 15. Istituti Giuridici — schede strutturate + ragionamento IQRAC

Feature mergiata il 2026-06-30 (PR #7), estesa con mappatura sistematica e
fix il 2026-07-03. Colma il divario tra "il retrieval trova chunk sparsi" e
"l'avvocato ha una scheda concettuale dell'istituto" — alimenta anche il
registro di ragionamento IQRAC (§2).

- **Storage**: collection `istituti_giuridici` — **193 istituti mappati**
  su 4 codici maggiori + 11 leggi complementari (231/2001, Antimafia,
  Consumo, TUB, TUF, Privacy, TUIR, Proprietà Industriale, Assicurazioni,
  Ambiente, Sicurezza Lavoro, Crisi d'Impresa). Optimistic locking
  per-documento (campo `version`, 409 su conflitto).
- **CRUD UI** (route `/istituti`): l'avvocato crea/modifica/cancella schede
  senza toccare MongoDB — [istituti_router.py](../aiura_legal/api/istituti_router.py),
  [Istituti.tsx](../frontend/src/pages/Istituti.tsx).
- **Sync verso il registry IQRAC**
  ([sync_istituti_registry.py](../scripts/sync_istituti_registry.py)):
  merge non distruttivo MongoDB → `aiura_legal/core/istituti/registry.yaml`,
  preserva le voci curate a mano (es. sentenze pilota).
- **Classificazione istituto in Fase 1**: match lessicale primario, con
  **fallback LLM** sull'`istituto_id` già prodotto nella stessa chiamata di
  Fase 1 se il lessicale fallisce (nessuna chiamata extra) — risolve il
  gap del match lessicale in modalità "doctrine". Il match **semantico**
  via embedding è stato testato e scartato come classificatore primario
  (troppi falsi positivi cross-settore ad alta confidenza su testo breve);
  resta solo come segnale secondario a soglia 0.85 per il Clarifier.
- **Disambiguazione multi-scelta nel Clarifier (S1)**: quando la query tocca
  istituti esplicitamente marcati `disambigua_da` tra loro (es. sequestro
  CPP vs confisca antimafia), il Clarifier propone una scelta con le label
  reali invece della domanda generica "penale o civile?" — la scelta
  arricchisce la query (`enriched_query`) per S2/S3.
- **Gap noto**: 0/193 istituti sul settore "lavoro" — vedi §5.
  Codice dei Contratti Pubblici 2023 (D.Lgs. 36/2023) scaricato in KB il
  2026-07-03 ma non ancora mappato in istituti.

### 16. Valutazione qualità

- **Eval retrieval** (`eval/run_eval.py`): recall su query JSONL con
  `expected_source_ids`, report JSON+Markdown per modulo legislativo.
- **Query suite** (`scripts/run_query_suite.py`): 130 query su 6 domini.
- **Golden test set** con giurisprudenza (v2) + bench
  (`eval/run_bench.py`, in sviluppo).
- 665 test automatici con mongomock-motor (zero MongoDB reale).

### 17. Questioni Giuridiche — livello ontologico (scoperta 2026-07-04)

Feature esistente nel codice ma non documentata finora in questo file né
nel backlog — trovata solo con un inventario sistematico dei componenti
assenti da CLAUDE.md. Distinta dagli Istituti Giuridici (§15): mentre gli
istituti sono schede pratiche per il ragionamento IQRAC, le Questioni sono
un livello di modellazione ontologica separato.

- **Storage file-based** (non MongoDB): `ontology/legal_kb_ontology.ttl`
  (schema RDF/OWL — classi/relazioni astratte, es. `Tesi_Dottrinale`,
  `Orientamento_Interpretativo`) + `ontology/questioni_curate.yaml`
  (istanze `QuestioneGiuridica` curate).
- **QuestioneLoader** ([questione_loader.py](../aiura_legal/core/graph/questione_loader.py)):
  legge solo le voci con stato approvato, validazione referenziale, scrive
  gli archi nel grafo legale.
- **QuestioniRegistry** ([questioni_registry.py](../aiura_legal/core/graph/questioni_registry.py)):
  CRUD per la UI di revisione — vede tutte le voci indipendentemente dallo
  stato, optimistic concurrency control. Dipende da `QuestioneLoader` per
  parsing/validazione (non duplica la logica).
- **API**: [questioni_router.py](../aiura_legal/api/questioni_router.py) —
  `GET/PUT /questioni`, `GET /questioni/search-nodes`.
- **Frontend** (route `/questioni`): `Questioni.tsx`, `QuestioneCard.tsx`,
  `NodeIdPicker.tsx`, `useQuestioni.ts`.
- **Why**: l'avvocato approva/modifica/rifiuta le `QuestioneGiuridica`
  proposte senza editare YAML a mano — stesso principio delle Istituti
  Giuridici ma per la struttura ontologica anziché le schede pratiche.
- Spec di riferimento:
  `docs/superpowers/specs/2026-06-26-questioni-review-ui-design.md`.
- **Non verificato in questa sessione**: quanto della strategia
  "ontologia al posto dei manuali coperti da copyright" (vedi
  `docs/prompts/audit-manuali-copyright-ontologia.md`) sia effettivamente
  popolato con dati reali vs. solo l'infrastruttura CRUD.

---

## Features future

### Roadmap a breve termine (hardening — da code review 2026-06-10)

Priorità alta, chiudono il divario tra promessa di privacy/grounding e
implementazione attuale:

- [ ] **Cifratura entity map nel percorso giurisprudenza** — `anonymizer_bridge`
  salva oggi l'entity map in chiaro in `pii_vault`; deve passare da `PiiVault`
  (AES-256-GCM), che è già pronto ma non collegato.
- [ ] **spaCy NER nell'ingest studio** — `Tier1Pipeline` usa
  `LegalAnonymizer(use_spacy=False)`: i nomi di persona/organizzazione non
  vengono anonimizzati nel percorso `/ingest`. Attivare il layer 2 e salvare
  l'entity map nel vault (oggi viene scartata → de-anonimizzazione impossibile).
- [ ] **`is_anonymized` veritiero** — se l'anonymizer fallisce, il documento
  non deve essere marcato come anonimizzato.
- [ ] **Guardia "solo locale" sul backend LLM** — il Settings consente qualsiasi
  base_url remoto: validare localhost/LAN o mostrare warning esplicito prima
  di inviare query a endpoint esterni.
- [ ] **Citation Contract v2: citazioni in prosa** — il reviewer verifica solo
  gli ID strutturati (`urn:nir:…`, `CC_ART_…`); riconoscere e verificare anche
  i riferimenti in linguaggio naturale ("Cass. civ. n. 12345/2020",
  "art. 1218 c.c.") contro le fonti del Packet.
- [x] **Wiring ContextBudgetManager** — verificato 2026-07-04: collegato di
  default (`AIURA_FULLTEXT_CONTEXT=1`) in `analyst._source_texts_for_prompt()`.
  Questa voce di roadmap era obsoleta.
- [ ] **Stima token lato client prima dell'invio LLM** — `openai_compat_client.py`
  costruisce ed invia il payload senza contare i token; un overflow di `n_ctx`
  produce solo un 400 dal server, intercettato per-fase con un `except`
  generico che logga e prosegue con fallback silenziosi (vedi bug Fase 1 in
  CLAUDE.md, risolto 2026-07-04 solo per il caso specifico del vocabolario
  istituti — il problema di fondo, nessun controllo preventivo generico,
  resta aperto).
- [ ] **Segnalare le fasi IQRAC degradate in UI/Reviewer** — quando una fase
  S3 fallisce (400, timeout, JSON non parsabile) la pipeline prosegue con
  fallback silenziosi senza propagare un flag `degraded`/`error` al frontend
  né declassare la confidence vista dal Reviewer S5 — un utente può vedere
  PASS·HIGH anche se la Fase 1 (framing) non ha prodotto nulla.
- [ ] **Riparare i test del branch corrente** — 3 gruppi rotti dopo i refactor
  recenti (`test_classify_batch`, `test_sequential_analyst`,
  `test_retrieval_perf`).
- [ ] Retention/cifratura `query_history` (contiene fatti dei clienti in chiaro).
- [ ] Validazione nome workspace (`POST /workspace/{name}`) e `.env.bak` in
  `.gitignore`.

### Knowledge base e fonti

- [ ] **Colmare il gap istituti settore "lavoro"** — 0/193 istituti mappati,
  nessun dominio "lavoro" nella query suite. Verificare prima se manca la
  normativa di base (Statuto Lavoratori e leggi lavoristiche) o solo la
  mappatura istituti — vedi §5, §15.
- [ ] **Mappare in istituti il Codice Contratti Pubblici 2023** (D.Lgs.
  36/2023) — scaricato in KB il 2026-07-03, non ancora mappato.
- [ ] **Investigare il gap chunk `corpus=studio`** — 1.061 documenti
  `is_chunked=True` in `documents`, zero chunk `corpus=studio` in `chunks`
  (scoperto 2026-07-03, vedi §8) — i documenti caricati sono invisibili al
  retrieval.
- [ ] **Filtro settore sull'espansione grafo** — `GraphRetriever.expand()`
  non applica il filtro settore usato da BM25/Vector, può reiniettare
  rumore cross-settore (vedi §10).
- [ ] **Pulizia punti Qdrant orfani** — sospetti dopo la migrazione a id
  deterministico dei chunk normattiva (2026-07-03), mai confermata/pulita.
- [ ] **D.Lgs. 175/2024 (TU processo tributario)** — estendere
  `NormattivaWebFetcher` al formato `~all1~artN` (allegati). Sblocca 6 query
  della suite tributaria/cross che oggi puntano al D.Lgs. 546/1992 abrogato.
- [ ] **Cross query ranking** — investigare le ~9 query con atti in corpus ma
  non recuperati (trib_013/016/020, cross_003/004/006/021/022/023).
- [ ] **Rebuild grafo giurisprudenziale** — il grafo (733k archi) va ricostruito
  dopo gli import OpenGA e Corte Costituzionale (`build_jurisprudence_graph.py --rebuild`).
- [ ] **Cron settimanale automatico** — `sync_jurisprudence.py` schedulato
  (Task Scheduler/cron) per mantenere la giurisprudenza aggiornata.
- [ ] **NormSync Agent** — polling settimanale Normattiva per mantenere il
  corpus aggiornato automaticamente (riusa `fetch_normattiva.py`).
- [ ] **HUDOC CEDU** — key cases con traduzione italiana.
- [ ] **Italgiure** (Cassa Forense) — client autenticato, richiede vault
  credenziali.

### Quality gate e HITL

- [ ] **Golden Test Set validato con avvocato** — 50 coppie query/risposta
  validate da dominio (oggi esiste il set v2 ma manca la validazione formale).
- [ ] **HITL feedback loop** — usare i feedback raccolti in `/feedback` per
  raffinare i prompt degli agenti.
- [ ] **Bench giurisprudenza** — completare `eval/run_bench.py` e il verify
  bench (spec `2026-06-09-giuri-verify-bench-design.md`).

### Distribuzione e SaaS (Milestone 2)

- [ ] **Docker Compose** — mongod + API + Ollama/LM Studio per installazione
  one-command negli studi.
- [ ] **SaaS Boundary Gate** — anonimizzazione della query *prima* di un
  eventuale invio a modelli cloud: estende la garanzia privacy anche a un
  futuro tier ibrido. Dipende dall'hardening anonymizer di cui sopra.
- [ ] Multi-utente per studio (auth, ruoli, audit log).

### Idee in valutazione

- De-anonimizzazione automatica delle risposte verso l'avvocato (richiede
  entity map nel vault — vedi hardening).
- Export atti S4 in DOCX con formattazione studio.
- Notifiche su novità normative/giurisprudenziali rilevanti per le pratiche
  aperte (dipende da NormSync + grafo).
