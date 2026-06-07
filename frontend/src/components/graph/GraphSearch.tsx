import { useState, useEffect, useRef } from 'react'
import { Search } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { GraphNode } from '@/hooks/useGraph'

interface GraphSearchProps {
  onSelect: (node: GraphNode) => void
  searchNodes: (q: string) => Promise<void>
  results: GraphNode[]
}

const TYPE_STYLES: Record<string, string> = {
  norma:    'bg-blue-950 border-blue-700 text-blue-300',
  sentenza: 'bg-green-950 border-green-700 text-green-300',
}

export function GraphSearch({ onSelect, searchNodes, results }: GraphSearchProps) {
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    clearTimeout(debounceRef.current)
    if (query.length >= 2) {
      debounceRef.current = setTimeout(() => {
        searchNodes(query)
        setOpen(true)
      }, 300)
    } else {
      setOpen(false)
    }
    return () => clearTimeout(debounceRef.current)
  }, [query, searchNodes])

  const handleSelect = (node: GraphNode) => {
    setQuery(node.label)
    setOpen(false)
    onSelect(node)
  }

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="Cerca norma o sentenza…"
          className="w-full bg-muted border border-border rounded-md pl-8 pr-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      {open && results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-card border border-border rounded-lg shadow-lg max-h-52 overflow-y-auto">
          {results.map((node) => (
            <button
              key={node.id}
              onClick={() => handleSelect(node)}
              className="w-full text-left px-3 py-2 hover:bg-accent transition-colors flex items-center gap-2"
            >
              <span className={cn(
                'text-[10px] border rounded px-1.5 py-0.5 flex-shrink-0',
                TYPE_STYLES[node.type] ?? 'bg-muted border-border text-muted-foreground'
              )}>
                {node.type === 'norma' ? 'N' : 'S'}
              </span>
              <span className="text-xs text-foreground truncate">{node.label}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
