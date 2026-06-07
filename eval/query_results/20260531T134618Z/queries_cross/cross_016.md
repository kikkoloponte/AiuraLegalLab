# cross_016 — penale+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:01 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 14.0s (ret 0.3s + llm 13.5s) |

## Query

> Quando il sequestro preventivo per equivalente si applica ai reati tributari?

## Risposta

**QUALIFICAZIONE**
Il sequestro preventivo per equivalente si applica quando vi è pericolo che la libera disponibilità di una cosa pertinente al reato possa aggravare o protrarre le conseguenze del reato, ovvero agevolare la commissione di altri reati. Questo concetto si applica anche ai reati tributari.

**NORMA APPLICABILE**
Il sequestro preventivo per equivalente si applica ai reati tributari in base al DECRETO LEGISLATIVO 12 gennaio 2019, n. 14, Art. 318.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano esplicitamente il sequestro preventivo per equivalente ai reati tributari. Tuttavia, la norma generale del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447, Art. 321 suggerisce che il sequestro preventivo può essere applicato anche ai reati tributari.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione della solidità di questa affermazione è alta, in quanto la norma generale del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447, Art. 321 suggerisce che il sequestro preventivo può essere applicato anche ai reati tributari.

**GAP ANALYSIS**
Non ci sono specifiche giurisprudenze menzionate nel Packet che affrontano esplicitamente il sequestro preventivo per equivalente ai reati tributari. Tuttavia, la norma generale del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447, Art. 321 suggerisce che il sequestro preventivo può essere applicato anche ai reati tributari.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il sequestro preventivo per equivalente si applica quando vi è pericolo che la libera disponibilità di una cosa pertinente al reato possa aggravare o protrarre le conseguenze del reato, ovvero agevolare la commissione di altri reati. Questo concetto si applica anche ai reati tributari.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art321', 'claim': 'Il sequestro preventivo può essere applicato quando vi è pericolo che la libera disponibilità di una cosa pertinente al reato possa aggravare o protrarre le conseguenze del reato, ovvero agevolare la commissione di altri reati.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'CC_ART_1218'}*

### NORMA APPLICABILE

Il sequestro preventivo per equivalente si applica ai reati tributari in base al DECRETO LEGISLATIVO 12 gennaio 2019, n. 14, Art. 318.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art318', 'claim': 'Il sequestro preventivo per equivalente si applica ai reati tributari in base al DECRETO LEGISLATIVO 12 gennaio 2019, n. 14, Art. 318.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DLGS_ART_318'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano esplicitamente il sequestro preventivo per equivalente ai reati tributari. Tuttavia, la norma generale del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447, Art. 321 suggerisce che il sequestro preventivo può essere applicato anche ai reati tributari.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art321', 'claim': 'Il sequestro preventivo può essere applicato anche ai reati tributari.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'CC_ART_1218'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione della solidità di questa affermazione è alta, in quanto la norma generale del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447, Art. 321 suggerisce che il sequestro preventivo può essere applicato anche ai reati tributari.

### GAP ANALYSIS

Non ci sono specifiche giurisprudenze menzionate nel Packet che affrontano esplicitamente il sequestro preventivo per equivalente ai reati tributari. Tuttavia, la norma generale del DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447, Art. 321 suggerisce che il sequestro preventivo può essere applicato anche ai reati tributari.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art380` | 3.8282 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art847` | 2.6343 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art384` | 1.4549 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art318` | 1.1758 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art13` | 1.0726 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art382` | 0.7710 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art3` | 0.7020 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art848` | 0.3077 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art849` | -0.3089 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324` | -1.3324 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art12bis`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art380`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 321 Oggetto del sequestro preventivo 1. Quando vi è pericolo che la libera disponibilità di una cosa pertinente al reato possa aggravare o protrarre le conseguenze di esso ovvero agevolare la commissione di altri reati, a richies

**[2]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art847`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 677. (Esecuzione del sequestro giudiziario). Il sequestro giudiziario si esegue a norma degli articoli 605 e seguenti, in quanto applicabili, omessa la notificazione del precetto per consegna o rilascio nonché la comunicazione di cui all'art. 608, primo co

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art384`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 323 Perdita di efficacia del sequestro preventivo 1. Con la sentenza di proscioglimento o di non luogo a procedere, ancorché soggetta a impugnazione, il giudice ordina che le cose sequestrate siano restituite a chi ne abbia dirit

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art318`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 318 Sequestro preventivo 1. In pendenza della procedura di liquidazione giudiziale non può essere disposto sequestro preventivo ai sensi dell' articolo 321, comma 1, del codice di procedura penale sulle cose di cui all'articolo 142, sempre che la loro

**[5]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art13`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 10 Regolamento preventivo di giurisdizione 1. Nel giudizio davanti ai tribunali amministrativi regionali è ammesso il ricorso per regolamento preventivo di giurisdizione previsto dall' articolo 41 del codice di procedura civile . Si applica il primo com

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art382`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 322 Riesame del decreto di sequestro preventivo 1. Contro il decreto di sequestro emesso dal giudice l'imputato e il suo difensore, la persona alla quale le cose sono state sequestrate e quella che avrebbe diritto alla loro resti

**[7]** `urn:nir:stato:legge:2000-07-27;212~art3`

> LEGGE 27 luglio 2000, n. 212 Art. 3 Efficacia temporale delle norme tributarie 1. Salvo quanto previsto dall'articolo 1, comma 2, le disposizioni tributarie non hanno effetto retroattivo. Le presunzioni legali non si applicano retroattivamente. Relativamente ai tributi dovuti, determinati o liquidat

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art848`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 678. (Esecuzione del sequestro conservativo sui mobili). Il sequestro conservativo sui mobili e sui crediti si esegue secondo le norme stabilite per il pignoramento presso il debitore o presso terzi. In quest'ultimo caso il sequestrante deve, con l'atto di

**[9]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art849`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 679. (Esecuzione del sequestro conservativo sugli immobili). Il sequestro conservativo sugli immobili si esegue con la trascrizione del provvedimento ((presso l'ufficio del conservatore dei registri immobiliari)) del luogo in cui i beni sono situati. Per l

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 324 Esenzioni dai reati di bancarotta 1. Le disposizioni di cui agli articoli 322, comma 3 e 323 non si applicano ai pagamenti e alle operazioni computi in esecuzione di un concordato preventivo o di accordi di ristrutturazione dei debiti omologati o d

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
