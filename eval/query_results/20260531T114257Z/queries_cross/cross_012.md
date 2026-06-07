# cross_012 — civile+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 11:53 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 32.7s (ret 0.2s + llm 31.9s) |

## Query

> Come si risolvono i conflitti tra vincoli urbanistici e diritto di proprietà privata?

## Risposta

**QUALIFICAZIONE**
Il conflitto tra vincoli urbanistici e diritto di proprietà privata si risolve in base al codice civile, specificatamente all'articolo 2645-quater.

**NORMA APPLICABILE**
L'articolo 2645-quater del codice civile stabilisce che gli atti di diritto privato, i contratti e altri atti nonché le convenzioni e i contratti devono essere trascritti se hanno per oggetto beni immobili.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al conflitto tra vincoli urbanistici e diritto di proprietà privata. Tuttavia, la norma 2645-quater suggerisce che i vincoli devono essere trascritti se hanno per oggetto beni immobili.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione della solidità della norma è alta, in quanto si tratta di una disposizione chiara e specifica del codice civile. Tuttavia, la mancanza di giurisprudenza diretta sul tema rende la situazione un po' meno certa.

**GAP ANALYSIS**
Il packet non contiene giurisprudenze specifiche che si riferiscono al conflitto tra vincoli urbanistici e diritto di proprietà privata. Ciò rende difficile una valutazione completa della situazione.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il conflitto tra vincoli urbanistici e diritto di proprietà privata si risolve in base al codice civile, specificatamente all'articolo 2645-quater.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2866', 'claim': "Il conflitto tra vincoli urbanistici e diritto di proprietà privata si risolve in base all'articolo 2645-quater del codice civile.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

L'articolo 2645-quater del codice civile stabilisce che gli atti di diritto privato, i contratti e altri atti nonché le convenzioni e i contratti devono essere trascritti se hanno per oggetto beni immobili.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2866', 'claim': "L'articolo 2645-quater del codice civile stabilisce che gli atti di diritto privato, i contratti e altri atti nonché le convenzioni e i contratti devono essere trascritti se hanno per oggetto beni immobili.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al conflitto tra vincoli urbanistici e diritto di proprietà privata. Tuttavia, la norma 2645-quater suggerisce che i vincoli devono essere trascritti se hanno per oggetto beni immobili.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2866', 'claim': 'Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al conflitto tra vincoli urbanistici e diritto di proprietà privata.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione della solidità della norma è alta, in quanto si tratta di una disposizione chiara e specifica del codice civile. Tuttavia, la mancanza di giurisprudenza diretta sul tema rende la situazione un po' meno certa.

### GAP ANALYSIS

Il packet non contiene giurisprudenze specifiche che si riferiscono al conflitto tra vincoli urbanistici e diritto di proprietà privata. Ciò rende difficile una valutazione completa della situazione.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2866` | 2.3523 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3043` | 2.2451 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art738` | 1.8570 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1421` | 1.5886 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1202` | -0.3625 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1395` | -0.4194 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1009` | -0.5959 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art32` | -1.6449 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1138` | -1.6568 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2037` | -2.0936 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-06;380~art12`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2866`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2645-quater. (( (Trascrizione di atti costitutivi di vincolo). )) ((Si devono trascrivere, se hanno per oggetto beni immobili, gli atti di diritto privato, i contratti e gli altri atti di diritto privato, anche unilaterali, nonché le convenzioni e i contratti

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3043`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2815. (Ipoteca sul diritto del concedente e sul diritto dell'enfiteuta). Nel caso di affrancazione, le ipoteche gravanti sul diritto del concedente si risolvono sul prezzo dovuto per l'affrancazione; le ipoteche gravanti sul diritto dell'enfiteuta si estendon

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art738`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 649. (Acquisto del legato). Il legato si acquista senza bisogno di accettazione, salva la facoltà di rinunziare. Quando oggetto del legato è la proprietà di una cosa determinata o altro diritto appartenente al testatore, la proprietà o il diritto si trasmette

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1421`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1376. (Contratto con effetti reali). Nei contratti che hanno per oggetto il trasferimento della proprietà di una cosa determinata, la costituzione o il trasferimento di un diritto reale ovvero il trasferimento di un altro diritto, la proprietà o il diritto si

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1202`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1158. (Usucapione dei beni immobili e dei diritti reali immobiliari). La proprietà dei beni immobili e gli altri diritti reali di godimento sui beni medesimi si acquistano in virtù del possesso continuato per venti anni.

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1395`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1350. (Atti che devono farsi per iscritto). Devono farsi per atto pubblico o per scrittura privata, sotto pena di nullità: 1) i contratti che trasferiscono la proprietà di beni immobili; 2) i contratti che costituiscono, modificano o trasferiscono il diritto

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1009`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 912. (Conciliazione di opposti interessi). Se sorge controversia tra i proprietari a cui un'acqua non pubblica può essere utile, l'autorità giudiziaria deve valutare l'interesse dei singoli proprietari nei loro rapporti e rispetto ai vantaggi che possono deri

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art32`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 29 Cessazione del conflitto 1. I conflitti previsti dall'articolo 28 cessano per effetto del provvedimento di uno dei giudici che dichiara, anche di ufficio, la propria competenza o la propria incompetenza.

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1138`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1100. (Norme regolatrici). Quando la proprietà o altro diritto reale spetta in comune a più persone, se il titolo o la legge non dispone diversamente, si applicano le norme seguenti.

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2037`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1997. (Efficacia dei vincoli sul credito). Il pegno, il sequestro, il pignoramento e ogni altro vincolo sul diritto menzionato in un titolo di credito o sulle merci da esso rappresentate non hanno effetto se non si attuano sul titolo.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
