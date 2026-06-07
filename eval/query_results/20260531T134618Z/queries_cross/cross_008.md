# cross_008 — penale+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:00 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 6.7s (ret 0.3s + llm 6.2s) |

## Query

> Quali sono gli effetti della sentenza penale di condanna sull'interdizione dai pubblici uffici?

## Risposta

**QUALIFICAZIONE**
Si tratta dell'effetto della sentenza penale di condanna sull'interdizione dai pubblici uffici.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme stabiliscono chiaramente che la condanna a determinate pene importa l'interdizione dai pubblici uffici. Non ci sono contrasti giurisprudenziali rilevanti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Si tratta dell'effetto della sentenza penale di condanna sull'interdizione dai pubblici uffici.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art29', 'claim': "La condanna all'ergastolo e la condanna alla reclusione per un tempo non inferiore a cinque anni importano l'interdizione perpetua del condannato dai pubblici uffici.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398'}, {'source_id': 'urn:nir:stato:regio.decreto:1930-10-19;1398~art460', 'claim': "La condanna per i delitti preveduti dagli articoli 380, 381, prima parte, e 382 importa l'interdizione dai pubblici uffici.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 19 ottobre 1930, n. 1398'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme stabiliscono chiaramente che la condanna a determinate pene importa l'interdizione dai pubblici uffici. Non ci sono contrasti giurisprudenziali rilevanti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675` | 6.5188 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art34` | 5.4190 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art679` | 5.4053 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art678` | 5.3909 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art508` | 4.9777 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677` | 4.6588 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art545` | 3.3656 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art813` | 3.1693 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art690` | 3.1435 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art460` | 2.9499 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 651 Efficacia della sentenza penale di condanna nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di condanna pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accertamento

**[2]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art34`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 29. (Casi nei quali alla condanna consegue l'interdizione dai pubblici uffici) La condanna all'ergastolo e la condanna alla reclusione per un tempo non inferiore a cinque anni importano l'interdizione perpetua del condannato dai pubblici uffici; e la conda

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art679`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 654 Efficacia della sentenza penale di condanna o di assoluzione in altri giudizi civili o amministrativi 1. Nei confronti dell'imputato, della parte civile e del responsabile civile che si sia costituito o che sia intervenuto ne

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art678`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 653 Efficacia della sentenza penale (( . . . )) nel giudizio disciplinare 1. La sentenza penale irrevocabile di assoluzione (( . . . )) ha efficacia di giudicato nel giudizio per responsabilità disciplinare davanti alle pubbliche

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art508`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 421. (Decorrenza degli effetti dell'interdizione e dell'inabilitazione). L'interdizione e l'inabilitazione producono i loro effetti dal giorno della pubblicazione della sentenza, salvo il caso previsto dall'art. 416. ((146))

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 652 Efficacia della sentenza penale di assoluzione nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di assoluzione pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accert

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art545`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 448. (Pene accessorie) La condanna per taluno dei delitti preveduti da questo capo importa la pubblicazione della sentenza. ((La condanna per taluno dei delitti preveduti dagli articoli 439, 440, 441 e 442 importa l'interdizione da cinque a dieci anni dall

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art813`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 609-nonies. (Pene accessorie ed altri effetti penali). La condanna o l'applicazione della pena su richiesta delle parti ai sensi dell' articolo 444 del codice di procedura penale per alcuno dei delitti previsti dagli articoli 609-bis, 609-ter, 609-quater,

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art690`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 663 Esecuzione di pene concorrenti 1. Quando la stessa persona è stata condannata con più sentenze o decreti penali per reati diversi, il pubblico ministero determina la pena da eseguirsi, in osservanza delle norme sul concorso d

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art460`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 383. (Interdizione dai pubblici uffici) La condanna per i delitti preveduti dagli articoli 380, 381, prima parte, e 382 importa l'interdizione dai pubblici uffici.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
