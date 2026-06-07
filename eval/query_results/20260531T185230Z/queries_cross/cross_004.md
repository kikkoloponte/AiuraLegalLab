# cross_004 — penale+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:41 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.8s (ret 0.1s + llm 65.5s) |

## Query

> Come si configura il reato di dichiarazione fraudolenta mediante uso di fatture false?

## Risposta

**QUALIFICAZIONE**
La domanda riguarda la configurazione del reato di dichiarazione fraudolenta mediante uso di fatture false, che tipicamente rientra nella disciplina dei reati tributari/fiscali. Nel Research Packet fornito non è presente alcuna fonte normativa che definisca specificamente questo tipo di reato.

**NORMA APPLICABILE**
VALUTAZIONE PERSONALE: Il DPR 633/1972 (source_id [4], [5]) riguarda l'IVA e il potere dell'ufficio di procedere all'accertamento o alla rettifica della dichiarazione, ma non definisce esplicitamente la fattispecie delittuale della dichiarazione fraudolenta con fatture false. L'art. 369 CP (source_id [2]) riguarda l'autocalunnia, mentre l'art. 106 CP (source_id [3]) tratta gli effetti dell'estinzione del reato sulla recidiva.

**GIURISPRUDENZA**
VALUTAZIONE PERSONALE: Nel Research Packet non sono presenti fonti giurisprudenziali che affrontino specificamente la configurazione del reato di dichiarazione fraudolenta mediante uso di fatture false. Le fonti disponibili (source_id [1]-[10]) coprono temi diversi come querela, autocalunnia, insolvenza fraudolenta, ubriachezza abituale, alterazione di stato civile.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità dell'analisi è BASSA perché il Research Packet non contiene fonti normative che definiscono esplicitamente la fattispecie delittuale della dichiarazione fraudolenta mediante uso di fatture false. Le fonti disponibili (DPR 633/1972, RD 1398/1930) trattano aspetti procedurali IVA o reati diversi senza specificare la configurazione penale richiesta.

**GAP ANALYSIS**
VALUTAZIONE PERSONALE: Manca nel Packet qualsiasi fonte che definisca il reato di dichiarazione fraudolenta mediante uso di fatture false (tipicamente art. 81-bis D.Lgs. 74/2000 o disposizioni analoghe nel codice tributario). Mancano anche fonti giurisprudenziali che chiariscano gli elementi costitutivi del reato e le conseguenze penali specifiche.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La domanda riguarda la configurazione del reato di dichiarazione fraudolenta mediante uso di fatture false, che tipicamente rientra nella disciplina dei reati tributari/fiscali. Nel Research Packet fornito non è presente alcuna fonte normativa che definisca specificamente questo tipo di reato.

### NORMA APPLICABILE

VALUTAZIONE PERSONALE: Il DPR 633/1972 (source_id [4], [5]) riguarda l'IVA e il potere dell'ufficio di procedere all'accertamento o alla rettifica della dichiarazione, ma non definisce esplicitamente la fattispecie delittuale della dichiarazione fraudolenta con fatture false. L'art. 369 CP (source_id [2]) riguarda l'autocalunnia, mentre l'art. 106 CP (source_id [3]) tratta gli effetti dell'estinzione del reato sulla recidiva.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art55', 'claim': "Il DPR 633/1972 disciplina l'accertamento dell'imposta IVA indipendentemente dalla previa ispezione", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art54', 'claim': "L'ufficio IVA procede alla rettifica della dichiarazione annuale quando ritiene che ne risulti un'imposta inferiore a quella dovuta", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

