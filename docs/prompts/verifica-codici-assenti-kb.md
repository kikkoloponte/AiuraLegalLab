# Prompt operativo — Codici di settore completamente assenti dalla KB

> Come usare questo prompt: incollalo per intero in una sessione con
> accesso al filesystem del progetto AiUra LegalLab, a MongoDB (sia
> `aiura_legal_lab_db` in scrittura sia `legal_lab` in lettura) e a rete
> (Normattiva, per costruire l'elenco autorevole e per i fetch dei gap
> confermati). Richiede Bash/Read/Grep, WebSearch/WebFetch, e i permessi
> per lanciare script Python che scrivono su MongoDB. È il seguito diretto
> della sessione 2026-07-03 (`docs/prompts/verifica-pattern-codice-allegato.md`)
> che ha risolto 2 gap (D.Lgs. 174/2016, D.Lgs. 79/2011) ma ha lasciato
> esplicitamente scoperto il rischio residuo affrontato qui.

---

## Contesto — il rischio residuo non coperto dalla sessione precedente

La sessione del 2026-07-03 ha verificato il pattern "decreto legislativo che
approva un codice allegato" (vedi quel prompt per la spiegazione tecnica del
pattern) cercando **atti già presenti in KB con pochi articoli** — un segnale
di conteggio che presuppone che l'atto esista già, anche solo come guscio.
Con questa metodologia ha trovato e colmato 2 gap (Codice di giustizia
contabile, Codice del Turismo) e scartato ~28 candidati come falsi positivi.

**Il buco esplicitamente segnalato in quel report**: un atto con pattern
codice-allegato ma **completamente assente dalla KB** (zero articoli, non
solo pochi) non emerge da nessuna query sul conteggio articoli — non c'è
nulla da contare. Questa sessione copre esattamente questo caso.

## Metodologia — serve una lista esterna autorevole, non solo query interne

Non esiste un modo di trovare "atti che non ci sono" guardando solo dentro
la KB. Serve un **elenco di riferimento esterno** dei codici di settore
italiani, poi un controllo di presenza (esiste sì/no in
`aiura_legal_lab_db` e in `legal_lab`) per ciascuna voce.

