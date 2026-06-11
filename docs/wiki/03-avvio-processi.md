# Avvio processi

## Mappa dei processi

| Processo | Script / Comando | Frequenza | Durata tipica |
|---------|-----------------|-----------|--------------|
| API principale | `python -m aiura_legal.api` | Continuo | — |
| Sync giurisprudenza | `sync_jurisprudence.py` | Settimanale | 5–15 min |
| Caricamento storico | `sync_jurisprudence.py --initial-load` | Una tantum | 30–60 min |
| Build indici (BM25+Vector) | `build_jurisprudence_indexes.py` | Dopo sync | 5–15 min |
| Grafo sentenza→norma | `build_jurisprudence_graph.py` | Dopo sync | 3–5 min |
| Update settimanale completo | `weekly_jurisprudence_update.py` | Settimanale | 20–40 min |
| Report knowledge base | `_kb_report.py` | On demand | 5 sec |
| Test retrieval E2E | `test_jurisprudence_retrieval.py` | On demand | 2 min |

---

## 1. API principale

```powershell
# Attiva venv (se non già attivo)
.venv\Scripts\activate

# Avvio standard
python -m aiura_legal.api

# Con reload automatico (sviluppo)
uvicorn aiura_legal.api.app:app --host 127.0.0.1 --port 8765 --reload
```

**Verifica:**
```powershell
curl http://127.0.0.1:8765/health
# → {"status":"ok","mongodb":true,"ollama":true,"version":"0.1.0.dev0"}
```

**Swagger UI interattivo:** http://127.0.0.1:8765/docs

**Log di avvio normale:**
```
INFO  | AiUra LegalLab API avviata
INFO  | MongoDB: connesso
INFO  | Wiki layer: inizializzato
INFO  | LLM backend: LMStudio  (http://127.0.0.1:1234  model=qwen2.5-7b-instruct)
INFO  | LMStudio: disponibile — modelli: [...]
```

> ⚠️ Se LMStudio non è attivo, l'API parte comunque ma risponde senza testo LLM (`llm_available=false`).

---

## 2. Sincronizzazione giurisprudenza

### 2.1 Aggiornamento settimanale (ultimi 7 giorni)

```powershell
python scripts/sync_jurisprudence.py
```

Scarica le sentenze degli ultimi 7 giorni da tutte le fonti attive
(Cassazione, TAR, Corte dei Conti). Corte Costituzionale è esclusa automaticamente.

### 2.2 Caricamento storico — da eseguire solo al primo setup

```powershell
# Carica gli ultimi 2 anni (100k+ sentenze)
python scripts/sync_jurisprudence.py --initial-load
```

Con `--initial-load`:
- Cassazione: usa `max_results=100_000` e `rate_limit=0.1s` → ~8 minuti
- TAR e CdC: usa la finestra temporale di 2 anni

### 2.3 Singola fonte

```powershell
python scripts/sync_jurisprudence.py --source cassazione
python scripts/sync_jurisprudence.py --source corte_conti
python scripts/sync_jurisprudence.py --source tar

# Con data esplicita
python scripts/sync_jurisprudence.py --source cassazione --since 2024-01-01

# Dry-run (simula senza scrivere)
python scripts/sync_jurisprudence.py --dry-run
```

### 2.4 Note per fonte

| Fonte | Meccanismo | Note |
|-------|-----------|------|
| **Cassazione** | Solr API diretta (httpx) | Più veloce, no Playwright |
| **TAR / CdS** | Playwright + Liferay portlet | 10 termini di ricerca, ~4 min/termine |
| **Corte dei Conti** | CdcWebApi REST + download PDF | ~1.5s/sentenza, ~300 pag scansionate |
| **Corte Cost.** | ❌ Bloccata da hCaptcha | Richiede servizio 2captcha |

**Problema noto — TAR:** il termine `annullamento` causa un hang di Playwright
dopo ~30 min. È presente un timeout di 5 min per termine che lo salta automaticamente.

---

## 3. Costruzione indici di ricerca

### 3.1 Indicizzazione giurisprudenza (append)

Aggiunge solo i documenti non ancora presenti nell'indice:

```powershell
python scripts/build_jurisprudence_indexes.py --workspace mio-studio
```

