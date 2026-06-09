# KB Refactor v3 — Chunk Schema, Classificazione Settore e Context Budget

**Data:** 2026-06-09  
**Autore:** Nicola Grasso  
**Branch target:** main  
**Stato:** Bozza approvata

---

## Contesto e Motivazioni

Il sistema di knowledge base attuale presenta quattro limitazioni operative:

1. **Normattiva "cieca"**: il 97% degli articoli ha `settore=["altro"]` perché i titoli degli atti sono burocratici (es. "DECRETO LEGISLATIVO 1 agosto 2003, n. 259"). Il filtro per area giuridica è inapplicabile senza tagliare fonti rilevanti.

2. **Giurisprudenza priva di settore**: il campo `materia` esiste nei record ma non viene usato per filtrare. Chunk con testo vuoto raggiungono l'indice e producono "gusci vuoti" che costringono a dichiarare gap informativi.

3. **Dottrina monocultura penale**: tutti i 178k chunk dottrina hanno `settore=["penale"]` hardcoded (corpus attuale: Sistema Penale + Diritto Penale Contemporaneo). Query su diritto del lavoro, civile, tributario non trovano supporto dottrinale.

4. **Context window esaurito**: con n_ctx=4096, il RAG attuale (6 chunk normattiva + 4 dottrina) occupa 3.600–3.900 token lasciando solo 200–300 token per la risposta del modello.

---

## Obiettivi del Refactor

- Classificare correttamente il `settore` per normattiva, giurisprudenza e dottrina
- Aggiungere un campo `sommario` per BM25 semantico e context compression
- Portare lo spazio risposta da ~200 token a ~700 token con n_ctx=4096
- Indicizzare il corpus `prassi` già presente in MongoDB ma mai retrieval-integrato
- Ridurre la dimensione dei chunk per corpus densi (dottrina, prassi)

---

## Schema Chunk v3

### Campi aggiunti al modello `Chunk` esistente

```python
sommario: Optional[str] = None
# Frase di 40–60 token LLM-generata che descrive l'oggetto giuridico del chunk.
# Usata da: BM25 indexing, ContextBudgetManager (al posto del full text),
# UI tooltip sulle fonti citate.

settore_confidence: float = 0.0
# 0.0 = default/euristico, 1.0 = classificazione LLM ad alta certezza.
# Usata da PhaseRetriever per filtri soft vs hard.
```

Il campo `settore: List[str]` non cambia struttura — viene solo popolato correttamente.

### Retrocompatibilità

Chunk esistenti con `sommario=None` e `settore_confidence=0.0` continuano a funzionare. Il `ContextBudgetManager` usa full text come fallback se `sommario` è assente. Il filtro settore con confidence < 0.5 non esclude mai un chunk.

---

## Pipeline di Classificazione Batch

Script: `scripts/classify_knowledge_base.py`  
Hardware target: RTX 5080 16GB, modello locale Qwen2.5 32B Q4 (o equivalente)  
Modalità: riprendibile da checkpoint JSON locale

### Idempotenza e Resume

**Requisito:** ogni fase è idempotente — se il job si interrompe, può ripartire dal punto in cui si è fermato senza duplicare lavoro o corrompere dati.

**Meccanismo per fase:**
- **Fasi A, B:** checkpoint file JSON locale (`act_classification.json`, `sommario_progress.json`) con set degli `act_urn` / `chunk_id` già processati. Al riavvio, skip degli ID già presenti nel checkpoint.
- **Fase C, D, E:** operazioni `$set` MongoDB sono idempotenti per natura — rieseguire sovrascrive con lo stesso valore. Skip automatico via query `{"settore_confidence": {"$gt": 0}}` (già classificati).
- **Tutti i `$set` bulk** usano `upsert=False` — non creano mai documenti nuovi, aggiornano solo chunk esistenti.

### Fase A — Normattiva: classificazione a livello di atto (26.217 atti)

