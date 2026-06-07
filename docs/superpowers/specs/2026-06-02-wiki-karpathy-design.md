# Design Spec — LLM Wiki (paradigma Karpathy)
**Data:** 2026-06-02  
**Progetto:** AiUraLegalLab  
**Status:** Approvato

---

## Obiettivo

Implementare il paradigma LLM Wiki di Karpathy come layer di memoria incrementale
degli agenti legali. La wiki cresce automaticamente ad ogni query che supera il
CitationReviewer, senza intervento dell'avvocato. Ogni risposta sintetizzata viene
"filata" nelle pagine wiki dei concetti giuridici rilevanti.

---

## Scelte di design

| Domanda | Scelta |
|---|---|
| Tipo di wiki | Memoria incrementale degli agenti (cresce con ogni query) |
| Trigger scrittura | Automatico post-query (ogni PASS/WARN dal CitationReviewer) |
| Struttura pagine | Flat per concetto giuridico — markdown libero + sezione `## Fonti` |

---

## Architettura

```
aiura_legal/
  wiki/
    __init__.py
    store.py        # WikiStore   — CRUD async su MongoDB wiki_pages
    writer.py       # WikiWriter  — chiamate Ollama per sintesi e merge
    engine.py       # WikiEngine  — orchestra store + writer
    lint.py         # WikiLinter  — health check periodico
    middleware.py   # FastAPI middleware post-query (fire-and-forget)

scripts/
  wiki_bootstrap.py  # seed iniziale da normattiva_docs (one-shot, no Ollama)

tests/
  test_wiki_store.py
  test_wiki_writer.py
  test_wiki_engine.py
  test_wiki_lint.py
```

**Flusso post-query:**
```
Request API
  → HybridRetriever  (esistente)
  → CitationReviewer (esistente)
  → Response PASS|WARN
  → WikiMiddleware   [NUOVO — asyncio.create_task, non blocca la response]
       └→ WikiEngine.file_response(query, response_text, research_packet)
              └→ WikiWriter.extract_concepts()    # Ollama: lista concetti
              └→ WikiStore.get_or_create_page()   # MongoDB upsert
              └→ WikiWriter.merge_knowledge()     # Ollama: aggiorna body md
              └→ WikiStore.save_page()            # version++
```

Il middleware usa `asyncio.create_task` — la risposta all'avvocato non aspetta
la scrittura wiki.

---

## Schema MongoDB — collection `aiura_legal.wiki_pages`

```python
{
  "_id":          ObjectId,
  "slug":         str,       # es. "licenziamento_giusta_causa" (unique)
  "title":        str,       # es. "Licenziamento per giusta causa"
  "body_md":      str,       # markdown libero gestito da WikiWriter
  "sources":      [str],     # lista URN citati (Citation Contract)
  "query_count":  int,       # quante query hanno alimentato questa pagina
  "last_updated": datetime,
  "version":      int,       # incrementale ad ogni merge
  "workspace":    str        # isolamento multi-tenant
}
```

**Indici:**
- `(slug, workspace)` → unique
- `last_updated` → per WikiLinter (pagine stale)
- `sources` → multikey, per trovare pagine che citano un URN

**Struttura `body_md` generata da Ollama:**
```markdown
## Sintesi
<testo sintetico del concetto>

## Principi chiave
- ...

## Evoluzione normativa
- ...

## Casi applicativi
- ...

## Fonti
- urn:nir:stato:regio.decreto:1942-03-16;262~art2119
```

La sezione `## Fonti` è l'ancora del Citation Contract. `WikiWriter` la aggiorna
ad ogni merge mantenendo solo URN presenti in almeno un `ResearchPacket`.

---

## Componenti

### `WikiStore` (`wiki/store.py`)
Puro CRUD async, zero logica di business.

