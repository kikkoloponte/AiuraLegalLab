import { useState } from 'react'
import { RefreshCw, Save, CheckCircle, AlertTriangle, Loader2, ChevronDown, ChevronRight } from 'lucide-react'
import { useSettings, type LLMSettings } from '@/hooks/useSettings'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

// ---------------------------------------------------------------------------
// Componenti UI di base
// ---------------------------------------------------------------------------

function Section({
  title, description, children, defaultOpen = true,
}: { title: string; description: string; children: React.ReactNode; defaultOpen?: boolean }) {
  const [open, setOpen] = useState(defaultOpen)
  return (
    <div className="border border-border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-center justify-between px-5 py-4 bg-muted/30 hover:bg-muted/50 transition-colors text-left"
      >
        <div>
          <div className="text-sm font-semibold text-foreground">{title}</div>
          <div className="text-xs text-muted-foreground mt-0.5">{description}</div>
        </div>
        {open ? <ChevronDown className="w-4 h-4 text-muted-foreground" /> : <ChevronRight className="w-4 h-4 text-muted-foreground" />}
      </button>
      {open && <div className="px-5 py-4 space-y-4">{children}</div>}
    </div>
  )
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <label className="text-xs font-medium text-foreground">{label}</label>
      {children}
      {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
    </div>
  )
}

function Input({ value, onChange, type = 'text', min, max, step, placeholder, disabled }: {
  value: string | number; onChange: (v: string) => void
  type?: string; min?: number; max?: number; step?: number
  placeholder?: string; disabled?: boolean
}) {
  return (
    <input
      type={type}
      value={value}
      min={min} max={max} step={step}
      placeholder={placeholder}
      disabled={disabled}
      onChange={(e) => onChange(e.target.value)}
      className={cn(
        'w-full bg-muted border border-border rounded-md px-3 py-1.5 text-sm text-foreground',
        'focus:outline-none focus:ring-1 focus:ring-primary transition-colors',
        'disabled:opacity-50 disabled:cursor-not-allowed',
      )}
    />
  )
}

function Select({ value, onChange, options, disabled }: {
  value: string; onChange: (v: string) => void
  options: { value: string; label: string }[]; disabled?: boolean
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className={cn(
        'w-full bg-muted border border-border rounded-md px-3 py-1.5 text-sm text-foreground',
        'focus:outline-none focus:ring-1 focus:ring-primary transition-colors',
        'disabled:opacity-50 disabled:cursor-not-allowed',
      )}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>{o.label}</option>
      ))}
    </select>
  )
}

