import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

export interface Document {
  id: string
  filename: string
  workspace: string
  folder_id?: string
  folder_name?: string
  status: 'ready' | 'processing' | 'error'
  text_length: number
  chunk_count: number
  pii_stats: Record<string, number>
  created_at: string
  error?: string
}

export function useDocuments(workspace: string, folderId?: string | null) {
  return useQuery<Document[]>({
    queryKey: ['documents', workspace, folderId],
    queryFn: async () => {
      const params: Record<string, string> = { workspace }
      if (folderId) params.folder_id = folderId
      const { data } = await apiClient.get('/documents', { params })
      return data.documents
    },
    retry: false,
    placeholderData: [],
  })
}

export function useDeleteDocument(workspace: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) =>
      apiClient.delete(`/documents/${id}`, { params: { workspace } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['documents', workspace] }),
  })
}

export function useMoveDocument(workspace: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, folderId }: { id: string; folderId: string | null }) =>
      apiClient.post(`/documents/${id}/folder`, { folder_id: folderId }, { params: { workspace } }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents', workspace] })
      qc.invalidateQueries({ queryKey: ['folders', workspace] })
    },
  })
}

export function useIngestDocument(workspace: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ file, folderId }: { file: File; folderId?: string | null }) => {
      const form = new FormData()
      form.append('file', file)
      form.append('workspace', workspace)
      const { data } = await apiClient.post('/ingest', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      // Se è stata scelta una cartella, sposta subito il documento
      if (folderId && data.document_id) {
        await apiClient.post(
          `/documents/${data.document_id}/folder`,
          { folder_id: folderId },
          { params: { workspace } }
        )
      }
      return data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['documents', workspace] })
      qc.invalidateQueries({ queryKey: ['folders', workspace] })
    },
  })
}
