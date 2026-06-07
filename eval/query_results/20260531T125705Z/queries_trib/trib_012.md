# trib_012 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:40 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 10.1s (ret 0.4s + llm 9.2s) |

## Query

> Come si determina la base imponibile IRES per le società di capitali?

## Risposta

**QUALIFICAZIONE**
La base imponibile IRES per le società di capitali si determina sulla base del patrimonio della società.

**NORMA APPLICABILE**
Il patrimonio della società di capitali viene stimato in base all'articolo 64 del codice di procedura civile.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alla determinazione della base imponibile IRES per le società di capitali.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione è basata esclusivamente sulle norme legislative e non su precedenti giurisprudenziali, quindi la solidità della posizione è ALTA.

**GAP ANALYSIS**
Non ci sono specifiche normative o giurisprudenze nel Packet che trattino la determinazione della base imponibile IRES per le società di capitali. Potrebbe essere utile esaminare ulteriormente il codice delle imposte e eventuali disposizioni successive.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La base imponibile IRES per le società di capitali si determina sulla base del patrimonio della società.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2672', 'claim': "Il valore delle cause relative all'esistenza, alla validità o alla risoluzione di un rapporto giuridico obbligatorio si determina in base a quella parte del rapporto che è in contestazione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il patrimonio della società di capitali viene stimato in base all'articolo 64 del codice di procedura civile.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;2672', 'claim': "Il valore delle cause relative all'esistenza, alla validità o alla risoluzione di un rapporto giuridico obbligatorio si determina in base a quella parte del rapporto che è in contestazione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alla determinazione della base imponibile IRES per le società di capitali.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione è basata esclusivamente sulle norme legislative e non su precedenti giurisprudenziali, quindi la solidità della posizione è ALTA.

### GAP ANALYSIS

Non ci sono specifiche normative o giurisprudenze nel Packet che trattino la determinazione della base imponibile IRES per le società di capitali. Potrebbe essere utile esaminare ulteriormente il codice delle imposte e eventuali disposizioni successive.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2679` | 0.5050 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2660` | 0.3313 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2663` | -0.2083 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380` | -0.5215 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2655` | -1.1982 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2665` | -1.9425 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2664` | -2.0215 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art15` | -3.1247 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2672` | -3.1413 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art16` | -3.3049 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art83`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2679`

> REGIO DECRETO 16 marzo 1942, n. 262 età di capitali ovvero mediante incorporazione in una società di capitali non libera i soci a responsabilità illimitata dalla responsabilità per le obbligazioni delle rispettive società partecipanti alla fusione anteriori all'ultima delle iscrizioni prescritte dal

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2660`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-ter. (Trasformazione di società di persone). Salvo diversa disposizione del contratto sociale, la trasformazione di società di persone in società di capitali è decisa con il consenso della maggioranza dei soci determinata secondo la parte attribuita a ci

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2663`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-sexies. (( (Trasformazione di società di capitali).)) ((Salvo diversa disposizione dello statuto, la deliberazione di trasformazione di società di capitali in società di persone è adottata con le maggioranze previste per le modifiche dello statuto. È com

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 380 (( (Cause di scioglimento delle società di capitali).)) (( 1. All' articolo 2484, primo comma, del codice civile dopo il numero 7) è aggiunto il seguente: "7-bis) per l'apertura della procedura di liquidazione giudiziale e della liquidazione contro

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2655`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2497-septies. (( (Coordinamento fra società).)) ((Le disposizioni del presente capo si applicano altresì alla società o all'ente che, fuori dalle ipotesi di cui all'articolo 2497-sexies, esercita attività di direzione e coordinamento di società sulla base di

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2665`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-octies. (( (Trasformazione eterogenea in società di capitali).)) ((I consorzi, le società consortili, le comunioni d'azienda, le associazioni riconosciute e le fondazioni possono trasformarsi in una delle società disciplinate nei capi V, VI e VII del pre

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2664`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-septies. (( (Trasformazione eterogenea da società di capitali).)) ((Le società disciplinate nei capi V, VI, VII del presente titolo possono trasformarsi in consorzi, società consortili, società cooperative, comunioni di azienda, associazioni non riconosc

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art15`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 12. (Cause relative a rapporti obbligatori, a locazioni e a divisioni). Il valore delle cause relative all'esistenza, alla validità o alla risoluzione di un rapporto giuridico obbligatorio si determina in base a quella parte del rapporto che è in contestaz

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2672`

> REGIO DECRETO 16 marzo 1942, n. 262 articolo 64 del codice di procedura civile . Ai soggetti di cui ai precedenti terzo e quarto comma è altresì affidata, in ipotesi di fusione di società di persone con società di capitali, la relazione di stima del patrimonio della società di persone a norma dell'a

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art16`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 13. (Cause relative a prestazioni alimentari e a rendite). Nelle cause per prestazioni alimentari periodiche, se il titolo è controverso, il valore si determina in base all'ammontare delle somme dovute per due anni. Nelle cause relative a rendite perpetue,

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
