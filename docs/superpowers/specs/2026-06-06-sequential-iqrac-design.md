# Sequential IQRAC + Per-Phase Retrieval + SSE Streaming

**Data:** 2026-06-06  
**Obiettivo:** Migliorare la qualità del ragionamento giuridico di AiUra su modelli locali 7B,
senza ricorrere a modelli cloud o hardware ad alte prestazioni.

---

## Problema

Il modello `qwen2.5:7b` con `analyze()` (singola chiamata LLM, 9 step IQRAC in 4500 token)
produce risposte circolari: ogni step ripete la domanda invece di aggiungere ragionamento nuovo.
Un 7B non ha la capacità di "tenere" nove step concettuali complessi in un unico contesto.

Il confronto con Gemini/Claude mostra che la differenza non è nel modello in sé, ma
nell'approccio: grandi modelli ragionano implicitamente step-by-step grazie al context window
enorme. Con un 7B locale occorre rendere esplicita quella sequenzialità.

---

## Soluzione: Approccio C — Sequential IQRAC + Retrieval per fase + SSE

### Principio

Dividere i 9 step IQRAC in **4 fasi sequenziali**. Ogni fase:
1. Riceve il contesto delle fasi precedenti (carry-over)
2. Fa un retrieval mirato sulla sua specifica esigenza
3. Produce un output focalizzato su 2-3 step (non 9)
4. Emette un evento SSE appena completata (streaming progressivo)

### Le 4 fasi

| Fase | Step IQRAC | Retrieval | Focus |
|------|-----------|-----------|-------|
| **1 — Framing** | RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE | Nessuno | Analizza solo la domanda, distilla la QUESTIONE giuridica precisa |
| **2 — Normativa** | FONTI_NORMATIVE, INTERPRETAZIONE | Re-query mirata su `corpus=normattiva` usando la QUESTIONE di Fase 1 | Cita articoli specifici, applica criteri interpretativi |
| **3 — Giurisprudenza** | GIURISPRUDENZA | Re-query mirata su `corpus=giurisprudenza` usando QUALIFICAZIONE + QUESTIONE | Cita sentenze reali (ThyssenKrupp, Formula Frank, ecc.) |
| **4 — Sintesi** | SUSSUNZIONE, OBIEZIONI, CONCLUSIONE | Nessuno | Ragiona sul corpus delle fasi 1-3, produce conclusione operativa |

La **re-query per fase** è la chiave: invece di usare la query originale grezza
(che produce fonti generiche), le fasi 2-3 riformulano la ricerca usando l'output
delle fasi precedenti come query più precisa.

---

## Architettura

```
POST /query/stream  (nuovo endpoint SSE)
        │
        ▼
LegalOrchestrator.run_sequential()
        │
        ├─ S1 Clarifier (invariato)
        │
        ├─ S2 Retrieval bifasico (invariato — produce packet iniziale)
        │
        ├─ SequentialAnalyst.analyze_sequential()
        │       │
        │       ├─ FASE 1: Framing
        │       │     prompt: query sola, senza fonti
        │       │     output: {RICOSTRUZIONE_FATTO, QUALIFICAZIONE, QUESTIONE}
        │       │     SSE event: phase_complete {phase:1, sections:[...]}
        │       │
        │       ├─ PhaseRetriever.retrieve_normativa(questione_f1)
        │       │     re-query con QUESTIONE come testo di ricerca
        │       │     corpus=normattiva, top_k=6
        │       │
        │       ├─ FASE 2: Normativa
        │       │     prompt: contesto_f1 + fonti_normativa_fresche
        │       │     output: {FONTI_NORMATIVE, INTERPRETAZIONE}
        │       │     SSE event: phase_complete {phase:2, sections:[...]}
        │       │
        │       ├─ PhaseRetriever.retrieve_giurisprudenza(qualificazione + questione)
        │       │     re-query con QUALIFICAZIONE+QUESTIONE come testo di ricerca
        │       │     corpus=giurisprudenza, top_k=6
        │       │
        │       ├─ FASE 3: Giurisprudenza
        │       │     prompt: contesto_f1+f2 + sentenze_fresche
        │       │     output: {GIURISPRUDENZA}
        │       │     SSE event: phase_complete {phase:3, sections:[...]}
        │       │
        │       └─ FASE 4: Sintesi
        │             prompt: contesto_f1+f2+f3 (nessun retrieval nuovo)
        │             output: {SUSSUNZIONE, OBIEZIONI, CONCLUSIONE}
        │             SSE event: phase_complete {phase:4, sections:[...]}
        │
        └─ S5 Reviewer (invariato, opera sull'output merged)
                SSE event: done {verdict, confidence, warnings}
```

