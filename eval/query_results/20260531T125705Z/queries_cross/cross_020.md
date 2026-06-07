# cross_020 — civile+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:24 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 41.7s (ret 0.2s + llm 41.1s) |

## Query

> Qual è il trattamento fiscale del trust e gli effetti civilistici della segregazione patrimoniale?

## Risposta

**QUALIFICAZIONE**
Il trust è un meccanismo che permette la segregazione patrimoniale tra i coniugi, ma non è specificamente menzionato nelle normative elencate. Gli effetti civilistici della segregazione patrimoniale sono trattati in vari articoli del Codice Civile.

**NORMA APPLICABILE**
Le norme applicabili riguardano principalmente il Codice Civile, in particolare gli articoli 156, 2427 e 2900.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che trattano il trust e gli effetti civilistici della segregazione patrimoniale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme elencate non specificamente menzionano il trust, ma trattano gli effetti civilistici della segregazione patrimoniale tra i coniugi. La valutazione del trattamento fiscale del trust richiederebbe ulteriori ricerche in leggi fiscali.

**GAP ANALYSIS**
Il Packet manca di normative specifiche sul trust e le relative implicazioni fiscale. Inoltre, non ci sono giurisprudenze menzionate che trattano il tema.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il trust è un meccanismo che permette la segregazione patrimoniale tra i coniugi, ma non è specificamente menzionato nelle normative elencate. Gli effetti civilistici della segregazione patrimoniale sono trattati in vari articoli del Codice Civile.

*Citazioni: {'source_id': 'CC_ART_156', 'claim': 'Il regio decreto 16 marzo 1942, n. 262 stabilisce gli effetti della separazione sui rapporti patrimoniali tra i coniugi.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'CC_ART_2427', 'claim': "Il regio decreto 16 marzo 1942, n. 262 permette l'aggregazione delle azioni secondo la loro natura.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'CC_ART_2900', 'claim': 'Il regio decreto 16 marzo 1942, n. 262 stabilisce le condizioni, modalità ed effetti del creditore che esercita i diritti e le azioni verso i terzi.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### NORMA APPLICABILE

Le norme applicabili riguardano principalmente il Codice Civile, in particolare gli articoli 156, 2427 e 2900.

*Citazioni: {'source_id': 'CC_ART_156', 'claim': 'Il regio decreto 16 marzo 1942, n. 262 stabilisce gli effetti della separazione sui rapporti patrimoniali tra i coniugi.', 'claim_type': 'NORMA APPLICABILE', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'CC_ART_2427', 'claim': "Il regio decreto 16 marzo 1942, n. 262 permette l'aggregazione delle azioni secondo la loro natura.", 'claim_type': 'NORMA APPLICABILE', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'CC_ART_2900', 'claim': 'Il regio decreto 16 marzo 1942, n. 262 stabilisce le condizioni, modalità ed effetti del creditore che esercita i diritti e le azioni verso i terzi.', 'claim_type': 'NORMA APPLICABILE', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che trattano il trust e gli effetti civilistici della segregazione patrimoniale.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme elencate non specificamente menzionano il trust, ma trattano gli effetti civilistici della segregazione patrimoniale tra i coniugi. La valutazione del trattamento fiscale del trust richiederebbe ulteriori ricerche in leggi fiscali.

### GAP ANALYSIS

Il Packet manca di normative specifiche sul trust e le relative implicazioni fiscale. Inoltre, non ci sono giurisprudenze menzionate che trattano il tema.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art198` | 2.0340 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art95` | 0.8217 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2539` | 0.7352 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art86` | -0.0320 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art888` | -0.8896 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65` | -1.7175 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art303` | -2.2479 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87` | -2.6193 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art5` | -3.7976 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3129` | -3.9779 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art73`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art198`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 156. Effetti della separazione sui rapporti patrimoniali tra i coniugi. Il giudice, pronunziando la separazione, stabilisce a vantaggio del coniuge cui non sia addebitabile la separazione il diritto di ricevere dall'altro coniuge quanto è necessario al suo ma

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art95`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Gli eredi rispondono in solido delle obbligazioni tributarie il cui presupposto si è verificato anteriormente alla morte del dante causa. Gli eredi del contribuente devono comunicare all'ufficio delle imposte del domicilio fiscale del

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2539`

> REGIO DECRETO 16 marzo 1942, n. 262 azioni possono essere aggregate secondo la loro natura, salvo quando la loro separata evidenziazione sia necessaria per comprendere gli effetti delle operazioni medesime sulla situazione patrimoniale e finanziaria e sul risultato economico della società; ((246)) 2

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art86`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Agli effetti dell'applicazione delle imposte sui redditi ogni soggetto si intende domiciliato in un comune dello Stato, giusta le disposizioni seguenti. (100) Le persone fisiche residenti nel territorio dello Stato hanno il domicilio

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art888`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 792. (Effetti della riversibilità). Il patto di riversibilità produce l'effetto di risolvere tutte le alienazioni dei beni donati e di farli ritornare al donante liberi da ogni peso o ipoteca, ad eccezione dell'ipoteca iscritta a garanzia della dote o di altr

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Alla rettifica delle dichiarazioni presentate dai soggetti all'imposta sul reddito delle persone giuridiche si procede con unico atto agli effetti di tale imposta e dell'imposta locale sui redditi, con riferimento unitario al reddito

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art303`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 303 Effetti del provvedimento di liquidazione 1. Dalla data del provvedimento che ordina la liquidazione si applicano gli articoli 142, 144, 145, 146 e 147 e se l'impresa è una persona giuridica, cessano le funzioni delle assemblee e degli organi di am

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 L'amministrazione finanziaria può stabilire il domicilio fiscale del soggetto, in deroga alle disposizioni dell'articolo precedente, nel comune dove il soggetto stesso svolge in modo continuativo la principale attività ovvero, per i s

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art5`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 ati alla conservazione del bilancio le società semplici e le società o le associazioni equiparate né gli enti non commerciali che non esercitano nel territorio dello Stato attività commerciali o che, ammessi a regimi contabili semplif

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3129`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2900. (Condizioni, modalità ed effetti). Il creditore, per assicurare che siano soddisfatte o conservate le sue ragioni, può esercitare i diritti e le azioni che spettano verso i terzi al proprio debitore e che questi trascura di esercitare, purché i diritti

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
