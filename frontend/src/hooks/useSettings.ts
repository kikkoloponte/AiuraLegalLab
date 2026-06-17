import { useState, useEffect, useCallback } from 'react'

export interface LLMSettings {
  aiura_llm_backend:        'ollama' | 'lmstudio'
  ollama_base_url:          string
  ollama_model_main:        string
  lmstudio_base_url:        string
  lmstudio_model:           string
  lmstudio_timeout:         number
  llm_temperature:          number
  llm_max_tokens_per_phase: number  // legacy fallback — non esposto in UI
  // Parametri runtime LLM
  llm_n_ctx:                number
  llm_n_batch:              number
  // Max output tokens per fase IQRAC
  llm_max_tokens_fase1:     number
  llm_max_tokens_fase2:     number
  llm_max_tokens_fase3:     number
  llm_max_tokens_fase4:     number
  retrieval_top_k_rerank:   number
  retrieval_top_k_retrieve: number
  qdrant_url:               string  // vuoto = Qdrant embedded
}

const DEFAULTS: LLMSettings = {
  aiura_llm_backend:        'lmstudio',
  ollama_base_url:          'http://localhost:11434',
  ollama_model_main:        'qwen2.5:7b',
  lmstudio_base_url:        'http://127.0.0.1:1234',
  lmstudio_model:           'qwen2.5-7b-instruct',
  lmstudio_timeout:         300,
  llm_temperature:          0.10,
  llm_max_tokens_per_phase: 1800,
  llm_n_ctx:                8192,
  llm_n_batch:              256,
  llm_max_tokens_fase1:     700,
  llm_max_tokens_fase2:     1100,
  llm_max_tokens_fase3:     900,
  llm_max_tokens_fase4:     1000,
  retrieval_top_k_rerank:   6,
  retrieval_top_k_retrieve: 20,
  qdrant_url:               '',
}

export function useSettings() {
  const [settings, setSettings]         = useState<LLMSettings>(DEFAULTS)
  const [models, setModels]             = useState<string[]>([])
  const [modelsError, setModelsError]   = useState<string | null>(null)
  const [loading, setLoading]           = useState(true)
  const [saving, setSaving]             = useState(false)
  const [restartPending, setRestartPending] = useState(false)
  const [restartTimeout, setRestartTimeout] = useState(false)
  const [online, setOnline]             = useState(false)

  // ── Carica config corrente ──────────────────────────────────────────
  useEffect(() => {
    fetch('/api/settings')
      .then((r) => r.json())
      .then((data) => {
        setSettings({ ...DEFAULTS, ...data.settings })
      })
      .catch(() => { /* usa i default */ })
      .finally(() => setLoading(false))
  }, [])

  // ── Carica lista modelli ────────────────────────────────────────────
  const fetchModels = useCallback(async () => {
    setModelsError(null)
    try {
      const r = await fetch('/api/settings/models')
      const data = await r.json()
      setModels(data.models ?? [])
      if (data.error) setModelsError(data.error)
    } catch {
      setModels([])
      setModelsError('Backend LLM non raggiungibile')
    }
  }, [])

  useEffect(() => { fetchModels() }, [fetchModels])

  // ── Polling /health dopo riavvio ────────────────────────────────────
  useEffect(() => {
    if (!restartPending) return

    let attempts = 0
    const MAX_ATTEMPTS = 30  // 30 × 2s = 60s

    const interval = setInterval(async () => {
      attempts++
      try {
        const r = await fetch('/api/health')
        if (r.ok) {
          clearInterval(interval)
          setRestartPending(false)
          setSaving(false)
          setOnline(true)
          // Ricarica config e modelli dopo il riavvio
          const data = await (await fetch('/api/settings')).json()
          setSettings({ ...DEFAULTS, ...data.settings })
          fetchModels()
          setTimeout(() => setOnline(false), 4000)
        }
      } catch { /* API ancora offline */ }

      if (attempts >= MAX_ATTEMPTS) {
        clearInterval(interval)
        setRestartPending(false)
        setSaving(false)
        setRestartTimeout(true)
        setTimeout(() => setRestartTimeout(false), 8000)
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [restartPending, fetchModels])

  // ── Salva e riavvia ─────────────────────────────────────────────────
  const save = useCallback(async (newSettings: LLMSettings) => {
    setSaving(true)
    setOnline(false)
    setRestartTimeout(false)
    try {
      const r = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newSettings),
      })
      if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: 'Errore sconosciuto' }))
        throw new Error(err.detail ?? 'Errore salvataggio')
      }
      setSettings(newSettings)
      setRestartPending(true)
    } catch (err) {
      setSaving(false)
      throw err
    }
  }, [])

  return {
    settings,
    setSettings,
    models,
    modelsError,
    loading,
    saving,
    restartPending,
    restartTimeout,
    online,
    save,
    fetchModels,
  }
}
