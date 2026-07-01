import { useMemo, useState } from 'react'
import { ChevronRight, ChevronDown, Folder, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { IstitutoGiuridico } from '@/hooks/useIstitutiGiuridici'

interface IstitutiTreeProps {
  items: IstitutoGiuridico[]
  selectedId?: string
  onSelect: (istituto: IstitutoGiuridico) => void
}

const MACRO_AREE = [
  { label: 'Civile', codici: ['CC', 'CPC'] },
  { label: 'Penale', codici: ['CP', 'CPP'] },
] as const

const NON_CATEGORIZZATO = 'Non categorizzato'

/**
 * Albero a due livelli: macro-area (Civile/Penale, raggruppa CC+CPC e
 * CP+CPP) -> raggruppamento (campo libero sull'istituto, es. "Persone e
 * Famiglia") -> istituto. Stato di espansione locale, nessuna persistenza.
 */
export function IstitutiTree({ items, selectedId, onSelect }: IstitutiTreeProps) {
  const [openMacro, setOpenMacro] = useState<Set<string>>(new Set())
  const [openGroup, setOpenGroup] = useState<Set<string>>(new Set())

  const byMacro = useMemo(() => {
    return MACRO_AREE.map((macro) => {
      const macroItems = items.filter((it) => (macro.codici as readonly string[]).includes(it.codice_riferimento))
      const groups = new Map<string, IstitutoGiuridico[]>()
      for (const it of macroItems) {
        const key = it.raggruppamento?.trim() || NON_CATEGORIZZATO
        if (!groups.has(key)) groups.set(key, [])
        groups.get(key)!.push(it)
      }
      const sortedGroups = [...groups.entries()].sort(([a], [b]) => {
        if (a === NON_CATEGORIZZATO) return 1
        if (b === NON_CATEGORIZZATO) return -1
        return a.localeCompare(b)
      })
      return { ...macro, groups: sortedGroups, count: macroItems.length }
    })
  }, [items])

  const toggleMacro = (label: string) => {
    setOpenMacro((prev) => {
      const next = new Set(prev)
      next.has(label) ? next.delete(label) : next.add(label)
      return next
    })
  }

  const toggleGroup = (key: string) => {
    setOpenGroup((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })
  }

  return (
    <div className="space-y-1">
      {byMacro.map((macro) => {
        const isMacroOpen = openMacro.has(macro.label)
        return (
          <div key={macro.label}>
            <button
              onClick={() => toggleMacro(macro.label)}
              className="w-full flex items-center gap-1.5 px-2 py-1.5 rounded-md hover:bg-accent text-sm font-medium text-foreground"
            >
              {isMacroOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              <span>{macro.label}</span>
              <span className="ml-auto text-[11px] text-muted-foreground">{macro.count}</span>
            </button>

            {isMacroOpen && (
              <div className="ml-4 space-y-0.5">
                {macro.groups.length === 0 && (
                  <p className="text-xs text-muted-foreground px-2 py-1">Nessun istituto</p>
                )}
                {macro.groups.map(([groupLabel, groupItems]) => {
                  const groupKey = `${macro.label}::${groupLabel}`
                  const isGroupOpen = openGroup.has(groupKey)
                  return (
                    <div key={groupKey}>
                      <button
                        onClick={() => toggleGroup(groupKey)}
                        className="w-full flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-accent text-xs text-foreground"
                      >
                        {isGroupOpen ? (
                          <ChevronDown className="w-3 h-3" />
                        ) : (
                          <ChevronRight className="w-3 h-3" />
                        )}
                        <Folder className="w-3 h-3 text-muted-foreground" />
                        <span className="truncate">{groupLabel}</span>
                        <span className="ml-auto text-[10px] text-muted-foreground">{groupItems.length}</span>
                      </button>

                      {isGroupOpen && (
                        <div className="ml-4">
                          {groupItems.map((it) => (
                            <button
                              key={it.id}
                              onClick={() => onSelect(it)}
                              className={cn(
                                'w-full flex items-center gap-1.5 px-2 py-1 rounded-md text-xs text-left hover:bg-accent',
                                selectedId === it.id ? 'bg-accent text-foreground font-medium' : 'text-muted-foreground'
                              )}
                            >
                              <FileText className="w-3 h-3 flex-shrink-0" />
                              <span className="truncate">{it.denominazione}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
