# Graph Viewer — Design Spec
**Data:** 2026-06-05
**Feature:** Visualizzazione interattiva del grafo sentenza→norma

---

## Contesto

Il sistema mantiene un grafo NetworkX DiGraph in `workspaces/jurisprudence_graph.json` con:
- **236.931 nodi** — tipo `sentenza` (id hex, organo, numero, anno) e tipo `norma` (id = URN/shortform)
- **1.375.250 archi** — tipo `interpreta`, `applicata_in`, `cita`

Il grafo non può essere inviato intero al browser. Tutta la logica di filtraggio avviene lato backend, che espone sottografi su richiesta.

---

## Entry point e layout

### 1. Pagina dedicata `/graph`

Layout a due colonne:
- **Sidebar sinistra (260px):** barra di ricerca unificata norma+sentenza, lista risultati, scheda del nodo selezionato
- **Canvas destra:** grafo force-directed interattivo (react-force-graph-2d)

L'utente cerca una norma o sentenza → clicca sul risultato → il canvas mostra il sottografo centrato su quel nodo. Ogni click su un nodo nel canvas espande i suoi vicini (espansione progressiva).

### 2. Pannello laterale nella Chat

Quando la risposta cita una norma, `SourceChip` mostra un'icona 🕸. Click → `GraphPanel` si apre a destra della risposta (il layout chat si restringe per fare spazio). Il pannello mostra il sottografo depth=1 centrato sulla norma cliccata. Un link "Apri pagina /graph →" naviga alla pagina dedicata con il nodo pre-selezionato (`/graph?center=<id>`).

---

## Architettura backend

### Nuovo file: `aiura_legal/api/graph_router.py`

Montato in `app.py` su prefisso `/graph`.

Il grafo viene caricato una sola volta in memoria all'avvio dell'API (evento `startup`), letto da `workspaces/jurisprudence_graph.json`. Nessuna rilettura per richiesta.

#### `GET /graph/search`

```
Parametri:
  q: str          — testo di ricerca (min 2 caratteri)
  limit: int = 20 — max risultati

Logica:
  - Norme: match case-insensitive su node["id"] e node.get("urn", "")
  - Sentenze: match su organo, numero, anno (formato "Cass. 12345/2025")

Risposta:
  { "results": [ { "id", "type", "label", "meta" }, ... ] }
```

`label` è una stringa leggibile: per norme → `id` (es. `art.2043`), per sentenze → `Cass. n.12345/2025 — I Civile`.
`meta` contiene i campi extra del nodo (organo, anno, sezione per sentenze; urn per norme).

#### `GET /graph/subgraph`

```
Parametri:
  center: str       — id del nodo centrale
  depth: int = 1    — profondità BFS (1 o 2)
  limit: int = 50   — max nodi nel sottografo

Logica:
  BFS dal nodo center fino a depth livelli.
  Se i nodi superano limit, si tronca per grado (nodi più connessi prima).

Risposta:
  {
    "nodes": [ { "id", "type", "label", "meta" }, ... ],
    "links": [ { "source", "target", "type" }, ... ]
  }
```

Il formato `nodes/links` è quello nativo di react-force-graph.

Il backend supporta `depth=1` e `depth=2`. Il frontend usa sempre `depth=1` — depth=2 è riservato a usi futuri via API diretta.

---

## Architettura frontend

### Nuovi file

```
frontend/src/
├── pages/
│   └── Graph.tsx
├── components/graph/
│   ├── GraphCanvas.tsx
│   ├── GraphSearch.tsx
│   ├── NodeCard.tsx
│   └── GraphPanel.tsx
└── hooks/
    └── useGraph.ts
```

### File modificati

| File | Modifica |
|------|---------|
| `src/App.tsx` | Aggiunge `<Route path="graph" element={<Graph />} />` |
| `src/components/layout/Sidebar.tsx` | Aggiunge voce nav "Grafo" con icona `Network` |
| `src/components/chat/SourceChip.tsx` | Aggiunge icona 🕸 per norme, prop `onGraphOpen` |
| `src/pages/Chat.tsx` | Aggiunge stato `graphPanelNorm` + rendering `GraphPanel` |

