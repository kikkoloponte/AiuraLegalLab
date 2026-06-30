import { useState, useEffect, useRef } from 'react'
import { Search, X } from 'lucide-react'
import { useSearchChunks, type ChunkCorpus, type ChunkSearchResult } from '@/hooks/useIstitutiGiuridici'

interface ChunkPickerProps {
  value: string | null
  onChange: (id: string | null) => void
  corpus?: ChunkCorpus
  placeholder?: string
}

/**
 * Campo source_mongo_id con autocomplete: l'utente digita testo libero,
 * vede label+preview dei chunk che matchano e sceglie — niente ObjectId a
 * memoria. Il campo rimane editabile a mano per chi vuole incollare un id diretto.
 */
export function ChunkPicker({ value, onChange, corpus, placeholder }: ChunkPickerProps) {
  const searchChunks = useSearchChunks()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<ChunkSearchResult[]>([])
  const [open, setOpen] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const wrapperRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    clearTimeout(debounceRef.current)
    if (query.length < 2) {
      setResults([])
      setOpen(false)
      return
    }
    debounceRef.current = setTimeout(async () => {
      const r = await searchChunks(query, corpus)
      setResults(r)
      setOpen(true)
    }, 350)
    return () => clearTimeout(debounceRef.current)
  }, [query, corpus, searchChunks])

  // chiudi dropdown se click fuori
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSelect = (r: ChunkSearchResult) => {
    onChange(r.id)
    setQuery('')
    setResults([])
    setOpen(false)
  }

  const handleClear = () => {
    onChange(null)
    setQuery('')
  }

  const inputClass =
    'w-full bg-card border border-border rounded-md px-2.5 py-1.5 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-mono'

  return (
    <div ref={wrapperRef} className="space-y-1">
      {/* valore corrente selezionato */}
      {value && (
        <div className="flex items-center gap-1.5 text-xs bg-muted border border-border rounded-md px-2 py-1">
          <span className="flex-1 font-mono text-foreground truncate">{value}</span>
          <button
            type="button"
            onClick={handleClear}
            className="text-muted-foreground hover:text-foreground flex-shrink-0"
            aria-label="Rimuovi source_mongo_id"
          >
            <X className="w-3 h-3" />
          </button>
        </div>
      )}

      {/* campo ricerca con autocomplete */}
      <div className="relative">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-muted-foreground pointer-events-none" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder={placeholder ?? 'Cerca chunk per testo (es. "Art. 321", "confisca"…)'}
          className={`${inputClass} pl-7 text-xs font-sans`}
        />
      </div>

      {/* dropdown risultati */}
      {open && results.length > 0 && (
        <div className="relative z-50">
          <div className="absolute top-0 left-0 right-0 bg-card border border-border rounded-lg shadow-lg max-h-56 overflow-y-auto">
            {results.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => handleSelect(r)}
                className="w-full text-left px-3 py-2 hover:bg-accent transition-colors border-b border-border last:border-0"
              >
                <div className="text-xs font-medium text-foreground truncate">{r.label}</div>
                <div className="text-[10px] text-muted-foreground truncate mt-0.5">{r.preview}</div>
                <div className="text-[10px] text-muted-foreground/60 font-mono mt-0.5">{r.id}</div>
              </button>
            ))}
          </div>
        </div>
      )}

      {open && results.length === 0 && query.length >= 2 && (
        <p className="text-[11px] text-muted-foreground">Nessun chunk trovato.</p>
      )}
    </div>
  )
}
