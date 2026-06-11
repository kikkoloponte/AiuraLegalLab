# AiUra LegalLab — Backlog (storico milestone)
# Formato: [P] Titolo | Effort S/M/L/XL | Dipende da | Profilo
# Aggiornato: 2026-05-31 (run5: R=0.721, corpus 91 atti / 17062 chunk)
#
# NOTA: per lo stato corrente e le metriche aggiornate vedi
#   docs/wiki/05-backlog.md  (snapshot 2026-06-05: KB 316k sentenze, debito tecnico)
#   docs/FEATURES.md         (features implementate + roadmap consolidata)

---

## MILESTONE 0 — Setup + MongoDB + Ring 0 base ✅ (90% completato)

### Setup e MongoDB

- [x] [P0] Setup: pyproject.toml, CLAUDE.md, struttura dir | S | — | BE
- [x] [P0] Tipi condivisi: core/types.py | S | Setup | BE
- [x] [P0] MongoDB client (motor) + models | M | Tipi | BE
- [x] [P0] .env con valori da LegalAgentLab | S | client | BE
- [x] [P0] Test MongoDB con mongomock-motor | S | models | BE
- [x] [P0] Script build_indexes.py da LegalAgentLab | M | client | BE

### Ingestione

- [x] [P0] Document Extractor PDF/DOCX/TXT | M | Tipi | BE
- [x] [P0] Chunker sliding window 512 tok overlap 64 | M | Extractor | BE
- [x] [P0] PII Anonymizer Layer 1 regex | M | Tipi | AI
- [x] [P0] PII Anonymizer Layer 2 spaCy | M | Layer 1 | AI
- [x] [P0] Pipeline Tier 1: file → MongoDB.documents + chunks | M | Tutti sopra | BE
- [x] [P0] File watcher su incoming/ | S | Pipeline | BE

### Retrieval

- [x] [P0] BM25Retriever + VectorRetriever + CrossEncoderReranker | L | Chunker | AI/BE
- [x] [P0] HybridRetriever con RRF + weight profiles per intent | M | Tutti retrieval | BE

### Agenti e API

- [x] [P0] Ollama client async | S | Tipi | BE
- [x] [P0] 7 Pi Skills (.md): S0 Supervisor, S1 Clarifier, S2 Researcher, S3 Analyst, S4 Drafter, S5 Reviewer, S6 Annotator | L | — | AI
- [x] [P0] FastAPI /query /ingest /workspace (retrieval + citation review) | M | Retrieval | BE
- [x] [P0] README installazione e primo utilizzo | S | — | FULL

---

## MILESTONE 1 — Ring 0 Completo

### 1A · Tipizzazione Chunk + Modulo Normattiva ✅ (completato 2026-05-28)

- [x] [P1] Chunk model: +corpus, +fonte, +testo_tipo con defaults | S | — | BE
- [x] [P1] migrate_chunks_typing.py: backfill chunk esistenti (update_many) | S | Chunk model | BE
- [x] [P1] Tier1Pipeline: imposta corpus="studio" sui nuovi chunk | S | Chunk model | BE
- [x] [P1] normattiva/connector.py: copia da LegalAgentLab (sync, standalone) | S | — | BE
- [x] [P1] normattiva/parser.py: fonte_from_doc() + NormattivaDocAdapter | M | connector | BE
- [x] [P1] normattiva/pipeline.py: NormattivaPipeline (normattiva_docs → chunks tipizzati) | M | parser | BE
- [x] [P1] mirror_normattiva.py: CLI sync legal_lab → aiura_legal (idempotente) | M | pipeline | BE
- [x] [P1] BM25Retriever: filtro subset + bm25_meta.json (maschera numpy) | M | Chunk model | BE
- [x] [P1] VectorRetriever: where filter ChromaDB | S | Chunk model | BE
- [x] [P1] HybridRetriever: chunk_filter passthrough (chunk_filter=None = nessuna regressione) | S | BM25+Vector | BE
- [x] [P1] build_indexes.py: legge da aiura_legal.chunks (non più da legal_lab) | M | tutto sopra | BE
- [x] [P1] test_normattiva_parser.py + test_normattiva_pipeline.py | M | tutto sopra | BE
- [x] [P1] fetch_normattiva.py: CLI fetch da API Normattiva (uso futuro) | M | pipeline | BE
- [x] [P1] Verifica operativa: mirror 500 doc reali + build_indexes + retrieval subset-filter | S | tutto 1A | BE

