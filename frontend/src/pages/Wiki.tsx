import { useState, useMemo } from 'react'
import { BookOpen, Search, Loader2, FileDown, ExternalLink } from 'lucide-react'
import { useWikiList, useWikiPage } from '@/hooks/useWiki'
import { useWorkspace } from '@/context/WorkspaceContext'
import { WikiPageCard } from '@/components/wiki/WikiPageCard'
import { MarkdownViewer } from '@/components/wiki/MarkdownViewer'
import { useToast } from '@/context/ToastContext'
import { formatDate } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Materia extraction — very simple heuristic on slug prefix
// ---------------------------------------------------------------------------
function extractMateria(slug: string): string {
  const prefix = slug.split('_')[0]
  const MAP: Record<string, string> = {
    lavoro: 'Lavoro',
    contratto: 'Contratti',
    penale: 'Penale',
    fiscale: 'Fiscale',
    famiglia: 'Famiglia',
    societa: 'Società',
    immobiliare: 'Immobiliare',
    procedure: 'Procedure',
    privacy: 'Privacy',
    appalti: 'Appalti',
  }
  return MAP[prefix] ?? 'Generale'
}

export function Wiki() {
  const { workspace } = useWorkspace()
  const { toast } = useToast()

  const [search, setSearch] = useState('')
  const [activeSlug, setActiveSlug] = useState<string | null>(null)
  const [activeMaterial, setActiveMaterial] = useState<string | null>(null)

  const debouncedSearch = search.length >= 2 ? search : undefined
  const { data: pages = [], isLoading } = useWikiList(workspace, debouncedSearch)
  const { data: currentPage, isLoading: pageLoading } = useWikiPage(activeSlug, workspace)

  // Materia filter options derived from loaded pages
  const materie = useMemo(() => {
    const set = new Set(pages.map((p) => extractMateria(p.slug)))
    return ['Tutte', ...Array.from(set).sort()]
  }, [pages])

  const filteredPages = useMemo(() => {
    if (!activeMaterial || activeMaterial === 'Tutte') return pages
    return pages.filter((p) => extractMateria(p.slug) === activeMaterial)
  }, [pages, activeMaterial])

  // ---------------------------------------------------------------------------
  // Export PDF via window.print()
  // ---------------------------------------------------------------------------
  const handleExportPdf = () => {
    if (!currentPage) return
    const printWindow = window.open('', '_blank')
    if (!printWindow) {
      toast('Impossibile aprire la finestra di stampa', 'error')
      return
    }
    const html = `<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8"/>
  <title>${currentPage.title} — AiUra LegalLab Wiki</title>
  <style>
    body { font-family: Georgia, serif; max-width: 700px; margin: 40px auto; color: #111; line-height: 1.6; font-size: 14px; }
    h1 { font-size: 22px; border-bottom: 2px solid #333; padding-bottom: 6px; }
    h2 { font-size: 17px; margin-top: 24px; border-bottom: 1px solid #ccc; padding-bottom: 4px; }
    h3 { font-size: 15px; margin-top: 18px; }
    code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; font-family: monospace; font-size: 12px; }
    ul { padding-left: 20px; }
    .sources { margin-top: 24px; border-top: 1px solid #ccc; padding-top: 12px; font-size: 12px; color: #555; }
    .meta { font-size: 11px; color: #888; margin-bottom: 20px; }
    @media print { body { margin: 20px; } }
  </style>
</head>
<body>
  <h1>${currentPage.title}</h1>
  <div class="meta">Workspace: ${currentPage.workspace} · v${currentPage.version} · ${formatDate(currentPage.last_updated)} · ${currentPage.query_count} query</div>
  <pre style="white-space:pre-wrap;font-family:inherit">${currentPage.body_md}</pre>
  ${currentPage.sources.length > 0 ? `<div class="sources"><strong>Fonti:</strong> ${currentPage.sources.join(' · ')}</div>` : ''}
</body>
</html>`
    printWindow.document.write(html)
    printWindow.document.close()
    printWindow.onload = () => {
      printWindow.print()
      printWindow.onafterprint = () => {
        printWindow.close()
        window.focus()
      }
    }
    toast('PDF in preparazione...', 'success')
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------
  return (
    <div className="flex h-full overflow-hidden">
      {/* ── Left panel: index ─────────────────────────────────────────── */}
      <div className="w-[260px] flex-shrink-0 flex flex-col border-r border-border bg-card overflow-hidden">
        {/* Search */}
        <div className="px-3 py-3 border-b border-border">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
            <input
              type="text"
              placeholder="Cerca nella wiki..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-background border border-border rounded-md pl-8 pr-3 py-1.5 text-sm text-foreground placeholder:text-muted-foreground outline-none focus:border-primary"
            />
          </div>
        </div>

        {/* Materia filter chips */}
        {materie.length > 1 && (
          <div className="px-3 py-2 border-b border-border flex flex-wrap gap-1.5">
            {materie.map((m) => (
              <button
                key={m}
                onClick={() => setActiveMaterial(m === 'Tutte' ? null : m)}
                className={`text-xs px-2 py-0.5 rounded-full border transition-colors ${
                  (activeMaterial === null && m === 'Tutte') || activeMaterial === m
                    ? 'bg-primary text-primary-foreground border-primary'
                    : 'bg-muted text-muted-foreground border-border hover:border-primary'
                }`}
              >
                {m}
              </button>
            ))}
          </div>
        )}

        {/* Page list */}
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-0.5">
          {isLoading && (
            <div className="flex items-center justify-center py-8 text-muted-foreground gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-xs">Caricamento...</span>
            </div>
          )}

          {!isLoading && filteredPages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-10 text-center text-muted-foreground px-4">
              <BookOpen className="w-8 h-8 opacity-20 mb-2" />
              <p className="text-xs">
                {search.length >= 2
                  ? `Nessuna pagina trovata per "${search}"`
                  : 'La wiki si popola automaticamente durante le query legali.'}
              </p>
            </div>
          )}

          {filteredPages.map((page) => (
            <WikiPageCard
              key={page.slug}
              page={page}
              isActive={activeSlug === page.slug}
              onClick={() => setActiveSlug(page.slug)}
            />
          ))}
        </div>

        {/* Footer count */}
        <div className="px-3 py-2 border-t border-border">
          <p className="text-xs text-muted-foreground/60">
            {filteredPages.length} pagina{filteredPages.length !== 1 ? 'e' : ''} · workspace {workspace}
          </p>
        </div>
      </div>

      {/* ── Right panel: page viewer ───────────────────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {!activeSlug && (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-3">
            <BookOpen className="w-10 h-10 opacity-20" />
            <p className="text-sm font-medium">Seleziona una pagina</p>
            <p className="text-xs opacity-60 max-w-[300px] text-center">
              La wiki legale viene generata automaticamente dall'agente S3 durante le analisi.
              Ogni pagina è verificata dalla Citation Contract prima di essere salvata.
            </p>
          </div>
        )}

        {activeSlug && pageLoading && (
          <div className="flex items-center justify-center h-full text-muted-foreground gap-2">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span className="text-sm">Caricamento pagina...</span>
          </div>
        )}

        {activeSlug && !pageLoading && currentPage && (
          <>
            {/* Page header */}
            <div className="flex items-center justify-between px-6 py-3 border-b border-border bg-card flex-shrink-0">
              <div>
                <h2 className="text-sm font-semibold text-foreground">{currentPage.title}</h2>
                <p className="text-xs text-muted-foreground mt-0.5">
                  v{currentPage.version} · {formatDate(currentPage.last_updated)}
                  {currentPage.query_count > 0 && ` · ${currentPage.query_count} query`}
                </p>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={handleExportPdf}
                  className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-md bg-muted text-muted-foreground hover:bg-accent hover:text-foreground transition-colors border border-border"
                >
                  <FileDown className="w-3.5 h-3.5" />
                  Esporta PDF
                </button>
              </div>
            </div>

            {/* Page content */}
            <div className="flex-1 overflow-y-auto px-6 py-5" id="wiki-print-area">
              <MarkdownViewer content={currentPage.body_md} />

              {/* Sources */}
              {currentPage.sources.length > 0 && (
                <div className="mt-6 pt-4 border-t border-border">
                  <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Fonti citate</p>
                  <div className="flex flex-wrap gap-2">
                    {currentPage.sources.map((urn) => (
                      <span
                        key={urn}
                        className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded bg-blue-950 text-blue-300 border border-blue-800 font-mono"
                      >
                        <ExternalLink className="w-3 h-3" />
                        {urn}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}

        {activeSlug && !pageLoading && !currentPage && (
          <div className="flex flex-col items-center justify-center h-full text-muted-foreground gap-2">
            <p className="text-sm">Pagina non trovata</p>
            <button
              onClick={() => setActiveSlug(null)}
              className="text-xs text-primary hover:underline"
            >
              Torna all'indice
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
