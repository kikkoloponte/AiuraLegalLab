import { useState } from 'react'
import { FolderSidebar } from '@/components/documents/FolderSidebar'
import { DropZone } from '@/components/documents/DropZone'
import { DocumentCard } from '@/components/documents/DocumentCard'
import { useWorkspace } from '@/context/WorkspaceContext'
import { useDocuments } from '@/hooks/useDocuments'
import { useFolders } from '@/hooks/useFolders'
import { FolderOpen, Loader2 } from 'lucide-react'

export function Documents() {
  const { workspace } = useWorkspace()
  const [activeFolderId, setActiveFolderId] = useState<string | null>(null)
  const { data: docs = [], isLoading } = useDocuments(workspace, activeFolderId)
  const { data: folders = [] } = useFolders(workspace)

  const activeFolder = folders.find((f) => f.id === activeFolderId)
  const headerLabel = activeFolder ? `📁 ${activeFolder.name}` : 'Tutti i documenti'

  return (
    <div className="flex h-full overflow-hidden">
      {/* Folder sidebar */}
      <FolderSidebar
        workspace={workspace}
        activeFolderId={activeFolderId}
        onSelect={setActiveFolderId}
      />

      {/* Document list */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-card flex-shrink-0">
          <div>
            <h2 className="text-sm font-semibold text-foreground">{headerLabel}</h2>
            <p className="text-xs text-muted-foreground">{docs.length} documento{docs.length !== 1 ? 'i' : ''}</p>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-4">
          {/* Drop zone — compact when there are docs, full when empty */}
          <DropZone
            workspace={workspace}
            folders={folders}
            activeFolderId={activeFolderId}
            compact={docs.length > 0}
          />

          {/* Loading */}
          {isLoading && (
            <div className="flex items-center justify-center py-12 text-muted-foreground gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Caricamento documenti...</span>
            </div>
          )}

          {/* Empty state */}
          {!isLoading && docs.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
              <FolderOpen className="w-10 h-10 mb-3 opacity-20" />
              <p className="text-sm">
                {activeFolderId
                  ? 'Nessun documento in questa cartella'
                  : 'Nessun documento caricato — trascina un PDF o DOCX sopra'}
              </p>
            </div>
          )}

          {/* Document cards */}
          {!isLoading && docs.length > 0 && (
            <div className="space-y-3">
              {docs.map((doc) => (
                <DocumentCard
                  key={doc.id}
                  doc={doc}
                  workspace={workspace}
                  folders={folders}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
