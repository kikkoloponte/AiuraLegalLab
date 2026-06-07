import { useState } from 'react'
import { Star, CheckCircle2, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { submitFeedback } from '@/api/client'

export const ALLOWED_TAGS = [
  'Utile',
  'Parziale',
  'Errata',
  'Da approfondire',
  'Citazioni corrette',
  'Citazioni errate',
] as const

type Tag = (typeof ALLOWED_TAGS)[number]
type Status = 'idle' | 'submitting' | 'done' | 'error'

interface FeedbackSectionProps {
  historyId: string | undefined
}

export function FeedbackSection({ historyId }: FeedbackSectionProps) {
  const [open, setOpen]               = useState(false)
  const [hoverRating, setHoverRating] = useState(0)
  const [rating, setRating]           = useState(0)
  const [selectedTags, setSelectedTags] = useState<Set<Tag>>(new Set())
  const [note, setNote]               = useState('')
  const [status, setStatus]           = useState<Status>('idle')
  const [errorMsg, setErrorMsg]       = useState('')
  // Valori salvati — mostrati nel badge post-submit
  const [savedRating, setSavedRating] = useState(0)
  const [savedTags, setSavedTags]     = useState<Tag[]>([])

  const disabled = !historyId

  const toggleTag = (tag: Tag) => {
    setSelectedTags((prev) => {
      const next = new Set(prev)
      next.has(tag) ? next.delete(tag) : next.add(tag)
      return next
    })
  }

  const handleSubmit = async () => {
    if (!historyId || rating === 0) return
    setStatus('submitting')
    setErrorMsg('')
    try {
      await submitFeedback(historyId, rating, Array.from(selectedTags), note || undefined)
      setSavedRating(rating)
      setSavedTags(Array.from(selectedTags))
      setStatus('done')
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore'
      if (msg === 'ALREADY_SUBMITTED') {
        setErrorMsg('Hai già valutato questa risposta.')
      } else {
        setErrorMsg('Impossibile salvare la valutazione. Riprova.')
      }
      setStatus('error')
    }
  }

  // ── Badge permanente post-submit ───────────────────────────────────────────
  if (status === 'done') {
    return (
      <div className="px-4 py-3 flex items-center gap-2 flex-wrap">
        <CheckCircle2 className="w-4 h-4 text-teal-400 flex-shrink-0" />
        <span className="text-xs text-teal-300 font-medium">Valutazione salvata</span>
        <span className="text-amber-400 text-sm tracking-tight">
          {'★'.repeat(savedRating)}{'☆'.repeat(5 - savedRating)}
        </span>
        {savedTags.map((tag) => (
          <span
            key={tag}
            className="text-[10px] px-1.5 py-0.5 rounded bg-teal-900/50 border border-teal-700 text-teal-300"
          >
            {tag}
          </span>
        ))}
      </div>
    )
  }

  // ── Bottone toggle ─────────────────────────────────────────────────────────
  return (
    <div>
      <button
        onClick={() => !disabled && setOpen((o) => !o)}
        disabled={disabled}
        title={disabled ? 'Ricarica la pagina per abilitare la valutazione' : undefined}
        className={cn(
          'w-full flex items-center gap-1.5 px-4 py-2.5 text-xs transition-colors',
          disabled
            ? 'text-muted-foreground/40 cursor-not-allowed'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent/40 cursor-pointer',
        )}
      >
        <Star className="w-3.5 h-3.5" />
        <span>{open ? 'Chiudi valutazione' : 'Valuta risposta'}</span>
        <span className={cn('ml-auto text-[10px] transition-transform', open && 'rotate-180')}>▾</span>
      </button>

      {/* ── Form espanso ────────────────────────────────────────────────── */}
      {open && !disabled && (
        <div className="px-4 pb-4 space-y-3 border-t border-border pt-3">

          {/* Stelle */}
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
              <button
                key={i}
                onMouseEnter={() => setHoverRating(i)}
                onMouseLeave={() => setHoverRating(0)}
                onClick={() => setRating(i)}
                className="text-xl leading-none transition-colors"
              >
                <span className={cn(
                  i <= (hoverRating || rating) ? 'text-amber-400' : 'text-muted-foreground/30'
                )}>
                  ★
                </span>
              </button>
            ))}
            {rating > 0 && (
              <span className="ml-2 text-xs text-muted-foreground">
                {['', 'Pessima', 'Scarsa', 'Discreta', 'Buona', 'Ottima'][rating]}
              </span>
            )}
          </div>

          {/* Chip tag */}
          <div className="flex flex-wrap gap-1.5">
            {ALLOWED_TAGS.map((tag) => {
              const active = selectedTags.has(tag)
              return (
                <button
                  key={tag}
                  onClick={() => toggleTag(tag)}
                  className={cn(
                    'text-xs px-2.5 py-1 rounded-md border transition-colors',
                    active
                      ? 'bg-teal-900/60 border-teal-500 text-teal-200'
                      : 'bg-muted border-border text-muted-foreground hover:bg-accent',
                  )}
                >
                  {tag}
                </button>
              )
            })}
          </div>

          {/* Nota */}
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value.slice(0, 500))}
            placeholder="Note opzionali (max 500 caratteri)..."
            rows={2}
            className="w-full text-xs bg-muted border border-border rounded-md px-3 py-2 text-foreground placeholder:text-muted-foreground/50 resize-none focus:outline-none focus:ring-1 focus:ring-ring"
          />
          {note.length > 400 && (
            <p className="text-[10px] text-muted-foreground text-right -mt-2">{note.length}/500</p>
          )}

          {/* Messaggio errore */}
          {status === 'error' && (
            <p className="text-xs text-red-400">{errorMsg}</p>
          )}

          {/* Submit */}
          <div className="flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={rating === 0 || status === 'submitting'}
              className={cn(
                'flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-md border transition-colors',
                rating === 0 || status === 'submitting'
                  ? 'opacity-40 cursor-not-allowed bg-muted border-border text-muted-foreground'
                  : 'bg-teal-900 border-teal-600 text-teal-200 hover:bg-teal-800 cursor-pointer',
              )}
            >
              {status === 'submitting' && <Loader2 className="w-3 h-3 animate-spin" />}
              Invia valutazione
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
