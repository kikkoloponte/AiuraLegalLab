# trib_004 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:27 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 28.3s (ret 0.2s + llm 27.8s) |

## Query

> Quali sono i presupposti per l'accertamento sintetico del reddito?

## Risposta

**QUALIFICAZIONE**
I presupposti per l'accertamento sintetico del reddito sono descritti nel DECRETO LEGISLATIVO 19 giugno 1997, n. 218.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 17 prevede che il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta la scadenza del termine di sospensione.

**GIURISPRUDENZA**
Non sono presenti giurisprudenze specifiche sulle norme relative all'accertamento sintetico del reddito.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le disposizioni in materia di accertamento sono chiare e specifiche, ma non ci sono giurisprudenze contrastanti. La solidità della norma è alta.

**GAP ANALYSIS**
Non sono presenti giurisprudenze relative all'accertamento sintetico del reddito nel Packet.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

I presupposti per l'accertamento sintetico del reddito sono descritti nel DECRETO LEGISLATIVO 19 giugno 1997, n. 218.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art17', 'claim': 'Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 prevedeva le disposizioni comuni in materia di accertamento.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 17 prevede che il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta la scadenza del termine di sospensione.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art17', 'claim': "Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 17 prevede che il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta la scadenza del termine di sospensione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non sono presenti giurisprudenze specifiche sulle norme relative all'accertamento sintetico del reddito.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le disposizioni in materia di accertamento sono chiare e specifiche, ma non ci sono giurisprudenze contrastanti. La solidità della norma è alta.

### GAP ANALYSIS

Non sono presenti giurisprudenze relative all'accertamento sintetico del reddito nel Packet.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49` | 4.3310 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | 3.6035 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15` | 2.5928 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 2.4579 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | 1.1299 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 0.8101 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art97` | -0.2312 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99` | -0.5343 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art68` | -0.5679 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207` | -1.0874 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 39 ((Decorrenza delle variazioni 1. Le variazioni del reddito risultanti dalle revisioni effettuate a norma dell'articolo 35 hanno effetto dal 1 gennaio dell'anno successivo al triennio in cui si sono verificati i presupposti per

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Ai fini dell'accertamento sono obbligati alla tenuta di scritture contabili, secondo le disposizioni di questo titolo: a) le società soggette all'imposta sul reddito delle persone giuridiche; b) gli enti pubblici e privati diversi dal

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[5]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  qualora ne ricorrano i presupposti, successivamente alla scadenza del termine di sospensione. L'impugnazione dell'atto comporta rinuncia all'istanza. (23) 4. Entro quindici giorni dalla ricezione dell'istanza di cui ai commi 2 e 2-bis, l'ufficio, anche tel

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art97`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 La stessa imposta non può essere applicata più volte in dipendenza dello stesso presupposto, neppure nei confronti di soggetti diversi. ((L'imposta personale pagata dal soggetto erogante a titolo definitivo a seguito di accertamento è

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 i dell'articolo 55. ((209)) 3. L'avviso di accertamento di cui ai commi 1 e 2, emesso entro i termini di cui all'articolo 57, costituisce titolo esecutivo ai fini della riscossione. 4. Qualora l'Amministrazione finanziaria verifichi sul

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art68`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 41-bis (Accertamento parziale) 1. Senza pregiudizio dell'ulteriore azione accertatrice nei termini stabiliti dall'articolo 43, i competenti uffici dell'Agenzia delle entrate, qualora ((dalle attività istruttorie di cui all'artico

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 'aliquota media applicata sul reddito del soggetto cui sono imputati e, comunque, non inferiore all'aliquota ordinaria dell'imposta sul reddito delle società. 9. Dall'imposta determinata ai sensi del comma 8 sono ammesse in detrazione,

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