### 1B · Loop LLM — E2E ✅ (completato 2026-05-29)

- [x] [P1] Wiring Ollama in /query: S3 Analyst (CoT) genera risposta da Research Packet | L | Retrieval | AI/BE
- [x] [P1] Orchestrazione agenti Python: S0 routing → S2 retrieval → S3 analysis → S5 review | L | Ollama wiring | AI
- [x] [P1] S1 Clarifier integrato nel loop (max 2 turni prima della ricerca) | M | Orchestrazione | AI

### 1C · Completamento Ring 0

#### 1C-Graph · Legal Graph Builder ✅ (completato 2026-05-29, graph.json buildato 2026-05-31)

- [x] [P1] NormattivaDocAdapter: aggiungi valid_to (data_fine_vigenza) + propagazione nei chunk | S | — | BE
- [x] [P1] ReferenceExtractor: regex + euristiche RINVIA/ABROGA/MODIFICA su testo IT | S | — | AI
- [x] [P1] LegalGraphBuilder: build completo + update incrementale → graph.json (nodi con valid_from+valid_to) | M | Extractor | BE
- [x] [P1] LegalGraphBuilder._norm_num: fix strip prefisso "Art." per risoluzione lookup | S | Builder | BE  ← fix 2026-05-31
- [x] [P1] scripts/build_graph.py: CLI build grafo da MongoDB chunks | S | Builder | BE
- [x] [P1] GraphRetriever: neighbor expansion (con filtro valid_on) + conflict detection | M | Builder | AI/BE
- [x] [P1] HybridRetriever: RRF tripartito (BM25+Vector+Graph), pesi per intent, passa valid_on al grafo | M | Retriever | BE
- [x] [P1] CitationReviewer: conflict_disclosure reale via GraphRetriever | S | Retriever | BE
- [x] [P1] Pipeline hook: update incrementale grafo dopo ingestione | S | Builder | BE
- [x] [P1] test_graph_extractor.py + test_graph_builder.py (68 test) + test_graph_retriever.py | M | tutto sopra | BE

#### 1C-Agenti

- [x] [P1] S4 Drafter: generazione atto/parere da Research Packet | M | Loop LLM | AI
- [x] [P1] S6 Annotator: Document Intelligence asincrona (Workflow B) | L | Loop LLM | AI

#### 1C-Backend ✅ (completato 2026-05-29)

- [x] [P1] Tier 2 worker asincrono: embedding via MongoDB.ingestion_queue | L | models | BE
- [x] [P1] Normattiva AKN parser raffinato (vigenza, abrogazioni) | M | normattiva/parser | BE
- [x] [P1] PII Vault MongoDB: entity map cifrata AES-256-GCM (core/vault/) | L | Anonymizer | BE

#### 1C-KnowledgeBase · Espansione corpus normativo ✅ (completato 2026-05-31)

