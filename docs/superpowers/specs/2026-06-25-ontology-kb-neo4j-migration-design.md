# Ontologia KB giuridica — Enrichment grafo + migrazione Neo4j — Design Spec
**Data:** 2026-06-25
**Effort stimato:** L (migrazione Neo4j) + M (enrichment schema)
**Dipendenza:** `aiura_legal/core/graph/builder.py` e `retriever.py` esistenti (vedi `2026-05-29-legal-graph-builder-design.md`); `ontology/legal_kb_ontology.ttl` (TBox di riferimento)

---

## 1. Obiettivo

Rendere operativa l'ontologia del dominio giuridico (`ontology/legal_kb_ontology.ttl`) nel grafo usato a runtime da `PhaseRetriever`/`CitationReviewer`, aggiungendo:

1. Un nodo hub `QuestioneGiuridica` che collega Norma/Decisione/Dottrina/Principio per pertinenza giuridica (non solo similarità testuale) — usato per il pre-filtro di retrieval in Fase 2/3 IQRAC.
2. Il nodo `Massima`, distinto da `Sentenza`, per riflettere lo step MASSIMARIO ora separato da GIURISPRUDENZA in Fase 3 (`c5af661`).
3. L'arco `QUALIFICA` (Decisione → Fatto) per la sussunzione in Fase 4 (SINTESI).
4. Un check di vigenza temporale e di ancoraggio documentale dei principi nel `CitationReviewer` (S5), reso possibile dai nuovi nodi/archi.

Contestualmente, **migrare il backend grafo di `mio-studio` da NetworkX a Neo4j**, perché il grafo ha già superato le soglie di staleness configurate (`GraphHealthSettings`) prima di qualsiasi enrichment, e l'enrichment le aggrava.

---

## 2. Stato attuale verificato (2026-06-25)

```
mio-studio: 150.8 MB, 307.325 nodi, 666.291 archi, load 3.07s
stale_reasons: ['size=150.8MB > soglia 150.0MB', 'load_s=3.07s > soglia 3.0s']
```

Proiezione con l'enrichment (stima per ordine di grandezza, vedi conversazione precedente):
- `Massima` + `SINTETIZZA`: +15-30k nodi/archi
- `QuestioneGiuridica` + `PERTINENTE_A`/`RISOLVE`/`ANCORATA_A`: pochi nodi, alto fan-out → +5-15% archi
- `QUALIFICA`: +15-30k archi

**Totale stimato: ~340-350k nodi, ~770-830k archi, ~170-190MB** — oltre soglia su entrambi i parametri.

`workspaces/normattiva` (e varianti per-dominio) sono stati rimossi (`d61b7cf`) — non sono nella base di calcolo, la migrazione riguarda **solo `mio-studio`**.

Il backend Neo4j esiste già come POC funzionalmente completo (`_Neo4jBackend` in `retriever.py:418`, stessa interfaccia pubblica di `_NetworkXBackend`: `expand()`, `get_conflicts()`, `get_health()`), con test di parità (`tests/test_graph_retriever_parity.py`, marcati `integration`). Nessun chiamante (`hybrid_retriever.py`, `reviewer.py`) deve cambiare per passare da un backend all'altro — solo `AIURA_GRAPH_BACKEND=neo4j` in `.env`.

---

## 3. Schema — nodi e archi nuovi

Estende lo schema Neo4j esistente (`Articolo`, `Sentenza`, `Provvedimento`, `ABROGA`, `MODIFICA`, `INTERPRETA`, `APPLICATA_IN`, `CONTRASTA`), mappato da `ontology/legal_kb_ontology.ttl`.

### 3.1 Nodi nuovi

| Label Neo4j | Concetto TTL | Proprietà |
|---|---|---|
| `Massima` | `:Massima` | `id`, `testo`, `urn`, `corpus="massimario"` |
| `QuestioneGiuridica` | `:QuestioneGiuridica` | `id`, `formulazione`, `materia`, `parole_chiave[]`, `orientamento_prevalente` |

`Fatto` non è un nodo nuovo a sé per questo sprint: si usa il nodo `Sentenza`/chunk esistente con campo testuale come target di `QUALIFICA` — modellare `FattoGiuridico` come nodo pieno è fuori scope (vedi §7).

