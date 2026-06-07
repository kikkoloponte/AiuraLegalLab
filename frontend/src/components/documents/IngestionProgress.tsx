import { CheckCircle, Circle, Loader2 } from 'lucide-react'

interface IngestionStep {
  label: string
  done: boolean
  active: boolean
  detail?: string
}

interface IngestionProgressProps {
  textLength?: number
  piiStats?: Record<string, number>
  chunking?: boolean
  annotating?: boolean
  done?: boolean
}

export function IngestionProgress({ textLength, piiStats, chunking = false, annotating = false, done = false }: IngestionProgressProps) {
  const piiCount = piiStats ? Object.values(piiStats).reduce((a, b) => a + b, 0) : 0
  const piiDetail = piiStats
    ? Object.entries(piiStats)
        .filter(([, v]) => v > 0)
        .map(([k, v]) => `${v} ${k}`)
        .join(', ')
    : ''

  const steps: IngestionStep[] = [
    {
      label: 'Testo estratto',
      done: !!textLength,
      active: !textLength,
      detail: textLength ? `${textLength.toLocaleString('it-IT')} caratteri` : undefined,
    },
    {
      label: 'PII anonimizzate',
      done: !!textLength && piiCount >= 0,
      active: !!textLength && piiCount === 0 && !chunking,
      detail: piiDetail || (piiCount === 0 ? 'nessuna rilevata' : undefined),
    },
    {
      label: 'Chunking e indicizzazione',
      done: done,
      active: chunking,
      detail: undefined,
    },
    {
      label: 'Analisi rischio S6',
      done: false,
      active: annotating,
      detail: undefined,
    },
  ]

  const progress = steps.filter((s) => s.done).length
  const total = steps.length
  const pct = Math.round((progress / total) * 100)

  return (
    <div className="space-y-2">
      {/* Progress bar */}
      <div className="h-1.5 bg-muted rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Steps */}
      <div className="space-y-1">
        {steps.map((step, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            {step.done ? (
              <CheckCircle className="w-3.5 h-3.5 text-green-500 flex-shrink-0" />
            ) : step.active ? (
              <Loader2 className="w-3.5 h-3.5 text-primary animate-spin flex-shrink-0" />
            ) : (
              <Circle className="w-3.5 h-3.5 text-muted-foreground/30 flex-shrink-0" />
            )}
            <span className={step.done ? 'text-foreground' : step.active ? 'text-primary' : 'text-muted-foreground/50'}>
              {step.label}
              {step.detail && <span className="ml-1 text-muted-foreground">({step.detail})</span>}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
