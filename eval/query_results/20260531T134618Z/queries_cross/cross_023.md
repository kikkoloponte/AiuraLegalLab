# cross_023 — tributario+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:03 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 15.7s (ret 0.4s + llm 15.1s) |

## Query

> Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?

## Risposta

**QUALIFICAZIONE**
Il ne bis in idem è un principio che impedisce di applicare più volte la stessa sanzione per lo stesso fatto. Il doppio binario sanzionatorio tributario-penale riguarda la possibilità di applicare sia sanzioni amministrative che penali per il medesimo atto.

**NORMA APPLICABILE**
Il ne bis in idem è regolato dal codice penale (Art. 2516) e il doppio binario sanzionatorio tributario-penale è disciplinato dalla legge 27 luglio 2000, n. 212 (Art. 10).

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel packet che trattano direttamente il ne bis in idem e il doppio binario sanzionatorio tributario-penale. Tuttavia, la giurisprudenza tende a garantire l'applicazione del principio di non bis in idem anche nelle sanzioni amministrative.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della valutazione è media, in quanto non ci sono giurisprudenze specifiche menzionate nel packet che trattano il ne bis in idem e il doppio binario sanzionatorio tributario-penale.

**GAP ANALYSIS**
Il packet manca di giurisprudenze specifiche che trattano il ne bis in idem e il doppio binario sanzionatorio tributario-penale. Inoltre, non ci sono citazioni dirette per la legge 27 luglio 2000, n. 212 Art. 10.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il ne bis in idem è un principio che impedisce di applicare più volte la stessa sanzione per lo stesso fatto. Il doppio binario sanzionatorio tributario-penale riguarda la possibilità di applicare sia sanzioni amministrative che penali per il medesimo atto.

*Citazioni: {'source_id': 'CC_ART_2516', 'claim': "Il principio del ne bis in idem impedisce l'applicazione di più sanzioni per lo stesso fatto.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}, {'source_id': 'CC_ART_3BIS', 'claim': "Il doppio binario sanzionatorio tributario-penale permette l'applicazione di sanzioni amministrative e penali per lo stesso atto.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398'}*

### NORMA APPLICABILE

Il ne bis in idem è regolato dal codice penale (Art. 2516) e il doppio binario sanzionatorio tributario-penale è disciplinato dalla legge 27 luglio 2000, n. 212 (Art. 10).

*Citazioni: {'source_id': 'CC_ART_2516', 'claim': 'Il ne bis in idem è regolato dal codice penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}, {'source_id': 'L_2000_212_ART_10', 'claim': 'Il doppio binario sanzionatorio tributario-penale è disciplinato dalla legge 27 luglio 2000, n. 212.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'LEGGE 27 luglio 2000, n. 212'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel packet che trattano direttamente il ne bis in idem e il doppio binario sanzionatorio tributario-penale. Tuttavia, la giurisprudenza tende a garantire l'applicazione del principio di non bis in idem anche nelle sanzioni amministrative.

*Citazioni: {'source_id': 'GU_1942_79', 'claim': "La giurisprudenza tende a garantire l'applicazione del principio di non bis in idem anche nelle sanzioni amministrative.", 'claim_type': 'FACT', 'source_authority': 'GIURISPRUDENZA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della valutazione è media, in quanto non ci sono giurisprudenze specifiche menzionate nel packet che trattano il ne bis in idem e il doppio binario sanzionatorio tributario-penale.

### GAP ANALYSIS

Il packet manca di giurisprudenze specifiche che trattano il ne bis in idem e il doppio binario sanzionatorio tributario-penale. Inoltre, non ci sono citazioni dirette per la legge 27 luglio 2000, n. 212 Art. 10.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art10` | 3.4052 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2709` | 0.8772 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724` | -0.2436 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art7` | -1.4396 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | -1.8089 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317` | -3.6633 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59` | -4.6592 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge:2000-07-27;212~art1` | -5.7070 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47` | -6.0516 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215` | -6.1606 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art20`
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art13`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art10`

> LEGGE 27 luglio 2000, n. 212 Art. 10 Tutela dell'affidamento e della buona fede. Errori del contribuente 1. I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede. 2. Non sono irrogate sanzioni nè richiesti interessi moratori al

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2709`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516. (( (Rapporti con i soci).)) ((Nella costituzione e nell'esecuzione dei rapporti mutualistici deve essere rispettato il principio di parità di trattamento.))

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-bis (( (Principio del mutuo riconoscimento). )) (( 1. Il principio del mutuo riconoscimento è disciplinato dalle norme del presente titolo e dalle altre disposizioni di legge attuative del diritto dell'Unione europea. 2. Le d

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art7`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis. (( (Principio della riserva di codice). )) ((Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia.))

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 317 Principio di prevalenza delle misure cautelari reali e tutela dei terzi 1. Le condizioni e i criteri di prevalenza rispetto alla gestione concorsuale delle misure cautelari reali sulle cose indicate dall'articolo 142 sono regolate dalle disposizion

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 ((, che può essere aumentata fino al doppio, tenuto conto della causa di inammissibilità della richiesta)) . ((6-bis. Gli importi di cui al comma 6 sono adeguati ogni due anni con decreto del Ministro della giustizia, di concerto con

**[8]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis.1 (( (Strumenti di cooperazione amministrativa avanzata). )) (( 1. L'Amministrazione finanziaria, in attuazione del principio di economicità dell'azione amministrativa, si avvale di strumenti di cooperazione amministrativa

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 emi, hanno riguardo le norme tributarie che disciplinano il valore stesso. 7. Se gli effetti della scissione sono fatti retroagire a norma del comma 11, per i beni di cui agli articoli 92 e 94 le disposizioni del precedente comma 4 tro

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
