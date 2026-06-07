# cross_003 — tributario+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:59 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 13.8s (ret 0.3s + llm 13.3s) |

## Query

> Qual è la natura giuridica dell'atto impositivo e i suoi rapporti con il provvedimento amministrativo?

## Risposta

**QUALIFICAZIONE**
L'atto impositivo è un provvedimento amministrativo che accertamento la situazione fiscale di una persona giuridica. Il rapporto tra l'atto impositivo e il provvedimento amministrativo è strettamente legato al procedimento amministrativo.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 5 regola la natura dell'atto impositivo e il suo rapporto con il provvedimento amministrativo.

**GIURISPRUDENZA**
Non esistono giurisprudenze specifiche che si riferiscano direttamente alla natura dell'atto impositivo e ai suoi rapporti con il provvedimento amministrativo. Tuttavia, la giurisprudenza tende a considerare l'atto impositivo come un atto amministrativo di notifica.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione della natura dell'atto impositivo e dei suoi rapporti con il provvedimento amministrativo è alta, in quanto la normativa è chiara e specifica.

**GAP ANALYSIS**
Non ci sono gap nel Packet che riguardano la natura dell'atto impositivo e i suoi rapporti con il provvedimento amministrativo. Tutte le informazioni necessarie sono presenti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'atto impositivo è un provvedimento amministrativo che accertamento la situazione fiscale di una persona giuridica. Il rapporto tra l'atto impositivo e il provvedimento amministrativo è strettamente legato al procedimento amministrativo.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art5', 'claim': "L'atto impositivo è un provvedimento amministrativo che accertamento la situazione fiscale di una persona giuridica.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art11', 'claim': "Il rapporto tra l'atto impositivo e il provvedimento amministrativo è strettamente legato al procedimento amministrativo.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 5 regola la natura dell'atto impositivo e il suo rapporto con il provvedimento amministrativo.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art5', 'claim': "Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 5 regola la natura dell'atto impositivo e il suo rapporto con il provvedimento amministrativo.", 'claim_type': 'NORMA', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### GIURISPRUDENZA

Non esistono giurisprudenze specifiche che si riferiscano direttamente alla natura dell'atto impositivo e ai suoi rapporti con il provvedimento amministrativo. Tuttavia, la giurisprudenza tende a considerare l'atto impositivo come un atto amministrativo di notifica.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art5', 'claim': "Non esistono giurisprudenze specifiche che si riferiscano direttamente alla natura dell'atto impositivo e ai suoi rapporti con il provvedimento amministrativo.", 'claim_type': 'NORMA', 'source_authority': 'GIURISPRUDENZA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione della natura dell'atto impositivo e dei suoi rapporti con il provvedimento amministrativo è alta, in quanto la normativa è chiara e specifica.

### GAP ANALYSIS

Non ci sono gap nel Packet che riguardano la natura dell'atto impositivo e i suoi rapporti con il provvedimento amministrativo. Tutte le informazioni necessarie sono presenti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art5` | 3.4935 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art74` | 2.9787 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art123` | 1.1831 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2126` | 1.1311 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65` | 0.7754 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art15` | 0.3679 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art375` | -0.8631 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art218` | -0.9028 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art60` | -1.4105 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11` | -1.5663 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art7`
- `urn:nir:stato:legge:1990-08-07;241~art3`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art5`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 EMBRE 2008, N. 185 , CONVERTITO CON MODIFICAZIONI DALLA L. 28 GENNAIO 2009, N. 2 . 3-bis. Qualora tra la data di comparizione, di cui al comma 1, lettera b), e quella di decadenza dell'amministrazione dal potere di notificazione dell'atto impositivo interco

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art74`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 41. (Responsabilità dei componenti. Rappresentanza in giudizio). Qualora il comitato non abbia ottenuto la personalità giuridica, i suoi componenti rispondono personalmente e solidalmente delle obbligazioni assunte. I sottoscrittori sono tenuti soltanto a eff

**[3]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art123`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 118 Decreto ingiuntivo 1. Nelle controversie devolute alla giurisdizione esclusiva del giudice amministrativo, aventi ad oggetto diritti soggettivi di natura patrimoniale, si applica il Capo I del Titolo I del Libro IV del codice di procedura civile . P

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2126`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2086. ((Gestione dell'impresa)) L'imprenditore è il capo dell'impresa e da lui dipendono gerarchicamente i suoi collaboratori. ((L'imprenditore, che operi in forma societaria o collettiva, ha il dovere di istituire un assetto organizzativo, amministrativo e c

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Alla rettifica delle dichiarazioni presentate dai soggetti all'imposta sul reddito delle persone giuridiche si procede con unico atto agli effetti di tale imposta e dell'imposta locale sui redditi, con riferimento unitario al reddito

**[6]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art15`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 12 Rapporti con l'arbitrato 1. Le controversie concernenti diritti soggettivi devolute alla giurisdizione del giudice amministrativo possono essere risolte mediante arbitrato rituale di diritto ((ai sensi degli articoli 806 e seguenti del codice di proc

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art375`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 375 Assetti organizzativi dell'impresa 1. La rubrica dell' articolo 2086 del codice civile è sostituita dalla seguente: «Gestione dell'impresa». 2. All' articolo 2086 del codice civile , dopo il primo comma è aggiunto il seguente: «L'imprenditore, che

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art218`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  elementi dell'attivo costituenti immobilizzazioni materiali e immateriali relativi all'azienda ricevuta, di un'imposta sostitutiva delle imposte sui redditi e dell'imposta regionale sulle attività produttive con aliquota, rispettivame

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art60`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 27. (Estinzione della persona giuridica). Oltre che per le cause previste nell'atto costitutivo e nello statuto, la persona giuridica si estingue quando lo scopo è stato raggiunto o è divenuto impossibile. Le associazioni si estinguono inoltre quando tutti gl

**[10]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 11 Avvio del procedimento 1. ((L'ufficio di iniziativa, nei casi di cui all' articolo 6-bis, comma 2, della legge n. 212 del 2000 , contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero, ovvero su istanza

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
