import { useState } from 'react'
import { Plus, Scale } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { IstitutoForm } from '@/components/istituti/IstitutoForm'
import { useIstitutiList, type IstitutoGiuridico } from '@/hooks/useIstitutiGiuridici'

export function Istituti() {
  const { data, isLoading } = useIstitutiList()
  const items = data ?? []
  const [editing, setEditing] = useState<IstitutoGiuridico | 'new' | null>(null)

  return (
    <div className="flex h-full flex-col overflow-y-auto px-6 py-5">
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

      {editing && (
        <div className="mb-4">
          <IstitutoForm
            istituto={editing === 'new' ? undefined : editing}
            onClose={() => setEditing(null)}
          />
        </div>
      )}

      {isLoading && <p className="text-sm text-muted-foreground">Caricamento…</p>}

      {!isLoading && items.length === 0 && !editing && (
        <p className="text-sm text-muted-foreground">Nessun istituto censito.</p>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {items.map((istituto) => (
          <button
            key={istituto.id}
            onClick={() => setEditing(istituto)}
            className="text-left bg-card border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <div className="flex items-center justify-between gap-2 mb-2">
              <span className="text-sm font-medium text-foreground truncate">{istituto.denominazione}</span>
              <Badge variant="default">{istituto.codice_riferimento}</Badge>
            </div>
            <p className="text-xs text-muted-foreground line-clamp-2">
              {istituto.definizione_e_natura_giuridica.testo ?? 'Nessuna definizione inserita.'}
            </p>
          </button>
        ))}
      </div>
    </div>
  )
}
