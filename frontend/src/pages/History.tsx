import { useState } from 'react'
import { History as HistoryIcon, ChevronDown } from 'lucide-react'
import { useWorkspace } from '@/context/WorkspaceContext'
import { useHistory } from '@/hooks/useHistory'
import type { HistoryEntry } from '@/hooks/useHistory'
import { formatDate } from '@/lib/utils'
import { cn } from '@/lib/utils'
import { ResponseCard } from '@/components/chat/ResponseCard'
import type { LegalResponse, Source } from '@/components/chat/ResponseCard'

// ---------------------------------------------------------------------------
// Costanti UI
// ---------------------------------------------------------------------------

const VERDICT_LABEL: Record<string, string> = {
  PASS: '✅', FAIL: '❌', WARN: '⚠️', RE_RETRIEVAL: '🔄',
}

const VERDICT_DOT: Record<string, string> = {
  PASS: 'bg-green-500', FAIL: 'bg-red-500',
  WARN: 'bg-yellow-500', RE_RETRIEVAL: 'bg-yellow-500',
}

const ORGANO_MAP: Record<string, string> = {
  cassazione: 'Cass.', tar: 'TAR', consiglio_stato: 'Cons. St.',
  corte_cost: 'Corte Cost.', corte_conti: 'Corte Conti',
}

// ---------------------------------------------------------------------------
// Helper: converte HistoryEntry.sources[] → Source[] per ResponseCard
// ---------------------------------------------------------------------------

function mapHistorySource(s: HistoryEntry['sources'][number]): Source {
  const meta = s.metadata ?? {}
  const sourceId = s.source_id ?? ''
  const corpus   = meta.corpus ?? ''

  let type: Source['type'] = 'normativa'
  if (corpus === 'giurisprudenza' || sourceId.startsWith('giurisprudenza_')) {
    type = 'giurisprudenza'
  } else if (corpus === 'studio') {
    type = 'studio'
  }

  let label = sourceId
  if (type === 'giurisprudenza') {
    if (!meta.organo && !meta.numero && !meta.anno) {
      label = meta.titolo?.slice(0, 50) || meta.materia || sourceId
    } else {
      const org = ORGANO_MAP[meta.organo ?? ''] ?? meta.organo ?? 'Sent.'
      const num = meta.numero ? `n.${meta.numero}` : ''
      const yr  = meta.anno  ? `/${meta.anno}` : ''
      label = [org, num + yr].filter(Boolean).join(' ') || sourceId
    }
  } else if (meta.articolo && meta.titolo) {
    label = `${meta.articolo} — ${meta.titolo}`.slice(0, 60)
  } else if (meta.articolo) {
    label = meta.articolo
  } else if (meta.titolo) {
    label = meta.titolo.slice(0, 50)
  } else if (sourceId.length > 40) {
    label = sourceId.slice(sourceId.lastIndexOf(':') + 1)
  }

  let url: string | undefined
  if (sourceId.startsWith('urn:nir:')) {
    url = `https://www.normattiva.it/uri-res/N2Ls?${sourceId}`
  }

  return {
    source_id: sourceId,
    doc_id:    s.doc_id ?? '',
    label,
    type,
    snippet:   s.snippet ?? '',
    url,
    metadata:  meta,
  }
}

// ---------------------------------------------------------------------------
// HistoryDetail — mostra la risposta completa di una voce
// ---------------------------------------------------------------------------

function HistoryDetail({ entry }: { entry: HistoryEntry }) {
  const response: LegalResponse = {
    summary:          entry.answer || entry.answer_summary || entry.query,
    analysis_sections: entry.analysis_sections as LegalResponse['analysis_sections'],
    analysis_fase_1:   entry.analysis_fase_1   as LegalResponse['analysis_fase_1'],
    analysis_fase_2:   entry.analysis_fase_2   as LegalResponse['analysis_fase_2'],
    mode:              (entry.mode ?? 'standard') as 'standard' | 'deep',
    fase_2_available:  (entry.analysis_fase_2?.length ?? 0) > 0,
    verdict:           entry.verdict as LegalResponse['verdict'],
    confidence:        entry.confidence as LegalResponse['confidence'],
    sources:           entry.sources.map(mapHistorySource),
    elapsed_ms:        Math.round(entry.duration_total_s * 1000),
    gaps:              [],
    // history_id solo se il feedback non è ancora stato inviato
    history_id:        entry.feedback_at ? undefined : entry.id,
  }

  return (
    <div className="border-t border-border bg-background/40 px-2 py-3">
      <ResponseCard response={response} />
    </div>
  )
}

