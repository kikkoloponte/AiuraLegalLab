import { useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import { useToast } from '@/context/ToastContext'

export interface RiferimentoNormativo {
  riferimento: string
  source_mongo_id: string | null
}

export interface QuadroNormativo {
  articoli_principali: RiferimentoNormativo[]
  leggi_complementari: RiferimentoNormativo[]
}

export interface DefinizioneNaturaGiuridica {
  testo: string | null
  source_mongo_id: string | null
}

export interface ElementoCostitutivo {
  id_elemento_ui: string
  descrizione: string
  source_mongo_id: string | null
}

export interface MassimaChiave {
  riferimento_sentenza: string
  principio_diritto: string
  source_mongo_id: string | null
}

export interface FormazioneGiurisprudenziale {
  orientamento_prevalente: string | null
  massime_chiave: MassimaChiave[]
  contrasti_risolti_o_aperti: string | null
}

export interface MetadataUI {
  progetto: string
  stato_istanza: string
  fonti_mongodb_coinvolte: string[]
}

export interface IstitutoGiuridicoInput {
  metadata_ui: MetadataUI
  denominazione: string
  codice_riferimento: string
  quadro_normativo: QuadroNormativo
  definizione_e_natura_giuridica: DefinizioneNaturaGiuridica
  elementi_costitutivi: ElementoCostitutivo[]
  formazione_giurisprudenziale: FormazioneGiurisprudenziale
}

export interface IstitutoGiuridico extends IstitutoGiuridicoInput {
  id: string
  version: number
  updated_at: string
}

export function emptyIstituto(): IstitutoGiuridicoInput {
  return {
    metadata_ui: { progetto: 'AiuraLegalLab', stato_istanza: 'ready_for_ui_crud', fonti_mongodb_coinvolte: [] },
    denominazione: '',
    codice_riferimento: 'CC',
    quadro_normativo: { articoli_principali: [], leggi_complementari: [] },
    definizione_e_natura_giuridica: { testo: null, source_mongo_id: null },
    elementi_costitutivi: [],
    formazione_giurisprudenziale: {
      orientamento_prevalente: null,
      massime_chiave: [],
      contrasti_risolti_o_aperti: null,
    },
  }
}

export function useIstitutiList() {
  return useQuery<IstitutoGiuridico[]>({
    queryKey: ['istituti'],
    queryFn: async () => {
      const { data } = await apiClient.get('/istituti')
      return data.items
    },
    placeholderData: [],
  })
}

export function useIstituto(id: string | undefined) {
  return useQuery<IstitutoGiuridico>({
    queryKey: ['istituti', id],
    queryFn: async () => {
      const { data } = await apiClient.get(`/istituti/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useCreateIstituto() {
  const qc = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async (payload: IstitutoGiuridicoInput) => {
      const { data } = await apiClient.post<IstitutoGiuridico>('/istituti', payload)
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['istituti'] })
      toast('Istituto creato.', 'success')
    },
    onError: (err: Error) => toast(err.message, 'error'),
  })
}

export function useUpdateIstituto() {
  const qc = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async ({
      id,
      istituto,
      expectedVersion,
    }: {
      id: string
      istituto: IstitutoGiuridicoInput
      expectedVersion: number
    }) => {
      const { data } = await apiClient.put<IstitutoGiuridico>(`/istituti/${id}`, {
        istituto,
        expected_version: expectedVersion,
      })
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['istituti'] })
      toast('Istituto salvato.', 'success')
    },
    onError: (err: Error) => {
      if (err.message.includes('409') || err.message.toLowerCase().includes('modificat')) {
        toast('Questo istituto è stato modificato altrove — ricaricato.', 'error')
      } else {
        toast(err.message, 'error')
      }
      qc.invalidateQueries({ queryKey: ['istituti'] })
    },
  })
}

export interface ChunkSearchResult {
  id: string
  label: string
  preview: string
}

export type ChunkCorpus = 'normattiva' | 'giurisprudenza' | 'dottrina' | 'studio'

export function useSearchChunks() {
  return useCallback(async (q: string, corpus?: ChunkCorpus): Promise<ChunkSearchResult[]> => {
    if (q.length < 2) return []
    try {
      const params: Record<string, string> = { q }
      if (corpus) params.corpus = corpus
      const { data } = await apiClient.get('/istituti/search-chunks', { params })
      return data.results
    } catch {
      return []
    }
  }, [])
}

export function useDeleteIstituto() {
  const qc = useQueryClient()
  const { toast } = useToast()

  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/istituti/${id}`)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['istituti'] })
      toast('Istituto eliminato.', 'success')
    },
    onError: (err: Error) => toast(err.message, 'error'),
  })
}
