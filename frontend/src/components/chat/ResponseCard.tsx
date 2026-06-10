import { useState, useMemo } from 'react'
import { ChevronDown, ChevronRight, FileText, Download, BookOpen, Scale } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ReviewerBadge } from './ReviewerBadge'
import { SourceChip } from './SourceChip'
import { FeedbackSection } from './FeedbackSection'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useToast } from '@/context/ToastContext'

export interface Source {
  source_id: string
  doc_id: string
  label: string
  type: 'normativa' | 'giurisprudenza' | 'studio'
  url?: string
  snippet: string
  metadata: Record<string, string>
}

export interface AnalysisSection {
  step: string
  content: string
  citations: Array<{
    source_id: string
    claim?: string
    claim_type?: string
    source_authority?: string
  }>
}

export interface LegalResponse {
  summary: string
  full_analysis?: string
  analysis_sections?: AnalysisSection[]
  verdict: 'PASS' | 'FAIL' | 'WARN' | 'RE_RETRIEVAL'
  confidence: 'HIGH' | 'MEDIUM' | 'LOW'
  sources: Source[]
  elapsed_ms?: number
  gaps?: string[]
  history_id?: string
}

// ---------------------------------------------------------------------------
// Step name → etichetta italiana
// ---------------------------------------------------------------------------

const STEP_LABELS: Record<string, string> = {
  RICOSTRUZIONE_FATTO: 'Ricostruzione del fatto',
  QUALIFICAZIONE: 'Qualificazione giuridica',
  QUESTIONE: 'Questione giuridica',
  FONTI_NORMATIVE: 'Fonti normative',
  INTERPRETAZIONE: 'Interpretazione',
  GIURISPRUDENZA: 'Orientamenti giurisprudenziali',
  SUSSUNZIONE: 'Sussunzione',
  OBIEZIONI: 'Obiezioni e tesi contrarie',
  CONCLUSIONE: 'Conclusione',
  ANALISI: 'Analisi',
}

function stepLabel(step: string) {
  return STEP_LABELS[step.toUpperCase()] ?? step
}

// Colore accent per step
function stepColor(step: string) {
  const s = step.toUpperCase()
  if (['RICOSTRUZIONE_FATTO', 'QUALIFICAZIONE', 'QUESTIONE'].includes(s))
    return 'text-sky-400 border-sky-800'
  if (['FONTI_NORMATIVE', 'INTERPRETAZIONE'].includes(s))
    return 'text-violet-400 border-violet-800'
  if (s === 'GIURISPRUDENZA')
    return 'text-amber-400 border-amber-800'
  if (['SUSSUNZIONE', 'OBIEZIONI'].includes(s))
    return 'text-orange-400 border-orange-800'
  if (s === 'CONCLUSIONE')
    return 'text-emerald-400 border-emerald-800'
  return 'text-primary border-border'
}

// ---------------------------------------------------------------------------
// StepAccordion — singolo step espandibile
// ---------------------------------------------------------------------------