// ---------------------------------------------------------------------------
// StarBadge — stelle in amber
// ---------------------------------------------------------------------------

function StarBadge({ rating }: { rating: number }) {
  return (
    <span className="text-amber-400 text-xs tracking-tight flex-shrink-0">
      {'★'.repeat(rating)}{'☆'.repeat(5 - rating)}
    </span>
  )
}

// ---------------------------------------------------------------------------
// History page
// ---------------------------------------------------------------------------

export function History() {
  const { workspace }  = useWorkspace()
  const [feedbackOnly, setFeedbackOnly] = useState(false)
  const [expandedId, setExpandedId]     = useState<string | null>(null)

  const { data: history = [], isLoading } = useHistory(workspace, 1, feedbackOnly)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground text-sm">
        Caricamento cronologia...
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div className="max-w-2xl mx-auto">

        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-foreground mb-1 flex items-center gap-2">
              <HistoryIcon className="w-4 h-4 text-primary" />
              Cronologia
            </h2>
            <p className="text-xs text-muted-foreground">
              workspace: <span className="text-primary">{workspace}</span>
            </p>
          </div>

          {/* Filtro Solo valutate */}
          <button
            onClick={() => {
              setFeedbackOnly((f) => !f)
              setExpandedId(null)
            }}
            className={cn(
              'text-xs px-3 py-1.5 rounded-full border transition-colors flex items-center gap-1.5',
              feedbackOnly
                ? 'bg-teal-900/60 border-teal-500 text-teal-300'
                : 'bg-muted border-border text-muted-foreground hover:bg-accent',
            )}
          >
            <span>⭐</span>
            Solo valutate
          </button>
        </div>

        {/* Empty state */}
        {history.length === 0 && (
          <div className="text-center py-16 text-muted-foreground">
            <HistoryIcon className="w-8 h-8 mx-auto mb-3 opacity-20" />
            <p className="text-sm">
              {feedbackOnly ? 'Nessuna risposta valutata' : 'Nessuna query nella cronologia'}
            </p>
          </div>
        )}

        {/* Lista */}
        <div className="space-y-2">
          {history.map((entry) => {
            const isExpanded = expandedId === entry.id

            return (
              <div
                key={entry.id}
                className="border border-border rounded-lg overflow-hidden"
              >
                {/* Row principale */}
                <button
                  onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                  className="w-full flex items-center gap-3 bg-card hover:bg-accent px-4 py-3 text-left transition-colors group"
                >
                  <span className="text-base flex-shrink-0">{VERDICT_LABEL[entry.verdict] ?? '•'}</span>
                  <span className="flex-1 text-sm text-foreground truncate">{entry.query}</span>

                  {/* Badge feedback */}
                  {entry.feedback_rating && (
                    <StarBadge rating={entry.feedback_rating} />
                  )}
                  {(entry.feedback_tags ?? []).slice(0, 2).map((tag) => (
                    <span
                      key={tag}
                      className="hidden sm:inline text-[10px] px-1.5 py-0.5 rounded bg-teal-900/50 text-teal-300 border border-teal-700 flex-shrink-0"
                    >
                      {tag}
                    </span>
                  ))}

                  <span className="text-xs text-muted-foreground flex-shrink-0 hidden sm:block">
                    {formatDate(entry.created_at)}
                  </span>
                  <span className={cn('w-2 h-2 rounded-full flex-shrink-0 sm:hidden', VERDICT_DOT[entry.verdict])} />
                  <ChevronDown
                    className={cn(
                      'w-3.5 h-3.5 text-muted-foreground flex-shrink-0 transition-transform',
                      isExpanded && 'rotate-180',
                    )}
                  />
                </button>

                {/* Dettaglio espandibile */}
                {isExpanded && <HistoryDetail entry={entry} />}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
