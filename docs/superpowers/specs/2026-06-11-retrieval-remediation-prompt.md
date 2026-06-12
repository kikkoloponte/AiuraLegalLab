# Prompt di esecuzione — Risanamento retrieval (per Claude Sonnet 4.6)

> Copiare il blocco sotto come primo messaggio di una sessione Claude Code
> nel progetto `C:\project\AiUraLegalLab`. Il prompt esegue Fase P + Fase 0
> e si ferma al gate. Per le fasi successive: vedere "Fasi successive" in fondo.

---

Sei un ingegnere senior che lavora sul progetto AiUraLegalLab (leggi CLAUDE.md per le convenzioni). Devi eseguire un piano di risanamento del retrieval già approvato. Lavora in autonomia, una fase alla volta, con commit separati per ogni step e i test sempre verdi prima di passare allo step successivo.

## CONTESTO

Sistema RAG legale italiano, LLM locale (LM Studio/Ollama), MongoDB `aiura_legal_lab_db`, indici BM25 per-corpus (pkl in `workspaces/mio-studio/indices/`) + Qdrant (collection `legal_docs`, embedding `paraphrase-multilingual-MiniLM-L12-v2`). Catena: S2 retrieval (HybridRetriever, RRF, CrossEncoder) → S3 analyst Sequential IQRAC a 4 fasi → S5 CitationReviewer. KB: 457.479 chunk (normattiva 278.684 + dottrina 178.795, tutti con campo `settore` classificato) + 316.889 sentenze in `jurisprudence`. Baseline storica query suite: R=0.721. Hardware: torch CPU-only.

Una code review ha identificato questi difetti, tutti verificati sul codice:

1. **L'LLM ragiona su frammenti**: BM25 salva snippet di 300 char (`aiura_legal/core/retrieval/bm25_retriever.py`, `doc_snippets.append(doc.text[:300])`), Qdrant ritorna `payload["text"][:300]` (`vector_retriever.py` ~riga 382), il prompt tronca a 400 (`agents/analyst.py::_format_source`, `s.snippet[:400]`). Con n_ctx=8192 si usano ~600 token di fonti. Il modello completa il contenuto delle norme dal pretraining attaccando source_id validi: il reviewer verifica che l'ID esista, non che il contenuto corrisponda.
2. **La fusione RRF non fonde mai**: in `hybrid_retriever.py::_rrf_fuse` la chiave è `r.doc_id`, ma BM25 ritorna l'`_id` Mongo mentre Qdrant ritorna `str(hit.id)` = UUID5 (`vector_retriever.py::_to_qdrant_id`). Le chiavi non collidono mai: stesso chunk = 2 risultati, fusione = interleaving.
3. **Reranker inglese**: `core/retrieval/reranker.py` usa `cross-encoder/ms-marco-MiniLM-L-6-v2` (addestrato su MS MARCO inglese) per rerank-are testo giuridico italiano, per giunta sugli snippet da 300 char.
4. **Confidence fittizia**: `hybrid_retriever.py::build_research_packet` assegna HIGH solo contando le fonti (≥5), senza guardare gli score.
5. **`ContextBudgetManager`** (`core/retrieval/context_budget.py`) esiste ed è testato ma non è collegato a nulla; inoltre è calibrato per n_ctx=4096 con budget minuscoli (300 token la prima fonte, 40 le altre).
6. Tre gruppi di test sono rotti per refactor recenti (vedi Fase P).

## REGOLE VINCOLANTI

- Convenzioni CLAUDE.md: async ovunque (motor), type hints, loguru (mai print), test con mongomock-motor, path con `/`.
- MAI distruggere indici funzionanti: i pkl si rinominano `.bak`, non si cancellano. Niente rebuild di Qdrant in queste fasi.
- Il database `legal_lab` (progetto LegalAgentLab) è READ-ONLY.
- Ogni modifica comportamentale del contesto LLM va dietro feature flag env (rollback = flip del flag).
- Un commit per step (P.1, 0.1, 0.2, …) con messaggio in italiano stile repo (`fix:`/`feat:`/`test:`).
- `pytest tests/ -q` deve essere verde prima di ogni commit.
- Non toccare: anonymizer, vault, scrapers, frontend, wiki. Solo retrieval e analyst.
- Se MongoDB o LM Studio non sono raggiungibili, esegui comunque tutto ciò che non li richiede e segnala chiaramente cosa è rimasto da verificare.

## FASE P — Prerequisiti e baseline

P.1 Ripara i 3 gruppi di test rotti (solo lato test, non cambiare il codice di produzione):
   - `tests/test_classify_batch.py::TestFaseAResume::test_skip_atti_gia_nel_checkpoint`: il mock dell'LLM non accetta il kwarg `system` introdotto dal batch LLM in `scripts/classify_knowledge_base.py`.
   - `tests/test_sequential_analyst.py::test_phase_retriever_retrieve_{normativa,giurisprudenza}_calls_search_round`: si aspettano `_search_round` chiamato 1 volta, ora ne fa 3 (round dottrina/prassi aggiunti). Aggiorna le attese verificando il comportamento reale in `core/retrieval/phase_retriever.py`.
   - `tests/test_retrieval_perf.py::TestIntegrationPerf` (6 errori di setup): la fixture usa `BM25Retriever._ensure_bm25`, rimosso dal refactor per-corpus. Adatta la fixture all'API attuale di `bm25_retriever.py`.
P.2 Baseline (solo se MongoDB+indici disponibili): esegui `python scripts/run_query_suite.py` due volte — una senza filtri settore, una con `AIURA_SETTORE_SOFT=1` — e salva i riepiloghi in `eval/results/baseline_pre_fase0/` con un README che riporta R globale e per dominio, data, configurazione. Se la suite richiede l'API attiva e non lo è, salta e segnala.
P.3 Crea branch `feat/retrieval-fase0` da main.

