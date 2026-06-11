# AiUra LegalLab — Documentazione

> Versione 0.1.0-dev — Aggiornato al 5 giugno 2026

---

## Indice

| # | Documento | Contenuto |
|---|-----------|-----------|
| [01](01-architettura.md) | **Architettura di sistema** | Schema a blocchi, agenti S0–S6, flussi Workflow A/B, stack tecnologico, struttura directory |
| [02](02-installazione.md) | **Installazione e configurazione** | Prerequisiti, setup Python, `.env`, Node.js, build indici, verifica installazione |
| [03](03-avvio-processi.md) | **Avvio processi** | API, sync giurisprudenza, build indici, grafo, update settimanale, utilità CLI |
| [04](04-sorgenti-conoscenza.md) | **Sorgenti della conoscenza** | Normattiva, Giurisprudenza (per fonte), Documenti studio, Wiki, schemi MongoDB |
| [05](05-backlog.md) | **Backlog aggiornato** | Completato, in corso, priorità, debito tecnico, metriche |
| [06](06-frontend.md) | **Frontend — Roadmap** | Requisiti, wireframe MVP, stack React/TypeScript, modifiche backend, stima |

---

## Quick start

```powershell
# 1. Attiva ambiente
cd C:\project\AiUraLegalLab
.venv\Scripts\activate

# 2. Avvia API (LMStudio deve essere già attivo)
python -m aiura_legal.api

# 3. Verifica
curl http://127.0.0.1:8765/health
```

## Knowledge base attuale

| Sorgente | Documenti |
|---------|-----------|
| Normattiva (articoli) | **166.822** |
| Giurisprudenza totale | **316.889** |
| — Cassazione (2020–2026) | 249.468 |
| — TAR (2023–2026, via OpenGA) | 30.094 |
| — Consiglio di Stato (2023–2026) | 14.729 |
| — Corte Costituzionale (1956–oggi) | 22.331 |
| — Corte dei Conti | 267 |
| Prassi AdE | **134** |
| — Circolari (2021–2026) | ~115 |
| — Risoluzioni (2026) | 19 |
| Documenti studio | 0 |
| Archi grafo sent.→norma | **da ricostruire** |

## Database

```
MongoDB: aiura_legal_lab_db (localhost:27017)
├── normattiva_docs    (166.822)
├── jurisprudence      (316.889)
├── sync_state         (4)
└── wiki_pages         (0 — si popola dopo le query)

Indici: workspaces/mio-studio/indices/
├── bm25.pkl           (~700 MB)
└── qdrant/            (~2 GB, o Qdrant server)
```
