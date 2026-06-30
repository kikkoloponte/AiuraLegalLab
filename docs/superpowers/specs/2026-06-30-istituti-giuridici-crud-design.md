# Istituti Giuridici — CRUD UI design

## Contesto

Gli "Istituti Giuridici" sono schede strutturate (denominazione, quadro
normativo, definizione e natura giuridica, elementi costitutivi, formazione
giurisprudenziale) generate analizzando i chunk della KB MongoDB
(`aiura_legal_lab_db.chunks`). Serve un posto dove persisterle e una
schermata UI che permetta all'avvocato di crearle, modificarle (anche a
livello di singola voce annidata) o cancellarle, senza editare JSON a mano.

Esiste già un pattern quasi identico per `QuestioneGiuridica` (vedi
`docs/superpowers/specs/2026-06-26-questioni-review-ui-design.md`):
router → registry → modelli Pydantic → hook React Query → pagina. Questo
design replica lo stesso schema architetturale, con due differenze
deliberate rispetto a Questioni:

- **storage**: MongoDB invece di YAML su disco — gli Istituti hanno
  struttura nidificata più ricca e un volume atteso più alto di Questioni
  (che sono proposte single-record derivate dal grafo).
- **locking**: optimistic locking per-documento (campo `version` intero)
  invece di un hash sull'intero file — coerente con documenti Mongo
  indipendenti invece di un unico file YAML.

## Storage

Collection: `aiura_legal_lab_db.istituti_giuridici`.

Ogni documento è un istituto giuridico completo, struttura 1:1 con il JSON
già prodotto manualmente in questa conversazione:

```
_id: ObjectId
version: int            # parte da 1, incrementato a ogni update riuscito
updated_at: datetime     # UTC, aggiornato a ogni create/update
metadata_ui:
  progetto: str
  stato_istanza: str
  fonti_mongodb_coinvolte: list[str]
denominazione: str
codice_riferimento: str  # "CC" | "CPC" | "CP" | "CPP"
quadro_normativo:
  articoli_principali: list[{riferimento: str, source_mongo_id: str | None}]
  leggi_complementari: list[{riferimento: str, source_mongo_id: str | None}]
definizione_e_natura_giuridica:
  testo: str | None
  source_mongo_id: str | None
elementi_costitutivi: list[{
  id_elemento_ui: str
  descrizione: str
  source_mongo_id: str | None
}]
formazione_giurisprudenziale:
  orientamento_prevalente: str | None
  massime_chiave: list[{
    riferimento_sentenza: str
    principio_diritto: str
    source_mongo_id: str | None
  }]
  contrasti_risolti_o_aperti: str | None
```

Tutti i campi testuali/liste annidate ammettono `null` / `[]` — nessun dato
inventato lato backend, la validazione di "niente ID Mongo allucinati" resta
responsabilità di chi compila la scheda (umano o agente a monte), non del
CRUD stesso.

`fonti_mongodb_coinvolte` e i vari `source_mongo_id` sono stringhe libere
(non validate contro l'esistenza reale in `chunks` — fuori scope di questo
CRUD; un controllo di esistenza potrebbe essere aggiunto in futuro come
arricchimento separato).

## Backend

### `aiura_legal/core/graph/istituti_store.py`

Store async (motor), analogo a `QuestioniRegistry` ma su Mongo:

```python
class IstitutoNotFoundError(KeyError): ...
class VersionConflictError(ValueError): ...

class IstitutiStore:
    def __init__(self, db: AsyncIOMotorDatabase) -> None: ...

    async def list_all(self) -> list[IstitutoGiuridico]: ...
    async def get(self, id: str) -> tuple[IstitutoGiuridico, int]: ...
    async def create(self, payload: IstitutoGiuridicoCreate) -> tuple[IstitutoGiuridico, int]: ...
    async def update(
        self, id: str, payload: IstitutoGiuridicoCreate, expected_version: int
    ) -> tuple[IstitutoGiuridico, int]: ...
    async def delete(self, id: str) -> None: ...
```

- `create`: inserisce con `version=1`, `updated_at=now()`.
- `update`: sovrascrittura **completa** del documento (tutti i campi tranne
  `_id`/`version`/`updated_at`) — coerente con l'editing a form strutturato
  lato UI, che rimanda sempre l'intero istituto, non patch parziali. Usa
  `find_one_and_update` con filtro `{_id, version: expected_version}`: se
  zero documenti modificati, distingue "non trovato" da "conflitto di
  versione" con una `get` di verifica, poi solleva l'eccezione giusta.
