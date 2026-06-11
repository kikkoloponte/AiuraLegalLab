# Design Spec — Verifica Giurisprudenza + Benchmark Qualitativo
**Data:** 2026-06-09
**Progetto:** AiUra LegalLab

---

## Scope

Tre interventi indipendenti:

| Parte | Descrizione |
|-------|-------------|
| A | Aumento token `LLM_MAX_TOKENS_FASE*` — fix regressione qualità |
| B | Propagazione `source_url` nei chunk giurisprudenziali → link cliccabile nel SourceChip |
| C | Script `eval/run_bench.py` — benchmark qualitativo con 10 domande, report Markdown |

---

## Parte A — Token (triviale)

Modificare `.env` e impostare i valori ai massimi del range configurabile:

```
LLM_MAX_TOKENS_FASE1=2048
LLM_MAX_TOKENS_FASE2=2048
LLM_MAX_TOKENS_FASE3=2048
LLM_MAX_TOKENS_FASE4=2700
```

Nessun'altra modifica necessaria.

---

## Parte B — Source URL giurisprudenza

### Problema

`coordinator.py::to_chunks()` genera i Document indicizzabili da `JurisprudenceDocument`
ma **non include `source_url`** nel metadata del chunk. Di conseguenza il campo
`Source.url` rimane `undefined` per tutte le fonti di giurisprudenza, e il SourceChip
mostra solo "Clicca per copiare il riferimento sentenza" invece di aprire il documento originale.

### Fix pipeline (coordinator.py)

In `to_chunks()`, aggiungere `"source_url": doc.source_url` al dict metadata di ogni chunk:

```python
metadata={
    "corpus": "giurisprudenza",
    "chunk_type": chunk_type,
    "jdoc_id": doc.id,
    "organo": doc.organo.value,
    "numero": doc.numero,
    "anno": doc.anno,
    "materia": doc.materia,
    "source_url": doc.source_url,   # ← aggiunto
},
```

### Fix useChat.ts

Il mapping source → `Source.url` attualmente controlla solo `sourceId.startsWith('urn:nir:')`.
Estenderlo per controllare anche `meta.source_url`:

```typescript
let url: string | undefined
if (sourceId.startsWith('urn:nir:')) {
  url = `https://www.normattiva.it/uri-res/N2Ls?${sourceId}`
} else if (meta.source_url) {
  url = meta.source_url   // ← giurisprudenza, dottrina open-access, ecc.
}
```

Questo blocco compare in DUE posti in `useChat.ts`: `mapBackendResponse()` e il
handler `review_done`. Aggiornare entrambi.

### Fix SourceChip.tsx

Il tooltip hint e il label ExternalLink sono hardcodati su "normattiva.it".
Renderli generici:

```tsx
// Tooltip hint
{url ? 'Clicca per aprire il documento originale'
  : type === 'studio' ? 'Clicca per aprire i Documenti'
  : type === 'giurisprudenza' ? 'Clicca per copiare il riferimento sentenza'
  : 'Clicca per copiare il riferimento'}