---

## Componenti da creare/modificare

### 1. Nuovi Pi Skills (`.pi/skills/`)

Quattro file, uno per fase. Ogni skill ha un prompt focalizzato su 2-3 step,
con istruzioni esplicite su cosa NON fare (non anticipare fasi successive).

- `legal_analyst_framing.md` — step 1-3, nessuna fonte obbligatoria
- `legal_analyst_normativa.md` — step 4-5, usa SOLO fonti normativa
- `legal_analyst_giurisprudenza.md` — step 6, usa SOLO sentenze
- `legal_analyst_sintesi.md` — step 7-9, ragiona su output precedenti

### 2. `PhaseRetriever` (nuovo, `aiura_legal/core/retrieval/phase_retriever.py`)

Wrapper leggero su `HybridRetriever`. Due metodi:

```python
class PhaseRetriever:
    def __init__(self, retriever: HybridRetriever) -> None: ...

    def retrieve_normativa(self, query: str, top_k: int = 6) -> list[SearchResult]:
        """Re-query su corpus=normattiva con pesi BM25-heavy."""

    def retrieve_giurisprudenza(self, query: str, top_k: int = 6) -> list[SearchResult]:
        """Re-query su corpus=giurisprudenza con pesi Vector-heavy."""
```

Usa `HybridRetriever.search()` con `chunk_filter={"corpus": "normattiva"|"giurisprudenza"}`.
Non costruisce un nuovo Research Packet — restituisce `list[SearchResult]` diretta.

### 3. `SequentialAnalyst` (nuovo metodo in `analyst.py`)

Nuovo metodo `analyze_sequential()` su `AnalystAgent`. Aggiunge:
- `PhaseRetriever` come dipendenza opzionale
- 4 chiamate LLM sequenziali (pattern già stabilito da `analyze_deep`)
- Carry-over context: ogni fase riceve un riassunto compatto (≤400 char/step)
  delle fasi precedenti, non l'output completo (per non saturare il context)
- Ritorna `AsyncGenerator[PhaseResult, None]` per permettere lo streaming

```python
@dataclass
class PhaseResult:
    phase: int                        # 1-4
    name: str                         # "FRAMING" | "NORMATIVA" | "GIURISPRUDENZA" | "SINTESI"
    sections: list[AnalysisSection]
    sources_used: list[str]           # source_id delle fonti usate in questa fase
    duration_s: float
    parse_ok: bool
```

### 4. Nuovo endpoint SSE `POST /query/stream` (`app.py`)

```python
@app.post("/query/stream")
async def query_stream(req: QueryRequest) -> StreamingResponse:
    """SSE: emette eventi per fase man mano che S3 completa ogni step."""
```

**Formato eventi SSE:**

```
event: retrieval_done
data: {"sources_count": 12, "confidence": "HIGH"}

event: phase_start
data: {"phase": 1, "name": "FRAMING", "steps": ["RICOSTRUZIONE_FATTO", "QUALIFICAZIONE", "QUESTIONE"]}

event: phase_complete
data: {"phase": 1, "name": "FRAMING", "sections": [...], "duration_s": 3.2}

event: phase_start
data: {"phase": 2, "name": "NORMATIVA", "steps": ["FONTI_NORMATIVE", "INTERPRETAZIONE"]}

... (fasi 3-4 analoghe)

event: review_done
data: {"verdict": "PASS", "action": "DELIVER", "warnings": []}

event: done
data: {"overall_confidence": "HIGH", "duration_total_s": 48.1}
```

L'endpoint `/query` esistente **non cambia** — rimane disponibile per client
che non supportano SSE. Il `mode="sequential"` può essere aggiunto anche lì
(risposta bloccante completa).

