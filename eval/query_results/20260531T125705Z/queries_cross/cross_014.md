# cross_014 — tributario+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:21 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 27.2s (ret 0.3s + llm 26.7s) |

## Query

> Come interagiscono le procedure concorsuali (fallimento) con i crediti tributari?

## Risposta

**QUALIFICAZIONE**
Le procedure concorsuali (fallimento) possono influire sui crediti tributari.

**NORMA APPLICABILE**
Le norme applicabili sono Articoli 88 e 63 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano l'interazione tra le procedure concorsuali e i crediti tributari.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme sono chiare ma non ci sono giurisprudenze contrastanti. La solidità è alta.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le procedure concorsuali (fallimento) possono influire sui crediti tributari.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art88', 'claim': 'Nel concordato liquidatorio, il debitore può proporre il pagamento dei tributi.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art63', 'claim': 'Il debitore può proporre il pagamento, parziale o dilazionato, dei crediti tributari durante le trattative per la stipulazione degli accordi di ristrutturazione.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Le norme applicabili sono Articoli 88 e 63 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art88', 'claim': 'Nel concordato liquidatorio, il debitore può proporre il pagamento dei tributi.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art63', 'claim': 'Il debitore può proporre il pagamento, parziale o dilazionato, dei crediti tributari durante le trattative per la stipulazione degli accordi di ristrutturazione.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che affrontano l'interazione tra le procedure concorsuali e i crediti tributari.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme sono chiare ma non ci sono giurisprudenze contrastanti. La solidità è alta.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art28` | 1.4005 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2463` | 0.3055 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art288` | 0.0924 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -0.5600 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -2.2006 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:legge:2000-07-27;212~art6` | -2.2433 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2983` | -2.6983 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art349` | -2.8503 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art63` | -3.0824 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:legge:2000-07-27;212~art6` | -3.2948 | hybrid_rrf |  |

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

**[6]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212  tributi per i quali il contribuente non è tenuto ad effettuare il versamento diretto. Sono ((annullabili)) i provvedimenti emessi in violazione delle disposizioni di cui al presente comma. (9) 5-bis. In caso di esercizio di attività istruttorie di controllo nei confront

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2983`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2758. ((Crediti per tributi indiretti.)) ((I crediti dello Stato per i tributi indiretti hanno privilegio sui mobili ai quali i tributi si riferiscono e sugli altri beni indicati dalle leggi relative, con l'effetto da esse stabilito. Eguale privilegio hanno i

**[8]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art349`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 349 Sostituzione dei termini fallimento e fallito 1. Nelle disposizioni normative vigenti i termini «fallimento», «procedura fallimentare», «fallito» nonchè le espressioni dagli stessi termini derivate devono intendersi sostituite, rispettivamente, con

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art63`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 63 (( (Transazione su crediti tributari e contributivi).)) (( 1. Nell'ambito delle trattative che precedono la stipulazione degli accordi di ristrutturazione di cui agli articoli 57, 60 e 61 il debitore può proporre il pagamento, parziale o anche dilaz

**[10]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212  in materia tributaria. L'amministrazione finanziaria assicura che il contribuente possa ottemperare agli obblighi tributari con il minor numero di adempimenti e nelle forme meno costose e più agevoli. 3-ter. Le amministrazioni interessate provvedono alle attività relati

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