### 3.2 Archi nuovi

| Tipo | Direzione | Trigger | Uso |
|---|---|---|---|
| `SINTETIZZA` | `Sentenza → Massima` | 1:1, da pipeline massimario esistente (`corpus=massimario`) | Fase 3: cita la Massima prima della Sentenza integrale |
| `QUALIFICA` | `Sentenza → Articolo` o `Sentenza → Sentenza` (fatto richiamato) | estratto da motivazione (LLM-assisted, non regex — la sussunzione non ha pattern testuali fissi come ABROGA/MODIFICA) | Fase 4: SUSSUNZIONE, trova precedenti con pattern di qualificazione simile |
| `PERTINENTE_A` | `Articolo → QuestioneGiuridica` | curato/validato offline (stesso ciclo proposta/approvazione del registro istituti) | Pre-filtro Fase 2 |
| `RISOLVE` | `Sentenza → QuestioneGiuridica` | curato/validato offline | Pre-filtro Fase 3 |
| `ANCORATA_A` | `Principio → Documento` (Articolo/Sentenza/OperaDottrinale) | curato/validato offline | Vincolo Reviewer su principi non ancorati |

**Decisione di design:** `PERTINENTE_A`/`RISOLVE`/`ANCORATA_A` **non** sono estratti automaticamente da regex o LLM in questo sprint — sono curati manualmente con lo stesso meccanismo già rodato per `ontology/candidati_assiomi_review.md` (proposta con evidenza osservabile → review umana → trascrizione). Estrarli via LLM è un secondo sprint, perché qui il rischio è introdurre rumore proprio nel nodo che dovrebbe ridurre il rumore di retrieval.

---

## 4. Componenti — file da toccare

```
aiura_legal/core/graph/
├── builder.py          # LegalGraphBuilder — aggiungere scrittura Massima/QuestioneGiuridica
├── retriever.py         # GraphRetriever — nuovi metodi match_questione()/expand_from_questione()
└── questione_loader.py  # NUOVO — carica QuestioneGiuridica curate da file YAML/JSON curato

aiura_legal/agents/
└── reviewer.py          # check vigenza + principio non ancorato

scripts/
├── migrate_graph_to_neo4j.py     # esistente — ri-eseguire su mio-studio dopo enrichment
└── load_questioni.py              # NUOVO — CLI: carica questioni curate nel grafo (NetworkX o Neo4j)

ontology/
└── questioni_curate.yaml          # NUOVO — registro delle QuestioneGiuridica validate, stesso pattern del registro istituti

tests/
├── test_graph_builder.py          # estendere: nodi Massima/QuestioneGiuridica
├── test_graph_retriever.py        # estendere: match_questione, expand_from_questione
└── test_graph_retriever_parity.py # eseguire su mio-studio reale prima del cutover
```

### 4.1 `questione_loader.py` (nuovo)

```python
class QuestioneLoader:
    def load_curated(self, path: str) -> list[QuestioneGiuridica]
    # Legge ontology/questioni_curate.yaml, valida schema (formulazione, materia,
    # parole_chiave, norme_pertinenti[], decisioni_pertinenti[] — tutti id verificati
    # esistere nel grafo prima del caricamento, fallisce rumorosamente se no)

    def write_to_graph(self, questioni: list[QuestioneGiuridica], builder: LegalGraphBuilder) -> None
    # Scrive nodi QuestioneGiuridica + archi PERTINENTE_A/RISOLVE
```

### 4.2 `ontology/questioni_curate.yaml` (nuovo) — formato

```yaml
- id: q_silenzio_assenso_241_1990
  formulazione: "Il silenzio della PA equivale ad accettazione tacita nei procedimenti ex L.241/1990?"
  materia: amministrativo
  parole_chiave: [silenzio-assenso, procedimento amministrativo, art 20 L.241]
  norme_pertinenti: ["urn:nir:stato:legge:1990-08-07;241~art20"]
  decisioni_pertinenti: []   # popolato in iterazione successiva
```

### 4.3 `GraphRetriever` — nuovi metodi (`retriever.py`)

