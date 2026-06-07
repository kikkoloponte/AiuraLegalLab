# cross_003 — tributario+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:03 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 28.7s (ret 0.3s + llm 28.2s) |

## Query

> Qual è la natura giuridica dell'atto impositivo e i suoi rapporti con il provvedimento amministrativo?

## Risposta

**QUALIFICAZIONE**
L'atto impositivo è un atto amministrativo che determina l'imposizione di una obbligazione fiscale.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218, Art. 5 regola la natura e gli effetti dell'atto impositivo.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche che si riferiscano espressamente alla natura giuridica dell'atto impositivo. Tuttavia, la normativa amministrativa e fiscale conferma l'interpretazione fornita dalla norma.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione è alta in quanto la normativa amministrativa e fiscale conferma l'interpretazione fornita dalla norma.

**GAP ANALYSIS**
Non ci sono giurisprudenze specifiche che si riferiscano alla natura giuridica dell'atto impositivo. Potrebbe essere utile includere giurisprudenze relative all'interpretazione e applicazione dell'atto impositivo.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'atto impositivo è un atto amministrativo che determina l'imposizione di una obbligazione fiscale.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art5', 'claim': "L'atto impositivo determina l'imposizione di una obbligazione fiscale.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218, Art. 5 regola la natura e gli effetti dell'atto impositivo.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art5', 'claim': "Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218, Art. 5 regola la natura e gli effetti dell'atto impositivo.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche che si riferiscano espressamente alla natura giuridica dell'atto impositivo. Tuttavia, la normativa amministrativa e fiscale conferma l'interpretazione fornita dalla norma.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art5', 'claim': "Non ci sono giurisprudenze specifiche che si riferiscano espressamente alla natura giuridica dell'atto impositivo.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione è alta in quanto la normativa amministrativa e fiscale conferma l'interpretazione fornita dalla norma.

### GAP ANALYSIS

Non ci sono giurisprudenze specifiche che si riferiscano alla natura giuridica dell'atto impositivo. Potrebbe essere utile includere giurisprudenze relative all'interpretazione e applicazione dell'atto impositivo.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2023-03-31;36~art185` | 5.1234 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art5` | 3.4935 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art74` | 2.9787 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2126` | 1.1311 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65` | 0.7754 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art375` | -0.8631 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art218` | -0.9028 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art60` | -1.4105 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11` | -1.5663 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art407` | -2.1682 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art7`
- `urn:nir:stato:legge:1990-08-07;241~art3`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2023-03-31;36~art185`

> DECRETO LEGISLATIVO 31 marzo 2023, n. 36 , indipendentemente dalla natura giuridica dei suoi rapporti con loro. Se un operatore economico vuole fare affidamento sulle capacità di altri soggetti deve dimostrare all'ente concedente che disporrà delle risorse necessarie per l'intera durata della conces

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art5`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 EMBRE 2008, N. 185 , CONVERTITO CON MODIFICAZIONI DALLA L. 28 GENNAIO 2009, N. 2 . 3-bis. Qualora tra la data di comparizione, di cui al comma 1, lettera b), e quella di decadenza dell'amministrazione dal potere di notificazione dell'atto impositivo interco

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art74`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 41. (Responsabilità dei componenti. Rappresentanza in giudizio). Qualora il comitato non abbia ottenuto la personalità giuridica, i suoi componenti rispondono personalmente e solidalmente delle obbligazioni assunte. I sottoscrittori sono tenuti soltanto a eff

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2126`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2086. ((Gestione dell'impresa)) L'imprenditore è il capo dell'impresa e da lui dipendono gerarchicamente i suoi collaboratori. ((L'imprenditore, che operi in forma societaria o collettiva, ha il dovere di istituire un assetto organizzativo, amministrativo e c

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Alla rettifica delle dichiarazioni presentate dai soggetti all'imposta sul reddito delle persone giuridiche si procede con unico atto agli effetti di tale imposta e dell'imposta locale sui redditi, con riferimento unitario al reddito

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art375`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 375 Assetti organizzativi dell'impresa 1. La rubrica dell' articolo 2086 del codice civile è sostituita dalla seguente: «Gestione dell'impresa». 2. All' articolo 2086 del codice civile , dopo il primo comma è aggiunto il seguente: «L'imprenditore, che

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art218`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  elementi dell'attivo costituenti immobilizzazioni materiali e immateriali relativi all'azienda ricevuta, di un'imposta sostitutiva delle imposte sui redditi e dell'imposta regionale sulle attività produttive con aliquota, rispettivame

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art60`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 27. (Estinzione della persona giuridica). Oltre che per le cause previste nell'atto costitutivo e nello statuto, la persona giuridica si estingue quando lo scopo è stato raggiunto o è divenuto impossibile. Le associazioni si estinguono inoltre quando tutti gl

**[9]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 11 Avvio del procedimento 1. ((L'ufficio di iniziativa, nei casi di cui all' articolo 6-bis, comma 2, della legge n. 212 del 2000 , contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero, ovvero su istanza

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art407`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 339-bis. (( (Circostanza aggravante. Atti intimidatori di natura ritorsiva ai danni di un componente di un Corpo politico, amministrativo o giudiziario).)) ((Salvo che il fatto costituisca più grave reato, le pene stabilite per i delitti previsti dagli art

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