1. Costruisci l'elenco autorevole incrociando **almeno due fonti indipendenti**:
   - La sezione "Codici" di Normattiva (https://www.normattiva.it — naviga la
     pagina che elenca i codici vigenti raggruppati per materia; se la
     struttura del sito è cambiata rispetto a quanto atteso, cerca con
     WebSearch "normattiva elenco codici vigenti" per trovare il percorso
     corretto aggiornato).
   - Un elenco enciclopedico di controllo (es. voce Wikipedia "Codici della
     Repubblica Italiana" o equivalente) — usalo solo come cross-check, non
     come fonte primaria, e verifica ogni voce contro Normattiva prima di
     considerarla affidabile.
   - Non fidarti di un solo elenco: la sessione precedente ha già dimostrato
     (per le leggi complementari) che le checklist costruite a memoria o da
     una sola fonte non sono esaustive.
2. Per ogni codice nell'elenco unito, determina l'`act_urn` NIR (formato
   `urn:nir:stato:<tipo>:<YYYY-MM-DD>;<numero>`, vedi `_NIR_TO_DENOM` in
   `scripts/fetch_normattiva.py` per gli alias tipo validi).
3. Query di presenza su **entrambe** le collection, per ciascun `act_urn`:
   ```python
   from pymongo import MongoClient
   c = MongoClient("mongodb://localhost:27017")
   aiura = c["aiura_legal_lab_db"]["normattiva_docs"]
   legal = c["legal_lab"]["normattiva_docs"]
   for urn in candidati:
       n_aiura = aiura.count_documents({"act_urn": urn})
       n_legal = legal.count_documents({"act_urn": urn})
       print(urn, "| aiura:", n_aiura, "| legal_lab:", n_legal)
   ```
   Se `n_aiura == 0`: gap totale confermato (a prescindere da `n_legal`).
   Se `n_aiura == 0` e `n_legal > 0`: usa `mirror_normattiva.py`, non
   `fetch_normattiva.py` (vedi Fase 2).
4. Non limitarti a controllare l'`act_urn` esatto che ti aspetti: i numeri di
   decreto/anno che ricordi potrebbero essere sbagliati o riferirsi a una
   versione previgente/abrogata. Prima di concludere "assente", fai anche
   una query di ricerca testuale libera sul titolo (`titolo` regex case
   insensitive) su entrambe le collection, per escludere un mismatch di URN
   piuttosto che un'assenza reale.

## Punto di partenza — candidati da verificare (non ancora controllati)

Lista compilata incrociando conoscenza di dominio + la copertura attuale
osservata in `aiura_legal/core/istituti/registry.yaml` (232 istituti, 27
atti distinti coperti al 2026-07-03). **Nessuna di queste voci è stata
verificata in questa sessione — sono ipotesi da controllare, non fatti.**
Non fidarti della lista senza eseguire il controllo di presenza del punto
3 sopra per ciascuna.

Candidati con segnale di probabile assenza (non compaiono tra gli atti
coperti dal registry.yaml istituti né sono stati toccati nelle sessioni
precedenti):

- **Codice della Strada** — D.Lgs. 30 aprile 1992, n. 285 (già in checklist
  di `completare-kb-normativa.md`, mai verificato)
- **Codice dell'Amministrazione Digitale (CAD)** — D.Lgs. 7 marzo 2005, n. 82
- **Codice dei Beni Culturali e del Paesaggio** — D.Lgs. 22 gennaio 2004, n. 42
- **Codice dell'Ordinamento Militare** — D.Lgs. 15 marzo 2010, n. 66
  (attenzione: non confondere con D.Lgs. 8 aprile 2003, n. 66 sull'orario di
  lavoro, già presente e diverso atto)
- **Codice delle Comunicazioni Elettroniche** — verifica se il testo vigente
  corrente è ancora D.Lgs. 1 agosto 2003, n. 259 o se è stato sostituito dal
  D.Lgs. 8 novembre 2021, n. 207 (recepimento del Codice europeo delle
  comunicazioni elettroniche) — controlla la vigenza prima di scegliere quale
  fetchare
- **Codice della Nautica da Diporto** — D.Lgs. 18 luglio 2005, n. 171
- **Codice delle Pari Opportunità** — D.Lgs. 11 aprile 2006, n. 198 (già in
  checklist di `completare-kb-normativa.md`, mai verificato)
- **Codice del Terzo Settore** — D.Lgs. 3 luglio 2017, n. 117 (già in
  checklist di `completare-kb-normativa.md`, mai verificato)
- **T.U. Immigrazione** — D.Lgs. 25 luglio 1998, n. 286 (già in checklist di
  `completare-kb-normativa.md`, mai verificato)
- **Codice dei Contratti Pubblici** — D.Lgs. 31 marzo 2023, n. 36: risulta
  già scaricato in una sessione precedente (2026-07-03,
  `project_ingestion_leggi_mancanti`); verifica comunque il conteggio
  articoli attuale, potrebbe essere un altro caso di allegato parziale
  (verifica rapida, priorità bassa)

Atti già confermati coperti (non ricontrollare, spreco di tempo): i 27 atti
distinti elencati in `registry.yaml` al 2026-07-03 (include già Codice
Civile/Penale/Proc.Civile/Proc.Penale impliciti, Codice del Consumo D.Lgs
206/2005, Codice delle Assicurazioni D.Lgs 209/2005, Codice della Proprietà
Industriale D.Lgs 30/2005, Codice Privacy D.Lgs 196/2003, Codice
dell'Ambiente D.Lgs 152/2006, Codice Antimafia D.Lgs 159/2011, Codice della
Crisi d'Impresa D.Lgs 14/2019, Codice di Giustizia Contabile D.Lgs 174/2016
e Codice del Turismo D.Lgs 79/2011 appena fixati) e i 3 atti scaricati nella
sessione ingestion (D.Lgs 36/2023, R.D. 267/1942, R.D. 327/1942).

## Fase 1 — Costruire e verificare l'elenco completo

Segui la metodologia sopra: costruisci l'elenco autorevole incrociando
Normattiva + fonte di controllo, poi esegui la query di presenza per
ciascuna voce (inclusi i candidati di partenza sopra, ma senza fermarti a
quelli). Produci una tabella: codice | act_urn ipotizzato | presente in
aiura? | presente in legal_lab? | azione (mirror / fetch / nessuna azione).

## Fase 2 — Colmare i gap confermati

Stessa procedura rodata nelle due sessioni precedenti:

- Se presente in `legal_lab` ma assente in `aiura`: usa
  `scripts/mirror_normattiva.py --filter-urn <prefisso> --workspace mio-studio`
  (zero richieste HTTP, copia locale).
- Se assente in entrambe: usa `scripts/fetch_normattiva.py --urn <urn> --limit 5`
  come test preliminare per confermare che il fetch recupera davvero il
  contenuto del codice (non solo il preambolo), poi lancia senza `--limit`.
  Batch piccoli (max 3-4 atti alla volta), verifica il conteggio articoli nel
  log prima di procedere al successivo. Non abbassare `--delay` sotto 0.4s.
- **Prima di ogni fetch**, se l'atto ha subito modifiche costituzionali o
  abrogazioni parziali note (es. il caso Corte Cost. 80/2012 sul Codice del
  Turismo, risolto nella sessione precedente controllando
  `data_inizio_vigenza`/`data_fine_vigenza` sui singoli articoli piuttosto
  che fidarsi di un riassunto di seconda mano), verifica lo stato di
  vigenza con lo stesso metodo prima di scrivere in KB.

## Fase 3 — Chunk + rebuild indici

Dopo ogni batch di nuovi atti (segui la pipeline documentata nella skill
`aiura-retrieval-architecture`, sezione "Pipeline per aggiungere nuovo
contenuto normattiva"):

```bash
python scripts/mirror_normattiva.py --workspace mio-studio --only-chunks
python scripts/build_indexes.py --workspace mio-studio --corpus normattiva --skip-vector
python scripts/reindex_v2.py --workspace mio-studio --corpus normattiva
```

Verifica ogni step leggendo l'output reale (conteggio chunk, conteggio
punti Qdrant via `QdrantClient.get_collection(...).points_count`), non
assumere il successo. Controlla che non ci siano istanze concorrenti di
`reindex_v2.py` prima di lanciarlo (vedi skill, rischio OOM GPU).

## Cosa NON fare

- Non scrivere mai su `legal_lab` (fonte di un altro progetto, read-only).
- Non abbassare `--delay` sotto 0.4s su `fetch_normattiva.py`.
- Non fetchare un atto senza prima verificare la vigenza reale se ha subito
  pronunce di incostituzionalità note — controlla i metadati
  `data_inizio_vigenza`/`data_fine_vigenza` articolo per articolo, non
  fidarti di un riassunto secondario (lezione della sessione precedente sul
  Codice del Turismo).
- Non inventare URN: se un codice non si trova con ricerca diretta, salta e
  segnalalo nel report — non improvvisare un URN plausibile.
- Non rifidarti ciecamente della lista "punto di partenza" sopra: è
  compilata da conoscenza di dominio incrociata con la copertura del
  registry, non da un controllo sistematico — trattala come ipotesi di
  lavoro, non come risultato.
- Non mappare istituti giuridici in questa sessione: se emergono nuovi gap
  risolti, la mappatura in `registry.yaml` è un task separato successivo
  (vedi `docs/prompts/mappare-istituti-tuel-cpa-lavoro.md` come modello).

## Formato del report finale

1. Fonti usate per l'elenco autorevole dei codici (URL, con nota su
   eventuali discrepanze tra le fonti incrociate).
2. Tabella Fase 1 completa (codice | act_urn | presente aiura | presente
   legal_lab | azione), inclusi i candidati di partenza sopra con esito
   reale (non assunto).
3. Log delle operazioni Fase 2/3 (comando, atti scritti, conteggio
   articoli reale da log) per ogni gap confermato e colmato.
4. Stato finale: conteggio `aiura_legal_lab_db.normattiva_docs` prima →
   dopo, conferma rebuild BM25/Qdrant con numeri reali da log/client, non
   stime.
5. Eventuali fonti scartate per dubbio su vigenza/legittimità, con
   motivazione.
6. Prossimi passi (max 3 righe) — inclusa la necessità di una sessione
   dedicata per mappare i nuovi codici in `istituti_giuridici` se emergono
   gap significativi.
