# Frontend UI — Design Spec
**Data:** 3 giugno 2026
**Progetto:** AiUra LegalLab
**Stato:** approvato dall'utente

---

## Contesto

Il sistema AiUra LegalLab espone oggi solo API REST (Swagger su `/docs`). Questo spec definisce l'interfaccia web che rende il sistema utilizzabile dall'avvocato senza conoscenze tecniche. Il frontend comunica con la FastAPI su `http://127.0.0.1:8765`. Tutti i dati rimangono in locale — nessun dato esce dalla macchina dello studio.

---

## Decisioni di design validate

| Domanda | Scelta |
|---------|--------|
| Struttura navigazione | Sidebar verticale fissa + Dashboard iniziale |
| Tema visivo | Dark + Light con toggle (shadcn/ui native) |
| Visualizzazione risposta chat | Sintesi sempre visibile + analisi espandibile + chip fonti |
| Dashboard | Minimal: input grande al centro + ultime query |
| Organizzazione documenti | Sidebar cartelle + lista documenti con badge cartella |
| Scope MVP | Chat · Dashboard · Upload documenti (con cartelle) · Wiki viewer |
| Target device | Desktop only (≥1280px) per MVP |

---

## Stack tecnologico

| Layer | Tecnologia | Motivazione |
|-------|-----------|-------------|
| Framework | **React 18 + TypeScript** | Ecosistema maturo, tipizzazione forte |
| Build | **Vite** | HMR immediato, build rapido |
| UI Components | **shadcn/ui** | Componenti professionali, dark/light nativo |
| Styling | **Tailwind CSS v3** | Utility-first, dark mode, responsive |
| State / Data | **TanStack Query v5** | Cache, loading states, error handling |
| HTTP | **Axios** | Interceptors, timeout, base URL configurabile |
| Streaming | **EventSource / SSE** | Risposta LLM in streaming da `/query/stream` |
| Routing | **React Router v6** | SPA con history mode |
| Markdown | **react-markdown + remark-gfm** | Render risposte strutturate |
| Deploy locale | **Vite preview** | Serve il build in locale, zero cloud |

---

## Struttura cartelle

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppShell.tsx          # Sidebar + outlet
│   │   │   ├── Sidebar.tsx           # Nav + workspace selector + theme toggle
│   │   │   └── TopBar.tsx            # Breadcrumb + data
│   │   ├── chat/
│   │   │   ├── ChatInput.tsx         # Textarea + tasto Invia
│   │   │   ├── ChatMessage.tsx       # Bolla utente / risposta AI
│   │   │   ├── ResponseCard.tsx      # Sintesi + espandibile + fonti + azioni
│   │   │   ├── SourceChip.tsx        # Chip fonte (normativa/giurisprudenza)
│   │   │   └── ReviewerBadge.tsx     # Badge PASS/FAIL/WARN con confidence
│   │   ├── documents/
│   │   │   ├── FolderSidebar.tsx     # Albero cartelle + "Nuova cartella"
│   │   │   ├── DocumentList.tsx      # Lista documenti filtrata per cartella
│   │   │   ├── DocumentCard.tsx      # Card singolo doc + azioni
│   │   │   ├── DropZone.tsx          # Drag & drop upload
│   │   │   └── IngestionProgress.tsx # Step pipeline in tempo reale
│   │   └── wiki/
│   │       ├── WikiIndex.tsx         # Pannello indice + ricerca + filtri materia
│   │       ├── WikiPage.tsx          # Contenuto pagina con citazioni cliccabili
│   │       └── WikiPageCard.tsx      # Card in lista indice
│   ├── pages/
│   │   ├── Dashboard.tsx             # Input centrale + ultime query
│   │   ├── Chat.tsx                  # Schermata chat completa
│   │   ├── Documents.tsx             # Upload + gestione con cartelle
│   │   └── Wiki.tsx                  # Wiki viewer
│   ├── hooks/
│   │   ├── useChat.ts                # POST /query/stream (SSE)
│   │   ├── useIngest.ts              # POST /ingest + polling stato
│   │   ├── useFolders.ts             # GET/POST/DELETE /folders
│   │   ├── useDocuments.ts           # GET/DELETE /documents
│   │   ├── useWiki.ts                # GET /wiki, GET /wiki/:slug
│   │   └── useHistory.ts             # GET /history per workspace
│   ├── api/
│   │   └── client.ts                 # Axios instance + TanStack Query setup
│   ├── lib/
│   │   └── utils.ts                  # cn(), formatDate(), ecc.
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Schermata 1 — App Shell (layout fisso)