### Libreria grafo

**`react-force-graph-2d`** — wrapper React di force-graph (d3-force). Scelto perché:
- Già in roadmap (06-frontend.md)
- Supporta grafi dinamici (aggiunta nodi/archi a runtime)
- Canvas 2D = performance accettabile fino a ~500 nodi
- API semplice: `graphData={{ nodes, links }}`, callback `onNodeClick`

```bash
npm install react-force-graph-2d
```

### `useGraph.ts`

Gestisce lo stato del grafo nel frontend:
- `graphData: { nodes, links }` — stato corrente del canvas
- `selectedNode` — nodo cliccato (per NodeCard)
- `fetchSubgraph(id)` — chiama `/graph/subgraph`, **merge** nel graphData esistente (nodi/archi già presenti non vengono duplicati)
- `searchNodes(q)` — chiama `/graph/search`
- `reset()` — svuota il canvas

### `GraphCanvas.tsx`

Wrapper attorno a `ForceGraph2D`. Configurazione:
- Nodi: colore per tipo (`norma` → blu `#1d4ed8`, `sentenza` → verde scuro `#14532d` con bordo `#22c55e`)
- Archi: colore per tipo (`interpreta` → `#3b82f6`, `applicata_in` → `#a855f7`, `cita` → `#64748b`)
- `onNodeClick(node)` → chiama `fetchSubgraph(node.id)` + imposta `selectedNode`
- Label visibili solo su zoom ≥ 2 (evita clutter)

### `GraphSearch.tsx`

Input con debounce 300ms. Mostra lista risultati come pill cliccabili. Click → `fetchSubgraph(id)`.

### `NodeCard.tsx`

Scheda nodo selezionato nella sidebar. Mostra:
- Per norma: id, URN completo, numero archi uscenti
- Per sentenza: organo, numero, anno, sezione, numero norme citate, numero sentenze che la citano
- Pulsante "Espandi vicini" (chiama `fetchSubgraph`)

### `GraphPanel.tsx`

Pannello compatto (280px) per la chat. Contiene `GraphCanvas` in modalità ridotta. Footer con conteggio nodi + link "Apri pagina /graph →" (`/graph?center=<id>`).

### `Graph.tsx` (pagina)

Legge `?center=<id>` da URL al mount e chiama `fetchSubgraph(id)` se presente. Permette di atterrare sulla pagina con un nodo pre-selezionato (dal link in `GraphPanel`).

---

## Flusso dati completo

```
Pagina /graph:
  1. utente digita → GET /graph/search?q=<testo>
  2. clicca risultato → GET /graph/subgraph?center=<id>&depth=1&limit=50
     → graphData sostituito
  3. clicca nodo nel canvas → GET /graph/subgraph?center=<id>&depth=1&limit=20
     → graphData merge (nodi/archi nuovi aggiunti, duplicati ignorati)

Chat panel:
  1. click 🕸 su SourceChip → GraphPanel apre
  2. GraphPanel mount → GET /graph/subgraph?center=<urn>&depth=1&limit=20
  3. "Apri /graph →" → navigate("/graph?center=<id>")
```

---

## Gestione errori

- Nodo non trovato nel grafo → 404, frontend mostra toast "Nodo non trovato nel grafo"
- Grafo non ancora caricato (startup) → 503, frontend mostra "Grafo in caricamento..."
- `q` troppo corto (< 2 char) → ricerca non parte (solo client-side)

---

## Cosa non è incluso in questo spec

- Filtri per tipo arco (interpreta/applicata_in/cita) — sprint successivo
- Depth > 1 esposto in UI — troppo pesante senza paginazione
- Export sottografo — sprint successivo
- Colorazione nodi per organo (cassazione/tar/corte_cost) — sprint successivo
