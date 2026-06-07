# Frontend UI — Piano di Implementazione
**Spec di riferimento:** `2026-06-03-frontend-ui-design.md`
**Data:** 3 giugno 2026

---

## Prerequisiti (prima di iniziare)

- [ ] Backend FastAPI avviato su `http://127.0.0.1:8765`
- [ ] Node.js ≥ 18 installato
- [ ] Aggiungere `.superpowers/` al `.gitignore` del progetto

---

## Sprint 1 — Setup + AppShell + Dashboard + Chat base
**Durata stimata: 1 settimana**
**Obiettivo: l'avvocato può fare una query e vedere la risposta**

### 1.1 — Setup progetto

- [ ] `npm create vite@latest frontend -- --template react-ts`
- [ ] Installare dipendenze: `shadcn/ui`, `tailwindcss`, `react-router-dom`, `@tanstack/react-query`, `axios`
- [ ] Configurare Tailwind dark mode (`darkMode: 'class'` in `tailwind.config.js`)
- [ ] Inizializzare shadcn/ui (`npx shadcn-ui@latest init`)
- [ ] Configurare `vite.config.ts` con proxy verso `http://127.0.0.1:8765`
- [ ] Creare `src/api/client.ts` — Axios con `baseURL` e interceptor errori

### 1.2 — AppShell e routing

- [ ] Creare `AppShell.tsx` — layout con sidebar fissa (200px) + `<Outlet />`
- [ ] Creare `Sidebar.tsx`:
  - Logo + workspace selector (dropdown statico per ora)
  - Voci nav: Dashboard · Chat · Documenti · Wiki · Cronologia
  - Toggle dark/light in fondo (shadcn `Switch` + `useTheme`)
  - Collasso a icone sotto 1280px
- [ ] Creare `TopBar.tsx` — breadcrumb + data corrente
- [ ] Configurare `App.tsx` con React Router: routes per `/`, `/chat`, `/documents`, `/wiki`, `/history`

### 1.3 — Dashboard

- [ ] Creare `pages/Dashboard.tsx`:
  - Saluto + info workspace
  - Input centrale grande (shadcn `Textarea` o `Input`) con bordo blu, CTA "Fai una domanda" e "Carica documento"
  - Click "Fai una domanda" → naviga a `/chat` con query pre-compilata
  - Sezione "Ultime query" — placeholder statico per ora (dati reali in Sprint 2)

### 1.4 — Chat base (senza streaming)

- [ ] Creare `hooks/useChat.ts` — `POST /query` (versione sync, no SSE)
- [ ] Creare `ChatInput.tsx` — textarea + tasto Invia + disclaimer fisso
- [ ] Creare `ChatMessage.tsx` — bolla utente (destra) e risposta AI (sinistra)
- [ ] Creare `ReviewerBadge.tsx` — badge PASS/FAIL/WARN con colori corretti
- [ ] Creare `SourceChip.tsx` — chip normativa (blu) e giurisprudenza (verde)
- [ ] Creare `ResponseCard.tsx`:
  - Badge reviewer in cima
  - Sezione Sintesi sempre visibile
  - Accordion "Analisi completa" (shadcn `Collapsible`)
  - Lista SourceChip
  - Azioni: Genera atto · Esporta PDF · Wiki → (placeholder per ora)
- [ ] Creare `pages/Chat.tsx` — assembla i componenti, gestisce stato messaggi

---

## Sprint 2 — Streaming SSE + ResponseCard completa + Cronologia
**Durata stimata: 1 settimana**
**Obiettivo: risposta in streaming in tempo reale + storico query**

### 2.1 — Backend: endpoint streaming

- [ ] Aggiungere `POST /query/stream` in FastAPI (SSE con `StreamingResponse`)
- [ ] Verificare CORS: `allow_origins: ["http://localhost:5173"]`

### 2.2 — Streaming nel frontend

- [ ] Aggiornare `hooks/useChat.ts` per usare `EventSource` su `/query/stream`
- [ ] Mostrare indicatore agente attivo durante streaming: `S2 Researcher… → S3 Analyst… → S5 Reviewer…`
- [ ] Risposta si costruisce progressivamente nella `ResponseCard`

### 2.3 — Backend: endpoint history

- [ ] Aggiungere `GET /history?workspace=<id>&page=N` in FastAPI
- [ ] Salvare ogni query+risposta in MongoDB collection `query_history`

### 2.4 — Dashboard ultime query (dati reali)

- [ ] Creare `hooks/useHistory.ts` — `GET /history`
- [ ] Aggiornare `Dashboard.tsx` con lista reale — pallino PASS/FAIL, testo, timestamp, freccia →
- [ ] Click freccia → naviga a `/chat?id=<query_id>` con risposta in read-only + follow-up attivo

### 2.5 — Pagina Cronologia

- [ ] Creare `pages/History.tsx`:
  - Lista paginata (20 per pagina) con `GET /history`
  - Filtro per stato (Tutti / PASS / FAIL / WARN)
  - Ricerca full-text client-side
  - Click "Rivedi" → `/chat?id=<query_id>`

---

## Sprint 3 — Upload documenti + Cartelle
**Durata stimata: 1 settimana**
**Obiettivo: l'avvocato carica i suoi atti e li organizza per fascicolo**

### 3.1 — Backend: endpoint cartelle e documenti

