# Backlog aggiornato

Aggiornato al **3 luglio 2026** (precedente: 5 giugno 2026). Numeri
verificati direttamente su MongoDB il 2026-07-03, non riportati da note
precedenti.

---

## ✅ Completato

### Infrastruttura e architettura

| # | Funzionalità | Note |
|---|-------------|------|
| 1 | Architettura multi-agente S0–S6 | FastAPI + LegalOrchestrator |
| 2 | HybridRetriever (BM25 + Vector + CrossEncoder + RRF) | Pesi adattivi per intent |
| 3 | Citation Contract — CitationReviewer S5 | Blocca allucinazioni, verifica grounding |
| 4 | Document Intelligence — S6 Annotator | Analisi rischio per sezione, asincrono |
| 5 | PII Vault — anonimizzazione + cifratura AES | spaCy it_core_news_lg |
| 6 | Wiki layer — auto-generazione post-query | WikiEngine fire-and-forget |
| 7 | MongoDB unificato `aiura_legal_lab_db` | Migrazione da aiura_legal + legal_lab |
| 8 | API REST FastAPI :8765 con Swagger UI | Tutti gli endpoint documentati |

### Knowledge base

| # | Funzionalità | Dettaglio |
|---|-------------|---------|
| 9 | Normattiva 170.857 documenti (+4.035 da giugno) | Copiato da legal_lab, con URN NIR |
| 9b | 3 leggi complementari scaricate (3 luglio) | Contratti Pubblici 2023 (D.Lgs. 36/2023), Legge Fallimentare previgente (R.D. 267/1942), Codice Navigazione (R.D. 327/1942) — 2.226 articoli |
| 9c | 193 istituti giuridici mappati + CRUD UI | PR #7 (30 giugno) + mappatura sistematica 4 codici + 11 leggi complementari (3 luglio) — vedi `FEATURES.md` §15 |
| 10 | Giurisprudenza Cassazione 249.468 sentenze | Solr API, 2020–2026 |
| 11 | Giurisprudenza TAR 30.094 sentenze | OpenGA CKAN API (31 dataset, 2023–2026) |
| 11b | Giurisprudenza Consiglio di Stato 14.729 sentenze | OpenGA CKAN API (2023–2026) |
| 12 | Giurisprudenza Corte dei Conti 267 sentenze | CdcWebApi + PDF reali |
| 12b | Giurisprudenza Corte Costituzionale 22.331 pronunce | Open data ZIP, 1956–oggi |
| 13 | Grafo sentenza→norma: **464.603 nodi, 2.302.324 archi** (verificato 3 luglio) | `workspaces/jurisprudence_graph.json` — molto più grande dei 733.598 archi dell'ultimo snapshot; la voce "da ricostruire" non è più accurata, ma non è chiaro chi/quando abbia rilanciato il rebuild |
| 13b | Grafo legale norma↔norma: **307.325 nodi, 666.291 archi** (verificato 3 luglio) | `workspaces/mio-studio/indices/graph.json` — RINVIA/ABROGA/MODIFICA |
| 14 | Visualizzazione grafo interattiva HTML | pyvis, top 30 norme |

### Valutazione

| # | Funzionalità | Dettaglio |
|---|-------------|---------|
| 15 | Golden Test Set v1 — Penale Tributario | 10 query, prima sessione (senza giurisprudenza) |
| 16 | Golden Test Set v2 — con giurisprudenza | 6/10 PASS, 10/10 fonti giurisprudenziali |
| 17 | Script generazione documento Word automatico | generate_golden_v2.js |

---

## 🔄 In corso / prossimi sprint

### Priorità ALTA

| # | Funzionalità | Effort | Note |
|---|-------------|--------|------|
| 18 | ~~**Frontend web MVP**~~ | — | **Completato**: Chat (streaming SSE per fase), Dashboard, Documents, Graph, History, Settings, Wiki, Istituti — vedi `06-frontend.md` e FEATURES.md §12 |
| 19 | ~~Caricamento documenti studio reali~~ | — | **Parzialmente fatto**: 1.061 documenti caricati via `POST /ingest`, ma non indicizzati (vedi DT-7) — non chiudere finché DT-7 non è risolto |
| 20 | Cron settimanale automatico | 2 ore | `weekly_jurisprudence_update.py` + Windows Task Scheduler o cron — ancora non attivo |

### Priorità MEDIA

| # | Funzionalità | Effort | Note |
|---|-------------|--------|------|
| 21 | ~~TAR Playwright — termini bloccati~~ | — | **Risolto** con OpenGA CKAN (import_openga.py) |
| 22 | Autenticazione API (JWT / API key) | 3 giorni | Multi-tenant per più studi legali |
| 23 | ~~Streaming risposta LLM (SSE)~~ | — | **Completato**: `POST /query/stream` con Sequential IQRAC a 4 fasi |
| 24 | Endpoint `GET /wiki` per browsing | 1 giorno | Serve al frontend per wiki viewer |
| 25 | ~~Rebuild grafo dopo nuovi import~~ | — | **Verificato fatto** (numeri correnti superiori allo snapshot di giugno, vedi riga 13 sopra) — non chiaro quando/da chi, da confermare |

### Priorità BASSA

