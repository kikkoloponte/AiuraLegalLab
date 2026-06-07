import { Loader2, Search, Brain, ShieldCheck } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AgentStatusBarProps {
  status: string
  className?: string
}

const AGENT_STEPS = [
  { key: 'S2', label: 'Researcher', icon: Search,      match: 'S2' },
  { key: 'S3', label: 'Analyst',    icon: Brain,       match: 'S3' },
  { key: 'S5', label: 'Reviewer',   icon: ShieldCheck, match: 'S5' },
]

function currentStep(status: string): string {
  for (const s of AGENT_STEPS) {
    if (status.includes(s.match)) return s.key
  }
  return 'S2'
}

export function AgentStatusBar({ status, className }: AgentStatusBarProps) {
  const active = currentStep(status)
  const activeIdx = AGENT_STEPS.findIndex((s) => s.key === active)

  return (
    <div className={cn('flex items-center gap-3 py-2 px-1', className)}>
      {AGENT_STEPS.map((step, i) => {
        const Icon = step.icon
        const isActive = step.key === active
        const isDone = i < activeIdx

        return (
          <div key={step.key} className="flex items-center gap-1.5">
            <div className={cn(
              'flex items-center gap-1 text-xs px-2 py-1 rounded-full transition-colors',
              isActive && 'bg-primary/20 text-primary',
              isDone && 'text-green-500',
              !isActive && !isDone && 'text-muted-foreground/40',
            )}>
              {isActive ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Icon className="w-3 h-3" />
              )}
              <span>{step.key} {step.label}</span>
            </div>
            {i < AGENT_STEPS.length - 1 && (
              <span className={cn(
                'text-xs',
                i < activeIdx ? 'text-green-500' : 'text-muted-foreground/20'
              )}>→</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
