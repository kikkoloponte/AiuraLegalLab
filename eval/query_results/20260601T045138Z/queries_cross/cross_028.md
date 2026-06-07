# cross_028 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:14 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 27.4s (ret 0.2s + llm 26.9s) |

## Query

> Qual è il regime della prescrizione del diritto al risarcimento del danno derivante da reato?

## Risposta

**QUALIFICAZIONE**
Il regime della prescrizione del diritto al risarcimento del danno derivante da reato è stato chiesto. Si tratta di un tema legato alla limitazione temporale dei diritti civili.

**NORMA APPLICABILE**
La norma applicabile è l'articolo 2947 del Codice Civile.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente al regime della prescrizione del diritto al risarcimento del danno derivante da reato. Tuttavia, la norma generale è quella prevista dall'articolo 2947 del Codice Civile.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione del regime della prescrizione è alta in quanto la norma è chiara e specifica.

**GAP ANALYSIS**
Non ci sono gap nel Packet per quanto riguarda il tema della prescrizione del diritto al risarcimento del danno derivante da reato. Tuttavia, sarebbe utile avere giurisprudenze specifiche su questo argomento.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il regime della prescrizione del diritto al risarcimento del danno derivante da reato è stato chiesto. Si tratta di un tema legato alla limitazione temporale dei diritti civili.

*Citazioni: {'source_id': 'CC_ART_2947', 'claim': 'Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### NORMA APPLICABILE

La norma applicabile è l'articolo 2947 del Codice Civile.

*Citazioni: {'source_id': 'CC_ART_2947', 'claim': 'Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente al regime della prescrizione del diritto al risarcimento del danno derivante da reato. Tuttavia, la norma generale è quella prevista dall'articolo 2947 del Codice Civile.

*Citazioni: {'source_id': 'CC_ART_2947', 'claim': 'Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione del regime della prescrizione è alta in quanto la norma è chiara e specifica.

### GAP ANALYSIS

Non ci sono gap nel Packet per quanto riguarda il tema della prescrizione del diritto al risarcimento del danno derivante da reato. Tuttavia, sarebbe utile avere giurisprudenze specifiche su questo argomento.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3177` | 7.1858 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art125` | 6.5833 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1263` | 4.4642 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1544` | 4.1192 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art671` | 3.7679 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art175` | 3.4598 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90` | 3.3744 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art45` | 3.2748 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2005-09-07;209~art148` | 3.2713 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3184` | 3.0871 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3177`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2947. (Prescrizione del diritto al risarcimento del danno). Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato. Per il risarcimento del danno prodotto dalla circolazione dei

**[2]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art125`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 125 Prescrizione 1. Il diritto al risarcimento si prescrive in tre anni dal giorno in cui il danneggiato ha avuto o avrebbe dovuto avere conoscenza del danno, del difetto e dell'identità del responsabile. 2. Nel caso di aggravamento del danno, la pre

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1263`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1218. (Responsabilità del debitore). Il debitore che non esegue esattamente la prestazione dovuta è tenuto al risarcimento del danno, se non prova che l'inadempimento o il ritardo è stato determinato da impossibilità della prestazione derivante da causa a lui

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1544`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1494. (Risarcimento del danno). In ogni caso il venditore è tenuto verso il compratore al risarcimento del danno, se non prova di avere ignorato senza colpa i vizi della cosa. Il venditore deve altresì risarcire al compratore i danni derivati dai vizi della c

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art671`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 647 Risarcimento del danno e riparazione 1. Nel caso previsto dall'articolo 630 comma 1 lettera d), lo Stato, se ha corrisposto la riparazione, si surroga, fino alla concorrenza della somma pagata, nel diritto al risarcimento dei

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art175`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 157. (Prescrizione. Tempo necessario a prescrivere). La prescrizione estingue il reato decorso il tempo corrispondente al massimo della pena edittale stabilita dalla legge e comunque un tempo non inferiore a sei anni se si tratta di delitto e a quattro ann

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 74 Legittimazione all'azione civile 1. L'azione civile per le restituzioni e per il risarcimento del danno di cui all' articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha rec

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art45`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 8 giugno 2001, n. 327  nel caso di fondatezza del ricorso o della domanda, disponga la condanna al risarcimento del danno, con esclusione della restituzione del bene senza limiti di tempo. (L) 4. Qualora il giudice amministrativo abbia escluso la restituzione

**[9]** `urn:nir:stato:decreto.legislativo:2005-09-07;209~art148`

> DECRETO LEGISLATIVO 7 settembre 2005, n. 209 Art. 148 Procedura di risarcimento 1. Per i sinistri con soli danni a cose, la richiesta di risarcimento deve recare l'indicazione degli aventi diritto al risarcimento e del luogo, dei giorni e delle ore in cui le cose danneggiate sono disponibili, per no

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3184`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2954. (Prescrizione di sei mesi). Si prescrive in sei mesi il diritto degli albergatori e degli osti per l'alloggio e il vitto che somministrano, e si prescrive nello stesso termine il diritto di tutti coloro che danno alloggio con o senza pensione.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
