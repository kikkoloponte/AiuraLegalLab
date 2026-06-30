import { useState } from 'react'
import { Save, Trash2, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EditableList } from '@/components/istituti/EditableList'
import {
  emptyIstituto,
  useCreateIstituto,
  useDeleteIstituto,
  useUpdateIstituto,
  type ElementoCostitutivo,
  type IstitutoGiuridico,
  type IstitutoGiuridicoInput,
  type MassimaChiave,
  type RiferimentoNormativo,
} from '@/hooks/useIstitutiGiuridici'

const CODICI = ['CC', 'CPC', 'CP', 'CPP']

interface IstitutoFormProps {
  istituto?: IstitutoGiuridico
  onClose: () => void
}

const inputClass =
  'w-full bg-card border border-border rounded-md px-2.5 py-1.5 text-sm text-foreground focus:outline-none focus:ring-1 focus:ring-primary'
const textareaClass = `${inputClass} resize-none`

function nextElementoId(items: ElementoCostitutivo[]): string {
  const n = items.length + 1
  return `elem_${String(n).padStart(2, '0')}`
}

export function IstitutoForm({ istituto, onClose }: IstitutoFormProps) {
  const [form, setForm] = useState<IstitutoGiuridicoInput>(istituto ?? emptyIstituto())
  const [fontiText, setFontiText] = useState(form.metadata_ui.fonti_mongodb_coinvolte.join(', '))

  const create = useCreateIstituto()
  const update = useUpdateIstituto()
  const del = useDeleteIstituto()

  const isEditing = !!istituto
  const pending = create.isPending || update.isPending || del.isPending

  const handleSave = () => {
    const payload: IstitutoGiuridicoInput = {
      ...form,
      metadata_ui: {
        ...form.metadata_ui,
        fonti_mongodb_coinvolte: fontiText
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      },
    }
    if (isEditing) {
      update.mutate(
        { id: istituto.id, istituto: payload, expectedVersion: istituto.version },
        { onSuccess: onClose }
      )
    } else {
      create.mutate(payload, { onSuccess: onClose })
    }
  }

  const handleDelete = () => {
    if (!istituto) return
    if (!window.confirm(`Eliminare definitivamente l'istituto "${istituto.denominazione}"?`)) return
    del.mutate(istituto.id, { onSuccess: onClose })
  }

  return (
    <div className="bg-card border border-border rounded-lg p-4 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-foreground">
          {isEditing ? 'Modifica istituto' : 'Nuovo istituto'}
        </h2>
        <button onClick={onClose} className="text-muted-foreground hover:text-foreground" aria-label="Chiudi">
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Header */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="sm:col-span-2 space-y-1">
          <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Denominazione</label>
          <input
            value={form.denominazione}
            onChange={(e) => setForm({ ...form, denominazione: e.target.value })}
            className={inputClass}
          />
        </div>
        <div className="space-y-1">
          <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Codice riferimento</label>
          <select
            value={form.codice_riferimento}
            onChange={(e) => setForm({ ...form, codice_riferimento: e.target.value })}
            className={inputClass}
          >
            {CODICI.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">
          Fonti MongoDB coinvolte (id separati da virgola)
        </label>
        <input value={fontiText} onChange={(e) => setFontiText(e.target.value)} className={inputClass} />
      </div>

      {/* Quadro normativo */}
      <EditableList<RiferimentoNormativo>
        label="Articoli principali"
        items={form.quadro_normativo.articoli_principali}
        onChange={(items) =>
          setForm({ ...form, quadro_normativo: { ...form.quadro_normativo, articoli_principali: items } })
        }
        makeEmpty={() => ({ riferimento: '', source_mongo_id: null })}
        addLabel="Aggiungi articolo"
        renderRow={(item, onUpdate) => (
          <RiferimentoRow item={item} onUpdate={onUpdate} />
        )}
      />

      <EditableList<RiferimentoNormativo>
        label="Leggi complementari"
        items={form.quadro_normativo.leggi_complementari}
        onChange={(items) =>
          setForm({ ...form, quadro_normativo: { ...form.quadro_normativo, leggi_complementari: items } })
        }
        makeEmpty={() => ({ riferimento: '', source_mongo_id: null })}
        addLabel="Aggiungi legge"
        renderRow={(item, onUpdate) => (
          <RiferimentoRow item={item} onUpdate={onUpdate} />
        )}
      />

      {/* Definizione e natura giuridica */}
      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">
          Definizione e natura giuridica
        </label>
        <textarea
          value={form.definizione_e_natura_giuridica.testo ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              definizione_e_natura_giuridica: { ...form.definizione_e_natura_giuridica, testo: e.target.value },
            })
          }
          rows={3}
          className={textareaClass}
        />
        <input
          placeholder="source_mongo_id"
          value={form.definizione_e_natura_giuridica.source_mongo_id ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              definizione_e_natura_giuridica: {
                ...form.definizione_e_natura_giuridica,
                source_mongo_id: e.target.value || null,
              },
            })
          }
          className={`${inputClass} font-mono text-xs`}
        />
      </div>

      {/* Elementi costitutivi */}
      <EditableList<ElementoCostitutivo>
        label="Elementi costitutivi"
        items={form.elementi_costitutivi}
        onChange={(items) => setForm({ ...form, elementi_costitutivi: items })}
        makeEmpty={() => ({
          id_elemento_ui: nextElementoId(form.elementi_costitutivi),
          descrizione: '',
          source_mongo_id: null,
        })}
        addLabel="Aggiungi elemento"
        renderRow={(item, onUpdate) => (
          <div className="space-y-1.5">
            <div className="text-[10px] text-muted-foreground font-mono">{item.id_elemento_ui}</div>
            <textarea
              value={item.descrizione}
              onChange={(e) => onUpdate({ ...item, descrizione: e.target.value })}
              rows={2}
              placeholder="Descrizione"
              className={textareaClass}
            />
            <input
              placeholder="source_mongo_id"
              value={item.source_mongo_id ?? ''}
              onChange={(e) => onUpdate({ ...item, source_mongo_id: e.target.value || null })}
              className={`${inputClass} font-mono text-xs`}
            />
          </div>
        )}
      />

      {/* Formazione giurisprudenziale */}
      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">Orientamento prevalente</label>
        <textarea
          value={form.formazione_giurisprudenziale.orientamento_prevalente ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              formazione_giurisprudenziale: {
                ...form.formazione_giurisprudenziale,
                orientamento_prevalente: e.target.value,
              },
            })
          }
          rows={2}
          className={textareaClass}
        />
      </div>

      <EditableList<MassimaChiave>
        label="Massime chiave"
        items={form.formazione_giurisprudenziale.massime_chiave}
        onChange={(items) =>
          setForm({
            ...form,
            formazione_giurisprudenziale: { ...form.formazione_giurisprudenziale, massime_chiave: items },
          })
        }
        makeEmpty={() => ({ riferimento_sentenza: '', principio_diritto: '', source_mongo_id: null })}
        addLabel="Aggiungi massima"
        renderRow={(item, onUpdate) => (
          <div className="space-y-1.5">
            <input
              placeholder="Riferimento sentenza"
              value={item.riferimento_sentenza}
              onChange={(e) => onUpdate({ ...item, riferimento_sentenza: e.target.value })}
              className={inputClass}
            />
            <textarea
              placeholder="Principio di diritto"
              value={item.principio_diritto}
              onChange={(e) => onUpdate({ ...item, principio_diritto: e.target.value })}
              rows={2}
              className={textareaClass}
            />
            <input
              placeholder="source_mongo_id"
              value={item.source_mongo_id ?? ''}
              onChange={(e) => onUpdate({ ...item, source_mongo_id: e.target.value || null })}
              className={`${inputClass} font-mono text-xs`}
            />
          </div>
        )}
      />

      <div className="space-y-1">
        <label className="text-[11px] text-muted-foreground uppercase tracking-wide">
          Contrasti risolti o aperti
        </label>
        <textarea
          value={form.formazione_giurisprudenziale.contrasti_risolti_o_aperti ?? ''}
          onChange={(e) =>
            setForm({
              ...form,
              formazione_giurisprudenziale: {
                ...form.formazione_giurisprudenziale,
                contrasti_risolti_o_aperti: e.target.value,
              },
            })
          }
          rows={2}
          className={textareaClass}
        />
      </div>

      <div className="flex items-center justify-between pt-2">
        {isEditing ? (
          <Button variant="destructive" size="sm" onClick={handleDelete} disabled={pending} className="gap-1.5">
            <Trash2 className="w-3.5 h-3.5" />
            Elimina istituto
          </Button>
        ) : (
          <span />
        )}
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onClose} disabled={pending}>
            Annulla
          </Button>
          <Button
            size="sm"
            onClick={handleSave}
            disabled={pending || !form.denominazione.trim()}
            className="gap-1.5"
          >
            <Save className="w-3.5 h-3.5" />
            Salva
          </Button>
        </div>
      </div>
    </div>
  )
}

function RiferimentoRow({
  item,
  onUpdate,
}: {
  item: RiferimentoNormativo
  onUpdate: (item: RiferimentoNormativo) => void
}) {
  return (
    <div className="space-y-1.5">
      <input
        placeholder="Riferimento (es. Art. 321 c.p.p.)"
        value={item.riferimento}
        onChange={(e) => onUpdate({ ...item, riferimento: e.target.value })}
        className={inputClass}
      />
      <input
        placeholder="source_mongo_id"
        value={item.source_mongo_id ?? ''}
        onChange={(e) => onUpdate({ ...item, source_mongo_id: e.target.value || null })}
        className={`${inputClass} font-mono text-xs`}
      />
    </div>
  )
}
