# Prompt operativo — Mappare istituti giuridici: TUEL, CPA, D.Lgs. 271/1989 e settore lavoro

> Come usare questo prompt: incollalo per intero in una sessione con
> accesso al filesystem del progetto AiUra LegalLab (Read/Grep/Edit) e a
> MongoDB in lettura (`aiura_legal_lab_db.chunks`). Non serve accesso di
> rete: tutti gli atti coinvolti sono già indicizzati in KB. Richiede
> Bash/Read/Edit e i permessi per modificare
> `aiura_legal/core/istituti/registry.yaml` e
> `scripts/sync_istituti_registry.py`.

---

## Contesto

`aiura_legal/core/istituti/registry.yaml` alimenta il ragionamento
Sequential IQRAC (S3): ogni istituto mappato aiuta il modello a trovare le
norme giuste per una query. Al 2026-07-03 il registro ha **193 istituti**
su 4 codici maggiori (Civile, Penale, Procedura Civile, Procedura Penale)
+ 11 leggi complementari, con questa distribuzione per settore:

| settore | istituti |
|---|---:|
| civile | 124 |
| penale | 59 |
| tributario | 4 |
| amministrativo | 3 |
| **lavoro** | **3** |

Il settore **lavoro** è marcatamente sotto-rappresentato (3 istituti,
tutti dal solo D.Lgs. 81/2008 — sicurezza sul lavoro) rispetto a civile e
penale, nonostante la KB contenga da tempo Statuto dei Lavoratori, Legge
Biagi, T.U. maternità/paternità, l'intera suite Jobs Act 2015 e la Riforma
Fornero, tutti **presenti e verificati in KB ma mai mappati a istituti**.

Nella sessione precedente (2026-07-03) sono stati inoltre scaricati e
indicizzati 3 atti che oggi hanno **zero istituti mappati**:

- **T.U. Enti Locali — D.Lgs. 18 agosto 2000, n. 267** (295 articoli,
  prima completamente assente dalla KB)
- **Codice del Processo Amministrativo — D.Lgs. 2 luglio 2010, n. 104**
  (168 articoli — prima in KB c'erano solo i 2 articoli del decreto di
  approvazione; ora c'è anche l'Allegato 1, il vero codice)
- **Norme di attuazione del c.p.p. — D.Lgs. 28 luglio 1989, n. 271**
  (326 articoli — stesso pattern: prima solo il preambolo, ora anche
  l'allegato sostanziale)

Questa sessione mappa questi 3 atti **e** amplia in modo sistematico il
settore lavoro.

## Metodologia — leggi prima di scrivere qualunque voce

Le mappature esistenti (vedi commit `95f744e` e `0a17dfe`, comando
`git log --oneline -- aiura_legal/core/istituti/registry.yaml`) sono state
scritte **direttamente in `registry.yaml`** come voci YAML a mano, non
tramite la collection MongoDB `istituti_giuridici` + CRUD UI + script di
sync. Segui lo stesso metodo: non serve passare dall'API `/istituti`.

Formato di ogni voce (copia questa struttura esatta):

```yaml
  - id: <slug_snake_case_univoco>
    label: <Nome istituto> (<CODICE>)
    settore: <penale|civile|amministrativo|lavoro|tributario>
    norme_urn:
      - urn:nir:stato:<tipo>:<YYYY-MM-DD>;<numero>~art<N>
    norme_riferimento:
      - Art. <N> <denominazione atto> (<rubrica articolo>)
    termini_chiave:
      - <label in minuscolo, stessa forma di label senza il codice tra parentesi>
    disambigua_da: {}
    sentenze_pilota: []
```

Regole non negoziabili (dalla testata del file, non derogare):

1. **Ogni URN in `norme_urn` deve essere verificato presente** in
   `aiura_legal_lab_db.chunks` con `corpus="normattiva"`,
   `workspace="mio-studio"`, PRIMA di scriverlo nel registro:
   ```python
   db.chunks.find_one({
       "source_id": "<urn>",
       "corpus": "normattiva",
       "workspace": "mio-studio",
   })
   ```
   Se non trovi il chunk, non inventare l'URN: correggi la ricerca (numero
   articolo, formato data) o salta l'istituto e segnalalo nel report.
