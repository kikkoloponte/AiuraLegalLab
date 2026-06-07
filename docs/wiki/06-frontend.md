# Frontend — Implementazione e Roadmap

## Contesto

Il frontend React è **parzialmente implementato** nella cartella `frontend/`.
Le pagine principali (Chat, Dashboard, Documenti, Wiki, Cronologia) sono scaffoldate.
Il backend FastAPI è accessibile anche via Swagger UI su `/docs`.

### Pagine implementate

| Pagina | File | Stato |
|--------|------|-------|
| Chat legale | `src/pages/Chat.tsx` | ✅ Scaffoldata |
| Dashboard | `src/pages/Dashboard.tsx` | ✅ Scaffoldata |
| Documenti | `src/pages/Documents.tsx` | ✅ Scaffoldata |
| Wiki | `src/pages/Wiki.tsx` | ✅ Scaffoldata |
| Cronologia | `src/pages/History.tsx` | ✅ Scaffoldata |

### Componenti chiave implementati

- `ChatInput`, `ChatMessage`, `ReviewerBadge`, `FeedbackSection`, `ResponseCard`, `SourceChip`
- `DropZone`, `IngestionProgress`, `DocumentCard`, `FolderSidebar`
- `WikiPageCard`, `MarkdownViewer`
- `AgentStatusBar`, `TopBar`, `Sidebar`, `AppShell`
- Sistema feedback risposta + history completa

---

## Requisiti

### Utenti target

- **Avvocato** — utente principale. Non tecnico. Usa il sistema per ricerca e redazione.
- **Collaboratore studio** — carica documenti, consulta la wiki.
- **Admin** (futuro) — gestisce workspace e utenti.

### Principi UI

- **Semplice prima di tutto** — l'avvocato non vuole configurare niente
- **Locale per ora** — i dati sono sensibili, il deploy è in studio (no cloud)
- **Trasparente sulle fonti** — ogni affermazione deve mostrare la fonte cliccabile
- **Feedback immediato** — indicatore visivo su Reviewer PASS/FAIL

---

## Funzionalità MVP (Sprint 1–2)

### 1. Chat legale

Il cuore dell'interfaccia. Input query → risposta strutturata con fonti.

```
┌─────────────────────────────────────────────────────┐
│  AiUra LegalLab          [workspace: mio-studio ▼]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌───────────────────────────────────────────────┐  │
│  │ Quali sono gli elementi costitutivi del       │  │
│  │ reato ex art. 2 D.Lgs. 74/2000?               │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  ╔═══════════════════════════════════════════════╗  │
│  ║  ✅ PASS → DELIVER              [HIGH]        ║  │
│  ║  ─────────────────────────────────────────    ║  │
│  ║  QUALIFICAZIONE                               ║  │
│  ║  Il reato di dichiarazione fraudolenta...     ║  │
│  ║                                               ║  │
│  ║  NORMA APPLICABILE                            ║  │
│  ║  [urn:nir:...art2] Art. 2 D.Lgs. 74/2000 ↗   ║  │
│  ║                                               ║  │
│  ║  GIURISPRUDENZA                               ║  │
│  ║  [Cass. n.12345/2025] Il nesso causale... ↗   ║  │
│  ╚═══════════════════════════════════════════════╝  │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ Fai una domanda legale...            [Invia] │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

**Comportamenti:**
- Mostra risposta in streaming (SSE) man mano che il LLM genera
- Le citazioni normative e giurisprudenziali sono link cliccabili
- Badge colorato: 🟢 PASS / 🔴 FAIL / 🟡 RE_RETRIEVAL
- Gap analysis mostrata in un collassabile
- Pulsante "Genera atto" per passare al Drafter

### 2. Research Packet sidebar

Pannello laterale che mostra le fonti usate per la risposta:

```
┌──────────────────────────┐
│  FONTI (10)              │
│  ─────────────────────   │
│  🟦 Normativa (3)        │
│  ┌──────────────────┐    │
│  │ Art. 2 D.Lgs.74  │    │
│  │ score: 2.79  ↗   │    │
│  │ "Il reato di..." │    │
│  └──────────────────┘    │
│                          │
│  🟩 Giurisprudenza (7)   │
│  ┌──────────────────┐    │
│  │ Cass. 12345/2025 │    │
│  │ [massima] ↗      │    │
│  │ "La Corte ha..." │    │
│  └──────────────────┘    │
└──────────────────────────┘
```

### 3. Upload documento

Drag & drop con progress bar e stato anonimizzazione:

```
┌─────────────────────────────────────┐
│  Carica documento                   │
│                                     │
│  ┌─────────────────────────────┐    │
│  │  📄 Trascina qui il PDF     │    │
│  │  oppure clicca per sfogliare│    │
│  └─────────────────────────────┘    │
│                                     │
│  contratto_locazione.pdf            │
│  ██████████░░░░░  65%               │
│  ✓ Testo estratto (12.450 chars)    │
│  ✓ PII anonimizzate (3 persone)     │
│  ⏳ Chunking in corso...             │
│                                     │
│  [Avvia annotazione automatica]     │
└─────────────────────────────────────┘
```

### 4. Workspace selector

Switch rapido tra studi diversi (multi-tenant futuro):

```
workspace: [mio-studio ▼]
           ├── mio-studio
           ├── studio-rossi
           └── + Nuovo workspace
