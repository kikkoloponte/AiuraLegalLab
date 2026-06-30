import { Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface EditableListProps<T> {
  label: string
  items: T[]
  onChange: (items: T[]) => void
  makeEmpty: () => T
  renderRow: (item: T, onUpdate: (item: T) => void) => React.ReactNode
  addLabel?: string
}

/**
 * Lista di righe editabili con bottone "rimuovi" per riga e "aggiungi riga"
 * in fondo — meccanismo unico di cancellazione di una singola voce
 * annidata: si rimuove la riga e si salva il form (PUT completo).
 */
export function EditableList<T>({ label, items, onChange, makeEmpty, renderRow, addLabel }: EditableListProps<T>) {
  const updateAt = (index: number, value: T) => {
    onChange(items.map((it, i) => (i === index ? value : it)))
  }
  const removeAt = (index: number) => {
    onChange(items.filter((_, i) => i !== index))
  }
  const add = () => {
    onChange([...items, makeEmpty()])
  }

  return (
    <div className="space-y-2">
      <label className="text-[11px] text-muted-foreground uppercase tracking-wide">{label}</label>
      <div className="space-y-2">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-2 bg-muted border border-border rounded-md p-2">
            <div className="flex-1">{renderRow(item, (v) => updateAt(i, v))}</div>
            <button
              type="button"
              onClick={() => removeAt(i)}
              className="text-muted-foreground hover:text-red-500 mt-1"
              aria-label="Rimuovi riga"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
      <Button type="button" variant="outline" size="sm" onClick={add} className="gap-1.5">
        <Plus className="w-3.5 h-3.5" />
        {addLabel ?? 'Aggiungi riga'}
      </Button>
    </div>
  )
}
