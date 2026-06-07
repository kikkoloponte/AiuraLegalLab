# trib_002 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:38 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 5.9s (ret 0.6s + llm 4.8s) |

## Query

> Qual è il termine di decadenza per la notifica degli avvisi di accertamento ai fini IRPEF?

## Risposta

**QUALIFICAZIONE**
Il termine di decadenza per la notifica degli avvisi di accertamento ai fini IRPEF è stabilito dal decreto del Presidente della Repubblica 29 settembre 1973, n. 600.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica sul termine di decadenza, rendendo la valutazione alta.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il termine di decadenza per la notifica degli avvisi di accertamento ai fini IRPEF è stabilito dal decreto del Presidente della Repubblica 29 settembre 1973, n. 600.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71', 'claim': 'Gli avvisi di accertamento devono essere notificati, a pena di decadenza, entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica sul termine di decadenza, rendendo la valutazione alta.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71` | 6.8361 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 3.8850 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7` | 2.8391 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3196` | 2.7253 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11` | 1.8363 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71` | 1.6629 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art18` | 0.7943 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | -1.7810 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art53` | -5.4082 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -7.2485 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 43 (Termine per l'accertamento) 1. Gli avvisi di accertamento devono essere notificati, a pena di decadenza, entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione. (140)(151) (152) 2.

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

**[3]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  alla notifica dell'avviso di accertamento o di rettifica, ovvero dell'atto di recupero, che sia stato preceduto dal contraddittorio preventivo ai sensi dell' articolo 6-bis, comma 3, della legge 27 luglio 2000, n. 212 , l'ufficio, ai fini dell'accertamento

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3196`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2966. (Cause che impediscono la decadenza). La decadenza non è impedita se non dal compimento dell'atto previsto dalla legge o dal contratto. Tuttavia, se si tratta di un termine stabilito dal contratto o da una norma di legge relativa a diritti disponibili,

**[5]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 11 Avvio del procedimento 1. ((L'ufficio di iniziativa, nei casi di cui all' articolo 6-bis, comma 2, della legge n. 212 del 2000 , contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero, ovvero su istanza

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  di decadenza per l'accertamento di cui all' articolo 43 del decreto del Presidente della Repubblica 29 settembre 1973, n. 600 , e all' articolo 57 del decreto del Presidente della Repubblica 26 ottobre 1972, n. 633 , nonché i termini

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art18`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 14. (Computo e decorrenza dei termini) Quando la legge penale fa dipendere un effetto giuridico dal decorso del tempo, per il computo di questo si osserva il calendario comune. Ogni qual volta la legge penale stabilisce un termine per il verificarsi di un

**[8]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  qualora ne ricorrano i presupposti, successivamente alla scadenza del termine di sospensione. L'impugnazione dell'atto comporta rinuncia all'istanza. (23) 4. Entro quindici giorni dalla ricezione dell'istanza di cui ai commi 2 e 2-bis, l'ufficio, anche tel

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art53`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 'imposta, rilevanti ai fini dell'accertamento, nei confronti di loro clienti, fornitori e prestatori di lavoro autonomo. 8-bis) invitare ogni altro soggetto ad esibire o trasmettere, anche in copia fotostatica, atti o documenti fiscal

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  tale adesione è determinante ai fini del raggiungimento della maggioranza delle classi prevista dall'articolo 112, comma 2, lettera d), oppure se la stessa maggioranza è raggiunta escludendo dal computo le classi dei creditori di cui al comma 1. In ogni ca

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
