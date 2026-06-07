import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

type Verdict = 'PASS' | 'FAIL' | 'WARN' | 'RE_RETRIEVAL'
type Confidence = 'HIGH' | 'MEDIUM' | 'LOW'

interface ReviewerBadgeProps {
  verdict: Verdict
  confidence?: Confidence
  sources?: number
  elapsedMs?: number
  className?: string
}

const VERDICT_CONFIG = {
  PASS: { variant: 'pass' as const, icon: CheckCircle, label: 'PASS' },
  FAIL: { variant: 'fail' as const, icon: XCircle, label: 'FAIL' },
  WARN: { variant: 'warn' as const, icon: AlertTriangle, label: 'WARN' },
  RE_RETRIEVAL: { variant: 'warn' as const, icon: AlertTriangle, label: 'RE-RETRIEVAL' },
}

export function ReviewerBadge({ verdict, confidence, sources, elapsedMs, className }: ReviewerBadgeProps) {
  const { variant, icon: Icon, label } = VERDICT_CONFIG[verdict] ?? VERDICT_CONFIG.WARN

  return (
    <div className={cn('flex items-center gap-2 flex-wrap', className)}>
      <Badge variant={variant} className="gap-1">
        <Icon className="w-3 h-3" />
        {label}
        {confidence && <span className="opacity-70">· {confidence}</span>}
      </Badge>
      <span className="text-xs text-muted-foreground">CitationReviewer S5</span>
      {sources != null && (
        <span className="text-xs text-muted-foreground">{sources} fonti verificate</span>
      )}
      {elapsedMs != null && (
        <span className="text-xs text-muted-foreground">{(elapsedMs / 1000).toFixed(0)}s</span>
      )}
    </div>
  )
}
