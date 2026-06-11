# Design Spec — Parametri LLM configurabili via UI
**Data:** 2026-06-09  
**Progetto:** AiUra LegalLab  
**Scope:** Aggiungere n_ctx, n_batch e max_tokens per-fase alla pagina Settings

---

## Problema

La pipeline Sequential IQRAC usa valori hardcoded o un unico valore globale
(`LLM_MAX_TOKENS_PER_PHASE`) per i token di output di tutte e 4 le fasi.
Su hardware con GPU commerciali (6–8 GB VRAM) questo causa:
- Troncamenti di contesto (truncated=1) su Packet RAG densi
- Loop sintattici in Fase 2 (Normativa) che richiedono un limite inferiore rispetto alle altre fasi
- Nessun controllo dal frontend su n_ctx e n_batch senza modificare file di codice

---

## Obiettivo

Rendere completamente configurabili via UI (Settings → Parametri LLM):
1. **Context Length** (`n_ctx`) — finestra KV-Cache, range 2048–32768
2. **Batch Size** (`n_batch`) — token in parallelo durante prompt ingest, range 128–512
3. **Max Output Tokens per fase** — 4 valori distinti per Fase 1/2/3/4 IQRAC

Tutti i valori vengono salvati nel `.env` di progetto e letti dinamicamente
da `analyst.py` senza riavvii manuali (il salvataggio Settings già riavvia l'API).

---

## Approccio scelto

**Variabili env flat separate** (Approccio A).

Allineato al pattern esistente. Zero rottura backward. Leggibile nel `.env` senza parsing custom.

### n_ctx / n_batch su LM Studio

LM Studio non espone questi parametri via API `/v1/chat/completions`.  
Strategia: salva nel `.env`, passa nel body JSON della chiamata come campi extra.  
LM Studio li ignora silenziosamente. Restano come riferimento documentato per la
configurazione manuale del pannello LM Studio e per futura compatibilità.  
Per Ollama vengono passati nel campo `options` e sono effettivamente rispettati.

---

## Data Model

### Nuove variabili `.env`

```
# Parametri runtime LLM
LLM_N_CTX=8192          # range 2048–32768  (default hardware comune)
LLM_N_BATCH=256         # range 128–512

# Max output tokens per fase IQRAC
LLM_MAX_TOKENS_FASE1=1024   # Framing           range 512–2048
LLM_MAX_TOKENS_FASE2=1024   # Normativa         range 512–2560
LLM_MAX_TOKENS_FASE3=1024   # Giurisprudenza    range 512–2048
LLM_MAX_TOKENS_FASE4=1536   # Sintesi/Conclusione range 512–2700
```

**Backward compatibility:** `LLM_MAX_TOKENS_PER_PHASE` resta invariato come
fallback per i path non-sequenziali (`analyze_deep`, `analyze`).

---

## Backend — `settings_router.py`

### Whitelist

Aggiungere a `_WHITELIST`:
```
LLM_N_CTX, LLM_N_BATCH,
LLM_MAX_TOKENS_FASE1, LLM_MAX_TOKENS_FASE2,
LLM_MAX_TOKENS_FASE3, LLM_MAX_TOKENS_FASE4
```

### `_DEFAULTS`

```python
"LLM_N_CTX":             "8192",
"LLM_N_BATCH":           "256",
"LLM_MAX_TOKENS_FASE1":  "1024",
"LLM_MAX_TOKENS_FASE2":  "1024",
"LLM_MAX_TOKENS_FASE3":  "1024",
"LLM_MAX_TOKENS_FASE4":  "1536",
```

### `LLMSettings` (Pydantic)

```python
llm_n_ctx:              int = Field(8192,  ge=2048,  le=32768)
llm_n_batch:            int = Field(256,   ge=128,   le=512)
llm_max_tokens_fase1:   int = Field(1024,  ge=512,   le=2048)
llm_max_tokens_fase2:   int = Field(1024,  ge=512,   le=2560)
llm_max_tokens_fase3:   int = Field(1024,  ge=512,   le=2048)
llm_max_tokens_fase4:   int = Field(1536,  ge=512,   le=2700)
```

### `_settings_from_env()` e `save_settings()`

Estendere con i 6 nuovi campi seguendo il pattern esistente
(`int(g("LLM_N_CTX") or 8192)` ecc.).

---

## Backend — `analyst.py`

### `LlmBehaviorSettings`

```python
class LlmBehaviorSettings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    llm_temperature:          float = 0.10
    llm_max_tokens_per_phase: int   = 1800   # legacy fallback
    llm_n_ctx:                int   = 8192
    llm_n_batch:              int   = 256
    llm_max_tokens_fase1:     int   = 1024
    llm_max_tokens_fase2:     int   = 1024
    llm_max_tokens_fase3:     int   = 1024
    llm_max_tokens_fase4:     int   = 1536
```

### `analyze_sequential()` — injection per fase

Sostituire i valori hardcoded nelle 4 chiamate `self._ollama.generate()`:

| Fase | Prima | Dopo |
|------|-------|------|
| F1 Framing        | `max_tokens_per_phase` | `_llm_settings.llm_max_tokens_fase1` |
| F2 Normativa      | `1500` (hardcoded)     | `_llm_settings.llm_max_tokens_fase2` |
| F3 Giurisprudenza | `max_tokens_per_phase` | `_llm_settings.llm_max_tokens_fase3` |
| F4 Sintesi        | `max_tokens_per_phase` | `_llm_settings.llm_max_tokens_fase4` |

### Injection `n_ctx` / `n_batch`

Ogni chiamata `generate()` riceve due parametri aggiuntivi:
```python
n_ctx=_llm_settings.llm_n_ctx,
n_batch=_llm_settings.llm_n_batch,
```

Il client Ollama (`self._ollama`) deve passarli nel campo `options` del body.
Verificare come `generate()` è implementato nel client — aggiungere `**kwargs`
o parametri espliciti se non già presenti.

---

## Frontend — `useSettings.ts`

Estendere l'interfaccia `LLMSettings`:

```typescript
export interface LLMSettings {
  // ... campi esistenti ...
  llm_n_ctx:              number
  llm_n_batch:            number
  llm_max_tokens_fase1:   number
  llm_max_tokens_fase2:   number
  llm_max_tokens_fase3:   number
  llm_max_tokens_fase4:   number
}
```

Aggiornare `DEFAULTS`:
```typescript
llm_n_ctx:              8192,
llm_n_batch:            256,
llm_max_tokens_fase1:   1024,
llm_max_tokens_fase2:   1024,
llm_max_tokens_fase3:   1024,
llm_max_tokens_fase4:   1536,
```

Il `save()` esistente serializza l'intero oggetto `LLMSettings` → nessun cambiamento necessario al metodo.

---

## Frontend — `Settings.tsx`

La sezione "Parametri LLM" viene ristrutturata. Il campo singolo
`llm_max_tokens_per_phase` viene **rimosso** dalla UI (resta nel .env come
fallback, ma non esposto).

### Layout della sezione aggiornata

```
Section: "Parametri LLM"
  Field: Temperatura (slider esistente — invariato)

  Field: Context Length (n_ctx)
    Input numerico, min=2048, max=32768, step=256
    Hint: "Finestra KV-Cache. 8k per GPU 6-8 GB, 16k per GPU 12 GB+.
           Per LM Studio: impostare anche nel pannello Model Config."

  Field: Batch Size (n_batch)
    Input numerico, min=128, max=512, step=64
    Hint: "Token elaborati in parallelo. Ridurre a 128-256 su GPU con VRAM limitata."

  SubSection: "Limite token per fase" (accordion collassabile, default aperto)
    Row: Fase 1 — Framing       [input 512–2048]
    Row: Fase 2 — Normativa     [input 512–2560] + badge "⚠ anti-loop"
    Row: Fase 3 — Giurisprudenza [input 512–2048]
    Row: Fase 4 — Sintesi       [input 512–2700]
```

Ogni riga della sottosezione usa un layout a griglia (label + badge opzionale + input + range display) per leggibilità su schermi stretti.

---

## Invarianti e vincoli

- `LLM_MAX_TOKENS_PER_PHASE` resta nel `.env` e nel modello backend — non viene rimosso
- Il path `analyze_deep` e `analyze` continuano a usare `llm_max_tokens_per_phase`
- Il riavvio API esistente si applica a tutte le nuove variabili
- Nessuna migrazione MongoDB necessaria (tutto in `.env`)
- TypeScript: zero `any`, tutte le chiavi tipizzate in `LLMSettings`

---

## File modificati

| File | Tipo di modifica |
|------|-----------------|
| `.env` | Aggiunta 6 variabili (se non presenti) |
| `aiura_legal/api/settings_router.py` | Whitelist + defaults + LLMSettings + _settings_from_env + save_settings |
| `aiura_legal/agents/analyst.py` | LlmBehaviorSettings + 4 chiamate generate() in analyze_sequential |
| `frontend/src/hooks/useSettings.ts` | Interfaccia LLMSettings + DEFAULTS |
| `frontend/src/pages/Settings.tsx` | Rimozione campo singolo + aggiunta n_ctx/n_batch + sottosezione 4 fasi |

Verifica opzionale: controllare il client Ollama per assicurarsi che `generate()`
accetti e passi `n_ctx`/`n_batch` nel body — se non lo fa, aggiungere i parametri.
