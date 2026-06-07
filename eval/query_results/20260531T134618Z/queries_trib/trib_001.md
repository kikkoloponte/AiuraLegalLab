# trib_001 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:08 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 5.4s (ret 0.3s + llm 4.9s) |

## Query

> Quali sono i principi fondamentali dello Statuto del contribuente?

## Risposta

**QUALIFICAZIONE**
Il principio fondamentale dello Statuto del contribuente è la tutela dei diritti e delle libertà dell'individuo nel rapporto con l'amministrazione fiscale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il principio è chiaramente enunciato nel decreto e non contrasta con altre norme.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il principio fondamentale dello Statuto del contribuente è la tutela dei diritti e delle libertà dell'individuo nel rapporto con l'amministrazione fiscale.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60', 'claim': "Il principio fondamentale dello Statuto del contribuente è la tutela dei diritti e delle libertà dell'individuo nel rapporto con l'amministrazione fiscale.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il principio è chiaramente enunciato nel decreto e non contrasta con altre norme.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4` | 3.4835 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2` | 0.3663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3` | -0.0998 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3` | -0.2036 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60` | -0.3100 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | -0.4634 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725` | -1.5843 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art138` | -2.0774 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art140` | -2.0966 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:2000-07-27;212~art1` | -3.3706 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 5 Art. 4 ((In armonia con la Costituzione e i principi dell'ordinamento giuridico dello Stato e col rispetto degli obblighi internazionali e degli interessi nazionali - tra i quali è compreso quello della tutela delle minoranze linguistiche locali - nonchè d

**[2]** `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2`

> LEGGE COSTITUZIONALE 10 novembre 1971, n. 1 Art. 2 L'articolo 4 dello Statuto speciale per il Trentino-Alto Adige, approvato con legge costituzionale 26 febbraio 1948, n. 5 , è sostituito dal seguente: "In armonia con la Costituzione e i principi dell'ordinamento giuridico dello Stato e col rispetto

**[3]** `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3`

> LEGGE COSTITUZIONALE 22 novembre 1999, n. 1 Art. 3 (Modifica dell'articolo 123 della Costituzione) 1. L' articolo 123 della Costituzione è sostituito dal seguente: "Art. 123. - Ciascuna Regione ha uno statuto che, in armonia con la Costituzione, ne determina la forma di governo e i principi fondamen

**[4]** `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3`

> LEGGE COSTITUZIONALE 10 novembre 1971, n. 1 Art. 3 L'articolo 5 dello Statuto speciale per il Trentino-Alto Adige, approvato con legge costituzionale 26 febbraio 1948, n. 5 , è sostituito dal seguente: "La regione, nei limiti del precedente articolo e dei principi stabiliti dalle leggi dello Stato,

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  2000, n. 212 , recante lo Statuto dei diritti del contribuente)) . Le persone interposte, che provino di aver pagato imposte in relazione a redditi successivamente imputati, a norma del comma terzo, ad altro contribuente, possono chi

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-ter (( (Tutela dei diritti fondamentali della persona nel mutuo riconoscimento). )) (( 1. L'autorità giudiziaria provvede al riconoscimento e all'esecuzione se non sussistono fondate ragioni per ritenere che l'imputato o il c

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art138`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 quinquies. I commi 3-bis, 3-ter e 3-quater non si applicano ai soggetti che redigono il bilancio in base ai principi contabili internazionali di cui al regolamento (CE) n. 1606/2002 del Parlamento europeo e del Consiglio, del 19 luglio

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art140`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  alla corretta applicazione di tali principi, delle passività assumono rilievo anche ai fini fiscali. (133) 2. Per la determinazione del valore normale dei beni e dei servizi e, con riferimento alla data in cui si considerano conseguit

**[10]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
