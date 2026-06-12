# Prompt di esecuzione — Risanamento retrieval FASE 1 (per Claude Sonnet 4.6)

> Copiare il blocco sotto la riga `---` come primo messaggio di una sessione
> Claude Code in `C:\project\AiUraLegalLab`. Prerequisito: PR #3 (Fase 0)
> validata. La Fase 1 include una run macchina di ~9 ore (embedding):
> il prompt la prepara, la valida su un sottoinsieme e la lancia in
> background resume-safe solo alla fine.

---

Sei un ingegnere senior sul progetto AiUraLegalLab (leggi CLAUDE.md per le convenzioni). Esegui la FASE 1 del piano di risanamento retrieval. La Fase 0 è già stata completata (PR #3): fusione RRF con chiave uuid5, campo `SearchResult.full_text` + `core/retrieval/source_texts.py` + ContextBudgetManager collegato (flag `AIURA_FULLTEXT_CONTEXT`, default on, forzato a 0 in `tests/conftest.py`), reranker configurabile via `RERANKER_MODEL` (default mmarco multilingue), confidence basata sugli score (`RETRIEVAL_SCORE_THRESHOLD`), payload Qdrant dei punti nuovi con `mongo_id` e `workspace`, `QDRANT_URL` letto via pydantic-settings.

## OBIETTIVO FASE 1

Oggi ogni sentenza diventa 3 chunk monolitici (massima, motivazione, dispositivo — `jurisprudence/coordinator.py::to_chunks`): una motivazione media ~10.400 caratteri (~2.700 token) è un unico Document, embedded da un modello che tronca a 128 token e indicizzato BM25 sui primi 200 caratteri. Tutto oltre l'incipit è irrecuperabile. La Fase 1: (a) spezza le motivazioni in chunk 512/64, (b) porta BM25 a indicizzare il testo pieno, (c) embedda i nuovi chunk in modo incrementale, (d) attiva il filtro workspace nel vector search.

## CONTESTO TECNICO E NUMERI

- KB: 316.889 sentenze in `aiura_legal_lab_db.jurisprudence` (motivazione: media 10.4k char, mediana 8k, p90 21.6k); 457.479 chunk in `chunks` (normattiva 278.684 + dottrina 178.795, tutti con campo `settore`).
- Hardware: torch CPU-only, embedding MiniLM ~60 chunk/s → ~1,9M nuovi chunk ≈ 9 ore. La run va fatta resume-safe.
- BM25: `core/retrieval/bm25_retriever.py`, `_BM25Sub` per-corpus, `rank_bm25` (puro Python). `indexed_text` attuale = `sommario + titolo_articolo + text[:200]`. A ~2,5M documenti full-text rank_bm25 rischia OOM (build attuale già 4-8 GB): per questo c'è lo spike 1.0.
- Qdrant: collection `legal_docs`, `skip_existing=True` in `add_documents_batch` (salta punti con stesso uuid5). I vecchi punti motivazione hanno id `{hex16}_motivazione`; i nuovi avranno id diversi → non vengono saltati (bene) ma i VECCHI vanno eliminati esplicitamente o duplicano i contenuti nei risultati.
- Indicizzazione giurisprudenza: `scripts/build_jurisprudence_indexes.py` / `scripts/index_jurisprudence.py` leggono da `jurisprudence` e generano i Document via `to_chunks`.
- `source_texts.py` (Fase 0) recupera il full_text giurisprudenza da `jurisprudence.{massima,motivazione,dispositivo}` via `metadata.jdoc_id`+`chunk_type`: con le motivazioni spezzate questo NON basta più (ritornerebbe l'intera motivazione, sfondando il budget) — vedi step 1.1.

## GOTCHA EREDITATI DALLA FASE 0 (verificati, non riscoprirli)

- L'eval della Fase 0 è girata SOLO-BM25 (QDRANT_URL non arrivava all'API, fixato in `e5c3720`): il fix RRF non è ancora stato esercitato dall'eval. La PRIMA cosa da fare in Fase 1 è una baseline CON Qdrant server attivo (verifica che `/health` veda la collection e che i log non diano warning di collection vuota).
- La query suite (`scripts/run_query_suite.py`) usa `POST /query` e il workspace `normattiva` (18k chunk): per misurare la giurisprudenza usa `eval/run_bench.py` + `eval/bench_questions.jsonl`.
- `pytest tests/ -q` esclude i test `integration` di default (addopts); opt-in con `pytest -m integration`.
- I flag `AIURA_SETTORE_*` agiscono solo sul percorso `/query/stream` (PhaseRetriever).

## REGOLE VINCOLANTI

- Convenzioni CLAUDE.md: async ovunque (motor), type hints, loguru, mongomock-motor nei test, path con `/`.
- MAI distruggere indici funzionanti: pkl rinominati `.v1.bak`; i punti Qdrant vecchi si eliminano SOLO dopo che i nuovi sono indicizzati e verificati.
- `legal_lab` è READ-ONLY. Niente rebuild della collection Qdrant (quello è Fase 2).
- Un commit per step (1.0, 1.1, …), messaggi in italiano stile repo, suite verde prima di ogni commit.
- Branch: `feat/retrieval-fase1`. Se PR #3 è merged parti da main, altrimenti da `feat/retrieval-fase0` (PR stacked — dichiaralo nella descrizione).
- Operazioni lunghe (>30 min): lanciale in background con log di progresso, mai in foreground.
- Non toccare: anonymizer, vault, scrapers, frontend, wiki.

## STEP

### 1.B — Baseline con Qdrant attivo (PRIMA di ogni modifica)
Verifica Qdrant server su (`QDRANT_URL`), API su, poi: query suite completa + bench giurisprudenza. Salva in `eval/results/baseline_pre_fase1/` con README (R per dominio, configurazione, conteggio punti Qdrant). Questa è la baseline vera del fix RRF di Fase 0: se R cambia rispetto a `eval/results/fase0_post/` (che era solo-BM25), annotalo — è atteso.

### 1.0 — Spike bm25s (DECISION GATE, ~mezza giornata, nessun commit di produzione)
`pip install bm25s` e misura su un corpus di prova realistico (es. 500k testi da motivazioni reali, estendibile a 2,5M sintetici): tempo build, RAM picco, latenza query top-20, dimensione su disco. Confronta con rank_bm25 sullo stesso campione.
- ESITO A (bm25s regge: RAM build < 8 GB, latenza < 200ms): migra `_BM25Sub` a bm25s mantenendo l'interfaccia pubblica di `BM25Retriever` invariata (stessi metodi, stessi SearchResult); aggiungi bm25s a pyproject.
- ESITO B (bm25s non regge o API incompatibile): BM25 full-text solo su normattiva+dottrina (457k, rank_bm25 regge); la giurisprudenza resta indicizzata su incipit+metadati e si affida al vettoriale.
Documenta l'esito e le misure in `docs/superpowers/specs/2026-06-12-spike-bm25s-results.md`. Tutto il resto della fase si adatta a questo esito.

### 1.1 — Chunking motivazioni
- `jurisprudence/coordinator.py::to_chunks`: motivazione → chunk con `Chunker(max_tokens=512, overlap=64)` (`ingestion/chunker.py`); id `{doc.id}_motivazione_{i:03d}`; metadata: `chunk_type="motivazione"`, `chunk_index=i`, più i metadata esistenti (organo, numero, anno, materia, jdoc_id). Massima e dispositivo invariati.
- **Persisti i chunk giurisprudenza nella collection `chunks`** (corpus="giurisprudenza", campo `text` col testo del chunk, `jdoc_id`, `chunk_type`, `chunk_index`): lo schema in CLAUDE.md lo prevede già. Questo rende uniforme il fetch di `source_texts.py` (lookup per `_id` come gli altri corpora — adattalo) e dà una fonte unica per i build BM25/Qdrant.
- Script `scripts/rechunk_motivazioni.py`: legge `jurisprudence`, scrive i chunk in `chunks`, idempotente (riconosce sentenze già processate, secondo run = 0 nuovi), batch con checkpoint/resume (stesso pattern di `classify_knowledge_base.py`), `--dry-run` e `--limit N` per i test.
- ATTENZIONE reviewer: i nuovi doc_id `{hex16}_motivazione_001` devono continuare a soddisfare il grounding giurisprudenziale di `core/reviewer/reviewer.py` (`_SENTENZA_ID_RE` estrae hex16 dalla risposta e confronta con i doc_id del packet): verifica e aggiorna il matching se serve (es. confronto per prefisso hex16), con test dedicati.

### 1.2 — BM25 full-text
- `_BM25Sub.add`: `indexed_text` = testo pieno del chunk (elimina il `text[:200]`; mantieni sommario+titolo in testa). Bump della versione schema pkl con rebuild automatico dal legacy (meccanismo già esistente per la migrazione dal pkl monolitico).
- Secondo l'esito 1.0: backend bm25s (A) o rank_bm25 limitato a normattiva+dottrina full-text (B).
- Rebuild dei pkl per-corpus dal contenuto di `chunks` (ora include giurisprudenza). Misura e logga RAM/tempi.

### 1.3 — Embedding incrementale dei nuovi chunk (~9h, background)
- Estendi lo script di indicizzazione giurisprudenza per leggere i chunk da `chunks` (post 1.1); payload completo: `mongo_id`, `workspace`, `jdoc_id`, `chunk_type`, `chunk_index`, date int.
- Validazione su sottoinsieme: indicizza 5.000 sentenze (`--limit`), verifica conteggi attesi, una query vettoriale di smoke che peschi un chunk profondo di motivazione.
- Run completa in background (resume-safe via skip_existing, log di progresso ogni 10k punti con ETA). Durata attesa ~9h: lanciala e prosegui con 1.4 e i test mentre gira.
- SOLO a run completata e verificata (conteggio punti atteso ±1%): elimina i vecchi punti monolitici `{hex16}_motivazione` (itera gli id da `jurisprudence`, calcola uuid5, delete in batch). Conserva nel log il conteggio eliminati.

### 1.4 — Filtro workspace nel vector search
- `vector_retriever.py::_build_qdrant_filter`: parametro `workspace` opzionale; quando presente, condizione che accetta i punti con `workspace` uguale OPPURE assente (compat coi punti legacy pre-Fase 0 — usa `IsEmptyCondition` in `should`). `HybridRetriever` propaga il workspace.
- Test: con due workspace fittizi i risultati non si mescolano; i punti legacy senza payload workspace restano visibili.

## TEST RICHIESTI

- Update `tests/test_coordinator.py`: sentenza con motivazione ~3.000 token → numero chunk atteso, overlap corretto, massima intera.
- Nuovi test per `rechunk_motivazioni.py` (mongomock): idempotenza, dry-run, resume da checkpoint.
- Update `tests/test_reviewer.py`: grounding con doc_id `{hex16}_motivazione_001` nel packet e hex16 citato nella risposta → PASS; hex16 non nel packet → FAIL.
- Test migrazione pkl legacy → nuovo schema senza perdita.
- Update `tests/test_source_texts.py`: fetch del chunk di motivazione ritorna il testo del CHUNK, non l'intera motivazione.
- `pytest tests/ -q` → 0 failed prima di ogni commit; alla fine anche `pytest -m integration` (segnala i flaky senza bloccarti).

## GATE DI USCITA FASE 1

1. Suite verde + test nuovi.
2. Re-run eval (query suite + bench giurisprudenza) CON Qdrant attivo → confronto con `baseline_pre_fase1`: R non regredisce su normattiva; il bench giurisprudenza migliora (atteso: le risposte che stanno in mezzo alla motivazione ora emergono — verifica con 10 query mirate, target ≥6/10 col chunk giusto nel top-6). Salva in `eval/results/fase1_post/`.
3. RAM build BM25 < 8 GB; latenza query BM25 < 200ms (misurata, nel report).
4. PR verso la base corretta con: esito spike 1.0, before/after eval, conteggi (chunk creati, punti embeddati, punti vecchi eliminati), istruzioni di rollback (pkl `.v1.bak`, chunk eliminabili con `db.chunks.delete_many({corpus:"giurisprudenza"})` + ripristino punti — documenta la procedura esatta).

NON proseguire con la Fase 2 (nuovo embedder, rebuild completo): richiede la decisione GPU e parte solo dopo la validazione umana di questa PR.

## SE QUALCOSA VA STORTO

- Embedding interrotto: rilancia lo stesso comando, skip_existing riprende da dove era.
- bm25s dà risultati diversi da rank_bm25 sulle stesse query: confronta top-10 su 20 query campione; difformità di ranking lievi sono attese (implementazioni diverse di BM25), difformità di recall no — in quel caso ESITO B.
- RAM oltre 8 GB durante build BM25: passa a ESITO B senza insistere.
- MongoDB/LM Studio/Qdrant giù: ferma gli step che li richiedono, completa il resto, segnala nel riepilogo cosa manca.
