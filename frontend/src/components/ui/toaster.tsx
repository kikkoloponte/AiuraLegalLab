import { CheckCircle, XCircle, Info, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useToast } from '@/context/ToastContext'

const ICONS = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
}

const STYLES = {
  success: 'border-green-700 bg-green-950/90 text-green-300',
  error: 'border-red-700 bg-red-950/90 text-red-300',
  info: 'border-border bg-card text-foreground',
}

export function Toaster() {
  const { toasts, dismiss } = useToast()

  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-5 right-5 z-[100] flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => {
        const Icon = ICONS[t.type]
        return (
          <div
            key={t.id}
            className={cn(
              'flex items-center gap-2.5 px-4 py-3 rounded-lg border shadow-lg',
              'min-w-[240px] max-w-[360px] pointer-events-auto',
              'animate-in slide-in-from-right-full duration-200',
              STYLES[t.type]
            )}
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            <p className="text-sm flex-1">{t.message}</p>
            <button
              onClick={() => dismiss(t.id)}
              className="text-current opacity-50 hover:opacity-100 transition-opacity"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
