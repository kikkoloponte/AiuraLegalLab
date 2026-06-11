# Costruzione della Knowledge Base da Zero
**AiUra LegalLab — Guida operativa completa**

---

## Panoramica

La knowledge base è composta da tre corpora distinti che confluiscono
negli stessi indici BM25 (per-corpus) + Qdrant:

| Corpus | Fonte | Documenti | Tempo download | Tempo indicizzazione |
|--------|-------|-----------|---------------|---------------------|
| **normattiva** | `legal_lab.normattiva_docs` (read-only) | ~166.800 | — già presenti | 2–4 ore |
| **giurisprudenza** | 4 fonti pubbliche (vedi sotto) | ~316.900 | 8–24 ore totali | 1–2 ore |
| **studio** | upload avvocato via `/ingest` | variabile | — | automatico |

---

## Prerequisiti

```bash
.venv\Scripts\activate
python -c "from aiura_legal.ingestion.mongodb.client import MongoClient; print('MongoDB OK')"
```

`.env` necessario:
```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=aiura_legal_lab_db
AIURA_WORKSPACES_PATH=workspaces
```

---

## STRUTTURA DEI DOCUMENTI

Prima di eseguire qualsiasi script è utile capire cosa viene scaricato
e come ogni fonte contribuisce al retrieval.

---

### Normattiva (`legal_lab.normattiva_docs`)

**Origine:** LegalAgentLab, già presente localmente — **non scaricare**.

```
_id            ObjectId
urn            "urn:nir:stato:legge:1990-08-07;241~art1"   ← URN univoco articolo
act_urn        "urn:nir:stato:legge:1990-08-07;241"        ← URN atto padre
titolo         "LEGGE 7 agosto 1990, n. 241"
titolo_articolo "(Principi generali dell'attività amministrativa)"
articolo_num   "Art. 1"
text           "La Camera dei deputati..."                  ← testo completo articolo
testo_tipo     "normativo" | "formula" | "formula_ridondante" | "formula_unica"
doc_type       "LEGGE" | "DLGS" | "DPR" | "DL" | ...
source_id      "normattiva_it"
anno           1990
data_inizio_vigenza  "20200915"
```

**Chunk generato:** 1 chunk per articolo, con snippet = `text[:300]`.
Il campo `testo_tipo` filtra le formule ridondanti a build-time.

**Copertura:** Leggi, decreti legislativi, DPR, regolamenti — dal 1948
a oggi. Aggiornamento automatico da normattiva.it (gestito da LegalAgentLab).

---

### Cassazione (`source_channel = scraping`)

**Origine:** API Solr `italgiure.giustizia.it`. Testo integrale della
sentenza estratto da HTML.

```
_id            "e1e91293f059fbe6"   ← SHA-256[:16] di "cassazione:numero:anno"
organo         "cassazione"
numero         "1"
anno           2021
data_deposito  "2022-01-04"
sezione        "Sez. 6"
materia        ""                   ← vuoto (~0% compilato)
massima        ""                   ← vuoto (~0% compilato)
motivazione    "0/2020 n. 137..."   ← testo integrale (100% compilato)
dispositivo    "Accoglie il..."     ← dispositivo finale (75% compilato)
norme_citate   ["art. 23", "art. 37 bis d.", ...]
source_url     "https://italgiure.giustizia.it/..."
source_channel "scraping"
```

**Chunk generati:** fino a 2 chunk per sentenza (`motivazione` + `dispositivo`).
La `massima` è vuota perché non disponibile nell'API pubblica.

**Qualità campi:**

| Campo | Compilato |
|-------|-----------|
| motivazione | ~100% |
| dispositivo | ~75% |
| massima | 0% |
| materia | 0% |

**Copertura:** ~249.000 sentenze civili, penali, lavoro (2020–2026).
Storico più profondo disponibile ma richiede credenziali premium.

---

### TAR + Consiglio di Stato (`source_channel = open_data`)

**Origine:** OpenGA CKAN API (`openga.giustizia-amministrativa.it`).
Solo metadati CSV — niente testo della motivazione.

```
_id             "tar_202400001_2024"   ← "{organo}_{numero}_{anno}"
organo          "tar" | "consiglio_stato"
numero          "202400001"
anno            2024
data_deposito   "2024-01-16"
sezione         "SEZIONE I"
nome_sede       "CGA GIURISDIZIONALE - PALERMO"
materia         "PROCEDURA APERTA PER L'AFFIDAMENTO..."  ← oggetto ricorso (100%)
massima         "PROCEDURA APERTA..."                    ← = materia (100%)
motivazione     ""                                        ← non disponibile (0%)
dispositivo     "RESPINGE" | "ACCOGLIE" | ...             ← esito (100%)
tipo_provvedimento  "SENTENZA" | "ORDINANZA"
source_channel  "open_data"
```