- [ ] `POST /folders` · `GET /folders?workspace=<id>` · `DELETE /folders/{id}` · `PATCH /folders/{id}` (rinomina)
- [ ] `GET /documents?workspace=<id>&folder_id=<id>` — lista documenti filtrata
- [ ] `POST /documents/{id}/folder` — assegna documento a cartella
- [ ] `DELETE /documents/{id}` — elimina documento e chunks

### 3.2 — FolderSidebar

- [ ] Creare `hooks/useFolders.ts` — CRUD cartelle
- [ ] Creare `components/documents/FolderSidebar.tsx`:
  - Lista cartelle con conteggio
  - "Tutti" in cima come filtro universale
  - "+ Nuova cartella" → dialog shadcn con input nome
  - Menu contestuale ⋯ per rinomina ed elimina

### 3.3 — DropZone e IngestionProgress

- [ ] Creare `DropZone.tsx` — drag & drop PDF/DOCX (usa `react-dropzone`)
  - Compatta quando ci sono già documenti, grande quando lista è vuota
  - Mostra dialog selezione cartella di destinazione al momento del drop
- [ ] Creare `IngestionProgress.tsx` — step inline con polling su `GET /ingest/{job_id}/status`:
  1. ✓ Testo estratto
  2. ✓ PII anonimizzate (con conteggi)
  3. ⏳ Chunking e indicizzazione
  4. ○ Analisi rischio S6

### 3.4 — DocumentList e DocumentCard

- [ ] Creare `hooks/useDocuments.ts` — GET/DELETE documenti
- [ ] Creare `DocumentCard.tsx`:
  - Icona tipo · nome file · badge cartella · metadati · stato
  - Azioni: Analizza (→ `/chat?doc_id=<id>`) · Rischio · Elimina · Sposta (cambia cartella)
- [ ] Creare `DocumentList.tsx` — lista filtrata per cartella attiva + header con pulsante Carica
- [ ] Creare `pages/Documents.tsx` — layout due colonne: FolderSidebar + DocumentList

---

## Sprint 4 — Wiki viewer + Export PDF + polish finale
**Durata stimata: 1 settimana**
**Obiettivo: wiki legale navigabile + export + rifinitura UX generale**

### 4.1 — Backend: endpoint wiki

- [ ] `GET /wiki?workspace=<id>&q=<query>` — lista pagine con ricerca opzionale
- [ ] `GET /wiki/{slug}?workspace=<id>` — pagina singola

### 4.2 — WikiIndex e WikiPage

- [ ] Creare `hooks/useWiki.ts` — GET lista + GET pagina singola
- [ ] Creare `WikiPageCard.tsx` — card in lista indice con titolo, data, materia
- [ ] Creare `WikiIndex.tsx`:
  - Search box full-text
  - Filtri materia come pill (tag auto dal backend)
  - Lista pagine con pagina attiva evidenziata (bordo blu)
- [ ] Creare `WikiPage.tsx`:
  - Header con titolo, data, badge agente generatore
  - Azioni: Esporta PDF · "Chiedi" (→ `/chat?wiki_slug=<slug>`)
  - Render Markdown con `react-markdown` + `remark-gfm`
  - Link citazioni inline colorati (blu normativa / verde giurisprudenza)
- [ ] Creare `pages/Wiki.tsx` — layout due colonne: WikiIndex + WikiPage

### 4.3 — Export PDF

- [ ] Azione "Esporta PDF" nella `ResponseCard` — `POST /export/pdf` o client-side con `html2pdf.js`
- [ ] Azione "⬇ PDF" nella WikiPage — stessa logica

### 4.4 — Dashboard workspace selector (funzionale)

- [ ] Collegare il dropdown workspace selector a `GET /workspaces`
- [ ] Salvare workspace attivo in `localStorage` + context React

### 4.5 — Toast notifications

- [ ] Installare shadcn `Toaster`
- [ ] Aggiungere toast per: upload completato · cartella creata · errori API · clipboard copy

### 4.6 — Keyboard shortcut

- [ ] `Ctrl+K` da qualsiasi schermata → focus su input chat

### 4.7 — Error states e loading skeletons

- [ ] Ogni pagina ha skeleton animato durante il fetch iniziale
- [ ] Ogni errore API mostra messaggio leggibile + pulsante Riprova

---

## Checklist finale pre-consegna

- [ ] Test manuale di tutte e 5 le schermate (Dashboard, Chat, Documenti, Wiki, Cronologia)
- [ ] Verificare dark mode e light mode su tutti i componenti
- [ ] Verificare comportamento a 1280px (sidebar collassata a icone)
- [ ] Verificare disclaimer sempre visibile nella chat
- [ ] Verificare badge PASS/FAIL/WARN su risposte reali
- [ ] `npm run build` senza errori TypeScript
- [ ] `npm run preview` → verificare build di produzione funzionante

---

## Dipendenze npm da installare

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend

# Core
npm install react-router-dom @tanstack/react-query axios

# shadcn/ui + Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npx shadcn-ui@latest init

# Componenti shadcn necessari
npx shadcn-ui@latest add button input textarea collapsible dialog dropdown-menu badge toast switch separator skeleton

# Markdown
npm install react-markdown remark-gfm

# Upload
npm install react-dropzone

# Export PDF (Sprint 4)
npm install html2pdf.js
```
