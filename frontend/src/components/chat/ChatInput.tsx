import { useState, useRef, type KeyboardEvent } from 'react'
import { SendHorizonal, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSend: (query: string) => void
  loading?: boolean
  className?: string
}

export function ChatInput({ onSend, loading = false, className }: ChatInputProps) {
  const [text, setText] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = () => {
    const q = text.trim()
    if (!q || loading) return
    onSend(q)
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

  return (
    <div className={cn('border-t border-border bg-card px-4 py-3 space-y-2', className)}>
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
          className="h-8 w-8 p-0 flex-shrink-0 mb-0.5"
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
