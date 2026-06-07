# trib_008 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:39 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 9.5s (ret 0.2s + llm 8.9s) |

## Query

> Quali sono i casi di responsabilità solidale tributaria?

## Risposta

**QUALIFICAZIONE**
Si tratta di determinare i casi in cui la responsabilità solidale è applicabile nel contesto tributario.

**NORMA APPLICABILE**
La responsabilità solidale è regolata dall'articolo 2740 del Codice Civile.

**GIURISPRUDENZA**
Non ci sono specifiche giurisprudenze menzionate nel Packet che si riferiscano alla responsabilità solidale tributaria.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma non ci sono giurisprudenze per fornire ulteriori dettagli. La solidità della norma è alta.

**GAP ANALYSIS**
Non ci sono giurisprudenze menzionate nel Packet che si riferiscano alla responsabilità solidale tributaria.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Si tratta di determinare i casi in cui la responsabilità solidale è applicabile nel contesto tributario.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2740', 'claim': "Il debitore risponde dell'adempimento delle obbligazioni con tutti i suoi beni presenti e futuri.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### NORMA APPLICABILE

La responsabilità solidale è regolata dall'articolo 2740 del Codice Civile.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2740', 'claim': "Il debitore risponde dell'adempimento delle obbligazioni con tutti i suoi beni presenti e futuri.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### GIURISPRUDENZA

Non ci sono specifiche giurisprudenze menzionate nel Packet che si riferiscano alla responsabilità solidale tributaria.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma non ci sono giurisprudenze per fornire ulteriori dettagli. La solidità della norma è alta.

### GAP ANALYSIS

Non ci sono giurisprudenze menzionate nel Packet che si riferiscano alla responsabilità solidale tributaria.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art43` | 2.9907 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2338` | 2.0403 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2095` | 1.5114 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art107` | 1.1307 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2964` | 0.9956 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art393` | -2.2495 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1274` | -2.3499 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art536` | -3.1926 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2997` | -4.4769 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1352` | -5.4387 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art36`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art43`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 34. (Decadenza dalla responsabilità genitoriale e sospensione dall'esercizio di essa). La legge determina i casi nei quali la condanna importa la decadenza dalla responsabilità genitoriale. La condanna per delitti commessi con abuso della responsabilità ge

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2338`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2297. (Mancata registrazione). Fino a quando la società non è iscritta nel registro delle imprese, i rapporti tra la società e i terzi, ferma restando la responsabilità illimitata e solidale di tutti i soci, sono regolati dalle disposizioni relative alla soci

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2095`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2055. (Responsabilità solidale). Se il fatto dannoso è imputabile a più persone, tutte sono obbligate in solido al risarcimento del danno. Colui che ha risarcito il danno ha regresso contro ciascuno degli altri, nella misura determinata dalla gravità della ri

**[4]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art107`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 97. (Responsabilità di più soccombenti). Se le parti soccombenti sono più, il giudice condanna ciascuna di esse alle spese e ai danni in proporzione del rispettivo interesse nella causa. Può anche pronunciare condanna solidale di tutte o di alcune tra esse

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2964`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2740. (Responsabilità patrimoniale). Il debitore risponde dell'adempimento delle obbligazioni con tutti i suoi beni presenti e futuri. Le limitazioni della responsabilità non sono ammesse se non nei casi stabiliti dalla legge.

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art393`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 317. Impedimento di uno dei genitori. Nel caso di lontananza, di incapacità o di altro impedimento che renda impossibile ad uno dei genitori l'esercizio della ((responsabilità genitoriale)) , questa è esercitata in modo esclusivo dall'altro. ((La responsabili

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1274`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1229. (Clausole di esonero da responsabilità). È nullo qualsiasi patto che esclude o limita preventivamente la responsabilità del debitore per dolo o per colpa grave. È nullo altresì qualsiasi patto preventivo di esonero o di limitazione di responsabilità per

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art536`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 448-bis (Cessazione per decadenza dell'avente diritto dalla ((responsabilità genitoriale)) sui figli). Il figlio, anche adottivo, e, in sua mancanza, i discendenti prossimi non sono tenuti all'adempimento dell'obbligo di prestare gli alimenti al genitore nei

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2997`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2772. ((Crediti per tributi indiretti.)) ((Hanno pure privilegio i crediti dello Stato per ogni tributo indiretto, nonché quelli derivanti dall'applicazione dell'imposta comunale sull'incremento di valore degli immobili, sopra gli immobili ai quali il tributo

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1352`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1307. (Inadempimento). Se l'adempimento dell'obbligazione è divenuto impossibile per causa imputabile a uno o più condebitori, gli altri condebitori non sono liberati dall'obbligo solidale di corrispondere il valore della prestazione dovuta. Il creditore può

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
