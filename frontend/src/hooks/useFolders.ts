import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

export interface Folder {
  id: string
  name: string
  workspace: string
  doc_count: number
  created_at: string
}

export function useFolders(workspace: string) {
  return useQuery<Folder[]>({
    queryKey: ['folders', workspace],
    queryFn: async () => {
      const { data } = await apiClient.get('/folders', { params: { workspace } })
      return data.folders
    },
    retry: false,
    placeholderData: [],
  })
}

export function useCreateFolder(workspace: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (name: string) =>
      apiClient.post('/folders', { name, workspace }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['folders', workspace] }),
  })
}

export function useRenameFolder(workspace: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) =>
      apiClient.patch(`/folders/${id}`, { name }, { params: { workspace } }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['folders', workspace] }),
  })
}

export function useDeleteFolder(workspace: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) =>
      apiClient.delete(`/folders/${id}`, { params: { workspace } }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['folders', workspace] })
      qc.invalidateQueries({ queryKey: ['documents', workspace] })
    },
  })
}
