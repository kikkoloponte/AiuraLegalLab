import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, FolderOpen, ArrowRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useWorkspace } from '@/context/WorkspaceContext'
import { useHistory } from '@/hooks/useHistory'
import { greetingByHour, formatDate } from '@/lib/utils'
import { cn } from '@/lib/utils'

const VERDICT_DOT: Record<string, string> = {
  PASS: 'bg-green-500',
  FAIL: 'bg-red-500',
  WARN: 'bg-yellow-500',
  RE_RETRIEVAL: 'bg-yellow-500',
}

export function Dashboard() {
  const { workspace } = useWorkspace()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const { data: history = [] } = useHistory(workspace)

  const handleAsk = () => {
    if (!query.trim()) return
    navigate('/chat', { state: { initialQuery: query.trim() } })
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleAsk()
  }

  return (
    <div className="h-full overflow-y-auto px-8 py-8 max-w-2xl mx-auto w-full">
      {/* Greeting */}
      <h1 className="text-xl font-semibold text-foreground mb-1">
        {greetingByHour()} 👋
      </h1>
      <p className="text-sm text-muted-foreground mb-8">
        workspace: <span className="text-primary font-medium">{workspace}</span>
      </p>

      {/* Main input */}
      <div className="rounded-xl border-2 border-primary bg-card p-5 mb-8 space-y-3">
        <p className="text-sm text-muted-foreground">Cosa ti serve oggi?</p>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Fai una domanda legale o carica un documento dello studio..."
          className="w-full bg-background border border-border rounded-lg px-3 py-2.5 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary transition-colors"
        />
        <div className="flex gap-2">
          <Button size="sm" onClick={handleAsk} className="gap-1.5">
            <MessageSquare className="w-4 h-4" />
            Fai una domanda
          </Button>
          <Button size="sm" variant="secondary" onClick={() => navigate('/documents')} className="gap-1.5">
            <FolderOpen className="w-4 h-4" />
            Carica documento
          </Button>
        </div>
      </div>

      {/* Recent queries */}
      {history.length > 0 && (
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-3">
            Ultime query
          </p>
          <div className="space-y-2">
            {history.slice(0, 5).map((entry) => (
              <button
                key={entry.id}
                onClick={() => navigate('/chat', { state: { initialQuery: entry.query } })}
                className="w-full flex items-center gap-3 bg-card hover:bg-accent border border-border rounded-lg px-4 py-3 text-left transition-colors group"
              >
                <span className={cn('w-2 h-2 rounded-full flex-shrink-0', VERDICT_DOT[entry.verdict] ?? 'bg-muted')} />
                <span className="flex-1 text-sm text-foreground truncate">{entry.query}</span>
                <span className="text-xs text-muted-foreground flex-shrink-0">{formatDate(entry.created_at)}</span>
                <ArrowRight className="w-3.5 h-3.5 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
              </button>
            ))}
          </div>
          {history.length > 5 && (
            <button
              onClick={() => navigate('/history')}
              className="mt-3 text-xs text-primary hover:underline"
            >
              Vedi tutta la cronologia →
            </button>
          )}
        </div>
      )}

      {history.length === 0 && (
        <div className="text-center py-12 text-muted-foreground">
          <MessageSquare className="w-8 h-8 mx-auto mb-3 opacity-30" />
          <p className="text-sm">Nessuna query ancora — inizia con una domanda legale</p>
        </div>
      )}
    </div>
  )
}
