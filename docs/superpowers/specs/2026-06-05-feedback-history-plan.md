# Piano di Implementazione: Feedback + History Completa
**Spec di riferimento:** `2026-06-05-feedback-history-design.md`
**Data:** 2026-06-05

---

## Ordine di esecuzione

Le fasi sono sequenziali. Ogni fase ha prerequisiti dalla precedente.

```
Fase 1 — Backend core       (schemas + salvataggio completo)
Fase 2 — Backend endpoints  (PATCH feedback, GET dettaglio, filtro)
Fase 3 — Migration script   (indici MongoDB)
Fase 4 — Frontend base      (api/client + useChat + useHistory)
Fase 5 — FeedbackSection    (componente ResponseCard)
Fase 6 — History UI         (filtro + stelle + dettaglio)
Fase 7 — Test               (backend + frontend)
```

---

## Fase 1 — Backend core: schemas + salvataggio completo

### 1.1 `aiura_legal/api/schemas.py`

**A. Costante tag ammessi** — aggiungere subito dopo gli import:
```python
FEEDBACK_ALLOWED_TAGS: frozenset[str] = frozenset({
    "Utile", "Parziale", "Errata",
    "Da approfondire", "Citazioni corrette", "Citazioni errate",
})
```

**B. Nuovo modello `FeedbackRequest`** — aggiungere dopo `HistoryListResponse`:
```python
class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    tags:   list[str] = Field(default_factory=list)
    note:   str | None = Field(default=None, max_length=500)

    @field_validator("tags")
    @classmethod
    def tags_must_be_allowed(cls, v: list[str]) -> list[str]:
        invalid = set(v) - FEEDBACK_ALLOWED_TAGS
        if invalid:
            raise ValueError(f"Tag non ammessi: {invalid}")
        return list(dict.fromkeys(v))   # dedup preservando ordine
```

**C. Estendere `HistoryEntry`** — aggiungere i campi mancanti:
```python
class HistoryEntry(BaseModel):
    id: str
    query: str
    workspace: str
    intent: str = "fattispecie_analysis"
    mode: str = "standard"
    verdict: str
    confidence: str = "LOW"
    # Risposta completa (nuovi campi — default vuoti per retrocompatibilità)
    answer: str = ""
    answer_summary: str = ""            # mantenuto per retrocompatibilità
    analysis_sections: list[dict] = []
    analysis_fase_1:   list[dict] = []
    analysis_fase_2:   list[dict] = []
    sources:           list[dict] = []
    sources_count: int = 0
    duration_total_s: float = 0.0
    created_at: str
    # Feedback (opzionali — presenti solo dopo PATCH)
    feedback_rating: int | None = None
    feedback_tags:   list[str] = []
    feedback_note:   str | None = None
    feedback_at:     str | None = None
```

**D. Estendere `QueryResponse`** — aggiungere campo `history_id`:
```python
class QueryResponse(BaseModel):
    ...
    history_id: str | None = None
```

**E. Import `field_validator`** — aggiungere a `from pydantic import ...` se mancante.

### 1.2 `aiura_legal/api/app.py` — salvataggio history completo

**Aggiungere helper `_source_to_dict()`** vicino alle altre funzioni helper:
```python
def _source_to_dict(s) -> dict:
    """Serializza un SearchResult per il salvataggio in MongoDB."""
    return {
        "source_id":  s.source_id,
        "doc_id":     s.doc_id,
        "snippet":    s.snippet,
        "score":      round(float(s.score), 4),
        "metadata":   dict(s.metadata or {}),
        "source_layer": getattr(s, "source_layer", "normativa"),
    }
```

**Aggiungere helper `_section_to_dict()`**:
```python
def _section_to_dict(s) -> dict:
    return {
        "step":      s.step,
        "content":   s.content,
        "citations": list(s.citations or []),
    }
```

**Modificare il blocco fire-and-forget in entrambi `/query` e `/query/stream`**:

1. Generare `history_id = str(uuid.uuid4())` PRIMA di costruire il payload.
2. Includere `history_id` nel payload di risposta.
3. Nel `insert_one` salvare il documento completo:

```python
history_id = str(uuid.uuid4())

# ... costruzione payload (aggiungere history_id) ...
payload = {
    ...
    "history_id": history_id,
}

# fire-and-forget history
try:
    mongo = MongoClient.get()
    sections = result.analysis.sections or []
    await mongo.db["query_history"].insert_one({
        "_id":               history_id,
        "query":             req.query,
        "workspace":         req.workspace,
        "intent":            req.intent,
        "mode":              getattr(req, "mode", "standard"),
        "verdict":           result.reviewer_verdict,
        "confidence":        result.analysis.overall_confidence,
        "answer":            result.answer or "",
        "answer_summary":    (result.answer or "")[:300],
        "analysis_sections": [_section_to_dict(s) for s in sections],
        "analysis_fase_1":   [_section_to_dict(s) for s in (result.analysis_fase_1 or [])],
        "analysis_fase_2":   [_section_to_dict(s) for s in (result.analysis_fase_2 or [])],
        "sources":           [_source_to_dict(s) for s in result.sources],
        "sources_count":     len(result.sources),
        "duration_total_s":  result.duration_total_s,
        "created_at":        datetime.now(timezone.utc).isoformat(),
    })
except Exception as e:
    logger.warning(f"[History] Salvataggio fallito: {e}")
```

**Attenzione**: nel blocco streaming il payload SSE è JSON — verificare che `history_id`
sia incluso nel dict `payload` passato a `json.dumps({"type": "result", "data": payload})`.

**Aggiungere `FeedbackRequest` agli import da `schemas`** in `app.py`.

---

## Fase 2 — Backend endpoints

### 2.1 Helper condiviso `_doc_to_history_entry()`

Aggiungere vicino a `list_history` per evitare duplicazione:
```python
def _doc_to_history_entry(doc: dict) -> HistoryEntry:
    return HistoryEntry(
        id=str(doc.get("_id", "")),
        query=doc.get("query", ""),
        workspace=doc.get("workspace", ""),
        intent=doc.get("intent", "fattispecie_analysis"),
        mode=doc.get("mode", "standard"),
        verdict=doc.get("verdict", "PASS"),
        confidence=doc.get("confidence", "LOW"),
        answer=doc.get("answer", doc.get("answer_summary", "")),
        answer_summary=doc.get("answer_summary", ""),
        analysis_sections=doc.get("analysis_sections", []),
        analysis_fase_1=doc.get("analysis_fase_1", []),
        analysis_fase_2=doc.get("analysis_fase_2", []),
        sources=doc.get("sources", []),
        sources_count=doc.get("sources_count", 0),
        duration_total_s=doc.get("duration_total_s", 0.0),
        created_at=doc.get("created_at", ""),
        feedback_rating=doc.get("feedback_rating"),
        feedback_tags=doc.get("feedback_tags", []),
        feedback_note=doc.get("feedback_note"),
        feedback_at=doc.get("feedback_at"),
    )
```

### 2.2 Aggiornare `list_history` — aggiungere `feedback_only`

```python
@app.get("/history", response_model=HistoryListResponse, tags=["history"])
async def list_history(
    workspace: str = Query(..., min_length=1),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    feedback_only: bool = Query(default=False),
):
    mongo = MongoClient.get()
    skip = (page - 1) * limit
    query_filter: dict = {"workspace": workspace}
    if feedback_only:
        query_filter["feedback_at"] = {"$exists": True}
    try:
        cursor = mongo.db["query_history"].find(
            query_filter, sort=[("created_at", -1)], skip=skip, limit=limit
        )
        docs = await cursor.to_list(length=limit)
        total = await mongo.db["query_history"].count_documents(query_filter)
    except Exception as e:
        logger.error(f"[History] Errore lettura: {e}")
        return HistoryListResponse(entries=[], total=0, page=page, limit=limit)

    return HistoryListResponse(
        entries=[_doc_to_history_entry(doc) for doc in docs],
        total=total, page=page, limit=limit,
    )
```

