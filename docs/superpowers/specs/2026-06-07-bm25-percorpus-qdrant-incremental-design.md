# BM25 Per-Corpus + Qdrant Incremental Indexing

**Data:** 2026-06-07  
**Stato:** Approvato  
**Obiettivo:** Eliminare i rebuild completi del BM25 e i re-embedding Qdrant inutili. Aggiornare un corpus deve toccare solo quel corpus.

---

## Problema

Oggi ogni `build_indexes.py --corpus dottrina` provoca:

1. **BM25**: carica il pkl monolitico (470k doc), rimuove dottrina, ri-aggiunge dottrina, salva → `BM25Okapi(470k)` rebuild (~8 min)
2. **Qdrant**: re-embedd tutti i 191k chunk di dottrina anche se sono già indicizzati (~40 min)
3. **Startup API**: `load()` del pkl monolitico → `BM25Okapi(470k)` rebuild al primo `search()` (~15s)

Risultato: ogni operazione di manutenzione richiede ore anche per aggiornamenti minimali.

---

## Soluzione

Due modifiche indipendenti e complementari:

### 1. BM25 per-corpus (4 pkl separati)
### 2. Qdrant skip-existing (salta UUID già presenti)

---

## Architettura: BM25 per-corpus

### Struttura file

```
workspaces/mio-studio/indices/
  bm25_normattiva.pkl        # ~278k docs + BM25Okapi serializzato
  bm25_dottrina.pkl          # ~191k docs + BM25Okapi serializzato
  bm25_studio.pkl            # ~400 docs  + BM25Okapi serializzato
  bm25_giurisprudenza.pkl    # ~316k docs + BM25Okapi serializzato
  bm25.pkl                   # LEGACY — rimosso automaticamente dopo migrazione
  bm25_meta.json             # stato aggregato per ispezione/kb_sync
```

### Classe interna `_BM25Sub`

Non esposta pubblicamente. Gestisce un singolo corpus:

```python
@dataclass
class _BM25Sub:
    corpus: str
    ws: Path
    # dati
    doc_ids:        list[str]
    doc_snippets:   list[str]
    doc_metadata:   list[dict]
    doc_source_ids: list[str]
    tokenized:      list[list[str]]   # corpus tokenizzato
    chunk_meta:     dict[str, dict]
    # BM25
    bm25:           BM25Okapi | None
    dirty:          bool              # True se docs aggiunti dopo load
    # numpy filter arrays (precalcolati)
    corpus_arr:     np.ndarray
    fonte_arr:      np.ndarray
    testo_tipo_arr: np.ndarray

    @property
    def index_path(self) -> Path:
        return self.ws / "indices" / f"bm25_{self.corpus}.pkl"
```

Metodi di `_BM25Sub`:
- `add(docs: list[Document])` — tokenizza, appende, `dirty=True`, ricalcola numpy arrays
- `reset()` — svuota tutto
- `search(query, top_k, chunk_filter) -> list[SearchResult]`
- `save()` — esegue `BM25Okapi(tokenized)` se `dirty`, poi pickle con BM25Okapi incluso
- `load()` — carica da pkl, `bm25` è già pronto (no lazy rebuild), `dirty=False`

**Punto chiave:** `save()` include l'oggetto `BM25Okapi` nel pkl. Al caricamento successivo `bm25` è già pronto → il primo `search()` post-startup è istantaneo.

### Interfaccia pubblica `BM25Retriever` (invariata)

```python
class BM25Retriever:
    def __init__(self, workspace_path: str) -> None: ...
    def add_documents_batch(self, docs: list[Document]) -> None: ...
    def search(self, query, top_k, chunk_filter) -> list[SearchResult]: ...
    def save(self) -> None: ...
    def load(self) -> None: ...        # retrocompatibilità
    def _remove_corpus(self, corpus: str) -> None: ...
    def _reset(self) -> None: ...
    @property
    def _doc_ids(self) -> list[str]: ...   # aggregato da tutti i sub
```

Internamente gestisce `dict[str, _BM25Sub]` con chiavi `("normattiva", "dottrina", "studio", "giurisprudenza")`.

### Routing delle operazioni

| Operazione | Prima | Dopo |
|-----------|-------|------|
| `add_documents_batch(docs)` | appende a lista unica | raggruppa per corpus → delega al sub giusto |
| `search(query, filter={"corpus": "normattiva"})` | BM25 su 470k, maschera numpy | BM25 solo su `_sub["normattiva"]` (278k) |
| `search(query)` senza filtro | BM25 su 470k | BM25 su 4 sub → merge per score → top_k |
| `_remove_corpus("dottrina")` | rimuove da lista unica, `dirty=True` | `_sub["dottrina"].reset()` |
| `save()` | rebuild BM25Okapi su 470k | rebuild solo sub con `dirty=True` |

**Merge senza filtro corpus:** ogni sub ritorna top_k risultati, si aggregano tutti (dedup per doc_id, keep highest score), si sortano per score, si ritorna top_k globale. Questo è corretto per RRF downstream che usa solo il rank, non lo score assoluto.

### Migrazione automatica

In `BM25Retriever.__init__()`, se esiste `bm25.pkl` ma non `bm25_normattiva.pkl`:

```python
def _maybe_migrate_legacy(self) -> None:
    legacy = self._ws / "indices" / "bm25.pkl"
    if not legacy.exists():
        return
    if (self._ws / "indices" / "bm25_normattiva.pkl").exists():
        return   # già migrato

    logger.info("BM25: migrazione da pkl monolitico a per-corpus...")
    with open(legacy, "rb") as f:
        state = pickle.load(f)

    # Raggruppa per corpus senza re-tokenizzare
    by_corpus: dict[str, list[int]] = {}
    for i, meta in enumerate(state["doc_metadata"]):
        c = meta.get("corpus", "studio")
        by_corpus.setdefault(c, []).append(i)

    for corpus, indices in by_corpus.items():
        sub = self._get_or_create_sub(corpus)
        for i in indices:
            sub.doc_ids.append(state["doc_ids"][i])
            sub.doc_snippets.append(state["doc_snippets"][i])
            sub.doc_metadata.append(state["doc_metadata"][i])
            sub.doc_source_ids.append(state["doc_source_ids"][i])
            sub.tokenized.append(state["corpus"][i])
        sub.chunk_meta.update({
            k: v for k, v in state.get("chunk_meta", {}).items()
            if k in set(sub.doc_ids)
        })
        sub.dirty = True
        sub._rebuild_filter_arrays()

    # Salva sub-indici (BM25Okapi viene costruito qui)
    self.save()
    legacy.rename(legacy.with_suffix(".pkl.migrated"))
    logger.success("BM25: migrazione completata, bm25.pkl rinominato in bm25.pkl.migrated")
```

Tempo atteso: ~5-15 secondi (solo rebuild BM25Okapi per corpus, non re-tokenizzazione).

---

## Architettura: Qdrant skip-existing

### Modifica a `add_documents_batch()`

Nuovo parametro: `skip_existing: bool = True`

```python
def add_documents_batch(
    self,
    docs: list[Document],
    batch_size: int = 512,
    skip_existing: bool = True,
) -> None:
```

Flusso per ogni batch di `batch_size` doc:

```
1. Calcola uuids = [_to_qdrant_id(d.id) for d in batch]
2. Se skip_existing:
     existing = client.retrieve(
         collection_name, ids=uuids,
         with_payload=False, with_vectors=False
     )
     existing_set = {str(p.id) for p in existing}
     to_embed = [d for d, uid in zip(batch, uuids) if uid not in existing_set]
     skipped = len(batch) - len(to_embed)
     if skipped: logger.debug(f"Qdrant: saltati {skipped} punti già esistenti")
3. Altrimenti: to_embed = batch
4. Se to_embed vuoto → continua al prossimo batch (niente embedding)
5. vectors = self._embed([d.text for d in to_embed])
6. points = [PointStruct(id=uid, vector=vec, payload=...) for ...]
7. client.upsert(points, wait=False)
```

### Nuovo flag `--force-reindex` in build_indexes.py

```
--force-reindex    Forza re-embedding Qdrant anche per chunk già presenti.
                   Usare dopo un cambio modello embedding.
                   Default: False (usa skip_existing=True)
```

Quando `--force-reindex` è passato, chiama `add_documents_batch(..., skip_existing=False)`.

### Effetto pratico

| Scenario | Prima | Dopo |
|----------|-------|------|
| Rebuild dottrina (già in Qdrant, nessuna modifica) | embed 191k (~40 min) | retrieve IDs (~20s), embed 0 |
| Rebuild dottrina (500 doc nuovi aggiunti) | embed 191k | retrieve IDs, embed 500 (~1 min) |
| Rebuild studio (400 doc già in Qdrant) | embed 400 (<1 min) | retrieve IDs (~1s), embed 0 |
| `--force-reindex` dopo cambio modello | embed 191k | embed 191k (comportamento invariato) |

---

## Impatto su altri componenti

### `build_indexes.py`
- Nessuna modifica alla logica: usa già `bm25._remove_corpus(corpus)` + `add_documents_batch`
- Aggiunge `--force-reindex` flag → passa `skip_existing=False` a `VectorRetriever`
- Nessuna modifica al flusso Qdrant reset/upsert

### `build_jurisprudence_indexes.py`
- Usa `bm25._doc_ids` (property aggregata) → invariato
- Usa `bm25.add_documents_batch()` → invariato
- `BM25Okapi` rebuild per giurisprudenza avviene solo su `bm25_giurisprudenza.pkl` (~316k)

### `kb_sync.py`
- `_bm25_counts()`: legge i 4 pkl separati invece di uno → aggiorna logica di lettura
- Nessun altro cambiamento

### `HybridRetriever`
- Usa `BM25Retriever.search()` → API invariata → nessuna modifica

### Test
- `test_bm25_retriever.py`: aggiornare per istanziare `_BM25Sub` o mockare i 4 sub-indici
- `test_retrieval_perf.py`: invariato (testa API pubblica)
- Nuovi test: migrazione legacy, search multi-corpus senza filtro

---

## Sequenza di implementazione

1. **`_BM25Sub`** — classe interna con load/save/add/search/reset
2. **`BM25Retriever` refactor** — gestisce dict di sub-indici, migrazione legacy
3. **`VectorRetriever.add_documents_batch()`** — aggiunge `skip_existing` + retrieve-before-embed
4. **`build_indexes.py`** — aggiunge `--force-reindex`
5. **`kb_sync.py`** — aggiorna `_bm25_counts()` per leggere i 4 pkl
6. **Test** — aggiorna mock e aggiungi test migrazione

---

## Metriche di successo

- `build_indexes --corpus studio` BM25: da ~8 min a <1s
- `build_indexes --corpus dottrina` BM25: da ~8 min a ~3 min (solo 191k)
- API startup primo search: da ~15s a <1s
- Re-run `build_indexes --corpus dottrina` senza modifiche Qdrant: da ~40 min a ~20s