**Input per ogni `act_urn`:** `titolo` + primi 5 `titolo_articolo`  
**Prompt LLM:**
```
Classifica questo atto normativo italiano nei settori giuridici pertinenti.
Settori disponibili: penale, civile, amministrativo, lavoro, tributario,
processuale, costituzionale, altro.
Rispondi ONLY con JSON: {"settori": [...], "confidence": 0.0-1.0}
```
**Output:** `act_classification.json` (checkpoint locale — append-only, non sovrascritto)  
**Resume:** al riavvio carica il checkpoint, skippa `act_urn` già presenti  
**Propagazione:** `$set` bulk su tutti i chunk con quell'`act_urn`  
**Stima:** ~26k chiamate × 0.5s = ~3.6 ore

### Fase B — Normattiva: generazione sommario (articoli normativi)

**Target:** chunk con `testo_tipo="normativo"` (~100k su 166k totali)  
**Skip:** `testo_tipo="formula_ridondante"` — non portano contenuto classificatorio  
**Prompt LLM:** *"In una frase di massimo 60 token, descrivi l'oggetto giuridico di questo articolo."*  
**Parallelismo:** batch da 8 richieste concorrenti  
**Resume:** `sommario_progress.json` traccia i `chunk_id` completati; al riavvio skip chunk già processati  
**Stima:** ~100k × 0.3s / 8 = ~1 ora

### Fase C — Giurisprudenza: settore rule-based (zero LLM)

Mapping deterministico `organo → settori`:

```python
ORGANO_SETTORE_MAP = {
    "cassazione":      (["civile", "penale"], 0.6),       # disambiguato via materia
    "tar":             (["amministrativo"], 0.9),
    "consiglio_stato": (["amministrativo"], 0.95),
    "corte_cost":      (["costituzionale"], 0.95),
    "corte_conti":     (["amministrativo", "tributario"], 0.85),
}
```

Per `cassazione`: se `materia` contiene keyword penali → `["penale"]`, confidence 0.9.  
**Filtro vuoti:** chunk con `len(text) < 20` esclusi dall'indicizzazione (non da MongoDB).

### Fase D — Dottrina: classificazione document-level (pochi documenti)

Per ogni documento dottrina distinto, invia `chunk_index=0` al modello locale.  
Propaga `settore` + `settore_confidence` a tutti i chunk del documento.  
Rimuove il default hardcoded `["penale"]`.

### Fase E — Prassi: nuovo corpus

Crea chunk da `PrassiDocument` esistenti in MongoDB:  
- Chunk size: 256 tok, overlap 32  
- `corpus="prassi"`  
- Settore derivato da `fonte` (ADE → tributario, INPS/MinLavoro → lavoro)  
- Genera `sommario` LLM  
- Aggiunge `bm25_prassi.pkl` e collection Qdrant `prassi`

---

## Adaptive Chunking per Corpus

| Corpus | Chunk size | Overlap | Note |
|--------|-----------|---------|------|
| normattiva | articolo intero se ≤ 400 tok; altrimenti 256/32 | 32 | 1 articolo = 1 concetto |
| giurisprudenza | invariato — massima/motivazione/dispositivo | — | struttura semantica già corretta |
| dottrina | 256 / 32 | 32 | argomenti densi, sommario compensa |
| prassi | 256 / 32 | 32 | circolari con punti numerati |
| studio | invariato 512 / 64 | 64 | documenti liberi |

**Logica normattiva:**
```python
if token_count <= 400:   # ~80% degli articoli
    chunks = [full_article]
elif token_count <= 800:
    chunks = split(size=256, overlap=32)
else:
    chunks = split(size=256, overlap=64)
```

---

## Retrieval — Modifiche

### BM25: campo indicizzato

```python
# Prima: solo text
# Dopo:
indexed_text = f"{sommario} {titolo_articolo} {text[:200]}"
```

Questo rende il BM25 resistente al rumore da keyword: il D.Lgs 30/2001 (carriera diplomatica) avrà sommario *"Ordinamento corpo diplomatico — trattamento economico"*, non le keyword di un licenziamento.

### PhaseRetriever: filtri soft/hard

```python
if settore_confidence >= 0.7:
    # filtro hard: escludi chunk fuori settore
elif settore_confidence >= 0.4:
    # filtro soft: includi ma penalizza nel RRF score (×0.5)
else:
    # nessun filtro: chunk sempre candidato
```

Fallback automatico: se filtro hard restituisce < 3 chunk, degradazione a filtro soft.

