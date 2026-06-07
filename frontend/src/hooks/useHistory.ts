import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

type AnalysisSectionRaw = { step: string; content: string; citations: unknown[] }
type SourceRaw = {
  source_id: string
  doc_id: string
  snippet: string
  score: number
  metadata: Record<string, string>
  source_layer?: string
}

export interface HistoryEntry {
  id: string
  query: string
  verdict: 'PASS' | 'FAIL' | 'WARN' | 'RE_RETRIEVAL'
  confidence: 'HIGH' | 'MEDIUM' | 'LOW'
  mode: string
  // Risposta completa
  answer: string
  answer_summary: string
  analysis_sections: AnalysisSectionRaw[]
  analysis_fase_1:   AnalysisSectionRaw[]
  analysis_fase_2:   AnalysisSectionRaw[]
  sources: SourceRaw[]
  sources_count: number
  duration_total_s: number
  created_at: string
  workspace: string
  // Feedback (opzionali)
  feedback_rating?: number
  feedback_tags:    string[]
  feedback_note?:   string
  feedback_at?:     string
}

interface HistoryResponse {
  entries: HistoryEntry[]
  total: number
  page: number
  limit: number
}

export function useHistory(workspace: string, page = 1, feedbackOnly = false) {
  return useQuery<HistoryEntry[]>({
    queryKey: ['history', workspace, page, feedbackOnly],
    queryFn: async () => {
      const { data } = await apiClient.get<HistoryResponse>('/history', {
        params: { workspace, page, limit: 20, feedback_only: feedbackOnly },
      })
      return data.entries
    },
    retry: false,
    placeholderData: [],
  })
}
