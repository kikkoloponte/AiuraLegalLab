import { BookOpen, RefreshCw } from 'lucide-react'
import { cn, formatDate } from '@/lib/utils'
import type { WikiPage } from '@/hooks/useWiki'

interface WikiPageCardProps {
  page: WikiPage
  isActive: boolean
  onClick: () => void
}

export function WikiPageCard({ page, isActive, onClick }: WikiPageCardProps) {
  const preview = page.body_md.slice(0, 120).replace(/#+\s/g, '').replace(/\*\*/g, '')

  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full text-left px-3 py-2.5 rounded-lg transition-colors border',
        isActive
          ? 'bg-primary/10 border-primary/30 text-foreground'
          : 'bg-transparent border-transparent hover:bg-accent text-muted-foreground hover:text-foreground'
      )}
    >
      <div className="flex items-start gap-2">
        <BookOpen className="w-3.5 h-3.5 mt-0.5 flex-shrink-0 text-primary" />
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-foreground truncate">{page.title}</p>
          <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">{preview}</p>
          <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground/60">
            {page.last_updated && (
              <span className="flex items-center gap-0.5">
                <RefreshCw className="w-2.5 h-2.5" />
                {formatDate(page.last_updated)}
              </span>
            )}
            {page.sources.length > 0 && (
              <span>{page.sources.length} fonte{page.sources.length !== 1 ? 'i' : 'e'}</span>
            )}
          </div>
        </div>
      </div>
    </button>
  )
}
