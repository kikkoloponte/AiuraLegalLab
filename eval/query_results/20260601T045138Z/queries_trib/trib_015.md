# trib_015 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:31 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 27.1s (ret 0.2s + llm 26.7s) |

## Query

> Qual è il regime IVA delle prestazioni di servizi intracomunitarie?

## Risposta

**QUALIFICAZIONE**
Le prestazioni di servizi intracomunitarie sono soggette al regime forfetario previsto dal D.P.R. n. 917 del 22 dicembre 1986, Art. 145.

**NORMA APPLICABILE**
Il regime forfetario è specificato nel D.P.R. n. 917 del 22 dicembre 1986, Art. 145.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano al regime IVA delle prestazioni di servizi intracomunitarie. Tuttavia, il regime forfetario è generalmente interpretato in base alla normativa vigente.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il regime forfetario previsto dal D.P.R. n. 917 del 22 dicembre 1986, Art. 145, è considerato solido in quanto specifica chiaramente il trattamento fiscale delle prestazioni di servizi intracomunitarie.

**GAP ANALYSIS**
Non ci sono gap notevoli nel Packet per questa domanda. Tuttavia, sarebbe utile avere una giurisprudenza specifica o ulteriori dettagli normativi.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le prestazioni di servizi intracomunitarie sono soggette al regime forfetario previsto dal D.P.R. n. 917 del 22 dicembre 1986, Art. 145.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art145', 'claim': 'Le prestazioni di servizi intracomunitarie sono soggette al regime forfetario.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917'}*

### NORMA APPLICABILE

Il regime forfetario è specificato nel D.P.R. n. 917 del 22 dicembre 1986, Art. 145.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art145', 'claim': 'Il regime forfetario è specificato nel D.P.R. n. 917 del 22 dicembre 1986, Art. 145.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano al regime IVA delle prestazioni di servizi intracomunitarie. Tuttavia, il regime forfetario è generalmente interpretato in base alla normativa vigente.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il regime forfetario previsto dal D.P.R. n. 917 del 22 dicembre 1986, Art. 145, è considerato solido in quanto specifica chiaramente il trattamento fiscale delle prestazioni di servizi intracomunitarie.

### GAP ANALYSIS

Non ci sono gap notevoli nel Packet per questa domanda. Tuttavia, sarebbe utile avere una giurisprudenza specifica o ulteriori dettagli normativi.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | 5.4400 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art33` | 0.0838 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -1.4138 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | -2.5758 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -3.1340 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72` | -3.5279 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art30` | -4.6296 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72` | -7.2422 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72` | -7.8226 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art185` | -7.9016 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi. 3. Il regime forfetario previsto nel presente articolo si estende di anno in anno qualora i limiti indicati al comma 1 non ven

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art33`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  nei termini previsti dalle vigenti disposizioni di legge. Sono fatti salvi gli effetti prodotti nei periodi d'imposta precedenti. La revoca o la decadenza dal regime precludono l'esercizio di una nuova opzione. 5. Le persone fisiche d

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia. (126) 3. Ai fini della determinazione in denaro dei valori di cui al comma 1, compresi quelli dei beni ceduti e dei servizi prestati al co

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 145 ((Regime forfetario degli enti non commerciali )) (( 1. Fatto salvo quanto previsto, per le associazioni sportive dilettantistiche, dalla legge 16 dicembre 1991, n. 398 , e, per le associazioni senza scopo di lucro e per le pr

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  MODIFICAZIONI DALLA L. 24 LUGLIO 2008, N. 126 ; c) le somministrazioni di vitto da parte del datore di lavoro nonché quelle in mense organizzate direttamente dal datore di lavoro o gestite da terzi; le prestazioni sostitutive delle so

**[6]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  9 e 10 della legge 23 ottobre 1985, n. 595 . Le convenzioni possono essere stipulate anche con istituzioni sanitarie private gestite da persone fisiche e da società che erogano prestazioni poliambulatoriali, di laboratorio generale e specialistico in materi

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art30`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 17-bis (( (Acquisto di pubblicità on line) )) (( 1. I soggetti passivi che intendano acquistare servizi di pubblicità e link sponsorizzati on line, anche attraverso centri media e operatori terzi, sono obbligati ad acquistarli da s

**[8]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  cento delle tariffe convenzionate con il limite massimo di lire 70.000 per ciclo di cura; il limite massimo di partecipazione alla spesa farmaceutica è fissato in lire 50.000 per ricetta oltre al pagamento della quota fissa per singola prescrizione. Le quot

**[9]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  comunitarie e, limitatamente alle modalità di erogazione, degli accordi di lavoro per il personale dipendente; b) gli standard organizzativi e di attività sono determinati a fini di calcolo del parametro capitario di finanziamento e non costituiscono vincol

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art185`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 , regolamento, atto costitutivo o statuto fanno parte di un'unica organizzazione locale o nazionale, dei rispettivi associati o partecipanti e dei tesserati dalle rispettive organizzazioni nazionali, nonché le cessioni anche a terzi di

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