```python
def match_questione(self, query_text: str, threshold: float = 0.75) -> Optional[str]
    # Embedding di query_text vs formulazione/parole_chiave dei nodi QuestioneGiuridica.
    # Ritorna questione_id se sopra soglia, None altrimenti (fallback: retrieval testuale puro, comportamento attuale).

def expand_from_questione(self, questione_id: str, valid_on: Optional[date] = None) -> list[SearchResult]
    # Segue PERTINENTE_A/RISOLVE da questione_id, filtra vigenza come expand() esistente.
    # retrieval_method="questione_expansion".
```

Entrambi i metodi devono esistere identici su `_NetworkXBackend` e `_Neo4jBackend` (stessa interfaccia pubblica già garantita per `expand`/`get_conflicts`/`get_health`) — anche se la migrazione di `mio-studio` rende `_Neo4jBackend` il path reale, `_NetworkXBackend` deve restare funzionante per workspace piccoli futuri.

### 4.4 `CitationReviewer` — nuovi check (`reviewer.py`)

**Aggiornamento post-implementazione (vedi §6):** il check `temporal_validity` esisteva **già** in `reviewer.py` (basato su `metadata.valid_to` del Research Packet) — non andava duplicato come nuovo check "vigenza", andava chiuso il gap: il check storico assumeva silenziosamente "vigente" quando `metadata.valid_to` era assente. Implementato invece un **fallback** su `GraphRetriever.is_abrogated()` solo per quel caso (metadata assente), con priorità a metadata quando presente:

```python
valid_to = src.metadata.get("valid_to", "")
if valid_to:
    if valid_to < str(reference_date):
        expired.append(src.source_id)
elif self._graph and self._graph.is_available:
    if self._graph.is_abrogated(src.source_id, reference_date):
        expired.append(src.source_id)
```

Il check "principio non ancorato" (`has_anchor()`) **non è stato wirato nel reviewer** in questo sprint: non esiste oggi alcuna convenzione di citazione per i principi nella risposta dell'LLM (`extract_citations` riconosce solo pattern URN/hex16: `CC_ART_*`, `CASS_*`, `COST_*`, sentenze hex16) né alcuna pipeline che scriva nodi `principio`/archi `ANCORATA_A` nel grafo (curation manuale futura, §7). Wirare `has_anchor()` senza un modo per popolare gli id citati sarebbe codice morto, mai attivato da un input reale. Resta nel backlog come **dipendenza**: prima serve (a) una sintassi di citazione per i principi nel prompt/parsing della risposta, (b) il primo batch di nodi `principio` curati. `has_anchor()` esiste già su `GraphRetriever` (punto 4) pronto per essere usato quando queste due precondizioni sono soddisfatte.

---

## 5. Migrazione Neo4j — sequenza

1. **Backup**: `graph.json` di `mio-studio` già a 150.8MB, backup prima di ogni modifica (stesso pattern usato in `d61b7cf` — `../AiUraLegalLab_stale_backup_<data>/`).
2. **Enrichment su NetworkX prima della migrazione**: implementare §3-4 sopra scrivendo ancora su `graph.json` (più rapido da iterare/debuggare in locale senza dipendenza da container Docker). Verificare con `test_graph_builder.py` estesi.
3. **Aggiornare `scripts/migrate_graph_to_neo4j.py`** per mappare i nuovi node label (`Massima`, `QuestioneGiuridica`) e relationship types (`SINTETIZZA`, `QUALIFICA`, `PERTINENTE_A`, `RISOLVE`, `ANCORATA_A`) — oggi mappa solo lo schema base.
4. **Eseguire la migrazione** su `mio-studio` enriched: `python scripts/migrate_graph_to_neo4j.py --workspace mio-studio`.
5. **Validare parità**: `pytest -m integration tests/test_graph_retriever_parity.py` — deve passare su tutti gli `expand()`/`get_conflicts()` esistenti **prima** di aggiungere asserzioni sui nuovi metodi (`match_questione`, `expand_from_questione` non hanno equivalente NetworkX in produzione dopo il cutover, quindi la parità si misura solo sullo schema base).
6. **Cutover**: `AIURA_GRAPH_BACKEND=neo4j` in `.env` per l'ambiente che serve `mio-studio`.
7. **Aggiornare il commento-baseline obsoleto** in `retriever.py:64-67` (oggi riporta numeri del 21/06, già superati del +58% nodi/+154% archi alla verifica del 25/06) — sostituirlo con un riferimento a `get_health()` come fonte di verità invece di un numero statico nel commento, per evitare che si rifaccia stale allo stesso modo.

