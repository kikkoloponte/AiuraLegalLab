# Installazione e configurazione

## Prerequisiti

| Componente | Versione minima | Obbligatorio | Note |
|-----------|----------------|-------------|------|
| Python | 3.11+ | ✅ | Testato con 3.14 su Windows 11 |
| MongoDB | 6.0+ | ✅ | Locale su `localhost:27017` |
| Node.js | 18+ | ⚠️ | Solo per generazione documenti Word |
| LMStudio | qualsiasi | ✅* | Backend LLM consigliato (locale) |
| Ollama | qualsiasi | ✅* | Alternativa a LMStudio |
| Playwright | auto | ⚠️ | Solo per scraping TAR (Giustizia Amministrativa) |

> \* Almeno uno tra LMStudio e Ollama deve essere attivo.

---

## 1. Installazione Python

### 1.1 Clona il repository

```bash
cd C:\project
# già presente — il repo è in C:\project\AiUraLegalLab
```

### 1.2 Crea virtual environment e installa dipendenze

```powershell
cd C:\project\AiUraLegalLab
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

Il flag `.[dev]` installa anche le dipendenze di sviluppo (pytest, mypy, ruff).

### 1.3 Scarica il modello spaCy italiano

Necessario per l'anonimizzazione PII (Tier1Pipeline):

```powershell
python -m spacy download it_core_news_lg
```

### 1.4 Installa Playwright (solo per scraping TAR)

```powershell
playwright install chromium
```

---

## 2. Configurazione `.env`

Crea o modifica il file `.env` nella root del progetto (`C:\project\AiUraLegalLab\.env`):

```env
# ── MongoDB — database unificato ─────────────────────────────────────────
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=aiura_legal_lab_db

# Normattiva (ora nello stesso DB unificato)
LEGALAGENTLAB_MONGODB_URI=mongodb://localhost:27017
LEGALAGENTLAB_MONGODB_DATABASE=aiura_legal_lab_db
LEGALAGENTLAB_CHUNKS_COLLECTION=normattiva_docs
LEGALAGENTLAB_TEXT_FIELD=text

# ── LLM Backend ───────────────────────────────────────────────────────────
# Scegli "lmstudio" oppure "ollama"
AIURA_LLM_BACKEND=lmstudio

# LMStudio (backend OpenAI-compatibile — consigliato)
LMSTUDIO_BASE_URL=http://127.0.0.1:1234
LMSTUDIO_MODEL=qwen2.5-7b-instruct

# Ollama (alternativo)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_MAIN=qwen2.5:7b

# ── Percorsi ──────────────────────────────────────────────────────────────
AIURA_WORKSPACES_PATH=C:/project/AiUraLegalLab/workspaces

# ── API ───────────────────────────────────────────────────────────────────
AIURA_API_HOST=127.0.0.1
AIURA_API_PORT=8765

# ── Log ───────────────────────────────────────────────────────────────────
LOG_LEVEL=INFO
```

---

## 3. Node.js (generazione documenti Word)

Usato dagli script `scripts/generate_*.js`:

```powershell
npm install -g docx
```

Per eseguire gli script `.js`, impostare `NODE_PATH`:

```powershell
$env:NODE_PATH = "C:\Users\<utente>\AppData\Roaming\npm\node_modules"
node scripts/generate_golden_v2.js
```

---

## 4. MongoDB — primo avvio

Se il database `aiura_legal_lab_db` non esiste ancora:

```powershell
# Verifica che MongoDB sia in esecuzione
mongosh --eval "db.adminCommand('ping')"

# La migrazione crea il database e copia i dati
python scripts/migrate_to_aiura_legal_lab_db.py --dry-run   # anteprima
python scripts/migrate_to_aiura_legal_lab_db.py             # esecuzione
```

La migrazione copia:
- `legal_lab.normattiva_docs` → `aiura_legal_lab_db.normattiva_docs` (166.822 doc)
- `aiura_legal.jurisprudence` → `aiura_legal_lab_db.jurisprudence` (58.845 doc)
- `aiura_legal.sync_state` → `aiura_legal_lab_db.sync_state` (4 doc)

---

## 5. Costruzione indici (primo avvio)

Gli indici BM25 e Qdrant **non vengono creati automaticamente** — vanno costruiti
esplicitamente. Questo è necessario solo la prima volta o dopo un rebuild.

### Indici normattiva + giurisprudenza

```powershell
# Workspace "mio-studio" (crea la cartella se non esiste)
python scripts/build_indexes.py --workspace mio-studio
python scripts/build_jurisprudence_indexes.py --workspace mio-studio
```

Stima tempo: ~15-20 minuti (BM25 + Qdrant su 225k documenti totali).

Output in `workspaces/mio-studio/indices/`:
```
indices/
├── bm25.pkl           (~700 MB)
├── bm25_meta.json
└── qdrant/   (oppure Qdrant server via QDRANT_URL)
    ├── chroma.sqlite3 (~2.9 GB)
    └── ...
```

### Grafo sentenza → norma

```powershell
python scripts/build_jurisprudence_graph.py
```

Output: `workspaces/jurisprudence_graph.json`

---

## 6. Verifica installazione

```powershell
# 1. Avvia API
python -m aiura_legal.api

# 2. In un altro terminale, verifica health
curl http://127.0.0.1:8765/health
# → {"status":"ok","mongodb":true,"ollama":true,"version":"0.1.0.dev0"}

# 3. Test retrieval end-to-end
python scripts/test_jurisprudence_retrieval.py --workspace mio-studio --verbose
```

---

## 7. Esegui i test

```powershell
# Tutti i test (usa mongomock-motor — nessun MongoDB reale necessario)
pytest tests/ -v

# Solo giurisprudenza
pytest tests/test_jurisprudence_models.py tests/test_jurisprudence_parser.py -v

# Con coverage
pytest tests/ --cov=aiura_legal --cov-report=term-missing
```

> ⚠️ I test usano `mongomock-motor` — non modificano mai il database reale.

---

## 8. Linting e type check

```powershell
ruff check aiura_legal/
mypy aiura_legal/ --ignore-missing-imports
```