VALUTAZIONE PERSONALE: Nel Research Packet non sono presenti fonti giurisprudenziali che affrontino specificamente la configurazione del reato di dichiarazione fraudolenta mediante uso di fatture false. Le fonti disponibili (source_id [1]-[10]) coprono temi diversi come querela, autocalunnia, insolvenza fraudolenta, ubriachezza abituale, alterazione di stato civile.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità dell'analisi è BASSA perché il Research Packet non contiene fonti normative che definiscono esplicitamente la fattispecie delittuale della dichiarazione fraudolenta mediante uso di fatture false. Le fonti disponibili (DPR 633/1972, RD 1398/1930) trattano aspetti procedurali IVA o reati diversi senza specificare la configurazione penale richiesta.

### GAP ANALYSIS

VALUTAZIONE PERSONALE: Manca nel Packet qualsiasi fonte che definisca il reato di dichiarazione fraudolenta mediante uso di fatture false (tipicamente art. 81-bis D.Lgs. 74/2000 o disposizioni analoghe nel codice tributario). Mancano anche fonti giurisprudenziali che chiariscano gli elementi costitutivi del reato e le conseguenze penali specifiche.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art403` | 4.3793 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art441` | 1.3458 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art121` | -0.4168 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art100` | -1.3090 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art94` | -2.1903 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art882` | -2.8285 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art265` | -2.9361 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art124` | -3.5360 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art109` | -4.0615 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art721` | -4.1486 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art2`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art403`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 336 Querela 1. La querela è proposta mediante dichiarazione nella quale, personalmente o a mezzo di procuratore speciale, si manifesta la volontà che si proceda in ordine a un fatto previsto dalla legge come reato.

**[2]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art441`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 369. (Autocalunnia) Chiunque, mediante dichiarazione ad alcuna delle Autorità indicate nell'articolo precedente, anche se fatta con scritto anonimo o sotto falso nome, ovvero mediante confessione innanzi all'Autorità giudiziaria, incolpa sé stesso di un re

**[3]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art121`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 106. (Effetti dell'estinzione del reato o della pena) Agli effetti della recidiva e della dichiarazione di abitualità o di professionalità nel reato, si tien conto altresì delle condanne per le quali è intervenuta una causa di estinzione del reato o della

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art100`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Se il contribuente non ha presentato la dichiarazione annuale l'ufficio dell'imposta sul valore aggiunto può procedere in ogni caso all'accertamento dell'imposta dovuta indipendentemente dalla previa ispezione della contabilità. In tal

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art94`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 L'ufficio dell'imposta sul valore aggiunto procede alla rettifica della dichiarazione annuale presentata dal contribuente quando ritiene che ne risulti un'imposta inferiore a quella dovuta ovvero una eccedenza detraibile o rimborsabile

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art882`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 641. (Insolvenza fraudolenta) Chiunque, dissimulando il proprio stato d'insolvenza, contrae un'obbligazione col proposito di non adempierla è punito, a querela della persona offesa, qualora la obbligazione non sia adempiuta, con la reclusione fino a due an

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art265`

> REGIO DECRETO 19 ottobre 1930, n. 1398  del codice di procedura penale . La disposizione del numero 2° non si applica se la cosa appartiene a persona estranea al reato e la fabbricazione, l'uso, il porto, la detenzione o l'alienazione possono essere consentiti mediante autorizzazione amministrativa.

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art124`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 109. (Effetti della dichiarazione di abitualità, professionalità o tendenza a delinquere) Oltre gli aumenti di pena stabiliti per la recidiva e i particolari effetti indicati da altre disposizioni di legge, la dichiarazione di abitualità o di professionali

**[9]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art109`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 94. (Ubriachezza abituale) Quando il reato è commesso in stato di ubriachezza, e questa è abituale, la pena è aumentata. Agli effetti della legge penale, è considerato ubriaco abituale chi è dedito all'uso di bevande alcooliche e in stato frequente di ubri

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art721`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 567. (Alterazione di stato) Chiunque, mediante la sostituzione di un neonato, ne altera lo stato civile è punito con la reclusione da tre a dieci anni. Si applica la reclusione da cinque a quindici anni a chiunque, nella formazione di un atto di nascita, a

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
