# Graph Viewer — Piano di implementazione
**Spec:** `2026-06-05-graph-viewer-design.md`
**Data:** 2026-06-05

---

## Ordine di esecuzione

```
Step 1  Backend: graph_router.py
Step 2  Backend: mount in app.py + caricamento grafo in lifespan
Step 3  Frontend: npm install react-force-graph-2d
Step 4  Frontend: useGraph.ts
Step 5  Frontend: GraphCanvas.tsx
Step 6  Frontend: GraphSearch.tsx + NodeCard.tsx
Step 7  Frontend: GraphPanel.tsx
Step 8  Frontend: Graph.tsx (pagina)
Step 9  Frontend: App.tsx + Sidebar.tsx (routing + nav)
Step 10 Frontend: SourceChip.tsx + Chat.tsx (integrazione chat)
```

Ogni step è testabile indipendentemente. Il backend (1-2) può essere fatto in
parallelo con l'installazione (3).

---

## Step 1 — `aiura_legal/api/graph_router.py` (nuovo file)

Creare `aiura_legal/api/graph_router.py`.

### Stato globale condiviso con app.py

Il grafo viene iniettato da `app.py` tramite una variabile di modulo:

```python
# graph_router.py
_graph: nx.DiGraph | None = None          # iniettato da app.py al lifespan
_nodes_index: dict[str, dict] = {}        # id → attributi nodo (per ricerca O(1))

def set_graph(g: nx.DiGraph) -> None:
    global _graph, _nodes_index
    _graph = g
    _nodes_index = dict(g.nodes(data=True))
```

### `GET /graph/search`

```python
@router.get("/search")
async def search_nodes(q: str = Query(..., min_length=2), limit: int = 20):
    """Cerca nodi per testo (norma: id/urn, sentenza: organo+numero+anno)."""
```

Logica:
- Se `_graph is None` → HTTP 503 `{"detail": "grafo non caricato"}`
- Itera `_nodes_index`. Per ogni nodo:
  - `type == "norma"`: match su `id` e `urn` (case-insensitive, `q in field`)
  - `type == "sentenza"`: costruisce stringa `f"{organo} {numero} {anno}"`, match su quella
- Ritorna i primi `limit` match come lista `SearchNodeResult`:
  ```python
  class SearchNodeResult(BaseModel):
      id: str
      type: str          # "norma" | "sentenza"
      label: str         # leggibile: "art.2043" | "Cass. n.12345/2025"
      meta: dict         # campi extra del nodo
  ```

Helper `_make_label(node_id, attrs)`:
- `type == "norma"` → `attrs.get("urn", node_id)` (fallback a id)
- `type == "sentenza"` → `f"{attrs['organo'].capitalize()} n.{attrs['numero']}/{attrs['anno']}"`

### `GET /graph/subgraph`

```python
@router.get("/subgraph")
async def get_subgraph(
    center: str,
    depth: int = Query(default=1, ge=1, le=2),
    limit: int = Query(default=50, ge=1, le=200),
):
```

Logica:
- Se `center` non in `_nodes_index` → HTTP 404 `{"detail": "nodo non trovato"}`
- BFS `nx.ego_graph(G, center, radius=depth, undirected=True)` → sottografo
- Se nodi > `limit`: ordina per grado (decrescente), tronca mantenendo `center` sempre incluso
- Serializza in formato react-force-graph:
  ```python
  class SubgraphResponse(BaseModel):
      nodes: list[GraphNode]    # {id, type, label, meta}
      links: list[GraphLink]    # {source, target, type}
  ```
- Gli archi inclusi sono solo quelli tra nodi presenti nel sottografo dopo troncamento

### Dipendenze da aggiungere a `pyproject.toml`

Nessuna nuova — NetworkX è già presente.

---

## Step 2 — Mount in `aiura_legal/api/app.py`

### 2a. Import e dichiarazione variabile

Dopo gli import esistenti, aggiungere:
```python
from aiura_legal.api.graph_router import router as graph_router
from aiura_legal.api.graph_router import set_graph as _set_graph
import networkx as nx
import time as time   # già presente nel file
```

### 2b. Caricamento grafo nel lifespan `_lifespan`

Subito dopo il warm-up indici esistente, aggiungere:

