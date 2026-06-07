# cross_023 — tributario+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 11:56 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 16.7s (ret 0.3s + llm 15.8s) |

## Query

> Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?

## Risposta

**QUALIFICAZIONE**
Il principio del ne bis in idem impedisce di sottoporre una persona a un processo e una pena per lo stesso fatto, mentre il doppio binario sanzionatorio tributario-penale prevede che un atto sia sanzionato sia dal diritto tributario che dal diritto penale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione del rapporto tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale richiede una analisi approfondita, poiché non ci sono norme specifiche che regolamentino tale relazione.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il principio del ne bis in idem impedisce di sottoporre una persona a un processo e una pena per lo stesso fatto, mentre il doppio binario sanzionatorio tributario-penale prevede che un atto sia sanzionato sia dal diritto tributario che dal diritto penale.

*Citazioni: {'source_id': 'CC_ART_1218', 'claim': 'Il principio del ne bis in idem impedisce di sottoporre una persona a un processo e una pena per lo stesso fatto.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione del rapporto tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale richiede una analisi approfondita, poiché non ci sono norme specifiche che regolamentino tale relazione.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2709` | 0.8772 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724` | -0.2436 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art7` | -1.4396 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317` | -3.6633 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art723` | -4.0622 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59` | -4.6593 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge:1990-08-07;241~art16` | -5.8091 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47` | -6.0516 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art51` | -6.2360 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757` | -6.7800 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art20`
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art13`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2709`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516. (( (Rapporti con i soci).)) ((Nella costituzione e nell'esecuzione dei rapporti mutualistici deve essere rispettato il principio di parità di trattamento.))

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-bis (( (Principio del mutuo riconoscimento). )) (( 1. Il principio del mutuo riconoscimento è disciplinato dalle norme del presente titolo e dalle altre disposizioni di legge attuative del diritto dell'Unione europea. 2. Le d

**[3]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art7`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis. (( (Principio della riserva di codice). )) ((Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia.))

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 317 Principio di prevalenza delle misure cautelari reali e tutela dei terzi 1. Le condizioni e i criteri di prevalenza rispetto alla gestione concorsuale delle misure cautelari reali sulle cose indicate dall'articolo 142 sono regolate dalle disposizion

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art723`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696 (( (Prevalenza del diritto dell'Unione europea, delle convenzioni e del diritto internazionale generale). )) (( 1. Nei rapporti con gli Stati membri dell'Unione europea le estradizioni, le domande di assistenza giudiziaria in

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 ((, che può essere aumentata fino al doppio, tenuto conto della causa di inammissibilità della richiesta)) . ((6-bis. Gli importi di cui al comma 6 sono adeguati ogni due anni con decreto del Ministro della giustizia, di concerto con

**[7]** `urn:nir:stato:legge:1990-08-07;241~art16`

> LEGGE 7 agosto 1990, n. 241 ioni interessate. 4-bis. ((I pareri di cui al comma 1 sono congruamente motivati, sono formulati in termini di assenso o dissenso e indicano le prescrizioni e le misure mitigatrici che rendano possibile l'assenso, quantificando altresì, ove possibile, i relativi costi. Ta

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis.1 (( (Strumenti di cooperazione amministrativa avanzata). )) (( 1. L'Amministrazione finanziaria, in attuazione del principio di economicità dell'azione amministrativa, si avvale di strumenti di cooperazione amministrativa

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art51`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  al decreto del Presidente della Repubblica 22 luglio 1998, n. 322 , senza l'applicazione delle eventuali sanzioni. 3-bis. L'ammissibilità della richiesta di accordo preventivo di cui al comma 3 è subordinata al versamento di una comm

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 721 (( (Principio di specialità).)) (( 1. La persona estradata non può essere sottoposta a restrizione della libertà personale in esecuzione di una pena o di una misura di sicurezza detentiva, né assoggettata ad altra misura rest

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
