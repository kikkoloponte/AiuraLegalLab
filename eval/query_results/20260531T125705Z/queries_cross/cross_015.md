# cross_015 — amministrativo+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:21 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 33.5s (ret 0.3s + llm 33.0s) |

## Query

> Qual è la disciplina dell'espropriazione per pubblica utilità e l'indennità dovuta?

## Risposta

**QUALIFICAZIONE**
L'espropriazione per pubblica utilità è disciplinata dal Codice Civile e dalla Legge Costituzionale.

**NORMA APPLICABILE**
L'espropriazione per pubblica utilità è disciplinata dall'Art. 834 del Codice Civile.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'espropriazione per pubblica utilità e l'indennità dovuta.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della norma è alta, ma la mancanza di giurisprudenza specifica rende la valutazione media.

**GAP ANALYSIS**
Il Packet non contiene giurisprudenze specifiche sull'espropriazione per pubblica utilità e l'indennità dovuta.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'espropriazione per pubblica utilità è disciplinata dal Codice Civile e dalla Legge Costituzionale.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art834', 'claim': 'Nessuno può essere privato in tutto o in parte dei beni di sua proprietà, se non per causa di pubblico interesse, legalmente dichiarata, e contro il pagamento di una giusta indennità.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'urn:nir:stato:legge.costituzionale:1993-09-23;2~art5', 'claim': "La legge costituzionale elenca diversi ambiti in cui l'espropriazione per pubblica utilità può avvenire.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

L'espropriazione per pubblica utilità è disciplinata dall'Art. 834 del Codice Civile.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art834', 'claim': 'Nessuno può essere privato in tutto o in parte dei beni di sua proprietà, se non per causa di pubblico interesse, legalmente dichiarata, e contro il pagamento di una giusta indennità.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'espropriazione per pubblica utilità e l'indennità dovuta.

*Citazioni: {'source_id': '', 'claim': "VALUTAZIONE PERSONALE: Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'espropriazione per pubblica utilità e l'indennità dovuta.", 'claim_type': 'OPINION', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della norma è alta, ma la mancanza di giurisprudenza specifica rende la valutazione media.

### GAP ANALYSIS

Il Packet non contiene giurisprudenze specifiche sull'espropriazione per pubblica utilità e l'indennità dovuta.

*Citazioni: {'source_id': '', 'claim': "VALUTAZIONE PERSONALE: Il Packet non contiene giurisprudenze specifiche sull'espropriazione per pubblica utilità e l'indennità dovuta.", 'claim_type': 'OPINION', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1058` | 4.1465 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1696` | 3.3418 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art930` | 2.8008 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5` | 2.6091 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art975` | 1.2605 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art754` | 0.7490 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art934` | -0.3306 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art511` | -0.8607 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art961` | -1.7358 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2286` | -2.7511 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art32`
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art37`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1058`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1020. (Requisizione o espropriazione). Se la cosa è requisita o espropriata per pubblico interesse, l'usufrutto si trasferisce sull'indennità relativa.

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1696`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1638. (Espropriazione per pubblico interesse). In caso di espropriazione per pubblico interesse o di occupazione temporanea del fondo locato, l'affittuario ha diritto di ottenere dal locatore la parte d'indennità a questo corrisposta per i frutti non percepit

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art930`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 834. (Espropriazione per pubblico interesse). Nessuno può essere privato in tutto o in parte dei beni di sua proprietà, se non per causa di pubblico interesse, legalmente dichiarata, e contro il pagamento di una giusta indennità. Le norme relative all'espropr

**[4]** `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5`

> LEGGE COSTITUZIONALE 23 settembre 1993, n. 2  di programmi di sviluppo economico; 10) miniere, cave e torbiere; 11) espropriazione per pubblica utilità non riguardanti opere a carico dello Stato; 12) linee marittime di cabotaggio tra gli scali della regione; 13) polizia locale, urbana e rurale; 14)

**[5]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art975`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 795. (Espropriazione). Se è fatta istanza di espropriazione, il giudice, verificate le condizioni stabilite dalla legge per l'ammissibilità di essa, dispone con decreto che si proceda a norma degli articoli 567 e seguenti. La vendita non può essere fatta c

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art754`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 602. (Modo dell'espropriazione). Quando oggetto dell'espropriazione è un bene gravato da pegno o da ipoteca per un debito altrui, oppure un bene la cui alienazione da parte del debitore è stata revocata per frode, si applicano le disposizioni contenute nei

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art934`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 838. (Espropriazione di beni che interessano la produzione nazionale o di prevalente interesse pubblico). Salve le disposizioni delle leggi penali e di polizia, nonché le norme dell'ordinamento corporativo e le disposizioni particolari concernenti beni determ

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art511`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 420. (Attentato a impianti di pubblica utilità). Chiunque commette un fatto diretto a danneggiare o distruggere impianti di pubblica utilità, è punito, salvo che il fatto costituisca più grave reato, con la reclusione da uno a quattro anni. ((COMMA ABROGAT

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art961`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 865. (Espropriazione per inosservanza degli obblighi). Quando l'inosservanza degli obblighi imposti ai proprietari risulta tale da compromettere l'attuazione del piano di bonifica, può farsi luogo all'espropriazione parziale o totale del fondo appartenente al

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2286`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2245. (Indennità di anzianità). In caso di cessazione del contratto è dovuta al prestatore di lavoro un'indennità proporzionale agli anni di servizio, salvo il caso di licenziamento per colpa di lui o di dimissioni volontarie. L'ammontare dell'indennità è det

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
