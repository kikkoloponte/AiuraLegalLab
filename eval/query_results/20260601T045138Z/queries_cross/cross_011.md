# cross_011 — amministrativo+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:06 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 31.0s (ret 0.3s + llm 30.4s) |

## Query

> Qual è il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale?

## Risposta

**QUALIFICAZIONE**
Durante la verifica fiscale, gli atti dell'amministrazione finanziaria sono generalmente accessibili al contribuente.

**NORMA APPLICABILE**
Il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale è regolato dall'articolo 10 del DECRETO LEGISLATIVO 18 agosto 2000, n. 267.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente al regime dell'accesso agli atti durante la verifica fiscale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il regime dell'accesso agli atti dell'amministrazione finanziaria è stabilito dalla normativa e non ci sono contrasti giurisprudenziali rilevanti.

**GAP ANALYSIS**
Il Packet manca di giurisprudenza specifica riguardante il regime dell'accesso agli atti durante la verifica fiscale.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Durante la verifica fiscale, gli atti dell'amministrazione finanziaria sono generalmente accessibili al contribuente.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2000-08-18;267~art12', 'claim': "Articolo 10 del DLGS 18 agosto 2000, n. 267 stabilisce che tutti gli atti dell'amministrazione comunale e provinciale sono pubblici ad eccezione di quelli riservati per espressa indicazione di legge o per effetto di una temporanea e motivata dichiarazione del sindaco.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art6', 'claim': "Articolo 6 del DLGS 27 luglio 2000, n. 212 stabilisce che l'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il regime dell'accesso agli atti dell'amministrazione finanziaria durante la verifica fiscale è regolato dall'articolo 10 del DECRETO LEGISLATIVO 18 agosto 2000, n. 267.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2000-08-18;267~art12', 'claim': "Articolo 10 del DLGS 18 agosto 2000, n. 267 stabilisce che tutti gli atti dell'amministrazione comunale e provinciale sono pubblici ad eccezione di quelli riservati per espressa indicazione di legge o per effetto di una temporanea e motivata dichiarazione del sindaco.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente al regime dell'accesso agli atti durante la verifica fiscale.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il regime dell'accesso agli atti dell'amministrazione finanziaria è stabilito dalla normativa e non ci sono contrasti giurisprudenziali rilevanti.

### GAP ANALYSIS

Il Packet manca di giurisprudenza specifica riguardante il regime dell'accesso agli atti durante la verifica fiscale.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art92` | 4.4448 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art7` | 3.2249 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2000-08-18;267~art12` | 2.7893 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge:2000-07-27;212~art6` | 1.0473 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:legge:2000-07-27;212~art6` | 0.6354 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87` | 0.5463 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215` | 0.4147 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art111` | -0.4197 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art59` | -0.8734 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2007-11-21;231~art21` | -2.2401 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:1990-08-07;241~art22`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art92`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Gli uffici dell'imposta sul valore aggiunto possono disporre l'accesso di impiegati dell'Amministrazione finanziaria nei locali destinati all'esercizio di attività commerciali, agricole, artistiche o professionali, nonché in quelli util

**[2]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 ici e dipendenti, fermo l'obbligo di autonoma notificazione della cartella di pagamento nei loro confronti. )) 2. Gli atti dell'amministrazione finanziaria e dei concessionari della riscossione devono tassativamente indicare: a) l'ufficio presso il quale è possibile otte

**[3]** `urn:nir:stato:decreto.legislativo:2000-08-18;267~art12`

> DECRETO LEGISLATIVO 18 agosto 2000, n. 267 Articolo 10 Diritto di accesso e di informazione 1. Tutti gli atti dell'amministrazione comunale e provinciale sono pubblici, ad eccezione di quelli riservati per espressa indicazione di legge o per effetto di una temporanea e motivata dichiarazione del sin

**[4]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212 Art. 6 Conoscenza degli atti e semplificazione 1. L'amministrazione finanziaria deve assicurare l'effettiva conoscenza da parte del contribuente degli atti a lui destinati. A tal fine essa provvede comunque a comunicarli nel luogo di effettivo domicilio del contribuente,

**[5]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212  in materia tributaria. L'amministrazione finanziaria assicura che il contribuente possa ottemperare agli obblighi tributari con il minor numero di adempimenti e nelle forme meno costose e più agevoli. 3-ter. Le amministrazioni interessate provvedono alle attività relati

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art87`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 L'amministrazione finanziaria può stabilire il domicilio fiscale del soggetto, in deroga alle disposizioni dell'articolo precedente, nel comune dove il soggetto stesso svolge in modo continuativo la principale attività ovvero, per i s

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art215`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Amministrazione. 14. Ai fini dei suddetti procedimenti la società scissa o quella designata debbono indicare, a richiesta degli organi dell'Amministrazione finanziaria, i soggetti e i luoghi presso i quali sono conservate, qualora non

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art111`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 65 ((Obblighi dell'amministrazione finanziaria L'amministrazione finanziaria provvede allo scambio, con le altre autorità competenti degli Stati membri della Comunità economica europea, delle informazioni necessarie per assicurare

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 36-ter (Controllo formale delle dichiarazioni) 1. Gli uffici periferici dell'amministrazione finanziaria, procedono, entro il 31 dicembre del secondo anno successivo a quello di presentazione, al controllo formale delle dichiaraz

**[10]** `urn:nir:stato:decreto.legislativo:2007-11-21;231~art21`

> DECRETO LEGISLATIVO 21 novembre 2007, n. 231 imento volto a rilevare la ricorrenza delle cause di esclusione dell'accesso e a valutare la sussistenza dell'interesse all'accesso in capo ai soggetti di cui ((al comma 2, lettera f), e)) al comma 4, lettera d-bis), nonchè i mezzi di tutela dei medesimi

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
