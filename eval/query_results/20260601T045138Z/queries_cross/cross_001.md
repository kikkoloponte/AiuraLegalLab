# cross_001 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:02 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 32.8s (ret 0.5s + llm 17.7s) |

## Query

> Quali sono i rapporti tra azione civile e azione penale per il risarcimento del danno da reato?

## Risposta

**QUALIFICAZIONE**
L'azione civile per il risarcimento del danno da reato può essere esercitata nel processo penale e ha rapporti con l'azione penale.

**NORMA APPLICABILE**
Le norme applicabili sono Articoli 74, 538 e 287 del Codice di Procедура Пенальна.

**GIURISPRUDENZA**
Non sono presenti giurisprudenze specifiche nel Packet.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme esistenti sono chiare e forniscono un quadro completo per la gestione delle azioni civili e penali per il risarcimento del danno da reato.

**GAP ANALYSIS**
Non sono presenti gap nel Packet.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'azione civile per il risarcimento del danno da reato può essere esercitata nel processo penale e ha rapporti con l'azione penale.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90', 'claim': "L'azione civile per le restituzioni e per il risarcimento del danno di cui all'articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha recato danno.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art538', 'claim': 'Il giudice decide sulla domanda per le restituzioni e il risarcimento del danno, proposta a norma degli articoli 74 e seguenti.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-07;209~art144', 'claim': "Il danneggiato per sinistro causato dalla circolazione di un veicolo o di un natante, per i quali vi è obbligo di assicurazione, ha azione diretta per il risarcimento del danno nei confronti dell'impresa di assicurazione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-07;209~art145', 'claim': "Nel caso si applichi la procedura di cui all'articolo 148, l'azione per il risarcimento dei danni causati dalla circolazione dei veicoli e dei natanti, per i quali vi è obbligo di assicurazione, può essere esercitata.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-07;209~art287', 'claim': "Nelle ipotesi previste dall'articolo 283, comma 1, lettere a), b) (( , c-bis) ), d) , d-bis) e d-ter), l'azione per il risarcimento dei danni causati dalla circolazione dei veicoli e dei natanti, per i quali vi è obbligo di assicurazione, può essere esercitata.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Le norme applicabili sono Articoli 74, 538 e 287 del Codice di Procедура Пенальна.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art74', 'claim': "L'azione civile per le restituzioni e per il risarcimento del danno di cui all'articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha recato danno.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art538', 'claim': 'Il giudice decide sulla domanda per le restituzioni e il risarcimento del danno, proposta a norma degli articoli 74 e seguenti.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-07;209~art287', 'claim': "Nelle ipotesi previste dall'articolo 283, comma 1, lettere a), b) (( , c-bis) ), d) , d-bis) e d-ter), l'azione per il risarcimento dei danni causati dalla circolazione dei veicoli e dei natanti, per i quali vi è obbligo di assicurazione, può essere esercitata.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non sono presenti giurisprudenze specifiche nel Packet.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme esistenti sono chiare e forniscono un quadro completo per la gestione delle azioni civili e penali per il risarcimento del danno da reato.

### GAP ANALYSIS

Non sono presenti gap nel Packet.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90` | 6.4549 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art91` | 6.3969 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2005-09-07;209~art144` | 4.4415 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2005-09-07;209~art145` | 3.9852 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art548` | 2.3819 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:2005-09-07;209~art287` | 2.1835 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545` | 0.7086 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.legislativo:2005-09-07;209~art141` | -0.5674 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677` | -0.8049 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2001-06-08;231~art1` | -1.1464 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:regio.decreto:1942-03-16;262~art2043`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 74 Legittimazione all'azione civile 1. L'azione civile per le restituzioni e per il risarcimento del danno di cui all' articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha rec

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art91`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 75 Rapporti tra azione civile e azione penale 1. L'azione civile proposta davanti al giudice civile può essere trasferita nel processo penale fino a quando in sede civile non sia stata pronunciata sentenza di merito anche non pas

**[3]** `urn:nir:stato:decreto.legislativo:2005-09-07;209~art144`

> DECRETO LEGISLATIVO 7 settembre 2005, n. 209 Art. 144 Azione diretta del danneggiato 1. Il danneggiato per sinistro causato dalla circolazione di un veicolo o di un natante, per i quali vi è obbligo di assicurazione, ha azione diretta per il risarcimento del danno nei confronti dell'impresa di assic

**[4]** `urn:nir:stato:decreto.legislativo:2005-09-07;209~art145`

> DECRETO LEGISLATIVO 7 settembre 2005, n. 209 Art. 145 Proponibilità dell'azione di risarcimento 1. Nel caso si applichi la procedura di cui all'articolo 148, l'azione per il risarcimento dei danni causati dalla circolazione dei veicoli e dei natanti, per i quali vi è obbligo di assicurazione, può es

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art548`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 541 Condanna alle spese relative all'azione civile 1. Con la sentenza che accoglie la domanda di restituzione o di risarcimento del danno, il giudice condanna l'imputato e il responsabile civile in solido al pagamento delle spese

**[6]** `urn:nir:stato:decreto.legislativo:2005-09-07;209~art287`

> DECRETO LEGISLATIVO 7 settembre 2005, n. 209 Art. 287 Esercizio dell'azione di risarcimento 1. Nelle ipotesi previste dall'articolo 283, comma 1, lettere a), b) (( , c-bis) )) ,d) , d-bis) e d-ter), l'azione per il risarcimento dei danni causati dalla circolazione dei veicoli e dei natanti, per i qu

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 538 Condanna per la responsabilità civile 1. Quando pronuncia sentenza di condanna, il giudice decide sulla domanda per le restituzioni e il risarcimento del danno, proposta a norma degli articoli 74 e seguenti. 2. Se pronuncia c

**[8]** `urn:nir:stato:decreto.legislativo:2005-09-07;209~art141`

> DECRETO LEGISLATIVO 7 settembre 2005, n. 209 Art. 141 Risarcimento del terzo trasportato 1. Salva l'ipotesi di sinistro cagionato da caso fortuito, il danno subito dal terzo trasportato è risarcito dall'impresa di assicurazione del veicolo sul quale era a bordo al momento del sinistro entro il massi

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 652 Efficacia della sentenza penale di assoluzione nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di assoluzione pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accert

**[10]** `urn:nir:stato:decreto.legislativo:2001-06-08;231~art1`

> DECRETO LEGISLATIVO 8 giugno 2001, n. 231  responsabilità; v) prevedere che il riconoscimento del danno a seguito dell'azione di risarcimento spettante al singolo socio o al terzo nei confronti degli amministratori dei soggetti di cui all'alinea del presente comma, di cui sia stata accertata la resp

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
