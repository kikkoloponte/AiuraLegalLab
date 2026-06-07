import { useState, useRef, type KeyboardEvent } from 'react'
import { SendHorizonal, Loader2, Layers } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSend: (query: string, mode: 'standard' | 'deep') => void
  loading?: boolean
  className?: string
}

export function ChatInput({ onSend, loading = false, className }: ChatInputProps) {
  const [text, setText] = useState('')
  const [mode, setMode] = useState<'standard' | 'deep'>('standard')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const q = text.trim()
    if (!q || loading) return
    onSend(q, mode)
    setText('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 160) + 'px'
  }

  const toggleMode = () => setMode((m) => m === 'standard' ? 'deep' : 'standard')
  const isDeep = mode === 'deep'

  return (
    <div className={cn('border-t border-border bg-card px-4 py-3 space-y-2', className)}>
      {/* Mode toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={toggleMode}
          title={isDeep ? 'Modalità deep: due fasi LLM (più lento, più dettagliato)' : 'Modalità standard: singola fase LLM'}
          className={cn(
            'flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border transition-colors',
            isDeep
              ? 'border-violet-600 text-violet-400 bg-violet-950/40 hover:bg-violet-950/60'
              : 'border-border text-muted-foreground hover:border-muted-foreground hover:text-foreground'
          )}
        >
          <Layers className="w-3 h-3" />
          {isDeep ? 'Deep' : 'Standard'}
        </button>
        {isDeep && (
          <span className="text-xs text-muted-foreground/60">
            Analisi in 2 fasi — normativa poi giurisprudenziale
          </span>
        )}
      </div>

      {/* Input */}
      <div className="flex items-end gap-2 bg-background border border-border rounded-lg px-3 py-2 focus-within:border-primary transition-colors">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder="Fai una domanda legale... (Invio per inviare, Shift+Invio per andare a capo)"
          rows={1}
          data-chat-input
          className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground resize-none outline-none min-h-[24px] max-h-[160px] leading-6"
          disabled={loading}
        />
        <Button
          size="sm"
          onClick={handleSend}
          disabled={!text.trim() || loading}
          className={cn(
            'h-8 w-8 p-0 flex-shrink-0 mb-0.5',
            isDeep && 'bg-violet-700 hover:bg-violet-600'
          )}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <SendHorizonal className="w-4 h-4" />
          )}
        </Button>
      </div>

      <p className="text-xs text-muted-foreground/50 text-center">
        AiUra cita solo fonti nella KB verificata — sempre revisionare prima dell'uso processuale
      </p>
    </div>
  )
}
