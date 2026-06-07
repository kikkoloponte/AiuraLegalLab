import { useEffect, useRef, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { UserMessage, AIMessage } from '@/components/chat/ChatMessage'
import { ChatInput } from '@/components/chat/ChatInput'
import { GraphPanel } from '@/components/graph/GraphPanel'
import { useChat } from '@/hooks/useChat'
import { useWorkspace } from '@/context/WorkspaceContext'
import { MessageSquare } from 'lucide-react'

export function Chat() {
  const { workspace } = useWorkspace()
  const { messages, loading, sendQuery } = useChat(workspace)
  const bottomRef = useRef<HTMLDivElement>(null)
  const sentRef = useRef(false)
  const location = useLocation()
  const [graphPanelNode, setGraphPanelNode] = useState<string | null>(null)

  // Auto-send query coming from Dashboard (ref guard prevents StrictMode double-fire)
  useEffect(() => {
    const state = location.state as { initialQuery?: string } | null
    if (state?.initialQuery && !sentRef.current) {
      sentRef.current = true
      sendQuery(state.initialQuery)
      window.history.replaceState({}, '')
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex h-full overflow-hidden">
      {/* Colonna chat principale */}
      <div className="flex-1 flex flex-col min-w-0">
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-3">
              <MessageSquare className="w-10 h-10 opacity-20" />
              <p className="text-sm">Fai una domanda legale per iniziare</p>
              <p className="text-xs opacity-60">
                Es: "Quali sono gli elementi costitutivi del reato ex art. 2 D.Lgs. 74/2000?"
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <div key={msg.id}>
              {msg.role === 'user' && msg.text && <UserMessage text={msg.text} />}
              {msg.role === 'assistant' && (
                <AIMessage
                  response={msg.response}
                  streaming={msg.streaming}
                  agentStatus={msg.agentStatus}
                  error={msg.error}
                  onGraphOpen={setGraphPanelNode}
                />
              )}
            </div>
          ))}

          <div ref={bottomRef} />
        </div>

        <ChatInput onSend={(q, mode) => sendQuery(q, mode)} loading={loading} />
      </div>

      {/* Pannello grafo (laterale destro) */}
      {graphPanelNode && (
        <GraphPanel
          centerId={graphPanelNode}
          onClose={() => setGraphPanelNode(null)}
        />
      )}
    </div>
  )
}
