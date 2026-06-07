import { useState } from 'react'
import { FolderOpen, Folder, Plus, Pencil, Trash2, MoreHorizontal } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useFolders, useCreateFolder, useRenameFolder, useDeleteFolder } from '@/hooks/useFolders'
import { useDocuments } from '@/hooks/useDocuments'

interface FolderSidebarProps {
  workspace: string
  activeFolderId: string | null       // null = Tutti
  onSelect: (id: string | null) => void
}

export function FolderSidebar({ workspace, activeFolderId, onSelect }: FolderSidebarProps) {
  const { data: folders = [] } = useFolders(workspace)
  const { data: allDocs = [] } = useDocuments(workspace)
  const createFolder = useCreateFolder(workspace)
  const renameFolder = useRenameFolder(workspace)
  const deleteFolder = useDeleteFolder(workspace)

  const [creating, setCreating] = useState(false)
  const [newName, setNewName] = useState('')
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editName, setEditName] = useState('')
  const [menuId, setMenuId] = useState<string | null>(null)

  const handleCreate = async () => {
    if (!newName.trim()) return
    await createFolder.mutateAsync(newName.trim())
    setNewName('')
    setCreating(false)
  }

  const handleRename = async (id: string) => {
    if (!editName.trim()) return
    await renameFolder.mutateAsync({ id, name: editName.trim() })
    setEditingId(null)
  }

  const handleDelete = async (id: string) => {
    await deleteFolder.mutateAsync(id)
    if (activeFolderId === id) onSelect(null)
    setMenuId(null)
  }

  return (
    <div className="w-[180px] flex-shrink-0 flex flex-col border-r border-border bg-card h-full">
      {/* Header */}
      <div className="px-3 pt-4 pb-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Cartelle</p>
      </div>

      {/* "Tutti" item */}
      <button
        onClick={() => onSelect(null)}
        className={cn(
          'flex items-center gap-2 px-3 py-2 text-sm w-full text-left transition-colors',
          activeFolderId === null
            ? 'bg-primary text-primary-foreground font-medium'
            : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
        )}
      >
        <FolderOpen className="w-3.5 h-3.5 flex-shrink-0" />
        <span className="flex-1 truncate">Tutti</span>
        <span className="text-xs opacity-60">{allDocs.length}</span>
      </button>

      {/* Folder list */}
      <div className="flex-1 overflow-y-auto py-1">
        {folders.map((folder) => (
          <div key={folder.id} className="relative group">
            {editingId === folder.id ? (
              <div className="px-2 py-1">
                <input
                  autoFocus
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleRename(folder.id)
                    if (e.key === 'Escape') setEditingId(null)
                  }}
                  onBlur={() => handleRename(folder.id)}
                  className="w-full bg-background border border-primary rounded px-2 py-0.5 text-xs text-foreground outline-none"
                />
              </div>
            ) : (
              <button
                onClick={() => onSelect(folder.id)}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 text-sm w-full text-left transition-colors',
                  activeFolderId === folder.id
                    ? 'bg-primary text-primary-foreground font-medium'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )}
              >
                <Folder className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="flex-1 truncate">{folder.name}</span>
                <span className="text-xs opacity-60">{folder.doc_count}</span>
              </button>
            )}

            {/* Context menu trigger */}
            {editingId !== folder.id && (
              <button
                onClick={(e) => { e.stopPropagation(); setMenuId(menuId === folder.id ? null : folder.id) }}
                className="absolute right-1 top-1/2 -translate-y-1/2 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-muted transition-opacity"
              >
                <MoreHorizontal className="w-3 h-3 text-muted-foreground" />
              </button>
            )}

            {/* Dropdown menu */}
            {menuId === folder.id && (
              <div className="absolute right-0 top-8 z-50 bg-card border border-border rounded-md shadow-lg py-1 min-w-[120px]">
                <button
                  onClick={() => { setEditingId(folder.id); setEditName(folder.name); setMenuId(null) }}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs text-foreground hover:bg-accent w-full text-left"
                >
                  <Pencil className="w-3 h-3" /> Rinomina
                </button>
                <button
                  onClick={() => handleDelete(folder.id)}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs text-red-400 hover:bg-red-950/30 w-full text-left"
                >
                  <Trash2 className="w-3 h-3" /> Elimina
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* New folder */}
      <div className="border-t border-border p-2">
        {creating ? (
          <div className="flex gap-1">
            <input
              autoFocus
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleCreate()
                if (e.key === 'Escape') setCreating(false)
              }}
              onBlur={() => { if (!newName.trim()) setCreating(false) }}
              placeholder="Nome cartella"
              className="flex-1 bg-background border border-primary rounded px-2 py-1 text-xs text-foreground outline-none"
            />
            <button onClick={handleCreate} className="text-xs text-primary hover:text-primary/80 px-1">✓</button>
          </div>
        ) : (
          <button
            onClick={() => setCreating(true)}
            className="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 transition-colors w-full"
          >
            <Plus className="w-3.5 h-3.5" /> Nuova cartella
          </button>
        )}
      </div>
    </div>
  )
}