### 2.3 Nuovo `GET /history/{entry_id}`

```python
@app.get("/history/{entry_id}", response_model=HistoryEntry, tags=["history"])
async def get_history_entry(entry_id: str):
    """Restituisce il dettaglio completo di una voce della cronologia."""
    mongo = MongoClient.get()
    doc = await mongo.db["query_history"].find_one({"_id": entry_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Voce non trovata")
    return _doc_to_history_entry(doc)
```

### 2.4 Nuovo `PATCH /history/{entry_id}/feedback`

```python
@app.patch("/history/{entry_id}/feedback", status_code=204, tags=["history"])
async def add_feedback(entry_id: str, body: FeedbackRequest):
    """
    Aggiunge una valutazione a una voce della cronologia.
    Restituisce 409 se il feedback è già stato inviato.
    """
    mongo = MongoClient.get()
    doc = await mongo.db["query_history"].find_one(
        {"_id": entry_id}, {"feedback_at": 1}
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Voce non trovata")
    if doc.get("feedback_at"):
        raise HTTPException(status_code=409, detail="Feedback già inviato per questa risposta")

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

---

## Fase 3 — Script migrazione indici

### `scripts/migrate_history_indexes.py` (nuovo file)

```python
"""
Crea gli indici ottimizzati sulla collection query_history.
Idempotente: eseguire una sola volta dopo il deploy, poi a piacere.

Uso:
  python scripts/migrate_history_indexes.py
"""
from __future__ import annotations
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from loguru import logger
from aiura_legal.ingestion.mongodb.client import settings

def migrate() -> None:
    client = MongoClient(settings.mongodb_uri)
    coll = client[settings.mongodb_database]["query_history"]

    indexes = [
        # Query principale: workspace + data desc
        (
            [("workspace", ASCENDING), ("created_at", DESCENDING)],
            {"name": "ws_date"},
        ),
        # Filtro "solo valutate"
        (
            [("workspace", ASCENDING), ("feedback_at", DESCENDING)],
            {"name": "ws_feedback_date", "sparse": True},
        ),
        # Filtro per rating
        (
            [("workspace", ASCENDING), ("feedback_rating", ASCENDING)],
            {"name": "ws_rating", "sparse": True},
        ),
        # Tag multikey
        (
            [("feedback_tags", ASCENDING)],
            {"name": "tags_multikey", "sparse": True},
        ),
        # Full-text sulla domanda
        (
            [("query", TEXT)],
            {"name": "query_text"},
        ),
    ]

    for keys, opts in indexes:
        name = opts["name"]
        try:
            coll.create_index(keys, **opts)
            logger.success(f"Indice '{name}' creato (o già esistente)")
        except Exception as e:
            logger.error(f"Errore indice '{name}': {e}")

    client.close()
    logger.info("Migrazione indici completata.")

if __name__ == "__main__":
    migrate()
```

---

## Fase 4 — Frontend base

### 4.1 `frontend/src/api/client.ts` — aggiungere `submitFeedback`

```typescript
export async function submitFeedback(
  historyId: string,
  rating: number,
  tags: string[],
  note?: string,
): Promise<void> {
  const res = await fetch(`/api/history/${historyId}/feedback`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ rating, tags, note: note ?? null }),
  })
  if (res.status === 409) throw new Error('ALREADY_SUBMITTED')
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
}

