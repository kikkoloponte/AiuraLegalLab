# UI di revisione QuestioneGiuridica — Design Spec
**Data:** 2026-06-26
**Effort stimato:** M (backend) + M (frontend)
**Dipendenza:** `aiura_legal/core/graph/questione_loader.py`, `ontology/questioni_curate.yaml` (vedi `2026-06-25-ontology-kb-neo4j-migration-design.md`)

---

## 1. Obiettivo

Oggi l'unico modo per approvare/modificare/rifiutare una voce di `ontology/questioni_curate.yaml` è editare il file YAML a mano — rischioso (nessuna validazione degli id contro il grafo reale, nessun controllo di concorrenza) e scomodo per un avvocato senza dimestichezza con YAML/git.

Questa spec descrive una pagina dedicata nella UI esistente (`frontend/`) che permette di:
1. vedere ogni `QuestioneGiuridica` proposta (formulazione, materia, norme/decisioni pertinenti)
2. modificarne i campi, con ricerca/autocomplete degli id reali (niente URN scritti a mano)
3. approvarla o rifiutarla (stato persistito, non solo booleano — vedi §3)

**Fuori scope esplicito**: creazione di nuove voci da zero (nascono da analisi offline, come già fatto per le 4 attuali), e scrittura automatica nel grafo dopo l'approvazione (resta un passo separato via `QuestioneLoader.write_to_graph`, eseguito manualmente).

---

## 2. Incongruenza scoperta e risolta

Esiste già `GET /graph/search` (`aiura_legal/api/graph_router.py`), ma interroga `jurisprudence_graph.json` — un file separato usato solo dal visualizzatore grafico (`/graph` nella UI), **non** `workspaces/<ws>/indices/graph.json`/Neo4j dove vivono gli articoli/sentenze reali del registro. Schema diverso (`attrs["type"]` vs `attrs["node_type"]`, edge key `"links"` vs `"edges"`). Non riusabile per questa feature — serve un endpoint di ricerca nuovo, contro il grafo vero (§4.3).

---

## 3. Migrazione schema YAML

`approvato: bool` → `stato: str` (`"proposto" | "approvato" | "rifiutato"`, default `"proposto"`).

Motivo: il rifiuto deve essere "soft" (la voce resta visibile in un tab "Rifiutate" per essere rivista) — un booleano `approvato` non distingue "non ancora deciso" da "deciso che no". Le 4 voci esistenti in `ontology/questioni_curate.yaml` (tutte `approvato: false`) vengono migrate a `stato: proposto` come parte dell'implementazione.

`QuestioneLoader.load_curated(only_approved=True)` cambia internamente il filtro da `q.approvato` a `q.stato == "approvato"` — firma pubblica invariata, nessun chiamante esterno da aggiornare. `QuestioneGiuridica` (dataclass) perde il campo `approvato: bool` e guadagna `stato: str = "proposto"`.

---

## 4. Backend

### 4.1 `aiura_legal/core/graph/questioni_registry.py` (nuovo)

```python
class VersionConflictError(ValueError):
    """expected_version non coincide con la versione attuale del file."""

class QuestioniRegistry:
    def __init__(self, path: str | Path = _DEFAULT_REGISTRY_PATH) -> None: ...

    def list(self, stato: str | None = None) -> list[QuestioneGiuridica]
        # stato=None → tutte. Nessun filtro only_approved qui (a differenza
        # di QuestioneLoader.load_curated): questa è la vista di gestione,
        # deve mostrare anche le proposte non ancora decise.

    def get(self, id: str) -> tuple[QuestioneGiuridica, str]
        # Raises KeyError se id non esiste. Ritorna (voce, version_hash).

    def update(self, id: str, changes: dict, expected_version: str) -> tuple[QuestioneGiuridica, str]
        # 1. Verifica expected_version == hash attuale del file, altrimenti
        #    VersionConflictError (nessuna scrittura).
        # 2. Applica changes alla voce (merge per campo, non sovrascrittura totale).
        # 3. Se changes tocca norme_pertinenti/decisioni_pertinenti, valida gli
        #    id contro il grafo (stessa logica di
        #    QuestioneLoader._validate_refs_exist) — solleva QuestioneRegistryError
        #    su id inesistente, nessuna scrittura parziale.
        # 4. Riscrive l'intero file (stesso pattern di write_to_graph: leggi
        #    tutto, modifica in memoria, riscrivi tutto — il file ha poche
        #    decine di voci, non serve editing incrementale).
        # 5. Ritorna (voce aggiornata, nuovo version_hash).

    def _compute_version(self, raw_text: str) -> str
        # sha256(raw_text).hexdigest()[:16] — abbastanza per detection di
        # conflitto, non per sicurezza crittografica.
```

Dipende da `questione_loader.py` per parsing/dataclass — non duplica la logica di validazione, la richiama.

### 4.2 `GraphRetriever.search_nodes()` (estensione `retriever.py`)

```python
def search_nodes(self, query_text: str, node_type: str, limit: int = 10) -> list[dict]
    # node_type: "article" | "sentenza".
    # Ritorna [{"id": ..., "label": ...}, ...] — label leggibile per l'autocomplete
    # (es. "Art. 1218 c.c." per article, "Cass. n.123/2024" per sentenza).
```

