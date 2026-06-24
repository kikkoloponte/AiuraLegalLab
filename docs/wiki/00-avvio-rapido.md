# Avvio rapido — AiUra LegalLab

Guida per avviare tutti i servizi in ordine corretto. Da leggere dall'alto in basso.

---

## Prerequisiti esterni (una tantum)

Questi programmi devono essere installati sul PC ma **non sono gestiti da questo repo**:

| Servizio | Versione | Scarica da |
|----------|----------|------------|
| MongoDB | 8.x | mongodb.com/try/download/community |
| Node.js | 20+ | nodejs.org |
| LM Studio | latest | lmstudio.ai |
| Docker Desktop | latest | docker.com (solo se Qdrant in server mode) |

---

## Avvio sessione di lavoro (ordine da rispettare)

### 1. MongoDB

MongoDB gira come servizio Windows. Va avviato **prima** di tutto il resto.

**Metodo A — PowerShell normale** (nella maggior parte dei casi basta):
```powershell
Start-Service MongoDB
```

**Metodo B — PowerShell come Amministratore** (se il metodo A fallisce):
```powershell
# Apri PowerShell come Admin, poi:
Start-Service MongoDB
```

**Verifica:**
```powershell
(Get-Service MongoDB).Status   # deve essere: Running
```

> **Problema: "Impossibile avviare il servizio"** — succede dopo un crash OOM o arresto forzato.
> Soluzione da PowerShell **Admin**:
> ```powershell
> Remove-Item "C:\Program Files\MongoDB\Server\8.3\data\mongod.lock" -Force -ErrorAction SilentlyContinue
> Start-Service MongoDB
> ```
> Se ancora non parte, riavvia il PC: Windows risolve automaticamente i lock stale.

---

### 2. Qdrant (Vector DB)

Due modalità: **embedded** (default, nessuna azione) oppure **server** (Docker).

#### Modalità embedded (default, zero config)
Qdrant parte in-process con l'API Python. I dati vengono salvati in
`workspaces/mio-studio/qdrant_storage/`. Nessun comando necessario.

Verifica che `.env` contenga:
```env
QDRANT_URL=   # vuoto = embedded
```

#### Modalità server con Docker (raccomandato per performance)
```powershell
# Avvio (crea il container se non esiste)
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 `
  -v "${PWD}/qdrant_data:/qdrant/storage" `
  qdrant/qdrant

# Stop
docker stop qdrant

# Riavvio sessione successiva
docker start qdrant
```

Verifica: http://localhost:6333/collections (deve rispondere 200)

In `.env` imposta:
```env
QDRANT_URL=http://localhost:6333
```

> **Nota:** se passi da embedded a server mode (o viceversa), i dati NON si migrano
> automaticamente — devi ricostruire gli indici con `build_jurisprudence_indexes.py`.

---

### 3. LM Studio (LLM locale)

1. Apri **LM Studio** dall'icona nel taskbar
2. Carica il modello: **qwen2.5-7b-instruct** (o quello configurato in `.env`)
3. Vai su **Local Server** e premi **Start Server**
4. Il server deve rispondere su `http://127.0.0.1:1234`

Verifica:
```powershell
curl http://127.0.0.1:1234/v1/models
# deve restituire JSON con i modelli caricati
```

