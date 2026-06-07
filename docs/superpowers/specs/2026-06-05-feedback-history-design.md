# Design: Sistema di Feedback e History Completa
**Data:** 2026-06-05
**Stato:** Approvato

---

## Obiettivo

Permettere all'avvocato di valutare ogni risposta del sistema (stelle + tag + nota) e di
rivedere in seguito l'analisi completa. I feedback vengono salvati su MongoDB come patch
in-place sul documento `query_history`, che viene esteso per contenere la risposta strutturata
completa anziché il solo sommario troncato.

---

## 1. Data Model — `query_history`

### 1a. Schema completo del documento

```json
{
  "_id":               "<UUID>",
  "query":             "Testo della domanda dell'avvocato",
  "workspace":         "mio-studio",
  "intent":            "fattispecie_analysis",
  "mode":              "standard | deep",
  "verdict":           "PASS | WARN | FAIL | RE_RETRIEVAL",
  "confidence":        "HIGH | MEDIUM | LOW",

  "answer":            "Testo completo della risposta (non troncato)",
  "analysis_sections": [{ "step": "QUALIFICAZIONE", "content": "...", "citations": [] }],
  "analysis_fase_1":   [...],
  "analysis_fase_2":   [...],
  "sources": [
    {
      "source_id": "urn:nir:...",
      "doc_id":    "...",
      "snippet":   "...",
      "score":     0.87,
      "metadata":  { "articolo": "Art. 1", "titolo": "...", "corpus": "normattiva" }
    }
  ],
  "sources_count":     6,
  "duration_total_s":  4.2,
  "created_at":        "2026-06-05T10:00:00Z",

  "feedback_rating":   4,
  "feedback_tags":     ["Utile", "Citazioni corrette"],
  "feedback_note":     "Manca il riferimento al comma 3.",
  "feedback_at":       "2026-06-05T10:05:00Z"
}
```

I campi `feedback_*` sono **opzionali** — assenti fino al primo (e unico) invio di feedback.

### 1b. Tag fissi ammessi

```
"Utile" | "Parziale" | "Errata" | "Da approfondire" |
"Citazioni corrette" | "Citazioni errate"
```

### 1c. Indici MongoDB

```python
# Query principale: lista workspace × data desc
db["query_history"].create_index(
    [("workspace", 1), ("created_at", -1)], name="ws_date"
)
# Filtro "solo valutate" + ordinamento
db["query_history"].create_index(
    [("workspace", 1), ("feedback_at", -1)], name="ws_feedback_date", sparse=True
)
# Filtro per rating
db["query_history"].create_index(
    [("workspace", 1), ("feedback_rating", 1)], name="ws_rating", sparse=True
)
# Filtro per tag (multikey)
db["query_history"].create_index(
    [("feedback_tags", 1)], name="tags_multikey", sparse=True
)
# Ricerca full-text sulla domanda
db["query_history"].create_index(
    [("query", "text")], name="query_text"
)
```

Tutti gli indici sono idempotenti (`create_index` ignora se già esistente).

---

## 2. Backend

### 2a. Modifiche a `aiura_legal/api/schemas.py`

**`HistoryEntry`** — aggiungere i campi completi:

```python
class HistoryEntry(BaseModel):
    id: str
    query: str
    workspace: str
    intent: str = "fattispecie_analysis"
    mode: str = "standard"
    verdict: str
    confidence: str = "LOW"
    answer: str = ""                        # ← completo (non troncato)
    analysis_sections: list[dict] = []      # ← step IQRAC
    analysis_fase_1:   list[dict] = []
    analysis_fase_2:   list[dict] = []
    sources:           list[dict] = []      # ← fonti complete
    sources_count: int = 0
    duration_total_s: float = 0.0
    created_at: str
    # Feedback (opzionali)
    feedback_rating: int | None = None
    feedback_tags:   list[str] = []
    feedback_note:   str | None = None
    feedback_at:     str | None = None
```

**Nuovo `FeedbackRequest`**:

