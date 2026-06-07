import { ResponseCard, type LegalResponse } from './ResponseCard'
import { AgentStatusBar } from './AgentStatusBar'
import { cn } from '@/lib/utils'

interface UserMessageProps {
  text: string
}

export function UserMessage({ text }: UserMessageProps) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[70%] bg-primary text-primary-foreground rounded-2xl rounded-br-sm px-4 py-2.5 text-sm leading-relaxed">
        {text}
      </div>
    </div>
  )
}

interface AIMessageProps {
  response?: LegalResponse
  streaming?: boolean
  agentStatus?: string
  error?: string
  className?: string
  onGraphOpen?: (nodeId: string) => void
}

export function AIMessage({ response, streaming, agentStatus, error, className, onGraphOpen }: AIMessageProps) {
  if (error) {
    return (
      <div className={cn('text-xs text-red-400 bg-red-950/50 border border-red-800 rounded-lg px-3 py-2 max-w-[85%]', className)}>
        ❌ {error}
      </div>
    )
  }

  // Streaming: mostra sempre la status bar.
  // Se ci sono già sezioni parziali (fasi completate), le mostriamo sotto.
  if (streaming) {
    return (
      <div className={cn('max-w-[85%] space-y-3', className)}>
        <AgentStatusBar status={agentStatus ?? ''} />
        {response && <ResponseCard response={response} onGraphOpen={onGraphOpen} />}
      </div>
    )
  }

  if (!response) {
    return (
      <div className={cn('max-w-[85%]', className)}>
        <AgentStatusBar status={agentStatus ?? ''} />
      </div>
    )
  }

  return (
    <div className={cn('max-w-[85%]', className)}>
      <ResponseCard response={response} onGraphOpen={onGraphOpen} />
    </div>
  )
}
