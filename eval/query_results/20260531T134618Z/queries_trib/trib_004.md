# trib_004 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:09 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 5.7s (ret 0.3s + llm 5.1s) |

## Query

> Quali sono i presupposti per l'accertamento sintetico del reddito?

## Risposta

**QUALIFICAZIONE**
I presupposti per l'accertamento sintetico del reddito sono specificati nel DECRETO LEGISLATIVO 19 giugno 1997, n. 218.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica i presupposti per l'accertamento sintetico del reddito.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

I presupposti per l'accertamento sintetico del reddito sono specificati nel DECRETO LEGISLATIVO 19 giugno 1997, n. 218.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art17', 'claim': "Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 prevedeva che quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica i presupposti per l'accertamento sintetico del reddito.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49` | 4.3310 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | 3.6035 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204` | 2.9212 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15` | 2.5928 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art92` | 2.5850 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 2.4579 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art62` | 1.8095 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2984` | 1.7977 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art2` | 1.4035 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art10` | 1.1734 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 39 ((Decorrenza delle variazioni 1. Le variazioni del reddito risultanti dalle revisioni effettuate a norma dell'articolo 35 hanno effetto dal 1 gennaio dell'anno successivo al triennio in cui si sono verificati i presupposti per

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 165 Credito d'imposta per i redditi prodotti all'estero 1. Se alla formazione del reddito complessivo concorrono redditi prodotti all'estero, le imposte ivi pagate a titolo definitivo su tali redditi sono ammesse in detrazione dal

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Ai fini dell'accertamento sono obbligati alla tenuta di scritture contabili, secondo le disposizioni di questo titolo: a) le società soggette all'imposta sul reddito delle persone giuridiche; b) gli enti pubblici e privati diversi dal

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art92`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 71 Altri redditi 1. I redditi di cui alla lettera g) del comma 1 dell'articolo 81 costituiscono reddito per l'ammontare percepito nel periodo di imposta, ridotto del 25 per cento se i diritti dalla cui utilizzazione derivano sono

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art62`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 L'ufficio delle imposte procede alla rettifica delle dichiarazioni presentate dalle persone fisiche quando il reddito complessivo dichiarato risulta inferiore a quello effettivo o non sussistono o non spettano, in tutto o in parte, le

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2984`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2759. ((Crediti per le imposte sul reddito.)) ((I crediti dello Stato per l'imposta sul reddito delle persone fisiche, sul reddito delle persone giuridiche e per l'imposta locale sui redditi, dovuta per i due anni anteriori a quello in cui si procede, hanno p

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art2`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 1 ((Presupposto dell'imposta )) (( 1. Presupposto dell'imposta sul reddito delle persone fisiche è il possesso di redditi in denaro o in natura rientranti nelle categorie indicate nell'articolo 6. ))

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art10`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 9 Determinazione dei redditi e delle perdite 1. I redditi e le perdite che concorrono a formare il reddito complessivo sono determinati distintamente per ciascuna categoria, secondo le disposizioni dei successivi capi, in base al

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
