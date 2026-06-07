# cross_001 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:14 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 27.9s (ret 0.3s + llm 27.4s) |

## Query

> Quali sono i rapporti tra azione civile e azione penale per il risarcimento del danno da reato?

## Risposta

**QUALIFICAZIONE**
L'azione civile per il risarcimento del danno da reato può essere esercitata nel processo penale dal soggetto al quale il reato ha recato un danno, in base all'articolo 185 del Codice Penale.

**NORMA APPLICABILE**
L'azione civile per il risarcimento del danno da reato può essere esercitata nel processo penale in base all'articolo 74 del Codice di Processo Penale.

**GIURISPRUDENZA**
Non ci sono specifiche giurisprudenze che si riferiscano espressamente ai rapporti tra azione civile e azione penale per il risarcimento del danno da reato. Tuttavia, la giurisprudenza tende a considerare l'azione civile come una continuazione dell'azione penale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della norma è alta in quanto specifica chiaramente i presupposti per l'esercizio dell'azione civile nel processo penale. Tuttavia, la mancanza di giurisprudenza diretta rende il quadro un po' meno chiaro.

**GAP ANALYSIS**
Il Packet non contiene giurisprudenza specifica sui rapporti tra azione civile e azione penale per il risarcimento del danno da reato. Ci sarebbe bisogno di ulteriori esempi o decisioni giudiziarie che illustrino come queste due azioni interagiscono in pratica.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'azione civile per il risarcimento del danno da reato può essere esercitata nel processo penale dal soggetto al quale il reato ha recato un danno, in base all'articolo 185 del Codice Penale.

*Citazioni: {'source_id': '9', 'claim': 'Ogni reato obbliga alle restituzioni, a norma delle leggi civili. Ogni reato, che abbia cagionato un danno patrimoniale o non patrimoniale, obbliga al risarcimento il colpevole e le persone che, a norma delle leggi civili, sono responsabili solidali.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398'}*

### NORMA APPLICABILE

L'azione civile per il risarcimento del danno da reato può essere esercitata nel processo penale in base all'articolo 74 del Codice di Processo Penale.

*Citazioni: {'source_id': '1', 'claim': "L'azione civile per le restituzioni e per il risarcimento del danno di cui all'articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha recato un danno.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447'}*

### GIURISPRUDENZA

Non ci sono specifiche giurisprudenze che si riferiscano espressamente ai rapporti tra azione civile e azione penale per il risarcimento del danno da reato. Tuttavia, la giurisprudenza tende a considerare l'azione civile come una continuazione dell'azione penale.

*Citazioni: {'source_id': '2', 'claim': "L'azione civile proposta davanti al giudice civile può essere trasferita nel processo penale fino a quando in sede civile non sia stata pronunciata sentenza di merito anche non pasticciata.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della norma è alta in quanto specifica chiaramente i presupposti per l'esercizio dell'azione civile nel processo penale. Tuttavia, la mancanza di giurisprudenza diretta rende il quadro un po' meno chiaro.

### GAP ANALYSIS

Il Packet non contiene giurisprudenza specifica sui rapporti tra azione civile e azione penale per il risarcimento del danno da reato. Ci sarebbe bisogno di ulteriori esempi o decisioni giudiziarie che illustrino come queste due azioni interagiscono in pratica.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90` | 6.4549 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art91` | 6.3969 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art61` | 3.0969 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art548` | 2.3819 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art92` | 1.1213 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art85` | 0.8518 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545` | 0.7086 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677` | -0.8049 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art209` | -1.1859 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art676` | -1.4079 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:regio.decreto:1942-03-16;262~art2043`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 74 Legittimazione all'azione civile 1. L'azione civile per le restituzioni e per il risarcimento del danno di cui all' articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha rec

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art91`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 75 Rapporti tra azione civile e azione penale 1. L'azione civile proposta davanti al giudice civile può essere trasferita nel processo penale fino a quando in sede civile non sia stata pronunciata sentenza di merito anche non pas

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art61`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 50 Azione penale 1. Il pubblico ministero esercita l'azione penale quando non sussistono i presupposti per la richiesta di archiviazione. 2. Quando non è necessaria la querela, la richiesta, l'istanza o l'autorizzazione a procede

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art548`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 541 Condanna alle spese relative all'azione civile 1. Con la sentenza che accoglie la domanda di restituzione o di risarcimento del danno, il giudice condanna l'imputato e il responsabile civile in solido al pagamento delle spese

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art92`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 76 Costituzione di parte civile 1. L'azione civile nel processo penale è esercitata, anche a mezzo di procuratore speciale, mediante la costituzione di parte civile. 2. La costituzione di parte civile produce i suoi effetti in og

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art85`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 70. (Circostanze oggettive e soggettive) Agli effetti della legge penale: 1° sono circostanze oggettive quelle che concernono la natura, la specie, i mezzi, l'oggetto, il tempo, il luogo e ogni altra modalità, dell'azione, la gravità del danno o del perico

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 538 Condanna per la responsabilità civile 1. Quando pronuncia sentenza di condanna, il giudice decide sulla domanda per le restituzioni e il risarcimento del danno, proposta a norma degli articoli 74 e seguenti. 2. Se pronuncia c

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 652 Efficacia della sentenza penale di assoluzione nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di assoluzione pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accert

**[9]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art209`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 185. (Restituzioni e risarcimento del danno) Ogni reato obbliga alle restituzioni, a norma delle leggi civili. Ogni reato, che abbia cagionato un danno patrimoniale o non patrimoniale, obbliga al risarcimento il colpevole e le persone che, a norma delle le

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art676`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 651-bis ((Efficacia della sentenza di proscioglimento per particolare tenuità del fatto nel giudizio civile o amministrativo di danno.)) (( 1. La sentenza penale irrevocabile di proscioglimento pronunciata per particolare tenuità

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