2. **Estendi `_CODICE_TO_SETTORE` in `scripts/sync_istituti_registry.py`**
   per ogni nuovo `codice_riferimento` che usi (es. `"D.LGS. 267/2000":
   "amministrativo"`). Anche se questa sessione non esegue lo script di
   sync, ometterlo causa uno scarto silenzioso se in futuro qualcuno lo
   esegue — è il bug già preso due volte nelle sessioni precedenti (vedi
   commento nel file stesso).
3. **`id` deve essere univoco** nell'intero file — verifica con
   `grep "^  - id:" registry.yaml | sort | uniq -d` che non produca output
   dopo le tue modifiche.
4. Non toccare le voci esistenti (non rinominare, non spostare settore) a
   meno che tu non trovi un errore oggettivo (es. URN che punta all'atto
   sbagliato) — in tal caso segnalalo separatamente nel report, non
   correggerlo silenziosamente in mezzo a un commit che dovrebbe essere
   solo additivo.
5. Mantieni l'ordine dei settori nel file (`_SETTORE_ORDER` in
   `sync_istituti_registry.py`: penale, civile, amministrativo, lavoro,
   tributario) — inserisci le nuove sezioni/voci nel blocco del settore
   corretto, non in coda al file.

## Fase 1 — TUEL, CPA, D.Lgs. 271/1989 (priorità alta, atti appena arrivati in KB)

Questi 3 atti sono grandi (295 + 168 + 326 = 789 articoli): **non mappare
articolo per articolo**. Leggi un campione rappresentativo di chunk per
capire la struttura dell'atto, poi seleziona 3-6 istituti per atto sul
modello delle leggi complementari già mappate (2-5 istituti a legge).
Criterio di selezione: istituti che un avvocato citerebbe spesso nella
pratica, non ogni definizione tecnica.

**TUEL (D.Lgs. 267/2000)** — `settore: amministrativo`. Candidati da
verificare (non esaustivo, cerca nei chunk prima di confermare articolo e
rubrica esatti):
- Organi di governo del comune/provincia (consiglio, giunta, sindaco)
- Scioglimento e commissariamento degli enti locali
- Controlli sugli atti e revisione economico-finanziaria
- Responsabilità degli amministratori e dipendenti locali
- Contratti e forme di gestione dei servizi pubblici locali

**CPA (D.Lgs. 104/2010, Allegato 1)** — `settore: amministrativo`.
Candidati:
- Giurisdizione amministrativa (generale di legittimità, esclusiva,
  di merito)
- Ricorso al TAR — termini e forma
- Sospensione cautelare del provvedimento amministrativo
- Motivi di ricorso in appello al Consiglio di Stato
- Rito abbreviato per gli appalti pubblici (se presente nei chunk)

**D.Lgs. 271/1989 (norme att. c.p.p.)** — `settore: penale`. Candidati:
- Competenza per i procedimenti riguardanti i magistrati
- Riunione e separazione dei processi
- Priorità nella trattazione delle notizie di reato (art. 3-bis, già
  visto nel campione di verifica di questa sessione)
- Disposizioni sul casellario giudiziale, se presenti
- Norme transitorie di maggior rilievo pratico

Verifica sempre il contenuto reale del chunk prima di scrivere
`norme_riferimento` — le rubriche sopra sono ipotesi di lavoro, non testo
verificato.

## Fase 2 — Settore lavoro (priorità alta, gap strutturale)

