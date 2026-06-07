import { useState, useCallback } from 'react'
import { apiClient } from '@/api/client'

export interface GraphNode {
  id: string
  type: 'norma' | 'sentenza'
  label: string
  meta: Record<string, string | number>
}

export interface GraphLink {
  source: string
  target: string
  type: string
}

export interface GraphData {
  nodes: GraphNode[]
  links: GraphLink[]
}

export function useGraph() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] })
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [searchResults, setSearchResults] = useState<GraphNode[]>([])

  const fetchSubgraph = useCallback(async (id: string, replace = false) => {
    setLoading(true)
    setError(null)
    try {
      const res = await apiClient.get<GraphData>('/graph/subgraph', {
        params: { center: id, depth: 1, limit: replace ? 50 : 20 },
      })
      const data = res.data
      if (replace) {
        setGraphData(data)
      } else {
        setGraphData(prev => {
          const existingNodeIds = new Set(prev.nodes.map(n => n.id))
          const existingLinkKeys = new Set(
            prev.links.map(l => `${l.source}→${l.target}`)
          )
          const newNodes = data.nodes.filter(n => !existingNodeIds.has(n.id))
          const newLinks = data.links.filter(
            l => !existingLinkKeys.has(`${l.source}→${l.target}`)
          )
          return {
            nodes: [...prev.nodes, ...newNodes],
            links: [...prev.links, ...newLinks],
          }
        })
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Errore sconosciuto'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [])

  const searchNodes = useCallback(async (q: string) => {
    if (q.length < 2) {
      setSearchResults([])
      return
    }
    try {
      const res = await apiClient.get<{ results: GraphNode[] }>('/graph/search', {
        params: { q, limit: 20 },
      })
      setSearchResults(res.data.results)
    } catch {
      setSearchResults([])
    }
  }, [])

  const reset = useCallback(() => {
    setGraphData({ nodes: [], links: [] })
    setSelectedNode(null)
    setSearchResults([])
    setError(null)
  }, [])

  return {
    graphData,
    selectedNode,
    setSelectedNode,
    loading,
    error,
    searchResults,
    fetchSubgraph,
    searchNodes,
    reset,
  }
}
