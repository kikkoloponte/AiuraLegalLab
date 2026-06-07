# trib_006 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:28 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 26.3s (ret 0.2s + llm 25.9s) |

## Query

> Quali sono le operazioni imponibili ai fini IVA?

## Risposta

**QUALIFICAZIONE**
Le operazioni imponibili ai fini IVA sono quelle che vengono eseguite dalle imprese nel corso delle loro attività commerciali e productive.

**NORMA APPLICABILE**
Le operazioni imponibili ai fini IVA sono stabilite dal DECRETO LEGISLATIVO 9 luglio 1997, n. 241 Art. 11.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle operazioni imponibili ai fini IVA.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma non ci sono giurisprudenze contrastanti. La solidità della valutazione è ALTA.

**GAP ANALYSIS**
Non ci sono giurisprudenze menzionate nel Packet che si riferiscano alle operazioni imponibili ai fini IVA. Potrebbe essere utile includere giurisprudenza per confermare la valutazione.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le operazioni imponibili ai fini IVA sono quelle che vengono eseguite dalle imprese nel corso delle loro attività commerciali e productive.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-07-09;241~art11', 'claim': "DECRETO LEGISLATIVO 9 luglio 1997, n. 241 Art. 11 individuazione del contribuente, per la determinazione dell'ammontare delle operazioni e dell'imposta nonchè per l'effettuazione dei controlli e gli altri elementi richiesti nel modello di dichiarazione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA'}*

### NORMA APPLICABILE

Le operazioni imponibili ai fini IVA sono stabilite dal DECRETO LEGISLATIVO 9 luglio 1997, n. 241 Art. 11.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-07-09;241~art11', 'claim': "DECRETO LEGISLATIVO 9 luglio 1997, n. 241 Art. 11 individuazione del contribuente, per la determinazione dell'ammontare delle operazioni e dell'imposta nonchè per l'effettuazione dei controlli e gli altri elementi richiesti nel modello di dichiarazione.", 'claim_type': 'NORMA', 'source_authority': 'NORMATTIVA'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle operazioni imponibili ai fini IVA.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma non ci sono giurisprudenze contrastanti. La solidità della valutazione è ALTA.

### GAP ANALYSIS

Non ci sono giurisprudenze menzionate nel Packet che si riferiscano alle operazioni imponibili ai fini IVA. Potrebbe essere utile includere giurisprudenza per confermare la valutazione.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art11` | -0.1647 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art14` | -4.3566 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -5.0279 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art223` | -5.3428 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art90` | -5.5782 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art14` | -6.4277 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art8` | -7.0226 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge:2000-07-27;212~art8` | -7.1334 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art70` | -7.3141 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art120` | -8.8470 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art11`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 ividuazione del contribuente, per la determinazione dell'ammontare delle operazioni e dell'imposta nonchè per l'effettuazione dei controlli e gli altri elementi richiesti nel modello di dichiarazione, esclusi quelli che l'Amministrazione finanziaria è in gra

**[2]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art14`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 'art. 26. Tuttavia, in deroga a tale disposizione, il contribuente che affida a terzi la tenuta della contibilità, ai fini del calcolo della differenza di imposta relativa al mese precedente può fare riferimento alle annotazioni eseguite per il secondo mese

**[3]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  gennaio 1929, n. 4 , e successive modificazioni, e dal relativo decreto ministeriale di attuazione del 1 settenibre 1931, la quale ha effetto, con unico atto ai sensi del comma 1 e del presente comma, anche ai fini delle imposte sul reddito. L'imposta sul

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art223`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 179 Regime di neutralità fiscale 1. Alle operazioni indicate nelle lettere a), b) e b-bis) dell'articolo 178 si applicano le disposizioni di cui agli articoli 172 e 173. (132) 2. Ai conferimenti di cui alla lettera c) del comma 1

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 26 ottobre 1995, n. 504 . I dati ed elementi attinenti ai rapporti ed alle operazioni acquisiti e rilevati rispettivamente a norma del numero 7) e dell'articolo 52, ultimo comma, o dell'articolo 63, primo comma, o acquisiti ai sensi del

**[6]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art14`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 ati dagli esercenti impianti di distribuzione di carburante per uso di autotrazione e dagli autotrasportatori iscritti nell'albo sopra indicato, nonchè per le liquidazioni ed i versamenti trimestrali disposti con decreti del Ministro delle finanze, emanati a

**[7]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

**[8]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  parte di altri soggetti, deve sempre comprendere l'indicazione dei redditi anche al netto delle relative imposte. 8. Ferme restando, in via transitoria, le disposizioni vigenti in materia di compensazione, con regolamenti emanati ai sensi dell' articolo 17, comma 2, del

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art70`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Gli accertamenti in rettifica e gli accertamenti d'ufficio sono portati a conoscenza dei contribuenti mediante la notificazione di avvisi sottoscritti dal capo dell'ufficio o da altro impiegato della carriera direttiva da lui delegato

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art120`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  disposizioni emanate in attuazione dell' articolo 1, comma 60, della legge 24 dicembre 2007, n. 244 , dell' articolo 4, commi 7-quater e 7-quinquies, del decreto legislativo 28 febbraio 2005, n. 38 , e dell' articolo 13-bis, comma 11,

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
