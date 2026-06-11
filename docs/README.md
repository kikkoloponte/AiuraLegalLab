# AiUra LegalLab — Indice documentazione

> Punto di ingresso per tutta la documentazione del progetto.
> Aggiornato: 2026-06-10.

## Per iniziare

| Documento | Contenuto |
|-----------|-----------|
| [README principale](../README.md) | Installazione, avvio rapido, esempi API, architettura |
| [FEATURES.md](FEATURES.md) | **Features implementate e roadmap futura** — il documento di riferimento sullo stato del progetto |
| [KNOWLEDGE_BASE_SETUP.md](KNOWLEDGE_BASE_SETUP.md) | Costruzione della knowledge base da zero: normattiva, giurisprudenza, dottrina (tempi, fonti, troubleshooting) |

## Manuale operativo (`wiki/`)

| # | Documento | Contenuto |
|---|-----------|-----------|
| [01](wiki/01-architettura.md) | Architettura di sistema | Schema a blocchi, agenti S0–S6, flussi, stack |
| [02](wiki/02-installazione.md) | Installazione e configurazione | Setup Python, `.env`, Node.js, build indici |
| [03](wiki/03-avvio-processi.md) | Avvio processi | API, sync giurisprudenza, build indici, utilità CLI |
| [04](wiki/04-sorgenti-conoscenza.md) | Sorgenti della conoscenza | Normattiva, giurisprudenza per fonte, schemi MongoDB |
| [05](wiki/05-backlog.md) | Backlog e metriche (2026-06-05) | Stato corrente, debito tecnico, metriche KB — il più aggiornato |
| [06](wiki/06-frontend.md) | Frontend | Requisiti, wireframe, stack React/TypeScript |

## Pianificazione

| Documento | Contenuto |
|-----------|-----------|
| [BACKLOG.md](../BACKLOG.md) | Storico milestone M0–M2 con dettaglio task (aggiornato 2026-05-31) |
| [FEATURES.md → Features future](FEATURES.md#features-future) | Roadmap consolidata: hardening privacy, knowledge base, quality gate, SaaS |

## Design specs (`superpowers/specs/`)

Documenti di design storici, uno per feature, in ordine cronologico
(`YYYY-MM-DD-<feature>-design.md`). Registrano le decisioni architetturali:
non vengono aggiornati dopo l'implementazione — per lo stato corrente fare
riferimento a [FEATURES.md](FEATURES.md).

## Dataset golden test

| File | Contenuto |
|------|-----------|
| [golden_v2_clean.json](golden_v2_clean.json) | Dataset golden test set v2 (input di `scripts/generate_golden_v2.js`) |
| `golden_test_set_*.docx` | Versioni Word del golden set per la validazione con l'avvocato |

I **risultati** delle run golden/eval sono artefatti generati e vivono in
`eval/results/` e `eval/query_results/` (gitignored, riproducibili con
`run_golden_queries.py` e `scripts/run_query_suite.py`).

## Generatori documenti Word

- `generate_manuale.js` + `package.json` — genera il manuale .docx dal contenuto wiki
- `../scripts/generate_docs.js` — genera la documentazione .docx v1
- `../scripts/generate_golden_v2.js` — genera il .docx del golden test set

Gli output .docx generati non sono versionati (riproducibili con `node <script>`).

## Archivio (`archive/`)

Materiale storico non più mantenuto:

- [AiUra_brAInstorming.md](archive/AiUra_brAInstorming.md) — brainstorming iniziale del progetto
