# Settings UI — Configurazione LLM da interfaccia

**Data:** 2026-06-06  
**Obiettivo:** Pagina Settings nel portale per configurare backend LLM, modello,
timeout e parametri di retrieval, con salvataggio su `.env` e riavvio automatico dell'API.

---

## Problema

I parametri LLM (modello, timeout, temperatura, retrieval) sono configurabili solo
modificando `.env` manualmente e riavviando l'API da terminale. L'avvocato o il
tecnico non-dev non può cambiarli senza accesso al filesystem.

---

## Soluzione

Pagina `/settings` nel frontend con quattro sezioni configurabili.
Il salvataggio scrive `.env`, poi l'API si riavvia da sola.
L'UI mostra uno spinner e fa polling su `/health` finché l'API non risponde.

---

## Parametri configurabili

| Sezione | Parametro | Variabile `.env` | Default |
|---------|-----------|-----------------|---------|
| **Backend** | Provider LLM | `AIURA_LLM_BACKEND` | `lmstudio` |
| **Backend** | Ollama base URL | `OLLAMA_BASE_URL` | `http://localhost:11434` |
| **Backend** | LMStudio base URL | `LMSTUDIO_BASE_URL` | `http://127.0.0.1:1234` |
| **Modello** | Nome modello | `OLLAMA_MODEL_MAIN` / `LMSTUDIO_MODEL` | — |
| **Modello** | Timeout (s) | `LMSTUDIO_TIMEOUT` | `300` |
| **LLM** | Temperatura | `LLM_TEMPERATURE` | `0.10` |
| **LLM** | Max tokens per fase IQRAC | `LLM_MAX_TOKENS_PER_PHASE` | `1800` |
| **Retrieval** | Fonti per round (rerank) | `RETRIEVAL_TOP_K_RERANK` | `6` |
| **Retrieval** | Candidati retrieval | `RETRIEVAL_TOP_K_RETRIEVE` | `20` |

---

## Architettura backend

### Nuovo router: `aiura_legal/api/settings_router.py`

**`GET /settings`**
Legge il file `.env` corrente riga per riga, estrae le variabili configurabili
e le restituisce come JSON. Non espone variabili sensibili (MongoDB URI, chiavi).

**`GET /settings/models`**
Interroga il backend LLM attivo:
- Ollama: `GET /api/tags` → lista nomi modelli
- LMStudio: `GET /v1/models` → lista model id

Restituisce `{"models": ["qwen3-14b", "qwen2.5:7b", ...]}`.
Se il backend non è raggiungibile: restituisce lista vuota (non errore).

**`POST /settings`**
1. Valida i valori ricevuti (temperatura in [0.0, 1.0], timeout > 0, ecc.)
2. Fa backup di `.env` → `.env.bak`
3. Legge `.env` corrente, aggiorna solo le variabili note, lascia intatte le altre
4. Scrive il nuovo `.env`
5. Risponde `{"ok": true, "message": "Configurazione salvata. Riavvio in corso..."}`
6. Schedula riavvio asincrono: `loop.call_later(0.8, _restart)`

**Riavvio (`_restart`):**
```python
import subprocess, sys, os
subprocess.Popen([sys.executable, "-m", "aiura_legal.api"])
os._exit(0)
```
Lancia un nuovo processo API e termina quello corrente.
Funziona su Windows con avvio manuale da terminale.

### Variabili nuove nel codice

I nuovi parametri (`LLM_TEMPERATURE`, `LLM_MAX_TOKENS_PER_PHASE`,
`RETRIEVAL_TOP_K_RERANK`, `RETRIEVAL_TOP_K_RETRIEVE`) vengono letti
da `pydantic_settings.BaseSettings` nelle classi già esistenti:

- `analyst.py` → `LlmBehaviorSettings` legge temperatura e max_tokens_per_phase,
  passati come default a `analyze_sequential()`
- `hybrid_retriever.py` → `RetrievalSettings` legge top_k_retrieve e top_k_rerank,
  usati nei metodi `search()` e `_search_round()`

---

## Architettura frontend

### `frontend/src/hooks/useSettings.ts`

```typescript
// Carica config corrente
useSettings() → { settings, models, loading, save, saving, restartPending }

// save(newSettings) →
//   1. POST /api/settings
//   2. setta restartPending=true
//   3. poll /api/health ogni 2s per max 60s
//   4. quando health risponde → restartPending=false, toast "API operativa"
```

### `frontend/src/pages/Settings.tsx`

Quattro sezioni con accordion collassabile:

**1. Backend**
- Radio: Ollama / LMStudio
- Input testo: base URL (mostra solo quello del backend selezionato)

**2. Modello**
- Dropdown: lista modelli da `GET /settings/models` (con refresh button)
- Se lista vuota: input testo libero con placeholder
- Input numerico: Timeout (secondi), min=30, max=600

**3. Parametri LLM**
- Slider + input: Temperatura (0.00–1.00, step 0.01)
- Input numerico: Max tokens per fase (500–4000)

**4. Retrieval**
- Input numerico: Fonti per round — top_k_rerank (1–20)
- Input numerico: Candidati retrieval — top_k_retrieve (10–50)

**Footer della pagina:**
- Pulsante "Salva e riavvia" (disabled durante saving/restartPending)
- Durante riavvio: spinner + "Riavvio API in corso... (attendi ~10s)"
- Al ritorno online: toast verde "API operativa · Configurazione applicata"
- In caso di timeout (60s): messaggio "Riavvio non rilevato — verifica il terminale"

### Sidebar e routing

- Aggiunta voce "Impostazioni" (icona `Settings`) in fondo alla nav, sopra Cronologia
- Route `/settings` in `App.tsx`

---

## Gestione errori

| Scenario | Comportamento |
|---------|--------------|
| Backend LLM non raggiungibile per lista modelli | Lista vuota, input testo libero |
| Valore non valido (temperatura > 1) | Validazione client-side + server-side, messaggio inline |
| Riavvio non avviene entro 60s | Messaggio "Verifica il terminale" senza bloccare l'UI |
| `.env` non scrivibile (permessi) | `500` con messaggio esplicativo |
| Backup `.env.bak` fallisce | Il salvataggio procede comunque (warning in log) |

---

## File da creare/modificare

| File | Tipo | Descrizione |
|------|------|-------------|
| `aiura_legal/api/settings_router.py` | Nuovo | GET/POST /settings, GET /settings/models |
| `frontend/src/pages/Settings.tsx` | Nuovo | Pagina settings con 4 sezioni |
| `frontend/src/hooks/useSettings.ts` | Nuovo | Fetch/save/poll logic |
| `aiura_legal/api/app.py` | Modifica | include settings_router |
| `frontend/src/App.tsx` | Modifica | + route /settings |
| `frontend/src/components/layout/Sidebar.tsx` | Modifica | + voce Impostazioni |
| `aiura_legal/agents/analyst.py` | Modifica | legge LLM_TEMPERATURE, LLM_MAX_TOKENS_PER_PHASE |
| `aiura_legal/core/retrieval/hybrid_retriever.py` | Modifica | legge RETRIEVAL_TOP_K_* |

---

## Non incluso in questo scope

- Autenticazione / protezione della pagina settings
- Multi-utente (ogni utente con config propria)
- Storico delle configurazioni precedenti
- Configurazione workspace-specifica (è globale)
