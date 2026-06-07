import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { Network } from 'lucide-react'
import { GraphCanvas } from '@/components/graph/GraphCanvas'
import { GraphSearch } from '@/components/graph/GraphSearch'
import { NodeCard } from '@/components/graph/NodeCard'
import { useGraph } from '@/hooks/useGraph'
import type { GraphNode } from '@/hooks/useGraph'

export function Graph() {
  const [searchParams] = useSearchParams()
  const {
    graphData, selectedNode, setSelectedNode,
    loading, error, searchResults,
    fetchSubgraph, searchNodes, reset,
  } = useGraph()

  // Pre-carica se arriva con ?center=<id>
  useEffect(() => {
    const center = searchParams.get('center')
    if (center) fetchSubgraph(center, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node)
    fetchSubgraph(node.id, false)
  }

  return (
    <div className="flex h-full overflow-hidden">
      {/* Sidebar sinistra */}
      <aside className="w-[260px] flex-shrink-0 flex flex-col border-r border-border bg-card px-3 py-3 gap-3 overflow-y-auto">
        <div className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide">
          Esplora grafo
        </div>

        <GraphSearch
          onSelect={(node) => {
            setSelectedNode(node)
            fetchSubgraph(node.id, true)
          }}
          searchNodes={searchNodes}
          results={searchResults}
        />

        {graphData.nodes.length > 0 && (
          <button
            onClick={reset}
            className="text-[10px] text-muted-foreground hover:text-foreground transition-colors text-left"
          >
            ✕ Svuota canvas
          </button>
        )}

        {selectedNode && (
          <NodeCard
            node={selectedNode}
            onExpand={() => fetchSubgraph(selectedNode.id, false)}
          />
        )}

        {/* Legenda */}
        <div className="mt-auto pt-3 border-t border-border space-y-1.5">
          <p className="text-[10px] text-muted-foreground/60 uppercase tracking-wide">Legenda</p>
          <LegendItem color="#1d4ed8" label="Norma" />
          <LegendItem color="#166534" label="Sentenza" />
          <div className="pt-1 space-y-1">
            <LegendLink color="#3b82f6" label="interpreta" />
            <LegendLink color="#a855f7" label="applicata_in" />
            <LegendLink color="#475569" label="cita" />
          </div>
        </div>
      </aside>

      {/* Canvas */}
      <main className="flex-1 relative bg-[#050f1a] overflow-hidden">
        {loading && graphData.nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center z-10">
            <span className="text-sm text-muted-foreground animate-pulse">Caricamento grafo…</span>
          </div>
        )}

        {error && (
          <div className="absolute top-3 left-1/2 -translate-x-1/2 z-10 bg-destructive/20 border border-destructive/40 text-destructive text-xs px-4 py-2 rounded-lg">
            {error}
          </div>
        )}

        {graphData.nodes.length === 0 && !loading && (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-muted-foreground">
            <Network className="w-12 h-12 opacity-10" />
            <p className="text-sm">Cerca una norma o sentenza per esplorare il grafo</p>
            <p className="text-xs opacity-50">Es: "art.2043", "Cass 12345"</p>
          </div>
        )}

        {graphData.nodes.length > 0 && (
          <>
            <GraphCanvas
              graphData={graphData}
              selectedNodeId={selectedNode?.id}
              onNodeClick={handleNodeClick}
            />
            <div className="absolute bottom-3 right-3 text-[10px] text-muted-foreground/40">
              {graphData.nodes.length} nodi · {graphData.links.length} archi
            </div>
          </>
        )}
      </main>
    </div>
  )
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
      <span className="text-[10px] text-muted-foreground">{label}</span>
    </div>
  )
}

function LegendLink({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className="w-3 h-0.5 flex-shrink-0" style={{ backgroundColor: color }} />
      <span className="text-[10px] text-muted-foreground">{label}</span>
    </div>
  )
}
