# cross_014 — tributario+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 11:54 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 33.6s (ret 0.3s + llm 32.3s) |

## Query

> Come interagiscono le procedure concorsuali (fallimento) con i crediti tributari?

## Risposta

**QUALIFICAZIONE**
Le procedure concorsuali (fallimento) possono influire sui crediti tributari. Il DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 regola le interazioni tra i due ambiti.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 88 e Art. 63 regolamentano la questione.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel packet che affrontano l'interazione tra le procedure concorsuali e i crediti tributari.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La normativa è chiara, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

**GAP ANALYSIS**
Il packet non contiene giurisprudenze che affrontano specificamente l'interazione tra le procedure concorsuali e i crediti tributari.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le procedure concorsuali (fallimento) possono influire sui crediti tributari. Il DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 regola le interazioni tra i due ambiti.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art88', 'claim': 'Il decreto legge 12 gennaio 2019, n. 14 regola il trattamento dei crediti tributari nel concordato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art63', 'claim': 'Il decreto legge 12 gennaio 2019, n. 14 regola anche le trattative per i crediti tributari.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 88 e Art. 63 regolamentano la questione.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art88', 'claim': 'Art. 88 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 regola il trattamento dei crediti tributari nel concordato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art63', 'claim': 'Art. 63 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 regola le trattative per i crediti tributari.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel packet che affrontano l'interazione tra le procedure concorsuali e i crediti tributari.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La normativa è chiara, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

### GAP ANALYSIS

Il packet non contiene giurisprudenze che affrontano specificamente l'interazione tra le procedure concorsuali e i crediti tributari.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art28` | 1.4005 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2463` | 0.3055 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art288` | 0.0924 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -0.5600 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -2.2006 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art671` | -2.5635 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2983` | -2.6983 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art349` | -2.8503 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art63` | -3.0824 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art158` | -3.6778 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art19`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art28`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81  disposto (con l'art. 1, comma 5-bis) che "Nelle more della conclusione delle procedure concorsuali, di cui all' articolo 4, comma 6, del decreto-legge 31 agosto 2013, n. 101 , convertito, con modificazioni, dalla legge 30 ottobre 2013, n. 125 , da bandire e

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2463`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2394-bis. (Azioni di responsabilità nelle procedure concorsuali). In caso ((di liquidazione giudiziale, concordato liquidatorio,)) , liquidazione coatta amministrativa e amministrazione straordinaria le azioni di responsabilità previste dai precedenti articol

**[3]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art288`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 288 Procedure concorsuali autonome di imprese appartenenti allo stesso gruppo 1. Nel caso in cui più imprese appartenenti a un medesimo gruppo siano assoggettate a separate procedure di liquidazione giudiziale ovvero a separate procedure di concordato

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 88 (( (Trattamento dei crediti tributari e contributivi). )) (( 1. Con il piano di concordato il debitore, esclusivamente mediante proposta presentata ai sensi del presente articolo, può proporre il pagamento, parziale o anche dilazionato, dei tributi

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 azione del professionista indipendente, relativamente ai crediti tributari e contributivi, ha ad oggetto anche, nel concordato liquidatorio, la convenienza del trattamento proposto rispetto alla liquidazione giudiziale e, nel concordato in continuità aziend

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art671`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 528. (Intervento tardivo). ((I creditori chirografari che intervengono successivamente ai termini di cui all'articolo 525, ma prima del provvedimento di distribuzione, concorrono alla distribuzione della parte della somma ricavata che sopravanza dopo soddi

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2983`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2758. ((Crediti per tributi indiretti.)) ((I crediti dello Stato per i tributi indiretti hanno privilegio sui mobili ai quali i tributi si riferiscono e sugli altri beni indicati dalle leggi relative, con l'effetto da esse stabilito. Eguale privilegio hanno i

**[8]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art349`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 349 Sostituzione dei termini fallimento e fallito 1. Nelle disposizioni normative vigenti i termini «fallimento», «procedura fallimentare», «fallito» nonchè le espressioni dagli stessi termini derivate devono intendersi sostituite, rispettivamente, con

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art63`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 63 (( (Transazione su crediti tributari e contributivi).)) (( 1. Nell'ambito delle trattative che precedono la stipulazione degli accordi di ristrutturazione di cui agli articoli 57, 60 e 61 il debitore può proporre il pagamento, parziale o anche dilaz

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art158`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 158 Crediti non pecuniari 1. I crediti non scaduti, aventi per oggetto una prestazione in danaro determinata con riferimento ad altri valori o aventi per oggetto una prestazione diversa dal danaro, concorrono secondo il loro valore alla data di apertur

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
