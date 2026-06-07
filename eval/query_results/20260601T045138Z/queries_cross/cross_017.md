# cross_017 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:09 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 42.4s (ret 0.3s + llm 41.8s) |

## Query

> Come si coordina l'azione revocatoria ordinaria con il reato di sottrazione fraudolenta al pagamento di imposte?

## Risposta

**QUALIFICAZIONE**
L'azione revocatoria ordinaria è un procedimento penale che permette al curatore di dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile (Art. 165 DLGS 2019-01-12;14). Il reato di sottrazione fraudolenta al pagamento delle imposte è previsto nel Codice Penale (Art. 116 DPR 1930-10-19;1398).

**NORMA APPLICABILE**
L'azione revocatoria ordinaria è regolata dall'Art. 165 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14, mentre il reato di sottrazione fraudolenta al pagamento delle imposte è previsto dall'Art. 116 del REGIO DECRETO 19 ottobre 1930, n. 1398.

**GIURISPRUDENZA**
Non esistono giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte. Tuttavia, le norme penali generali suggeriscono una distinzione tra i due fenomeni.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della valutazione è MEDIA. Le norme specifiche non sono chiare sulla coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'azione revocatoria ordinaria è un procedimento penale che permette al curatore di dichiarare inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori, secondo le norme del codice civile (Art. 165 DLGS 2019-01-12;14). Il reato di sottrazione fraudolenta al pagamento delle imposte è previsto nel Codice Penale (Art. 116 DPR 1930-10-19;1398).

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art165', 'claim': "L'azione revocatoria ordinaria è prevista dal DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 165.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art116', 'claim': "Il reato di sottrazione fraudolenta al pagamento delle imposte è previsto dall'Art. 116 del REGIO DECRETO 19 ottobre 1930, n. 1398.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

L'azione revocatoria ordinaria è regolata dall'Art. 165 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14, mentre il reato di sottrazione fraudolenta al pagamento delle imposte è previsto dall'Art. 116 del REGIO DECRETO 19 ottobre 1930, n. 1398.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art165', 'claim': "L'azione revocatoria ordinaria è regolata dall'Art. 165 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art116', 'claim': "Il reato di sottrazione fraudolenta al pagamento delle imposte è previsto dall'Art. 116 del REGIO DECRETO 19 ottobre 1930, n. 1398.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non esistono giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte. Tuttavia, le norme penali generali suggeriscono una distinzione tra i due fenomeni.

*Citazioni: {'source_id': '', 'claim': "Non esistono giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte.", 'claim_type': 'FACT', 'source_authority': 'GIURISPRUDENZA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della valutazione è MEDIA. Le norme specifiche non sono chiare sulla coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte.

### GAP ANALYSIS

Il Packet manca di giurisprudenze specifiche che trattino la coordinazione tra l'azione revocatoria ordinaria e il reato di sottrazione fraudolenta al pagamento delle imposte.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art165` | 4.2469 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3132` | 1.4604 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art166` | 1.0313 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3133` | -1.7779 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art131` | -2.7919 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art10` | -2.9124 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art53` | -5.7025 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3131` | -6.1803 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art96` | -6.1932 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2462` | -6.5709 | hybrid_rrf | ✅ |

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

**[5]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art131`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 116. (Reato diverso da quello voluto da taluno dei concorrenti) Qualora il reato commesso sia diverso da quello voluto da taluno dei concorrenti, anche questi ne risponde, se l'evento è conseguenza della sua azione od omissione. Se il reato commesso è più

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art10`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 6. (Reati commessi nel territorio dello Stato) Chiunque commette un reato nel territorio dello Stato è punito secondo la legge italiana. Il reato si considera commesso nel territorio dello Stato, quando l'azione o l'omissione, che lo costituisce, è ivi avv

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art53`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 43. (Elemento psicologico del reato) Il delitto: è doloso, o secondo l'intenzione, quando l'evento dannoso o pericoloso, che è il risultato dell'azione od omissione e da cui la legge fa dipendere l'esistenza del delitto, è dall'agente preveduto e voluto co

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3131`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2902. (Effetti). Il creditore, ottenuta la dichiarazione di inefficacia, può promuovere nei confronti dei terzi acquirenti le azioni esecutive o conservative sui beni che formano oggetto dell'atto impugnato. Il terzo contraente, che abbia verso il debitore ra

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art96`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 54-bis.1 (( (Liquidazione IVA nel caso di dichiarazioni omesse) )) 1. ((Senza pregiudizio dell'azione accertatrice, l'Agenzia delle entrate, entro il termine di cui all'articolo 57, comma 2, può procedere, in caso di omessa present

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2462`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2394. (( (Responsabilità verso i creditori sociali).)) ((Gli amministratori rispondono verso i creditori sociali per l'inosservanza degli obblighi inerenti alla conservazione dell'integrità del patrimonio sociale. L'azione può essere proposta dai creditori qu

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