## FASE 0 — Quick wins (zero rebuild indici)

0.1 **Fix fusione RRF** (`core/retrieval/hybrid_retriever.py::_rrf_fuse`):
   - Calcola la chiave di fusione con `_to_qdrant_id(r.doc_id)` (importala da `vector_retriever.py`) per i risultati BM25 e graph; i risultati vector hanno già quell'ID come doc_id. ATTENZIONE: `SearchResult.doc_id` esposto nel packet deve restare l'ID originale per ogni risultato (il reviewer S5 e il frontend ne dipendono) — la chiave UUID serve solo internamente alla fusione.
   - In `VectorRetriever.add_documents_batch` aggiungi `mongo_id: doc.id` e `workspace` (se presente nei metadata) al payload dei punti nuovi; in `search`, se il payload ha `mongo_id`, usa quello come `doc_id` del SearchResult.
   - Test nuovi `tests/test_rrf_fusion.py`: (a) stesso chunk presente in BM25 e vector → 1 solo risultato fuso con score combinato; (b) nessun duplicato per doc nel risultato; (c) i pesi (bm25, vec, graph) influenzano l'ordinamento come atteso.

0.2 **Testo pieno nel prompt** (l'intervento più importante):
   - Nuovo modulo `core/retrieval/source_texts.py` con una funzione che, dato un elenco di SearchResult, recupera il testo completo: per corpus normattiva/dottrina/studio da `aiura_legal_lab_db.chunks` (campo `text`, lookup per `_id`); per giurisprudenza da `jurisprudence` (campi `massima`/`motivazione`/`dispositivo`, lookup per `metadata.jdoc_id` + `metadata.chunk_type`). Usa pymongo sync chiamato via `asyncio.to_thread` dal punto di integrazione (coerente con come l'orchestrator chiama S2). Documento mancante → fallback allo snippet, mai eccezioni.
   - Aggiungi `full_text: str = ""` a `SearchResult` in `core/types.py`.
   - Ricalibra `ContextBudgetManager.BUDGETS` per n_ctx=8192: normativa {full_text_slots: 3, full_text_tokens: 400, summary_slots: 3, summary_tokens: 60}; giurisprudenza {3, 500, 2, 60}; dottrina {1, 200, 2, 60}; prassi {0, 0, 2, 60}. Adatta `format_chunks` ad accettare SearchResult (usa `full_text` se presente, altrimenti `snippet`).
   - Integra in `agents/analyst.py`: `_format_source` e `_format_phase_sources` usano `full_text` (troncato via ContextBudgetManager) al posto di `snippet[:400]`, in tutte le modalità (analyze, analyze_deep, analyze_sequential). Il fetch dei full_text avviene una volta, dopo il retrieval, nell'orchestrator (`agents/orchestrator.py`, dopo S2 e dopo ogni re-query di fase).
   - Feature flag `AIURA_FULLTEXT_CONTEXT` (default "1"): a "0" ripristina il comportamento attuale.
   - Test: `tests/test_source_texts.py` con mongomock (fetch per i 4 corpora, fallback su doc mancante); estendi `tests/test_context_budget.py` ai nuovi budget; test anti-regressione in `tests/test_sequential_analyst.py`: il prompt della fase NORMATIVA contiene testo della fonte oltre il 300° carattere; test anti-overflow: token totali del prompt (tiktoken) ≤ n_ctx − max_tokens_fase.

0.3 **Reranker multilingue** (`core/retrieval/reranker.py`):
   - Modello configurabile via env `RERANKER_MODEL` (pydantic-settings come gli altri moduli), default `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`.
   - Input del rerank: `full_text` troncato a ~510 token se disponibile, altrimenti snippet.
   - Test: il modello configurato viene usato; con modello non disponibile il fallback mantiene l'ordine (comportamento esistente). Marca con `@pytest.mark.skipif` i test che richiedono il download del modello.

0.4 **Confidence su score** (`hybrid_retriever.py`):
   - HIGH solo se ≥3 fonti con score reranker sopra una soglia configurabile (`RETRIEVAL_SCORE_THRESHOLD`, default ragionevole da verificare empiricamente, parti da 0.0 visto che i cross-encoder mmarco danno logit anche negativi — scegli tu un default difendibile e documentalo); MEDIUM se ≥2 fonti qualunque; LOW altrimenti. Aggiorna i test esistenti in `tests/test_retrieval.py`.

## GATE DI USCITA FASE 0

1. `pytest tests/ -q` → 0 failed.
2. Se l'ambiente lo consente: riesegui la query suite e confronta con la baseline P.2 — R non deve regredire; salva il report in `eval/results/fase0_post/`. Se non puoi eseguirla, dichiaralo esplicitamente nel riepilogo finale.
3. Apri una PR verso main con: descrizione delle modifiche, before/after dell'eval (o nota che va eseguita), istruzioni di rollback (flag).

NON proseguire oltre la Fase 0: le fasi successive (re-chunking motivazioni, BM25 full-text, nuovo embedder) richiedono decisioni hardware e ore di rebuild, e partono solo dopo la validazione umana di questa PR.

## FASI SUCCESSIVE (solo riferimento, NON eseguire)

- Fase 1: chunking motivazioni 512/64 (~1,9M nuovi chunk, ~9h embedding CPU), BM25 full-text previa valutazione `bm25s` (rank_bm25 rischia OOM a 2,5M doc), filtro workspace in Qdrant.
- Fase 2: embedder multilingual-e5 (small su CPU ~15-40h, base con GPU ~3-4h) su collection parallela con cutover A/B.
- Fase 3: claim-level verification (S5.5), reviewer v2 per citazioni in prosa.
