import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { MessageSquare, AlertTriangle, Trash2, FolderInput, FileText, FileType } from 'lucide-react'
import { cn } from '@/lib/utils'
import { formatDate } from '@/lib/utils'
import { useDeleteDocument, useMoveDocument, type Document } from '@/hooks/useDocuments'
import type { Folder } from '@/hooks/useFolders'

interface DocumentCardProps {
  doc: Document
  workspace: string
  folders: Folder[]
}

const STATUS_STYLES = {
  ready:      'bg-green-950 text-green-400 border-green-800',
  processing: 'bg-yellow-950 text-yellow-400 border-yellow-800',
  error:      'bg-red-950 text-red-400 border-red-800',
}
const STATUS_LABELS = { ready: '✓ pronto', processing: '⏳ in corso', error: '❌ errore' }

export function DocumentCard({ doc, workspace, folders }: DocumentCardProps) {
  const navigate = useNavigate()
  const deleteDoc = useDeleteDocument(workspace)
  const moveDoc = useMoveDocument(workspace)
  const [showMove, setShowMove] = useState(false)

  const isPdf = doc.filename.toLowerCase().endsWith('.pdf')
  const FileIcon = isPdf ? FileType : FileText

  const piiCount = Object.values(doc.pii_stats ?? {}).reduce((a, b) => a + b, 0)

  const handleAnalyze = () => {
    navigate('/chat', { state: { initialQuery: `Analizza il documento: ${doc.filename}`, docId: doc.id } })
  }

  const handleDelete = async () => {
    if (confirm(`Eliminare "${doc.filename}"?`)) {
      await deleteDoc.mutateAsync(doc.id)
    }
  }

  const handleMove = async (folderId: string | null) => {
    await moveDoc.mutateAsync({ id: doc.id, folderId })
    setShowMove(false)
  }

  return (
    <div className="bg-card border border-border rounded-lg p-4 hover:border-muted-foreground/30 transition-colors">
      {/* Header row */}
      <div className="flex items-start gap-3 mb-3">
        <FileIcon className="w-5 h-5 text-muted-foreground flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <p className="text-sm text-foreground font-medium truncate">{doc.filename}</p>
          <div className="flex items-center gap-2 flex-wrap mt-1">
            {doc.folder_name && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
                📁 {doc.folder_name}
              </span>
            )}
            <span className={cn('text-xs px-1.5 py-0.5 rounded border', STATUS_STYLES[doc.status])}>
              {STATUS_LABELS[doc.status]}
            </span>
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-3 text-xs text-muted-foreground mb-3 flex-wrap">
        {doc.text_length > 0 && <span>{doc.text_length.toLocaleString('it-IT')} chars</span>}
        {piiCount > 0 && <span>· {piiCount} PII anonimizzate</span>}
        {doc.created_at && <span>· {formatDate(doc.created_at)}</span>}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-1.5 flex-wrap">
        <button
          onClick={handleAnalyze}
          className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-primary/10 text-primary hover:bg-primary/20 transition-colors border border-primary/20"
        >
          <MessageSquare className="w-3 h-3" /> Analizza
        </button>
        <button className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-muted text-muted-foreground hover:bg-accent hover:text-foreground transition-colors">
          <AlertTriangle className="w-3 h-3" /> Rischio
        </button>
        <div className="relative">
          <button
            onClick={() => setShowMove(!showMove)}
            className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-muted text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          >
            <FolderInput className="w-3 h-3" /> Sposta
          </button>
          {showMove && (
            <div className="absolute bottom-full left-0 mb-1 z-50 bg-card border border-border rounded-lg shadow-lg py-1 min-w-[160px]">
              <button
                onClick={() => handleMove(null)}
                className="w-full text-left px-3 py-1.5 text-xs text-muted-foreground hover:bg-accent"
              >
                Nessuna cartella
              </button>
              {folders.map((f) => (
                <button
                  key={f.id}
                  onClick={() => handleMove(f.id)}
                  className={cn(
                    'w-full text-left px-3 py-1.5 text-xs hover:bg-accent',
                    doc.folder_id === f.id ? 'text-primary font-medium' : 'text-foreground'
                  )}
                >
                  📁 {f.name}
                </button>
              ))}
            </div>
          )}
        </div>
        <button
          onClick={handleDelete}
          className="flex items-center gap-1 text-xs px-2.5 py-1 rounded-md bg-muted text-muted-foreground hover:bg-red-950/40 hover:text-red-400 transition-colors ml-auto"
        >
          <Trash2 className="w-3 h-3" />
        </button>
      </div>

      {doc.error && (
        <p className="text-xs text-red-400 mt-2">❌ {doc.error}</p>
      )}
    </div>
  )
}