```python
ALLOWED_TAGS = frozenset({
    "Utile", "Parziale", "Errata",
    "Da approfondire", "Citazioni corrette", "Citazioni errate",
})

class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    tags:   list[str] = Field(default_factory=list)
    note:   str | None = Field(default=None, max_length=500)

    @field_validator("tags")
    @classmethod
    def tags_must_be_allowed(cls, v: list[str]) -> list[str]:
        invalid = set(v) - ALLOWED_TAGS
        if invalid:
            raise ValueError(f"Tag non ammessi: {invalid}")
        return v
```

**`QueryResponse`** — aggiungere `history_id`:

```python
class QueryResponse(BaseModel):
    ...
    history_id: str | None = None   # ← ID del documento query_history appena creato
```

### 2b. Modifiche a `aiura_legal/api/app.py`

**Salvataggio history** (endpoint `/query` e `/query/stream`):

1. Generare `history_id = str(uuid.uuid4())` **prima** di costruire il payload di risposta.
2. Includere `history_id` nel payload SSE / `QueryResponse`.
3. Nel blocco `insert_one`, salvare il documento completo:

```python
history_id = str(uuid.uuid4())

# ... costruzione payload ...

# fire-and-forget
await mongo.db["query_history"].insert_one({
    "_id":               history_id,
    "query":             req.query,
    "workspace":         req.workspace,
    "intent":            req.intent,
    "mode":              req.mode,
    "verdict":           result.reviewer_verdict,
    "confidence":        result.analysis.overall_confidence,
    "answer":            result.answer or "",
    "analysis_sections": [s.__dict__ for s in (result.analysis.sections or [])],
    "analysis_fase_1":   [s.__dict__ for s in (result.analysis_fase_1 or [])],
    "analysis_fase_2":   [s.__dict__ for s in (result.analysis_fase_2 or [])],
    "sources":           [_source_to_dict(s) for s in result.sources],
    "sources_count":     len(result.sources),
    "duration_total_s":  result.duration_total_s,
    "created_at":        datetime.now(timezone.utc).isoformat(),
})
```

**Nuovo endpoint `PATCH /history/{entry_id}/feedback`**:

```python
@app.patch("/history/{entry_id}/feedback", status_code=204, tags=["history"])
async def add_feedback(entry_id: str, body: FeedbackRequest):
    mongo = MongoClient.get()
    doc = await mongo.db["query_history"].find_one({"_id": entry_id})
    if not doc:
        raise HTTPException(404, "Voce non trovata")
    if doc.get("feedback_at"):
        raise HTTPException(409, "Feedback già inviato per questa risposta")
    await mongo.db["query_history"].update_one(
        {"_id": entry_id},
        {"$set": {
            "feedback_rating": body.rating,
            "feedback_tags":   body.tags,
            "feedback_note":   body.note,
            "feedback_at":     datetime.now(timezone.utc).isoformat(),
        }},
    )
```

**Nuovo endpoint `GET /history/{entry_id}`**:

```python
@app.get("/history/{entry_id}", response_model=HistoryEntry, tags=["history"])
async def get_history_entry(entry_id: str):
    mongo = MongoClient.get()
    doc = await mongo.db["query_history"].find_one({"_id": entry_id})
    if not doc:
        raise HTTPException(404, "Voce non trovata")
    return _doc_to_history_entry(doc)   # helper condiviso con list_history
```

### 2c. Nuovo script `scripts/migrate_history_indexes.py`

Script CLI sincrono (PyMongo) che crea i 5 indici descritti in §1c.
Da eseguire una volta sola dopo il deploy:
```bash
python scripts/migrate_history_indexes.py
```

---

## 3. Frontend

### 3a. `useChat.ts` — mappatura `history_id`

In `mapBackendResponse()` aggiungere:
```ts
history_id: String(data.history_id ?? '') || undefined,
```

### 3b. `LegalResponse` (interfaccia in `ResponseCard.tsx`)

```ts
export interface LegalResponse {
  ...
  history_id?: string
}
```

### 3c. `ResponseCard.tsx` — sezione feedback collassabile

In fondo alla card, dopo il blocco fonti, aggiungere `FeedbackSection`:

