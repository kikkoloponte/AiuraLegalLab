import { useState, useCallback } from 'react'
import type { LegalResponse } from '@/components/chat/ResponseCard'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text?: string
  response?: LegalResponse
  streaming?: boolean
  agentStatus?: string
  error?: string
}

type AnalysisSectionRaw = { step: string; content: string; citations: unknown[] }

// Mappa la QueryResponse del backend → LegalResponse del frontend
function mapBackendResponse(data: Record<string, unknown>): LegalResponse {
  const sources = (data.sources as Array<Record<string, unknown>> ?? []).map((s) => {
    const sourceId = String(s.source_id ?? '')
    const docId = String(s.doc_id ?? '')
    const meta = (s.metadata as Record<string, string> | undefined) ?? {}
    const corpus = meta.corpus ?? ''

    let type: 'normativa' | 'giurisprudenza' | 'studio' = 'normativa'
    if (corpus === 'giurisprudenza' || sourceId.startsWith('giurisprudenza_')) {
      type = 'giurisprudenza'
    } else if (corpus === 'studio') {
      type = 'studio'
    }

    let label = sourceId
    if (type === 'giurisprudenza') {
      // Costruisce "Cass. n.1234/2023" o "TAR n.456/2022" dal metadata
      const organoMap: Record<string, string> = {
        cassazione: 'Cass.', tar: 'TAR', consiglio_stato: 'Cons. St.',
        corte_cost: 'Corte Cost.', corte_conti: 'Corte Conti',
      }
      const organoLabel = organoMap[meta.organo ?? ''] ?? meta.organo ?? 'Sent.'
      const num = meta.numero ? `n.${meta.numero}` : ''
      const yr  = meta.anno  ? `/${meta.anno}` : ''
      label = [organoLabel, num + yr].filter(Boolean).join(' ') || sourceId
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
      doc_id: docId,
      label,
      type,
      snippet: String(s.snippet ?? ''),
      url,
      metadata: meta,
    }
  })

  const sections = (data.analysis_sections as AnalysisSectionRaw[] ?? [])
  const fase1   = (data.analysis_fase_1  as AnalysisSectionRaw[] ?? [])
  const fase2   = (data.analysis_fase_2  as AnalysisSectionRaw[] ?? [])
  const mode    = String(data.mode ?? 'standard') as 'standard' | 'deep'

  // Summary: preferisce QUESTIONE, poi QUALIFICAZIONE, poi CONCLUSIONE, poi answer
  const allSections = mode === 'deep' ? [...fase1, ...fase2] : sections
  const summaryStep =
    allSections.find((s) => s.step === 'QUESTIONE') ??
    allSections.find((s) => s.step === 'QUALIFICAZIONE') ??
    allSections.find((s) => s.step === 'CONCLUSIONE')
  const summary = (summaryStep?.content ?? String(data.answer ?? '').slice(0, 400)) || 'Nessuna risposta disponibile.'

  const verdict    = String(data.reviewer_verdict ?? 'PASS') as LegalResponse['verdict']
  const confidence = String(data.overall_confidence ?? data.retrieval_confidence ?? 'LOW') as LegalResponse['confidence']

  return {
    summary,
    analysis_sections: sections as LegalResponse['analysis_sections'],
    analysis_fase_1:   fase1   as LegalResponse['analysis_fase_1'],
    analysis_fase_2:   fase2   as LegalResponse['analysis_fase_2'],
    mode,
    fase_2_available: Boolean(data.fase_2_available ?? false),
    verdict,
    confidence,
    sources,
    elapsed_ms: Math.round(Number(data.duration_total_s ?? 0) * 1000),
    gaps: data.gaps as string[] ?? [],
    history_id: String(data.history_id ?? '') || undefined,
  }
}

const PHASE_LABELS: Record<string, string> = {
  FRAMING:        'Fase 1 · Inquadramento giuridico...',
  NORMATIVA:      'Fase 2 · Analisi normativa...',
  GIURISPRUDENZA: 'Fase 3 · Orientamenti giurisprudenziali...',
  SINTESI:        'Fase 4 · Sintesi e conclusione...',
}

