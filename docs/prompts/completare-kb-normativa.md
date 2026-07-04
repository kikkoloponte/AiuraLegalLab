# Prompt operativo — Completare la KB normativa (senza rischi di copyright)

> Come usare questo prompt: incollalo per intero in una sessione con accesso
> al filesystem del progetto AiUra LegalLab, a MongoDB (sia
> `aiura_legal_lab_db` in scrittura sia `legal_lab` in lettura) e a rete
> (Normattiva). Non è un audit: questa sessione deve **scaricare ed
> indicizzare** atti normativi mancanti, con verifica ad ogni passo prima di
> scrivere. Richiede Bash/Read/Grep e i permessi per lanciare script Python
> che scrivono su MongoDB.

---

## Contesto

AiUra LegalLab (`C:\project\AiUraLegalLab`) ha una KB normativa ereditata da
LegalAgentLab (`legal_lab.normattiva_docs`, **read-only**, mai scrivere lì) +
atti scaricati direttamente da Normattiva. Stato noto al 2026-07-03:

- ~166.800 articoli di base (4 codici maggiori, Costituzione, TUIR/IVA,
  Codice Ambiente, T.U. Sicurezza, Privacy, statuti lavoratori/contribuente,
  altri atti mirati).
- 193 istituti giuridici mappati in `aiura_legal/core/istituti/registry.yaml`
  su 11 leggi complementari (231/2001, Antimafia, Consumo, TUB, TUF,
  Privacy, TUIR, Proprietà Industriale, Assicurazioni, Ambiente, Sicurezza
  Lavoro, Crisi d'Impresa).
- 3 leggi scaricate il 2026-07-03: D.Lgs. 36/2023 (Codice Contratti
  Pubblici, sostituisce il D.Lgs. 50/2016 abrogato già in KB), R.D. 267/1942
  (Legge Fallimentare previgente), R.D. 327/1942 (Codice della Navigazione).
- **Segnale di gap forte e verificato**: sia `registry.yaml` (0 istituti su
  193 con `settore: lavoro`) sia i domini della query suite
  (`eval/query_results` — solo `amm, civ, cross, pen, trib`, **manca `lav`**)
  indicano che il diritto del lavoro è sotto-rappresentato nella KB. Dare
  priorità a questo ramo nella ricerca dei gap.
- **Nota metodologica da una sessione precedente**: una checklist di leggi
  complementari costruita "a memoria" si è rivelata non esaustiva (3 leggi
  mancanti trovate solo con un controllo più ampio). Non fidarti di nessuna
  lista, inclusa quella qui sotto, senza un secondo controllo sistematico
  (vedi Fase 1).

## Regola di sicurezza copyright — leggi prima di scaricare qualunque cosa

**Sempre sicuro (nessun copyright, procedi liberamente):**
- Testi di leggi, decreti, regolamenti, atti amministrativi ufficiali dello
  Stato italiano — esclusi dalla protezione d'autore ex art. 5 L. 633/1941.
- Regolamenti UE self-executing (es. GDPR 2016/679) e direttive/atti
  ufficiali istituzionali UE — stesso principio, testi ufficiali pubblici.
- Provvedimenti dell'autorità giudiziaria (sentenze, ordinanze) pubblicati
  da fonti istituzionali (Cassazione, Corte Costituzionale, TAR/CdS, Corte
  dei Conti, CEDU/HUDOC) — atti pubblici, non opere dell'ingegno protette.
- Relazioni istituzionali pubbliche: Ufficio del Massimario della
  Cassazione, relazioni illustrative di legge, atti parlamentari.

**Sicuro solo se esplicitamente dichiarato open access:**
- Riviste giuridiche, articoli accademici, tesi di dottorato — SOLO se la
  fonte dichiara licenza open access (es. Creative Commons, repository
  universitario aperto). Verifica la licenza alla fonte, non assumerla.

**MAI scaricare, in nessun caso:**
- Manuali commerciali di diritto (Trabucchi, Torrente, Fiandaca-Musco,
  Cian-Trabucchi, ecc.) — coperti da copyright, anche se trovati online.
- Contenuti da banche dati a pagamento (DeJure, Pluris/Wolters Kluwer,
  Leggi d'Italia, Il Sole 24 Ore banche dati, De Agostini, ecc.), anche
  con credenziali disponibili — non è nello scope di questa KB.
- Qualunque PDF/testo che sembri una copia scansionata di un libro/rivista
  a pagamento, anche se trovato "gratis" su un sito terzo — non verificarne
  la legalità è un rischio, salta la fonte e segnalala nel report finale.

Se durante la ricerca trovi una fonte ambigua, **non scaricarla**: segnalala
nel report finale con l'URL e la ragione del dubbio, e prosegui con le
fonti sicure.

## Regola operativa — non toccare `legal_lab`, preferisci il mirror

`legal_lab.normattiva_docs` è la fonte di LegalAgentLab, **read-only**
(mai scrivere, mai modificare). Per ogni atto mancante da `aiura_legal_lab_db`:

1. Controlla PRIMA se è già in `legal_lab.normattiva_docs` (query per
   prefisso URN). Se sì: usa `scripts/mirror_normattiva.py --filter-urn
   <prefisso>` — copia locale, zero richieste HTTP a Normattiva.
2. Solo se assente anche in `legal_lab`: usa `scripts/fetch_normattiva.py
   --urn <urn1> <urn2> ...` (o `--tipo`/`--anno` per batch), che scarica
   via Open Data API/scraping Normattiva con `--delay` di default (0.4s,
   non abbassarlo — è già un rate limit rispettoso).
3. Usa sempre `--dry-run` prima di scrivere, per validare URN e contare gli
   articoli attesi.

## Fase 1 — Costruire e verificare la lista dei gap

Non limitarti alla checklist sotto: cerca in modo sistematico un indice
autorevole degli atti normativi italiani di uso comune nella pratica legale
(es. la sezione "Codici" di Normattiva, indici di Gazzetta Ufficiale, o la
tua conoscenza di diritto italiano incrociata con più fonti) per non
ripetere l'errore di una lista arbitraria.

Checklist di partenza (verifica ciascuna voce con una query MongoDB per
prefisso URN su entrambe le collection, PRIMA di assumere che manchi):

**Lavoro (priorità alta — gap confermato):**
- Statuto dei Lavoratori (L. 20 maggio 1970, n. 300)
- D.Lgs. 15 giugno 2015, n. 23 (Jobs Act — contratto a tutele crescenti)
- L. 28 giugno 2012, n. 92 (Riforma Fornero)
- D.Lgs. 10 settembre 2003, n. 276 (Legge Biagi)
- D.Lgs. 8 aprile 2003, n. 66 (orario di lavoro)
- D.Lgs. 26 marzo 2001, n. 151 (T.U. maternità/paternità)
- L. 12 marzo 1999, n. 68 (collocamento disabili)

**Civile/famiglia:**
- Disposizioni sulla legge in generale (Preleggi, R.D. 262/1942)
- L. 1° dicembre 1970, n. 898 (divorzio)
- L. 4 maggio 1983, n. 184 (adozione)
- L. 20 maggio 2016, n. 76 (unioni civili)

**Amministrativo:**
- D.Lgs. 2 luglio 2010, n. 104 (Codice del Processo Amministrativo)
- L. 7 agosto 1990, n. 241 (procedimento amministrativo)
- D.Lgs. 18 agosto 2000, n. 267 (T.U. Enti Locali)

**Penale/altro:**
- D.Lgs. 28 luglio 1989, n. 271 (norme att. c.p.p.) se non già coperto
- Codice della Strada (D.Lgs. 30 aprile 1992, n. 285)

**Trasversali:**
- Codice del Terzo Settore (D.Lgs. 3 luglio 2017, n. 117)
- T.U. Immigrazione (D.Lgs. 25 luglio 1998, n. 286)
- Codice Pari Opportunità (D.Lgs. 11 aprile 2006, n. 198)

Per ognuna: query `db.normattiva_docs.countDocuments({urn: {$regex: "^<prefisso>"}})`
su entrambe le collection. Prefisso URN standard:
`urn:nir:stato:<tipo>:<YYYY-MM-DD>;<numero>` (vedi `_NIR_TO_DENOM` in
`scripts/fetch_normattiva.py` per gli alias tipo validi).

Produci una tabella: atto | presente in aiura? | presente in legal_lab? |
azione (mirror / fetch / nessuna).

## Fase 2 — Scaricare i gap confermati

Per ogni riga "azione=mirror": `mirror_normattiva.py --filter-urn <prefisso>
--workspace mio-studio` (fa anche il chunking, salvo `--skip-chunks`).

Per ogni riga "azione=fetch": `fetch_normattiva.py --urn <urn> --dry-run`
prima, poi senza dry-run. Batch piccoli (max 3-4 atti alla volta), verifica
il conteggio articoli scritto nel log prima di procedere al successivo.

## Fase 3 — Chunk + rebuild indici

Dopo ogni batch di nuovi atti: verifica che il chunking sia avvenuto (log
`NormattivaPipeline.chunk_collection`), poi rebuild indici per
corpus=normattiva:
```
python scripts/build_indexes.py --workspace mio-studio
```
Verifica in coda che BM25 e Qdrant abbiano contato i nuovi documenti (non
assumere — leggi l'output).

## Fase 4 — Estensione oltre la normativa (solo se Fasi 1-3 completate)

Non eseguire senza prima aver finito le fasi precedenti. Se c'è tempo/budget
residuo, valuta (ma non improvvisare scraping nuovo senza verificare prima
licenza/provenienza):
- `scripts/sync_dottrina.py --no-upload` per riviste open access già
  configurate (non aggiungere nuove fonti senza verificarne la licenza).
- Segnala (non implementare) eventuali fonti giurisprudenziali pubbliche
  aggiuntive trovate (es. HUDOC CEDU) per una sessione dedicata.

## Cosa NON fare

- Non scrivere mai su `legal_lab` (è la fonte di un altro progetto).
- Non abbassare `--delay` sotto 0.4s su `fetch_normattiva.py`.
- Non scaricare nulla della lista "MAI" nella sezione copyright, anche se
  sembra comodo o "solo per uso interno".
- Non inventare URN: se un atto non si trova con ricerca diretta, salta e
  segnalalo — non improvvisare un URN plausibile (causa gli stessi bug di
  ID instabili già risolti in `chunk_id.py`).
- Non toccare la mappatura `istituti_giuridici` — è un task separato,
  successivo a questo (serve una sessione dedicata per mappare gli
  istituti dei nuovi atti, specialmente lavoro).

## Formato del report finale

1. Tabella Fase 1 (atto | presente aiura | presente legal_lab | azione).
2. Log delle operazioni eseguite in Fase 2/3 (comando, atti scritti, esito
   rebuild indici) — con numeri reali, non stime.
3. Elenco fonti scartate per dubbio copyright (Fase copyright), con URL e
   motivo.
4. Stato finale: nuovo conteggio articoli in `aiura_legal_lab_db.normattiva_docs`
   vs conteggio iniziale.
5. Prossimi passi suggeriti (max 3 righe) — inclusa esplicitamente la
   necessità di una sessione dedicata per mappare i nuovi atti in
   `istituti_giuridici`, specialmente il settore lavoro.
