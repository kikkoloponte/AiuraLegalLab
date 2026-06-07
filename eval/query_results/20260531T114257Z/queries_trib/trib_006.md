# trib_006 — tributario

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
| **Latenza** | 5.5s (ret 0.3s + llm 4.6s) |

## Query

> Quali sono le operazioni imponibili ai fini IVA?

## Risposta

**QUALIFICAZIONE**
Le operazioni imponibili ai fini IVA sono quelle che devono essere registrate e annotate dai contribuenti secondo le disposizioni del D.P.R. 29 settembre 1973, n. 600.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica sulle operazioni che devono essere registrate per l'imposta sul valore aggiunto.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le operazioni imponibili ai fini IVA sono quelle che devono essere registrate e annotate dai contribuenti secondo le disposizioni del D.P.R. 29 settembre 1973, n. 600.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art20', 'claim': 'Le operazioni imponibili ai fini IVA sono quelle che devono essere registrate e annotate dai contribuenti.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica sulle operazioni che devono essere registrate per l'imposta sul valore aggiunto.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art965` | 2.2486 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art20` | 1.0082 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315` | -0.3473 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art267` | -1.8583 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art819` | -1.9876 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art969` | -2.1649 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13` | -2.1999 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art315` | -3.3689 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2320` | -4.1035 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge.costituzionale:1948-02-26;4~art13` | -4.8431 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art1`
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art2`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art965`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 786. (Direzione delle operazioni). Le operazioni di divisione sono dirette dal giudice istruttore, il quale, anche nel corso di esse, può delegarne la direzione a un notaio.

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art20`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  i contribuenti possono tenere i registri ai fini dell'imposta sul valore aggiunto senza operare annotazioni relative a incassi e pagamenti, fermo restando l'obbligo della separata annotazione delle operazioni non soggette a registraz

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 268 Esecuzione delle operazioni 1. Le comunicazioni intercettate sono registrate e delle operazioni è redatto verbale. 2. Nel verbale è trascritto, anche sommariamente, soltanto il contenuto delle comunicazioni intercettate rilev

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art267`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 229 Comunicazioni relative alle operazioni peritali 1. Il perito indica il giorno, l'ora e il luogo in cui inizierà le operazioni peritali e il giudice ne fa dare atto nel verbale. 2. Della eventuale continuazione delle operazion

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art819`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 730. (Deferimento delle operazioni a un notaio). Le operazioni indicate negli articoli precedenti possono essere, col consenso di tutti i coeredi, deferite a un notaio. La nomina di questo, in mancanza di accordo, è fatta con decreto dal trbunale del luogo de

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art969`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 790. (Operazioni davanti al notaio). Se a dirigere le operazioni di divisione è stato delegato un notaio, questi dà avviso, almeno cinque giorni prima, ai condividenti e ai creditori intervenuti del luogo, giorno e ora in cui le operazioni avranno inizio.

**[7]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 13 Definizioni 1. Ai fini del presente capo si intende per: a) prezzo di vendita: il prezzo finale, valido per una unità di prodotto o per una determinata quantità del prodotto, comprensivo dell'IVA e di ogni altra imposta; b) prezzo per unità di mis

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art315`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 275-quater. (Violazione delle condizioni dell'autorizzazione allo svolgimento di attività). Chiunque effettua operazioni o presta servizi o comunque svolge attività in difformità dagli obblighi prescritti nella autorizzazione rilasciata dall'autorità compe

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2320`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2279. (Divieto di nuove operazioni). I liquidatori non possono intraprendere nuove operazioni. Contravvenendo a tale divieto, essi rispondono personalmente e solidalmente per gli affari intrapresi.

**[10]** `urn:nir:stato:legge.costituzionale:1948-02-26;4~art13`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 4 Art. 13 Ai fini dell'accertamento delle imposte dirette erariali, gli uffici finanziari dello Stato nella Regione comunicano alla Giunta regionale la lista dei contribuenti che, domiciliati nella Valle, possiedono redditi tassabili al loro nome mediante ru

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
