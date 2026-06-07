/**
 * Lightweight markdown renderer — no external deps.
 * Handles: # headings, **bold**, *italic*, - lists, [text](url),
 * `code`, horizontal rules, paragraphs.
 * Citation inline refs like [urn:nir:...] are highlighted.
 */
import { cn } from '@/lib/utils'

interface MarkdownViewerProps {
  content: string
  className?: string
}

function renderInline(text: string): React.ReactNode[] {
  // Split on **bold**, *italic*, `code`, [citation](url) or bare [urn...]
  const parts: React.ReactNode[] = []
  let rest = text
  // Counter is local to each call so React keys are stable within one render
  let i = 0

  const patterns = [
    { re: /\*\*(.+?)\*\*/, render: (m: string[]) => <strong key={i++}>{m[1]}</strong> },
    { re: /\*(.+?)\*/, render: (m: string[]) => <em key={i++}>{m[1]}</em> },
    { re: /`(.+?)`/, render: (m: string[]) => <code key={i++} className="bg-muted text-foreground px-1 py-0.5 rounded text-[0.8em] font-mono">{m[1]}</code> },
    {
      re: /\[([^\]]+)\]\(([^)]+)\)/,
      render: (m: string[]) => (
        <a key={i++} href={m[2]} target="_blank" rel="noopener noreferrer"
          className="text-primary underline underline-offset-2 hover:opacity-80">
          {m[1]}
        </a>
      ),
    },
    {
      re: /\[(urn:[^\]]+)\]/,
      render: (m: string[]) => (
        <span key={i++} className="inline-flex items-center px-1.5 py-0.5 rounded text-[0.75em] bg-blue-950 text-blue-300 border border-blue-800 mx-0.5 font-mono">
          {m[1]}
        </span>
      ),
    },
  ]

  while (rest.length > 0) {
    let earliest: { index: number; length: number; node: React.ReactNode } | null = null

    for (const p of patterns) {
      const match = rest.match(p.re)
      if (match && match.index !== undefined) {
        const node = p.render(match)
        if (!earliest || match.index < earliest.index) {
          earliest = { index: match.index, length: match[0].length, node }
        }
      }
    }

    if (!earliest) {
      parts.push(rest)
      break
    }

    if (earliest.index > 0) parts.push(rest.slice(0, earliest.index))
    parts.push(earliest.node)
    rest = rest.slice(earliest.index + earliest.length)
  }

  return parts
}

export function MarkdownViewer({ content, className }: MarkdownViewerProps) {
  const lines = content.split('\n')
  const nodes: React.ReactNode[] = []
  let listItems: string[] = []
  let key = 0

  const flushList = () => {
    if (listItems.length > 0) {
      nodes.push(
        <ul key={key++} className="list-disc list-inside space-y-0.5 my-2 text-sm text-foreground/90 pl-2">
          {listItems.map((item, j) => (
            <li key={j}>{renderInline(item)}</li>
          ))}
        </ul>
      )
      listItems = []
    }
  }

  for (let idx = 0; idx < lines.length; idx++) {
    const line = lines[idx]

    // Heading
    const h3 = line.match(/^### (.+)/)
    const h2 = line.match(/^## (.+)/)
    const h1 = line.match(/^# (.+)/)

    if (h1) {
      flushList()
      nodes.push(<h1 key={key++} className="text-lg font-bold text-foreground mt-5 mb-2">{renderInline(h1[1])}</h1>)
    } else if (h2) {
      flushList()
      nodes.push(<h2 key={key++} className="text-base font-semibold text-foreground mt-4 mb-1.5 border-b border-border pb-1">{renderInline(h2[1])}</h2>)
    } else if (h3) {
      flushList()
      nodes.push(<h3 key={key++} className="text-sm font-semibold text-foreground mt-3 mb-1">{renderInline(h3[1])}</h3>)
    } else if (/^---+$/.test(line.trim())) {
      flushList()
      nodes.push(<hr key={key++} className="border-border my-4" />)
    } else if (/^[-*]\s/.test(line)) {
      listItems.push(line.replace(/^[-*]\s/, ''))
    } else if (line.trim() === '') {
      flushList()
      // Empty line = paragraph break
    } else {
      flushList()
      nodes.push(
        <p key={key++} className="text-sm text-foreground/90 leading-relaxed my-1.5">
          {renderInline(line)}
        </p>
      )
    }
  }

  flushList()

  return <div className={cn('', className)}>{nodes}</div>
}