---

## 6. Test strategy

### `test_graph_builder.py` (estensione, ≥8 nuovi test)
- Build con chunk `corpus=massimario` → crea nodo `Massima` + arco `SINTETIZZA`
- `QuestioneLoader.load_curated` valida schema YAML, fallisce su id norma/decisione non esistente nel grafo
- `write_to_graph` crea nodi `QuestioneGiuridica` + archi `PERTINENTE_A`/`RISOLVE` senza duplicati su rerun (idempotenza, stesso pattern di `_add_chunk`)

### `test_graph_retriever.py` (estensione, ≥10 nuovi test)
- `match_questione` sopra soglia → ritorna id corretto
- `match_questione` sotto soglia → `None` (fallback testuale)
- `expand_from_questione` filtra vigenza come `expand()`
- `is_abrogated`/`has_anchor` — casi positivi/negativi

### `test_graph_retriever_parity.py` (esistente, da eseguire non estendere prima del cutover)
- Tutti i test esistenti devono passare su `mio-studio` reale post-enrichment

### `test_reviewer_vigenza_graph.py` (nuovo)
- Norma abrogata nel grafo, metadata assente → `WARN` (fallback attivo)
- Norma vigente nel grafo, metadata assente → `PASS`
- Senza grafo e senza metadata → `PASS` (comportamento storico, backward compatible)
- Metadata presente → ha priorità sul grafo, anche se discordanti (nessuna regressione sul check esistente)

Check "principio non ancorato" non testato: non implementato in questo sprint, vedi §4.4.

---

## 7. Non incluso in questo sprint

- `FattoGiuridico` come nodo pieno (oggi `QUALIFICA` punta a chunk/Articolo, non a un nodo Fatto strutturato) — richiede prima una pipeline di estrazione fatti dalle motivazioni, fuori scope
- Estrazione automatica (LLM) di `PERTINENTE_A`/`RISOLVE`/`ANCORATA_A` — solo curation manuale in questo sprint
- Check "principio non ancorato" nel `CitationReviewer` — `has_anchor()` esiste su `GraphRetriever` ma non è wirato: manca sia la sintassi di citazione dei principi sia un primo batch di nodi `principio` curati (vedi §4.4)
- `OrientamentoGiurisprudenziale` come nodo calcolato/aggregato (oggi solo proprietà `orientamento_prevalente` su `QuestioneGiuridica`, popolata manualmente in curation, non derivata automaticamente da conteggio `Decisione` confluenti)
- `RuoloProcessuale`, `Pratica`, `QuesitoUtente` (livello applicativo dell'ontologia TTL) — restano nella TTL come riferimento futuro, non hanno priorità per questo sprint orientato al retrieval
- Migrazione di workspace diversi da `mio-studio` (nessun altro è sopra soglia)

---

## 8. Ordine di implementazione

1. `ontology/questioni_curate.yaml` — popolare un set iniziale piccolo (10-20 questioni) validato con l'avvocato, stesso ciclo del registro istituti
2. `questione_loader.py` + test
3. Estensione `builder.py` (Massima/SINTETIZZA, QUALIFICA) + test
4. Estensione `retriever.py` (match_questione, expand_from_questione, is_abrogated, has_anchor) + test, ancora su backend NetworkX per iterazione rapida
5. Estensione `reviewer.py` (check vigenza + ancoraggio) + test
6. Aggiornare `migrate_graph_to_neo4j.py` per i nuovi label/relationship types
7. Eseguire migrazione + parity test su `mio-studio` reale
8. Cutover `AIURA_GRAPH_BACKEND=neo4j`, aggiornare commento-baseline in `retriever.py`
9. Aggiornare `PhaseRetriever` per chiamare `match_questione`/`expand_from_questione` come pre-filtro Fase 2/3 (gated dietro fallback se nessun match, zero regressione sul comportamento attuale)
