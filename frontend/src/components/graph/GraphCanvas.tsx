import { useRef, useEffect, useCallback } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { NodeObject, LinkObject, ForceGraphMethods } from 'react-force-graph-2d'
import type { GraphData, GraphNode } from '@/hooks/useGraph'

interface GraphCanvasProps {
  graphData: GraphData
  selectedNodeId?: string
  onNodeClick: (node: GraphNode) => void
  height?: number
  compact?: boolean
}

function nodeColor(n: NodeObject, selectedNodeId?: string): string {
  if (n.id === selectedNodeId) return '#f59e0b'
  if (n['type'] === 'norma') return '#1d4ed8'
  return '#166534'
}

function linkColor(l: LinkObject): string {
  const t = l['type'] as string
  if (t === 'interpreta') return '#3b82f6'
  if (t === 'applicata_in') return '#a855f7'
  return '#475569'
}

export function GraphCanvas({ graphData, selectedNodeId, onNodeClick, height, compact = false }: GraphCanvasProps) {
  const fgRef = useRef<ForceGraphMethods>()

  // Zoom to fit whenever graph data changes
  useEffect(() => {
    if (graphData.nodes.length > 0) {
      setTimeout(() => fgRef.current?.zoomToFit(400, 20), 100)
    }
  }, [graphData])

  const handleNodeClick = useCallback((node: NodeObject) => {
    onNodeClick(node as unknown as GraphNode)
  }, [onNodeClick])

  return (
    <ForceGraph2D
      ref={fgRef}
      graphData={graphData}
      nodeId="id"
      nodeColor={(n) => nodeColor(n, selectedNodeId)}
      nodeLabel={(n) => (n as GraphNode).label}
      nodeRelSize={compact ? 4 : 6}
      linkColor={linkColor}
      linkWidth={1}
      linkDirectionalArrowLength={compact ? 0 : 3}
      linkDirectionalArrowRelPos={1}
      onNodeClick={handleNodeClick}
      backgroundColor="#050f1a"
      width={undefined}
      height={height}
      showNavInfo={false}
    />
  )
}
