# Prompt operativo — Verifica sistematica del pattern "codice allegato a decreto"

> Come usare questo prompt: incollalo per intero in una sessione con
> accesso al filesystem del progetto AiUra LegalLab, a MongoDB (sia
> `aiura_legal_lab_db` in scrittura sia `legal_lab` in lettura) e a rete
> (Normattiva, solo per i fetch dei gap confermati). Richiede
> Bash/Read/Grep e i permessi per lanciare script Python che scrivono su
> MongoDB. È il seguito diretto della sessione 2026-07-03 che ha scoperto
> il pattern su CPA e D.Lgs. 271/1989 (vedi `docs/prompts/completare-kb-normativa.md`).

---

## Contesto — il pattern e perché esiste

Dal 1997 (L. 59/1997, art. 20) molte leggi italiane di settore sono
redatte con la tecnica "decreto legislativo che approva un codice
allegato": il decreto legislativo pubblicato in Gazzetta ha solo 1-4
articoli propri ("Art. 1 Approvazione del codice e delle disposizioni
connesse", "Art. 2 Entrata in vigore", talvolta abrogazioni/norme
finanziarie) — il vero contenuto normativo sta nell'**Allegato 1** (il
codice vero e proprio), che su Normattiva è tecnicamente "attaccato" allo
stesso atto ma va navigato come sezione separata.