```python
# ── Caricamento grafo giurisprudenziale ───────────────────────────────────
async def _load_graph():
    graph_path = Path(_settings.aiura_workspaces_path) / "jurisprudence_graph.json"
    if not graph_path.exists():
        logger.warning(f"Grafo non trovato: {graph_path} — /graph disabilitato")
        return
    t0 = time.monotonic()
    logger.info("Grafo: caricamento in memoria...")
    loop = asyncio.get_event_loop()
    g = await loop.run_in_executor(None, _load_graph_sync, graph_path)
    _set_graph(g)
    logger.info(f"Grafo: {g.number_of_nodes()} nodi, {g.number_of_edges()} archi — {time.monotonic()-t0:.1f}s")

def _load_graph_sync(path: Path) -> nx.DiGraph:
    data = json.loads(path.read_text(encoding="utf-8"))
    return nx.node_link_graph(data)

asyncio.create_task(_load_graph())
```

Il caricamento è async (run_in_executor) per non bloccare il loop durante il parsing JSON (~50MB).

### 2c. Mount del router

Subito dopo il mount di `jurisprudence_router`:
```python
app.include_router(graph_router, prefix="/graph", tags=["graph"])
```

**Test step 1-2:**
```powershell
python -m aiura_legal.api
# Log atteso: "Grafo: 236931 nodi, 1375250 archi — X.Xs"

curl "http://127.0.0.1:8765/graph/search?q=art.2043"
curl "http://127.0.0.1:8765/graph/subgraph?center=art.2043&depth=1&limit=20"
```

---

## Step 3 — `npm install react-force-graph-2d`

```powershell
cd frontend
npm install react-force-graph-2d
npm install --save-dev @types/react-force-graph-2d   # se disponibile
```

`react-force-graph-2d` non ha tipi ufficiali. Creare
`frontend/src/types/react-force-graph-2d.d.ts` con dichiarazione minimale:

```typescript
declare module 'react-force-graph-2d' {
  import { FC, RefObject } from 'react'
  export interface NodeObject { id: string; [key: string]: unknown }
  export interface LinkObject { source: string | NodeObject; target: string | NodeObject; [key: string]: unknown }
  export interface ForceGraphMethods { zoomToFit(ms?: number): void; centerAt(x?: number, y?: number, ms?: number): void }
  interface ForceGraph2DProps {
    graphData: { nodes: NodeObject[]; links: LinkObject[] }
    nodeColor?: (node: NodeObject) => string
    nodeLabel?: (node: NodeObject) => string
    linkColor?: (link: LinkObject) => string
    linkLabel?: (link: LinkObject) => string
    onNodeClick?: (node: NodeObject, event: MouseEvent) => void
    nodeRelSize?: number
    linkWidth?: number | ((link: LinkObject) => number)
    width?: number
    height?: number
    ref?: RefObject<ForceGraphMethods>
    backgroundColor?: string
    zoom?: number
    minZoom?: number
    maxZoom?: number
  }
  const ForceGraph2D: FC<ForceGraph2DProps>
  export default ForceGraph2D
}
```

---

## Step 4 — `frontend/src/hooks/useGraph.ts` (nuovo file)

```typescript
// Stato e operazioni del grafo. Usato da Graph.tsx e GraphPanel.tsx.
interface GraphNode { id: string; type: 'norma' | 'sentenza'; label: string; meta: Record<string, string> }
interface GraphLink { source: string; target: string; type: string }
interface GraphData { nodes: GraphNode[]; links: GraphLink[] }

export function useGraph() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] })
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<GraphNode[]>([])

  const fetchSubgraph = useCallback(async (id: string, replace = false) => { ... })
  // replace=true → sostituisce graphData (click su risultato ricerca)
  // replace=false → merge (click su nodo nel canvas, espansione)

  const searchNodes = useCallback(async (q: string) => { ... })
  // chiama GET /api/graph/search?q=<q>

  const reset = useCallback(() => {
    setGraphData({ nodes: [], links: [] })
    setSelectedNode(null)
  }, [])

  return { graphData, selectedNode, setSelectedNode, loading, error, searchResults, fetchSubgraph, searchNodes, reset }
}
```

Merge in `fetchSubgraph` (replace=false):
```typescript
const existingIds = new Set(graphData.nodes.map(n => n.id))
const newNodes = data.nodes.filter(n => !existingIds.has(n.id))
const existingLinks = new Set(graphData.links.map(l => `${l.source}→${l.target}`))
const newLinks = data.links.filter(l => !existingLinks.has(`${l.source}→${l.target}`))
setGraphData(prev => ({ nodes: [...prev.nodes, ...newNodes], links: [...prev.links, ...newLinks] }))
```

