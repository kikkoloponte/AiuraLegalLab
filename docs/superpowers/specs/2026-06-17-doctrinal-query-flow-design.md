# Doctrinal Query Flow — Design Spec
**Data**: 2026-06-17  
**Branch target**: `feat/retrieval-fase1`  
**Status**: approvato, pronto per implementazione

---

## Problema

Il pipeline IQRAC (4 fasi sequenziali) è progettato per domande su casi concreti con fatti da ricostruire. Su domande astratte/dottrinali ("in quali casi è legittimo X?", "quali sono i presupposti di Y?") la Fase 1 FRAMING inventa fatti inesistenti in `RICOSTRUZIONE_FATTO`, producendo un'analisi strutturalmente sbagliata.

---

## Soluzione: flusso dottrinale parallelo

Due percorsi distinti selezionati da un classificatore LLM leggero (Phase 0):

```
Query → [Phase 0: QueryTypeClassifier] → "case" → IQRAC standard (invariato)
                                       → "doctrine" → DOTTRINALE (Fase 1 alternativa)
```

Fase 2, 3, 4 sono identiche in entrambi i percorsi.

---

## Componenti

### 1. `QueryTypeClassifier` — nuovo modulo

**File**: `aiura_legal/agents/query_classifier.py`

```python
class QueryTypeClassifier:
    async def classify(self, query: str) -> Literal["case", "doctrine"]
```

**Prompt LLM** (system ~50 token, output JSON a 1 campo):
```
System: Classifica la domanda legale italiana.
  "doctrine" = domanda astratta su istituto giuridico, presupposti normativi,
               orientamenti generali. Segnali: "in quali casi", "quando è legittimo",
               "cosa si intende per", "quali sono i requisiti", "come funziona".
  "case"     = domanda su situazione concreta con fatti specifici da analizzare.
Output esclusivamente: {"query_type": "case"|"doctrine"}
```

**Fallback**: se la chiamata fallisce o il JSON è malformato → `"case"` (nessuna regressione).

**Token attesi**: ~150-200 totali, ~0.3s su qwen2.5-7b.

---

### 2. Fase 1 Dottrinale — prompt alternativo

**Trigger**: `query_type == "doctrine"` in `analyze_sequential()`.

**Step names** prodotti (invece di RICOSTRUZIONE_FATTO / QUALIFICAZIONE / QUESTIONE):

| Step | Contenuto |
|------|-----------|
| `INQUADRAMENTO_ISTITUTO` | Identifica l'istituto giuridico, la norma madre, il settore, l'ambito applicativo |
| `PERIMETRO_DOTTRINALE` | Elenca le sotto-questioni rilevanti (es. buona fede del terzo, profitto del reato, equivalente vs diretto) |
| `QUESTIONE_ANALITICA` | Formula la questione precisa che guida il retrieval di Fase 2 e 3 |

**Schema JSON di output** — identico a Fase 1 FRAMING (stessi campi, nomi step diversi):

```json
{
  "analysis_sections": [
    {"step": "INQUADRAMENTO_ISTITUTO", "content": "...", "citations": []},
    {"step": "PERIMETRO_DOTTRINALE",   "content": "...", "citations": []},
    {"step": "QUESTIONE_ANALITICA",    "content": "...", "citations": []}
  ],
  "settore_giuridico": "penale",
  "questione_retrieval": "...",
  "qualificazione_retrieval": "...",
  "overall_confidence": "HIGH",
  "gaps": []
}
```

`questione_retrieval` e `qualificazione_retrieval` sono i campi consumati da `PhaseRetriever` per le re-query di Fase 2 e 3 — nessuna modifica downstream.

---

### 3. Modifiche a `AnalystAgent.analyze_sequential()`

**File**: `aiura_legal/agents/analyst.py`

- Aggiunge parametro `query_type: Literal["case", "doctrine"] = "case"` — retrocompatibile
- Se `"doctrine"`: carica prompt Fase 1 dottrinale (nuovo `.pi/skills/` o sezione condizionale)
- Il resto del metodo è invariato

---

### 4. Modifiche all'Orchestrator

**File**: `aiura_legal/agents/orchestrator.py`, metodo `run_sequential()`

```python
# Prima di analyze_sequential
classifier = QueryTypeClassifier(self._ollama)
query_type = await classifier.classify(query)
logger.info(f"[Orchestrator Seq] query_type={query_type}")

# Passa il tipo all'analyst
analysis = await self._analyst.analyze_sequential(
    query, packet, query_type=query_type
)
```

`query_type` viene incluso nella response JSON serializzata al frontend:
```python
"query_type": query_type  # "case" | "doctrine"
```

**SSE phase label** per Fase 1 dottrinale: il phase_complete event emette `"FRAMING_DOTTRINA"` invece di `"FRAMING"` così il frontend mostra la label corretta durante lo streaming.

---

### 5. Modifiche Frontend

**`frontend/src/components/chat/ResponseCard.tsx`**

- Aggiunge `query_type?: "case" | "doctrine"` a `LegalResponse`
- Aggiunge label per i nuovi step in `STEP_LABELS`:
  ```ts
  INQUADRAMENTO_ISTITUTO: 'Inquadramento dell\'istituto',
  PERIMETRO_DOTTRINALE:   'Perimetro dottrinale',
  QUESTIONE_ANALITICA:    'Questione analitica',
  ```
- Badge visibile nell'header della risposta accanto al ReviewerBadge:
  - `query_type === "doctrine"` → badge grigio/neutro: **"Analisi dottrinale"**
  - `query_type === "case"` → nessun badge aggiuntivo (comportamento corrente)

**`frontend/src/hooks/useChat.ts`**

- `mapBackendResponse` legge `data.query_type` e lo mappa su `LegalResponse`
- Summary extraction: aggiunge `QUESTIONE_ANALITICA` come candidato per domande dottrinali:
  ```ts
  sections.find((s) => s.step === 'QUESTIONE_ANALITICA') ??
  sections.find((s) => s.step === 'QUESTIONE') ??
  ...
  ```
- `PHASE_LABELS` aggiunge:
  ```ts
  FRAMING_DOTTRINA: 'Fase 1 · Inquadramento dottrinale...',
  ```

---

## Out of scope

- Problema A (S5 citation fake non rilevate): separato, affrontato in sessione dedicata
- Problema B (source_id posizionali in Fase 3/4): separato
- Nessuna modifica al retrieval, BM25, Qdrant, PhaseRetriever

---

## Test

- Unit test `QueryTypeClassifier` con mock LLM: verifica "case" e "doctrine" su esempi
- Unit test fallback: risposta LLM malformata → `"case"`
- Integration test `analyze_sequential(query_type="doctrine")`: verifica che i 3 step dottrinali siano presenti nell'output e `questione_retrieval` sia non vuoto