// Label ExternalLink nel tooltip header
{url && <span className="text-[0.65rem] text-blue-400 ..."><ExternalLink />apri originale</span>}
```

### Migrazione indici esistenti

I chunk già indicizzati in Qdrant e BM25 **non hanno** `source_url` nel payload.

**Qdrant** — aggiornamento in-place senza rebuild:
Script `scripts/update_giuri_source_urls.py`:
1. Legge tutti i documenti dalla collection `jurisprudence` MongoDB
2. Per ogni documento, costruisce i tre `point_id` (`{doc.id}_massima`, `_motivazione`, `_dispositivo`)
3. Chiama `qdrant_client.set_payload(collection, payload={"source_url": ...}, points=[...])`
4. Log degli aggiornamenti

**BM25** — il pkl non ha payload ricco; i metadati BM25 vengono da `SearchResult.metadata`
che è popolato dal `Document.metadata` al momento dell'indicizzazione. La BM25 restituisce
solo snippet e `source_id`, non il metadata completo. Pertanto **la BM25 non è interessata**
da questa modifica — il `source_url` arriverà comunque dai documenti Qdrant che sempre
vengono inclusi nella risposta ibrida.

---

## Parte C — Benchmark qualitativo (`eval/run_bench.py`)

### Obiettivo

Script CLI che:
1. Legge le domande da `eval/bench_questions.jsonl`
2. Per ogni domanda, chiama `POST /api/query/stream` (SSE) e raccoglie la risposta completa
3. Scrive un report Markdown a `eval/bench_results/YYYYMMDDTHHMMSSZ/report.md`

**Differenza da `run_eval.py`**: non calcola Recall@k (non ci sono expected_sources),
è un benchmark qualitativo — leggibilità della risposta, completezza delle citazioni,
tempo di risposta. Può girare con l'API in produzione senza toccare il sistema eval CI.

### File input: `eval/bench_questions.jsonl`

Ogni riga: `{"id": "...", "area": "...", "query": "..."}`

Le 10 domande fornite dall'utente (diritto civile, penale, lavoro, digitale, costituzionale).

### Formato report output

Per ogni domanda, una sezione strutturata:

```markdown
## 1. [area] Titolo breve

**Domanda:** testo completo

**Tempo di risposta:** 42.3s | **Verdict:** PASS | **Confidenza:** MEDIUM

### Analisi IQRAC

#### Ricostruzione del fatto
...

#### Qualificazione giuridica
...

[... tutti gli step presenti ...]

### Riferimenti citati

| # | Tipo | Label | Fonte | URL |
|---|------|-------|-------|-----|
| 1 | normativa | Art. 1321 c.c. | Codice Civile | https://... |
| 2 | giurisprudenza | Cass. n.1234/2023 | cassazione | https://... |
```

### Architettura script

```
run_bench.py
  ├── _load_questions(path) → list[BenchQuestion]
  ├── _call_stream(question, api_url, workspace) → BenchResult
  │     consuma SSE: accumula phase_complete sections + review_done sources/timing
  ├── _write_report(results, out_dir) → Path
  │     scrive report.md + raw_results.json (per debug)
  └── main() — argparse: --api-url, --workspace, --output-dir, --questions
```

`BenchResult` dataclass:
```python
@dataclass
class BenchResult:
    id: str
    area: str
    query: str
    verdict: str
    confidence: str
    sections: list[dict]   # [{step, content, citations}]
    sources: list[dict]    # [{source_id, label, type, url, snippet, metadata}]
    duration_s: float
    error: str | None
```

### Dipendenza dall'API

Lo script chiama l'API HTTP (non importa moduli Python direttamente) così è
riutilizzabile anche con API remote. Richiede `httpx` (già dipendenza del progetto).
SSE viene consumato leggendo la risposta in streaming con `httpx.stream()`.

---

## File modificati

| File | Modifica |
|------|----------|
| `.env` | Token FASE1-4 portati a max range |
| `aiura_legal/jurisprudence/coordinator.py` | `to_chunks()` aggiunge `source_url` al metadata |
| `frontend/src/hooks/useChat.ts` | Mapping `Source.url` da `meta.source_url` (2 posizioni) |
| `frontend/src/components/chat/SourceChip.tsx` | Tooltip hint e label ExternalLink generici |
| `scripts/update_giuri_source_urls.py` | Migrazione payload Qdrant in-place (nuovo) |
| `eval/bench_questions.jsonl` | 10 domande in formato JSON Lines (nuovo) |
| `eval/run_bench.py` | Script benchmark qualitativo (nuovo) |

---

## Invarianti

- `run_eval.py` e il sistema CI non vengono toccati
- Il rebuild indici NON è richiesto — la migrazione Qdrant è in-place
- I chunk nuovi (post-fix coordinator) avranno `source_url` automaticamente
- Backward compat: se `source_url` è vuota stringa, `meta.source_url` è falsy → nessun link
