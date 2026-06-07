# trib_001 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:38 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 6.4s (ret 0.4s + llm 5.5s) |

## Query

> Quali sono i principi fondamentali dello Statuto del contribuente?

## Risposta

**QUALIFICAZIONE**
Il principio fondamentale dello Statuto del contribuente è la tutela dei diritti fondamentali della persona nel mutuo riconoscimento.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione è alta in quanto la norma specifica chiaramente il principio fondamentale dello Statuto del contribuente.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il principio fondamentale dello Statuto del contribuente è la tutela dei diritti fondamentali della persona nel mutuo riconoscimento.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725', 'claim': "L'autorità giudiziaria provvede al riconoscimento e all'esecuzione se non sussistono fondate ragioni per ritenere che l'imputato o il contribuente abbia commesso un reato.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione è alta in quanto la norma specifica chiaramente il principio fondamentale dello Statuto del contribuente.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4` | 3.4835 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2` | 0.3663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3` | -0.0998 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3` | -0.2036 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60` | -0.3100 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725` | -1.5843 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5` | -3.6913 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge.costituzionale:1993-09-23;2~art4` | -3.8476 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge.costituzionale:1963-01-31;1~art8` | -4.1665 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:2000-07-27;212~art6` | -4.7848 | hybrid_rrf | ✅ |

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

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-ter (( (Tutela dei diritti fondamentali della persona nel mutuo riconoscimento). )) (( 1. L'autorità giudiziaria provvede al riconoscimento e all'esecuzione se non sussistono fondate ragioni per ritenere che l'imputato o il c

**[7]** `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5`

> LEGGE COSTITUZIONALE 23 settembre 1993, n. 2 Art. 5 1. All'articolo 4 dello statuto speciale della regione Friuli- Venezia Giulia, approvato con legge costituzionale 31 gennaio 1963, n. 1 , dopo il numero 1) è inserito il seguente: "1-bis) ordinamento degli enti locali e delle relative circoscrizion

**[8]** `urn:nir:stato:legge.costituzionale:1993-09-23;2~art4`

> LEGGE COSTITUZIONALE 23 settembre 1993, n. 2 Art. 4 1. All'articolo 3 dello statuto speciale per la Sardegna, approvato con legge costituzionale 26 febbraio 1948, n. 3, la lettera b) è sostituita dalla seguente: " b) ordinamento degli enti locali e delle relative circoscrizioni;". Nota all'art. 4: -

**[9]** `urn:nir:stato:legge.costituzionale:1963-01-31;1~art8`

> LEGGE COSTITUZIONALE 31 gennaio 1963, n. 1 Art. 8 1. ((La Regione esercita funzioni di programmazione nonchè funzioni amministrative nelle materie in cui ha potestà legislativa a norma degli articoli 4 e 5, in conformità ai principi della Costituzione e del presente Statuto)) .

**[10]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212 Art. 6 Conoscenza degli atti e semplificazione 1. L'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati. A tal fine essa provvede comunque a comunicarli nel luogo di effettivo domicilio del contribuente,

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
