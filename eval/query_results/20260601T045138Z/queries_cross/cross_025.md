# cross_025 — penale+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:13 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 26.7s (ret 0.3s + llm 26.1s) |

## Query

> Come si coordina il procedimento penale con la sospensione cautelare del dipendente pubblico?

## Risposta

**QUALIFICAZIONE**
Il procedimento penale può essere sospeso o interrotto nel caso di una sospensione cautelare del dipendente pubblico.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme indicate mostrano una chiara coordinazione tra il procedimento penale e la sospensione cautelare del dipendente pubblico, con specifiche disposizioni per l'interazione tra i due processi.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il procedimento penale può essere sospeso o interrotto nel caso di una sospensione cautelare del dipendente pubblico.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2009-10-27;150~art69', 'claim': 'Il procedimento penale non determina la sospensione del procedimento, né il differimento dei relativi termini.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art362', 'claim': "I termini previsti dall'articolo 303, comma 1, del codice di procedura penale sono sospesi dalla data del provvedimento che accoglie la dichiarazione di astensione o di ricusazione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.legislativo:2001-06-08;231~art38', 'claim': "Il procedimento per l'illecito amministrativo dell'ente è riunito al procedimento penale instaurato nei confronti dell'autore del reato.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art357', 'claim': "L'esecuzione di un ordine con cui si dispone la carcerazione nei confronti di un imputato al quale sia stata applicata una misura cautelare personale per un altro reato ne sospende l'efficacia.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme indicate mostrano una chiara coordinazione tra il procedimento penale e la sospensione cautelare del dipendente pubblico, con specifiche disposizioni per l'interazione tra i due processi.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art177` | 5.2814 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2009-10-27;150~art69` | 4.3211 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art347` | 4.1036 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2001-06-08;231~art38` | 3.3378 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art444` | 1.9748 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art362` | 1.9088 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2009-10-27;150~art69` | 1.8960 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art357` | 1.8193 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art61` | 1.4723 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:1981-11-24;689~art63` | 1.1898 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2001-03-30;165~art55ter`
- `urn:nir:stato:decreto.legislativo:2001-03-30;165~art55quater`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art177`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 159. (Sospensione del corso della prescrizione). Il corso della prescrizione rimane sospeso in ogni caso in cui la sospensione del procedimento o del processo penale o dei termini di custodia cautelare è imposta da una particolare disposizione di legge, ol

**[2]** `urn:nir:stato:decreto.legislativo:2009-10-27;150~art69`

> DECRETO LEGISLATIVO 27 ottobre 2009, n. 150 ioni pubbliche informazioni o documenti rilevanti per la definizione del procedimento. La predetta attività istruttoria non determina la sospensione del procedimento, nè il differimento dei relativi termini. 7. Il lavoratore dipendente o il dirigente, appa

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art347`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 289 Sospensione dall'esercizio di un pubblico ufficio o servizio 1. Con il provvedimento che dispone la sospensione dall'esercizio di un pubblico ufficio o servizio, il giudice interdice temporaneamente all'imputato, in tutto o i

**[4]** `urn:nir:stato:decreto.legislativo:2001-06-08;231~art38`

> DECRETO LEGISLATIVO 8 giugno 2001, n. 231 Art. 38 Riunione e separazione dei procedimenti 1. Il procedimento per l'illecito amministrativo dell'ente è riunito al procedimento penale instaurato nei confronti dell'autore del reato da cui l'illecito dipende. 2. Si procede separatamente per l'illecito a

**[5]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art444`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 371-bis. (False informazioni al pubblico ministero ((o al procuratore della Corte penale internazionale)) ) Chiunque, nel corso di un procedimento penale, richiesto dal pubblico ministero ((o dal procuratore della Corte penale internazionale)) di fornire i

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art362`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 1, comma 3) che "I termini previsti dall' articolo 303, comma 1, del codice di procedura penale sono sospesi dalla data del provvedimento che accoglie la dichiarazione di astensione o di ricusazione a quella in cui il dibattimento dav

**[7]** `urn:nir:stato:decreto.legislativo:2009-10-27;150~art69`

> DECRETO LEGISLATIVO 27 ottobre 2009, n. 150 ter (Rapporti fra procedimento disciplinare e procedimento penale). - 1. Il procedimento disciplinare, che abbia ad oggetto, in tutto o in parte, fatti in relazione ai quali procede l'autorità giudiziaria, è proseguito e concluso anche in pendenza del proc

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art357`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 298 Sospensione dell'esecuzione delle misure 1. L'esecuzione di un ordine con cui si dispone la carcerazione nei confronti di un imputato al quale sia stata applicata una misura cautelare personale per un altro reato ne sospende

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art61`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 50 Azione penale 1. Il pubblico ministero esercita l'azione penale quando non sussistono i presupposti per la richiesta di archiviazione. 2. Quando non è necessaria la querela, la richiesta, l'istanza o l'autorizzazione a procede

**[10]** `urn:nir:stato:legge:1981-11-24;689~art63`

> LEGGE 24 novembre 1981, n. 689 Art. 63 (( (Esecuzione del lavoro di pubblica utilità sostitutivo). )) ((La sentenza penale irrevocabile o il decreto penale esecutivo che applicano il lavoro di pubblica utilità sono immediatamente trasmessi per estratto a cura della cancelleria all'ufficio di pubblic

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