### 5. Orchestratore (`orchestrator.py`)

Aggiunta di `run_sequential()` — metodo async generator che:
1. Esegue S1, S2 (invariati, sincroni)
2. Chiama `SequentialAnalyst.analyze_sequential()` iterando le fasi
3. Yielda ogni `PhaseResult` appena disponibile
4. Esegue S5 sull'output merged finale

Il metodo `run()` esistente non cambia.

---

## Flusso dati dettagliato

```
query: "Qual è il confine tra dolo eventuale e colpa cosciente?"

FASE 1 — Framing (no fonti)
  Input:  query originale
  Output: QUESTIONE = "La questione consiste nello stabilire il criterio
          psicologico-volitivo che distingue l'accettazione del rischio
          (dolo eventuale) dalla fiducia nell'evitamento (colpa cosciente),
          con riferimento all'art. 43 c.p. e all'evoluzione giurisprudenziale."

  ↓ QUESTIONE usata come query di retrieval

FASE 2 — Normativa (re-query su normattiva con QUESTIONE)
  Retrieval: "criterio psicologico volitivo dolo eventuale colpa cosciente art. 43"
  Fonti attese: art. 43 c.p., art. 133 c.p., art. 61 n.3 c.p., art. 589 c.p.
  Output: FONTI_NORMATIVE con articoli specifici + INTERPRETAZIONE con criteri letterale/sistematico

  ↓ QUALIFICAZIONE + QUESTIONE usate come query

FASE 3 — Giurisprudenza (re-query su giurisprudenza)
  Retrieval: "dolo eventuale accettazione rischio formula Frank ThyssenKrupp"
  Fonti attese: Cass. SS.UU. 38343/2014, Cass. n.36663/2023, ecc.
  Output: GIURISPRUDENZA con massime reali e criteri indiziari

FASE 4 — Sintesi (nessun retrieval)
  Input: tutto l'output delle fasi 1-3 (compatto)
  Output: SUSSUNZIONE (A, B, C vs fatti) + OBIEZIONI + CONCLUSIONE operativa
```

---

## Gestione errori e degradazione

- Se Fase N fallisce → le fasi successive ricevono il contesto disponibile + nota gap
- Se il retrieval di fase non trova fonti → la fase usa le fonti del packet iniziale S2
- Se Ollama non risponde → SSE emette `event: error` e chiude lo stream
- `/query` (bloccante) continua a funzionare con `mode="deep"` come fallback

---

## Impatto sulla qualità attesa

Il 7B con 4500 token su 9 step → 500 token/step ≈ 2-3 frasi per step.
Il 7B con 1500 token su 2-3 step → 500-750 token/step ≈ 5-8 frasi focalizzate.

La re-query per fase garantisce che le fonti arrivino al momento giusto:
il modello riceve ThyssenKrupp **nella** fase Giurisprudenza, non sepolto
in un packet generico dove compete con 11 altre fonti.

---

## File da creare/modificare

| File | Tipo | Descrizione |
|------|------|-------------|
| `.pi/skills/legal_analyst_framing.md` | Nuovo | Pi skill Fase 1 |
| `.pi/skills/legal_analyst_normativa.md` | Nuovo | Pi skill Fase 2 |
| `.pi/skills/legal_analyst_giurisprudenza.md` | Nuovo | Pi skill Fase 3 |
| `.pi/skills/legal_analyst_sintesi.md` | Nuovo | Pi skill Fase 4 |
| `aiura_legal/core/retrieval/phase_retriever.py` | Nuovo | PhaseRetriever |
| `aiura_legal/agents/analyst.py` | Modifica | + PhaseResult, analyze_sequential() |
| `aiura_legal/agents/orchestrator.py` | Modifica | + run_sequential() |
| `aiura_legal/api/app.py` | Modifica | + POST /query/stream SSE |
| `tests/test_sequential_analyst.py` | Nuovo | Unit test analyze_sequential() |

---

## Non incluso in questo scope

- Modifica al frontend (UI per mostrare le fasi in tempo reale — sprint separato)
- Cambio modello (rimane qwen2.5:7b — questo è il vincolo)
- Modifica a S1, S4, S5 (invariati)
- Nuovi indici o re-indicizzazione della KB