Obiettivo: portare `settore: lavoro` da 3 a un ordine di grandezza
paragonabile a `amministrativo`/`tributario` (indicativamente 15-25
istituti), pescando dalle leggi già confermate presenti in KB (verificato
nella sessione precedente, non serve ri-verificare presenza/assenza, solo
i singoli articoli):

| Atto | Istituti candidati indicativi |
|---|---|
| Statuto dei Lavoratori (L. 300/1970) | licenziamento illegittimo e tutela reale (art. 18), libertà di opinione, divieto di indagini sulle opinioni, controlli a distanza, repressione condotta antisindacale (art. 28) |
| Legge Biagi (D.Lgs. 276/2003) | somministrazione di lavoro, staff leasing, distacco del lavoratore, lavoro intermittente |
| Codice contratti di lavoro (D.Lgs. 81/2015) | contratto a tempo determinato, part-time, apprendistato, lavoro accessorio/occasionale |
| Jobs Act tutele crescenti (D.Lgs. 23/2015) | licenziamento illegittimo nel regime a tutele crescenti, revoca del licenziamento |
| T.U. maternità/paternità (D.Lgs. 151/2001) | congedo di maternità, congedo di paternità, divieto di licenziamento durante la maternità |
| Riforma Fornero (L. 92/2012) | regime sanzionatorio del licenziamento (se distinto dal Jobs Act per rapporti ante 2015) |
| Orario di lavoro (D.Lgs. 66/2003) | riposo giornaliero/settimanale, durata massima dell'orario, lavoro straordinario |
| Collocamento disabili (L. 68/1999) | obbligo di assunzione, quote di riserva |
| T.U. Sicurezza Lavoro (D.Lgs. 81/2008) | *(già mappato — 3 istituti esistenti, non duplicare; puoi aggiungere solo se trovi un istituto distinto e non coperto, es. sorveglianza sanitaria, formazione dei lavoratori)* |

Non è un elenco chiuso: se durante la lettura dei chunk trovi un istituto
ricorrente e rilevante non in tabella, aggiungilo. Se un candidato in
tabella non trova riscontro chiaro nei chunk disponibili (es. articolo
troppo tecnico/procedurale per essere un "istituto" utile al
ragionamento), saltalo e segnalalo nel report — non forzare una voce
debole solo per riempire la tabella.

## Cosa NON fare

- Non passare dalla collection MongoDB `istituti_giuridici` / API
  `/istituti` — questa sessione scrive direttamente in `registry.yaml`
  (vedi Metodologia).
- Non mappare articolo per articolo TUEL/CPA/271-1989 — sono codici
  corposi, seleziona solo gli istituti ad alta rilevanza pratica.
- Non inventare o "aggiustare" un URN che non trovi nei chunk — salta e
  segnala.
- Non toccare le voci esistenti del registro (vedi regola 4 in
  Metodologia).
- Non eseguire `scripts/sync_istituti_registry.py` in questa sessione
  (agisce sulla collection MongoDB `istituti_giuridici`, non sulle voci
  che stai scrivendo a mano — eseguirlo non serve e rischia di confondere
  l'output).
- Non toccare corpus/indici (BM25, Qdrant) — questa sessione è solo
  mappatura concettuale su file YAML.

## Formato del report finale

1. Tabella Fase 1: atto | istituti aggiunti (label) | settore.
2. Tabella Fase 2: atto | istituti aggiunti (label).
3. Candidati scartati (di entrambe le fasi) con motivo (URN non trovato /
   articolo troppo tecnico / altro).
4. Conteggio finale registro: totale istituti e distribuzione per settore
   (prima → dopo), stesso formato della tabella in Contesto.
5. Conferma che `_CODICE_TO_SETTORE` è stato esteso per ogni nuovo
   `codice_riferimento` (elenco chiavi aggiunte).
6. Conferma che `grep "^  - id:" registry.yaml | sort | uniq -d` non
   produce output (nessun id duplicato).
7. Esito `pytest tests/test_istituti_registry.py -v` (deve passare).
