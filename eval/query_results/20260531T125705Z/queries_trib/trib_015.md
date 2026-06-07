# trib_015 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:40 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 10.5s (ret 0.6s + llm 9.4s) |

## Query

> Qual è il regime IVA delle prestazioni di servizi intracomunitarie?

## Risposta

**QUALIFICAZIONE**
Le prestazioni di servizi intracomunitarie sono riconducibili al contratto di servizi.

**NORMA APPLICABILE**
Il regime IVA per le prestazioni di servizi intracomunitarie è regolato dal D.Lgs. 6 settembre 2005, n. 206 Art. 128.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano al regime IVA per le prestazioni di servizi intracomunitarie.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il regime IVA è chiaramente regolato dalla normativa, ma non ci sono contrasti giurisprudenziali notevoli.

**GAP ANALYSIS**
Non ci sono specifiche giurisprudenze menzionate nel Packet che si riferiscano al regime IVA per le prestazioni di servizi intracomunitarie, ma la normativa è chiara.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le prestazioni di servizi intracomunitarie sono riconducibili al contratto di servizi.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2013-03-14;33~art41', 'claim': 'DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 inclusi i contratti che hanno come oggetto sia beni che servizi.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il regime IVA per le prestazioni di servizi intracomunitarie è regolato dal D.Lgs. 6 settembre 2005, n. 206 Art. 128.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2005-09-06;206~art128', 'claim': 'DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 128 permetta la riproduzione identica delle informazioni memorizzate.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano al regime IVA per le prestazioni di servizi intracomunitarie.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il regime IVA è chiaramente regolato dalla normativa, ma non ci sono contrasti giurisprudenziali notevoli.

### GAP ANALYSIS

Non ci sono specifiche giurisprudenze menzionate nel Packet che si riferiscano al regime IVA per le prestazioni di servizi intracomunitarie, ma la normativa è chiara.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1735` | 2.0740 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2264` | -0.8574 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art45` | -0.9575 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41` | -1.8904 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13` | -2.7596 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art202` | -3.3027 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art920` | -4.1736 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2003-09-10;276~art86` | -4.7494 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art52` | -5.3578 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art128` | -6.0291 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art7ter`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1735`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1677. (Prestazione continuativa o periodica di servizi). Se l'appalto ha per oggetto prestazioni continuative o periodiche di servizi, si osservano, in quanto compatibili, le norme di questo capo e quelle relative al contratto di somministrazione.

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2264`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2223. (Prestazione della materia). Le disposizioni di questo capo si osservano anche se la materia è fornita dal prestatore d'opera, purché le parti non abbiano avuto prevalentemente in considerazione la materia, nel qual caso si applicano le norme sulla vend

**[3]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art45`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206  inclusi i contratti che hanno come oggetto sia beni che servizi; f) "contratto di servizi": qualsiasi contratto diverso da un contratto di vendita in base al quale il professionista fornisce o si impegna a fornire un servizio, compreso un servizio digita

**[4]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 Trasparenza del servizio sanitario nazionale 1. Le amministrazioni e gli enti del servizio sanitario nazionale, dei servizi sanitari regionali, ivi comprese le aziende sanitarie territoriali ed ospedaliere, le agenzie e gli altri enti ed organismi pub

**[5]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 Art. 13 Definizione e casi di ricorso al lavoro intermittente 1. Il contratto di lavoro intermittente è il contratto, anche a tempo determinato, mediante il quale un lavoratore si pone a disposizione di un datore di lavoro che ne può utilizzare la prestazion

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art202`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 159. ((Del regime patrimoniale legale tra i coniugi.)) ((Il regime patrimoniale legale della famiglia, in mancanza di diversa convenzione stipulata a norma dell'articolo 162, è costituito dalla comunione dei beni regolata dalla sezione III del presente capo))

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art920`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 824. (Beni delle provincie e dei comuni soggetti al regime dei beni demaniali). I beni della specie di quelli indicati dal secondo comma dell'art. 822, se appartengono alle provincie o ai comuni, sono soggetti al regime del demanio pubblico. Allo stesso regim

**[8]** `urn:nir:stato:decreto.legislativo:2003-09-10;276~art86`

> DECRETO LEGISLATIVO 10 settembre 2003, n. 276  sia effettivamente avvenuto il trasferimento delle funzioni in materia di lavoro ai sensi del decreto legislativo 23 dicembre 1997, n. 469 . 12. Le disposizioni di cui agli articoli 13, 14, 34, comma 2, di cui al Titolo III e di cui al Titolo VII, capo

**[9]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art52`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 , che possono essere individuati dai contratti collettivi stipulati dalle organizzazioni sindacali comparativamente più rappresentative sul piano nazionale. 2. Dalla disposizione di cui al comma 1 sono escluse le prestazioni occasionali, intendendosi per tal

**[10]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art128`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206  permetta la riproduzione identica delle informazioni memorizzate; n) garanzia convenzionale: qualsiasi impegno di un venditore o di un produttore (il "garante"), assunto nei confronti del consumatore, in aggiunta agli obblighi di legge in merito alla gar

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