| # | Funzionalità | Effort | Note |
|---|-------------|--------|------|
| 26 | Dashboard metriche | 1 settimana | Pass rate, tempi risposta, gap analysis |
| 27 | Export wiki in PDF/DOCX | 2 giorni | `scripts/wiki_export.py` esiste già |
| 28 | Versioning sentenze (aggiornamenti Cassazione) | 2 giorni | Gestire sentenze modificate/ritirate |
| 29 | Ricerca full-text nella wiki | 1 giorno | `GET /wiki?q=...` con BM25 su wiki_pages |
| 30 | Notifiche push nuove sentenze rilevanti | 1 settimana | Pattern matching su topic studio |

---

## 🧱 Debito tecnico

| # | Problema | Impatto | Fix |
|---|---------|---------|-----|
| DT-1 | `chunks` collection in MongoDB vuota / stale | Basso | Svuotarla o rimuoverla |
| DT-2 | `wiki_pages` da sessioni vecchie in `aiura_legal_lab_db` | Basso | Svuotare e far ripopolare |
| DT-3 | Script probe/debug (`_probe_*.py`) nella cartella scripts | Basso | Spostare in `scripts/_dev/` |
| DT-4 | Indici BM25/Vector non allineati dopo migrazione DB | Medio | Migliorato (rebuild fatto per normattiva dopo fix id deterministico chunk, 3 luglio) — verificare dottrina/giurisprudenza |
| DT-5 | `LMStudio_MODEL` hardcoded in alcune configurazioni | Basso | Centralizzare in settings |
| DT-6 | Corte dei Conti: scan di 300 pagine anche per sync 7gg | Basso | Aggiungere cursore pagina in sync_state |
| DT-7 | 1.061 documenti studio `is_chunked=True` ma 0 chunk `corpus=studio` in KB | Alto | Documenti caricati invisibili al retrieval — da investigare (scoperto 3 luglio, non ancora causa nota) |
| DT-8 | Settore "lavoro" a 0/193 istituti e assente dai domini eval | Medio | Verificare copertura normativa di base (Statuto Lavoratori ecc.) prima di mappare istituti |
| DT-9 | Punti Qdrant orfani sospetti dopo migrazione id deterministico chunk normattiva | Medio | +447k punti non spiegati (stima 3 luglio) — mai confermati/puliti |
| DT-10 | Filtro settore non applicato all'espansione grafo (`GraphRetriever.expand()`) | Medio | Rumore cross-settore residuo anche dopo i fix di giugno-luglio al filtro BM25/Vector |

---

## 📊 Metriche attuali (3 luglio 2026, verificate su MongoDB)

| Metrica | Valore |
|---------|--------|
| Documenti normattiva (`normattiva_docs`) | **170.857** (era 166.822) |
| Chunk `corpus=normattiva` | 453.458 |
| Chunk `corpus=dottrina` | 178.795 |
| Chunk `corpus=giurisprudenza` | 1.176.698 |
| Chunk `corpus=massimario` | 35.245 |
| Chunk `corpus=studio` | **0** ⚠️ (1.061 documenti studio marcati `is_chunked=True` — anomalia, vedi debito tecnico DT-7) |
| Chunk totali (`chunks`) | 1.844.196 |
| Istituti giuridici mappati | **193** (nuova metrica — 0 su settore "lavoro") |
| Sentenze in KB | **316.889** |
| — Cassazione | 249.468 |
| — TAR (OpenGA) | 30.094 |
| — Consiglio di Stato (OpenGA) | 14.729 |
| — Corte Costituzionale (open data) | 22.331 |
| — Corte dei Conti | 267 |
| Archi grafo sentenza→norma | **2.302.324** (464.603 nodi) — non più "da ricostruire" |
| Archi grafo legale norma↔norma | **666.291** (307.325 nodi) |
| Eval retrieval (gate Fase 2+3, 17 giugno) | G=0.780 R=0.767, pass 100% (20/20) — non ancora rimisurato dopo le aggiunte del 3 luglio |
| Golden test PASS rate | 60% (6/10) — dato di giugno, non aggiornato in questa sessione |
| Golden test fonti giurisp. | 100% (10/10) — dato di giugno |
| Tempo risposta medio | ~30s (qwen2.5-7b locale) — non rimisurato |
| Documenti studio caricati | **1.061** (`documents`, `is_chunked=True`) ma **0 chunk indicizzati** (vedi sopra) |

---

## 🔮 Vision a 6 mesi

1. ~~**Frontend** operativo con chat legale + upload documenti~~ — completato (§18); l'upload funziona ma l'indicizzazione dei documenti studio no (DT-7)
2. **Multi-tenant**: più studi legali con workspace isolati
3. ~~**Corte Costituzionale** integrata~~ — completato via open data (22.331 pronunce)
4. ~~**TAR** completo~~ — completato via OpenGA CKAN (30.094 + 14.729 CdS)
5. **Normattiva aggiornata** automaticamente (cron mensile) — ancora manuale, +4.035 documenti dall'ultimo aggiornamento sono stati scaricati a mano
6. **Wiki matura**: 500+ pagine da sessioni reali — `wiki_pages` risulta a 0 documenti (verificato 3 luglio), invariato da DT-2
7. **Dashboard**: metriche per monitorare qualità e performance
8. ~~**Rebuild grafo** con 316k sentenze per sfruttare la nuova copertura~~ — numeri attuali (2,3M archi) indicano che è avvenuto, da confermare
