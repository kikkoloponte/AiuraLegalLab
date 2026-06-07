# cross_017 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:56 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 68.1s (ret 0.2s + llm 67.7s) |

## Query

> Come si coordina l'azione revocatoria ordinaria con il reato di sottrazione fraudolenta al pagamento di imposte?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "L'azione revocatoria ordinaria è disciplinata dall'Art. 165 DLgs 14/2019, che consente al curatore di domandare la dichiarazione di inefficacia degli atti compiuti dal debitore in pregiudizio dei creditori secondo le norme del codice civile. Il reato di sottrazione fraudolenta al pagamento di imposte rientra nella sfera penale (Codice Penale), ma il packet non contiene fonti specifiche su questo reato particolare.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2019-01-12;14~art165",
          "claim": "Il curatore può domandare che siano dichiarati inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori secondo le norme del codice civile.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art6",
          "claim": "Chiunque commette un reato nel territorio dello Stato è punito secondo la legge italiana.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "L'Art. 2903 RD 262/1942 stabilisce che l'azione revocatoria si prescrive in cinque anni dalla data dell'atto (source_id: urn:nir:stato:regio.decreto:1942-03-16;262~art3132). L'Art. 2904 RD 262/1942 rinvia alle disposizioni sull'azione revocatoria in materia fallimentare e penale (source_id: urn:nir:stato:regio.decreto:1942-03-16;262~art3133). L'Art. 1449 RD 262/1942 prevede che se il fatto costituisce reato, si applica l'ultimo comma dell'art. 2947 per la prescrizione (source_id: urn:nir:stato:regio.decreto:1942-03-16;262~art1494).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3132",
          "claim": "L'azione revocatoria si prescrive in cinque anni dalla data dell'atto.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3133",
          "claim": "Sono salve le disposizioni sull'azione revocatoria in materia fallimentare e in materia penale.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1494",
          "claim": "Se il fatto costituisce reato, si applica l'ultimo comma dell'art. 2947 per la prescrizione.",

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "L'azione revocatoria ordinaria è disciplinata dall'Art. 165 DLgs 14/2019, che consente al curatore di domandare la dichiarazione di inefficacia degli atti compiuti dal debitore in pregiudizio dei creditori secondo le norme del codice civile. Il reato di sottrazione fraudolenta al pagamento di imposte rientra nella sfera penale (Codice Penale), ma il packet non contiene fonti specifiche su questo reato particolare.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2019-01-12;14~art165",
          "claim": "Il curatore può domandare che siano dichiarati inefficaci gli atti compiuti dal debitore in pregiudizio dei creditori secondo le norme del codice civile.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art6",
          "claim": "Chiunque commette un reato nel territorio dello Stato è punito secondo la legge italiana.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "L'Art. 2903 RD 262/1942 stabilisce che l'azione revocatoria si prescrive in cinque anni dalla data dell'atto (source_id: urn:nir:stato:regio.decreto:1942-03-16;262~art3132). L'Art. 2904 RD 262/1942 rinvia alle disposizioni sull'azione revocatoria in materia fallimentare e penale (source_id: urn:nir:stato:regio.decreto:1942-03-16;262~art3133). L'Art. 1449 RD 262/1942 prevede che se il fatto costituisce reato, si applica l'ultimo comma dell'art. 2947 per la prescrizione (source_id: urn:nir:stato:regio.decreto:1942-03-16;262~art1494).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3132",
          "claim": "L'azione revocatoria si prescrive in cinque anni dalla data dell'atto.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3133",
          "claim": "Sono salve le disposizioni sull'azione revocatoria in materia fallimentare e in materia penale.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1494",
          "claim": "Se il fatto costituisce reato, si applica l'ultimo comma dell'art. 2947 per la prescrizione.",

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art165` | 4.2469 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3132` | 1.4604 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art166` | 1.0313 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1494` | -0.0529 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3133` | -1.7779 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art131` | -2.7919 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art10` | -2.9124 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art53` | -5.7025 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3131` | -6.1803 | hybrid_rrf | ✅ |
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

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1494`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1449. (Prescrizione). L'azione di rescissione si prescrive in un anno dalla conclusione del contratto; ma se il fatto costituisce reato, si applica l'ultimo comma dell'art. 2947. La rescindibilità del contratto non può essere opposta in via di eccezione quand

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3133`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2904. (Rinvio). Sono salve le disposizioni sull'azione revocatoria in materia fallimentare e in materia penale.

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art131`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 116. (Reato diverso da quello voluto da taluno dei concorrenti) Qualora il reato commesso sia diverso da quello voluto da taluno dei concorrenti, anche questi ne risponde, se l'evento è conseguenza della sua azione od omissione. Se il reato commesso è più

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art10`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 6. (Reati commessi nel territorio dello Stato) Chiunque commette un reato nel territorio dello Stato è punito secondo la legge italiana. Il reato si considera commesso nel territorio dello Stato, quando l'azione o l'omissione, che lo costituisce, è ivi avv

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art53`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 43. (Elemento psicologico del reato) Il delitto: è doloso, o secondo l'intenzione, quando l'evento dannoso o pericoloso, che è il risultato dell'azione od omissione e da cui la legge fa dipendere l'esistenza del delitto, è dall'agente preveduto e voluto co

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3131`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2902. (Effetti). Il creditore, ottenuta la dichiarazione di inefficacia, può promuovere nei confronti dei terzi acquirenti le azioni esecutive o conservative sui beni che formano oggetto dell'atto impugnato. Il terzo contraente, che abbia verso il debitore ra

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2462`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2394. (( (Responsabilità verso i creditori sociali).)) ((Gli amministratori rispondono verso i creditori sociali per l'inosservanza degli obblighi inerenti alla conservazione dell'integrità del patrimonio sociale. L'azione può essere proposta dai creditori qu

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