export function useChat(workspace: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loading, setLoading] = useState(false)
  const [agentStatus, setAgentStatus] = useState('')

  const sendQuery = useCallback(async (query: string, mode: 'standard' | 'deep' = 'standard') => {
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', text: query }
    const aiId = crypto.randomUUID()
    const aiMsg: ChatMessage = {
      id: aiId,
      role: 'assistant',
      streaming: true,
      agentStatus: 'S2 Researcher · recupero fonti...',
    }

    setMessages((prev) => [...prev, userMsg, aiMsg])
    setLoading(true)
    setAgentStatus('S2 Researcher · recupero fonti...')

    // Accumula sezioni delle 4 fasi per costruire la risposta progressiva
    const accumulatedSections: AnalysisSectionRaw[] = []
    let finalVerdict = 'PASS'
    let finalConfidence = 'MEDIUM'

    try {
      const res = await fetch('/api/query/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          workspace,
          intent: 'fattispecie_analysis',
          mode,
        }),
      })

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`)
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        // Processa tutti i blocchi SSE completi (separati da \n\n)
        const blocks = buffer.split('\n\n')
        buffer = blocks.pop() ?? ''   // l'ultimo blocco potrebbe essere incompleto

        for (const block of blocks) {
          if (!block.trim()) continue
          // Estrai la riga data: dal blocco (ignora event:, id:, :ping ecc.)
          const dataLine = block.split('\n').find((l) => l.startsWith('data: '))
          if (!dataLine) continue
          const raw = dataLine.slice(6).trim()
          if (!raw) continue

          let event: Record<string, unknown>
          try { event = JSON.parse(raw) } catch { continue }

          if (event.type === 'retrieval_done') {
            const statusMsg = 'S3 Analyst · ragionamento sequenziale...'
            setAgentStatus(statusMsg)
            setMessages((prev) =>
              prev.map((m) => m.id === aiId ? { ...m, agentStatus: statusMsg } : m)
            )

          } else if (event.type === 'phase_complete') {
            const phaseName = String(event.name ?? '')
            const sections = (event.sections as AnalysisSectionRaw[] ?? [])

            // Aggiunge le nuove sezioni all'accumulatore
            accumulatedSections.push(...sections)

            // Aggiorna status con fase successiva attesa
            const nextPhase = event.phase as number
            const nextLabel = PHASE_LABELS[
              ['', 'NORMATIVA', 'GIURISPRUDENZA', 'SINTESI', ''][nextPhase] ?? ''
            ] ?? 'S5 Reviewer · verifica citazioni...'
            const statusMsg = PHASE_LABELS[phaseName] ?? nextLabel
            setAgentStatus(nextLabel)

            // Aggiorna il messaggio con le sezioni accumulate finora (risposta progressiva)
            const partialResponse = _buildPartialResponse(query, accumulatedSections)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiId
                  ? { ...m, agentStatus: nextLabel, response: partialResponse }
                  : m
              )
            )
            void statusMsg

          } else if (event.type === 'review_done') {
            finalVerdict = String(event.verdict ?? 'PASS')
            finalConfidence = String(event.overall_confidence ?? 'MEDIUM')

            const finalResponse = _buildFinalResponse(
              query, accumulatedSections, finalVerdict, finalConfidence
            )
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiId
                  ? { ...m, streaming: false, response: finalResponse, agentStatus: undefined }
                  : m
              )
            )

          } else if (event.type === 'status') {
            // Backward compat con eventi status legacy
            const statusMsg = String(event.message ?? '')
            setAgentStatus(statusMsg)
            setMessages((prev) =>
              prev.map((m) => m.id === aiId ? { ...m, agentStatus: statusMsg } : m)
            )

          } else if (event.type === 'result') {
            // Backward compat: risposta bloccante da /query non-stream
            const response = mapBackendResponse(event.data as Record<string, unknown>)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiId ? { ...m, streaming: false, response, agentStatus: undefined } : m
              )
            )

          } else if (event.type === 'clarification_needed') {
            const question = String(event.question ?? '')
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiId
                  ? { ...m, streaming: false, text: question, agentStatus: undefined }
                  : m
              )
            )

          } else if (event.type === 'error') {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aiId
                  ? { ...m, streaming: false, error: String(event.message ?? 'Errore SSE'), agentStatus: undefined }
                  : m
              )
            )
          }
        }
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Errore di rete'
      setMessages((prev) =>
        prev.map((m) =>
          m.id === aiId
            ? { ...m, streaming: false, error: errorMsg, agentStatus: undefined }
            : m
        )
      )
    } finally {
      setLoading(false)
      setAgentStatus('')
    }
  }, [workspace])

  const clear = useCallback(() => setMessages([]), [])

  return { messages, loading, agentStatus, sendQuery, clear } as const
}

// ---------------------------------------------------------------------------
// Helpers per costruire LegalResponse parziale/finale dalle fasi accumulate
// ---------------------------------------------------------------------------

function _buildPartialResponse(
  query: string,
  sections: AnalysisSectionRaw[],
): import('@/components/chat/ResponseCard').LegalResponse {
  const summary = sections.find((s) => s.step === 'QUESTIONE')?.content
    ?? sections.find((s) => s.step === 'QUALIFICAZIONE')?.content
    ?? query

  return {
    summary,
    analysis_sections: sections as import('@/components/chat/ResponseCard').LegalResponse['analysis_sections'],
    mode: 'standard',
    verdict: 'PASS',
    confidence: 'MEDIUM',
    sources: [],
    gaps: [],
  }
}

function _buildFinalResponse(
  query: string,
  sections: AnalysisSectionRaw[],
  verdict: string,
  confidence: string,
): import('@/components/chat/ResponseCard').LegalResponse {
  const summary = sections.find((s) => s.step === 'QUESTIONE')?.content
    ?? sections.find((s) => s.step === 'CONCLUSIONE')?.content
    ?? query

  return {
    summary,
    analysis_sections: sections as import('@/components/chat/ResponseCard').LegalResponse['analysis_sections'],
    mode: 'standard',
    verdict: verdict as import('@/components/chat/ResponseCard').LegalResponse['verdict'],
    confidence: confidence as import('@/components/chat/ResponseCard').LegalResponse['confidence'],
    sources: [],
    gaps: [],
  }
}