- [x] [P1] Mirror CPC (RD 1443/1940, 1059 doc) → aiura_legal + chunk | S | mirror_normattiva.py | BE
- [x] [P1] Mirror L. 300/1970 (Statuto Lavoratori, 41 doc) → aiura_legal + chunk | S | mirror | BE
- [x] [P1] Mirror D.Lgs. 276/2003 (Biagi, 86 doc) → aiura_legal + chunk | S | mirror | BE
- [x] [P1] Mirror D.Lgs. 81/2015 (Jobs Act, 57 doc) → aiura_legal + chunk | S | mirror | BE
- [x] [P1] CPP completo (DPR 447/1988, 802 doc totali) → mirror da legal_lab | S | mirror | BE
- [x] [P1] Mirror L.212/2000 (Statuto contribuente, 21 doc) + D.Lgs.74/2000 (reati trib., 25) + D.Lgs.472/1997 (sanzioni, 30) + D.Lgs.218/1997 (adesione, 17) | S | mirror | BE
- [x] [P1] Fetch Normattiva: TUIR DPR 917/1986 (236 art.) + IVA DPR 633/1972 (158 art.) + DPR 602/1973 (22 art., parz.) | M | fetch_normattiva.py | BE
- [x] [P1] Rebuild BM25 + ChromaDB post-espansione: 9213 → 10107 chunk | S | build_indexes.py | BE
- [x] [P1] Rebuild graph.json (8218 nodi, 1954 RINVIA +39%, 3.8 MB) | S | build_graph.py | BE
- [x] [P1] Fix S1 Clarifier: pre-filtro Python + prompt aggiornato + bypass run_query_suite | M | clarifier.py | AI
- [x] [P1] Run2 query suite 130 query: R=0.644 globale (+109% vs run1 R=0.308) | S | eval | BE
  - amm: 0.575 | civ: 1.000 | cross: 0.372 | pen: 0.850 | trib: 0.250 | aiura_01: 0.950
- [x] [P1] Run3 query suite con TUIR+IVA indicizzati: R=0.674 globale (+4.7% vs run2) | S | eval | BE
  - amm: 0.575 | civ: 1.000 | cross: 0.406 | pen: 0.850 | trib: 0.450 | aiura_01: 0.900
- [x] [P1] Run4 confronto qwen3.5-9b vs qwen2.5:7b: R=0.674 identico — bottleneck è corpus, non modello | S | eval | BE
- [x] [P1] Mirror D.Lgs.471/1997 (17) + 241/1997 (40) + 165/2001 (73) + 231/2001 (85) da legal_lab | S | mirror | BE
- [x] [P1] Mirror 9 atti prioritari da legal_lab: T.U.Sicurezza (306) + Privacy (186) + Ass.Private (355) + CdS (240) + CAD (92) + Maternità (88) + Lic.Collettivi (31) + CIG (47) + L.689/1981 (148) | M | mirror | BE
- [x] [P1] Fetch Normattiva: D.Lgs.36/2023 Codice Appalti (557 art.) + DPR 327/2001 (7 art., parz. HTTP 500) | M | fetch | BE
- [x] [P1] Rebuild BM25+ChromaDB: 10107 → 15119 chunk (+50%) | S | build_indexes.py | BE
- [x] [P1] Rebuild graph.json: 8218 → 10500 nodi, RINVIA 1954 → 3532 (+81%), 5.0 MB | S | build_graph.py | BE
- [x] [P1] Fix HTTP-500 Normattiva: NormattivaWebFetcher fallback N2Ls automatico (threshold=1) | M | connector.py | BE
  - DPR 327/2001: 7 → 70 art. | DPR 602/1973: 22 → 105 art. | TUEL D.Lgs.267/2000: 0 → 295 art.
- [x] [P1] Mirror 6 atti da legal_lab: Antiriciclaggio (74) + Immigrazione TU (49) + GDPR adeguamento (27) + Disabilità (44) + Riforma proc. (74) + Mediazione (24) | S | mirror | BE
- [x] [P1] Fetch Normattiva: Costituzione Repubblica (157 art., N2Ls fallback pos.41) | S | fetch | BE
- [x] [P1] GDPR Reg. UE 679/2016: coperto da D.Lgs.196/2003 (186 art.) + D.Lgs.101/2018 (27 art.) già in corpus | S | — | BE
- [x] [P1] Rebuild finale: 10107 → 17062 chunk (+69%), 91 atti, grafo 10942 nodi / RINVIA 3736 | S | build | BE
- [x] [P1] Fix _recall() regex: ~art\d+ → ~art[\w-]+ (fix false R=0 su art7bis/art10bis) | S | run_query_suite.py | BE
- [x] [P1] Fix max_tokens: 16384 → 4096 (era per qwen3.5-9b, troppo per qwen2.5:7b → latenza 67s→10s) | S | openai_compat_client.py | BE
- [x] [P1] Run5 query suite: R=0.721 globale (+7% vs run4, +134% vs run1) | S | eval | BE
  - amm: 0.650↑ | civ: 1.000 | cross: 0.422↑ | pen: 0.950↑ | trib: 0.450 | aiura_01: 1.000↑
  - ⚠️ trib_001 regressione R=1→0 (corpus dilution: Costituzione scala BM25 sopra L.212/2000)