function StepAccordion({
  section,
  sources = [],
  defaultOpen = false,
}: {
  section: AnalysisSection
  sources?: Source[]
  defaultOpen?: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  const label = stepLabel(section.step)
  const color = stepColor(section.step)

  // Lookup veloce source_id → Source per citazioni cliccabili
  const sourceMap = useMemo(() => {
    const m: Record<string, Source> = {}
    sources.forEach((s) => { m[s.source_id] = s })
    return m
  }, [sources])

  return (
    <div className={cn('border-l-2 ml-1', color.split(' ')[1])}>
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center gap-2 px-3 py-2 hover:bg-muted/40 transition-colors text-left"
      >
        {open
          ? <ChevronDown className="w-3.5 h-3.5 flex-shrink-0 text-muted-foreground" />
          : <ChevronRight className="w-3.5 h-3.5 flex-shrink-0 text-muted-foreground" />
        }
        <span className={cn('text-xs font-semibold uppercase tracking-wide', color.split(' ')[0])}>
          {label}
        </span>
      </button>

      {open && (
        <div className="px-4 pb-3 space-y-2">
          <div className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{section.content}</ReactMarkdown>
          </div>
          {section.citations.length > 0 && (
            <div className="mt-2 space-y-1.5">
              {section.citations.map((c, i) => {
                const src = sourceMap[c.source_id]
                if (src) {
                  return (
                    <div key={i} className="flex flex-col gap-0.5">
                      <SourceChip
                        sourceId={src.source_id}
                        docId={src.doc_id}
                        label={src.label}
                        type={src.type}
                        url={src.url}
                        snippet={src.snippet}
                        metadata={src.metadata}
                      />
                      {c.claim && (
                        <span className="text-xs text-muted-foreground/70 italic pl-1">
                          "{c.claim.slice(0, 100)}{c.claim.length > 100 ? '…' : ''}"
                        </span>
                      )}
                    </div>
                  )
                }
                // fallback: source_id non nel Packet (citazione non verificata)
                return (
                  <div key={i} className="text-xs text-muted-foreground bg-muted/30 rounded px-2 py-1 flex flex-wrap gap-x-2">
                    <span className="font-mono text-primary/80">{c.source_id}</span>
                    {c.claim && <span className="italic opacity-75">"{c.claim.slice(0, 80)}{c.claim.length > 80 ? '…' : ''}"</span>}
                  </div>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// PhaseBlock — blocco di sezioni per una fase (standard o deep)
// ---------------------------------------------------------------------------

function PhaseBlock({
  title,
  icon,
  sections,
  sources = [],
  defaultOpen = false,
  badge,
}: {
  title: string
  icon: React.ReactNode
  sections: AnalysisSection[]
  sources?: Source[]
  defaultOpen?: boolean
  badge?: React.ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen)

  if (sections.length === 0) return null

  return (
    <div className="border-b border-border">
      <button
        onClick={() => setOpen((v) => !v)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-muted/50 hover:bg-muted transition-colors text-left"
      >
        <span className="text-xs font-semibold text-primary uppercase tracking-wide flex items-center gap-1.5">
          {open ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
          {icon}
          {title}
        </span>
        <div className="flex items-center gap-2">
          {badge}
          <span className="text-xs text-muted-foreground">{open ? 'comprimi' : 'espandi'}</span>
        </div>
      </button>

      {open && (
        <div className="px-2 py-2 space-y-0.5">
          {sections.map((s, i) => (
            <StepAccordion
              key={s.step + i}
              section={s}
              sources={sources}
              defaultOpen={s.step === 'CONCLUSIONE'}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ---------------------------------------------------------------------------
// ResponseCard
// ---------------------------------------------------------------------------

interface ResponseCardProps {
  response: LegalResponse
  className?: string
  onGraphOpen?: (nodeId: string) => void
}

export function ResponseCard({ response, className, onGraphOpen }: ResponseCardProps) {
  const navigate = useNavigate()
  const { toast } = useToast()

  const hasSections = (response.analysis_sections?.length ?? 0) > 0

  const handleExportPdf = () => {
    const printWindow = window.open('', '_blank')
    if (!printWindow) { toast('Impossibile aprire la finestra di stampa', 'error'); return }
    const esc = (s: string) =>
      s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

    const sectionsHtml = (response.analysis_sections ?? [])
      .map((s) => `<h3>${esc(stepLabel(s.step))}</h3><p>${esc(s.content)}</p>`)
      .join('')

    const sourcesHtml = response.sources.length > 0
      ? `<div style="margin-top:24px;border-top:1px solid #ccc;padding-top:12px;font-size:12px;color:#555">
           <strong>Fonti:</strong> ${response.sources.map((s) => esc(s.label)).join(' · ')}
         </div>`
      : ''

    const html = `<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="utf-8"/>
  <title>Analisi legale AiUra</title>
  <style>
    body { font-family: Georgia, serif; max-width: 700px; margin: 40px auto; color: #111; line-height: 1.6; font-size: 14px; }
    h1 { font-size: 20px; margin-bottom: 4px; }
    h3 { font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: #555; margin-top: 20px; margin-bottom: 4px; }
    .verdict { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; background: #eee; }
    @media print { body { margin: 20px; } }
  </style>
</head>
<body>
  <h1>Analisi legale AiUra LegalLab</h1>
  <div class="verdict">S5 Reviewer: ${esc(response.verdict)} · ${esc(response.confidence)}</div>
  <h2 style="font-size:15px;margin-top:20px">Sintesi</h2>
  <p>${esc(response.summary)}</p>
  ${sectionsHtml}
  ${sourcesHtml}
</body>
</html>`
    printWindow.document.write(html)
    printWindow.document.close()
    // Aspetta il caricamento completo prima di aprire il dialog di stampa.
    // onafterprint restituisce il focus alla finestra principale così la UI
    // non rimane "congelata" dopo la chiusura del dialog.
    printWindow.onload = () => {
      printWindow.print()
      printWindow.onafterprint = () => {
        printWindow.close()
        window.focus()
      }
    }
    toast('PDF in preparazione...', 'success')
  }

  return (
    <div className={cn('rounded-lg border border-border bg-card overflow-hidden', className)}>
      {/* Reviewer badge */}
      <div className="px-4 py-3 border-b border-border">
        <ReviewerBadge
          verdict={response.verdict}
          confidence={response.confidence}
          sources={response.sources.length}
          elapsedMs={response.elapsed_ms}
        />
      </div>

      {/* Summary */}
      <div className="px-4 py-3 border-b border-border">
        <p className="text-xs font-semibold uppercase tracking-wide text-primary mb-2">Sintesi</p>
        <p className="text-sm text-foreground leading-relaxed">{response.summary}</p>
      </div>

      {/* Analisi strutturata IQRAC */}
      {hasSections && (
        <PhaseBlock
          title="Analisi IQRAC"
          icon={<Scale className="w-3.5 h-3.5" />}
          sections={response.analysis_sections ?? []}
          sources={response.sources}
          defaultOpen={true}
        />
      )}

      {/* Fallback testo libero (parse failed) */}
      {!hasSections && response.full_analysis && (
        <div className="border-b border-border px-4 py-3 prose prose-sm dark:prose-invert max-w-none text-sm">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{response.full_analysis}</ReactMarkdown>
        </div>
      )}

      {/* Gaps */}
      {response.gaps && response.gaps.length > 0 && (
        <div className="px-4 py-3 border-b border-border bg-yellow-950/30">
          <p className="text-xs font-semibold uppercase tracking-wide text-yellow-400 mb-2">Gap analisi</p>
          <ul className="text-xs text-yellow-300/80 space-y-0.5 list-disc list-inside">
            {response.gaps.map((g, i) => <li key={i}>{g}</li>)}
          </ul>
        </div>
      )}

      {/* Sources */}
      {response.sources.length > 0 && (
        <div className="px-4 py-3 border-b border-border">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground mb-2">
            Fonti verificate
          </p>
          <div className="flex flex-wrap gap-2">
            {response.sources.map((s) => (
              <SourceChip
                key={`${s.source_id}-${s.doc_id}`}
                sourceId={s.source_id}
                docId={s.doc_id}
                label={s.label}
                type={s.type}
                url={s.url}
                snippet={s.snippet}
                metadata={s.metadata}
                onGraphOpen={onGraphOpen}
              />
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-4 py-2.5 bg-muted/30 flex items-center gap-2">
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1.5 text-muted-foreground">
          <FileText className="w-3.5 h-3.5" />
          Genera atto
        </Button>
        <Button variant="ghost" size="sm" className="h-7 text-xs gap-1.5 text-muted-foreground" onClick={handleExportPdf}>
          <Download className="w-3.5 h-3.5" />
          Esporta PDF
        </Button>
        <Button
          variant="ghost"
          size="sm"
          className="h-7 text-xs gap-1.5 text-muted-foreground"
          onClick={() => navigate('/wiki')}
        >
          <BookOpen className="w-3.5 h-3.5" />
          Wiki →
        </Button>
      </div>

      {/* Feedback */}
      <div className="border-t border-border">
        <FeedbackSection historyId={response.history_id} />
      </div>
    </div>
  )
}
