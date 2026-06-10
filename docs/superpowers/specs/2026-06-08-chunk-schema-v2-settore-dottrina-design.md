# Chunk Schema V2 — Settore + Dottrina Metadata
**Data**: 2026-06-08
**Autore**: Nicola Grasso / Claude

## Obiettivo

Ridisegnare la struttura dei chunk in `aiura_legal_lab_db.chunks` per:

1. Aggiungere un campo `settore` (lista di valori) che permetta il filtraggio
   per dominio giuridico prima che i chunk raggiungano il retrieval BM25/Vector.
2. Arricchire i metadati della dottrina (`titolo_doc`, `autore`, `anno_pubblicazione`,
   `rivista`, `fascicolo`) che attualmente sono tutti null.
3. Definire la procedura di reset + reload dell'intero knowledge base
   partendo da MongoDB sorgente, senza modificare il database `legal_lab` (read-only).

---

## Sezione 1: Nuovi campi chunk

### 1.1 Campo `settore` (tutti i corpus)

```
settore: list[str]
```

Valori ammessi: `"penale"`, `"civile"`, `"amministrativo"`, `"lavoro"`,
`"processuale"`, `"costituzionale"`, `"altro"`.

Un chunk può appartenere a più settori (es. procedura penale → `["penale", "processuale"]`).
Campo **opzionale in lettura**: chunk privi di `settore` vengono restituiti senza filtro
(retrocompatibilità con corpus=studio e chunk pre-rebuild).

### 1.2 Metadati dottrina (corpus=dottrina)

```
titolo_doc:         str | None   — titolo del documento/articolo
autore:             str | None   — es. "Viganò Francesco; Gatta Gian Luigi"
anno_pubblicazione: int | None   — anno (es. 2019)
rivista:            str | None   — slug rivista (es. "diritto_penale_contemporaneo")
fascicolo:          str | None   — es. "10/2017", "Fasc. I/2024"
```

Questi campi vengono **popolati in-place** con `$set` su tutti i chunk dello stesso
`document_id`, senza re-upload dei PDF originali.

### 1.3 Metadati normattiva (propagazione esistente)

```
titolo_articolo: str | None   — già in normattiva_docs, propagato nel chunk
```

---

## Sezione 2: Classificatore `settore_from_doc()`

Funzione pura in `aiura_legal/ingestion/normattiva/parser.py`.
Costo zero (nessuna chiamata LLM), eseguita al momento del rechunking.

### 2.1 Livello 1 — fonte già nota (codici maggiori)

| fonte (da URN)         | settore              |
|------------------------|----------------------|
| codice_penale          | `["penale"]`         |
| codice_proc_penale     | `["penale", "processuale"]` |
| codice_civile          | `["civile"]`         |
| codice_proc_civile     | `["civile", "processuale"]` |
| legge_costituzionale   | `["costituzionale"]` |
| codice_commercio / soc.| `["civile"]`         |

### 2.2 Livello 2 — keyword nel titolo (leggi/dlgs/dl)

Applicato quando fonte è `legge`, `dlgs`, `dl`, `dpr`, `dm`, o simili.

| Keyword nel titolo                                     | settore                    |
|--------------------------------------------------------|----------------------------|
| `penale`, `reato`, `pena `, `delitto`, `imputab`       | `["penale"]`               |
| `lavoro`, `lavorator`, `previdenz`, `sicurezza*lav`    | `["lavoro"]`               |
| `tribut`, `fiscal`, `impost`, `iva`, `irpef`, `accise` | `["amministrativo"]`       |
| `appalto`, `pubblica amm`, `concessione`, `permesso`   | `["amministrativo"]`       |
| `processo`, `procedur`, `esecuz`, `giurisdiz`          | `["processuale"]`          |
| `civile`, `contratt`, `obbligaz`, `società`, `fallim`  | `["civile"]`               |

Nota: diritto tributario → `"amministrativo"` per ora. Separabile in futuro
aggiungendo `"tributario"` come settimo valore senza modifiche di schema.

### 2.3 Livello 3 — fallback

`["altro"]` — per leggi tecniche/settoriali non classificabili dal titolo (~30% dei casi).

### 2.4 Dottrina

Impostato dall'estrattore (Sezione 3): `["penale"]` per riviste riconosciute
(DPC, Sistema Penale); `["penale"]` come default per tutta la dottrina attuale
(è penalistica al 100%).

---

