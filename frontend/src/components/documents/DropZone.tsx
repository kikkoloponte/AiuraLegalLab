import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { IngestionProgress } from './IngestionProgress'
import { useIngestDocument } from '@/hooks/useDocuments'
import type { Folder } from '@/hooks/useFolders'

interface DropZoneProps {
  workspace: string
  folders: Folder[]
  activeFolderId: string | null
  compact?: boolean
}

interface UploadItem {
  file: File
  status: 'uploading' | 'done' | 'error'
  result?: {
    text_length?: number
    pii_stats?: Record<string, number>
    chunk_count?: number
  }
  error?: string
}

export function DropZone({ workspace, folders, activeFolderId, compact = false }: DropZoneProps) {
  const [uploads, setUploads] = useState<UploadItem[]>([])
  const [selectedFolder, setSelectedFolder] = useState<string>(activeFolderId ?? '')
  const ingest = useIngestDocument(workspace)

  const processFile = useCallback(async (file: File) => {
    const item: UploadItem = { file, status: 'uploading' }
    setUploads((prev) => [...prev, item])

    try {
      const result = await ingest.mutateAsync({
        file,
        folderId: selectedFolder || null,
      })
      setUploads((prev) =>
        prev.map((u) => u.file === file ? { ...u, status: 'done', result } : u)
      )
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Errore upload'
      setUploads((prev) =>
        prev.map((u) => u.file === file ? { ...u, status: 'error', error: msg } : u)
      )
    }
  }, [ingest, selectedFolder])

  const onDrop = useCallback((accepted: File[]) => {
    accepted.forEach(processFile)
  }, [processFile])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt'] },
    maxSize: 50 * 1024 * 1024,
  })

  const dismiss = (file: File) => setUploads((prev) => prev.filter((u) => u.file !== file))

  if (compact && uploads.length === 0) {
    return (
      <div
        {...getRootProps()}
        className="flex items-center gap-2 border border-dashed border-border rounded-lg px-4 py-2.5 cursor-pointer hover:border-primary hover:bg-primary/5 transition-colors mb-3"
      >
        <input {...getInputProps()} />
        <Upload className="w-4 h-4 text-muted-foreground" />
        <span className="text-sm text-muted-foreground">+ Carica altro documento</span>
      </div>
    )
  }

  return (
    <div className="space-y-3 mb-4">
      {/* Folder selector */}
      {folders.length > 0 && (
        <div className="flex items-center gap-2">
          <label className="text-xs text-muted-foreground flex-shrink-0">Cartella:</label>
          <select
            value={selectedFolder}
            onChange={(e) => setSelectedFolder(e.target.value)}
            className="text-xs bg-background border border-border rounded px-2 py-1 text-foreground outline-none flex-1 max-w-[200px]"
          >
            <option value="">Nessuna cartella</option>
            {folders.map((f) => (
              <option key={f.id} value={f.id}>{f.name}</option>
            ))}
          </select>
        </div>
      )}

      {/* Drop area */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors',
          isDragActive
            ? 'border-primary bg-primary/10'
            : 'border-border hover:border-primary hover:bg-primary/5'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-3" />
        <p className="text-sm font-medium text-foreground">
          {isDragActive ? 'Rilascia il file qui' : 'Trascina PDF / DOCX qui'}
        </p>
        <p className="text-xs text-muted-foreground mt-1">oppure clicca per sfogliare · max 50MB</p>
      </div>

      {/* Upload items */}
      {uploads.map((u, i) => (
        <div key={i} className="bg-card border border-border rounded-lg p-4 space-y-3">
          <div className="flex items-center gap-2">
            <span className="text-lg">📄</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-foreground truncate">{u.file.name}</p>
              <p className="text-xs text-muted-foreground">{(u.file.size / 1024).toFixed(0)} KB</p>
            </div>
            <span className={cn(
              'text-xs px-2 py-0.5 rounded-full',
              u.status === 'done' && 'bg-green-950 text-green-400',
              u.status === 'uploading' && 'bg-blue-950 text-blue-400',
              u.status === 'error' && 'bg-red-950 text-red-400',
            )}>
              {u.status === 'done' ? '✓ pronto' : u.status === 'uploading' ? '⏳ in corso' : '❌ errore'}
            </span>
            {u.status !== 'uploading' && (
              <button onClick={() => dismiss(u.file)} className="text-muted-foreground hover:text-foreground">
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {u.status === 'uploading' && (
            <IngestionProgress chunking />
          )}
          {u.status === 'done' && u.result && (
            <IngestionProgress
              textLength={u.result.text_length}
              piiStats={u.result.pii_stats}
              done
            />
          )}
          {u.status === 'error' && (
            <p className="text-xs text-red-400">❌ {u.error}</p>
          )}
        </div>
      ))}
    </div>
  )
}
