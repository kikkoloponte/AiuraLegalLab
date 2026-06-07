import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/api/client'

export interface WikiPage {
  slug: string
  title: string
  body_md: string
  sources: string[]
  query_count: number
  last_updated: string
  version: number
  workspace: string
}

interface WikiListResponse {
  pages: WikiPage[]
  total: number
}

export function useWikiList(workspace: string, q?: string) {
  return useQuery<WikiPage[]>({
    queryKey: ['wiki', workspace, q ?? ''],
    queryFn: async () => {
      const params: Record<string, string> = { workspace }
      if (q) params.q = q
      const { data } = await apiClient.get<WikiListResponse>('/wiki', { params })
      return data.pages
    },
    retry: false,
    placeholderData: [],
  })
}

export function useWikiPage(slug: string | null, workspace: string) {
  return useQuery<WikiPage>({
    queryKey: ['wiki', workspace, 'page', slug],
    queryFn: async () => {
      const { data } = await apiClient.get<WikiPage>(`/wiki/${slug}`, {
        params: { workspace },
      })
      return data
    },
    enabled: !!slug,
    retry: false,
  })
}

// Hook to fetch workspaces for the selector
export interface WorkspaceInfo {
  name: string
  doc_count: number
  chunk_count: number
  pending_jobs: number
  has_bm25_index: boolean
  has_vector_index: boolean
}

export function useWorkspaces() {
  return useQuery<WorkspaceInfo[]>({
    queryKey: ['workspaces'],
    queryFn: async () => {
      const { data } = await apiClient.get<{ workspaces: WorkspaceInfo[] }>('/workspace')
      return data.workspaces
    },
    retry: false,
    placeholderData: [],
    staleTime: 60_000,
  })
}
