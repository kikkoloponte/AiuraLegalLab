# Normalizzatore di testo per i chunk (whitespace + tipografia)

Data: 2026-06-28

## Contesto

Il [pilot di valutazione Headroom](2026-06-28-headroom-compression-pilot-design.md) ha concluso
che la compressione semantica esterna non funziona su testo giuridico italiano in questo stack.
Durante il pilot, ispezionando chunk reali da `aiura_legal_lab_db.chunks`, è emerso un problema
più semplice e a basso rischio: il testo estratto da PDF (normattiva, giurisprudenza, dottrina)
contiene rumore di formattazione che spreca token e frammenta le frasi per l'LLM, ad esempio:

```
"Visti gli\narticoli 76\ne\n87 della Costituzione\n;"
```

Newline inserite a metà frase (artefatto dell'estrazione PDF a colonne/giustificata), spazi
multipli, spazi prima della punteggiatura, e punteggiatura tipografica (apostrofi/virgolette
curve) provenienti dai PDF di origine.

Nota: durante l'ispezione è stato inizialmente sospettato un bug di encoding (caratteri `�`
visibili in console). Verificato a livello di codepoint (`hex(ord(ch))`): i caratteri sono
Unicode validi (`à` = U+00E0, `'` = U+2019) — si trattava solo di un problema di rendering del
terminale Windows, **non di corruzione dei dati**. Questo spec si occupa quindi solo di
whitespace e normalizzazione tipografica leggera, non di un fix di encoding.

## Obiettivo

Pulire il testo dei chunk una sola volta, in ingestione, così che:
- meno token vengano sprecati in newline/spazi ridondanti nel research packet RAG;
- le frasi non arrivino frammentate all'LLM, migliorando la coerenza del contesto.

Non sostituisce né modifica `ContextBudgetManager` ([context_budget.py](../../../aiura_legal/core/retrieval/context_budget.py)):
quella resta la logica di troncamento a budget. Questo lavoro pulisce il testo a monte.

## Punto di intervento

Tutti i 4 corpus passano per uno di due chunker:
- [`Chunker.iter_chunks()`](../../../aiura_legal/ingestion/chunker.py) — usato da studio/dottrina
  (`aiura_legal/ingestion/pipeline.py:79,81`) e da giurisprudenza
  (`aiura_legal/jurisprudence/coordinator.py:69`).
- [`NormattivaChunker.chunk()`](../../../aiura_legal/ingestion/chunker.py) — usato da normattiva
  (`aiura_legal/ingestion/normattiva/pipeline.py:66`).

Normalizzare il testo grezzo all'ingresso di questi due metodi, **prima** della tokenizzazione
usata per calcolare i confini dei chunk, copre tutti i corpus con due punti di intervento
condivisi — niente da duplicare per corpus.

## Componente nuovo: `normalize_text`

Modulo `aiura_legal/ingestion/text_normalizer.py`, funzione pura:

```python
def normalize_text(text: str) -> str:
    ...
```

Trasformazioni, in ordine:
1. Collassa ogni sequenza di whitespace (spazi, tab, newline, anche ripetute) in un singolo
   spazio (`re.sub(r"\s+", " ", text)`).
2. Rimuove lo spazio prima della punteggiatura (`re.sub(r"\s+([;:,.!?])", r"\1", text)`), per
   correggere `"Costituzione ;"` → `"Costituzione;"` dopo lo step 1.
3. Normalizza tipografia: apostrofi curvi (`’` `‘`) → `'`, virgolette curve (`“` `”`) → `"`.
4. `strip()` finale.

**Proprietà richiesta: idempotenza.** `normalize_text(normalize_text(x)) == normalize_text(x)`
per qualsiasi `x` — necessaria perché la migrazione (sotto) applicherà la funzione sia a chunk
nuovi sia, in un secondo passaggio, a chunk già normalizzati in run successive dello script.

## Migrazione dei chunk esistenti

Nuovo script `scripts/normalize_existing_chunks.py`, stesso pattern CLI di
[`scripts/build_indexes.py`](../../../scripts/build_indexes.py) (argparse, `asyncio.run`,
connessione Mongo via `MongoClient.get()` / `iter_chunks`):

- Itera su `aiura_legal_lab_db.chunks` (filtro opzionale `--corpus`).
- Applica `normalize_text` ai campi `text` e `sommario` (se presente).
- Aggiorna in MongoDB solo i documenti il cui testo normalizzato differisce dall'originale
  (evita scritture inutili).
- Log: numero di chunk ispezionati / modificati per corpus.

**Passo successivo obbligatorio dopo la migrazione**: rilanciare
`scripts/build_indexes.py` (e `build_jurisprudence_indexes.py` per la giurisprudenza) per
ricostruire gli indici BM25/Qdrant sul testo aggiornato — gli indici attuali sono costruiti sul
testo non normalizzato e andrebbero disallineati altrimenti. Questo va documentato nell'help
dello script di migrazione (`epilog` di argparse, come già fa `build_indexes.py`).

## Testing

Unit test in `tests/test_text_normalizer.py`:
- Frase frammentata da newline (caso reale: `"Visti gli\narticoli 76\ne\n87..."`) → frase unica
  con spazi singoli.
- Apostrofo curvo (`dell’avvocato`) → apostrofo dritto (`dell'avvocato`).
- Spazi multipli e spazio prima di punteggiatura.
- Idempotenza: applicare la funzione due volte produce lo stesso risultato della singola
  applicazione, su tutti i casi sopra.

## Fuori scope

- Nessun fix di encoding (i dati sono già corretti — vedi nota nel Contesto).
- Nessuna modifica a `ContextBudgetManager`/troncamento a budget.
- Nessuna compressione semantica (capitolo chiuso dal pilot Headroom).
