# trib_006 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:09 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 6.9s (ret 0.3s + llm 6.3s) |

## Query

> Quali sono le operazioni imponibili ai fini IVA?

## Risposta

**QUALIFICAZIONE**
Le operazioni imponibili ai fini IVA sono quelle che devono essere registrate e per le quali si deve pagare l'imposta.

**NORMA APPLICABILE**
Le operazioni imponibili ai fini IVA sono stabilite dal DECRETO LEGISLATIVO 6 settembre 2005, n. 206 (Art. 13).

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle operazioni imponibili ai fini IVA.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma manca una giurisprudenza orientativa.

**GAP ANALYSIS**
C'è un gap nel Packet in quanto non ci sono giurisprudenze che possano fornire ulteriori dettagli o contesto sulle operazioni imponibili ai fini IVA.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le operazioni imponibili ai fini IVA sono quelle che devono essere registrate e per le quali si deve pagare l'imposta.

### NORMA APPLICABILE

Le operazioni imponibili ai fini IVA sono stabilite dal DECRETO LEGISLATIVO 6 settembre 2005, n. 206 (Art. 13).

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-06;206~art13', 'claim': 'Definizioni', 'claim_type': 'DEFINITION', 'source_authority': 'NORMATTIVA'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle operazioni imponibili ai fini IVA.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma manca una giurisprudenza orientativa.

### GAP ANALYSIS

C'è un gap nel Packet in quanto non ci sono giurisprudenze che possano fornire ulteriori dettagli o contesto sulle operazioni imponibili ai fini IVA.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315` | -0.3473 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13` | -2.1999 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art110` | -2.2781 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -4.3410 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art98` | -4.9576 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -5.0279 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art266` | -5.3164 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art223` | -5.3428 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art90` | -5.5782 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2458` | -6.0164 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 268 Esecuzione delle operazioni 1. Le comunicazioni intercettate sono registrate e delle operazioni è redatto verbale. 2. Nel verbale è trascritto, anche sommariamente, soltanto il contenuto delle comunicazioni intercettate rilev

**[2]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 13 Definizioni 1. Ai fini del presente capo si intende per: a) prezzo di vendita: il prezzo finale, valido per una unità di prodotto o per una determinata quantità del prodotto, comprensivo dell'IVA e di ogni altra imposta; b) prezzo per unità di mis

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art110`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 ((Gli uffici doganali eseguono i controlli necessari per l'accertamento delle violazioni di cui al quinto comma dell'art. 46 e ne riferiscono ai competenti uffici dell'imposta sul valore aggiunto. Per le controversie relative alla quali

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 30 settembre 1994, n. 564 (Disposizioni urgenti in materia fiscale), convertito, con modificazioni, dalla legge 30 novembre 1994, n. 656 , abrogati dal presente articolo: "Art. 2-bis (Accertamento con adesione del contribuente ai fini delle imposte sul redd

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art98`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 (Liquidazione dell'imposta dovuta relativamente ((alle operazioni effettuate nell'ambito dei regimi speciali di cui agli articoli 74-quinquies e seguenti)) da soggetti non residenti). ((209)) 1. Avvalendosi di procedure automatizzate l'

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  gennaio 1929, n. 4 , e successive modificazioni, e dal relativo decreto ministeriale di attuazione del 1 settenibre 1931, la quale ha effetto, con unico atto ai sensi del comma 1 e del presente comma, anche ai fini delle imposte sul reddito. L'imposta sul

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art266`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 228 Attività del perito 1. Il perito procede alle operazioni necessarie per rispondere ai quesiti. A tal fine può essere autorizzato dal giudice a prendere visione degli atti, dei documenti e delle cose prodotti dalle parti dei q

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art223`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 179 Regime di neutralità fiscale 1. Alle operazioni indicate nelle lettere a), b) e b-bis) dell'articolo 178 si applicano le disposizioni di cui agli articoli 172 e 173. (132) 2. Ai conferimenti di cui alla lettera c) del comma 1

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 26 ottobre 1995, n. 504 . I dati ed elementi attinenti ai rapporti ed alle operazioni acquisiti e rilevati rispettivamente a norma del numero 7) e dell'articolo 52, ultimo comma, o dell'articolo 63, primo comma, o acquisiti ai sensi del

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2458`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2391-bis. (Operazioni con parti correlate). Gli organi di amministrazione delle società con azioni quotate in mercati regolamentati adottano, secondo principi generali indicati dalla Consob, regole che assicurano la trasparenza e la correttezza sostanziale e

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
