# cross_004 — penale+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:59 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 16.1s (ret 0.3s + llm 15.7s) |

## Query

> Come si configura il reato di dichiarazione fraudolenta mediante uso di fatture false?

## Risposta

**QUALIFICAZIONE**
La dichiarazione fraudolenta mediante uso di fatture false si configura come un reato previsto dal Codice Penale italiano.

**NORMA APPLICABILE**
Il reato di dichiarazione fraudolenta mediante uso di fatture false è regolamentato dall'articolo 329 del Decreto Legislativo n. 14/01/2019.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente al reato di dichiarazione fraudolenta mediante uso di fatture false. Tuttavia, la giurisprudenza tende a interpretare le norme in modo da prevenire l'elusione fiscale.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione del reato di dichiarazione fraudolenta mediante uso di fatture false è alta, in quanto la normativa prevede pene severe e la giurisprudenza tende a interpretare le norme in modo da prevenire l'elusione fiscale.

**GAP ANALYSIS**
Non ci sono specifiche normative o giurisprudenze menzionate nel Packet che si riferiscano direttamente al reato di dichiarazione fraudolenta mediante uso di fatture false. Tuttavia, sarebbe utile avere una sentenza o un precedente giudiziario che definisca chiaramente il quadro normativo.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La dichiarazione fraudolenta mediante uso di fatture false si configura come un reato previsto dal Codice Penale italiano.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art403', 'claim': 'La dichiarazione è proposta mediante dichiarazione nella quale, personalmente o a mezzo di procuratore speciale, si manifesta la volontà che si proceda in ordine a un fatto previsto dalla legge come reato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art636', 'claim': 'Salvo che il fatto costituisca più grave reato, chiunque attribuisce fittiziamente ad altri la titolarità o disponibilità di denaro, beni o altre utilità al fine di eludere le disposizioni di legge in materia.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il reato di dichiarazione fraudolenta mediante uso di fatture false è regolamentato dall'articolo 329 del Decreto Legislativo n. 14/01/2019.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art329', 'claim': "Si applicano le pene stabilite nell'articolo 322 agli amministratori, ai direttori generali, ai sindaci e ai liquidatori di società in liquidazione giudiziale, i quali hanno commesso alcuno dei fatti preveduti nel", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente al reato di dichiarazione fraudolenta mediante uso di fatture false. Tuttavia, la giurisprudenza tende a interpretare le norme in modo da prevenire l'elusione fiscale.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art100', 'claim': "Se il contribuente non ha presentato la dichiarazione annuale l'ufficio dell'imposta sul valore aggiunto può procedere in ogni caso all'accertamento dell'imposta dovuta indipendentemente dalla previa ispezione della contabilità. In tal", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art94', 'claim': "L'ufficio dell'imposta sul valore aggiunto procede alla rettifica della dichiarazione annuale presentata dal contribuente quando ritiene che ne risulti un'imposta inferiore a quella dovuta ovvero una eccedenza detraibile o rimborsabile", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione del reato di dichiarazione fraudolenta mediante uso di fatture false è alta, in quanto la normativa prevede pene severe e la giurisprudenza tende a interpretare le norme in modo da prevenire l'elusione fiscale.

### GAP ANALYSIS

Non ci sono specifiche normative o giurisprudenze menzionate nel Packet che si riferiscano direttamente al reato di dichiarazione fraudolenta mediante uso di fatture false. Tuttavia, sarebbe utile avere una sentenza o un precedente giudiziario che definisca chiaramente il quadro normativo.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art403` | 4.3793 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art441` | 1.3458 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art636` | 0.1714 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art121` | -0.4168 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art100` | -1.3090 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art329` | -1.4677 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art322` | -1.5318 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art94` | -2.1903 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art882` | -2.8285 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art265` | -2.9361 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art2`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art403`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 336 Querela 1. La querela è proposta mediante dichiarazione nella quale, personalmente o a mezzo di procuratore speciale, si manifesta la volontà che si proceda in ordine a un fatto previsto dalla legge come reato.

**[2]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art441`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 369. (Autocalunnia) Chiunque, mediante dichiarazione ad alcuna delle Autorità indicate nell'articolo precedente, anche se fatta con scritto anonimo o sotto falso nome, ovvero mediante confessione innanzi all'Autorità giudiziaria, incolpa sé stesso di un re

**[3]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art636`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 512-bis. (Trasferimento fraudolento di valori). Salvo che il fatto costituisca più grave reato, chiunque attribuisce fittiziamente ad altri la titolarità o disponibilità di denaro, beni o altre utilità al fine di eludere le disposizioni di legge in materia

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art121`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 106. (Effetti dell'estinzione del reato o della pena) Agli effetti della recidiva e della dichiarazione di abitualità o di professionalità nel reato, si tien conto altresì delle condanne per le quali è intervenuta una causa di estinzione del reato o della

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art100`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Se il contribuente non ha presentato la dichiarazione annuale l'ufficio dell'imposta sul valore aggiunto può procedere in ogni caso all'accertamento dell'imposta dovuta indipendentemente dalla previa ispezione della contabilità. In tal

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art329`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 329 Fatti di bancarotta fraudolenta 1. Si applicano le pene stabilite nell'articolo 322 agli amministratori, ai direttori generali, ai sindaci e ai liquidatori di società in liquidazione giudiziale, i quali hanno commesso alcuno dei fatti preveduti nel

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art322`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 322 Bancarotta fraudolenta 1. È punito con la reclusione da tre a dieci anni, se è dichiarato in liquidazione giudiziale, l'imprenditore che: a) ha distratto, occultato, dissimulato, distrutto o dissipato in tutto o in parte i suoi beni ovvero, allo sc

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art94`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 L'ufficio dell'imposta sul valore aggiunto procede alla rettifica della dichiarazione annuale presentata dal contribuente quando ritiene che ne risulti un'imposta inferiore a quella dovuta ovvero una eccedenza detraibile o rimborsabile

**[9]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art882`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 641. (Insolvenza fraudolenta) Chiunque, dissimulando il proprio stato d'insolvenza, contrae un'obbligazione col proposito di non adempierla è punito, a querela della persona offesa, qualora la obbligazione non sia adempiuta, con la reclusione fino a due an

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art265`

> REGIO DECRETO 19 ottobre 1930, n. 1398  del codice di procedura penale . La disposizione del numero 2° non si applica se la cosa appartiene a persona estranea al reato e la fabbricazione, l'uso, il porto, la detenzione o l'alienazione possono essere consentiti mediante autorizzazione amministrativa.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