**Sidebar fissa (200px):**
- Logo "⚖ AiUra LegalLab" in cima
- Workspace selector (dropdown) sotto il logo
- Voci di navigazione: Dashboard · Chat legale · Documenti · Wiki legale · Cronologia (separatore)
- In fondo: versione app + toggle dark/light (🌙 / ☀️)
- Su schermi <1280px: collassabile a sole icone

**Top bar:**
- Breadcrumb della pagina corrente (sinistra)
- Data corrente (destra)

---

## Schermata 2 — Dashboard

**Layout:** pagina semplice, nessuna sidebar secondaria.

**Contenuto:**
1. Saluto contestuale ("Buongiorno" / workspace attivo + data KB)
2. **Input centrale** — grande, con bordo blu, placeholder "Cosa ti serve oggi?". Due CTA: `💬 Fai una domanda` (→ Chat) e `📁 Carica documento` (→ Documents)
3. **Ultime query** — lista cronologica con:
   - Pallino colorato PASS (verde) / FAIL (rosso) / WARN (giallo)
   - Testo della query
   - Timestamp
   - Freccia → per riaprire la risposta in Chat

**Comportamento:** click su una query passata naviga alla Chat mostrando la risposta salvata in read-only, con un campo input pre-attivo per fare domande di follow-up.

---

## Schermata 3 — Chat legale

**Layout:** area messaggi (flex-grow) + input fisso in fondo. Nessuna sidebar secondaria.

**Flusso query:**
1. L'utente scrive e invia
2. L'indicatore di streaming mostra l'agente attivo: `S2 Researcher · recupero fonti…` → `S3 Analyst…` → `S5 Reviewer…`
3. Appare la risposta strutturata

**Struttura risposta (ResponseCard):**
- **Reviewer badge** in cima: `✅ PASS · HIGH confidence` con tempo risposta e numero fonti. Colori: verde (PASS), rosso (FAIL), giallo (WARN/RE_RETRIEVAL)
- **Sintesi** — sempre visibile, 2-4 righe, grassetto sui concetti chiave
- **Analisi completa** — sezione collassata, espandibile on-click. Contiene sezioni: Qualificazione · Norma applicabile · Giurisprudenza · Gap analysis (se presente)
- **Fonti verificate** — chip cliccabili: 🔵 normativa (`bg-blue-950 border-blue-700`) / 🟢 giurisprudenza (`bg-green-950 border-green-700`). Click → apre fonte in nuova tab
- **Azioni**: `📋 Genera atto` · `⬇ Esporta PDF` · `📖 Wiki →`

**Input area:**
- Textarea multi-riga
- Disclaimer fisso sotto: *"AiUra cita solo fonti nella KB verificata — sempre revisionare prima dell'uso processuale"*

---

## Schermata 4 — Documenti studio

**Layout a due colonne:**

**Colonna sinistra — FolderSidebar (180px):**
- Header "CARTELLE" + link "Tutti"
- Lista cartelle con conteggio documenti
- Click filtra la lista a destra
- Pulsante "+ Nuova cartella" in fondo (dialog per nome)
- Rinomina/elimina cartella via menu contestuale (⋯)

**Colonna destra — DocumentList:**
- Header con nome cartella attiva + conteggio + pulsante `+ Carica`
- DropZone drag & drop visibile quando lista vuota; altrimenti compatta in cima
- Lista documenti (DocumentCard):
  - Icona tipo file (📄 PDF / 📝 DOCX)
  - Nome file + badge cartella di appartenenza
  - Metadati: dimensione testo · PII anonimizzate · data caricamento
  - Stato: `✓ pronto` (verde) / `⏳ in corso` (ambra) / `❌ errore` (rosso)
  - Azioni: `💬 Analizza` · `⚠ Rischio` · `🗑 Elimina` · `📁 Sposta` (assegna/cambia cartella)