Implementazione per backend:
- **NetworkX**: scan in-memory, `query_text.lower() in haystack` su `titolo+articolo_num+fonte` (article) o `organo+numero+anno` (sentenza) — stesso pattern di `/graph/search` esistente, non il file, solo lo stile del filtro.
- **Neo4j**: `MATCH (a:Articolo) WHERE toLower(a.titolo + ' ' + a.articolo_num) CONTAINS toLower($q) RETURN a LIMIT $limit` (e analogo per `Sentenza`).

Stessa interfaccia su entrambi i backend, come gli altri metodi di `GraphRetriever` (vedi `2026-06-25-ontology-kb-neo4j-migration-design.md` §4).

### 4.3 `aiura_legal/api/questioni_router.py` (nuovo)

Montato in `app.py`: `app.include_router(questioni_router, prefix="/questioni", tags=["questioni"])`.

| Endpoint | Comportamento |
|---|---|
| `GET /questioni?stato=proposto` | Lista voci, `stato` opzionale (default: tutte) |
| `GET /questioni/{id}` | Singola voce + `version` |
| `PUT /questioni/{id}` | Body `{changes: dict, expected_version: str}` → 200 `{questione, version}`, 409 su conflitto, 400 su id inesistente nel grafo, 404 se `id` non esiste nel registro |
| `GET /questioni/search-nodes?node_type=article&q=...&limit=10` | Autocomplete, `q` min 2 caratteri (stesso vincolo di `/graph/search`) |

Modelli Pydantic seguono il pattern esistente (`GraphNodeModel`, `SearchResponse` in `graph_router.py`).

---

## 5. Frontend

### 5.1 Routing e navigazione
- `frontend/src/App.tsx`: `<Route path="questioni" element={<Questioni />} />`
- `frontend/src/components/layout/Sidebar.tsx`: nuova voce "Questioni da approvare"

### 5.2 Pagina (`frontend/src/pages/Questioni.tsx`)
```
Tabs: Da revisionare | Approvate | Rifiutate
  └─ QuestioneCard per ogni voce (formulazione/materia editabili,
     chip norme_pertinenti/decisioni_pertinenti, pulsanti Rifiuta/Salva/Approva)
```

### 5.3 Componenti nuovi
- `components/questioni/QuestioneCard.tsx` — stato locale di editing per la singola voce
- `components/questioni/NodeIdPicker.tsx` — input con debounce (~300ms) → `GET /questioni/search-nodes` → dropdown → click aggiunge chip. Riusabile per entrambi i campi (`node_type` come prop)
- `hooks/useQuestioni.ts` — TanStack Query:
  - `useQuestioniList(stato?)`
  - `useUpdateQuestione()` — mutation; su 409 mostra toast "voce modificata altrove, ricaricata" + invalida la query per refetch automatico

### 5.4 Comportamento pulsanti
- **Salva**: `PUT` con i campi modificati, `stato` invariato (resta `proposto`)
- **Approva** / **Rifiuta**: `PUT` con `stato` aggiornato + eventuali modifiche pendenti del form, in un'unica chiamata (non due round-trip separati)

---

## 6. Error handling

- **409 Conflict** (versione obsoleta): toast + refetch automatico della voce. L'utente perde solo le modifiche non salvate di quella card — accettabile per uno strumento mono-utente locale.
- **400** (id inesistente nel grafo): messaggio inline nel form, niente scrittura.
- **File YAML assente/corrotto**: `QuestioniRegistry.list()` ritorna `[]` + log warning (non 500) — la pagina mostra "nessuna voce", non si rompe.
- **404** (id non nel registro, es. rimosso da un altro processo): toast + rimozione della card dalla lista locale.

---

## 7. Test strategy

- `tests/test_questioni_registry.py`: list/get/update, conflitto di versione (`VersionConflictError`), validazione id inesistente (nessuna scrittura), migrazione `approvato`→`stato` su file con schema vecchio (se serve compatibilità — vedi §9).
- Estensione `tests/test_graph_retriever_questione.py`: `search_nodes()` su entrambi i backend (pattern esistente, grafo sintetico in `tmp_path`).
- `tests/test_questioni_router.py`: `TestClient` (pattern già in `tests/test_api.py`) per i 4 endpoint, inclusi i casi 409/400/404.
- Test frontend: **non in scope** — il progetto non ha oggi una convenzione di test per componenti React (nessun file `*.test.*`/`*.spec.*` in `frontend/`); introdurla è una decisione separata, non implicita in questa feature.

---

## 8. Non incluso in questo sprint

- Creazione di nuove `QuestioneGiuridica` dalla UI (solo revisione di voci esistenti)
- Scrittura automatica nel grafo dopo l'approvazione (`QuestioneLoader.write_to_graph` resta un passo manuale separato)
- Autenticazione/permessi (lo strumento è oggi mono-utente locale, nessun concetto di auth esistente in `app.py`)
- Test automatici frontend (nessuna convenzione esistente nel progetto)

---

## 9. Migrazione dati esistenti

Le 4 voci in `ontology/questioni_curate.yaml` (schema `approvato: bool`) vanno convertite a `stato: str` come parte dell'implementazione — uno script una tantum o una modifica diretta del file, non una migrazione a runtime con doppio-schema permanente.