### Corpus prassi nel retrieval

Fase 2 (normativa) include prassi con peso addizionale leggero:

```
normattiva: BM25 0.60 / Vector 0.20 / Graph 0.15
prassi:     contribuisce 0.05 al RRF pool finale (segnale di supporto, non sostituto)
```

---

## Context Budget Manager (nuovo componente)

**File:** `aiura_legal/core/retrieval/context_budget.py`

Assembla il prompt RAG rispettando un budget fisso per n_ctx=4096:

| Slot | Token | Contenuto |
|------|-------|-----------|
| System prompt | ~300 | fisso |
| Phase prompt IQRAC | ~400 | fisso per fase |
| Fonti normativa | ~800 | top-1 full text (300 tok) + top-3 sommario (40 tok ×3) |
| Fonti giurisprudenza | ~600 | top-1 full text (250 tok) + top-2 sommario (40 tok ×2) |
| Fonti dottrina/prassi | ~200 | top-2 sommario (40 tok ×2) |
| **Spazio risposta** | **~700** | da ~200–300 tok attuali |

**Algoritmo:** ordina chunk per RRF score decrescente. Il primo chunk per corpus ottiene full text. Gli altri ricevono `sommario`. Se `sommario=None`, usa `text[:150]` come fallback.

---

## Testing Strategy

### Unit — `tests/test_chunk_schema_v3.py`
- `sommario`, `settore_confidence` opzionali e retrocompatibili
- Mapping `ORGANO_SETTORE_MAP` per tutti gli organi
- Filtro soft/hard con confidence threshold
- `ContextBudgetManager` rispetta il budget entro ±50 token

### Integration — `tests/test_classify_batch.py`
- Fase A su campione 50 atti (mock LLM)
- Checkpoint resume: interrompi a metà, riprendi, verifica nessun duplicato
- `$set` bulk non corrompe `text`, `embedding`, `corpus` esistenti

### Regression retrieval — `eval/bench_questions.jsonl`
- Esegui bench su 10 query rappresentative prima e dopo rebuild
- Metrica: precision@3 non peggiora su query già funzionanti
- Query di controllo: 2 lavoro, 2 civile, 2 penale, 2 amministrativo, 2 cross-settore

---

## Dipendenze e Ordine di Esecuzione

```
classify_knowledge_base.py
  ├── Fase A: act_classification.json  (checkpoint)
  ├── Fase B: sommario normattiva      (richiede Fase A completata)
  ├── Fase C: giurisprudenza settore   (indipendente)
  ├── Fase D: dottrina settore         (indipendente)
  └── Fase E: prassi corpus            (indipendente)
      ↓
rebuild_knowledge_base.py  (riscrive BM25 pkl + Qdrant payload)
      ↓
Attivare AIURA_SETTORE_FILTER=1 in .env
```

Le fasi C, D, E sono parallelizzabili. La Fase B dipende da A (per non sovrascrivere il settore appena classificato).

---

## File Modificati / Creati

| File | Tipo | Motivo |
|------|------|--------|
| `aiura_legal/ingestion/mongodb/models.py` | modifica | aggiunge `sommario`, `settore_confidence` |
| `aiura_legal/core/retrieval/bm25_retriever.py` | modifica | indicizza `sommario + titolo_articolo + text[:200]` |
| `aiura_legal/core/retrieval/phase_retriever.py` | modifica | filtri soft/hard, include prassi |
| `aiura_legal/core/retrieval/context_budget.py` | nuovo | `ContextBudgetManager` |
| `scripts/classify_knowledge_base.py` | nuovo | pipeline batch Fasi A–E |
| `tests/test_chunk_schema_v3.py` | nuovo | unit test schema |
| `tests/test_classify_batch.py` | nuovo | integration test batch |

---

## Non in Scope

- Nuovi scraper per dottrina civile/lavoro/tributario (la dottrina rimane prevalentemente penale fino a nuovi upload)
- UI per visualizzare `settore_confidence` per singola fonte
- `settore_confidence` esposto nelle API pubbliche (solo uso interno al retrieval)
- Corpus `studio`: nessun cambiamento (documenti utente trattati come testo libero)
