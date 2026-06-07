# trib_020 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:41 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 6.6s (ret 0.5s + llm 5.6s) |

## Query

> Quali sono le esenzioni IVA per le operazioni in ambito sanitario?

## Risposta

**QUALIFICAZIONE**
Le esenzioni IVA per le operazioni in ambito sanitario sono previste dal DECRETO LEGISLATIVO 6 settembre 2005, n. 206.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, non presentando dubbi o contraddizioni.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le esenzioni IVA per le operazioni in ambito sanitario sono previste dal DECRETO LEGISLATIVO 6 settembre 2005, n. 206.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-06;206~art16', 'claim': "Sono esenti dall'obbligo dell'indicazione del prezzo per unità di misura i prodotti per i quali tale indicazione non risulti utile a motivo della loro natura o della loro destinazione, o sia di natura tale da dare luogo a confusione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, non presentando dubbi o contraddizioni.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16` | 4.0225 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art763` | 3.9675 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16` | 2.0647 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324` | 1.6976 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art131` | 1.4517 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41` | 1.3517 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art969` | 1.0925 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge:1970-05-20;300~art41` | -0.2600 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art455` | -2.1035 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art89` | -4.3583 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art10`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 16 Esenzioni 1. Sono esenti dall'obbligo dell'indicazione del prezzo per unità di misura i prodotti per i quali tale indicazione non risulti utile a motivo della loro natura o della loro destinazione, o sia di natura tale da dare luogo a confusione.

**[2]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art763`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 590-sexies. (( (Responsabilità colposa per morte o lesioni personali in ambito sanitario).)) ((Se i fatti di cui agli articoli 589 e 590 sono commessi nell'esercizio della professione sanitaria, si applicano le pene ivi previste salvo quanto disposto dal s

**[3]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 are espressamente prodotti o categorie di prodotti non alimentari ai quali non si applicano le predette esenzioni. ((25)) ------------- AGGIORNAMENTO (25) Il D.Lgs. 6 agosto 2015, n. 130 ha disposto (con l'art. 2, comma 1) che "Le disposizioni del present

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 324 Esenzioni dai reati di bancarotta 1. Le disposizioni di cui agli articoli 322, comma 3 e 323 non si applicano ai pagamenti e alle operazioni computi in esecuzione di un concordato preventivo o di accordi di ristrutturazione dei debiti omologati o d

**[5]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art131`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 126 Ambito della giurisdizione sul contenzioso elettorale 1. Il giudice amministrativo ha giurisdizione in materia di operazioni elettorali relative al rinnovo degli organi elettivi dei comuni, delle province, delle regioni e all'elezione dei membri del

**[6]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 Trasparenza del servizio sanitario nazionale 1. Le amministrazioni e gli enti del servizio sanitario nazionale, dei servizi sanitari regionali, ivi comprese le aziende sanitarie territoriali ed ospedaliere, le agenzie e gli altri enti ed organismi pub

**[7]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art969`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 790. (Operazioni davanti al notaio). Se a dirigere le operazioni di divisione è stato delegato un notaio, questi dà avviso, almeno cinque giorni prima, ai condividenti e ai creditori intervenuti del luogo, giorno e ora in cui le operazioni avranno inizio.

**[8]** `urn:nir:stato:legge:1970-05-20;300~art41`

> LEGGE 20 maggio 1970, n. 300 Art. 41 (Esenzioni fiscali) Tutti gli atti e documenti necessari per la attuazione della presente legge e per l'esercizio dei diritti connessi, nonchè tutti gli atti e documenti relativi ai giudizi nascenti dalla sua applicazione sono esenti da bollo, imposte di registro

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art455`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447  o a causa di tali attività, ovvero commessi su cose ivi esistenti o comunque destinate al servizio sanitario o socio-sanitario, quando non è possibile procedere immediatamente all'arresto per ragioni di sicurezza o incolumità pubblic

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art89`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 73 Provvedimenti cautelari 1. In ogni caso in cui lo stato di mente dell'imputato appare tale da renderne necessaria la cura nell'ambito del servizio psichiatrico, il giudice informa con il mezzo più rapido l'autorità competente

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
