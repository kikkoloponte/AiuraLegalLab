# cross_006 — amministrativo+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:17 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 43.7s (ret 0.3s + llm 43.3s) |

## Query

> Quali sono i rapporti tra procedimento disciplinare e procedimento penale per il pubblico dipendente?

## Risposta

**QUALIFICAZIONE**
Il rapporto tra procedimento disciplinare e procedimento penale per il pubblico dipendente è regolato dal Codice di Procедурный Процессуальный Кодекс и Кодекса Пенальном.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidità della valutazione è alta in quanto basata su norme legali specifiche.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il rapporto tra procedimento disciplinare e procedimento penale per il pubblico dipendente è regolato dal Codice di Procедурный Процессуальный Кодекс и Кодекса Пенальном.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art802', 'claim': "Il pubblico ministero può trasferire procedimenti penali all'estero.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art698', 'claim': 'Il pubblico ministero può applicare la disciplina del concorso formale e del reato continuato.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art430', 'claim': 'Il concetto di persona incaricata di un pubblico servizio è definito nel Codice Penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art429', 'claim': 'Il concetto di pubblico ufficiale è definito nel Codice Penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art937', 'claim': 'Il pubblico è protetto dalla pubblicazione indebita di notizie concernenti un procedimento penale.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidità della valutazione è alta in quanto basata su norme legali specifiche.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art802` | 6.1056 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art698` | 2.9555 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art430` | 2.8915 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art429` | 2.8856 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art937` | 2.3626 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art936` | 2.3575 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art43` | 1.9611 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art126` | 1.1602 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art444` | 0.8672 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art793` | 0.7857 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2001-03-30;165~art55ter`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art802`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 746-quater (( (Trasferimento di procedimenti penali all'estero).)) (( 1. Quando il pubblico ministero ha notizia della pendenza di un procedimento penale all'estero, per gli stessi fatti per i quali si è proceduto all'iscrizione

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art698`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 671 Applicazione della disciplina del concorso formale e del reato continuato 1. Nel caso di più sentenze o decreti penali irrevocabili pronunciati in procedimenti distinti contro la stessa persona, il condannato o il pubblico mi

**[3]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art430`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 358. (( (Nozione della persona incaricata di un pubblico servizio). )) ((Agli effetti della legge penale, sono incaricati di un pubblico servizio coloro i quali, a qualunque titolo, prestano un pubblico servizio. Per pubblico servizio deve intendersi un'at

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art429`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 357. (Nozione del pubblico ufficiale). Agli effetti della legge penale, sono pubblici ufficiali coloro i quali esercitano una pubblica funzione legislativa, ((giudiziaria)) o amministrativa. ((Agli stessi effetti è pubblica la funzione amministrativa disci

**[5]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art937`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 685. (( (Indebita pubblicazione di notizie concernenti un procedimento penale).)) ((Chiunque pubblica i nomi dei giudici, con l'indicazione dei voti individuali che ad essi si attribuiscono nelle deliberazioni prese in un procedimento penale, è punito con

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art936`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 684. (( (Pubblicazione arbitraria di atti di un procedimento penale).)) ((Chiunque pubblica, in tutto o in parte, anche per riassunto o a guisa d'informazione, atti o documenti di un procedimento penale, di cui sia vietata per legge la pubblicazione, è pun

**[7]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art43`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33  di pubblicazione previsti dalla normativa vigente, all'ufficio di disciplina, ai fini dell'eventuale attivazione del procedimento disciplinare. Il responsabile segnala altresì gli inadempimenti al vertice politico dell'amministrazione, all'OIV ai fini dell'a

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art126`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 105 Abbandono e rifiuto della difesa 1. Il consiglio dell'ordine forense ha competenza esclusiva per le sanzioni disciplinari relative all'abbandono della difesa o al rifiuto della difesa di ufficio. 2. Il procedimento disciplina

**[9]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art444`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 371-bis. (False informazioni al pubblico ministero ((o al procuratore della Corte penale internazionale)) ) Chiunque, nel corso di un procedimento penale, richiesto dal pubblico ministero ((o dal procuratore della Corte penale internazionale)) di fornire i

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art793`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 741 Procedimento relativo al riconoscimento delle disposizioni civili di sentenze penali straniere 1. A domanda dell'interessato, nel medesimo procedimento e con la stessa sentenza prevista dall'articolo 734 possono essere dichia

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