- [x] [P1] Diagnosi gap residui run5: D.Lgs.546/1992 ABROGATO da D.Lgs.175/2024 (TU processo tributario) | S | — | BE
  - trib_003/009/017 + cross_014/019/027: tutti puntano ad articoli D.Lgs.546 che sono "PROVVEDIMENTO ABROGATO"
  - D.Lgs.175/2024 usa formato ~all1~artN (allegato) — non supportato da NormattivaWebFetcher attuale
- [x] [P1] Mirror D.Lgs.152/2006 Codice Ambiente (318 doc, ~1000 chunk) → fix cross_018 | S | mirror | BE
- [x] [P1] Mirror L.24/2017 Gelli-Bianco (18 doc, ~50 chunk) → fix cross_029 | S | mirror | BE
- [x] [P1] BM25 domain filter: _source_id_in pattern matching in BM25Retriever.search | S | bm25_retriever.py | BE
- [x] [P1] run_query_suite.py: domain chunk_filter per workspace normattiva_tributario (evita corpus dilution) | S | scripts | BE
- [x] [P1] Rebuild indici: 17062 → 18068 chunk, grafo 11732 nodi / RINVIA 4569 | S | build | BE
- [x] [P1] Run6 query suite: in corso... | S | eval | BE
- [ ] [P1] Fetch D.Lgs.175/2024 TU Processo Tributario: estendi NormattivaWebFetcher per ~all1~artN | M | connector.py | BE
  - URN: urn:nir:stato:decreto.legislativo:2024-11-14;175, allegato 1 contiene art1-art??? (count da verificare)
  - Fix: trib_003 (art18+21), trib_009 (art48), trib_017 (art19) + cross_014/019/027 (art19)
  - Aggiornare tests expected_source_ids: D.Lgs.546~artN -> D.Lgs.175~all1~artN
- [ ] [P1] Cross query ranking: investigare trib_013/016/020 + cross_003/004/006/021/022/023 (atti in corpus ma non recuperati) | M | retriever | BE

### 1D · Quality Gate (dopo Loop LLM)

- [ ] [P1] Golden Test Set: 50 query/risposta validate con avvocato | L | Loop LLM OK | Domain
- [x] [P1] Eval script: groundedness, latenza, citation precision | M | Golden Set | BE  ← anticipato a M0
- [ ] [P1] HITL feedback loop: avvocato valuta output → raffinamento prompt agenti | M | Golden Set | Domain

---

## MILESTONE 2 — Ring 1: Server e SaaS base (mese 2-3)

- [ ] [P2] Docker compose: mongod + API + Ollama | M | MS1 | BE
- [ ] [P2] NormSync Agent: polling settimanale Normattiva (usa fetch_normattiva.py) | L | fetch | BE
- [ ] [P2] HUDOC CEDU Key Cases + traduzione IT | M | — | AI
- [ ] [P2] Italgiure client (Cassa Forense) | XL | Vault cred. | BE
- [ ] [P2] SaaS Boundary Gate: anonimizzazione query prima del cloud | L | Anonymizer | AI

---

## Distribuzione Collaboratori

**Backend (BE)**: MongoDB, pipeline, BM25, FastAPI, vault, NormSync, Docker
**AI/ML (AI)**: Anonymizer, Vector, Reranker, Grafo, tutti gli agenti, eval
**Domain (Avvocato)**: Golden Test Set, validazione output, feedback HITL

---

## Legenda effort

`S` = ore | `M` = 1-2 giorni | `L` = 3-5 giorni | `XL` = settimana+
