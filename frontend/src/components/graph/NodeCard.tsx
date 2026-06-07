import { Network } from 'lucide-react'
import type { GraphNode } from '@/hooks/useGraph'

interface NodeCardProps {
  node: GraphNode
  onExpand: () => void
}

export function NodeCard({ node, onExpand }: NodeCardProps) {
  const isNorma = node.type === 'norma'

  return (
    <div className="mt-3 bg-muted/50 border border-border rounded-lg p-3 space-y-2">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-xs font-semibold text-foreground truncate">{node.label}</p>
          <p className="text-[10px] text-muted-foreground mt-0.5">
            {isNorma ? 'Norma' : 'Sentenza'}
          </p>
        </div>
        <span className={`text-[10px] border rounded px-1.5 py-0.5 flex-shrink-0 ${
          isNorma
            ? 'bg-blue-950 border-blue-700 text-blue-300'
            : 'bg-green-950 border-green-700 text-green-300'
        }`}>
          {isNorma ? 'N' : 'S'}
        </span>
      </div>

      {/* Metadati */}
      <div className="space-y-0.5">
        {isNorma && node.meta.urn && node.meta.urn !== node.id && (
          <MetaRow label="URN" value={String(node.meta.urn)} mono />
        )}
        {!isNorma && node.meta.organo && (
          <MetaRow label="Organo" value={String(node.meta.organo)} />
        )}
        {!isNorma && node.meta.sezione && (
          <MetaRow label="Sezione" value={String(node.meta.sezione)} />
        )}
        {!isNorma && node.meta.anno && (
          <MetaRow label="Anno" value={String(node.meta.anno)} />
        )}
      </div>

      <button
        onClick={onExpand}
        className="w-full flex items-center justify-center gap-1.5 bg-primary/10 hover:bg-primary/20 border border-primary/30 rounded-md py-1.5 text-xs text-primary transition-colors"
      >
        <Network className="w-3 h-3" />
        Espandi vicini
      </button>
    </div>
  )
}

function MetaRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="flex gap-1.5 text-[10px]">
      <span className="text-muted-foreground flex-shrink-0 w-12">{label}</span>
      <span className={`text-foreground/80 truncate ${mono ? 'font-mono text-[9px]' : ''}`}>
        {value}
      </span>
    </div>
  )
}
