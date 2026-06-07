# cross_022 — amministrativo+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:12 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 40.2s (ret 0.4s + llm 39.7s) |

## Query

> Come interagiscono il danno da occupazione illegittima e l'acquisizione sanante ex art. 42-bis TU espropri?

## Risposta

**QUALIFICAZIONE**
L'occupazione illegittima di un immobile può generare un danno risarcitorio. Art. 42-bis del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 8 giugno 2001, n. 327 specifica che per il periodo di occupazione senza titolo è computato a titolo risarcitorio l'interesse del cinque per cento annuo sul valore determinato.

**NORMA APPLICABILE**
Il danno derivante dall'occupazione illegittima può essere risarcito in base al diritto di acquisizione sanante. Art. 29 del DECRETO LEGISLATIVO 15 giugno 2015, n. 81 stabilisce che il lavoratore interessato ha diritto al risarcimento del danno derivente dalla prestazione di lavoro in violazione di disposizioni imperative.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente all'interazione tra il danno da occupazione illegittima e l'acquisizione sanante. Tuttavia, la teoria dell'acquisizione sanante prevede che chi ha posseduto una cosa per un certo periodo di tempo può acquisire la proprietà della stessa se non si oppone nessuno con diritto.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della valutazione è media. Le norme stabiliscono il diritto al risarcimento del danno, ma non specificano come l'acquisizione sanante possa interagire con questo diritto.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze direttamente rilevanti per l'interazione tra il danno da occupazione illegittima e l'acquisizione sanante. Inoltre, non ci sono dettagli specifici sulle condizioni sotto cui l'occupazione illegittima può portare a un diritto di acquisizione sanante.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'occupazione illegittima di un immobile può generare un danno risarcitorio. Art. 42-bis del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 8 giugno 2001, n. 327 specifica che per il periodo di occupazione senza titolo è computato a titolo risarcitorio l'interesse del cinque per cento annuo sul valore determinato.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art44', 'claim': "Per il periodo di occupazione senza titolo è computato a titolo risarcitorio l'interesse del cinque per cento annuo sul valore determinato.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### NORMA APPLICABILE

Il danno derivante dall'occupazione illegittima può essere risarcito in base al diritto di acquisizione sanante. Art. 29 del DECRETO LEGISLATIVO 15 giugno 2015, n. 81 stabilisce che il lavoratore interessato ha diritto al risarcimento del danno derivente dalla prestazione di lavoro in violazione di disposizioni imperative.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2015-06-15;81~art29', 'claim': 'Il lavoratore interessato ha diritto al risarcimento del danno derivente dalla prestazione di lavoro in violazione di disposizioni imperative.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente all'interazione tra il danno da occupazione illegittima e l'acquisizione sanante. Tuttavia, la teoria dell'acquisizione sanante prevede che chi ha posseduto una cosa per un certo periodo di tempo può acquisire la proprietà della stessa se non si oppone nessuno con diritto.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art923', 'claim': "Le cose mobili che non sono proprietà di alcuno si acquistano con l'occupazione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art1154', 'claim': "A colui che ha acquistato conoscendo l'illegittima provenienza della cosa non giova l'erronea credenza che il suo autore o un precedente possessore ne sia divenuto proprietario.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della valutazione è media. Le norme stabiliscono il diritto al risarcimento del danno, ma non specificano come l'acquisizione sanante possa interagire con questo diritto.

### GAP ANALYSIS

Il Packet manca di giurisprudenze direttamente rilevanti per l'interazione tra il danno da occupazione illegittima e l'acquisizione sanante. Inoltre, non ci sono dettagli specifici sulle condizioni sotto cui l'occupazione illegittima può portare a un diritto di acquisizione sanante.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art44` | 0.5612 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art29` | -0.1088 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:1992-04-30;285~art20` | -2.4792 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2006-04-03;152~art313` | -3.0457 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art963` | -3.3024 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2023-03-31;36~art463` | -3.8412 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1020` | -3.8464 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art864` | -4.2611 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1198` | -4.3107 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art65` | -4.6868 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art44`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 8 giugno 2001, n. 327 4, 5, 6 e 7. Per il periodo di occupazione senza titolo è computato a titolo risarcitorio, se dagli atti del procedimento non risulta la prova di una diversa entità del danno, l'interesse del cinque per cento annuo sul valore determinato

**[2]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art29`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 a la conversione in contratti a tempo indeterminato. Il lavoratore interessato ha diritto al risarcimento del danno derivante dalla prestazione di lavoro in violazione di disposizioni imperative. Le fondazioni hanno l'obbligo di recuperare le somme pagate a

**[3]** `urn:nir:stato:decreto.legislativo:1992-04-30;285~art20`

> DECRETO LEGISLATIVO 30 aprile 1992, n. 285 Art. 20 Occupazione della sede stradale 1. Sulle strade di tipo A), B), C) e D) è vietata ogni tipo di occupazione della sede stradale, ivi compresi fiere e mercati, con veicoli, baracche, tende e simili; sulle strade di tipo E) ed F) l'occupazione della ca

**[4]** `urn:nir:stato:decreto.legislativo:2006-04-03;152~art313`

> DECRETO LEGISLATIVO 3 aprile 2006, n. 152  del territorio e del mare, nuovi interventi comportanti aggravio di costi per l'operatore interessato. Resta in ogni caso fermo il diritto dei soggetti danneggiati dal fatto produttivo di danno ambientale, nella loro salute o nei beni di loro proprietà, di

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art963`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 867. (Sistemazione e rimboschimento dei terreni vincolati). Al fine del rimboschimento e del rinsaldamento i terreni vincolati possono essere assoggettati a espropriazione, a occupazione temporanea o a sospensione dell'esercizio del pascolo, nei modi e con le

**[6]** `urn:nir:stato:decreto.legislativo:2023-03-31;36~art463`

> DECRETO LEGISLATIVO 31 marzo 2023, n. 36 ittima maggiore durata della sospensione. 4. Il direttore dei lavori è responsabile nei confronti della stazione appaltante di un'eventuale sospensione illegittima dal medesimo ordinata per circostanze non previste dall'articolo 121 del codice.

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1020`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 923. (Cose suscettibili di occupazione). Le cose mobili che non sono proprietà di alcuno si acquistano con l'occupazione. Tali sono le cose abbandonate e gli animali che formano oggetto di caccia o di pesca.

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art864`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 634-bis. (( (Occupazione arbitraria di immobile destinato a domicilio altrui).)) ((Chiunque, mediante violenza o minaccia, occupa o detiene senza titolo un immobile destinato a domicilio altrui o sue pertinenze, ovvero impedisce il rientro nel medesimo imm

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1198`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1154. (Conoscenza dell'illegittima provenienza della cosa). A colui che ha acquistato conoscendo l'illegittima provenienza della cosa non giova l'erronea credenza che il suo autore o un precedente possessore ne sia divenuto proprietario.

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art65`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 8 giugno 2001, n. 327 Art. 55 (L) Occupazioni senza titolo, anteriori al 30 settembre 1996 (( 1. Nel caso di utilizzazione di un suolo edificabile per scopi di pubblica utilità, in assenza del valido ed efficace provvedimento di esproprio alla data del 30 sett

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
