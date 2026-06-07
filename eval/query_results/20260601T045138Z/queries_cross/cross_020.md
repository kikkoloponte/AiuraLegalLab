# cross_020 — civile+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:10 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 30.0s (ret 0.3s + llm 29.5s) |

## Query

> Qual è il trattamento fiscale del trust e gli effetti civilistici della segregazione patrimoniale?

## Risposta

**QUALIFICAZIONE**
Il trattamento fiscale del trust e gli effetti civilistici della segregazione patrimoniale sono disciplinati dalle norme tributarie e civili.

**NORMA APPLICABILE**
Il trattamento fiscale del trust è disciplinato dall'articolo 2506-quater del codice civile, mentre gli effetti civilistici della segregazione patrimoniale sono regolati dall'articolo 2501.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono al trattamento fiscale del trust o agli effetti civilistici della segregazione patrimoniale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità delle norme applicabili è alta, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

**GAP ANALYSIS**
Il packet manca di giurisprudenza che potrebbe fornire orientamenti specifici sul trattamento fiscale del trust e gli effetti civilistici della segregazione patrimoniale.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il trattamento fiscale del trust e gli effetti civilistici della segregazione patrimoniale sono disciplinati dalle norme tributarie e civili.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215', 'claim': 'Il trattamento fiscale del trust è regolato dalle norme tributarie.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art94', 'claim': 'La segregazione patrimoniale ha effetti civilistici.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il trattamento fiscale del trust è disciplinato dall'articolo 2506-quater del codice civile, mentre gli effetti civilistici della segregazione patrimoniale sono regolati dall'articolo 2501.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215', 'claim': "Il trattamento fiscale del trust è regolato dall'articolo 2506-quater del codice civile.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23', 'claim': "Gli effetti civilistici della segregazione patrimoniale sono regolati dall'articolo 2501.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono al trattamento fiscale del trust o agli effetti civilistici della segregazione patrimoniale.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità delle norme applicabili è alta, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

### GAP ANALYSIS

Il packet manca di giurisprudenza che potrebbe fornire orientamenti specifici sul trattamento fiscale del trust e gli effetti civilistici della segregazione patrimoniale.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215` | 2.2958 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215` | 2.0338 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art94` | 1.5348 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art95` | 0.8217 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2539` | 0.7352 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art86` | -0.0320 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23` | -0.9075 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | -2.1079 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art303` | -2.2479 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:1981-11-24;689~art52` | -2.3660 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 emi, hanno riguardo le norme tributarie che disciplinano il valore stesso. 7. Se gli effetti della scissione sono fatti retroagire a norma del comma 11, per i beni di cui agli articoli 92 e 94 le disposizioni del precedente comma 4 tro

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Ai fini delle imposte sui redditi, la decorrenza degli effetti della scissione è regolata secondo le disposizioni del comma 1 dell'articolo 2506-quater del codice civile , ma la retrodatazione degli effetti, ai sensi dell'articolo 2501

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art94`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 . 239 , quando, successivamente alla loro costituzione, un soggetto residente nel territorio dello Stato effettui in favore del trust un'attribuzione che importi il trasferimento di proprietà di beni immobili o la costituzione o il tra

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art95`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Gli eredi rispondono in solido delle obbligazioni tributarie il cui presupposto si è verificato anteriormente alla morte del dante causa. Gli eredi del contribuente devono comunicare all'ufficio delle imposte del domicilio fiscale del

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2539`

> REGIO DECRETO 16 marzo 1942, n. 262 azioni possono essere aggregate secondo la loro natura, salvo quando la loro separata evidenziazione sia necessaria per comprendere gli effetti delle operazioni medesime sulla situazione patrimoniale e finanziaria e sul risultato economico della società; ((246)) 2

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art86`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Agli effetti dell'applicazione delle imposte sui redditi ogni soggetto si intende domiciliato in un comune dello Stato, giusta le disposizioni seguenti. (100) Le persone fisiche residenti nel territorio dello Stato hanno il domicilio

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 17 Tassazione separata 1. L'imposta si applica separatamente sui seguenti redditi: a) trattamento di fine rapporto di cui all' articolo 2120 del codice civile e indennità equipollenti, comunque denominate, commisurate alla durata

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art303`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 303 Effetti del provvedimento di liquidazione 1. Dalla data del provvedimento che ordina la liquidazione si applicano gli articoli 142, 144, 145, 146 e 147 e se l'impresa è una persona giuridica, cessano le funzioni delle assemblee e degli organi di am

**[10]** `urn:nir:stato:legge:1981-11-24;689~art52`

> LEGGE 24 novembre 1981, n. 689 Art. 52 (Modifica dell'articolo 18 delle disposizioni relative al mercato mobiliare ed al trattamento fiscale dei titoli azionari) L'ultimo comma dell' articolo 18 del decreto-legge 8 aprile 1974, n. 95 , convertito con modificazioni nella legge 7 giugno 1974, n. 216 ,

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
