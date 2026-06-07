# Legal Graph Builder — Design Spec
**Data:** 2026-05-29  
**Milestone:** 1C  
**Effort stimato:** L (3-5 giorni) + M (Graph Retriever integration)  
**Dipendenza:** Block 1B completato ✅

---

## 1. Obiettivo

Costruire un grafo giuridico dei documenti normativi (NetworkX DiGraph) che serva due scopi:

1. **Retrieval expansion** — quando BM25+Vector recuperano un articolo, espandono automaticamente il Research Packet con i vicini rilevanti nel grafo (es. art. 1218 c.c. → aggiunge art. 1223, art. 1453)
2. **Conflict detection** — il CitationReviewer usa il grafo per avvertire l'avvocato quando norme citate si trovano in relazione `CONTRASTA`

---

## 2. Struttura del grafo

### 2.1 Nodi

Due tipi convivono nello stesso `nx.DiGraph`:

| Tipo | ID del nodo | Attributi |
|---|---|---|
| `article` | `source_id` (URN Normattiva) | `node_type="article"`, `fonte`, `titolo`, `articolo_num`, `testo_tipo`, `valid_from`, `valid_to` |
| `provvedimento` | `"PROV:{fonte}:{titolo}"` | `node_type="provvedimento"`, `fonte`, `titolo` |

**Convenzione vigenza:**
- `valid_from` — data inizio vigenza (`data_inizio_vigenza` in Normattiva, formato `"YYYYMMDD"` o `None`)
- `valid_to` — data fine vigenza (`data_fine_vigenza` in Normattiva, formato `"YYYYMMDD"`, `"99999999"` = vigente, o `None` = sconosciuto)
- Un nodo è vigente alla data `d` se: `valid_from <= d` AND (`valid_to` is None OR `valid_to >= d` OR `valid_to == "99999999"`)

### 2.2 Tipi di arco

| Tipo | Trigger testuale | Direzione | Uso |
|---|---|---|---|
| `RINVIA` | *"ai sensi dell'art. X"*, *"di cui all'art. X"*, *"previsto dall'art. X"*, *"art. X"* generico | A → B | Retrieval expansion |
| `ABROGA` | *"abrogato dall'art. X"* | X → A (chi abroga → abrogato) | Conflict detection |
| `MODIFICA` | *"come modificato dall'art. X"*, *"modificato dall'art. X"* | X → A | Conflict detection |
| `CONTRASTA` | Marcato manualmente o da LLM in iterazioni future | Bidirezionale (archi in entrambe le direzioni) | Conflict detection |
| `APPARTIENE_A` | Ogni articolo → il suo provvedimento (derivato dai metadati) | article → provvedimento | Navigazione gerarchica |

### 2.3 File su disco

```
{workspace}/indices/graph.json     # NetworkX node-link JSON format
```

Formato: `nx.node_link_data(G)` / `nx.node_link_graph(data)` — standard networkx, human-readable.

Dimensione attesa: ~10-30 MB per 166k nodi con bassa densità di archi (la maggior parte degli articoli ha 0-5 rimandi espliciti nel testo).

---

## 3. Componenti

### 3.1 Layout file

```
aiura_legal/core/graph/
├── __init__.py
├── extractor.py        # ReferenceExtractor — regex + heuristics
├── builder.py          # LegalGraphBuilder — build + update incrementale
└── retriever.py        # GraphRetriever — expansion + conflict detection

scripts/
└── build_graph.py      # CLI: build completo da MongoDB

tests/
├── test_graph_extractor.py
├── test_graph_builder.py
└── test_graph_retriever.py
```

### 3.2 `ReferenceExtractor` (`extractor.py`)

Responsabilità: dato il testo di un articolo normativo italiano, restituisce una lista di riferimenti `(articolo_num_target: str, edge_type: str, context: str)`.

**Pattern regex (ordine di priorità):**

```python
PATTERNS: list[tuple[re.Pattern, str]] = [
    # Abrogazione (priorità alta: parola chiave precisa)
    (re.compile(r"abrogat[oa]\s+dall['’]art\.?\s+(\d+[a-z\-]*)", re.I), "ABROGA"),
    # Modifica
    (re.compile(r"modificat[oa]\s+dall['’]art\.?\s+(\d+[a-z\-]*)", re.I), "MODIFICA"),
    # Rinvio esplicito (formule standard)
    (re.compile(r"(?:ai\s+sensi|di\s+cui\s+all['’]|previsto\s+dall['’]|fermo\s+restando.*?art\.?)\s*(\d+[a-z\-]*)", re.I), "RINVIA"),
    # Rinvio generico (fallback)
    (re.compile(r"\bart\.?\s*(\d+[a-z\-bis\-ter\-quater]*)\b", re.I), "RINVIA"),
]
```

**Risoluzione a source_id:**  
L'extractor lavora solo su `articolo_num`. La risoluzione a `source_id` avviene nel `LegalGraphBuilder` tramite un lookup index `{(fonte, articolo_num) → source_id}` costruito al momento del build.

**Nota vigenza:** l'extractor non ha accesso ai dati temporali — la vigenza è responsabilità del `GraphRetriever` durante il filtering.

