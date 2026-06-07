import { useEffect } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { Toaster } from '@/components/ui/toaster'

export function AppShell() {
  const navigate = useNavigate()

  // Ctrl+K  →  navigate to /chat and focus the input
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        navigate('/chat')
        // Focus the textarea after navigation (small delay for render)
        setTimeout(() => {
          const el = document.querySelector<HTMLTextAreaElement>('textarea[data-chat-input]')
          el?.focus()
        }, 80)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [navigate])

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
      <Toaster />
    </div>
  )
}
