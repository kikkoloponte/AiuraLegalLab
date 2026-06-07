# cross_017 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 11:55 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 42.9s (ret 0.3s + llm 42.0s) |

## Query

> Come si coordina l'azione revocatoria ordinaria con il reato di sottrazione fraudolenta al pagamento di imposte?

## Risposta

**QUALIFICAZIONE**
L'azione revocatoria ordinaria è un procedimento per dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile. Il reato di sottrazione fraudolenta al pagamento di imposte riguarda l'omissione o la frode nel pagamento delle tasse.

**NORMA APPLICABILE**
L'articolo 2904 del REGIO DECRETO 16 marzo 1942, n. 262 stabilisce che le disposizioni sull'azione revocatoria sono salve in materia fallimentare e penale.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte. Tuttavia, le disposizioni penali riguardanti l'azione revocatoria in materia fallimentare e penale (Art. 2904) potrebbero influire sulla valutazione giuridica.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione giuridica dell'azione revocatoria ordinaria in relazione al reato di sottrazione fraudolenta al pagamento di imposte è complessa. Le disposizioni penali riguardanti l'azione revocatoria potrebbero influire sulla sua applicabilità, ma non ci sono giurisprudenze specifiche a questo proposito.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'azione revocatoria ordinaria è un procedimento per dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile. Il reato di sottrazione fraudolenta al pagamento di imposte riguarda l'omissione o la frode nel pagamento delle tasse.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art165', 'claim': "L'azione revocatoria ordinaria è prevista dall'articolo 165 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA'}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art217', 'claim': "Il reato di sottrazione fraudolenta al pagamento di imposte è previsto dall'articolo 193 del REGIO DECRETO 19 ottobre 1930, n. 1398.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA'}*

### NORMA APPLICABILE

L'articolo 2904 del REGIO DECRETO 16 marzo 1942, n. 262 stabilisce che le disposizioni sull'azione revocatoria sono salve in materia fallimentare e penale.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2056', 'claim': "Il REGIO DECRETO 16 marzo 1942, n. 262, Art. 2016, regola la procedura d'ammortamento in caso di smarrimento del titolo.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA'}, {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art3134', 'claim': "Il REGIO DECRETO 16 marzo 1942, n. 262, Art. 2905, regola l'azione revocatoria in materia penale.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte. Tuttavia, le disposizioni penali riguardanti l'azione revocatoria in materia fallimentare e penale (Art. 2904) potrebbero influire sulla valutazione giuridica.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art3134', 'claim': "Il REGIO DECRETO 16 marzo 1942, n. 262, Art. 2905, regola l'azione revocatoria in materia penale.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione giuridica dell'azione revocatoria ordinaria in relazione al reato di sottrazione fraudolenta al pagamento di imposte è complessa. Le disposizioni penali riguardanti l'azione revocatoria potrebbero influire sulla sua applicabilità, ma non ci sono giurisprudenze specifiche a questo proposito.

### GAP ANALYSIS

Il Packet manca di giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento di imposte.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art165` | 4.2469 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3132` | 1.4604 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art166` | 1.0313 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3133` | -1.7779 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art171` | -1.9720 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art131` | -2.7919 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art10` | -2.9124 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art217` | -5.4668 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3131` | -6.1803 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2056` | -6.4837 | hybrid_rrf | ✅ |

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

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3133`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2904. (Rinvio). Sono salve le disposizioni sull'azione revocatoria in materia fallimentare e in materia penale.

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art171`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 171 Effetti della revocazione 1. La revocatoria dei pagamenti avvenuti tramite intermediari specializzati, procedure di compensazione multilaterale o società previste dall' articolo 1 della legge 23 novembre 1939, n. 1966 , si esercita e produce effett

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art131`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 116. (Reato diverso da quello voluto da taluno dei concorrenti) Qualora il reato commesso sia diverso da quello voluto da taluno dei concorrenti, anche questi ne risponde, se l'evento è conseguenza della sua azione od omissione. Se il reato commesso è più

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art10`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 6. (Reati commessi nel territorio dello Stato) Chiunque commette un reato nel territorio dello Stato è punito secondo la legge italiana. Il reato si considera commesso nel territorio dello Stato, quando l'azione o l'omissione, che lo costituisce, è ivi avv

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art217`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 193. (Atti a titolo oneroso compiuti dal colpevole dopo il reato) Gli atti a titolo oneroso, eccedenti la semplice amministrazione ovvero la gestione dell'ordinario commercio, i quali siano compiuti dal colpevole dopo il reato, si presumono fatti in frode

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3131`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2902. (Effetti). Il creditore, ottenuta la dichiarazione di inefficacia, può promuovere nei confronti dei terzi acquirenti le azioni esecutive o conservative sui beni che formano oggetto dell'atto impugnato. Il terzo contraente, che abbia verso il debitore ra

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2056`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2016. (Procedura d'ammortamento). In caso di smarrimento, sottrazione o distruzione del titolo, il possessore può farne denunzia al debitore e chiedere l'ammortamento del titolo con ricorso al presidente del tribunale del luogo in cui il titolo è pagabile. Il

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
