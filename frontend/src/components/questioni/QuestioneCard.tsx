import { useState } from 'react'
import { Check, X, Save } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { NodeIdPicker } from '@/components/questioni/NodeIdPicker'
import { useUpdateQuestione, type Questione } from '@/hooks/useQuestioni'

interface QuestioneCardProps {
  questione: Questione
  version: string
}

const STATO_BADGE = {
  proposto: { variant: 'warn' as const, label: 'Proposto' },
  approvato: { variant: 'pass' as const, label: 'Approvato' },
  rifiutato: { variant: 'fail' as const, label: 'Rifiutato' },
}

export function QuestioneCard({ questione, version }: QuestioneCardProps) {
  const update = useUpdateQuestione()

  const [formulazione, setFormulazione] = useState(questione.formulazione)
  const [materia, setMateria] = useState(questione.materia)
  const [normePertinenti, setNormePertinenti] = useState(questione.norme_pertinenti)
  const [decisioniPertinenti, setDecisioniPertinenti] = useState(questione.decisioni_pertinenti)

  const dirty =
    formulazione !== questione.formulazione ||
    materia !== questione.materia ||
    JSON.stringify(normePertinenti) !== JSON.stringify(questione.norme_pertinenti) ||
    JSON.stringify(decisioniPertinenti) !== JSON.stringify(questione.decisioni_pertinenti)

  const pendingChanges = () => ({
    formulazione,
    materia,
    norme_pertinenti: normePertinenti,
    decisioni_pertinenti: decisioniPertinenti,
  })

  const handleSave = () => {
    update.mutate({ id: questione.id, changes: pendingChanges(), expectedVersion: version })
  }

  const handleApprove = () => {
    update.mutate({ id: questione.id, changes: { ...pendingChanges(), stato: 'approvato' }, expectedVersion: version })
  }

  const handleReject = () => {
    update.mutate({ id: questione.id, changes: { ...pendingChanges(), stato: 'rifiutato' }, expectedVersion: version })
  }

  const badge = STATO_BADGE[questione.stato]

  return (
    <div className="bg-card border border-border rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] text-muted-foreground font-mono truncate">{questione.id}</span>
        <Badge variant={badge.variant}>{badge.label}</Badge>
      </div>

      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Formulazione</label>
        <textarea
          value={formulazione}
          onChange={(e) => setFormulazione(e.target.value)}
          rows={2}
          className="w-full bg-muted border border-border rounded-md px-2.5 py-1.5 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary resize-none"
        />
      </div>

      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Materia</label>
        <input
          value={materia}
          onChange={(e) => setMateria(e.target.value)}
          className="w-full bg-muted border border-border rounded-md px-2.5 py-1 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Norme pertinenti</label>
        <NodeIdPicker
          nodeType="article"
          ids={normePertinenti}
          onAdd={(id) => setNormePertinenti((prev) => [...prev, id])}
          onRemove={(id) => setNormePertinenti((prev) => prev.filter((x) => x !== id))}
        />
      </div>

      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Decisioni pertinenti</label>
        <NodeIdPicker
          nodeType="sentenza"
          ids={decisioniPertinenti}
          onAdd={(id) => setDecisioniPertinenti((prev) => [...prev, id])}
          onRemove={(id) => setDecisioniPertinenti((prev) => prev.filter((x) => x !== id))}
        />
      </div>

      <div className="flex items-center justify-end gap-2 pt-1">
        <Button variant="outline" size="sm" onClick={handleReject} disabled={update.isPending} className="gap-1.5">
          <X className="w-3.5 h-3.5" />
          Rifiuta
        </Button>
        <Button variant="secondary" size="sm" onClick={handleSave} disabled={!dirty || update.isPending} className="gap-1.5">
          <Save className="w-3.5 h-3.5" />
          Salva
        </Button>
        <Button size="sm" onClick={handleApprove} disabled={update.isPending} className="gap-1.5">
          <Check className="w-3.5 h-3.5" />
          Approva
        </Button>
      </div>
    </div>
  )
}
