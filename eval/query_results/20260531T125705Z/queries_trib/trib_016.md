# trib_016 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:41 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 8.1s (ret 0.4s + llm 7.3s) |

## Query

> Quali sono i limiti alla compensazione dei crediti fiscali?

## Risposta

**QUALIFICAZIONE**
La domanda riguarda i limiti alla compensazione dei crediti fiscali.

**NORMA APPLICABILE**
Il limite principale alla compensazione dei crediti fiscali è specificato nel Regio Decreto 16 marzo 1942, n. 262, Art. 1824.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente ai limiti della compensazione dei crediti fiscali.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione è alta in quanto la norma è chiara e specifica sui limiti alla compensazione, ma manca una giurisprudenza diretta.

**GAP ANALYSIS**
C'è un gap nel Packet poiché non ci sono giurisprudenze specifiche menzionate riguardanti i limiti della compensazione dei crediti fiscali.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La domanda riguarda i limiti alla compensazione dei crediti fiscali.

### NORMA APPLICABILE

Il limite principale alla compensazione dei crediti fiscali è specificato nel Regio Decreto 16 marzo 1942, n. 262, Art. 1824.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art1824', 'claim': 'Sono esclusi dal conto corrente i crediti che non sono suscettibili di compensazione.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente ai limiti della compensazione dei crediti fiscali.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione è alta in quanto la norma è chiara e specifica sui limiti alla compensazione, ma manca una giurisprudenza diretta.

### GAP ANALYSIS

C'è un gap nel Packet poiché non ci sono giurisprudenze specifiche menzionate riguardanti i limiti della compensazione dei crediti fiscali.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1888` | 3.9508 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6` | 3.1663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art8` | 2.6132 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art1011` | 2.3236 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155` | 2.0325 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1295` | 0.1879 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1347` | -0.1364 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1291` | -1.5055 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art224` | -2.0446 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art41` | -3.1013 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-07-09;241~art17`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1888`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1824. (Crediti esclusi dal conto corrente). Sono esclusi dal conto corrente i crediti che non sono suscettibili di compensazione. Qualora il contratto intervenga tra imprenditori, s'intendono esclusi dal conto i crediti estranei alle rispettive imprese.

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 6 (Prededucibilità dei crediti) 1. Oltre ai crediti così espressamente qualificati dalla legge, sono prededucibili: a) i crediti relativi a spese e compensi per le prestazioni rese ((nell'esercizio delle funzioni rientranti nella competenza dell'organi

**[3]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

**[4]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art1011`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 817-bis. (( (Compensazione).)) ((Gli arbitri sono competenti a conoscere dell'eccezione di compensazione, nei limiti del valore della domanda, anche se il controcredito non è compreso nell'ambito della convenzione di arbitrato.))

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 155 Compensazione 1. I creditori possono opporre in compensazione dei loro debiti verso il debitore il cui patrimonio è sottoposto alla liquidazione giudiziale i propri crediti verso quest'ultimo, ancorchè non scaduti prima dell'apertura della procedur

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1295`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1250. (Compensazione rispetto ai terzi). La compensazione non si verifica in pregiudizio dei terzi che hanno acquistato diritti di usufrutto o di pegno su uno dei crediti.

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1347`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1302. (Compensazione). Ciascuno dei debitori in solido può opporre in compensazione il credito di un condebitore solo fino alla concorrenza della parte di quest'ultimo. A uno dei creditori in solido il debitore può opporre in compensazione ciò che gli è dovut

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1291`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1246. (Casi in cui la compensazione non si verifica). La compensazione si verifica qualunque sia il titolo dell'uno o dell'altro debito, eccettuati i casi: 1) di credito per la restituzione di cose di cui il proprietario sia stato ingiustamente spogliato; 2)

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art224`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 224 Crediti assistiti da prelazione 1. I crediti assistiti da privilegio generale hanno diritto di prelazione per il capitale, le spese e gli interessi, nei limiti di cui agli articoli 153 e 154, sul prezzo ricavato dalla liquidazione del patrimonio mo

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art41`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 35. (Eccezione di compensazione). Quando è opposto in compensazione un credito che è contestato ed eccede la competenza per valore del giudice adito, questi, se la domanda è fondata su titolo non controverso o facilmente accertabile, può decidere su di ess

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
