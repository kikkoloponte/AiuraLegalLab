# Baseline Pre-Fase1 — 2026-06-12

## Configurazione

| Parametro | Valore |
|-----------|--------|
| Branch | `feat/retrieval-fase1` |
| Commit HEAD | `e5c3720` (Fase 0 integrata) |
| Data | 2026-06-12T09:51Z |
| Workspace | `mio-studio` |
| `QDRANT_URL` | `http://localhost:6333` |

## Stato Infrastruttura

| Servizio | Stato |
|----------|-------|
| Qdrant server | ✅ green |
| MongoDB (`aiura_legal_lab_db`) | ✅ operativo |
| API FastAPI (`:8765`) | ❌ non attiva — LLM bench saltato (contingenza) |

## Conteggi Qdrant

| Collection | Punti |
|------------|-------|
| `legal_docs` | **1.513.368** |

## Conteggi MongoDB

| Collection | Documenti |
|------------|-----------|
| `jurisprudence` | 316.889 |
| `chunks` (totale) | 457.479 |
| `chunks` corpus=normattiva | ~278.684 |
| `chunks` corpus=dottrina | ~178.795 |
| `chunks` corpus=giurisprudenza | **0** (da creare in Fase 1) |

## Struttura Chunk Attuale (Pre-Fase1)

Ogni sentenza produce **3 chunk monolitici**:
- `{hex16}_massima` — testo massima (tipicamente <200 token)
- `{hex16}_motivazione` — testo motivazione (~2.700 token, **troncato a 128 token nell'embedding**)
- `{hex16}_dispositivo` — testo dispositivo (<100 token)

BM25 indicizza solo `text[:200]` — tutta la motivazione oltre i primi 200 caratteri è **invisibile**.

## Benchmark LLM

Non eseguito: API LLM (`:8765`) non attiva al momento della baseline.
Come da **Piano di Contingenza** (Infrastruttura Down), si procede con i test unitari isolati.
Il benchmark post-fase1 sarà eseguito a completamento con API attiva.

## Note rispetto a `fase0_post/`

Il run `fase0_post` era erroneamente solo-BM25 (Qdrant non raggiungibile).
Questo baseline conferma Qdrant attivo con 1.513.368 punti — il retrieval ibrido
è operativo. Il delta atteso post-fase1 è sul retrieval delle motivazioni profonde
(chunk index >0), non misurabili con benchmark LLM offline.