> **LM Studio non è obbligatorio per avviare l'API.** Se non è attivo, l'API parte
> comunque ma risponde senza testo LLM (`ollama: false` nell'health check).
> Il retrieval BM25+vector continua a funzionare normalmente.

---

### 4. API Python

```powershell
# Dalla root del progetto
.venv\Scripts\activate
python -m aiura_legal.api
```

**Output di avvio normale:**
```
INFO  | MongoDB: connesso
INFO  | Wiki layer: inizializzato
INFO  | LLM backend: LMStudio (http://127.0.0.1:1234, model=qwen2.5-7b-instruct)
INFO  | LMStudio: disponibile — modelli: [qwen2.5-7b-instruct]
INFO  | Uvicorn running on http://127.0.0.1:8765
```

**Verifica health:**
```powershell
curl http://127.0.0.1:8765/health
# → {"status":"ok","mongodb":true,"ollama":true,"version":"0.1.0.dev0"}
```

| Campo health | Valore atteso | Problema se falso |
|---|---|---|
| `mongodb` | `true` | MongoDB non è avviato — vai al passo 1 |
| `ollama` | `true` | LM Studio non è avviato — vai al passo 3 |

**Swagger UI** (documentazione interattiva): http://127.0.0.1:8765/docs

> Per lo sviluppo backend con ricarica automatica:
> ```powershell
> uvicorn aiura_legal.api.app:app --host 127.0.0.1 --port 8765 --reload
> ```

---

### 5. Frontend (React + Vite)

In un **secondo terminale** (l'API deve restare aperta nel primo):

```powershell
cd frontend
npm install        # solo la prima volta o dopo npm update
npm run dev
```

**Output:**
```
  VITE v8.0.12  ready in 312 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Apri il browser su: **http://localhost:5173**

Il frontend fa proxy automatico: chiamate a `/api/*` vengono inoltrate a `http://127.0.0.1:8765`.

---

## Riepilogo porte e URL

| Servizio | URL | Note |
|----------|-----|------|
| Frontend (React) | http://localhost:5173 | Dev server con HMR |
| API (FastAPI) | http://127.0.0.1:8765 | Backend principale |
| Swagger UI | http://127.0.0.1:8765/docs | Documentazione API interattiva |
| MongoDB | mongodb://localhost:27017 | Servizio Windows |
| LM Studio | http://127.0.0.1:1234 | App esterna |
| Qdrant (server) | http://localhost:6333 | Solo in server mode |

---

## Checklist avvio rapido

```
[ ] 1. Start-Service MongoDB          → PowerShell
[ ] 2. docker start qdrant            → se usi server mode
[ ] 3. LM Studio → Start Server       → GUI applicazione
[ ] 4. python -m aiura_legal.api      → terminale 1 (venv attivo)
[ ] 5. cd frontend && npm run dev     → terminale 2
[ ] 6. curl http://127.0.0.1:8765/health  → verifica tutto green
[ ] 7. http://localhost:5173          → apri browser
```

---

## Spegnimento

```powershell
# Terminale 1: Ctrl+C sull'API
# Terminale 2: Ctrl+C sul frontend

# Ferma MongoDB (opzionale, consuma poca RAM a riposo)
Stop-Service MongoDB

# Ferma Qdrant Docker (opzionale)
docker stop qdrant

# LM Studio: chiudi dall'icona nel taskbar
```

---

## Gestione memoria (importante)

Il sistema carica in RAM:
- **BM25 giurisprudenza**: ~2 GB (1,176,698 chunk)
- **Qdrant embedded**: ~1–2 GB (cache vettoriale)
- **LM Studio / modello**: 4–8 GB (dipende dal modello)
- **MongoDB**: ~256–512 MB

**RAM minima consigliata: 16 GB.** Con 8 GB, non eseguire mai BM25 rebuild +
build indexes + LM Studio contemporaneamente — rischio OOM crash MongoDB
(come successo stanotte con il gate script).

Se hai 8 GB:
1. Spegni LM Studio durante i rebuild degli indici
2. Esegui `build_indexes.py` e `build_jurisprudence_indexes.py` di notte, uno alla volta
3. Riavvia LM Studio dopo

---

## Configurazione `.env`

Il file `.env` nella root controlla tutti i parametri. Non committarlo mai su git.

```env
# Database
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=aiura_legal_lab_db

# LLM (scegli uno)
AIURA_LLM_BACKEND=lmstudio          # oppure: ollama
LMSTUDIO_BASE_URL=http://127.0.0.1:1234
LMSTUDIO_MODEL=qwen2.5-7b-instruct

# Qdrant
QDRANT_URL=http://localhost:6333    # vuoto = embedded

# API
AIURA_API_HOST=127.0.0.1
AIURA_API_PORT=8765

# Workspace e retrieval
AIURA_WORKSPACES_PATH=C:/project/AiUraLegalLab/workspaces
RETRIEVAL_TOP_K_RETRIEVE=20
RETRIEVAL_TOP_K_RERANK=6
```

Cambia modello LLM senza riavviare l'API: http://localhost:5173/settings

---

## Troubleshooting rapido

| Sintomo | Causa probabile | Soluzione |
|---------|----------------|-----------|
| `"mongodb": false` nell'health | MongoDB non avviato o crashato | `Start-Service MongoDB` (come Admin se serve) |
| `"ollama": false` nell'health | LM Studio non attivo | Apri LM Studio → Start Server |
| Frontend mostra errori CORS | API non attiva | Avvia `python -m aiura_legal.api` |
| BM25 ricarica a ogni query | `.pkl` mancante o corrotto | `python scripts/build_indexes.py --workspace mio-studio` |
| Qdrant "collection vuota" | Primo avvio o cambio mode | `python scripts/build_jurisprudence_indexes.py --workspace mio-studio --from-chunks` |
| OOM crash MongoDB | RAM esaurita durante operazioni pesanti | Riavvia PC, non eseguire rebuild+LLM in parallelo |
| Lock file MongoDB stale | Crash precedente | Elimina `mongod.lock` da Admin, riavvia servizio |
