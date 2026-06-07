import { createContext, useContext, useState, type ReactNode } from 'react'
import { DEFAULT_WORKSPACE } from '@/api/client'

interface WorkspaceContextValue {
  workspace: string
  setWorkspace: (ws: string) => void
}

const WorkspaceContext = createContext<WorkspaceContextValue>({
  workspace: DEFAULT_WORKSPACE,
  setWorkspace: () => {},
})

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [workspace, setWorkspaceState] = useState<string>(() => {
    return localStorage.getItem('aiura-workspace') ?? DEFAULT_WORKSPACE
  })

  const setWorkspace = (ws: string) => {
    setWorkspaceState(ws)
    localStorage.setItem('aiura-workspace', ws)
  }

  return (
    <WorkspaceContext.Provider value={{ workspace, setWorkspace }}>
      {children}
    </WorkspaceContext.Provider>
  )
}

export const useWorkspace = () => useContext(WorkspaceContext)
