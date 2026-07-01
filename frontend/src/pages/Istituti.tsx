import { useState } from 'react'
import { Plus, Scale } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { IstitutoForm } from '@/components/istituti/IstitutoForm'
import { IstitutiTree } from '@/components/istituti/IstitutiTree'
import { useIstitutiList, type IstitutoGiuridico } from '@/hooks/useIstitutiGiuridici'

export function Istituti() {
  const { data, isLoading } = useIstitutiList()
  const items = data ?? []
  const [editing, setEditing] = useState<IstitutoGiuridico | 'new' | null>(null)

  return (
    <div className="flex h-full flex-col px-6 py-5 overflow-hidden">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <Scale className="w-5 h-5 text-primary" />
          <h1 className="text-lg font-semibold text-foreground">Istituti Giuridici</h1>
        </div>
        <Button size="sm" onClick={() => setEditing('new')} className="gap-1.5">
          <Plus className="w-3.5 h-3.5" />
          Nuovo istituto
        </Button>
      </div>
      <p className="text-sm text-muted-foreground mb-4">
        Schede istituto tracciate dalla Knowledge Base — crea, modifica o elimina senza toccare MongoDB a mano.
      </p>

      <div className="flex flex-1 gap-4 min-h-0">
        <div className="w-72 flex-shrink-0 overflow-y-auto border border-border rounded-lg p-2">
          {isLoading && <p className="text-sm text-muted-foreground px-2">Caricamento…</p>}
          {!isLoading && items.length === 0 && (
            <p className="text-sm text-muted-foreground px-2">Nessun istituto censito.</p>
          )}
          {!isLoading && items.length > 0 && (
            <IstitutiTree
              items={items}
              selectedId={editing !== 'new' ? editing?.id : undefined}
              onSelect={(it) => setEditing(it)}
            />
          )}
        </div>

        <div className="flex-1 overflow-y-auto">
          {editing ? (
            <IstitutoForm istituto={editing === 'new' ? undefined : editing} onClose={() => setEditing(null)} />
          ) : (
            <div className="h-full flex items-center justify-center text-sm text-muted-foreground">
              Seleziona un istituto dall'albero o creane uno nuovo.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
