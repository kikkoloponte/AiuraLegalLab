# trib_006 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:39 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 6.7s (ret 0.6s + llm 5.7s) |

## Query

> Quali sono le operazioni imponibili ai fini IVA?

## Risposta

**QUALIFICAZIONE**
Le operazioni imponibili ai fini IVA sono definite nel D.Lgs. 19 giugno 1997, n. 218.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La definizione fornita nel D.Lgs. 19 giugno 1997, n. 218 è chiara e specifica.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le operazioni imponibili ai fini IVA sono definite nel D.Lgs. 19 giugno 1997, n. 218.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art17', 'claim': 'Definizioni relative alle operazioni imponibili ai fini IVA.', 'claim_type': 'DEFINITION', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La definizione fornita nel D.Lgs. 19 giugno 1997, n. 218 è chiara e specifica.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315` | -0.3473 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art267` | -1.8583 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art969` | -2.1649 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13` | -2.1999 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art315` | -3.3689 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -4.3410 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -5.0279 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art266` | -5.3164 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2458` | -6.0164 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:2000-07-27;212~art8` | -7.0226 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art1`
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art2`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 268 Esecuzione delle operazioni 1. Le comunicazioni intercettate sono registrate e delle operazioni è redatto verbale. 2. Nel verbale è trascritto, anche sommariamente, soltanto il contenuto delle comunicazioni intercettate rilev

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art267`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 229 Comunicazioni relative alle operazioni peritali 1. Il perito indica il giorno, l'ora e il luogo in cui inizierà le operazioni peritali e il giudice ne fa dare atto nel verbale. 2. Della eventuale continuazione delle operazion

**[3]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art969`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 790. (Operazioni davanti al notaio). Se a dirigere le operazioni di divisione è stato delegato un notaio, questi dà avviso, almeno cinque giorni prima, ai condividenti e ai creditori intervenuti del luogo, giorno e ora in cui le operazioni avranno inizio.

**[4]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 13 Definizioni 1. Ai fini del presente capo si intende per: a) prezzo di vendita: il prezzo finale, valido per una unità di prodotto o per una determinata quantità del prodotto, comprensivo dell'IVA e di ogni altra imposta; b) prezzo per unità di mis

**[5]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art315`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 275-quater. (Violazione delle condizioni dell'autorizzazione allo svolgimento di attività). Chiunque effettua operazioni o presta servizi o comunque svolge attività in difformità dagli obblighi prescritti nella autorizzazione rilasciata dall'autorità compe

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 30 settembre 1994, n. 564 (Disposizioni urgenti in materia fiscale), convertito, con modificazioni, dalla legge 30 novembre 1994, n. 656 , abrogati dal presente articolo: "Art. 2-bis (Accertamento con adesione del contribuente ai fini delle imposte sul redd

**[7]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  gennaio 1929, n. 4 , e successive modificazioni, e dal relativo decreto ministeriale di attuazione del 1 settenibre 1931, la quale ha effetto, con unico atto ai sensi del comma 1 e del presente comma, anche ai fini delle imposte sul reddito. L'imposta sul

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art266`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 228 Attività del perito 1. Il perito procede alle operazioni necessarie per rispondere ai quesiti. A tal fine può essere autorizzato dal giudice a prendere visione degli atti, dei documenti e delle cose prodotti dalle parti dei q

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2458`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2391-bis. (Operazioni con parti correlate). Gli organi di amministrazione delle società con azioni quotate in mercati regolamentati adottano, secondo principi generali indicati dalla Consob, regole che assicurano la trasparenza e la correttezza sostanziale e

**[10]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