**Chunk generati:** 1–2 chunk per sentenza (`massima/materia` + `dispositivo`).
La motivazione è assente — OpenGA non la pubblica in bulk.

**Qualità campi:**

| Campo | Compilato |
|-------|-----------|
| massima (= materia) | ~100% |
| dispositivo (esito) | ~100% |
| motivazione | 0% |

**Copertura:** ~44.800 sentenze (2020–2026) di tutti i 29 TAR italiani
+ CdS. Anni precedenti non disponibili su OpenGA.

> ⚠️ Il testo della motivazione (ragionamento giuridico) non è indicizzato
> per questa fonte. Per sentenze TAR con motivazione completa è necessario
> scraping puntuale via `giustizia_amm.py` (soggetto a timeout).

---

### Corte Costituzionale (`source_channel = open_data`)

**Origine:** Archivi ZIP scaricati da `dati.cortecostituzionale.it`.
Struttura XML con testo completo + massime separate.

```
_id            "corte_cost_1_1956"   ← "corte_cost_{numero}_{anno}"
organo         "corte_cost"
numero         "1"
anno           1956
data_deposito  "1956-06-14"
ecli           "ECLI:IT:COST:1956:1"
presidente     "DE NICOLA"
relatore       "Gaetano Azzariti"
tipo_pronuncia "S"  (S=Sentenza, O=Ordinanza, D=Decreto)
materia        "Sentenza"
massima        "SENT. 1/56 A. GIUDIZIO DI LEGITTIMITÀ..."  ← testo massima (100%)
motivazione    "LA CORTE COSTITUZIONALE composta..."       ← testo completo (100%)
dispositivo    "per questi motivi..."                      ← dispositivo (100%)
source_url     "https://cortecostituzionale.it/scheda-pronuncia/1956/1"
source_channel "open_data"
```

**Chunk generati:** fino a 3 chunk per pronuncia (`massima` + `motivazione` + `dispositivo`).

**Qualità campi:**

| Campo | Compilato |
|-------|-----------|
| massima | ~100% |
| motivazione | ~100% |
| dispositivo | ~100% |
| materia | ~100% |

**Copertura:** ~22.300 pronunce dal 1956 a oggi (sentenze + ordinanze).
La qualità testuale è eccellente — fonte ideale per questioni di legittimità.

---

### Corte dei Conti (`source_channel = scraping`)

**Origine:** API CdcWebApi (`corteconti.it`). Testo parziale estratto
da PDF (OCR).

```
_id            "b66c4776a71f815f"   ← SHA-256[:16]
organo         "corte_conti"
numero         "1"
anno           2026
data_deposito  "2026-01-20"
sezione        "SEZIONE GIURISDIZIONALE PER..."
materia        ""                   ← raramente compilato
massima        ""                   ← raramente compilato
motivazione    "articolata, coerente..."  ← testo parziale (18% compilato)
dispositivo    "La Corte dei Conti..."    ← disponibile (23% compilato)
norme_citate   ["art. 640 c.", ...]
source_url     "https://corteconti.it/..."
source_channel "scraping"
```

**Chunk generati:** 0–2 chunk per sentenza (molti documenti hanno campi vuoti).

**Qualità campi:**

| Campo | Compilato |
|-------|-----------|
| motivazione | ~18% |
| dispositivo | ~23% |
| massima | ~2% |
| materia | 0% |

**Copertura:** ~267 sentenze (2025–2026). La copertura storica è limitata
dalla qualità dei PDF e dai limiti dell'API (500 PDF/run).

---

### Come i documenti diventano Chunk

`coordinator.py::to_chunks()` trasforma ogni `JurisprudenceDocument` in
fino a **3 chunk**, uno per campo testuale non vuoto:

```
Documento → [chunk_massima, chunk_motivazione, chunk_dispositivo]
                ↓                  ↓                   ↓
         se massima.strip()   se motiv.strip()   se disp.strip()
```

Ogni chunk ha:
```python
Document(
    id          = f"{doc.id}_{chunk_type}",   # es. "e1e91293_motivazione"
    text        = <testo del campo>,
    metadata    = {
        "corpus":     "giurisprudenza",
        "chunk_type": "massima"|"motivazione"|"dispositivo",
        "jdoc_id":    "<id doc padre>",
        "organo":     "cassazione"|"tar"|...,
        "numero":     "34311",
        "anno":       2023,
        "materia":    "<oggetto>",
    },
    source_id   = f"giurisprudenza_{organo}_{numero}_{anno}",
    valid_from  = data_deposito,
)
```

