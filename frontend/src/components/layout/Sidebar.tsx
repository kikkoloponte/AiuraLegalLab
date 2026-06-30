import { useState, useRef, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import { Home, MessageSquare, FolderOpen, BookOpen, History, Scale, Moon, Sun, ChevronDown, Check, Network, Settings, ClipboardCheck, Library } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useTheme } from '@/context/ThemeContext'
import { useWorkspace } from '@/context/WorkspaceContext'
import { useWorkspaces } from '@/hooks/useWiki'
import { Button } from '@/components/ui/button'

const NAV_ITEMS = [
  { to: '/',          icon: Home,          label: 'Dashboard' },
  { to: '/chat',      icon: MessageSquare, label: 'Chat legale' },
  { to: '/documents', icon: FolderOpen,    label: 'Documenti' },
  { to: '/wiki',      icon: BookOpen,      label: 'Wiki legale' },
  { to: '/graph',     icon: Network,       label: 'Grafo legale' },
  { to: '/questioni', icon: ClipboardCheck, label: 'Questioni da approvare' },
  { to: '/istituti',  icon: Library,       label: 'Istituti Giuridici' },
]

export function Sidebar() {
  const { theme, toggle } = useTheme()
  const { workspace, setWorkspace } = useWorkspace()
  const { data: workspaces = [] } = useWorkspaces()
  const [wsOpen, setWsOpen] = useState(false)
  const wsRef = useRef<HTMLDivElement>(null)

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (wsRef.current && !wsRef.current.contains(e.target as Node)) {
        setWsOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSelect = (name: string) => {
    setWorkspace(name)
    setWsOpen(false)
  }

  return (
    <aside className="w-[200px] flex-shrink-0 flex flex-col bg-card border-r border-border h-screen">
      {/* Logo + workspace selector */}
      <div className="px-4 py-4 border-b border-border space-y-2">
        <div className="flex items-center gap-2 text-foreground font-bold text-sm">
          <Scale className="w-4 h-4 text-primary" />
          AiUra LegalLab
        </div>

        {/* Workspace dropdown */}
        <div className="relative" ref={wsRef}>
          <button
            onClick={() => setWsOpen((o) => !o)}
            className="w-full bg-muted rounded px-2 py-1 text-xs text-muted-foreground flex items-center justify-between hover:bg-accent hover:text-foreground transition-colors"
          >
            <span className="truncate">{workspace}</span>
            <ChevronDown className={cn('w-3 h-3 ml-1 flex-shrink-0 transition-transform', wsOpen && 'rotate-180')} />
          </button>

          {wsOpen && (
            <div className="absolute top-full left-0 right-0 mt-1 z-50 bg-card border border-border rounded-lg shadow-lg py-1 max-h-48 overflow-y-auto">
              {workspaces.length === 0 && (
                <div className="px-3 py-2 text-xs text-muted-foreground">
                  Nessun workspace trovato
                </div>
              )}
              {workspaces.map((ws) => (
                <button
                  key={ws.name}
                  onClick={() => handleSelect(ws.name)}
                  className={cn(
                    'w-full text-left px-3 py-1.5 text-xs flex items-center justify-between hover:bg-accent transition-colors',
                    ws.name === workspace ? 'text-primary font-medium' : 'text-foreground'
                  )}
                >
                  <span className="truncate">{ws.name}</span>
                  {ws.name === workspace && <Check className="w-3 h-3 flex-shrink-0" />}
                </button>
              ))}
              {/* Always show current if not in list */}
              {workspaces.length > 0 && !workspaces.find((w) => w.name === workspace) && (
                <button
                  onClick={() => handleSelect(workspace)}
                  className="w-full text-left px-3 py-1.5 text-xs text-primary font-medium flex items-center justify-between"
                >
                  <span className="truncate">{workspace}</span>
                  <Check className="w-3 h-3 flex-shrink-0" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground font-medium'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              )
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}

        <div className="pt-2">
          <div className="h-px bg-border mx-1 mb-2" />
          {[
            { to: '/history',  icon: History,  label: 'Cronologia' },
            { to: '/settings', icon: Settings, label: 'Impostazioni' },
          ].map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground font-medium'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )
              }
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Footer: version + theme toggle */}
      <div className="px-3 py-3 border-t border-border flex items-center justify-between">
        <span className="text-xs text-muted-foreground/50">v0.1-mvp</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggle}
          className="h-7 px-2 text-xs text-muted-foreground gap-1"
        >
          {theme === 'dark' ? <Moon className="w-3.5 h-3.5" /> : <Sun className="w-3.5 h-3.5" />}
          {theme === 'dark' ? 'Dark' : 'Light'}
        </Button>
      </div>
    </aside>
  )
}