---

## Step 5 — `frontend/src/components/graph/GraphCanvas.tsx` (nuovo file)

Wrapper sottile attorno a `ForceGraph2D`. Props:

```typescript
interface GraphCanvasProps {
  graphData: GraphData
  selectedNodeId?: string
  onNodeClick: (node: GraphNode) => void
  height?: number          // default: fill container
  compact?: boolean        // true in GraphPanel (nodi più piccoli, no label)
}
```

Colori nodi:
```typescript
const nodeColor = (n: NodeObject) => {
  if (n.id === selectedNodeId) return '#f59e0b'      // ambra = selezionato
  if (n['type'] === 'norma') return '#1d4ed8'        // blu
  return '#14532d'                                    // verde scuro sentenza
}
```

Colori archi:
```typescript
const linkColor = (l: LinkObject) => {
  const t = l['type'] as string
  if (t === 'interpreta') return '#3b82f6'
  if (t === 'applicata_in') return '#a855f7'
  return '#475569'   // cita e altri
}
```

Label: mostrare solo se `!compact`. Usa `nodeLabel` di react-force-graph (tooltip al hover).

Il componente usa `useRef<ForceGraphMethods>` e chiama `zoomToFit(400)` dopo ogni
cambio di `graphData` tramite `useEffect`.

---

## Step 6 — `frontend/src/components/graph/GraphSearch.tsx` e `NodeCard.tsx`

### `GraphSearch.tsx`

Props:
```typescript
interface GraphSearchProps {
  onSelect: (node: GraphNode) => void
}
```

- Input con debounce 300ms (`useEffect` + `setTimeout`)
- Chiama `searchNodes(q)` da `useGraph` (ricevuto via prop o context)
- Mostra lista risultati come `<button>` pill con colore per tipo (blu=norma, verde=sentenza)
- Click → chiama `onSelect(node)` → il parent chiama `fetchSubgraph(id, true)`

### `NodeCard.tsx`

Props:
```typescript
interface NodeCardProps {
  node: GraphNode
  onExpand: () => void    // chiama fetchSubgraph(node.id, false)
}
```

Mostra:
- Norma: `node.label` (URN), badge blu "Norma", pulsante "Espandi vicini"
- Sentenza: organo, numero/anno, sezione (da `node.meta`), badge verde, pulsante "Espandi vicini"

---

## Step 7 — `frontend/src/components/graph/GraphPanel.tsx` (nuovo file)

Pannello compatto (280px fixed width) per la chat.

Props:
```typescript
interface GraphPanelProps {
  centerId: string       // urn/id della norma da centrare
  onClose: () => void
}
```

- Crea un'istanza locale di `useGraph()` (stato isolato dal panel della pagina /graph)
- Al mount: chiama `fetchSubgraph(centerId, true)` con `limit=20`
- Rendering:
  ```
  ┌─ header: "GRAFO · <label>" ──────── [✕] ┐
  │  GraphCanvas compact=true height=220    │
  │  ──────────────────────────────────     │
  │  N nodi · "Apri in /graph →"           │
  └─────────────────────────────────────────┘
  ```
- "Apri in /graph →": `navigate('/graph?center=' + centerId)`

---

## Step 8 — `frontend/src/pages/Graph.tsx` (nuovo file)

```typescript
export function Graph() {
  const [searchParams] = useSearchParams()
  const { graphData, selectedNode, setSelectedNode, loading, error,
          searchResults, fetchSubgraph, searchNodes, reset } = useGraph()

  // Pre-carica se arriva con ?center=<id>
  useEffect(() => {
    const center = searchParams.get('center')
    if (center) fetchSubgraph(center, true)
  }, [])   // eslint-disable-line

  return (
    <div className="flex h-full">
      {/* Sidebar sinistra 260px */}
      <aside className="w-[260px] ...">
        <GraphSearch onSelect={(n) => fetchSubgraph(n.id, true)} searchNodes={searchNodes} results={searchResults} />
        {selectedNode && <NodeCard node={selectedNode} onExpand={() => fetchSubgraph(selectedNode.id, false)} />}
      </aside>
      {/* Canvas */}
      <main className="flex-1 bg-[#050f1a] relative">
        {loading && <Spinner />}
        {error && <ErrorBanner message={error} />}
        {graphData.nodes.length === 0 && !loading && <EmptyState />}
        <GraphCanvas
          graphData={graphData}
          selectedNodeId={selectedNode?.id}
          onNodeClick={(n) => {
            setSelectedNode(n as GraphNode)
            fetchSubgraph(n.id, false)
          }}
        />
        {/* Legenda + zoom controls */}
      </main>
    </div>
  )
}
```

