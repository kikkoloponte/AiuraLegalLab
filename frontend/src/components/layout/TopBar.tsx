import { useLocation } from 'react-router-dom'

const LABELS: Record<string, string> = {
  '/': 'Dashboard',
  '/chat': 'Chat legale',
  '/documents': 'Documenti studio',
  '/wiki': 'Wiki legale',
  '/history': 'Cronologia',
}

export function TopBar() {
  const { pathname } = useLocation()
  const label = LABELS[pathname] ?? 'AiUra'

  const today = new Date().toLocaleDateString('it-IT', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })

  return (
    <header className="h-11 flex-shrink-0 flex items-center justify-between px-5 bg-card border-b border-border">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-xs text-muted-foreground/60 capitalize">{today}</span>
    </header>
  )
}
