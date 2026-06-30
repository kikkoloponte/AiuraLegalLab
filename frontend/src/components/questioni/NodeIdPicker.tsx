import { useState, useEffect, useRef } from 'react'
import { Search, X } from 'lucide-react'
import { useSearchNodes, type NodeSearchResult } from '@/hooks/useQuestioni'

interface NodeIdPickerProps {
  nodeType: 'article' | 'sentenza'
  ids: string[]
  onAdd: (id: string) => void
  onRemove: (id: string) => void
}

/**
 * Input con autocomplete per aggiungere id reali (articoli/sentenze) a
 * norme_pertinenti/decisioni_pertinenti — l'avvocato sceglie da una lista
 * di nodi che esistono davvero nel grafo, non scrive un URN a mano.
 */
export function NodeIdPicker({ nodeType, ids, onAdd, onRemove }: NodeIdPickerProps) {
  const searchNodes = useSearchNodes()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<NodeSearchResult[]>([])
  const [open, setOpen] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  useEffect(() => {
    clearTimeout(debounceRef.current)
    if (query.length < 2) {
      setResults([])
      setOpen(false)
      return
    }
    debounceRef.current = setTimeout(async () => {
      const r = await searchNodes(query, nodeType)
      setResults(r)
      setOpen(true)
    }, 300)
    return () => clearTimeout(debounceRef.current)
  }, [query, nodeType, searchNodes])

  const handleSelect = (result: NodeSearchResult) => {
    onAdd(result.id)
    setQuery('')
    setResults([])
    setOpen(false)
  }

  return (
    <div className="space-y-1.5">
      <div className="flex flex-wrap gap-1.5">
        {ids.map((id) => (
          <span
            key={id}
            className="inline-flex items-center gap-1 text-[11px] bg-muted border border-border rounded px-1.5 py-0.5 text-foreground"
          >
            <span className="max-w-[220px] truncate">{id}</span>
            <button
              type="button"
              onClick={() => onRemove(id)}
              className="text-muted-foreground hover:text-foreground"
              aria-label={`Rimuovi ${id}`}
            >
              <X className="w-3 h-3" />
            </button>
          </span>
        ))}
      </div>

      <div className="relative">
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => results.length > 0 && setOpen(true)}
            placeholder={nodeType === 'article' ? 'Cerca articolo…' : 'Cerca sentenza…'}
            className="w-full bg-muted border border-border rounded-md pl-7 pr-3 py-1 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>

        {open && results.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-card border border-border rounded-lg shadow-lg max-h-48 overflow-y-auto">
            {results.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => handleSelect(r)}
                disabled={ids.includes(r.id)}
                className="w-full text-left px-3 py-1.5 hover:bg-accent transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <span className="text-xs text-foreground block truncate">{r.label}</span>
                <span className="text-[10px] text-muted-foreground block truncate">{r.id}</span>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
