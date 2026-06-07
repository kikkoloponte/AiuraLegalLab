# trib_001 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 12:01 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 7.1s (ret 0.3s + llm 6.0s) |

## Query

> Quali sono i principi fondamentali dello Statuto del contribuente?

## Risposta

**QUALIFICAZIONE**
Il principio fondamentale dello Statuto del contribuente è l'accesso dei cittadini a informazioni chiare e complete sui loro diritti e obblighi fiscali, con la pubblicazione degli atti di concessione di sovvenzioni, contributi, sussidi e attribuzione di vantaggi economici.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione del principio fondamentale dello Statuto del contribuente è alta, in quanto la normativa specifica chiaramente l'obbligo di pubblicare tali atti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il principio fondamentale dello Statuto del contribuente è l'accesso dei cittadini a informazioni chiare e complete sui loro diritti e obblighi fiscali, con la pubblicazione degli atti di concessione di sovvenzioni, contributi, sussidi e attribuzione di vantaggi economici.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2013-03-14;33~art26', 'claim': 'Le pubbliche amministrazioni pubblicano gli atti con i quali sono determinati obblighi di pubblicazione degli atti di concessione di sovvenzioni, contributi, sussidi e attribuzione di vantaggi economici a persone fisiche ed enti pubblici e privati.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione del principio fondamentale dello Statuto del contribuente è alta, in quanto la normativa specifica chiaramente l'obbligo di pubblicare tali atti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4` | 3.4835 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art26` | 1.4763 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2` | 0.3663 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3` | -0.0998 | hybrid_rrf |  |
| 5 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3` | -0.2036 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60` | -0.3100 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge.costituzionale:1948-02-26;3~art10` | -0.5614 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge.costituzionale:2012-04-20;1~art5` | -0.8092 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725` | -1.5843 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5` | -3.6913 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art1`
- `urn:nir:stato:legge:2000-07-27;212~art10`

### Snippet fonti

**[1]** `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 5 Art. 4 ((In armonia con la Costituzione e i principi dell'ordinamento giuridico dello Stato e col rispetto degli obblighi internazionali e degli interessi nazionali - tra i quali è compreso quello della tutela delle minoranze linguistiche locali - nonchè d

**[2]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art26`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 26 Obblighi di pubblicazione degli atti di concessione di sovvenzioni, contributi, sussidi e attribuzione di vantaggi economici a persone fisiche ed enti pubblici e privati. 1. Le pubbliche amministrazioni pubblicano gli atti con i quali sono determinati

**[3]** `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2`

> LEGGE COSTITUZIONALE 10 novembre 1971, n. 1 Art. 2 L'articolo 4 dello Statuto speciale per il Trentino-Alto Adige, approvato con legge costituzionale 26 febbraio 1948, n. 5 , è sostituito dal seguente: "In armonia con la Costituzione e i principi dell'ordinamento giuridico dello Stato e col rispetto

**[4]** `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3`

> LEGGE COSTITUZIONALE 22 novembre 1999, n. 1 Art. 3 (Modifica dell'articolo 123 della Costituzione) 1. L' articolo 123 della Costituzione è sostituito dal seguente: "Art. 123. - Ciascuna Regione ha uno statuto che, in armonia con la Costituzione, ne determina la forma di governo e i principi fondamen

**[5]** `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3`

> LEGGE COSTITUZIONALE 10 novembre 1971, n. 1 Art. 3 L'articolo 5 dello Statuto speciale per il Trentino-Alto Adige, approvato con legge costituzionale 26 febbraio 1948, n. 5 , è sostituito dal seguente: "La regione, nei limiti del precedente articolo e dei principi stabiliti dalle leggi dello Stato,

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  2000, n. 212 , recante lo Statuto dei diritti del contribuente)) . Le persone interposte, che provino di aver pagato imposte in relazione a redditi successivamente imputati, a norma del comma terzo, ad altro contribuente, possono chi

**[7]** `urn:nir:stato:legge.costituzionale:1948-02-26;3~art10`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 3 Art. 10 ((La Regione, al fine di favorire lo sviluppo economico dell'Isola e nel rispetto della normativa comunitaria, con riferimento ai tributi erariali per i quali lo Stato ne prevede la possibilità, può, ferma restando la copertura del fabbisogno stand

**[8]** `urn:nir:stato:legge.costituzionale:2012-04-20;1~art5`

> LEGGE COSTITUZIONALE 20 aprile 2012, n. 1  di analisi e verifica degli andamenti di finanza pubblica e di valutazione dell'osservanza delle regole di bilancio; g) le modalità attraverso le quali lo Stato, nelle fasi avverse del ciclo economico o al verificarsi degli eventi eccezionali di cui alla le

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-ter (( (Tutela dei diritti fondamentali della persona nel mutuo riconoscimento). )) (( 1. L'autorità giudiziaria provvede al riconoscimento e all'esecuzione se non sussistono fondate ragioni per ritenere che l'imputato o il c

**[10]** `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5`

> LEGGE COSTITUZIONALE 23 settembre 1993, n. 2 Art. 5 1. All'articolo 4 dello statuto speciale della regione Friuli- Venezia Giulia, approvato con legge costituzionale 31 gennaio 1963, n. 1 , dopo il numero 1) è inserito il seguente: "1-bis) ordinamento degli enti locali e delle relative circoscrizion

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