---

## FASE 1 — Download Giurisprudenza

### 1A. Cassazione

```bash
python scripts/sync_jurisprudence.py --initial-load --source cassazione
```

- **Metodo:** API Solr `italgiure.giustizia.it` — POST JSON, no browser
- **Limite pubblico:** 5.000 sentenze/settimana per IP
- **Con `--initial-load`:** alza il cap a 100.000, copre ~5 anni
- **Tempo stimato:** 8–16 ore (dipende da rate limiting server)
- **Se interrotto:** idempotente, si può rilanciare — salta le già presenti
- **Storico completo:** richiede più run settimanali; per 249K sentenze
  stimate ~6 mesi di sync settimanale da zero

> 💡 In alternativa: esegui in background con `nohup` e monitora il log.

### 1B. TAR + Consiglio di Stato

```bash
python scripts/import_openga.py --from-year 2020
```

- **Metodo:** CKAN REST API — download CSV diretto, no browser, no limiti
- **Tempo stimato:** 15–30 minuti (31 dataset × ~2 anni × CSV download)
- **Copertura:** 2023–2026 di default; `--from-year 2020` estende ma
  OpenGA non ha anni precedenti al 2023 per molti TAR
- **Idempotente**

### 1C. Corte Costituzionale

**Step 1 — Download manuale** (una tantum, ~200 MB totali):
1. Apri **https://dati.cortecostituzionale.it/Scarica_i_dati/Scarica_i_dati**
2. Scarica i 6 ZIP in `download/`:
   - `CC_OpenPronunce_1956_1980.zip`, `CC_OpenPronunce_1981_2000.zip`, `CC_OpenPronunce_2001_oggi.zip`
   - `CC_OpenMassime_1956_1980.zip`, `CC_OpenMassime_1981_2000.zip`, `CC_OpenMassime_2001_oggi.zip`

**Step 2 — Import:**
```bash
python scripts/import_corte_cost.py
```

- **Tempo:** 1–2 minuti (22.300 pronunce XML già sul disco)
- **Idempotente**

### 1D. Corte dei Conti

```bash
python scripts/sync_jurisprudence.py --since 2020-01-01 --source corte_conti
```

- **Metodo:** API `corteconti.it` — scarica e OCR i PDF
- **Cap di sicurezza:** 500 PDF/run (impostato in `corte_conti.py`)
- **Tempo per run:** 1–3 ore (OCR dei PDF è lento)
- **Per coprire 2020–oggi:** esegui più volte con date progressive
- **Nota:** qualità del testo estratto bassa (~18–23% campi compilati)

---

## FASE 2 — Verifica MongoDB

```bash
python -c "
from pymongo import MongoClient
from aiura_legal.ingestion.mongodb.client import settings
c = MongoClient(settings.mongodb_uri)
db = c[settings.mongodb_database]
for org in ['cassazione','tar','consiglio_stato','corte_conti','corte_cost']:
    n = db.jurisprudence.count_documents({'organo': org})
    print(f'  {org}: {n:,}')
print(f'  TOTALE: {db.jurisprudence.count_documents({}):,}')
"
```

Stato attuale (riferimento):
```
cassazione:      249.468
tar:              30.094
consiglio_stato:  14.729
corte_conti:         267
corte_cost:       22.331
TOTALE:          316.889
```

---

## FASE 3 — Costruzione Indici

> ⚠️ **Ordine obbligatorio:** `build_indexes.py` prima,
> `index_jurisprudence.py` dopo. Il secondo fa append all'indice esistente.

### 3A. Indice Normattiva

```bash
python scripts/build_indexes.py --workspace mio-studio
```

- Legge `aiura_legal_lab_db.chunks` (corpus=normattiva)
- Costruisce BM25 per-corpus (`bm25_<corpus>.pkl`) + Qdrant
- **Tempo stimato: 2–4 ore**
- Output: `workspaces/mio-studio/indices/`

### 3B. Indice Giurisprudenza

```bash
python scripts/index_jurisprudence.py --workspace mio-studio
```

- Legge `aiura_legal_lab_db.jurisprudence` (~316K doc → ~700K chunk)
- Accumula tutti in RAM → **una sola** BM25Okapi build
- **Tempo stimato: 1–2 ore** (build BM25 + Qdrant batch 2000)
- RAM necessaria: ~4–8 GB durante la build
- Idempotente