```
┌─────────────────────────────────────────────────┐
│  [▾ Valuta risposta]                            │  ← bottone toggle
│                                                  │
│  ★ ★ ★ ☆ ☆   (cliccabili, highlight hover)     │  ← espanso
│                                                  │
│  [Utile] [Parziale] [Errata] [Da approfondire]  │
│  [Citazioni corrette] [Citazioni errate]         │  ← chip multi-select
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ Note (opzionale, max 500 car.)           │   │  ← textarea
│  └──────────────────────────────────────────┘   │
│                                    [Invia ▸]    │
└─────────────────────────────────────────────────┘
```

**Dopo il submit** (PATCH 204): il form viene sostituito da un badge permanente:
```
✓ Valutazione salvata  ★★★★☆  [Utile] [Citazioni corrette]
```

Se `history_id` è undefined: bottone "Valuta risposta" disabilitato con tooltip
*"Ricarica la pagina per abilitare la valutazione"*.

Comportamento stelle: hover progressivo (1→5), colore amber, click fisso.
Chip tag: toggle border+background, colore teal quando selezionato.

### 3d. `api/client.ts` — nuova funzione

```ts
export async function submitFeedback(
  historyId: string,
  rating: number,
  tags: string[],
  note?: string,
): Promise<void> {
  const res = await fetch(`/api/history/${historyId}/feedback`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, tags, note }),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
}
```

### 3e. `History.tsx` e `useHistory.ts`

**`useHistory.ts`**:
- Aggiungere parametro `feedbackOnly?: boolean` alla query
- Passare `?feedback_only=true` all'endpoint `/history` quando attivo
- `HistoryEntry` type: aggiungere campi feedback + risposta completa

**`History.tsx`**:
- Chip toggle **"Solo valutate"** accanto ai filtri esistenti
- Ogni entry nella lista mostra (se presenti): stelle ★★★★☆ in amber + tag pills teal
- Click su una entry → espande un `<details>`/accordeon che mostra la risposta completa
  riutilizzando i componenti `PhaseBlock` / `StepAccordion` già esistenti in `ResponseCard`

**Endpoint `/history` (backend)** — aggiungere query param:
```python
feedback_only: bool = Query(False)
# se True: aggiunge {"feedback_at": {"$exists": True}} al filtro MongoDB
```

---

## 4. Compatibilità con dati esistenti

I documenti `query_history` già presenti in MongoDB:
- Hanno `answer_summary` (troncato) ma non `answer` completo → le entry vecchie
  mostreranno il summary come fallback nel dettaglio History
- Non hanno i campi feedback → `feedback_rating` / `feedback_at` risultano `None`,
  il bottone "Valuta risposta" appare ma la PATCH creerà i campi ex-novo (nessuna migration dei dati)
- La migration degli indici è separata dai dati e non richiede downtime

---

## 5. File coinvolti (riepilogo)

| File | Tipo modifica |
|------|---------------|
| `aiura_legal/api/schemas.py` | Estende `HistoryEntry`, aggiunge `FeedbackRequest`, aggiunge `history_id` a `QueryResponse` |
| `aiura_legal/api/app.py` | Salvataggio completo, `PATCH /history/{id}/feedback`, `GET /history/{id}`, param `feedback_only` su `GET /history` |
| `scripts/migrate_history_indexes.py` | Nuovo script indici (sync PyMongo) |
| `frontend/src/hooks/useChat.ts` | Mappa `history_id` |
| `frontend/src/hooks/useHistory.ts` | Param `feedbackOnly`, tipi aggiornati |
| `frontend/src/components/chat/ResponseCard.tsx` | Aggiunge `FeedbackSection` collassabile |
| `frontend/src/api/client.ts` | Aggiunge `submitFeedback()` |
| `frontend/src/pages/History.tsx` | Filtro "Solo valutate", stelle/tag in lista, dettaglio espandibile |

---

## 6. Out of scope (v1)

- Editing del feedback dopo l'invio
- Dashboard analytics (distribuzione rating, tag più usati)
- Export CSV dei feedback
- Notifiche su feedback negativi (rating ≤ 2)
