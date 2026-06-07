# cross_011 — amministrativo+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:00 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 5.9s (ret 0.4s + llm 5.3s) |

## Query

> Qual è il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale?

## Risposta

**QUALIFICAZIONE**
Durante la verifica fiscale, gli impiegati dell'Amministrazione finanziaria possono accedere ai locali destinati all'esercizio di attività commerciali, agricole, artistiche o professionali.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica sul regime dell'accesso agli atti durante la verifica fiscale.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Durante la verifica fiscale, gli impiegati dell'Amministrazione finanziaria possono accedere ai locali destinati all'esercizio di attività commerciali, agricole, artistiche o professionali.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art92', 'claim': "Gli uffici dell'imposta sul valore aggiunto possono disporre l'accesso di impiegati dell'Amministrazione finanziaria nei locali destinati all'esercizio di attività commerciali, agricole, artistiche o professionali.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica sul regime dell'accesso agli atti durante la verifica fiscale.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art92` | 4.4448 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art7` | 3.2249 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art6` | 1.0473 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:legge:2000-07-27;212~art6` | 0.6354 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87` | 0.5463 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215` | 0.4147 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art19` | -0.1757 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art111` | -0.4197 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge:2000-07-27;212~art10` | -0.7778 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art59` | -0.8734 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:1990-08-07;241~art22`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art92`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Gli uffici dell'imposta sul valore aggiunto possono disporre l'accesso di impiegati dell'Amministrazione finanziaria nei locali destinati all'esercizio di attività commerciali, agricole, artistiche o professionali, nonché in quelli util

**[2]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 ici e dipendenti, fermo l'obbligo di autonoma notificazione della cartella di pagamento nei loro confronti. )) 2. Gli atti dell'amministrazione finanziaria e dei concessionari della riscossione devono tassativamente indicare: a) l'ufficio presso il quale è possibile otte

**[3]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212 Art. 6 Conoscenza degli atti e semplificazione 1. L'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati. A tal fine essa provvede comunque a comunicarli nel luogo di effettivo domicilio del contribuente,

**[4]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212  in materia tributaria. L'amministrazione finanziaria assicura che il contribuente possa ottemperare agli obblighi tributari con il minor numero di adempimenti e nelle forme meno costose e più agevoli. 3-ter. Le amministrazioni interessate provvedono alle attività relati

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 L'amministrazione finanziaria può stabilire il domicilio fiscale del soggetto, in deroga alle disposizioni dell'articolo precedente, nel comune dove il soggetto stesso svolge in modo continuativo la principale attività ovvero, per i s

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Amministrazione. 14. Ai fini dei suddetti procedimenti la società scissa o quella designata debbono indicare, a richiesta degli organi dell'Amministrazione finanziaria, i soggetti e i luoghi presso i quali sono conservate, qualora non

**[7]** `urn:nir:stato:legge:2000-07-27;212~art19`

> LEGGE 27 luglio 2000, n. 212 Art. 19 Attuazione del diritto di interpello del contribuente 1. L'amministrazione finanziaria, nel quadro dell'attuazione del decreto legislativo 30 luglio 1999, n. 300 , adotta ogni opportuno adeguamento della struttura organizzativa ed individua l'occorrente riallocaz

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art111`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 65 ((Obblighi dell'amministrazione finanziaria L'amministrazione finanziaria provvede allo scambio, con le altre autorità competenti degli Stati membri della Comunità economica europea, delle informazioni necessarie per assicurare

**[9]** `urn:nir:stato:legge:2000-07-27;212~art10`

> LEGGE 27 luglio 2000, n. 212 Art. 10 Tutela dell'affidamento e della buona fede. Errori del contribuente 1. I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede. 2. Non sono irrogate sanzioni nè richiesti interessi moratori al

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 36-ter (Controllo formale delle dichiarazioni) 1. Gli uffici periferici dell'amministrazione finanziaria, procedono, entro il 31 dicembre del secondo anno successivo a quello di presentazione, al controllo formale delle dichiaraz

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
