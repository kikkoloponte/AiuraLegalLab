# Sorgenti della conoscenza

## Database unificato: `aiura_legal_lab_db`

Tutte le sorgenti confluiscono in un unico database MongoDB.
Nessun dato viene scritto su `legal_lab` (read-only originale).

```
aiura_legal_lab_db
├── normattiva_docs     166.822 doc   ← normativa italiana (LegalAgentLab, read-only)
├── jurisprudence       316.889 doc   ← sentenze pubbliche (Cassazione, TAR, CdS, CC, CdC)
├── documents             ~30 doc    ← documenti studio + dottrina (post-ingestione)
├── chunks             ~295.000 doc  ← chunk indicizzati (normattiva + dottrina)
│   corpus breakdown:
│     normattiva:    557.368 (indice BM25/Qdrant)
│     dottrina:      ~20.000 (fascicoli DPC 2017-2019)
│     giurisprudenza: 0      (build con build_jurisprudence_indexes.py)
├── wiki_pages                0 doc   ← risposte archiviate (si popola dopo query)
└── sync_state                5 doc   ← cursori last_sync per fonte
```

---

## 1. Normattiva

### Origine

Portale ufficiale [normattiva.it](https://www.normattiva.it) — testi normativi italiani
in formato Akoma Ntoso (AKN). Gestito dal Governo italiano (IPZS).

### Schema documento

```json
{
  "_id": "ObjectId",
  "text": "Articolo 2043. (Risarcimento per fatto illecito) ...",
  "urn": "urn:nir:stato:regio.decreto:1930-10-19;1398~art2043",
  "titolo": "REGIO DECRETO 19 ottobre 1930, n. 2669",
  "titolo_articolo": "Art. 2043",
  "articolo_num": "Art. 2043",
  "testo_tipo": "normativo",
  "source_id": "normattiva_it"
}
```

### Tipi documento (`testo_tipo`)

| Tipo | Descrizione | Quantità |
|------|------------|---------|
| `normativo` | Articolo di legge vero e proprio | 150.264 |
| `formula` | Disposizione breve, tabella, allegato | 13.375 |
| `formula_ridondante` | Testo duplicato da altra norma | 328 |
| `formula_unica` | Formula non ripetuta | 221 |

### Copertura

Oltre 374 leggi/atti distinti campionati (il totale nel DB è molto maggiore).
Include: Codice Civile, Codice Penale, Codice di Procedura Civile e Penale,
TUIR, D.Lgs. 231/2001, D.Lgs. 74/2000, e centinaia di altri.

### Aggiornamento

Il DB originale (`legal_lab.normattiva_docs`) è gestito da LegalAgentLab.
La copia in `aiura_legal_lab_db.normattiva_docs` è statica.

Per aggiornare:
```powershell
# Fetch nuovi documenti da normattiva.it
python scripts/fetch_normattiva.py

# Oppure ri-esegui la migrazione dopo un aggiornamento di legal_lab
python scripts/migrate_to_aiura_legal_lab_db.py
```

---

## 2. Giurisprudenza

### Panoramica fonti

| Organo | Documenti | Meccanismo | Anni |
|--------|-----------|-----------|------|
| **Cassazione** | 249.468 | Solr API diretta + backfill mensile | 2020–2026 |
| **TAR** | 30.094 | OpenGA CKAN API (CSV) — 31 dataset | 2023–2026 |
| **Consiglio di Stato** | 14.729 | OpenGA CKAN API (CSV) | 2023–2026 |
| **Corte dei Conti** | 267 | CdcWebApi REST + PDF | 2024–2026 |
| **Corte Costituzionale** | 22.331 | Open data ZIP (dati.cortecostituzionale.it) | 1956–oggi |
| **Totale** | **316.889** | — | 1956–2026 |

### Schema documento

```json
{
  "_id": "dc2b193a50bbba2f",
  "organo": "cassazione",
  "numero": "12345",
  "anno": 2025,
  "data_deposito": "2025-03-15",
  "sezione": "I Civile",
  "massima": "Il nesso causale deve essere provato...",
  "motivazione": "FATTO E DIRITTO\n...",
  "dispositivo": "P.Q.M.\nLa Corte...",
  "norme_citate": ["art. 2043 c.c.", "art. 360 c.p.c."],
  "sentenze_citate": [],
  "source_url": "https://www.italgiure.giustizia.it/...",
  "is_anonymized": false,
  "source_channel": "SCRAPING",
  "ingested_at": "2026-06-01T..."
}
```

L'`_id` è `sha256(organo:numero:anno)[:16]` — garantisce deduplicazione deterministica.

### Cassazione — dettaglio tecnico

- **URL Solr**: `https://www.italgiure.giustizia.it/sncass/`
- **Meccanismo**: POST JSON all'API Solr, 20 risultati/pagina, finestre mensili
- **Rate limit sync settimanale**: 1.5s/pagina
- **Rate limit backfill**: 0.1s/pagina, 4 mesi in parallelo (~3 min/anno)
- **Limit deep pagination**: il Solr wrappa dopo ~58k offset su query aperta.
  Soluzione: finestre mensili chiuse `datdec:[YYYYMMDD TO YYYYMMDD]` con `sort: datdec asc`
- **Watermark backfill**: `sync_state.source = "cassazione_backfill"` — riprende dall'interruzione
- **Scraper**: `aiura_legal/jurisprudence/scrapers/cassazione.py`

```python
# Sync settimanale (finestra aperta)
async with CassazioneScraper() as s:
    results = await s.fetch_since(date(2024, 1, 1))

# Backfill storico (finestra chiusa mensile)
async with CassazioneScraper() as s:
    results = await s.fetch_since(date(2024, 1, 1), until=date(2024, 1, 31))
```

```powershell
# Backfill parallelo (4 mesi concorrenti)
python scripts/backfill_cassazione.py --from 2020-01-01 --to 2024-12-31
# Riprendi da watermark dopo interruzione
python scripts/backfill_cassazione.py
```

### TAR / Consiglio di Stato — dettaglio tecnico

**Canale primario — OpenGA CKAN API (consigliato)**

- **URL**: `https://openga.giustizia-amministrativa.it/api/3/action`
- **Meccanismo**: download CSV diretto tramite CKAN API — nessun browser, no Playwright
- **Copertura**: 31 dataset (tutti i TAR d'Italia + Consiglio di Stato + TRGA Bolzano/Trento)
- **Anni disponibili**: 2023–2026, aggiornamento mensile
- **Script**: `scripts/import_openga.py`

```powershell
# Import completo (tutti i dataset, tutti gli anni)
python scripts/import_openga.py

# Solo dal 2022 in poi
python scripts/import_openga.py --from-year 2022

# Solo Consiglio di Stato
python scripts/import_openga.py --dataset cds-sentenze

# Dry-run (conta senza salvare)
python scripts/import_openga.py --dry-run
```

**Canale alternativo — Playwright (Liferay portlet)**

- **URL**: `https://www.giustizia-amministrativa.it/web/guest/dcsnprr`
- **Meccanismo**: Playwright + Liferay portlet, 10 termini di ricerca
- **Problema noto**: il termine `annullamento` causa hang di Playwright dopo ~30 min. Il timeout di 5 min lo salta automaticamente.
- **Scraper**: `aiura_legal/jurisprudence/scrapers/giustizia_amm.py`

```python
async with GiustiziaAmmScraper() as s:
    results = await s.fetch_since(date(2024, 1, 1))
```

### Corte dei Conti — dettaglio tecnico

- **URL**: `https://www.corteconti.it/Home/Documenti/Sentenze`
- **Meccanismo**: REST API (`/DesktopModules/CdcWebApi/API/document/Search`) + download PDF
- **Filtro titolo**: regex `^(Sentenza|Ordinanza|Decreto|Decisione)\s+n\.?\s*\d+` — esclude ruoli udienza, concorsi, comunicati
- **Rate limit**: 0.3s/scan pagina + 1.5s/download PDF
- **PDF**: ogni sentenza è disponibile solo come PDF — viene scaricato e parsato con `pdfplumber`
- **Scraper**: `aiura_legal/jurisprudence/scrapers/corte_conti.py`

```python
# Filtra automaticamente per tipo documento, scarica PDF
async with CorteContiScraper() as s:
    results = await s.fetch_since(date(2024, 1, 1))
```

### Corte Costituzionale — open data

Il portale cortecostituzionale.it era bloccato da hCaptcha. Ora viene usato il
canale **open data ufficiale** su `dati.cortecostituzionale.it`.

- **Archivi disponibili**: ZIP per fascette temporali (1956–1980, 1981–2000, 2001–oggi)
- **Contenuto**: pronunce (sentenze + ordinanze) e massime in formato XML Akoma Ntoso
- **Documenti importati**: **22.331** (copertura 1956–oggi)
- **Script**: `scripts/import_corte_cost.py`

**Struttura attesa in `download/`:**
```
download/
├── CC_OpenPronunce_1956_1980.zip
├── CC_OpenPronunce_1981_2000.zip
├── CC_OpenPronunce_2001_oggi.zip
├── CC_OpenMassime_1956_1980.zip
├── CC_OpenMassime_1981_2000.zip
└── CC_OpenMassime_2001_oggi.zip
```

**Comandi import:**
```powershell
# Import completo
python scripts/import_corte_cost.py

# Solo dal 2000 in poi
python scripts/import_corte_cost.py --from-year 2000

# Solo sentenze (salta ordinanze)
python scripts/import_corte_cost.py --only-sentenze

# Dry-run (statistiche senza salvare)
python scripts/import_corte_cost.py --dry-run
```

### Grafo sentenza → norma

Il `JurisprudenceGraphBuilder` costruisce un grafo NetworkX DiGraph durante l'ingestione:

```
Nodo sentenza (tipo="sentenza")
  └── archi: interpreta / applicata_in / cita
        └── Nodo norma (tipo="norma", urn="urn:nir:...")
```

Statistiche attuali (da ricostruire dopo import OpenGA + Corte Cost.):
- **316.889+** nodi sentenza
- **61.852+** nodi norma (stima — rebuild necessario)
- **733.598+** archi totali (stima — rebuild necessario)
- Top norma citata: `art. 360`

```powershell
# Ricostruisce il grafo dopo un backfill
python scripts/build_jurisprudence_graph.py --rebuild
```

---

## 3. Prassi amministrativa (Agenzia delle Entrate)

### Panoramica

| Tipo | Documenti | Anni | Rilevanza |
|------|-----------|------|-----------|
| **Circolari AdE** | ~115 | 2021–2026 | ★★★★★ penale tributario |
| **Risoluzioni AdE** | ~20 | 2026 | ★★★★☆ interpretazione IVA/IRPEF |

### Meccanismo

- **URL**: `https://www.agenziaentrate.gov.it/portale/web/guest/normativa-e-prassi/`
- **Portale**: Liferay 7 — Asset Publisher paginato, SSR (no Playwright)
- **Paginazione**: `?p_p_id=<portlet>&_<portlet>_cur=N&_<portlet>_delta=20`
- **Portlet circolari**: `AssetPublisherPortlet_INSTANCE_mFmHL8QS3lq4`
- **Portlet risoluzioni**: `AssetPublisherPortlet_INSTANCE_oF14ixF85x6o`
- **Download**: PDF diretto `/portale/documents/<group>/<folder>/<filename>.pdf`
- **Parser**: `pdfplumber` → testo + regex norme citate
- **Scraper**: `aiura_legal/prassi/scrapers/agenzia_entrate.py`

### Schema documento

```json
{
  "_id": "sha256(emittente:tipo:numero:anno)[:16]",
  "tipo": "circolare",
  "emittente": "agenzia_entrate",
  "numero": "2",
  "anno": 2026,
  "data_emissione": "2026-02-24",
  "titolo": "Circolare n. 2 del 24 febbraio 2026",
  "testo": "OGGETTO: Novità sulla tassazione...",
  "norme_citate": ["art. 51 TUIR", "art. 2 D.Lgs. 74/2000"],
  "source_url": "https://www.agenziaentrate.gov.it/...",
  "pdf_url": "https://www.agenziaentrate.gov.it/portale/documents/..."
}
```

### Sync prassi

```powershell
# Caricamento storico dal 2020
python scripts/sync_prassi.py --since 2020-01-01

# Solo circolari
python scripts/sync_prassi.py --tipo circolare

# Aggiornamento settimanale (ultimi 30 giorni)
python scripts/sync_prassi.py
```

---

## 4. Dottrina giuridica

### Panoramica

Manuali, articoli accademici e commentari caricati come corpus `dottrina`.
Usati nella **Fase 2 — INTERPRETAZIONE** del Sequential IQRAC a supporto
dei criteri ermeneutici (Canestrari su dolo, Fiandaca su reato, ecc.).

### Fonti open access indicizzate

| Fonte | Area | PDF stimati | Script |
|-------|------|------------|--------|
| **Archivio DPC** (2010-2019) | Penale sostanziale e processuale | ~31 fascicoli | `sync_dottrina.py` |
| **DPC Rivista Trimestrale** (2019-oggi) | Penale | ~300 articoli | `sync_dottrina.py` |
| **Federalismi.it** | Pubblico, costituzionale, europeo | ~500 articoli | `sync_dottrina.py` |
| **Diritti Fondamentali** | Diritti fondamentali, CEDU | ~200 articoli | `sync_dottrina.py` |
| **Questione Giustizia** | Processo penale e civile | ~150 articoli | `sync_dottrina.py` |
| **PDF manuali** | Qualsiasi materia | illimitato | `/ingest` |

### Comandi

```powershell
# Scarica PDF open access (senza API)
python scripts/sync_dottrina.py --no-upload

# Solo penale (DPC)
python scripts/sync_dottrina.py --source dpc_archivio dpc_trimestrale --no-upload

# Carica i PDF scaricati in API
python scripts/upload_dottrina.py

# Carica un singolo PDF manuale
# POST /ingest  file=<PDF>  corpus=dottrina  workspace=mio-studio
```

### Differenza da corpus=studio

| | `studio` | `dottrina` |
|---|---|---|
| Contenuto | Atti, contratti, fascicoli cliente | Manuali, articoli accademici |
| Usato in | Fase 4 SUSSUNZIONE (fatti concreti) | Fase 2 INTERPRETAZIONE |
| Anonimizzazione | ✅ Obbligatoria (PII cliente) | ❌ Non necessaria |
| Retrieval | Vector standard | BM25+Vector bilanciato (0.40/0.50) |

### Indicizzazione dopo upload

```powershell
# Solo indice dottrina (veloce, non tocca normattiva)
python scripts/build_indexes.py --workspace mio-studio --corpus dottrina

# Oppure rebuild completo
python scripts/build_indexes.py --workspace mio-studio
```

---

## 5. Documenti studio avvocato

### Canali di upload

**A. Upload generico** (atti, contratti, pareri, fascicoli):
```
POST /ingest
  file: <PDF/DOCX/TXT>
  workspace: mio-studio
```

**B. Upload sentenza studio** (sentenze raccolte dallo studio):
```
POST /jurisprudence/upload
  file: <PDF sentenza>
  organo: cassazione|tar|consiglio_stato|corte_cost|corte_conti
  workspace: mio-studio
```

### Pipeline ingestione (Tier1Pipeline)

```
PDF/DOCX/TXT
    │
    ▼
DocumentExtractor          → estrae testo raw
    │
    ▼
LegalAnonymizer (spaCy)    → trova PII (nomi, CF, P.IVA, indirizzi)
    │                         sostituisce con placeholder [PERSONA_1], [CF_1]...
    ├──▶ pii_vault           → entity_map cifrata AES (reversibile con chiave)
    │
    ▼
MongoDB.documents          → testo anonimizzato + metadati
    │
    ▼
Chunker (sliding window)   → chunk 512 token, overlap 64 token
    │
    ▼
MongoDB.chunks             → chunk con posizione e workspace
```

### Anonimizzazione PII

Entità rilevate da spaCy `it_core_news_lg`:
- `PER` — nomi di persone → `[PERSONA_N]`
- `ORG` — organizzazioni → `[ORG_N]`
- `LOC` — luoghi → `[LUOGO_N]`
- `MISC` — codici fiscali, P.IVA, indirizzi → `[CF_N]`, `[PIVA_N]`

La `entity_map` è salvata in `pii_vault` cifrata con AES-256.
Il testo in chiaro non esce mai dalla collection `documents`.

---

## 4. Wiki (auto-generata)

### Meccanismo

La wiki si popola automaticamente dopo ogni risposta approvata dal CitationReviewer:

```
POST /query → risposta → S5 PASS → WikiMiddleware → WikiEngine.file_response()
```

Il `WikiEngine`:
1. Chiama `WikiWriter.extract_concepts()` — LLM estrae concetti chiave dalla risposta
2. Crea o aggiorna `WikiPage` in `wiki_pages` con URN citati e workspace
3. Operazione **fire-and-forget** — non blocca la risposta all'utente

### Schema WikiPage

```json
{
  "_id": "ObjectId",
  "slug": "dichiarazione-fraudolenta-art-2-dlgs-74-2000",
  "title": "Dichiarazione fraudolenta — D.Lgs. 74/2000 art. 2",
  "content": "Il reato richiede...",
  "concepts": ["dichiarazione fraudolenta", "fatture false", "D.Lgs. 74/2000"],
  "source_urns": ["urn:nir:stato:decreto.legislativo:2000-03-10;74~art2"],
  "workspace": "mio-studio",
  "created_at": "2026-06-01T...",
  "updated_at": "2026-06-01T..."
}
```

### Stato attuale

La collection `wiki_pages` contiene 109 pagine da sessioni di test precedenti.
Nella KB nuova (`aiura_legal_lab_db`) la wiki ripartirà da zero man mano che
l'avvocato usa il sistema.

### Export wiki

```powershell
# Export in Markdown
python scripts/wiki_export.py --workspace mio-studio --output docs/wiki_export/
```