### 3.3 `LegalGraphBuilder` (`builder.py`)

```python
class LegalGraphBuilder:
    GRAPH_FILENAME = "graph.json"
    
    def build(self, workspace: str, mongo_db, chunk_filter: dict | None = None) -> nx.DiGraph
    # Build completo da zero. Itera su chunks di MongoDB, estrae archi, salva graph.json.
    
    def update(self, chunk: dict, workspace: str) -> None
    # Incrementale: carica graph.json esistente (o crea vuoto), aggiunge nodi/archi del chunk, salva.
    
    def _reset(self, workspace: str) -> None
    # Cancella graph.json per forzare rebuild.
    
    def _graph_path(self, workspace: str) -> Path
    # Ritorna il path a {workspace}/indices/graph.json
    
    def _build_lookup(self, G: nx.DiGraph) -> dict[tuple[str, str], str]
    # Costruisce {(fonte, articolo_num) → source_id} dai nodi esistenti nel grafo.
    
    def _add_chunk(self, G: nx.DiGraph, chunk: dict, lookup: dict) -> None
    # Aggiunge nodo articolo (con valid_from e valid_to) + nodo provvedimento
    # + arco APPARTIENE_A + archi estratti dal testo.
```

**Campi vigenza nel chunk:** `LegalGraphBuilder._add_chunk` legge `chunk.get("valid_from")` e `chunk.get("valid_to")` e li imposta come attributi del nodo. Il campo `valid_to` deve essere propagato dal `NormattivaDocAdapter` (aggiunta `valid_to = doc.get("data_fine_vigenza")`).

**Flusso build completo:**
1. Crea `nx.DiGraph()` vuoto
2. Stream di tutti i chunks dal MongoDB (`chunk_filter` opzionale per workspace/corpus)
3. Per ogni chunk: `_add_chunk(G, chunk, lookup)`
4. Salva in `graph.json`

**Flusso update incrementale:**
1. Carica `graph.json` (o crea vuoto se non esiste)
2. Ricostruisce lookup dai nodi esistenti
3. `_add_chunk(G, new_chunk, lookup)`
4. Salva `graph.json`

Nota: l'update è **idempotente** — se il nodo esiste già, `nx.DiGraph` ignora silenziosamente `add_node` con lo stesso ID.

### 3.4 `GraphRetriever` (`retriever.py`)

```python
class GraphRetriever:
    def __init__(self, workspace_path: str) -> None
    # Carica graph.json in memoria al primo accesso (lazy). Graceful: is_available=False se file mancante.
    
    @property
    def is_available(self) -> bool
    
    def expand(
        self,
        source_ids: list[str],
        depth: int = 1,
        edge_types: list[str] | None = None,   # None = tutti tranne APPARTIENE_A
        max_nodes: int = 10,
        valid_on: date | None = None,           # filtra nodi non vigenti alla data
    ) -> list[SearchResult]
    # Espande source_ids di depth hop nel grafo.
    # Score = 1/(1+distanza). retrieval_method="graph_expansion".
    # Esclude i source_ids già presenti nell'input.
    # Se valid_on è specificato, esclude i nodi non vigenti alla data:
    #   - valid_from > valid_on  → non ancora in vigore
    #   - valid_to < valid_on AND valid_to != "99999999" → abrogato

    def get_conflicts(self, source_ids: list[str]) -> list[tuple[str, str, str]]
    # Ritorna lista (from_id, to_id, edge_type) di archi CONTRASTA o ABROGA
    # che coinvolgono source_ids.
    
    def _load(self) -> None
    # Carica graph.json, costruisce nx.DiGraph in self._graph.
```

### 3.5 Modifiche a `HybridRetriever`

**`__init__`:** aggiunge `self.graph = GraphRetriever(workspace_path)` (opzionale, già graceful)

**Profili pesi aggiornati** (aggiunta colonna graph):

| Intent | BM25 | Vector | Graph |
|---|---|---|---|
| NORMA_LOOKUP | 0.55 | 0.25 | 0.20 |
| GIURISPRUDENZA_SEARCH | 0.20 | 0.70 | 0.10 |
| FATTISPECIE_ANALYSIS | 0.25 | 0.60 | 0.15 |
| NORMA_EVOLUTION | 0.40 | 0.35 | 0.25 |
| RISCHIO_CONTRATTUALE | 0.35 | 0.55 | 0.10 |
| PRECEDENTE_INTERNO | 0.30 | 0.60 | 0.10 |

**`search()`:** se `self.graph.is_available`, dopo BM25+Vector:
1. Chiama `graph_results = self.graph.expand(bm25+vector top source_ids, depth=1, valid_on=valid_on)`
2. Fonde nel RRF tripartito con peso `w_graph`
3. CrossEncoder reranking finale (invariato)

Il parametro `valid_on` arriva già dalla firma di `HybridRetriever.search()` — nessuna modifica all'interfaccia esterna.

Se `self.graph.is_available` è False → comportamento identico all'attuale (nessuna regressione).

### 3.6 Modifiche a `CitationReviewer`