---

## FASE 4 — Migrazione Indici History

```bash
python scripts/migrate_history_indexes.py
```

Crea 5 indici ottimizzati su `query_history`. Tempo: pochi secondi.
Idempotente.

---

## FASE 5 — Avvio API

```bash
python -m aiura_legal.api
```

All'avvio il **warm-up indici** parte automaticamente in background:
carica HNSW (Qdrant) e il modello di embedding in RAM (~20s). Le query successive saranno veloci.

---

## Aggiornamento Settimanale

```bash
# Cassazione: nuove sentenze degli ultimi 7 giorni (default)
python scripts/sync_jurisprudence.py --source cassazione

# Corte dei Conti
python scripts/sync_jurisprudence.py --source corte_conti

# TAR+CdS (OpenGA aggiorna mensilmente)
python scripts/import_openga.py --from-year 2025

# Re-indicizza solo le nuove sentenze (append)
python scripts/index_jurisprudence.py --workspace mio-studio
```

Corte Costituzionale: re-scarica i ZIP quando il sito pubblica
aggiornamenti (~trimestrale) e riesegui `import_corte_cost.py`.

---

## Riepilogo Ordine Completo (da zero)

```
STEP  COMANDO                                                    DURATA STIMATA
────  ────────────────────────────────────────────────────────  ──────────────
 1    sync_jurisprudence.py --initial-load --source cassazione   8–16 ore
 2    import_openga.py --from-year 2020                         15–30 min
 3    [download ZIP manuale → download/]                         manuale
      import_corte_cost.py                                       1–2 min
 4    sync_jurisprudence.py --since 2020-01-01 --source          1–3 ore
        corte_conti                                              (per run)
 5    [verifica MongoDB: ~316K sentenze]                         —
 6    build_indexes.py --workspace mio-studio                    2–4 ore
 7    index_jurisprudence.py --workspace mio-studio              1–2 ore
 8    migrate_history_indexes.py                                 < 1 min
 9    python -m aiura_legal.api                                  —
────  ────────────────────────────────────────────────────────  ──────────────
      TOTALE (escl. Cassazione storico)                          ~8–10 ore
```

> **Nota sul tempo Cassazione:** il limit di 5.000 sentenze/settimana
> dell'API pubblica significa che le 249K sentenze attuali hanno richiesto
> mesi di sync incrementale. Da zero con `--initial-load` si ottengono le
> ultime ~100K sentenze (~5 anni) in 8–16 ore; lo storico più profondo
> richiede run settimanali ripetuti.

---

## Troubleshooting

### "0 sentenze indicizzate — già presenti"
I documenti in MongoDB non vengono chunckizzati.
Causa: `source_channel` non riconosciuto dall'enum `SourceChannel`.
Verifica `aiura_legal/jurisprudence/models.py`:
```python
class SourceChannel(str, Enum):
    SCRAPING     = "scraping"
    UPLOAD_STUDIO = "upload_studio"
    OPEN_DATA    = "open_data"   # ← deve esserci
```

### "BM25: indice vuoto" in index_jurisprudence.py
`build_indexes.py` non è stato eseguito ancora (o i file sono stati
cancellati). Eseguire prima la fase 3A.

### "Prima query lenta (~20s, cold start)"
Normale alla prima query dopo riavvio API. Il warm-up automatico lo
pre-carica all'avvio — le query successive sono ~1.4s.

### Ripartire da zero (rebuild indici)
```bash
# Ferma l'API
del workspaces\mio-studio\indices\bm25.pkl
del workspaces\mio-studio\indices\bm25.pkl.bak
del workspaces\mio-studio\indices\bm25_meta.json
del workspaces\mio-studio\indices\bm25_meta.json.bak
rmdir /s /q workspaces\mio-studio\indices\qdrant

# Ricostruisci (fasi 3A + 3B)
python scripts/build_indexes.py --workspace mio-studio
python scripts/index_jurisprudence.py --workspace mio-studio
```

---

## Dimensioni di riferimento (stato attuale)

| Risorsa | Dimensione |
|---------|-----------|
| `bm25_<corpus>.pkl` | ~2.7 GB totali |
| `bm25_meta.json` | ~85 MB |
| Qdrant (embedded `qdrant/` o server) | ~1–2 GB |
| `graph.json` | ~78 MB |
| MongoDB `jurisprudence` | ~5 GB |
| MongoDB `normattiva_docs` | ~800 MB |
| RAM durante index build | 4–8 GB |

---

*Ultima revisione: 2026-06-05*
