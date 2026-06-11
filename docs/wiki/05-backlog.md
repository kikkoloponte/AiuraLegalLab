# Backlog aggiornato

Aggiornato al **5 giugno 2026**.

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
| 9 | Normattiva 166.822 articoli | Copiato da legal_lab, con URN NIR |
| 10 | Giurisprudenza Cassazione 249.468 sentenze | Solr API, 2020–2026 |
| 11 | Giurisprudenza TAR 30.094 sentenze | OpenGA CKAN API (31 dataset, 2023–2026) |
| 11b | Giurisprudenza Consiglio di Stato 14.729 sentenze | OpenGA CKAN API (2023–2026) |
| 12 | Giurisprudenza Corte dei Conti 267 sentenze | CdcWebApi + PDF reali |
| 12b | Giurisprudenza Corte Costituzionale 22.331 pronunce | Open data ZIP, 1956–oggi |
| 13 | Grafo sentenza→norma (733.598 archi) | NetworkX JSON, 58k+61k nodi (da ricostruire) |
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
| 18 | **Frontend web MVP** (in corso) | ~1 settimana rimasta | Chat, Dashboard, Upload, Wiki, History già scaffoldate — vedi `06-frontend.md` |
| 19 | Caricamento documenti studio reali | 1 giorno | `POST /ingest` con PDF avvocato |
| 20 | Cron settimanale automatico | 2 ore | `weekly_jurisprudence_update.py` + Windows Task Scheduler o cron |

### Priorità MEDIA

| # | Funzionalità | Effort | Note |
|---|-------------|--------|------|
| 21 | ~~TAR Playwright — termini bloccati~~ | — | **Risolto** con OpenGA CKAN (import_openga.py) |
| 22 | Autenticazione API (JWT / API key) | 3 giorni | Multi-tenant per più studi legali |
| 23 | Streaming risposta LLM (SSE) | 2 giorni | `POST /query/stream` per frontend reattivo |
| 24 | Endpoint `GET /wiki` per browsing | 1 giorno | Serve al frontend per wiki viewer |
| 25 | Rebuild grafo dopo nuovi import | 1 ora | `build_jurisprudence_graph.py --rebuild` — necessario dopo OpenGA + CorteCost |

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
| DT-4 | Indici BM25/Vector non allineati dopo migrazione DB | Medio | Rebuild con `--rebuild` flag |
| DT-5 | `LMStudio_MODEL` hardcoded in alcune configurazioni | Basso | Centralizzare in settings |
| DT-6 | Corte dei Conti: scan di 300 pagine anche per sync 7gg | Basso | Aggiungere cursore pagina in sync_state |

---

## 📊 Metriche attuali (5 giugno 2026)

| Metrica | Valore |
|---------|--------|
| Articoli normattiva | 166.822 |
| Sentenze in KB | **316.889** |
| — Cassazione | 249.468 |
| — TAR (OpenGA) | 30.094 |
| — Consiglio di Stato (OpenGA) | 14.729 |
| — Corte Costituzionale (open data) | 22.331 |
| — Corte dei Conti | 267 |
| Archi nel grafo | 733.598 (da ricostruire) |
| BM25 documenti totali | 102.684 (da ricostruire) |
| Qdrant dimensione | ~2 GB |
| Golden test PASS rate | 60% (6/10) |
| Golden test fonti giurisp. | 100% (10/10) |
| Tempo risposta medio | ~30s (qwen2.5-7b locale) |
| Documenti studio caricati | 0 |

---

## 🔮 Vision a 6 mesi

1. **Frontend** operativo con chat legale + upload documenti (in corso)
2. **Multi-tenant**: più studi legali con workspace isolati
3. ~~**Corte Costituzionale** integrata~~ — completato via open data (22.331 pronunce)
4. ~~**TAR** completo~~ — completato via OpenGA CKAN (30.094 + 14.729 CdS)
5. **Normattiva aggiornata** automaticamente (cron mensile)
6. **Wiki matura**: 500+ pagine da sessioni reali
7. **Dashboard**: metriche per monitorare qualità e performance
8. **Rebuild grafo** con 316k sentenze per sfruttare la nuova copertura