**Pipeline di ingestion (IngestionProgress):**
Appare inline nella card durante il caricamento, mostra step sequenziali:
1. ✓ Testo estratto (N caratteri)
2. ✓ PII anonimizzate (N persone, N CF, N indirizzi)
3. ⏳ Chunking e indicizzazione BM25/Vector...
4. ○ Analisi rischio automatica (S6 Annotator)

---

## Schermata 5 — Cronologia

**Layout:** pagina semplice, nessuna sidebar secondaria.

**Contenuto:**
- Lista cronologica di tutte le query del workspace, paginate (20 per pagina)
- Ogni riga: pallino PASS/FAIL/WARN · testo query · data+ora · link "→ Rivedi"
- Filtro per stato (Tutti / PASS / FAIL / WARN) e ricerca full-text
- Click "→ Rivedi": naviga alla Chat con la risposta in read-only + follow-up attivo

**Nota implementativa:** usa `GET /history?workspace=<id>&page=N` — stesso endpoint della Dashboard.

---

## Schermata 6 — Wiki legale

**Layout a due colonne:**

**Colonna sinistra — WikiIndex (220px):**
- Search box full-text (`GET /wiki?q=...`)
- Filtri materia come pill: Tutti · Penale · Civile · Tributario · (tag auto dal backend)
- Lista pagine ordinata per data, con titolo e data generazione
- Pagina attiva: bordo sinistro blu + background evidenziato

**Colonna destra — WikiPage:**
- Header: titolo pagina + data generazione + agente che l'ha prodotta
- Azioni: `⬇ PDF` · `💬 Chiedi` (apre Chat con questa pagina come contesto)
- Contenuto strutturato in sezioni (Markdown renderizzato con `react-markdown`):
  - Inquadramento normativo
  - Elementi costitutivi / Principi chiave
  - Giurisprudenza rilevante
- Citazioni normative e sentenze: link colorati inline (blu/verde), cliccabili

---

## Modifiche backend necessarie

| Priorità | Endpoint | Note |
|----------|----------|------|
| ALTA | `POST /query/stream` | SSE streaming — già documentato in `06-frontend.md` |
| ALTA | CORS `allow_origins: ["http://localhost:5173"]` | Verificare configurazione esistente |
| ALTA | `GET /documents` · `POST /documents/{id}/folder` | Lista documenti + assegnazione cartella |
| ALTA | `POST /folders` · `GET /folders` · `DELETE /folders/{id}` | CRUD cartelle per workspace |
| MEDIA | `GET /wiki` · `GET /wiki/{slug}` | Lista + pagina singola |
| MEDIA | `GET /history` | Storico query per workspace (per Dashboard + Cronologia) |

---

## Comportamenti trasversali

- **Workspace isolation**: tutte le chiamate API includono `?workspace=<id>` come query param
- **Error states**: ogni pagina ha uno stato di errore esplicito con messaggio e retry
- **Loading skeletons**: placeholder animati durante il fetch iniziale
- **Toast notifications**: feedback non-bloccante per azioni async (upload completato, cartella creata, ecc.)
- **Keyboard shortcuts**: `Ctrl+K` → focus sull'input chat da qualsiasi schermata

---

## Stima sviluppo

| Sprint | Contenuto | Durata |
|--------|-----------|--------|
| 1 | Setup Vite+shadcn+Tailwind · AppShell · Dashboard · Chat MVP (no stream) | 1 settimana |
| 2 | Streaming SSE · ReviewerBadge · ResponseCard completa · Cronologia | 1 settimana |
| 3 | Upload + IngestionProgress · Cartelle (CRUD) · DocumentList | 1 settimana |
| 4 | Wiki viewer · WikiIndex · citazioni inline · export PDF | 1 settimana |

**MVP completo: ~4 settimane** con uno sviluppatore frontend.

---

## Deploy locale

```powershell
cd frontend
npm install
npm run dev       # http://localhost:5173 (sviluppo con HMR)
npm run build     # build produzione in dist/
npm run preview   # serve il build su http://localhost:4173
```

Il frontend comunica con la FastAPI su `http://127.0.0.1:8765`.
Aggiungere `.superpowers/` al `.gitignore`.