`EmptyState`: testo "Cerca una norma o sentenza per esplorare il grafo".

---

## Step 9 — Routing e navigazione

### `frontend/src/App.tsx`

Aggiungere import e route:
```typescript
import { Graph } from '@/pages/Graph'
// dentro <Route path="/" element={<AppShell />}>
<Route path="graph" element={<Graph />} />
```

### `frontend/src/components/layout/Sidebar.tsx`

Aggiungere alla lista `NAV_ITEMS`:
```typescript
{ to: '/graph', icon: Network, label: 'Grafo legale' }
```

Aggiungere `Network` agli import da `lucide-react`.

---

## Step 10 — Integrazione Chat

### `frontend/src/components/chat/SourceChip.tsx`

Aggiungere prop opzionale:
```typescript
onGraphOpen?: (nodeId: string) => void
```

Nel rendering, per `type === 'normativa'` con `onGraphOpen` definito, aggiungere
un secondo bottone affianco al chip principale:

```tsx
{type === 'normativa' && onGraphOpen && (
  <button
    onClick={(e) => { e.stopPropagation(); onGraphOpen(sourceId) }}
    className="ml-0.5 text-blue-400 hover:text-blue-300 opacity-60 hover:opacity-100 transition-opacity"
    title="Vedi nel grafo"
  >
    🕸
  </button>
)}
```

La prop è opzionale → tutti i chiamanti esistenti di `SourceChip` continuano a
funzionare senza modifiche.

### `frontend/src/pages/Chat.tsx`

Aggiungere:
```typescript
import { GraphPanel } from '@/components/graph/GraphPanel'

// Stato
const [graphPanelNode, setGraphPanelNode] = useState<string | null>(null)

// Nel JSX: layout condizionale
<div className="flex flex-col h-full">
  <div className={cn('flex h-full', graphPanelNode && 'pr-0')}>
    {/* colonna chat (flex-1) */}
    <div className="flex-1 flex flex-col min-w-0">
      {/* contenuto chat esistente invariato */}
    </div>
    {/* pannello grafo */}
    {graphPanelNode && (
      <GraphPanel
        centerId={graphPanelNode}
        onClose={() => setGraphPanelNode(null)}
      />
    )}
  </div>
</div>
```

Passare `onGraphOpen={setGraphPanelNode}` a ogni `SourceChip` di tipo normativa
dentro `ResponseCard` o `ChatMessage` (verificare dove vengono renderizzati i chip).

---

## Ordine di commit consigliato

```
1. feat(api): graph_router — GET /graph/search + /graph/subgraph
2. feat(api): carica jurisprudence_graph al lifespan, monta /graph router
3. feat(frontend): useGraph hook + tipo declarations react-force-graph-2d
4. feat(frontend): GraphCanvas — force-directed con colori per tipo
5. feat(frontend): GraphSearch + NodeCard
6. feat(frontend): GraphPanel — pannello compatto per la chat
7. feat(frontend): pagina /graph + routing + nav Sidebar
8. feat(frontend): SourceChip onGraphOpen + Chat GraphPanel integration
```

---

## Note implementative

- **`nx.ego_graph`** usa BFS undirected di default — corretto per questo caso (vogliamo
  vicini in entrambe le direzioni sentenza↔norma)
- **Deduplicazione merge**: usare `Set` su `id` per nodi e `source→target` per archi
- **ForceGraph2D e SSR**: non ha problemi con Vite, ma se si aggiunge SSR in futuro
  va importato con `dynamic` (non rilevante ora)
- **Grafo non trovato**: se `jurisprudence_graph.json` non esiste, l'API parte comunque
  e `/graph/search` risponde 503 — il frontend mostra "Grafo non disponibile" e la voce
  nav rimane visibile ma con un badge di warning