## Sezione 3: Estrattore metadati dottrina

**Classe**: `DottrinaMetadataExtractor`
**Modulo**: `aiura_legal/ingestion/dottrina/metadata_extractor.py`

Lavora sul testo del **primo chunk** (`chunk_index == 0`) di ogni `document_id`.
Emette un dizionario di metadati che viene applicato a **tutti** i chunk
dello stesso `document_id` via `bulk_write($set)`.

### 3.1 Riviste riconosciute

**Diritto Penale Contemporaneo (DPC)**
- Pattern riconoscimento: `r"DIRITTO PENALE.*CONTEMPORANEO"`
- Estrae anno/fascicolo da: `r"Fascicolo\s+(\d+)/(\d{4})"`
- `rivista = "diritto_penale_contemporaneo"`

**Sistema Penale**
- Pattern riconoscimento: `r"EDITOR-IN-CHIEF\s+Gian Luigi Gatta"` o
  `r"Rivista scientifica quadrimestrale"`
- Estrae da: `r"Anno\s+(\d{4})/Fascicolo\s+([IVX]+)"`
- `rivista = "sistema_penale"`

### 3.2 Documenti non riconosciuti (monografie/paper)

- Prima riga non-vuota di lunghezza > 10 → `titolo_doc`
- Seconda riga se ha pattern `Cognome Nome` (iniziali maiuscole) → `autore`
- Anno 4 cifre nella prima pagina → `anno_pubblicazione`
- `rivista = None`

### 3.3 Output per document_id

```python
{
    "rivista": "diritto_penale_contemporaneo",
    "titolo_doc": "Diritto Penale Contemporaneo",
    "anno_pubblicazione": 2017,
    "fascicolo": "10/2017",
    "autore": "Viganò Francesco",
    "settore": ["penale"],
}
```

---

## Sezione 4: PhaseRetriever — filtraggio settore-aware

### 4.1 Funzione di selezione filtro

```python
def _settore_filter_normativa(domain: str | None) -> dict:
    base = {"corpus": "normattiva"}
    mapping = {
        "penale":             {"$in": ["penale"]},
        "penale_processuale": {"$in": ["penale", "processuale"]},
        "civile":             {"$in": ["civile"]},
        "civile_processuale": {"$in": ["civile", "processuale"]},
        "amministrativo":     {"$in": ["amministrativo"]},
        "lavoro":             {"$in": ["lavoro"]},
        "costituzionale":     {"$in": ["costituzionale"]},
    }
    if domain in mapping:
        return {**base, "settore": mapping[domain]}
    return base  # nessun filtro settore — recupera tutto normattiva
```

`domain` viene inferito dalla QUALIFICAZIONE di Fase 1.
La funzione `_is_criminal_law_topic()` esistente copre il caso `"penale"`;
si aggiungono classificatori analoghi per gli altri domini.

### 4.2 Relazione con la query augmentation esistente

Il filtro `settore` **sostituisce** la query augmentation come meccanismo primario:
filtra i chunk prima del ranking invece di correggere il ranking dopo.
La query augmentation rimane come secondo strato di sicurezza ma non è più critica.

### 4.3 Retrocompatibilità

Chunk senza campo `settore` (corpus=studio, giurisprudenza, dottrina pre-rebuild):
- MongoDB `$in` su campo assente → document non matchato → escluso dal filtro
- Questo è corretto: corpus=studio e giurisprudenza non usano il filtro settore
- Dottrina post-rebuild avrà `settore: ["penale"]` → filtrata correttamente in Fase 2

### 4.4 Filtro Qdrant

Qdrant usa un filtro `should` su array field, equivalente al `$in` MongoDB.
`HybridRetriever._search_round()` già riceve `chunk_filter: dict` e lo traduce
nel formato corretto per entrambe le sorgenti — nessuna modifica architetturale.

---

## Sezione 5: Script reset + reload

**Script**: `scripts/rebuild_knowledge_base.py`

Orchestratore con 7 fasi sequenziali, riprendibile con `--from-phase N`.

### 5.1 Fasi

