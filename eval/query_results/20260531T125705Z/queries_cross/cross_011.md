# cross_011 — amministrativo+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:19 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 24.8s (ret 0.3s + llm 24.4s) |

## Query

> Qual è il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale?

## Risposta

**QUALIFICAZIONE**
Il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale è regolato dalla legge n. 212 del 27 luglio 2000.

**NORMA APPLICABILE**
Il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale è regolato dall'articolo 6 della legge n. 212 del 27 luglio 2000.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al regime dell'accesso agli atti durante la verifica fiscale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il regime è regolato dalla normativa esistente, ma non ci sono giurisprudenze specifiche che lo interpretino. La solidità della valutazione è media.

**GAP ANALYSIS**
Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al regime dell'accesso agli atti durante la verifica fiscale.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale è regolato dalla legge n. 212 del 27 luglio 2000.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art6', 'claim': "L'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'LEGGE 27 luglio 2000, n. 212'}*

### NORMA APPLICABILE

Il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale è regolato dall'articolo 6 della legge n. 212 del 27 luglio 2000.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art6', 'claim': "L'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'LEGGE 27 luglio 2000, n. 212'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al regime dell'accesso agli atti durante la verifica fiscale.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il regime è regolato dalla normativa esistente, ma non ci sono giurisprudenze specifiche che lo interpretino. La solidità della valutazione è media.

### GAP ANALYSIS

Non ci sono giurisprudenze specifiche menzionate nel packet che si riferiscono esplicitamente al regime dell'accesso agli atti durante la verifica fiscale.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art7` | 3.7601 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art7` | 3.2249 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art6` | 1.0473 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:legge:2000-07-27;212~art6` | 0.6354 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87` | 0.5463 | hybrid_rrf |  |
| 6 | `urn:nir:stato:legge:2000-07-27;212~art19` | -0.1757 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art10` | -0.7778 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art59` | -0.8734 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art48` | -2.2268 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art46` | -2.3939 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:1990-08-07;241~art22`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 Art. 7 Chiarezza e motivazione degli atti 1. Gli atti dell'amministrazione finanziaria ((, autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria,)) sono motivati ((, a pena di annullabilità, indicando specificamente i presupposti, i mezzi di prova)

**[2]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 ici e dipendenti, fermo l'obbligo di autonoma notificazione della cartella di pagamento nei loro confronti. )) 2. Gli atti dell'amministrazione finanziaria e dei concessionari della riscossione devono tassativamente indicare: a) l'ufficio presso il quale è possibile otte

**[3]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212 Art. 6 Conoscenza degli atti e semplificazione 1. L'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati. A tal fine essa provvede comunque a comunicarli nel luogo di effettivo domicilio del contribuente,

**[4]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212  in materia tributaria. L'amministrazione finanziaria assicura che il contribuente possa ottemperare agli obblighi tributari con il minor numero di adempimenti e nelle forme meno costose e più agevoli. 3-ter. Le amministrazioni interessate provvedono alle attività relati

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 L'amministrazione finanziaria può stabilire il domicilio fiscale del soggetto, in deroga alle disposizioni dell'articolo precedente, nel comune dove il soggetto stesso svolge in modo continuativo la principale attività ovvero, per i s

**[6]** `urn:nir:stato:legge:2000-07-27;212~art19`

> LEGGE 27 luglio 2000, n. 212 Art. 19 Attuazione del diritto di interpello del contribuente 1. L'amministrazione finanziaria, nel quadro dell'attuazione del decreto legislativo 30 luglio 1999, n. 300 , adotta ogni opportuno adeguamento della struttura organizzativa ed individua l'occorrente riallocaz

**[7]** `urn:nir:stato:legge:2000-07-27;212~art10`

> LEGGE 27 luglio 2000, n. 212 Art. 10 Tutela dell'affidamento e della buona fede. Errori del contribuente 1. I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede. 2. Non sono irrogate sanzioni nè richiesti interessi moratori al

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 36-ter (Controllo formale delle dichiarazioni) 1. Gli uffici periferici dell'amministrazione finanziaria, procedono, entro il 31 dicembre del secondo anno successivo a quello di presentazione, al controllo formale delle dichiaraz

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art48`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis.2 (( (Presenza negli uffici amministrativi e partecipazione alle indagini amministrative nel territorio dello Stato di funzionari di altri Stati membri o giurisdizioni terze (PAOE)) (( 1. L'Amministrazione finanziaria può

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art46`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis (( (Scambio di informazioni su richiesta). )) (( 1. L'Amministrazione finanziaria provvede allo scambio, con le altre autorità competenti degli Stati membri dell'Unione europea e delle giurisdizioni terze con le quali è in

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