Nella sessione precedente si è scoperto che per **due** atti già presenti
in KB (sia in `aiura_legal_lab_db` sia nella fonte `legal_lab`, quindi il
problema NON è nostro ma pre-esisteva nell'ingestione originale) era stato
acquisito solo il guscio del decreto (1-2 articoli), mai l'allegato:

- **CPA — D.Lgs. 104/2010**: aveva 2 articoli, ne ha ora 168 dopo il fix.
- **D.Lgs. 271/1989** (norme att. c.p.p.): aveva 1 articolo, ne ha ora 326.

Il fix si fa con `scripts/fetch_normattiva.py --urn <act_urn>`, che usa
`NormattivaWebFetcher.stream_articles_from_params()` — navigazione AJAX
del sito che **funziona per qualsiasi atto**, non solo per i 4 codici
maggiori (cc/cp/cpc/cpp), e recupera anche l'allegato. Vedi commit di
riferimento e sezione "Pipeline" nella skill `aiura-retrieval-architecture`.

Questa sessione verifica se **altri atti in KB soffrono dello stesso
problema**, non ancora identificati.

## Metodologia — lezioni già imparate su falsi positivi

Un primo tentativo di ricerca euristica in questa sessione ha mostrato che
il segnale ovvio è troppo rumoroso: cercare `"codice"` + `"approvazion"`
nel testo di atti con pochi articoli produce **~30 candidati**, di cui la
stragrande maggioranza falsi positivi — decreti di modifica che citano
"modifiche al codice civile" o "modifiche all'allegato X del D.Lgs. Y"
(cioè modificano l'allegato di *un altro* atto, non approvano un proprio
allegato).

**Il segnale affidabile è la rubrica (campo `titolo_articolo`) dell'Art. 1
dell'atto**, non il testo libero. I decreti col pattern reale hanno
letteralmente questa rubrica:

```python
from pymongo import MongoClient
c = MongoClient("mongodb://localhost:27017")
aiura = c["aiura_legal_lab_db"]["normattiva_docs"]

cursor = aiura.find({
    "titolo_articolo": {
        "$regex": "approvazione del codice|approvato il codice|"
                   "approvazione del testo unico|approvazione dell.allegato",
        "$options": "i",
    }
}, {"act_urn": 1, "titolo": 1, "titolo_articolo": 1})

for d in cursor:
    n = aiura.count_documents({"act_urn": d["act_urn"]})
    print(n, d["act_urn"], d["titolo"], "|", d["titolo_articolo"])
```

Con questa query mirata (eseguita già in questa sessione, risultati sotto)
i candidati scendono da ~30 a **5**, di cui **2 già noti fixati** (CPA e —
attenzione — ricontrolla che D.Lgs. 271/1989 NON compare qui: la sua
rubrica reale era "IL PRESIDENTE DELLA REPUBBLICA", non "Approvazione del
codice", quindi questa query da sola **non lo avrebbe trovato**. Tienilo a
mente: il segnale di rubrica cattura un sottoinsieme del pattern, non
tutto — vedi Fase 2 per la ricerca complementare che copre 271/1989).

**Rischio di falsi negativi**: il campo `titolo_articolo` viene estratto
con una regex CSS/HTML in `fetch_normattiva.py::_html_to_doc` e in alcuni
atti risulta vuoto (parsing fallito su markup irregolare) — un atto col
pattern reale ma rubrica non estratta correttamente sfugge a questa query.
Non fidarti al 100% del solo segnale di rubrica: la Fase 2 sotto copre
anche questo caso.

## Risultati già raccolti in questa sessione (punto di partenza, non da ripetere)

Query per rubrica (sopra), filtrando `act_urn` con conteggio articoli
basso:

| Atto | Articoli in aiura | Articoli in legal_lab | Verdetto |
|---|---:|---:|---|
| D.Lgs. 26 agosto 2016, n. 174 (**Codice di giustizia contabile**) | 2 | 2 | **GAP CONFERMATO** — stessa rubrica esatta di CPA ("Approvazione del codice e delle disposizioni connesse") |
| D.Lgs. 23 maggio 2011, n. 79 (**Codice del turismo**) | 4 | 4 | **DA VERIFICARE PRIMA DI FETCHARE** — vedi avvertenza sotto |
| L. 17 ottobre 2008, n. 168 | 18 | non verificato | probabile non-gap (18 articoli è un conteggio già sostanziale per una legge di ratifica; verifica rapida, non priorità) |
| L. 21 settembre 2010, n. 157 | 18 | non verificato | idem |
| D.Lgs. 2 luglio 2010, n. 104 (CPA) | 168 | 2 | già fixato nella sessione precedente — appare qui solo perché la rubrica matcha, ignora |

**Avvertenza su D.Lgs. 79/2011 (Codice del Turismo)**: prima di lanciare
il fetch, verifica lo stato di vigenza su Normattiva. Il Codice del
Turismo è stato oggetto di una sentenza della Corte Costituzionale
(risalente al 2012, per invasione della competenza regionale in materia
di turismo) che ne ha annullato larga parte — se la maggioranza
dell'allegato non è più in vigore, il conteggio basso in KB potrebbe
essere sostanzialmente corretto e non un gap da colmare. Verifica la data
di vigenza (`dataInizioVigenza`/eventuali note di annullamento) prima di
fetchare, non assumere che sia un gap solo perché il pattern di rubrica
combacia.

## Fase 1 — Confermare e colmare i gap già individuati

Per D.Lgs. 174/2016: segui esattamente la procedura già rodata su CPA:

```bash
python scripts/fetch_normattiva.py --urn "urn:nir:stato:decreto.legislativo:2016-08-26;174" --limit 5
```

Verifica che il testo degli articoli 3+ sia effettivamente il corpo del
Codice di giustizia contabile (non solo il preambolo ripetuto) prima di
lanciare il fetch completo senza `--limit`. Poi:

```bash
python scripts/fetch_normattiva.py --urn "urn:nir:stato:decreto.legislativo:2016-08-26;174"
```

Per D.Lgs. 79/2011: **solo se** la verifica di vigenza sopra conclude che
vale la pena, stessa procedura.

Dopo ogni fetch confermato: chunk + rebuild indici, stessa sequenza già
usata (vedi skill `aiura-retrieval-architecture`, sezione "Pipeline per
aggiungere nuovo contenuto normattiva"):

```bash
python scripts/mirror_normattiva.py --only-chunks --workspace mio-studio
python scripts/build_indexes.py --workspace mio-studio --corpus normattiva --skip-vector
python scripts/reindex_v2.py --workspace mio-studio --corpus normattiva
```

## Fase 2 — Ricerca complementare (copre il caso 271/1989, rubrica non estratta)

Il segnale di rubrica da solo non avrebbe trovato D.Lgs. 271/1989 (la cui
Art. 1 aveva rubrica "IL PRESIDENTE DELLA REPUBBLICA", cioè il parsing ha
preso il preambolo invece della rubrica reale). Serve un secondo giro con
segnale sul **testo**, ma ristretto per tenere il rumore basso:

1. Filtra `act_urn` con conteggio articoli basso (`<= 5`) E
   `tipo_provvedimento` in `DECRETO LEGISLATIVO` / `DECRETO DEL PRESIDENTE
   DELLA REPUBBLICA` (i tipi che storicamente veicolano codici allegati).
   Questo dà ~1.100 candidati — troppi per revisione manuale integrale.
2. Per ciascuno, leggi il testo completo (non solo l'Art. 1): se **nessun**
   articolo contiene un rinvio esplicito a "disposizioni di attuazione",
   "norme di coordinamento", "allegato" come sostantivo (non come
   riferimento tecnico tipo "allegato B" di una direttiva UE recepita),
   scartalo subito — è quasi certamente un decreto di modifica legittimo
   con pochi articoli propri (il caso comune, vedi i ~28 falsi positivi già
   scartati in questa sessione, elencati sotto per non rifare la stessa
   analisi).
3. Dai 30 candidati testuali già raccolti in questa sessione (grep
   `"codice"` + `"approvazion"`/`"indice generale"`/`"e allegat"` nel testo,
   ristretto a decreto.legislativo/dpr con ≤5 articoli), **26 sono già
   stati verificati come falsi positivi** — decreti di modifica/correttivi
   che citano "codice civile" o "allegato" di un atto altrui, non un
   proprio codice annesso. Non rianalizzarli, sono elencati sotto solo per
   evitare retrocontrolli inutili:

   ```
   D.Lgs. 260/2004, 18/2011, 67/2015, 120/2008, 124/2012, 52/2005,
   73/2015, 543/1992, 111/2015, 153/2012, 126/2014, 99/2005, 149/2022,
   205/2007, 253/1991, 88/2025, 84/2016, 150/2021, 110/2010, 102/2015,
   50/2024, 100/2024, 102/2020, 62/2018, 220/2017, 17/2026, 53/2014
   ```

4. Estendi la ricerca oltre i tipi `decreto.legislativo`/`dpr`: prova anche
   `regio.decreto` (come R.D. 267/1942 Legge Fallimentare, R.D. 327/1942
   Codice Navigazione, già scaricati integralmente in sessioni precedenti
   — verifica comunque che non abbiano lo stesso problema di allegati
   parziali) e `legge` — la tecnica del rinvio ad allegato non è
   esclusiva dei decreti legislativi.
5. **Rischio residuo non coperto da questa metodologia**: un atto con
   pattern codice-allegato ma **completamente assente dalla KB** (zero
   articoli, nemmeno il guscio del decreto) non emerge da nessuna query
   sul conteggio articoli — perché non c'è nulla da contare. Se hai tempo,
   incrocia con un elenco esterno autorevole dei "codici di settore"
   italiani (es. l'elenco della sezione "Codici" su Normattiva) contro
   quanto già verificato nel prompt `completare-kb-normativa.md` (Fase 1)
   — ma non è priorità di questa sessione, segnalalo come prossimo passo
   se non hai tempo di eseguirlo.

## Cosa NON fare

- Non scrivere mai su `legal_lab` (fonte di un altro progetto, read-only).
- Non abbassare `--delay` sotto 0.4s su `fetch_normattiva.py`.
- Non fetchare D.Lgs. 79/2011 senza prima verificare la vigenza reale
  (rischio di reintrodurre norme annullate come se fossero vigenti — viola
  la disciplina del progetto).
- Non rianalizzare i 26 falsi positivi già scartati (lista sopra) — spreco
  di tempo, la conclusione è già verificata in questa sessione.
- Non mappare istituti giuridici in questa sessione: se emergono nuovi
  gap risolti (es. Codice di giustizia contabile), la mappatura in
  `registry.yaml` è un task separato successivo (vedi
  `docs/prompts/mappare-istituti-tuel-cpa-lavoro.md` come modello).

## Formato del report finale

1. Conferma/smentita su D.Lgs. 174/2016 e D.Lgs. 79/2011, con esito del
   fetch (articoli scaricati, numeri reali) o motivo di non-azione
   (es. "annullato da Corte Cost., non fetchato").
2. Esito Fase 2: eventuali nuovi gap trovati con lo stesso pattern,
   tabella atto | conteggio pre | conteggio post | azione.
3. Log operazioni Fase 1/2 (comando, output reale — non stime).
4. Stato finale: conteggio `aiura_legal_lab_db.normattiva_docs` prima →
   dopo, conferma rebuild BM25/Qdrant (numeri da log, non assunti).
5. Prossimi passi (max 3 righe) — incluso se il rischio residuo del punto
   5 in Fase 2 (atti completamente assenti col pattern codice-allegato)
   merita una sessione dedicata con ricerca esterna sull'elenco
   Normattiva.