| Fase | Azione | Durata stimata |
|------|--------|----------------|
| 0 | Backup pkl BM25 (rinomina con timestamp) | < 1 min |
| 1 | Drop `aiura_legal_lab_db.chunks` (filtro workspace) | < 1 min |
| 2 | NormattivaPipeline: rechunk da `legal_lab.normattiva_docs` con `settore` + `titolo_articolo` | ~20 min |
| 3 | DottrinaMetadataExtractor: `$set` metadati su chunk dottrina esistenti | ~5 min |
| 4 | `build_indexes.py --corpus normattiva` (BM25 + Qdrant) | ~15 min |
| 5 | `build_indexes.py --corpus dottrina` | ~8 min |
| 6 | `build_indexes.py --corpus studio` (se esistono doc) | variabile |
| 7 | `build_jurisprudence_indexes.py` (se esistono sentenze) | variabile |

**Totale stimato**: ~50 min (senza studio/giurisprudenza variabili).

### 5.2 Flag CLI

```
--workspace WORKSPACE   filtra per workspace (default: tutti)
--from-phase N          riprende da fase N (es. dopo un crash)
--dry-run               mostra cosa farebbe senza eseguire
--skip-phase N [N ...]  salta fase(i) specifiche
```

### 5.3 Checkpoint

Ogni fase scrive un file `rebuild_state.json` nella root del progetto
con lo stato (`completed`, `failed`, `skipped`) per ciascuna fase.
`--from-phase` legge questo file come default se non specificato.

### 5.4 Vincolo read-only

Il database `legal_lab` (LegalAgentLab) è **read-only**.
Le fasi 2 e 3 leggono da `legal_lab.normattiva_docs` ma
scrivono **esclusivamente** in `aiura_legal_lab_db.chunks`.

---

## Sezione 6: Dipendenze tra componenti

```
NormattivaDocAdapter.to_chunk_base()
  └── chiama settore_from_doc(fonte, titolo, urn) → list[str]
  └── propagato nel campo Chunk.settore

DottrinaMetadataExtractor
  └── legge primo chunk da aiura_legal_lab_db.chunks (corpus=dottrina)
  └── scrive $set su tutti i chunk dello stesso document_id

PhaseRetriever.retrieve_normativa()
  └── chiama _infer_domain(questione_retrieval) → str | None
  └── chiama _settore_filter_normativa(domain) → dict
  └── passa chunk_filter a HybridRetriever._search_round()

rebuild_knowledge_base.py
  └── Fase 2: NormattivaPipeline (usa settore_from_doc)
  └── Fase 3: DottrinaMetadataExtractor
  └── Fase 4-7: build_indexes.py / build_jurisprudence_indexes.py
```

---

## Sezione 7: Testing

- `tests/ingestion/test_settore_classifier.py` — unit test per `settore_from_doc()`:
  - Casi copertura: ogni fonte nota + 10 titoli legge/dlgs rappresentativi
  - Verifica che `codice_proc_penale` → `["penale", "processuale"]`
  - Verifica fallback `["altro"]` per titoli non classificabili
- `tests/ingestion/test_dottrina_metadata.py` — unit test per `DottrinaMetadataExtractor`:
  - Testo DPC reale (anonimizzato) → verifica estrazione anno/fascicolo/rivista
  - Testo Sistema Penale → idem
  - Testo generico → titolo estratto dalla prima riga
- `tests/retrieval/test_phase_retriever_settore.py` — test integrazione filtro:
  - Mock `_search_round` con chunk a settori diversi
  - Verifica che query penale non restituisca chunk civili

---

## Decisioni prese / non discusse

| Decisione | Scelta | Motivazione |
|-----------|--------|-------------|
| Tipo campo settore | `list[str]` | Procedure penali/civili appartengono a 2 settori |
| Tributario | Sotto `amministrativo` | Separabile in futuro senza modifiche schema |
| Dottrina metadata | `$set` in-place | PDF non sempre disponibili; testo già in MongoDB |
| Reset scope | Indices + MongoDB chunks | Rechunk con nuovi campi; ~50 min totali |
| Dottrina settore default | `["penale"]` | Tutto il corpus dottrina attuale è penalistico |

---

## Prossimi passi (implementation plan)

1. `settore_from_doc()` in `parser.py` + update `Chunk` model in `mongodb/models.py`
2. `DottrinaMetadataExtractor` in `aiura_legal/ingestion/dottrina/metadata_extractor.py`
3. `_infer_domain()` + `_settore_filter_normativa()` in `phase_retriever.py`
4. `scripts/rebuild_knowledge_base.py`
5. Test suite (3 file)
6. Rebuild KB (Fase 0-7)
7. Caricare ThyssenKrupp n.38343/2014 in corpus giurisprudenza
