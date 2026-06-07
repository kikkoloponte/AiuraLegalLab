# trib_018 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:41 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 10.7s (ret 0.6s + llm 9.6s) |

## Query

> Qual è la disciplina dell'abuso del diritto in materia tributaria?

## Risposta

**QUALIFICAZIONE**
L'abuso del diritto in materia tributaria riguarda l'uso non legittimo dei poteri o delle procedure amministrative per ottenere vantaggi illegittimi.

**NORMA APPLICABILE**
La norma applicabile è Art. 4 della LEGGE 27 luglio 2000, n. 212.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'abuso del diritto in materia tributaria.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma non ci sono giurisprudenze che la interpretino ulteriormente. La solidità della norma è alta.

**GAP ANALYSIS**
C'è un gap in quanto mancano giurisprudenze che possano fornire una maggiore interpretazione o chiarimento sulla disciplina dell'abuso del diritto in materia tributaria.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'abuso del diritto in materia tributaria riguarda l'uso non legittimo dei poteri o delle procedure amministrative per ottenere vantaggi illegittimi.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art4', 'claim': "Non si può disporre con decreto-legge l'istituzione di nuovi tributi nè prevedere l'applicazione di tributi esistenti ad altre categorie di soggetti.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### NORMA APPLICABILE

La norma applicabile è Art. 4 della LEGGE 27 luglio 2000, n. 212.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art4', 'claim': "Non si può disporre con decreto-legge l'istituzione di nuovi tributi nè prevedere l'applicazione di tributi esistenti ad altre categorie di soggetti.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'abuso del diritto in materia tributaria.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, ma non ci sono giurisprudenze che la interpretino ulteriormente. La solidità della norma è alta.

### GAP ANALYSIS

C'è un gap in quanto mancano giurisprudenze che possano fornire una maggiore interpretazione o chiarimento sulla disciplina dell'abuso del diritto in materia tributaria.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3198` | 2.9744 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge:1990-08-07;241~art22` | 1.3518 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art4` | 0.7055 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art727` | 0.0004 | hybrid_rrf |  |
| 5 | `urn:nir:stato:legge:2000-07-27;212~art5` | -0.6560 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2264` | -1.1018 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art43` | -1.9264 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -2.0053 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge:1970-05-20;300~art18` | -2.5638 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art36` | -3.9142 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art10bis`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3198`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2968. (Diritti indisponibili). Le parti non possono modificare la disciplina legale della decadenza né possono rinunziare alla decadenza medesima, se questa è stabilita dalla legge in materia sottratta alla disponibilità delle parti.

**[2]** `urn:nir:stato:legge:1990-08-07;241~art22`

> LEGGE 7 agosto 1990, n. 241 Art. 22 (Definizioni e principi in materia di accesso). 1. Ai fini del presente capo si intende: a) per "diritto di accesso", il diritto degli interessati di prendere visione e di estrarre copia di documenti amministrativi; b) per "interessati", tutti i soggetti privati,

**[3]** `urn:nir:stato:legge:2000-07-27;212~art4`

> LEGGE 27 luglio 2000, n. 212 Art. 4 Utilizzo del decreto-legge in materia tributaria 1. Non si può disporre con decreto-legge l'istituzione di nuovi tributi nè prevedere l'applicazione di tributi esistenti ad altre categorie di soggetti.

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art727`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 571. (Abuso dei mezzi di correzione o di disciplina) Chiunque abusa dei mezzi di correzione o di disciplina in danno di una persona sottoposta alla sua autorità, o a lui affidata per ragione di educazione, istruzione, cura, vigilanza o custodia, ovvero per

**[5]** `urn:nir:stato:legge:2000-07-27;212~art5`

> LEGGE 27 luglio 2000, n. 212 Art. 5 Informazione del contribuente 1. L'amministrazione finanziaria deve assumere idonee iniziative volte a consentire la completa e agevole conoscenza delle disposizioni legislative e amministrative vigenti in materia tributaria, anche curando la predisposizione di te

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2264`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2223. (Prestazione della materia). Le disposizioni di questo capo si osservano anche se la materia è fornita dal prestatore d'opera, purché le parti non abbiano avuto prevalentemente in considerazione la materia, nel qual caso si applicano le norme sulla vend

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art43`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 10. (Abuso dell'immagine altrui). Qualora l'immagine di una persona o dei genitori, del coniuge o dei figli sia stata esposta o pubblicata fuori dei casi in cui l'esposizione o la pubblicazione è dalla legge consentita, ovvero con pregiudizio al decoro o alla

**[8]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[9]** `urn:nir:stato:legge:1970-05-20;300~art18`

> LEGGE 20 maggio 1970, n. 300  del lavoratore, accerti che vi è anche un difetto di giustificazione del licenziamento, nel qual caso applica, in luogo di quelle previste dal presente comma, le tutele di cui ai commi quarto, quinto o settimo. Il giudice applica la medesima disciplina di cui al quarto

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art36`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 31. (Condanna per delitti commessi con abuso di un pubblico ufficio o di una professione o di un'arte. Interdizione) Ogni condanna per delitti commessi con l'abuso dei poteri, o con la violazione dei doveri inerenti a una pubblica funzione, o ad un pubblic

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
