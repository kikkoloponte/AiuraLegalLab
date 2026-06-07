# trib_001 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:26 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 13.6s (ret 0.2s + llm 13.3s) |

## Query

> Quali sono i principi fondamentali dello Statuto del contribuente?

## Risposta

**QUALIFICAZIONE**
Il principale principio fondamentale dello Statuto del contribuente è la tutela dei diritti e delle garanzie del contribuente durante le verifiche fiscali.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il principio è chiaramente enunciato nella legge e non esistono contrasti giurisprudenziali.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il principale principio fondamentale dello Statuto del contribuente è la tutela dei diritti e delle garanzie del contribuente durante le verifiche fiscali.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art13', 'claim': "È istituito il Garante nazionale del contribuente, organo monocratico con sede in Roma che opera in piena autonomia e che è scelto e nominato dal Ministro dell'economia e delle finanze per la durata di quattro anni.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'Legge 27 luglio 2000, n. 212'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il principio è chiaramente enunciato nella legge e non esistono contrasti giurisprudenziali.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 1.6940 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | 1.0487 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60` | -0.3100 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art138` | -2.0774 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art11` | -2.6561 | hybrid_rrf |  |
| 6 | `urn:nir:stato:legge:2000-07-27;212~art1` | -3.3706 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art13` | -3.4999 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art93` | -4.1326 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge:2000-07-27;212~art12` | -4.1740 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art94` | -4.2544 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 6 Istanza del contribuente 1. Il contribuente nei cui confronti sono stati effettuati accessi, ispezioni o verifiche ai sensi degli articoli 33 del decreto del Presidente della Repubblica 29 settembre 1973, n. 600 , e 52 del decreto del Presidente dell

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  2000, n. 212 , recante lo Statuto dei diritti del contribuente)) . Le persone interposte, che provino di aver pagato imposte in relazione a redditi successivamente imputati, a norma del comma terzo, ad altro contribuente, possono chi

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art138`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 quinquies. I commi 3-bis, 3-ter e 3-quater non si applicano ai soggetti che redigono il bilancio in base ai principi contabili internazionali di cui al regolamento (CE) n. 1606/2002 del Parlamento europeo e del Consiglio, del 19 luglio

**[5]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art11`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 ividuazione del contribuente, per la determinazione dell'ammontare delle operazioni e dell'imposta nonchè per l'effettuazione dei controlli e gli altri elementi richiesti nel modello di dichiarazione, esclusi quelli che l'Amministrazione finanziaria è in gra

**[6]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

**[7]** `urn:nir:stato:legge:2000-07-27;212~art13`

> LEGGE 27 luglio 2000, n. 212 Art. 13 (( (Garante nazionale del contribuente). )) (( 1. È istituito il Garante nazionale del contribuente, organo monocratico con sede in Roma che opera in piena autonomia e che è scelto e nominato dal Ministro dell'economia e delle finanze per la durata di quattro ann

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art93`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633  decreto, ovvero da altro documento conservato a norma dello stesso articolo ((o da atto registrato presso l'ufficio del registro.)) I beni che si trovano nel luogo o in uno dei luoghi in cui il  contribuente esercita la sua attività si

**[9]** `urn:nir:stato:legge:2000-07-27;212~art12`

> LEGGE 27 luglio 2000, n. 212 Art. 12 Diritti e garanzie del contribuente sottoposto a verifiche fiscali 1. Tutti gli accessi, ispezioni e verifiche fiscali nei locali destinati all'esercizio di attività commerciali, industriali, agricole, artistiche o professionali sono effettuati sulla base di esig

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art94`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 . 239 , quando, successivamente alla loro costituzione, un soggetto residente nel territorio dello Stato effettui in favore del trust un'attribuzione che importi il trasferimento di proprietà di beni immobili o la costituzione o il tra

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