Output:
```
INFO  | Documenti giurisprudenza in MongoDB: 58,845  (filtro: nessuno)
INFO  | BM25 caricato: 102,684 doc
INFO  | Qdrant pronto
SUCCESS | Indicizzazione completata: 267 documenti → 435 chunk
```

### 3.2 Filtra per organo

```powershell
# Solo Cassazione
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione

# Solo Corte dei Conti
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo corte_conti
```

Organi disponibili: `cassazione` | `tar` | `consiglio_stato` | `corte_cost` | `corte_conti`

### 3.3 Rebuild completo da zero

```powershell
python scripts/build_jurisprudence_indexes.py --workspace mio-studio --rebuild
```

> ⚠️ Cancella BM25 e Qdrant esistenti prima di ricostruire.

### 3.4 Indicizzazione normattiva

```powershell
python scripts/build_indexes.py --workspace mio-studio
```

---

## 4. Grafo sentenza → norma

```powershell
# Costruisce o aggiorna il grafo
python scripts/build_jurisprudence_graph.py

# Ricostruisce da zero
python scripts/build_jurisprudence_graph.py --rebuild
```

Output: `workspaces/jurisprudence_graph.json`

Statistiche attuali:
- 58.845 nodi sentenza
- 61.852 nodi norma
- 733.598 archi

### Visualizzazione interattiva

```powershell
$env:NODE_PATH = "C:\Users\<utente>\AppData\Roaming\npm\node_modules"
python scripts/visualize_graph.py

# Personalizzata
python scripts/visualize_graph.py --top-norme 50 --sentenze-per-norma 10
```

Output: `workspaces/grafo_giurisprudenza.html` — apri nel browser.

---

## 5. Update settimanale completo (raccomandato)

Esegue sync + indicizzazione incrementale in un unico comando:

```powershell
python scripts/weekly_jurisprudence_update.py --workspace mio-studio

# Anteprima senza scrivere
python scripts/weekly_jurisprudence_update.py --workspace mio-studio --dry-run
```

Sequenza eseguita:
1. Sync giurisprudenza (ultimi 7 giorni, tutte le fonti)
2. Indicizzazione solo dei nuovi documenti
3. Salvataggio indici

---

## 6. Utilità

### Report knowledge base

```powershell
python scripts/_kb_report.py
```

Output:
```
══════════════════════════════════════════════════════════
  KNOWLEDGE BASE — Resoconto
══════════════════════════════════════════════════════════

1. NORMATTIVA  (sorgente: normattiva.it)
   Articoli totali:          166,822
   ...

2. GIURISPRUDENZA
   Sentenze totali:           58,845
   ...
```

### Test retrieval end-to-end

```powershell
python scripts/test_jurisprudence_retrieval.py --workspace mio-studio --verbose
```

Verifica 5 sezioni:
1. Conteggio documenti MongoDB per organo
2. Esistenza indici BM25 + Qdrant
3. 5 query di test su diversi intent
4. Citation Contract (test PASS e FAIL)
5. Statistiche grafo

### Genera golden test set per l'avvocato

```powershell
# 1. Assicurati che l'API sia attiva
python -m aiura_legal.api

# 2. Esegui le 10 query
python scripts/run_golden_test_v2.py

# 3. Genera documento Word
$env:NODE_PATH = "C:\Users\<utente>\AppData\Roaming\npm\node_modules"
node scripts/generate_golden_v2.js
```

Output: `docs/golden_test_set_v2_con_giurisprudenza.docx`

---

## 7. Ordine di avvio consigliato (primo setup)

```
1. Avvia MongoDB
2. Avvia LMStudio (carica modello qwen2.5-7b-instruct)
3. python scripts/migrate_to_aiura_legal_lab_db.py     # se DB non ancora migrato
4. python scripts/sync_jurisprudence.py --initial-load  # prima volta: 2 anni
5. python scripts/build_indexes.py --workspace mio-studio
6. python scripts/build_jurisprudence_indexes.py --workspace mio-studio
7. python scripts/build_jurisprudence_graph.py
8. python -m aiura_legal.api                            # avvia API
9. python scripts/test_jurisprudence_retrieval.py --workspace mio-studio
```