```python
@dataclass
class WikiPage:
    slug: str
    title: str
    body_md: str
    sources: list[str]
    query_count: int
    last_updated: datetime
    version: int
    workspace: str

class WikiStore:
    async def get_page(slug: str, workspace: str) -> WikiPage | None
    async def save_page(page: WikiPage) -> None           # upsert
    async def list_stale(days: int, workspace: str) -> list[WikiPage]
    async def search_by_urn(urn: str, workspace: str) -> list[WikiPage]
```

### `WikiWriter` (`wiki/writer.py`)
Due chiamate Ollama via httpx, prompt in italiano.

```python
class WikiWriter:
    async def extract_concepts(query: str, response_text: str) -> list[str]
    # prompt: "Elenca i concetti giuridici principali in questa risposta.
    #          Solo nomi, uno per riga."
    # ritorna: ["licenziamento per giusta causa", "art. 2119 cc"]

    async def merge_knowledge(page: WikiPage, new_evidence: str) -> str
    # prompt: "Sei un redattore giuridico. Aggiorna questa pagina wiki con le
    #          nuove informazioni. Mantieni le sezioni esistenti.
    #          Non inventare fonti."
    # ritorna: nuovo body_md
```

### `WikiEngine` (`wiki/engine.py`)
Orchestra store + writer, contiene tutta la logica.

```python
class WikiEngine:
    async def file_response(
        query: str,
        response_text: str,
        research_packet: ResearchPacket,
        workspace: str,
    ) -> None
    # 1. extract_concepts → slugify → get_or_create pages
    # 2. merge_knowledge per ogni concetto estratto
    # 3. aggiorna sources dagli URN nel ResearchPacket
    # 4. save_page con version++
```

### `WikiMiddleware` (`wiki/middleware.py`)
Hook FastAPI, fire-and-forget.

```python
class WikiMiddleware(BaseHTTPMiddleware):
    # intercetta POST /api/query con ReviewResult.verdict in {PASS, WARN}
    # asyncio.create_task → non blocca la response all'avvocato
```

### `WikiLinter` (`wiki/lint.py`)
Script/cron, genera report senza modificare dati.

```python
@dataclass
class LintReport:
    stale_pages: list[str]        # non aggiornate da >30gg
    empty_bodies: list[str]       # body_md vuoto o < 50 chars
    orphan_urns: list[str]        # URN in sources non in normattiva_docs
    total_pages: int

class WikiLinter:
    async def run(workspace: str) -> LintReport
```

### `wiki_bootstrap.py` (`scripts/`)
Seed one-shot da `normattiva_docs`. **Non chiama Ollama.**
Il `body_md` iniziale è il testo verbatim dell'articolo (`testo_tipo=normativo`).
Ollama interviene solo nei merge post-query successivi.

```
python scripts/wiki_bootstrap.py --workspace mio-studio --limit 500
```

---

## Testing

Convenzioni progetto: mongomock-motor, dati PII sintetici, zero MongoDB reale.

| File | Cosa testa |
|---|---|
| `test_wiki_store.py` | CRUD, upsert, indici, isolamento workspace |
| `test_wiki_writer.py` | mock Ollama httpx → prompt italiani, merge non perde `## Fonti` |
| `test_wiki_engine.py` | `file_response` end-to-end, URN propagati in `page.sources` |
| `test_wiki_lint.py` | pagina stale, body vuoto, URN orfano → LintReport corretto |

---

## Invarianti (non derogabili)

1. `WikiMiddleware` non blocca mai la response API — sempre `create_task`
2. La sezione `## Fonti` non viene mai rimossa dal `body_md`
3. `WikiStore` non scrive mai su `legal_lab` (read-only)
4. Il bootstrap non chiama Ollama — solo testo verbatim come seed
5. Ogni `WikiPage.sources` contiene solo URN presenti in almeno un `ResearchPacket`

---

## Dipendenze esterne (già nel progetto)

- `motor` — async MongoDB
- `httpx` — chiamate Ollama
- `loguru` — logging
- `fastapi` / `starlette` — middleware
- `python-slugify` — slug da titolo concetto (da aggiungere a pyproject.toml)
