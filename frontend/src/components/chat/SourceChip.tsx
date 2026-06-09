import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ExternalLink, Copy, Check, FolderOpen } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Tooltip } from '@/components/ui/tooltip'

type SourceType = 'normativa' | 'giurisprudenza' | 'studio'

interface SourceChipProps {
  sourceId: string
  docId: string
  label: string
  type: SourceType
  url?: string
  snippet?: string
  metadata?: Record<string, string>
  className?: string
  onGraphOpen?: (nodeId: string) => void
}

const TYPE_STYLES: Record<SourceType, string> = {
  normativa:      'bg-blue-950 border-blue-700 text-blue-300 hover:bg-blue-900',
  giurisprudenza: 'bg-green-950 border-green-700 text-green-300 hover:bg-green-900',
  studio:         'bg-purple-950 border-purple-700 text-purple-300 hover:bg-purple-900',
}

const TYPE_ICONS: Record<SourceType, string> = {
  normativa: '📜',
  giurisprudenza: '⚖',
  studio: '📁',
}

const TYPE_LABELS: Record<SourceType, string> = {
  normativa: 'Normativa',
  giurisprudenza: 'Giurisprudenza',
  studio: 'Documento studio',
}

export function SourceChip({
  sourceId, docId, label, type, url, snippet, metadata = {}, className, onGraphOpen,
}: SourceChipProps) {
  const [copied, setCopied] = useState(false)
  const navigate = useNavigate()

  const handleClick = () => {
    if (url) {
      window.open(url, '_blank', 'noopener,noreferrer')
      return
    }
    if (type === 'studio' && docId) {
      navigate('/documents')
      return
    }
    // Copia il sourceId (o URN) negli appunti
    navigator.clipboard.writeText(sourceId).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  // Costruisce le righe di metadati da mostrare nel tooltip
  const metaRows: { label: string; value: string }[] = []
  // Normativa
  if (metadata.articolo)  metaRows.push({ label: 'Articolo', value: metadata.articolo })
  if (metadata.titolo)    metaRows.push({ label: 'Titolo', value: metadata.titolo })
  if (metadata.fonte && metadata.fonte !== metadata.titolo)
                          metaRows.push({ label: 'Fonte', value: metadata.fonte })
  if (metadata.valid_from && metadata.valid_from !== 'None')
                          metaRows.push({ label: 'In vigore dal', value: metadata.valid_from })
  if (metadata.valid_to && metadata.valid_to !== 'None')
                          metaRows.push({ label: 'Fino al', value: metadata.valid_to })
  // Giurisprudenza
  if (metadata.organo)    metaRows.push({ label: 'Organo', value: metadata.organo })
  if (metadata.numero)    metaRows.push({ label: 'Numero', value: metadata.numero })
  if (metadata.anno)      metaRows.push({ label: 'Anno', value: metadata.anno })
  if (metadata.materia)   metaRows.push({ label: 'Materia', value: metadata.materia })
  if (metadata.chunk_type) metaRows.push({ label: 'Estratto', value: metadata.chunk_type })

  const tooltipContent = (
    <div className="space-y-1.5 max-w-[300px]">
      {/* Header */}
      <div className="flex items-center justify-between gap-2">
        <span className="font-semibold text-foreground text-[0.7rem]">{TYPE_LABELS[type]}</span>
        {url && <span className="text-[0.65rem] text-blue-400 flex items-center gap-0.5"><ExternalLink className="w-2.5 h-2.5" />apri originale</span>}
        {type === 'studio' && <span className="text-[0.65rem] text-purple-400 flex items-center gap-0.5"><FolderOpen className="w-2.5 h-2.5" />vai ai documenti</span>}
      </div>

      {/* Metadati strutturati */}
      {metaRows.length > 0 && (
        <div className="space-y-0.5 border-t border-border pt-1.5">
          {metaRows.map((r) => (
            <div key={r.label} className="flex gap-1.5 text-[0.65rem]">
              <span className="text-muted-foreground flex-shrink-0 w-16">{r.label}</span>
              <span className="text-foreground/90 line-clamp-1">{r.value}</span>
            </div>
          ))}
        </div>
      )}

      {/* sourceId / URN grezzo */}
      <p className="font-mono text-[0.6rem] text-muted-foreground/60 break-all leading-tight border-t border-border pt-1">
        {sourceId}
      </p>

      {/* Snippet */}
      {snippet && snippet.trim() && (
        <p className="text-[0.7rem] text-foreground/80 leading-snug border-t border-border pt-1.5">
          {snippet.slice(0, 260)}{snippet.length > 260 ? '…' : ''}
        </p>
      )}

      {/* Hint azione */}
      <p className="text-[0.6rem] text-muted-foreground/50 italic pt-0.5">
        {url ? 'Clicca per aprire il documento originale'
          : type === 'studio' ? 'Clicca per aprire i Documenti'
          : type === 'giurisprudenza' ? 'Clicca per copiare il riferimento sentenza'
          : 'Clicca per copiare il riferimento'}
      </p>
    </div>
  )

  return (
    <span className="inline-flex items-center gap-0.5">
      <Tooltip content={tooltipContent} side="top">
        <button
          onClick={handleClick}
          className={cn(
            'inline-flex items-center gap-1.5 border rounded-md px-2 py-1 text-xs font-medium transition-colors cursor-pointer',
            TYPE_STYLES[type],
            className
          )}
        >
          <span>{TYPE_ICONS[type]}</span>
          <span className="max-w-[160px] truncate">{label}</span>
          {copied
            ? <Check className="w-3 h-3 opacity-80 flex-shrink-0" />
            : url
              ? <ExternalLink className="w-3 h-3 opacity-60 flex-shrink-0" />
              : type === 'studio'
                ? <FolderOpen className="w-3 h-3 opacity-50 flex-shrink-0" />
                : <Copy className="w-3 h-3 opacity-40 flex-shrink-0" />
          }
        </button>
      </Tooltip>
      {type === 'normativa' && onGraphOpen && (
        <button
          onClick={(e) => { e.stopPropagation(); onGraphOpen(sourceId) }}
          title="Vedi nel grafo"
          className="text-blue-400/60 hover:text-blue-300 transition-colors px-0.5 text-[11px]"
        >
          🕸
        </button>
      )}
    </span>
  )
}
