# cross_010 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:00 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 9.1s (ret 0.3s + llm 8.6s) |

## Query

> Come opera la provvisionale nel processo penale rispetto alla domanda risarcitoria civile?

## Risposta

**QUALIFICAZIONE**
Nel processo penale, la provvisoria esecuzione delle disposizioni civili può essere richiesta quando ricorrono giustificati motivi.

**NORMA APPLICABILE**
Art. 540 del Codice di Procedura Penale.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano esplicitamente la provvisoria esecuzione delle disposizioni civili in relazione alla domanda risarcitoria.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

**GAP ANALYSIS**
CITAZIONE MANCANTE: Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano esplicitamente la provvisoria esecuzione delle disposizioni civili in relazione alla domanda risarcitoria.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Nel processo penale, la provvisoria esecuzione delle disposizioni civili può essere richiesta quando ricorrono giustificati motivi.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art547', 'claim': 'La condanna alle restituzioni e al risarcimento del danno è dichiarata provvisoriamente esecutiva, a richiesta della parte civile, quando ricorrono giustificati motivi.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Art. 540 del Codice di Procedura Penale.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art547', 'claim': 'Art. 540 del Codice di Procedura Penale.', 'claim_type': 'REFERENCE', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano esplicitamente la provvisoria esecuzione delle disposizioni civili in relazione alla domanda risarcitoria.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

### GAP ANALYSIS

CITAZIONE MANCANTE: Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano esplicitamente la provvisoria esecuzione delle disposizioni civili in relazione alla domanda risarcitoria.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90` | 1.8685 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art33` | 0.8066 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art92` | 0.6009 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art91` | -0.3881 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545` | -0.8078 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art85` | -1.2286 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art99` | -1.2286 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art547` | -1.8136 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675` | -2.2633 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art548` | -2.3354 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 74 Legittimazione all'azione civile 1. L'azione civile per le restituzioni e per il risarcimento del danno di cui all' articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha rec

**[2]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art33`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104  Nel caso in cui sia stata proposta azione di annullamento la domanda risarcitoria può essere formulata nel corso del giudizio o, comunque, sino a centoventi giorni dal passaggio in giudicato della relativa sentenza. 6. Di ogni domanda di condanna al risarci

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art92`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 76 Costituzione di parte civile 1. L'azione civile nel processo penale è esercitata, anche a mezzo di procuratore speciale, mediante la costituzione di parte civile. 2. La costituzione di parte civile produce i suoi effetti in og

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art91`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 75 Rapporti tra azione civile e azione penale 1. L'azione civile proposta davanti al giudice civile può essere trasferita nel processo penale fino a quando in sede civile non sia stata pronunciata sentenza di merito anche non pas

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 538 Condanna per la responsabilità civile 1. Quando pronuncia sentenza di condanna, il giudice decide sulla domanda per le restituzioni e il risarcimento del danno, proposta a norma degli articoli 74 e seguenti. 2. Se pronuncia c

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art85`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447  codice di procedura penale , nella parte in cui non prevede che, nel caso di responsabilità civile derivante dall'assicurazione obbligatoria prevista dall' art. 12, comma 8, della legge 11 febbraio 1992, n. 157 (Norme per la protezio

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art99`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447  codice di procedura penale , nella parte in cui non prevede che, nel caso di responsabilità civile derivante dall'assicurazione obbligatoria prevista dall' art. 12, comma 8, della legge 11 febbraio 1992, n. 157 (Norme per la protezio

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art547`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 540 Provvisoria esecuzione delle disposizioni civili 1. La condanna alle restituzioniu e al risarcimento del danno è dichiarata provvisoriamente esecutiva, a richiesta della parte civile, quando ricorrono giustificati motivi. 2.

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 651 Efficacia della sentenza penale di condanna nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di condanna pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accertamento

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art548`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 541 Condanna alle spese relative all'azione civile 1. Con la sentenza che accoglie la domanda di restituzione o di risarcimento del danno, il giudice condanna l'imputato e il responsabile civile in solido al pagamento delle spese

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
