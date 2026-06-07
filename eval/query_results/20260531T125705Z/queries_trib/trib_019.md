# trib_019 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:41 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 9.3s (ret 0.4s + llm 8.5s) |

## Query

> Come si applica la tassazione separata ai redditi pluriennali?

## Risposta

**QUALIFICAZIONE**
La domanda riguarda la tassazione separata ai redditi pluriennali.

**NORMA APPLICABILE**
Secondo il Regio Decreto 16 marzo 1942, n. 262, Art. 1635, se durante l'affitto convenuto per più anni almeno la metà dei frutti di un anno non ancora separati perisce per caso fortuito, l'affittuario può domandare una riduzione del fitto.

**GIURISPRUDENZA**
Non sono presenti giurisprudenze specifiche relative alla tassazione separata ai redditi pluriennali nel Packet.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La mancanza di giurisprudenza rende la valutazione basata esclusivamente sulla norma applicabile. Tuttavia, l'articolo 1635 del Regio Decreto 1942-03-16, n. 262, fornisce una chiara indicazione sul comportamento da adottare in caso di perdita dei frutti.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze relative alla tassazione separata ai redditi pluriennali, che potrebbero fornire ulteriori dettagli o orientamenti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La domanda riguarda la tassazione separata ai redditi pluriennali.

### NORMA APPLICABILE

Secondo il Regio Decreto 16 marzo 1942, n. 262, Art. 1635, se durante l'affitto convenuto per più anni almeno la metà dei frutti di un anno non ancora separati perisce per caso fortuito, l'affittuario può domandare una riduzione del fitto.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art1635', 'claim': "Se durante l'affitto convenuto per più anni almeno la metà dei frutti di un anno non ancora separati perisce per caso fortuito, l'affittuario può domandare una riduzione del fitto.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non sono presenti giurisprudenze specifiche relative alla tassazione separata ai redditi pluriennali nel Packet.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La mancanza di giurisprudenza rende la valutazione basata esclusivamente sulla norma applicabile. Tuttavia, l'articolo 1635 del Regio Decreto 1942-03-16, n. 262, fornisce una chiara indicazione sul comportamento da adottare in caso di perdita dei frutti.

### GAP ANALYSIS

Il Packet manca di giurisprudenze relative alla tassazione separata ai redditi pluriennali, che potrebbero fornire ulteriori dettagli o orientamenti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1693` | 2.5564 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art105` | -0.0603 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art1` | -3.6725 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2984` | -4.3630 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art5` | -4.9421 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1558` | -5.0580 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art1` | -5.2349 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2539` | -5.4589 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art603` | -5.6268 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11` | -5.8664 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art17`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1693`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1635. (Perdita fortuita dei frutti negli affitti pluriennali). Se, durante l'affitto convenuto per più anni, almeno la metà dei frutti di un anno non ancora separati perisce per caso fortuito, l'affittuario può domandare una riduzione del fitto, salvo che la

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art105`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Nell'applicazione delle disposizioni concernenti le imposte sui redditi sono fatti salvi gli accordi internazionali resi esecutivi in Italia.

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art1`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 bligate alla tenuta di scritture contabili che possiedono soltanto redditi esenti e redditi soggetti a ritenuta alla fonte a titolo di imposta nonché redditi fondiari per un importo complessivo, al lordo della deduzione ((di cui all'a

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2984`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2759. ((Crediti per le imposte sul reddito.)) ((I crediti dello Stato per l'imposta sul reddito delle persone fisiche, sul reddito delle persone giuridiche e per l'imposta locale sui redditi, dovuta per i due anni anteriori a quello in cui si procede, hanno p

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art5`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 5 (( (Certificazioni e documentazioni riguardanti la dichiarazione dei soggetti all'imposta sul reddito delle persone giuridiche) )) (( 1. I soggetti all'imposta sul reddito delle persone giuridiche devono conservare, per il peri

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1558`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1508. (Vendita separata di cosa indivisa). Se i comproprietari di una cosa non l'hanno venduta congiuntamente e per intero, ma ciascuno ha venduto la sola sua quota, essi possono separatamente esercitare il diritto di riscatto sopra la quota che loro spettava

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art1`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Ogni soggetto passivo deve dichiarare annualmente i redditi posseduti anche se non ne consegue alcun debito d'imposta. I soggetti obbligati alla tenuta di scritture contabili, di cui al successivo art. 13, devono presentare la dichiar

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2539`

> REGIO DECRETO 16 marzo 1942, n. 262  con l'indicazione dei diritti patrimoniali e partecipativi che conferiscono e delle principali caratteristiche delle operazioni relative; 19-bis) i finanziamenti effettuati dai soci alla società, ripartiti per scadenze e con la separata indicazione di quelli con

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art603`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 514. (Rapporti tra creditori separatisti e non separatisti). I creditori e i legatari che hanno esercitato la separazione hanno diritto di soddisfarsi sui beni separati a preferenza dei creditori e dei legatari che non l'hanno esercitata, quando il valore del

**[10]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 , e 11, comma 1-bis, del decreto legislativo 19 giugno 1997, n. 218 , nel testo vigente alla data di entrata in vigore della presente legge, continuano ad applicarsi agli inviti al contraddittorio in materia di imposte sui redditi, di imposta sul valore agg

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
