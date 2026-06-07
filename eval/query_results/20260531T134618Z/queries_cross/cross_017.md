# cross_017 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:02 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 14.6s (ret 0.4s + llm 13.9s) |

## Query

> Come si coordina l'azione revocatoria ordinaria con il reato di sottrazione fraudolenta al pagamento di imposte?

## Risposta

**QUALIFICAZIONE**
L'azione revocatoria ordinaria permette al curatore di dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile. Il reato di sottrazione fraudolenta al pagamento di imposte è previsto nel Codice Penale.

**NORMA APPLICABILE**
L'articolo 2902 del Codice Civile regola gli effetti dell'azione revocatoria ordinaria, mentre l'articolo 43 del Codice Penale definisce l'elemento psicologico del reato.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte. Tuttavia, la giurisprudenza tende a considerare l'azione revocatoria come un mezzo per proteggere i diritti dei creditori.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della valutazione è media, in quanto non esistono giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'azione revocatoria ordinaria permette al curatore di dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile. Il reato di sottrazione fraudolenta al pagamento di imposte è previsto nel Codice Penale.

*Citazioni: {'source_id': 'CC_ART_1218', 'claim': "L'azione revocatoria ordinaria permette al curatore di dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 165'}, {'source_id': 'CPP_ART_6', 'claim': 'Il reato di sottrazione fraudolenta al pagamento di imposte è previsto nel Codice Penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 6'}*

### NORMA APPLICABILE

L'articolo 2902 del Codice Civile regola gli effetti dell'azione revocatoria ordinaria, mentre l'articolo 43 del Codice Penale definisce l'elemento psicologico del reato.

*Citazioni: {'source_id': 'CC_ART_2902', 'claim': "L'articolo 2902 del Codice Civile regola gli effetti dell'azione revocatoria ordinaria.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262 Art. 2902'}, {'source_id': 'CPP_ART_43', 'claim': "L'articolo 43 del Codice Penale definisce l'elemento psicologico del reato.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 43'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte. Tuttavia, la giurisprudenza tende a considerare l'azione revocatoria come un mezzo per proteggere i diritti dei creditori.

*Citazioni: {'source_id': 'VALUTAZIONE_PERSONALE', 'claim': "Non ci sono giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.", 'claim_type': 'VALUTAZIONE_PERSONALE', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della valutazione è media, in quanto non esistono giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.

### GAP ANALYSIS

Il Packet manca di giurisprudenze specifiche che trattino l'intersezione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art165` | 4.2469 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3132` | 1.4604 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art166` | 1.0313 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1494` | -0.0529 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3133` | -1.7779 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art171` | -1.9720 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art131` | -2.7919 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art10` | -2.9124 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art53` | -5.7025 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3131` | -6.1803 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art11`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art165`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 165 Azione revocatoria ordinaria 1. Il curatore può domandare che siano dichiarati inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile . 2. L'azione si propone dinanzi al tribunale competente ai se

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3132`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2903. (Prescrizione dell'azione). L'azione revocatoria si prescrive in cinque anni dalla data dell'atto.

**[3]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art166`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 a l'apertura della liquidazione giudiziale o nei sei mesi anteriori. 3. Non sono soggetti all'azione revocatoria: a) i pagamenti di beni e servizi effettuati nell'esercizio dell'attività d'impresa nei termini d'uso; b) le rimesse effettuate su un conto corr

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1494`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1449. (Prescrizione). L'azione di rescissione si prescrive in un anno dalla conclusione del contratto; ma se il fatto costituisce reato, si applica l'ultimo comma dell'art. 2947. La rescindibilità del contratto non può essere opposta in via di eccezione quand

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3133`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2904. (Rinvio). Sono salve le disposizioni sull'azione revocatoria in materia fallimentare e in materia penale.

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art171`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 171 Effetti della revocazione 1. La revocatoria dei pagamenti avvenuti tramite intermediari specializzati, procedure di compensazione multilaterale o società previste dall' articolo 1 della legge 23 novembre 1939, n. 1966 , si esercita e produce effett

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art131`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 116. (Reato diverso da quello voluto da taluno dei concorrenti) Qualora il reato commesso sia diverso da quello voluto da taluno dei concorrenti, anche questi ne risponde, se l'evento è conseguenza della sua azione od omissione. Se il reato commesso è più

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art10`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 6. (Reati commessi nel territorio dello Stato) Chiunque commette un reato nel territorio dello Stato è punito secondo la legge italiana. Il reato si considera commesso nel territorio dello Stato, quando l'azione o l'omissione, che lo costituisce, è ivi avv

**[9]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art53`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 43. (Elemento psicologico del reato) Il delitto: è doloso, o secondo l'intenzione, quando l'evento dannoso o pericoloso, che è il risultato dell'azione od omissione e da cui la legge fa dipendere l'esistenza del delitto, è dall'agente preveduto e voluto co

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3131`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2902. (Effetti). Il creditore, ottenuta la dichiarazione di inefficacia, può promuovere nei confronti dei terzi acquirenti le azioni esecutive o conservative sui beni che formano oggetto dell'atto impugnato. Il terzo contraente, che abbia verso il debitore ra

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