- `delete`: cancellazione diretta per `_id`, idempotente lato API (404 se
  già assente).
- Cancellazione di singole voci annidate (un elemento costitutivo, una
  massima, un riferimento normativo) **non ha un endpoint dedicato**: è una
  `update` con l'array ridotto, salvata dal form.

### `aiura_legal/api/istituti_router.py`

Stesso stile di `questioni_router.py` (APIRouter a sé, eccezioni mappate a
HTTP status):

| Metodo | Path | Descrizione |
|---|---|---|
| GET | `/istituti` | lista tutti gli istituti |
| GET | `/istituti/{id}` | singolo istituto + `version` |
| POST | `/istituti` | crea nuovo istituto |
| PUT | `/istituti/{id}` | sovrascrive istituto, body `{istituto: {...}, expected_version: int}`, 409 su conflitto |
| DELETE | `/istituti/{id}` | cancella istituto intero, 404 se assente |

Modelli Pydantic (`IstitutoGiuridico`, `QuadroNormativo`, `ArticoloRef`,
`ElementoCostitutivo`, `MassimaChiave`, `FormazioneGiurisprudenziale`)
rispecchiano 1:1 la struttura sopra. `IstitutoGiuridicoCreate` è lo stesso
modello senza `_id`/`version`/`updated_at`, usato sia per POST che come body
di PUT.

Registrazione in `aiura_legal/api/app.py`:
```python
from aiura_legal.api.istituti_router import router as istituti_router
...
app.include_router(istituti_router, prefix="/istituti", tags=["istituti"])
```

## Frontend

### `frontend/src/hooks/useIstitutiGiuridici.ts`

React Query, stesso stile di `useQuestioni.ts`:

- `useIstitutiList()` — `GET /istituti`
- `useIstituto(id)` — `GET /istituti/{id}`
- `useCreateIstituto()` — `POST /istituti`, invalida `['istituti']` on success
- `useUpdateIstituto()` — `PUT /istituti/{id}`, gestisce 409 con toast
  ("Questo istituto è stato modificato altrove — ricaricato.") + refetch,
  stesso pattern di `useUpdateQuestione`
- `useDeleteIstituto()` — `DELETE /istituti/{id}`, invalida lista, toast di
  conferma

### `frontend/src/pages/Istituti.tsx`

- Lista istituti (denominazione, codice_riferimento, stato) con bottone
  "Nuovo istituto" che apre il form vuoto
- Click su un istituto apre il form di modifica precompilato
- Bottone "Elimina istituto" con conferma (dialog), per cancellazione totale

### `frontend/src/components/istituti/IstitutoForm.tsx`

Form a sezioni, una per blocco dello schema:
- Header: denominazione, codice_riferimento (select CC/CPC/CP/CPP),
  metadata_ui.fonti_mongodb_coinvolte (lista di stringhe editabile)
- Quadro normativo: due liste editabili (articoli_principali,
  leggi_complementari), ogni riga = riferimento + source_mongo_id + bottone
  "rimuovi riga"; bottone "aggiungi riga" in fondo a ciascuna lista
- Definizione e natura giuridica: textarea + source_mongo_id
- Elementi costitutivi: lista editabile (id_elemento_ui generato
  automaticamente come `elem_NN` incrementale, descrizione, source_mongo_id,
  rimuovi/aggiungi)
- Formazione giurisprudenziale: orientamento_prevalente (textarea),
  contrasti_risolti_o_aperti (textarea), massime_chiave come lista editabile
  (riferimento_sentenza, principio_diritto, source_mongo_id,
  rimuovi/aggiungi)
- Salvataggio: invia l'intero documento via `useUpdateIstituto` (o
  `useCreateIstituto` per un nuovo istituto) — rimuovere una riga da una
  lista e salvare è l'unico meccanismo di cancellazione di una singola voce

### Navigazione

`frontend/src/components/layout/Sidebar.tsx`: nuova voce "Istituti
Giuridici" allo stesso livello di "Questioni", route `/istituti` registrata
in `App.tsx` accanto alla route di Questioni.

## Fuori scope

- Validazione che i `source_mongo_id` referenzino chunk realmente esistenti
  in `aiura_legal_lab_db.chunks` (potenziale arricchimento futuro, non
  richiesto da questo CRUD).
- Versionamento storico (audit trail delle modifiche) — solo
  optimistic locking sull'ultima versione, niente cronologia.
- Ricerca/filtro full-text sulla lista istituti — la lista mostra tutti gli
  istituti, senza paginazione né filtro per `codice_riferimento` in questa
  prima iterazione.