```

---

## Funzionalità Sprint 3+

### 5. Wiki viewer

Naviga le pagine auto-generate per topic:

```
Wiki legale / mio-studio
  ┌──────────────────────────────────────┐
  │  🔍 Cerca nella wiki...              │
  └──────────────────────────────────────┘

  Recenti:
  • Dichiarazione fraudolenta — D.Lgs. 74/2000 art. 2
  • Omesso versamento IVA — art. 10-ter
  • Responsabilità extracontrattuale — art. 2043 c.c.

  Per topic:
  [Penale Tributario] [Diritto Civile] [Appalti] [TAR]
```

### 6. Grafo interattivo

Embed del grafo sentenza→norma in una tab dedicata.
Click su una norma → mostra le sentenze che la citano.

### 7. Export risposta

Bottone per esportare la risposta con fonti in:
- PDF formattato
- DOCX Word
- Copia testo plain

### 8. Cronologia query

Storico delle query per workspace con ricerca full-text:

```
📋 Cronologia — mio-studio
  ─────────────────────────
  ✅ 03/06 10:23  "Elementi costitutivi art. 2 D.Lgs. 74/2000"
  ✅ 03/06 09:15  "Soglie punibilità dichiarazione infedele"
  🔴 02/06 16:42  "Sequestro preventivo reati tributari"
  ✅ 02/06 14:11  "Confisca per equivalente art. 12-bis"
```

---

## Stack tecnologico

### Scelte

| Layer | Tecnologia | Motivazione |
|-------|-----------|-------------|
| Framework | **React 18 + TypeScript** | Ecosistema maturo, tipizzazione forte |
| Build | **Vite** | Build velocissimo, HMR immediato |
| UI Components | **shadcn/ui** | Componenti professionali, personalizzabili |
| Styling | **Tailwind CSS** | Utility-first, dark mode, responsive |
| State / Data | **TanStack Query** | Cache, loading states, error handling automatico |
| HTTP | **Axios** | Interceptors, timeout, base URL |
| Streaming | **EventSource / SSE** | Per risposta LLM in streaming |
| Routing | **React Router v6** | SPA con history mode |
| Markdown | **react-markdown + remark-gfm** | Render risposte strutturate |
| Syntax highlight | **Prism.js** | Per snippet codice / norme |
| Grafo | **react-force-graph** | Embed grafo interattivo (wrappa D3) |
| Deploy locale | **Vite preview** o **Electron** | Locale per dati sensibili |

### Struttura cartelle frontend

```
frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   ├── SourceCard.tsx
│   │   │   └── ReviewerBadge.tsx
│   │   ├── upload/
│   │   │   ├── DropZone.tsx
│   │   │   └── IngestionStatus.tsx
│   │   ├── wiki/
│   │   │   ├── WikiPage.tsx
│   │   │   └── WikiSearch.tsx
│   │   └── graph/
│   │       └── GraphViewer.tsx
│   ├── hooks/
│   │   ├── useQuery.ts        # POST /query con SSE streaming
│   │   ├── useIngest.ts       # POST /ingest con progress
│   │   └── useWorkspace.ts    # GET /workspace
│   ├── api/
│   │   └── client.ts          # Axios + TanStack Query setup
│   ├── pages/
│   │   ├── Chat.tsx
│   │   ├── Upload.tsx
│   │   ├── Wiki.tsx
│   │   └── Graph.tsx
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Modifiche backend necessarie

Il backend FastAPI richiede modifiche minime per supportare il frontend:

### 1. Streaming SSE (alta priorità)

```python
# Nuovo endpoint da aggiungere in app.py
from fastapi.responses import StreamingResponse

@app.post("/query/stream", tags=["query"])
async def query_stream(req: QueryRequest):
    """Risposta in streaming via Server-Sent Events."""
    async def event_generator():
        async for chunk in orchestrator.run_stream(req):
            yield f"data: {chunk.json()}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

### 2. CORS (già presente — da verificare origins)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Endpoint wiki

```python
@app.get("/wiki", tags=["wiki"])
async def list_wiki(workspace: str = "default", q: str = ""):
    """Lista pagine wiki con ricerca opzionale."""
    ...

@app.get("/wiki/{slug}", tags=["wiki"])
async def get_wiki_page(slug: str, workspace: str = "default"):
    """Recupera una pagina wiki specifica."""
    ...
```

---

## Stima sviluppo

| Sprint | Contenuto | Stato |
|--------|-----------|-------|
| 1 | Setup + Chat MVP + Research Packet sidebar | ✅ Scaffolding completato |
| 2 | Upload documento + streaming SSE + Reviewer badge | 🔄 In corso |
| 3 | Wiki viewer + cronologia + export | 🔄 In corso |
| 4 | Grafo interattivo + multi-workspace + polish | ⏳ Da fare |

**Completamento MVP: ~1 settimana** di integrazione API + polish.

---

## Deploy locale

```powershell
cd frontend
npm install
npm run dev       # http://localhost:5173 (sviluppo)
npm run build     # build produzione in dist/
npm run preview   # serve il build localmente
```

Il frontend comunica con la FastAPI su `http://127.0.0.1:8765`.
Entrambi girano in locale — nessun dato esce dalla macchina dello studio.
