# trib_005 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:39 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 12.3s (ret 0.4s + llm 11.4s) |

## Query

> Come funziona l'istituto dell'interpello tributario?

## Risposta

**QUALIFICAZIONE**
L'istituto dell'interpello tributario permette al contribuente di richiedere una risposta riguardante fattispecie concrete e personali relative all'applicazione delle disposizioni tributarie, quando vi sono condizioni di obiettiva incertezza.

**NORMA APPLICABILE**
Il diritto di interpello tributario è regolato dall'articolo 11 della legge n. 212 del 27 luglio 2000.

**GIURISPRUDENZA**
Non sono presenti giurisprudenze specifiche sul diritto di interpello tributario nel Packet.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il diritto di interpello tributario è regolato da una norma chiara e specifica, ma non esistono giurisprudenze contrastanti. La solidità della norma è alta.

**GAP ANALYSIS**
Non sono presenti giurisprudenze sul diritto di interpello tributario nel Packet.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'istituto dell'interpello tributario permette al contribuente di richiedere una risposta riguardante fattispecie concrete e personali relative all'applicazione delle disposizioni tributarie, quando vi sono condizioni di obiettiva incertezza.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art11', 'claim': "Il contribuente può interpellare l'amministrazione finanziaria per ottenere una risposta riguardante fattispecie concrete e personali relativamente alla applicazione delle disposizioni tributarie, quando vi sono condizioni di obiettiva incerte.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### NORMA APPLICABILE

Il diritto di interpello tributario è regolato dall'articolo 11 della legge n. 212 del 27 luglio 2000.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art11', 'claim': "Il contribuente può interpellare l'amministrazione finanziaria per ottenere una risposta riguardante fattispecie concrete e personali relativamente alla applicazione delle disposizioni tributarie, quando vi sono condizioni di obiettiva incerte.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### GIURISPRUDENZA

Non sono presenti giurisprudenze specifiche sul diritto di interpello tributario nel Packet.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il diritto di interpello tributario è regolato da una norma chiara e specifica, ma non esistono giurisprudenze contrastanti. La solidità della norma è alta.

### GAP ANALYSIS

Non sono presenti giurisprudenze sul diritto di interpello tributario nel Packet.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art11` | 0.8690 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art19` | 0.0195 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:legge.costituzionale:1948-02-26;4~art12` | -0.0710 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art65` | -0.6593 | hybrid_rrf |  |
| 5 | `urn:nir:stato:legge:2000-07-27;212~art2` | -1.6211 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:legge:2000-07-27;212~art11` | -2.1892 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art489` | -2.8377 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art248` | -3.2710 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1947` | -4.7437 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art363` | -5.0105 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art11`

> LEGGE 27 luglio 2000, n. 212 Art. 11 (Interpello) 1. Il contribuente può interpellare l'amministrazione finanziaria per ottenere una risposta riguardante fattispecie concrete e personali relativamente alla: a) applicazione delle disposizioni tributarie, quando vi sono condizioni di obiettiva incerte

**[2]** `urn:nir:stato:legge:2000-07-27;212~art19`

> LEGGE 27 luglio 2000, n. 212 Art. 19 Attuazione del diritto di interpello del contribuente 1. L'amministrazione finanziaria, nel quadro dell'attuazione del decreto legislativo 30 luglio 1999, n. 300 , adotta ogni opportuno adeguamento della struttura organizzativa ed individua l'occorrente riallocaz

**[3]** `urn:nir:stato:legge.costituzionale:1948-02-26;4~art12`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 4 Art. 12 Oltre il gettito delle entrate proprie della Valle, sarà dallo Stato, sentito il Consiglio della Valle, attribuita alla stessa una quota dei tributi erariali. La Valle può istituire proprie imposte e sovrimposte osservando i principi dell'ordinamen

**[4]** `urn:nir:stato:legge.costituzionale:1948-02-26;5~art65`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 5 Art. 65 La Regione ha facoltà di istituire con legge tributi propri in armonia coi principi del sistema tributario dello Stato e di applicare una sovrimposta sui terreni e fabbricati. ((Le province hanno facoltà di sovrimporre ai tributi stabiliti dalla re

**[5]** `urn:nir:stato:legge:2000-07-27;212~art2`

> LEGGE 27 luglio 2000, n. 212 Art. 2 Chiarezza e trasparenza delle disposizioni tributarie 1. Le leggi e gli altri atti aventi forza di legge che contengono disposizioni tributarie devono menzionarne l'oggetto nel titolo; la rubrica delle partizioni interne e dei singoli articoli deve menzionare l'og

**[6]** `urn:nir:stato:legge:2000-07-27;212~art11`

> LEGGE 27 luglio 2000, n. 212 , e ai soggetti che presentano le istanze di interpello di cui all' articolo 2 del decreto legislativo 14 settembre 2015, n. 147 . 3. ((La presentazione delle istanze di interpello, in relazione a fattispecie particolarmente complesse, è in ogni caso subordinata al versa

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art489`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 402. (Poteri tutelali spettanti agli istituti di assistenza). L'istituto di pubblica assistenza esercita i poteri tutelari sul minore ricoverato o assistito, secondo le norme del titolo X, capo I di questo libro, fino a quando non si provveda alla nomina di u

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art248`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 222. (Interpello della parte che ha prodotto la scrittura). Quando è proposta querela di falso in corso di causa, il giudice istruttore interpella la parte che ha prodotto il documento se intende valersene in giudizio. Se la risposta è negativa, il documen

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1947`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1883. (Esercizio delle assicurazioni). L'impresa di assicurazione non può essere esercitata che da un istituto di diritto pubblico o da una società per azioni e con l'osservanza delle norme stabilite dalle leggi speciali.

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art363`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 363 Certificazione dei debiti contributivi e per premi assicurativi 1. L'Istituto nazionale per la previdenza sociale e l'Istituto nazionale per gli infortuni sul lavoro, su richiesta del debitore o del tribunale, comunicano i crediti dagli stessi vant

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
