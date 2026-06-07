import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { X, ExternalLink } from 'lucide-react'
import { GraphCanvas } from './GraphCanvas'
import { useGraph } from '@/hooks/useGraph'
import type { GraphNode } from '@/hooks/useGraph'

interface GraphPanelProps {
  centerId: string
  onClose: () => void
}

export function GraphPanel({ centerId, onClose }: GraphPanelProps) {
  const navigate = useNavigate()
  const { graphData, selectedNode, setSelectedNode, loading, fetchSubgraph } = useGraph()

  useEffect(() => {
    fetchSubgraph(centerId, true)
  }, [centerId]) // eslint-disable-line react-hooks/exhaustive-deps

  const handleNodeClick = (node: GraphNode) => {
    setSelectedNode(node)
    fetchSubgraph(node.id, false)
  }

  return (
    <div className="w-[280px] flex-shrink-0 flex flex-col border-l border-border bg-[#050f1a]">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border/50">
        <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wide truncate">
          Grafo · {selectedNode?.label ?? centerId}
        </span>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground transition-colors ml-2 flex-shrink-0">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Canvas */}
      <div className="flex-1 relative">
        {loading && graphData.nodes.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs text-muted-foreground animate-pulse">Caricamento…</span>
          </div>
        )}
        {graphData.nodes.length > 0 && (
          <GraphCanvas
            graphData={graphData}
            selectedNodeId={selectedNode?.id}
            onNodeClick={handleNodeClick}
            height={220}
            compact
          />
        )}
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-border/50 flex items-center justify-between">
        <span className="text-[10px] text-muted-foreground">
          {graphData.nodes.length} nodi
        </span>
        <button
          onClick={() => navigate(`/graph?center=${encodeURIComponent(centerId)}`)}
          className="flex items-center gap-1 text-[10px] text-primary hover:text-primary/80 transition-colors"
        >
          Apri in /graph
          <ExternalLink className="w-2.5 h-2.5" />
        </button>
      </div>
    </div>
  )
}
