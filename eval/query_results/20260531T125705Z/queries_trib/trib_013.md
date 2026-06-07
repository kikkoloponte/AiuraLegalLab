# trib_013 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:40 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 14.2s (ret 0.6s + llm 13.2s) |

## Query

> Quali sono le sanzioni per omessa dichiarazione dei redditi?

## Risposta

**QUALIFICAZIONE**
Le sanzioni per omessa dichiarazione dei redditi sono previste dal DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600.

**NORMA APPLICABILE**
Le sanzioni per omessa dichiarazione dei redditi sono previste dall'articolo 41-ter del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle sanzioni per omessa dichiarazione dei redditi.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme citate non specificano esplicitamente le sanzioni in caso di omessa dichiarazione, ma si riferiscono principalmente al controllo e alla verifica delle dichiarazioni. La mancanza di specifiche sanzioni nel Packet riduce la solidità della valutazione.

**GAP ANALYSIS**
Il Packet manca di specifiche norme che definiscano le sanzioni in caso di omessa dichiarazione dei redditi. Ci sono solo riferimenti a controlli e verifiche delle dichiarazioni.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le sanzioni per omessa dichiarazione dei redditi sono previste dal DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art4', 'claim': "La dichiarazione dei soggetti all'imposta sul reddito delle persone giuridiche è obbligatoria.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art40-bis', 'claim': 'Il controllo delle dichiarazioni proprie presentate dalle società consolidate e dalla', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art41-ter', 'claim': 'Le disposizioni di cui agli articoli 32, primo comma, numero 7), 38, 40 e 41-bis non si applicano con riferimento ai redditi di fabbricati derivanti da locazione dichiara.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Le sanzioni per omessa dichiarazione dei redditi sono previste dall'articolo 41-ter del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art41-ter', 'claim': 'Le disposizioni di cui agli articoli 32, primo comma, numero 7), 38, 40 e 41-bis non si applicano con riferimento ai redditi di fabbricati derivanti da locazione dichiara.', 'claim_type': 'NORMA', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle sanzioni per omessa dichiarazione dei redditi.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme citate non specificano esplicitamente le sanzioni in caso di omessa dichiarazione, ma si riferiscono principalmente al controllo e alla verifica delle dichiarazioni. La mancanza di specifiche sanzioni nel Packet riduce la solidità della valutazione.

### GAP ANALYSIS

Il Packet manca di specifiche norme che definiscano le sanzioni in caso di omessa dichiarazione dei redditi. Ci sono solo riferimenti a controlli e verifiche delle dichiarazioni.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art691` | 4.4061 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art15` | 4.1262 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art67` | 3.5947 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art69` | 3.5537 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art4` | 2.7279 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art66` | 2.4405 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art55` | 2.3796 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art16` | 2.3097 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art3` | 1.3024 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art1` | -0.0737 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art1`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art691`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 664 Esecuzione di altre sanzioni pecuniarie 1. Le somme dovute per sanzioni disciplinari pecuniarie o per condanna alla perdita della cauzione o in conseguenza della dichiarazione di inammissibilità o di rigetto di una richiesta,

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art15`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 15 Sanzioni applicabili nel caso di omessa impugnazione 1. Le sanzioni irrogate per le violazioni indicate nell'articolo 2, comma 5, del presente decreto, ((negli articoli 71 e 72)) del testo unico delle disposizioni concernenti l'imposta di registro,

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art67`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Gli uffici delle imposte procedono all'accertamento d'ufficio nei casi di omessa presentazione della dichiarazione o di presentazione di dichiarazioni nulle ai sensi delle disposizioni del titolo I. Nelle ipotesi di cui al precedente

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art69`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 41-ter (((Accertamento dei redditi di fabbricati) )) (( 1. Le disposizioni di cui agli articoli 32, primo comma, numero 7), 38, 40 e 41-bis non si applicano con riferimento ai redditi di fabbricati derivanti da locazione dichiara

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art4`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 4 Contenuto della dichiarazione dei soggetti all'imposta sul reddito delle persone giuridiche). 1. La dichiarazione dei soggetti all'imposta sul reddito delle persone giuridiche, oltre quanto stabilito nel secondo comma dell'arti

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art66`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 40-bis (( Rettifica delle dichiarazioni dei soggetti aderenti al consolidato nazionale )) (( 1. Ai fini dell'imposta sul reddito delle società, il controllo delle dichiarazioni proprie presentate dalle società consolidate e dalla

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art55`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 44 Sanzioni in caso di inammissibilità o di rigetto della dichiarazione di ricusazione 1. Con l'ordinanza che dichiara inammissibile o rigetta la dichiarazione di ricusazione, la parte privata che l'ha proposta può essere condann

**[8]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art16`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 16 Controlli sulla base della copia delle dichiarazioni 1. Qualora successivamente all'accertamento le dichiarazioni presentate ai fini delle imposte sui redditi e dell'imposta sul valore aggiunto risultino difformi dalle copie acquisite nel corso dell

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art3`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 3 (((Certificazioni e documenti riguardanti la dichiarazione delle persone fisiche) )) (( 1. Le persone fisiche che esercitano imprese commerciali ai sensi dell'articolo 51 del testo unico delle imposte sui redditi, approvato con

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art1`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Ogni soggetto passivo deve dichiarare annualmente i redditi posseduti anche se non ne consegue alcun debito d'imposta. I soggetti obbligati alla tenuta di scritture contabili, di cui al successivo art. 13, devono presentare la dichiar

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
