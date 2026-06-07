# trib_015 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:11 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 10.5s (ret 0.3s + llm 9.9s) |

## Query

> Qual è il regime IVA delle prestazioni di servizi intracomunitarie?

## Risposta

**QUALIFICAZIONE**
Le prestazioni di servizi intracomunitarie sono soggette al regime forfetario previsto dal D.P.R. 22 dicembre 1986, n. 917, Art. 145.

**NORMA APPLICABILE**
Il regime forfetario previsto nel D.P.R. 22 dicembre 1986, n. 917, Art. 145 si estende di anno in anno qualora i limiti indicati al comma 1 non vengano superati.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente al regime IVA per le prestazioni di servizi intracomunitarie.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il regime forfetario è stabile e non ci sono contrasti giurisprudenziali notevoli.

**GAP ANALYSIS**
Il Packet manca di giurisprudenza specifica sul regime IVA per le prestazioni di servizi intracomunitarie.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le prestazioni di servizi intracomunitarie sono soggette al regime forfetario previsto dal D.P.R. 22 dicembre 1986, n. 917, Art. 145.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art145', 'claim': 'Le prestazioni di servizi intracomunitarie sono soggette al regime forfetario.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917'}*

### NORMA APPLICABILE

Il regime forfetario previsto nel D.P.R. 22 dicembre 1986, n. 917, Art. 145 si estende di anno in anno qualora i limiti indicati al comma 1 non vengano superati.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art145', 'claim': 'Il regime forfetario si estende di anno in anno.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente al regime IVA per le prestazioni di servizi intracomunitarie.

*Citazioni: {'source_id': '', 'claim': 'Nessuna giurisprudenza specifica è presente nel Packet.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il regime forfetario è stabile e non ci sono contrasti giurisprudenziali notevoli.

### GAP ANALYSIS

Il Packet manca di giurisprudenza specifica sul regime IVA per le prestazioni di servizi intracomunitarie.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | 5.4400 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1735` | 2.0740 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art32` | -0.0720 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2264` | -0.8574 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -1.4138 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41` | -1.8904 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138` | -2.2640 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | -2.5758 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13` | -2.7596 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -3.1340 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art7ter`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi. 3. Il regime forfetario previsto nel presente articolo si estende di anno in anno qualora i limiti indicati al comma 1 non ven

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1735`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1677. (Prestazione continuativa o periodica di servizi). Se l'appalto ha per oggetto prestazioni continuative o periodiche di servizi, si osservano, in quanto compatibili, le norme di questo capo e quelle relative al contratto di somministrazione.

**[3]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art32`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 32 Obblighi di pubblicazione concernenti i servizi erogati 1. Le pubbliche amministrazioni ((e i gestori di pubblici servizi)) pubblicano la carta dei servizi o il documento contenente gli standard di qualità dei servizi pubblici. 2. Le pubbliche amminis

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2264`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2223. (Prestazione della materia). Le disposizioni di questo capo si osservano anche se la materia è fornita dal prestatore d'opera, purché le parti non abbiano avuto prevalentemente in considerazione la materia, nel qual caso si applicano le norme sulla vend

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia. (126) 3. Ai fini della determinazione in denaro dei valori di cui al comma 1, compresi quelli dei beni ceduti e dei servizi prestati al co

**[6]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 Trasparenza del servizio sanitario nazionale 1. Le amministrazioni e gli enti del servizio sanitario nazionale, dei servizi sanitari regionali, ivi comprese le aziende sanitarie territoriali ed ospedaliere, le agenzie e gli altri enti ed organismi pub

**[7]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 lici servizi relative a concessioni di pubblici servizi, escluse quelle concernenti indennità, canoni ed altri corrispettivi, ovvero relative a provvedimenti adottati dalla pubblica amministrazione o dal gestore di un pubblico servizio in un procedimento amm

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 145 ((Regime forfetario degli enti non commerciali )) (( 1. Fatto salvo quanto previsto, per le associazioni sportive dilettantistiche, dalla legge 16 dicembre 1991, n. 398 , e, per le associazioni senza scopo di lucro e per le pr

**[9]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 Art. 13 Definizione e casi di ricorso al lavoro intermittente 1. Il contratto di lavoro intermittente è il contratto, anche a tempo determinato, mediante il quale un lavoratore si pone a disposizione di un datore di lavoro che ne può utilizzare la prestazion

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  MODIFICAZIONI DALLA L. 24 LUGLIO 2008, N. 126 ; c) le somministrazioni di vitto da parte del datore di lavoro nonché quelle in mense organizzate direttamente dal datore di lavoro o gestite da terzi; le prestazioni sostitutive delle so

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