function Slider({ value, onChange, min, max, step, disabled }: {
  value: number; onChange: (v: number) => void
  min: number; max: number; step: number; disabled?: boolean
}) {
  return (
    <div className="flex items-center gap-3">
      <input
        type="range"
        value={value}
        min={min} max={max} step={step}
        disabled={disabled}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="flex-1 accent-primary disabled:opacity-50"
      />
      <span className="text-sm font-mono text-foreground w-12 text-right">{value.toFixed(2)}</span>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Pagina Settings
// ---------------------------------------------------------------------------

export function Settings() {
  const {
    settings, setSettings,
    models, modelsError,
    loading, saving, restartPending, restartTimeout, online,
    save, fetchModels,
  } = useSettings()

  const [saveError, setSaveError] = useState<string | null>(null)

  const update = <K extends keyof LLMSettings>(key: K, value: LLMSettings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    setSaveError(null)
    try {
      await save(settings)
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : 'Errore sconosciuto')
    }
  }

  const isDisabled = saving || restartPending || loading
  const activeBackend = settings.aiura_llm_backend

  // Modelli disponibili per dropdown — se lista vuota, campo testo libero
  const modelOptions = models.length > 0
    ? models.map((m) => ({ value: m, label: m }))
    : null

  const currentModel = activeBackend === 'ollama'
    ? settings.ollama_model_main
    : settings.lmstudio_model

  const setCurrentModel = (v: string) => {
    if (activeBackend === 'ollama') update('ollama_model_main', v)
    else update('lmstudio_model', v)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-muted-foreground gap-2">
        <Loader2 className="w-5 h-5 animate-spin" />
        <span className="text-sm">Caricamento configurazione...</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="px-8 py-6 max-w-2xl w-full mx-auto space-y-4">

        {/* Header */}
        <div className="mb-2">
          <h1 className="text-lg font-bold text-foreground">Impostazioni</h1>
          <p className="text-sm text-muted-foreground">Configurazione LLM e retrieval. Il salvataggio riavvia l'API (~10s).</p>
        </div>

        {/* Banner stato riavvio */}
        {restartPending && (
          <div className="flex items-center gap-3 bg-primary/10 border border-primary/30 rounded-lg px-4 py-3">
            <Loader2 className="w-4 h-4 animate-spin text-primary flex-shrink-0" />
            <div>
              <div className="text-sm font-medium text-primary">Riavvio API in corso...</div>
              <div className="text-xs text-muted-foreground">La pagina si aggiornerà automaticamente (attendi ~10s)</div>
            </div>
          </div>
        )}
        {online && (
          <div className="flex items-center gap-3 bg-green-500/10 border border-green-500/30 rounded-lg px-4 py-3">
            <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
            <div className="text-sm font-medium text-green-500">API operativa · Configurazione applicata</div>
          </div>
        )}
        {restartTimeout && (
          <div className="flex items-center gap-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg px-4 py-3">
            <AlertTriangle className="w-4 h-4 text-yellow-500 flex-shrink-0" />
            <div>
              <div className="text-sm font-medium text-yellow-500">Riavvio non rilevato</div>
              <div className="text-xs text-muted-foreground">Verifica il terminale e riavvia manualmente se necessario</div>
            </div>
          </div>
        )}
        {saveError && (
          <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
            <AlertTriangle className="w-4 h-4 text-red-500 flex-shrink-0" />
            <div className="text-sm text-red-500">{saveError}</div>
          </div>
        )}

        {/* ── Sezione 1: Backend ── */}
        <Section title="Backend LLM" description="Provider e URL di connessione">
          <Field label="Provider">
            <div className="flex gap-3">
              {(['lmstudio', 'ollama'] as const).map((b) => (
                <button
                  key={b}
                  disabled={isDisabled}
                  onClick={() => update('aiura_llm_backend', b)}
                  className={cn(
                    'flex-1 py-2 rounded-md border text-sm font-medium transition-colors',
                    settings.aiura_llm_backend === b
                      ? 'bg-primary text-primary-foreground border-primary'
                      : 'border-border text-muted-foreground hover:border-primary/50',
                    isDisabled && 'opacity-50 cursor-not-allowed',
                  )}
                >
                  {b === 'lmstudio' ? 'LMStudio' : 'Ollama'}
                </button>
              ))}
            </div>
          </Field>

          {activeBackend === 'lmstudio' && (
            <Field label="LMStudio base URL" hint="Indirizzo del server LMStudio locale">
              <Input
                value={settings.lmstudio_base_url}
                onChange={(v) => update('lmstudio_base_url', v)}
                placeholder="http://127.0.0.1:1234"
                disabled={isDisabled}
              />
            </Field>
          )}
          {activeBackend === 'ollama' && (
            <Field label="Ollama base URL" hint="Indirizzo del server Ollama locale">
              <Input
                value={settings.ollama_base_url}
                onChange={(v) => update('ollama_base_url', v)}
                placeholder="http://localhost:11434"
                disabled={isDisabled}
              />
            </Field>
          )}
        </Section>

        {/* ── Sezione 2: Modello ── */}
        <Section title="Modello" description="Modello LLM e parametri di connessione">
          <Field
            label="Modello attivo"
            hint={modelsError ? `⚠ ${modelsError} — inserisci il nome manualmente` : undefined}
          >
            <div className="flex gap-2">
              {modelOptions ? (
                <Select
                  value={currentModel}
                  onChange={setCurrentModel}
                  options={modelOptions}
                  disabled={isDisabled}
                />
              ) : (
                <Input
                  value={currentModel}
                  onChange={setCurrentModel}
                  placeholder="es. qwen3-14b"
                  disabled={isDisabled}
                />
              )}
              <button
                onClick={fetchModels}
                disabled={isDisabled}
                title="Ricarica lista modelli"
                className="p-2 rounded-md border border-border hover:bg-accent transition-colors disabled:opacity-50"
              >
                <RefreshCw className="w-4 h-4 text-muted-foreground" />
              </button>
            </div>
          </Field>

          {activeBackend === 'lmstudio' && (
            <Field label="Timeout (secondi)" hint="Tempo massimo per risposta LLM — aumenta per modelli più grandi (min 30, max 600)">
              <Input
                type="number"
                value={settings.lmstudio_timeout}
                onChange={(v) => update('lmstudio_timeout', Math.max(30, Math.min(600, parseInt(v) || 300)))}
                min={30} max={600}
                disabled={isDisabled}
              />
            </Field>
          )}
        </Section>

        {/* ── Sezione 3: Parametri LLM ── */}
        <Section title="Parametri LLM" description="Temperatura e lunghezza delle risposte per fase IQRAC">
          <Field label={`Temperatura: ${settings.llm_temperature.toFixed(2)}`} hint="Valori bassi = risposte più deterministiche. Consigliato 0.05–0.15 per analisi legale.">
            <Slider
              value={settings.llm_temperature}
              onChange={(v) => update('llm_temperature', v)}
              min={0} max={1} step={0.01}
              disabled={isDisabled}
            />
          </Field>

          <Field label="Max tokens per fase IQRAC" hint="Token massimi generati per ogni fase (Framing/Normativa/Giurisprudenza/Sintesi). Range: 500–4000.">
            <Input
              type="number"
              value={settings.llm_max_tokens_per_phase}
              onChange={(v) => update('llm_max_tokens_per_phase', Math.max(500, Math.min(4000, parseInt(v) || 1800)))}
              min={500} max={4000}
              disabled={isDisabled}
            />
          </Field>
        </Section>

        {/* ── Sezione 4: Retrieval ── */}
        <Section title="Retrieval" description="Numero di fonti recuperate e reranked per ogni ricerca" defaultOpen={false}>
          <Field label="Fonti per round (rerank)" hint="Fonti finali mantenute dopo CrossEncoder reranking. Più alto = più ricco ma più lento. Range: 1–20.">
            <Input
              type="number"
              value={settings.retrieval_top_k_rerank}
              onChange={(v) => update('retrieval_top_k_rerank', Math.max(1, Math.min(20, parseInt(v) || 6)))}
              min={1} max={20}
              disabled={isDisabled}
            />
          </Field>

          <Field label="Candidati retrieval" hint="Documenti candidati recuperati da BM25+Vector prima del reranking. Range: 5–50.">
            <Input
              type="number"
              value={settings.retrieval_top_k_retrieve}
              onChange={(v) => update('retrieval_top_k_retrieve', Math.max(5, Math.min(50, parseInt(v) || 20)))}
              min={5} max={50}
              disabled={isDisabled}
            />
          </Field>
        </Section>

        {/* ── Footer ── */}
        <div className="pt-2 pb-8">
          <Button
            onClick={handleSave}
            disabled={isDisabled}
            className="w-full gap-2"
          >
            {saving || restartPending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                {restartPending ? 'Attendo riavvio API...' : 'Salvataggio...'}
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Salva e riavvia API
              </>
            )}
          </Button>
        </div>

      </div>
    </div>
  )
}
