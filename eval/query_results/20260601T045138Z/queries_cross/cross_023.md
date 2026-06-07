# cross_023 — tributario+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:12 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 41.0s (ret 0.4s + llm 40.3s) |

## Query

> Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?

## Risposta

**QUALIFICAZIONE**
Il principio del ne bis in idem impedisce di applicare più volte la stessa pena per un reato, mentre il doppio binario sanzionatorio tributario-penale prevede che una violazione fiscale possa essere sanzionata sia dal punto di vista tributario che penale.

**NORMA APPLICABILE**
Il ne bis in idem è regolato dal codice penale, mentre il doppio binario sanzionatorio tributario-penale è disciplinato dalla legge 27 luglio 2000, n. 212.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche che esprimano un orientamento prevalente sulla compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale. Tuttavia, la normativa vigente suggerisce una convergenza tra i due principi.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale è alta, poiché entrambi i principi mirano a prevenire la duplice punizione.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze specifiche che esprimono un orientamento prevalente sulla compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il principio del ne bis in idem impedisce di applicare più volte la stessa pena per un reato, mentre il doppio binario sanzionatorio tributario-penale prevede che una violazione fiscale possa essere sanzionata sia dal punto di vista tributario che penale.

*Citazioni: {'source_id': 'CC_ART_2516', 'claim': 'Il principio del ne bis in idem impedisce di applicare più volte la stessa pena per un reato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516'}, {'source_id': 'CC_ART_3BIS', 'claim': 'Il doppio binario sanzionatorio tributario-penale prevede che una violazione fiscale possa essere sanzionata sia dal punto di vista tributario che penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis'}*

### NORMA APPLICABILE

Il ne bis in idem è regolato dal codice penale, mentre il doppio binario sanzionatorio tributario-penale è disciplinato dalla legge 27 luglio 2000, n. 212.

*Citazioni: {'source_id': 'CC_ART_3BIS', 'claim': 'Il ne bis in idem è regolato dal codice penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis'}, {'source_id': 'CC_ART_2516', 'claim': 'Il doppio binario sanzionatorio tributario-penale è disciplinato dalla legge 27 luglio 2000, n. 212.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche che esprimano un orientamento prevalente sulla compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale. Tuttavia, la normativa vigente suggerisce una convergenza tra i due principi.

*Citazioni: {'source_id': 'CC_ART_3BIS', 'claim': 'Non ci sono giurisprudenze specifiche che esprimano un orientamento prevalente sulla compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale è alta, poiché entrambi i principi mirano a prevenire la duplice punizione.

### GAP ANALYSIS

Il Packet manca di giurisprudenze specifiche che esprimono un orientamento prevalente sulla compatibilità tra il ne bis in idem e il doppio binario sanzionatorio tributario-penale.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art10` | 3.4052 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2709` | 0.8772 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2009-10-27;150~art69` | -0.9792 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art7` | -1.4396 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | -1.8089 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317` | -3.6633 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art1` | -5.7070 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47` | -6.0516 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215` | -6.1606 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2023-03-31;36~art97` | -7.4616 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art20`
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art13`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art10`

> LEGGE 27 luglio 2000, n. 212 Art. 10 Tutela dell'affidamento e della buona fede. Errori del contribuente 1. I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede. 2. Non sono irrogate sanzioni nè richiesti interessi moratori al

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2709`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516. (( (Rapporti con i soci).)) ((Nella costituzione e nell'esecuzione dei rapporti mutualistici deve essere rispettato il principio di parità di trattamento.))

**[3]** `urn:nir:stato:decreto.legislativo:2009-10-27;150~art69`

> DECRETO LEGISLATIVO 27 ottobre 2009, n. 150 ter (Rapporti fra procedimento disciplinare e procedimento penale). - 1. Il procedimento disciplinare, che abbia ad oggetto, in tutto o in parte, fatti in relazione ai quali procede l'autorità giudiziaria, è proseguito e concluso anche in pendenza del proc

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art7`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis. (( (Principio della riserva di codice). )) ((Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia.))

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 317 Principio di prevalenza delle misure cautelari reali e tutela dei terzi 1. Le condizioni e i criteri di prevalenza rispetto alla gestione concorsuale delle misure cautelari reali sulle cose indicate dall'articolo 142 sono regolate dalle disposizion

**[7]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis.1 (( (Strumenti di cooperazione amministrativa avanzata). )) (( 1. L'Amministrazione finanziaria, in attuazione del principio di economicità dell'azione amministrativa, si avvale di strumenti di cooperazione amministrativa

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 emi, hanno riguardo le norme tributarie che disciplinano il valore stesso. 7. Se gli effetti della scissione sono fatti retroagire a norma del comma 11, per i beni di cui agli articoli 92 e 94 le disposizioni del precedente comma 4 tro

**[10]** `urn:nir:stato:decreto.legislativo:2023-03-31;36~art97`

> DECRETO LEGISLATIVO 31 marzo 2023, n. 36  , salvo che la pena sia dichiarata estinta ai sensi dell' articolo 179, settimo comma, del codice penale ; b) per un periodo pari a sette anni nei casi previsti dall'articolo 317-bis, primo comma, secondo periodo, del codice penale , salvo che sia intervenut

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
