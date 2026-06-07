# Design — Jurisprudence Pipeline
**Data:** 2026-06-01  
**Stato:** Approvato

---

## Contesto

Estensione di AiUra LegalLab per ingestire giurisprudenza italiana da fonti pubbliche e da upload dello studio legale. La pipeline arricchisce la knowledge base con sentenze strutturate, collegate alle norme già presenti in `normattiva_docs` tramite il grafo NetworkX. Il Citation Contract (Reviewer S5) viene esteso per verificare grounding e coerenza norma↔sentenza.

---

## Architettura generale

Due canali di ingestione convergono su un coordinator condiviso:

- **Batch settimanale** — `scripts/sync_jurisprudence.py` → scrapers → coordinator
- **Upload manuale** — `POST /jurisprudence/upload` (FastAPI) → coordinator

```
aiura_legal/jurisprudence/
  models.py               # JurisprudenceDocument + enum OrganoGiudicante, SourceChannel
  scrapers/
    base.py               # BaseScraper ABC
    cassazione.py         # SentenzeWeb (form POST, rate-limit 1 req/s)
    giustizia_amm.py      # portale GA (HTML/PDF, TAR + CdS)
    corte_cost.py         # Corte Costituzionale (HTML statico, archivio dal 1956)
    corte_conti.py        # Corte dei Conti (PDF)
  coordinator.py          # orchestra scraping + upload, dedup, indicizzazione
  parser.py               # estrae massima/motivazione/dispositivo/norme_citate
  graph_builder.py        # estende NetworkX con nodi sentenza → norma
  anonymizer_bridge.py    # chiama anonymizer esistente prima dell'indicizzazione

scripts/sync_jurisprudence.py   # entry point batch settimanale
```

---

## Modello dati

```python
@dataclass
class JurisprudenceDocument:
    id: str                          # hash(organo + numero + anno)
    organo: OrganoGiudicante         # CASSAZIONE | TAR | CONSIGLIO_STATO | CORTE_COST | CORTE_CONTI
    numero: str
    anno: int
    data_deposito: date
    sezione: str
    materia: str

    massima: str                     # chunk indicizzato separatamente
    motivazione: str                 # chunk indicizzato separatamente
    dispositivo: str                 # chunk indicizzato separatamente

    norme_citate: list[str]          # URN normattiva es. ["urn:nir:stato:codice.civile:..."]
    sentenze_citate: list[str]       # id di altri JurisprudenceDocument

    source_url: str
    source_channel: SourceChannel    # SCRAPING | UPLOAD_STUDIO
    is_anonymized: bool = False
    raw_pii_vault_id: Optional[str] = None  # ref a pii_vault se upload studio
```

Ogni `JurisprudenceDocument` genera **3 `Document`** per BM25/vector:
- `metadata["chunk_type"]` ∈ `{"massima", "motivazione", "dispositivo"}`
- `metadata["jdoc_id"]` → riferimento al documento padre

MongoDB collection: `aiura_legal.jurisprudence`

---

## Scraper e parsing

```python
class BaseScraper(ABC):
    async def fetch_since(self, since: date) -> list[RawSentenza]: ...
```

`RawSentenza` = HTML/PDF grezzo + metadati minimi (numero, data, url).

`parser.py` riceve `RawSentenza` e produce `JurisprudenceDocument` parziale (senza risoluzione URN norme — delegata al `graph_builder`). Tecnologie: `BeautifulSoup` per HTML, `pdfplumber` per PDF.

| Fonte | Formato | Note |
|---|---|---|
| Cassazione (SentenzeWeb) | HTML | form POST, paginazione, rate-limit 1 req/s |
| Giustizia Amministrativa | HTML/PDF | TAR + Consiglio di Stato nella stessa base |
| Corte Costituzionale | HTML statico | archivio completo dal 1956, crawl incrementale per anno |
| Corte dei Conti | PDF | struttura meno standardizzata |

Upload studio: PDF via FastAPI multipart → stesso `parser.py` → `anonymizer_bridge` (sempre, per policy) → `pii_vault`.

---

## Grafo e Citation Contract

**Estensione NetworkX:**

| Arco | Tipo | Origine |
|---|---|---|
| `sentenza → norma` | `"interpreta"` | `norme_citate` |
| `sentenza → sentenza` | `"cita"` | `sentenze_citate` |
| `norma → sentenza` | `"applicata_in"` | inverso calcolato da `graph_builder` |

Query abilitata:
```python
graph.neighbors("urn:nir:stato:codice.civile:art2043")
# → tutte le sentenze che interpretano l'art. 2043
```

**Citation Contract — Reviewer S5:**

Per ogni citazione nel draft il Reviewer verifica:
1. La sentenza è nel `ResearchPacket`? → se no, blocca
2. La norma citata dalla sentenza esiste in `normattiva_docs`? → se no, aggiunge `gap`
3. Il link grafo `sentenza → norma` è coerente con quanto scritto nel draft? → se diverge, aggiunge warning

L'interfaccia `ResearchPacket` non cambia — si estende solo la logica interna del Reviewer.

---

## Batch scheduler e aggiornamento indici

`scripts/sync_jurisprudence.py` — pipeline idempotente:

```
1. Per ogni fonte: scraper.fetch_since(last_sync_date[fonte])
2. parser.py → JurisprudenceDocument
3. anonymizer_bridge
4. Dedup per id → skip se già in MongoDB
5. Scrivi in aiura_legal.jurisprudence
6. Genera 3 Document (massima/motivazione/dispositivo)
7. bm25_retriever.add_documents_batch()
8. vector_retriever.add_documents_batch()
9. graph_builder.update(new_docs)
10. Aggiorna last_sync_date[fonte] in aiura_legal.sync_state
```

`sync_state` collection — cursore indipendente per fonte:
```json
{ "source": "cassazione", "last_sync": "2026-05-25" }
```

Il fallimento di uno scraper non blocca gli altri. Il batch è rieseguibile senza effetti collaterali.

---

## Testing

- Ogni scraper: mock HTTP, verifica parsing di fixture HTML/PDF reali (anonimizzate)
- `coordinator`: mongomock-motor, verifica dedup e idempotenza
- `graph_builder`: grafo sintetico con 5 norme + 3 sentenze, verifica archi
- `anonymizer_bridge`: verifica che upload studio produca sempre `pii_vault_id`
- Reviewer S5: verifica blocco citazione non-grounded e aggiunta gap norma mancante
