# trib_005 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 12:01 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 9.6s (ret 0.3s + llm 8.6s) |

## Query

> Come funziona l'istituto dell'interpello tributario?

## Risposta

**QUALIFICAZIONE**
L'istituto dell'interpello tributario si riferisce alla pratica di richiedere informazioni o documenti agli uffici tributari dello Stato.

**NORMA APPLICABILE**
Il meccanismo dell'interpello tributario non è esplicitamente regolamentato da una norma specifica, ma si basa sul diritto processuale civile e sulla legge costituzionale.

**GIURISPRUDENZA**
Non esistono specifiche giurisprudenze che trattino l'interpello tributario come istituto autonomo.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione dell'istituto dell'interpello tributario è bassa in quanto non esiste una normativa specifica e la sua applicazione deriva principalmente dal diritto processuale civile.

**GAP ANALYSIS**
Il Packet manca di una norma specifica che regoli l'istituto dell'interpello tributario. Ciò rende difficile un'analisi dettagliata e potrebbe portare a interpretazioni diverse.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'istituto dell'interpello tributario si riferisce alla pratica di richiedere informazioni o documenti agli uffici tributari dello Stato.

### NORMA APPLICABILE

Il meccanismo dell'interpello tributario non è esplicitamente regolamentato da una norma specifica, ma si basa sul diritto processuale civile e sulla legge costituzionale.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1940-10-28;1443~art248', 'claim': 'Il giudice istruttore interpella la parte che ha prodotto il documento se intende valersene in giudizio.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 28 ottobre 1940, n. 1443'}, {'source_id': 'urn:nir:stato:legge.costituzionale:1948-02-26;7~art71', 'claim': 'La Regione e le Province possono prendere visione delle operazioni di accertamento compiute dagli uffici tributari dello Stato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'LEGGE COSTITUZIONALE 26 febbraio 1948, n. 3'}*

### GIURISPRUDENZA

Non esistono specifiche giurisprudenze che trattino l'interpello tributario come istituto autonomo.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione dell'istituto dell'interpello tributario è bassa in quanto non esiste una normativa specifica e la sua applicazione deriva principalmente dal diritto processuale civile.

### GAP ANALYSIS

Il Packet manca di una norma specifica che regoli l'istituto dell'interpello tributario. Ciò rende difficile un'analisi dettagliata e potrebbe portare a interpretazioni diverse.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge.costituzionale:1948-02-26;4~art12` | -0.0710 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art65` | -0.6593 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art37` | -1.3405 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:2012-04-20;1~art3` | -2.4708 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art489` | -2.8377 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art248` | -3.2710 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art71` | -3.5201 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1947` | -4.7437 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art23` | -4.8673 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge.costituzionale:1948-02-26;3~art9` | -4.8888 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art11`

### Snippet fonti

**[1]** `urn:nir:stato:legge.costituzionale:1948-02-26;4~art12`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 4 Art. 12 Oltre il gettito delle entrate proprie della Valle, sarà dallo Stato, sentito il Consiglio della Valle, attribuita alla stessa una quota dei tributi erariali. La Valle può istituire proprie imposte e sovrimposte osservando i principi dell'ordinamen

**[2]** `urn:nir:stato:legge.costituzionale:1948-02-26;5~art65`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 5 Art. 65 La Regione ha facoltà di istituire con legge tributi propri in armonia coi principi del sistema tributario dello Stato e di applicare una sovrimposta sui terreni e fabbricati. ((Le province hanno facoltà di sovrimporre ai tributi stabiliti dalla re

**[3]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art37`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81  settori. Note all'art. 37: - Si riporta il testo dell' articolo 49 della legge 9 marzo 1989, n. 88 (Ristrutturazione dell'Istituto nazionale della previdenza sociale e dell'Istituto nazionale per l'assicurazione contro gli infortuni sul lavoro): «Art. 49. (

**[4]** `urn:nir:stato:legge.costituzionale:2012-04-20;1~art3`

> LEGGE COSTITUZIONALE 20 aprile 2012, n. 1 Art. 3 1. All' articolo 117 della Costituzione sono apportate le seguenti modificazioni: a) al secondo comma, lettera e), dopo le parole: «sistema tributario e contabile dello Stato;» sono inserite le seguenti: «armonizzazione dei bilanci pubblici;»; b) al t

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art489`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 402. (Poteri tutelali spettanti agli istituti di assistenza). L'istituto di pubblica assistenza esercita i poteri tutelari sul minore ricoverato o assistito, secondo le norme del titolo X, capo I di questo libro, fino a quando non si provveda alla nomina di u

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art248`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 222. (Interpello della parte che ha prodotto la scrittura). Quando è proposta querela di falso in corso di causa, il giudice istruttore interpella la parte che ha prodotto il documento se intende valersene in giudizio. Se la risposta è negativa, il documen

**[7]** `urn:nir:stato:legge.costituzionale:1948-02-26;5~art71`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 5 Art. 71 La Regione e le Province possono prendere visione delle operazioni di accertamento compiute dagli uffici tributari dello Stato e fornire ad essi dati ed informazioni. Gli uffici stessi sono tenuti a riferire alla Regione e alle Province i provvedim

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1947`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1883. (Esercizio delle assicurazioni). L'impresa di assicurazione non può essere esercitata che da un istituto di diritto pubblico o da una società per azioni e con l'osservanza delle norme stabilite dalle leggi speciali.

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art23`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  Per i tributi amministrati dall'Agenzia delle entrate, l'accordo è sottoscritto dal Direttore dell'ufficio su parere conforme della competente Direzione regionale. Per i tributi amministrati dall'Agenzia delle dogane e dei monopoli l'accordo è sottoscritto

**[10]** `urn:nir:stato:legge.costituzionale:1948-02-26;3~art9`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 3 Art. 9 La Regione può affidare agli organi dello Stato l'accertamento e la, riscossione dei propri tributi. ((La regione collabora all'accertamento delle imposte erariali sui redditi dei soggetti con domicilio fiscale nel suo territorio. A tal fine la giun

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
