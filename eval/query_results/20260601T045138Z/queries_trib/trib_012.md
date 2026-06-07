# trib_012 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:30 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 23.4s (ret 0.2s + llm 23.0s) |

## Query

> Come si determina la base imponibile IRES per le società di capitali?

## Risposta

**QUALIFICAZIONE**
La base imponibile IRES per le società di capitali è determinata secondo le disposizioni della sezione I del capo II.

**NORMA APPLICABILE**
Il DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 75 stabilisce la base imponibile.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alla determinazione della base imponibile IRES per le società di capitali.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, quindi la solidità dell'interpretazione è alta.

**GAP ANALYSIS**
Non ci sono giurisprudenze menzionate nel Packet che si riferiscano alla determinazione della base imponibile IRES per le società di capitali. Potrebbe essere utile esaminare ulteriori fonti giurisprudenziali.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La base imponibile IRES per le società di capitali è determinata secondo le disposizioni della sezione I del capo II.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art96', 'claim': 'La base imponibile IRES per le società di capitali è determinata secondo le disposizioni della sezione I del capo II.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 75 stabilisce la base imponibile.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art96', 'claim': 'Il DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 75 stabilisce la base imponibile.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alla determinazione della base imponibile IRES per le società di capitali.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, quindi la solidità dell'interpretazione è alta.

### GAP ANALYSIS

Non ci sono giurisprudenze menzionate nel Packet che si riferiscano alla determinazione della base imponibile IRES per le società di capitali. Potrebbe essere utile esaminare ulteriori fonti giurisprudenziali.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art96` | 5.7262 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art166` | 5.5782 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art193` | 2.9994 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172` | 2.6479 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art149` | 0.2345 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art177` | -0.4932 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380` | -0.5215 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art33` | -2.1093 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art258` | -3.4858 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art26` | -3.8085 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art96`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 75 Base imponibile 1. L'imposta si applica sul reddito complessivo netto, determinato secondo le disposizioni della sezione I del capo II, per le società e gli enti di cui alle lettere a) e b) del comma 1 dell'articolo 73, del cap

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art166`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 130 ((Soggetti ammessi alla determinazione della unica base imponibile per il gruppo di imprese non residenti.)) (( 1. Le società e gli enti di cui all'articolo 73, comma 1, lettere a) e b), possono esercitare l'opzione per includ

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art193`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 156 Determinazione del reddito imponibile 1. Il reddito imponibile, determinato in via forfetaria ed unitaria sulla base del reddito giornaliero di ciascuna nave con i requisiti predetti, è calcolato sulla base degli importi in ci

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 136 Determinazione dell'imposta dovuta 1. La società controllante, effettuando la somma algebrica del proprio imponibile e di quelli delle controllate estere determinati secondo i criteri ((di cui agli articoli precedenti)) , dete

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art149`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 116 ((Opzione per la trasparenza fiscale delle società a ristretta base proprietaria)) 1. L'opzione di cui all'articolo 115 può essere esercitata con le stesse modalità ed alle stesse condizioni, ad esclusione di quelle indicate n

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art177`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 140 ((Coordinamento con l'articolo 167 )) (( 1. Le disposizioni di cui all'articolo 167 non si applicano relativamente alle controllate estere il cui imponibile viene incluso in quello della società controllante per effetto dell'o

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 380 (( (Cause di scioglimento delle società di capitali).)) (( 1. All' articolo 2484, primo comma, del codice civile dopo il numero 7) è aggiunto il seguente: "7-bis) per l'apertura della procedura di liquidazione giudiziale e della liquidazione contro

**[8]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art33`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 Art. 33 (( (Requisiti soggettivi). )) (( 1. I centri sono costituiti nella forma di società di capitali. L'oggetto sociale dei centri prevede lo svolgimento delle attività di assistenza fiscale di cui all'articolo 34. 2. I centri designano uno o più responsa

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art258`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 258 Effetti sulla società dell'apertura della liquidazione giudiziale nei confronti dei soci 1. La liquidazione giudiziale aperta nei confronti di uno o più soci illimitatamente responsabili non determina l'apertura della liquidazione giudiziale nei co

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art26`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 19 Indennità di fine rapporto 1. Il trattamento di fine rapporto costituisce reddito per un importo che si determina riducendo il suo ammontare delle rivalutazioni già assoggettate ad imposta sostitutiva. L'imposta è applicata con

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
