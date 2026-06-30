import { useState } from 'react'
import { ClipboardCheck } from 'lucide-react'
import { cn } from '@/lib/utils'
import { QuestioneCard } from '@/components/questioni/QuestioneCard'
import { useQuestioniList, type QuestioneStato } from '@/hooks/useQuestioni'

const TABS: { value: QuestioneStato; label: string }[] = [
  { value: 'proposto', label: 'Da revisionare' },
  { value: 'approvato', label: 'Approvate' },
  { value: 'rifiutato', label: 'Rifiutate' },
]

export function Questioni() {
  const [tab, setTab] = useState<QuestioneStato>('proposto')
  const { data, isLoading } = useQuestioniList(tab)
  const items = data?.items ?? []
  const version = data?.version ?? ''

  return (
    <div className="flex h-full flex-col overflow-y-auto px-6 py-5">
      <div className="flex items-center gap-2 mb-1">
        <ClipboardCheck className="w-5 h-5 text-primary" />
        <h1 className="text-lg font-semibold text-foreground">Questioni da approvare</h1>
      </div>
      <p className="text-sm text-muted-foreground mb-4">
        Revisione delle QuestioneGiuridica proposte — approva, modifica o rifiuta senza editare il registro a mano.
      </p>

      <div className="flex gap-1 border-b border-border mb-4">
        {TABS.map((t) => (
          <button
            key={t.value}
            onClick={() => setTab(t.value)}
            className={cn(
              'px-3 py-2 text-sm border-b-2 -mb-px transition-colors',
              tab === t.value
                ? 'border-primary text-foreground font-medium'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading && <p className="text-sm text-muted-foreground">Caricamento…</p>}

      {!isLoading && items.length === 0 && (
        <p className="text-sm text-muted-foreground">Nessuna voce in questa categoria.</p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {items.map((q) => (
          <QuestioneCard key={q.id} questione={q} version={version} />
        ))}
      </div>
    </div>
  )
}
