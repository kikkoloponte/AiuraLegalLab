import { useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { useToast } from '@/context/ToastContext'

export type QuestioneStato = 'proposto' | 'approvato' | 'rifiutato'

export interface Questione {
  id: string
  formulazione: string
  materia: string
  parole_chiave: string[]
  norme_pertinenti: string[]
  decisioni_pertinenti: string[]
  stato: QuestioneStato
}

interface QuestioneWithVersion {
  questione: Questione
  version: string
}

export interface NodeSearchResult {
  id: string
  label: string
}

interface QuestioniListResult {
  items: Questione[]
  version: string
}

export function useQuestioniList(stato?: QuestioneStato) {
  return useQuery<QuestioniListResult>({
    queryKey: ['questioni', stato ?? 'all'],
    queryFn: async () => {
      const { data } = await apiClient.get('/questioni', { params: stato ? { stato } : {} })
      return { items: data.items, version: data.version }
    },
    placeholderData: { items: [], version: '' },
  })
}

export function useUpdateQuestione() {
  const qc = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async ({
      id,
      changes,
      expectedVersion,
    }: {
      id: string
      changes: Partial<Pick<Questione, 'formulazione' | 'materia' | 'parole_chiave' | 'norme_pertinenti' | 'decisioni_pertinenti' | 'stato'>>
      expectedVersion: string
    }) => {
      const { data } = await apiClient.put<QuestioneWithVersion>(`/questioni/${id}`, {
        changes,
        expected_version: expectedVersion,
      })
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['questioni'] })
    },
    onError: (err: Error) => {
      if (err.message.includes('409') || err.message.toLowerCase().includes('modificat')) {
        toast('Questa voce è stata modificata altrove — ricaricata.', 'error')
      } else {
        toast(err.message, 'error')
      }
      qc.invalidateQueries({ queryKey: ['questioni'] })
    },
  })
}

export function useSearchNodes() {
  // useCallback: identità stabile tra render — è una dipendenza di useEffect
  // in NodeIdPicker, una nuova funzione ogni render causerebbe un loop
  // (l'effect richiamerebbe setResults([]) ad ogni render, cambiando stato,
  // ri-renderizzando, ricreando la funzione, richiamando l'effect di nuovo).
  return useCallback(async (q: string, nodeType: 'article' | 'sentenza'): Promise<NodeSearchResult[]> => {
    if (q.length < 2) return []
    try {
      const { data } = await apiClient.get('/questioni/search-nodes', {
        params: { q, node_type: nodeType },
      })
      return data.results
    } catch {
      return []
    }
  }, [])
}