export async function getHistoryEntry(historyId: string): Promise<HistoryEntryFull> {
  const res = await fetch(`/api/history/${historyId}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
```

### 4.2 `frontend/src/hooks/useHistory.ts` — estendere il tipo e aggiungere filtro

```typescript
export interface HistoryEntry {
  id: string
  query: string
  verdict: 'PASS' | 'FAIL' | 'WARN' | 'RE_RETRIEVAL'
  confidence: 'HIGH' | 'MEDIUM' | 'LOW'
  mode: string
  answer: string
  answer_summary: string
  analysis_sections: AnalysisSectionRaw[]
  analysis_fase_1:   AnalysisSectionRaw[]
  analysis_fase_2:   AnalysisSectionRaw[]
  sources: SourceRaw[]
  sources_count: number
  duration_total_s: number
  created_at: string
  workspace: string
  // Feedback
  feedback_rating?: number
  feedback_tags:    string[]
  feedback_note?:   string
  feedback_at?:     string
}

// Aggiungere parametro feedbackOnly
export function useHistory(workspace: string, page = 1, feedbackOnly = false) {
  return useQuery<HistoryEntry[]>({
    queryKey: ['history', workspace, page, feedbackOnly],
    queryFn: async () => {
      const { data } = await apiClient.get<HistoryResponse>('/history', {
        params: { workspace, page, limit: 20, feedback_only: feedbackOnly },
      })
      return data.entries
    },
    retry: false,
    placeholderData: [],
  })
}
```

### 4.3 `frontend/src/hooks/useChat.ts` — mappare `history_id`

In `mapBackendResponse()`, aggiungere:
```typescript
history_id: String(data.history_id ?? '') || undefined,
```

### 4.4 `frontend/src/components/chat/ResponseCard.tsx` — interfaccia

Aggiungere `history_id?: string` a `LegalResponse`:
```typescript
export interface LegalResponse {
  ...
  history_id?: string
}
```

---

## Fase 5 — Componente FeedbackSection

### `frontend/src/components/chat/FeedbackSection.tsx` (nuovo file)

Componente isolato, riceve `historyId` e gestisce tutto lo stato interno.

**Struttura:**
```typescript
interface FeedbackSectionProps {
  historyId: string | undefined
}

export function FeedbackSection({ historyId }: FeedbackSectionProps)
```

**Stati interni:**
- `open: boolean` — accordion aperto/chiuso
- `rating: number` — 0 = non selezionato, 1–5
- `selectedTags: Set<string>`
- `note: string`
- `status: 'idle' | 'submitting' | 'done' | 'error'`
- `savedRating / savedTags` — dopo il submit, per il badge

**Comportamento:**
- Se `!historyId`: bottone disabilitato con `title="Ricarica la pagina per abilitare"`
- Stars: 5 `<button>` con icona ★ (filled amber se `i <= rating`, outline grigio altrimenti),
  hover progressivo (colora fino al cursore)
- Chip tag: `ALLOWED_TAGS.map(tag => <button>)`, toggle `bg-teal-900/border-teal-500`
  quando selezionato
- Submit disabilitato se `rating === 0`
- Su submit: `setStatus('submitting')` → `submitFeedback()` → `setStatus('done')`
- Su errore `ALREADY_SUBMITTED`: messaggio "Feedback già inviato"
- Status `done`: sostituisce tutto il form con badge permanente

**Badge post-submit:**
```
✓ Valutazione salvata  · ★★★★☆ · [Utile] [Citazioni corrette]
```

**Costante da esportare** (usata anche in `History.tsx`):
```typescript
export const ALLOWED_TAGS = [
  'Utile', 'Parziale', 'Errata',
  'Da approfondire', 'Citazioni corrette', 'Citazioni errate',
] as const
```

### Aggiungere in `ResponseCard.tsx`

In fondo al JSX, prima della chiusura della card:
```tsx
<div className="border-t border-border">
  <FeedbackSection historyId={response.history_id} />
</div>
```

---

## Fase 6 — History UI

### 6.1 `frontend/src/pages/History.tsx`

**A. Filtro "Solo valutate":**

```typescript
const [feedbackOnly, setFeedbackOnly] = useState(false)
const { data: history = [], isLoading } = useHistory(workspace, 1, feedbackOnly)
```

Chip toggle sopra la lista:
```tsx
<button
  onClick={() => setFeedbackOnly(f => !f)}
  className={cn(
    'text-xs px-3 py-1 rounded-full border transition-colors',
    feedbackOnly
      ? 'bg-teal-900 border-teal-500 text-teal-300'
      : 'bg-muted border-border text-muted-foreground hover:bg-accent'
  )}
>
  ⭐ Solo valutate
</button>
```

**B. Stelle e tag nella lista:**

Nella entry row, dopo la data, aggiungere:
```tsx
{entry.feedback_rating && (
  <span className="text-amber-400 text-xs flex-shrink-0">
    {'★'.repeat(entry.feedback_rating)}{'☆'.repeat(5 - entry.feedback_rating)}
  </span>
)}
{entry.feedback_tags.slice(0, 2).map(tag => (
  <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-teal-900/50 text-teal-300 border border-teal-700 flex-shrink-0">
    {tag}
  </span>
))}
```

**C. Dettaglio espandibile:**

Sostituire il `<button>` entry con un componente che al click espande
(non naviga più a `/chat`):

```tsx
const [expandedId, setExpandedId] = useState<string | null>(null)

// entry row
<div key={entry.id} className="border border-border rounded-lg overflow-hidden">
  <button
    onClick={() => setExpandedId(id => id === entry.id ? null : entry.id)}
    className="w-full flex items-center gap-3 bg-card hover:bg-accent px-4 py-3 text-left transition-colors group"
  >
    {/* ... contenuto esistente + stelle/tag ... */}
    <ChevronDown className={cn('w-3.5 h-3.5 transition-transform', expandedId === entry.id && 'rotate-180')} />
  </button>

  {expandedId === entry.id && (
    <HistoryDetail entry={entry} />
  )}
</div>
```

**D. Componente `HistoryDetail`** (inline in `History.tsx` o file separato):

Riceve `entry: HistoryEntry` e ricostruisce la risposta usando i componenti esistenti.
Mappa i campi di `HistoryEntry` → `LegalResponse` e usa `<ResponseCard>` in modalità
read-only (senza FeedbackSection se `feedback_at` già presente, con FeedbackSection
se ancora vuoto).

```typescript
function HistoryDetail({ entry }: { entry: HistoryEntry }) {
  const response: LegalResponse = {
    summary:           entry.answer || entry.answer_summary,
    analysis_sections: entry.analysis_sections,
    analysis_fase_1:   entry.analysis_fase_1,
    analysis_fase_2:   entry.analysis_fase_2,
    mode:              entry.mode as 'standard' | 'deep',
    fase_2_available:  entry.analysis_fase_2.length > 0,
    verdict:           entry.verdict as LegalResponse['verdict'],
    confidence:        entry.confidence as LegalResponse['confidence'],
    sources:           entry.sources.map(mapHistorySource),
    elapsed_ms:        Math.round(entry.duration_total_s * 1000),
    gaps:              [],
    history_id:        entry.feedback_at ? undefined : entry.id,
  }
  return (
    <div className="border-t border-border bg-background/50 px-4 py-4">
      <ResponseCard response={response} />
    </div>
  )
}
```

`mapHistorySource` converte il formato `sources[]` da MongoDB → `Source` di `ResponseCard`
(stessa logica di `mapBackendResponse` in `useChat.ts`).

---

## Fase 7 — Test

### 7.1 `tests/test_feedback_api.py` (nuovo file)

```python
"""Test endpoints feedback e history con mongomock-motor."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_add_feedback_ok(mock_db):
    """PATCH /history/{id}/feedback → 204."""
    ...

@pytest.mark.asyncio
async def test_add_feedback_409_if_already_submitted(mock_db):
    """Secondo PATCH sullo stesso entry → 409."""
    ...

@pytest.mark.asyncio
async def test_add_feedback_404_if_not_found(mock_db):
    """PATCH su ID inesistente → 404."""
    ...

@pytest.mark.asyncio
async def test_add_feedback_validates_rating(mock_db):
    """rating=6 → 422 Unprocessable."""
    ...

@pytest.mark.asyncio
async def test_add_feedback_validates_tags(mock_db):
    """tag non in ALLOWED_TAGS → 422."""
    ...

@pytest.mark.asyncio
async def test_list_history_feedback_only(mock_db):
    """GET /history?feedback_only=true restituisce solo entry con feedback_at."""
    ...

@pytest.mark.asyncio
async def test_get_history_entry_ok(mock_db):
    """GET /history/{id} → 200 con tutti i campi."""
    ...

@pytest.mark.asyncio
async def test_get_history_entry_404(mock_db):
    """GET /history/{id} inesistente → 404."""
    ...

@pytest.mark.asyncio
async def test_history_saved_with_full_response(mock_db):
    """Dopo /query/stream, query_history contiene answer completo e sources."""
    ...
```

### 7.2 `tests/test_feedback_schema.py` (nuovo file)

```python
def test_feedback_request_valid():
    req = FeedbackRequest(rating=4, tags=["Utile", "Citazioni corrette"])
    assert req.rating == 4

def test_feedback_request_invalid_rating():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=6, tags=[])

def test_feedback_request_invalid_tag():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=3, tags=["TagInesistente"])

def test_feedback_request_dedup_tags():
    req = FeedbackRequest(rating=3, tags=["Utile", "Utile"])
    assert req.tags == ["Utile"]

def test_feedback_request_note_max_length():
    with pytest.raises(ValidationError):
        FeedbackRequest(rating=3, tags=[], note="x" * 501)
```

### 7.3 `tests/test_migrate_history_indexes.py`

```python
def test_migrate_runs_idempotent(monkeypatch):
    """migrate() può essere chiamata due volte senza errori."""
    # mock PyMongo create_index → verifica chiamate
    ...
```

---

## Checklist di verifica manuale

Dopo l'implementazione, eseguire nell'ordine:

1. `python scripts/migrate_history_indexes.py` — verifica log "Indice '...' creato"
2. Riavviare API: `python -m aiura_legal.api`
3. Fare una query dalla UI → aprire MongoDB Compass, verificare `query_history`:
   - `answer` non troncato
   - `analysis_sections` array con 9 step
   - `sources` array con metadata completo
   - `history_id` presente nella risposta SSE
4. Cliccare "Valuta risposta" → espande il form
5. Selezionare stelle + tag + nota → "Invia" → badge permanente
6. Ricaricare la pagina → il bottone "Valuta risposta" deve essere scomparso
   (history_id non è nella risposta precedente — badge visibile solo nella History)
7. Aprire History → chip "Solo valutate" → entry con stelle + tag
8. Click su entry → espande `HistoryDetail` con risposta completa
9. `pytest tests/test_feedback_api.py tests/test_feedback_schema.py -v`

---

## Note implementative

- **Retrocompatibilità**: i documenti vecchi hanno `answer_summary` ma non `answer`.
  `_doc_to_history_entry` usa `doc.get("answer", doc.get("answer_summary", ""))` come fallback.
- **Fire-and-forget history**: se il salvataggio fallisce, la risposta è già stata inviata
  al client — l'utente non vedrà errori, ma `history_id` sarà presente nel payload
  e il click "Valuta" darà 404. Gestire con toast "Impossibile salvare la valutazione".
- **`history_id` in streaming**: nel blocco `query/stream`, il payload SSE è
  `{"type": "result", "data": {...}}` — assicurarsi che `data["history_id"]` sia presente.
- **Deduplicazione tags**: il validator in `FeedbackRequest` rimuove i duplicati preservando
  l'ordine di inserimento.