Il check `conflict_disclosure` diventa reale:

```python
# 3. Contrasti dichiarati (graph CONTRASTA/ABROGA edge)
conflicts = self._graph.get_conflicts(list({c.upper() for c in cited})) if self._graph else []
if conflicts:
    checks["conflict_disclosure"] = "WARN"
    warnings.append(f"Norme in conflitto/abrogazione: {conflicts[:3]}")
else:
    checks["conflict_disclosure"] = "PASS"
```

Il `GraphRetriever` viene iniettato nel `CitationReviewer` come dipendenza opzionale (default `None` → PASS come ora).

### 3.7 Integrazione pipeline (update incrementale)

**`NormattivaPipeline.chunk_collection()`:** dopo l'inserimento di ogni chunk in MongoDB, chiama:
```python
self._graph_builder.update(chunk_dict, workspace)
```

**`Tier1Pipeline.ingest()`:** idem per i documenti dello studio dell'avvocato.

Il `LegalGraphBuilder` viene costruito una volta e tenuto in stato nella pipeline.

---

## 4. Script CLI

### `scripts/build_graph.py`

```
usage: python scripts/build_graph.py --workspace <name> [--chunk-filter '{"corpus":"normattiva"}'] [--dry-run]

Argomenti:
  --workspace     nome workspace (default: "default")
  --chunk-filter  JSON filter opzionale per subset di chunk
  --dry-run       stampa statistiche senza scrivere il file
  --reset         cancella graph.json esistente prima del build
```

Output atteso:
```
[build_graph] Caricamento chunk da MongoDB...
[build_graph] 166,822 chunk elaborati in 45.2s
[build_graph] Nodi: 166,822 article + 8,412 provvedimento
[build_graph] Archi: 234,156 RINVIA, 1,847 ABROGA, 892 MODIFICA, 166,822 APPARTIENE_A
[build_graph] Salvato: workspaces/default/indices/graph.json (28.4 MB)
```

---

## 5. Test strategy

### `test_graph_extractor.py` (≥15 test)
- Pattern RINVIA: "ai sensi dell'art. 1", "di cui all'art. 2-bis", "previsto dall'art. 3"
- Pattern ABROGA: "abrogato dall'art. 5", "abrogata dall'art. 12"
- Pattern MODIFICA: "modificato dall'art. 7"
- Fallback generico: "art. 1218"
- Non-match: "articolo di giornale", "artigiano"
- Unicode: apostrofo curvo `'` vs dritto `'`
- Case insensitive: "ABROGATO DALL'ART. 5"

### `test_graph_builder.py` (≥10 test)
- Build da 3 chunk → verifica nodi article creati
- Nodi article hanno attributi `valid_from` e `valid_to`
- `valid_to="99999999"` propagato correttamente sul nodo
- `valid_to=None` quando `data_fine_vigenza` assente
- Archi APPARTIENE_A verso nodo provvedimento
- Arco RINVIA estratto correttamente da testo
- Idempotenza: update dello stesso chunk → nessun duplicato
- Reset + rebuild → stato pulito
- `is_available` False se graph.json non esiste

### `test_graph_retriever.py` (≥13 test)
- expand depth=1 su nodo con 2 vicini → 2 SearchResult
- expand depth=2 → include vicini di vicini
- expand esclude source_ids di input dall'output
- Score decrescente per distanza (depth=1 > depth=2)
- **expand con valid_on → esclude nodi abrogati (valid_to < valid_on)**
- **expand con valid_on → esclude nodi non ancora in vigore (valid_from > valid_on)**
- **expand con valid_on → include nodi con valid_to="99999999" (vigenti)**
- **expand senza valid_on → restituisce tutti i vicini (nessun filtro temporale)**
- get_conflicts con arco CONTRASTA → trova conflitto
- get_conflicts senza archi → lista vuota
- Graceful: is_available=False se file mancante
- expand su grafo vuoto → lista vuota
- retrieval_method == "graph_expansion"
- max_nodes limita output

---

## 6. Dipendenze

```toml
# pyproject.toml da aggiungere
"networkx>=3.3",
```

---

## 7. Non incluso in questo sprint

- Archi `CONTRASTA` da LLM (futuro: S3 Analyst può suggerirli)
- Graph Visualizer (futuro UI)
- Persistenza degli archi in MongoDB (approccio A: solo file JSON)
- AKN parser per cross-reference strutturati da Normattiva (backlog 1C separato)
- Vigenza temporale sugli **archi** ABROGA (data in cui è avvenuta l'abrogazione — distinta dalla vigenza del nodo abrogato)

---

## 8. Ordine di implementazione

1. `extractor.py` + `test_graph_extractor.py`
2. `builder.py` + `test_graph_builder.py`  
3. `scripts/build_graph.py`
4. `retriever.py` + `test_graph_retriever.py`
5. Modifica `HybridRetriever` (aggiungi GraphRetriever, aggiorna pesi)
6. Modifica `CitationReviewer` (conflict_disclosure reale)
7. Integrazione pipeline (update incrementale)
8. Aggiorna BACKLOG.md
