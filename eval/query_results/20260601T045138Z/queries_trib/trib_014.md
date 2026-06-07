# trib_014 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:31 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 23.8s (ret 0.2s + llm 23.4s) |

## Query

> Come funziona il ravvedimento operoso e quali riduzioni prevede?

## Risposta

**QUALIFICAZIONE**
Il ravvedimento operoso prevede riduzioni di crediti e altre operazioni in favore dei creditori.

**NORMA APPLICABILE**
Il ravvedimento operoso è regolato dall'articolo 132 del decreto legge 12 gennaio 2019, n. 14.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel packet riguardanti il ravvedimento operoso.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica sul ravvedimento operoso, ma manca di giurisprudenza per confermare l'interpretazione.

**GAP ANALYSIS**
Il packet non contiene giurisprudenze relative al ravvedimento operoso.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il ravvedimento operoso prevede riduzioni di crediti e altre operazioni in favore dei creditori.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art132', 'claim': 'Il decreto legge 12 gennaio 2019, n. 14 prevede riduzioni di crediti e altre operazioni in favore dei creditori.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il ravvedimento operoso è regolato dall'articolo 132 del decreto legge 12 gennaio 2019, n. 14.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art132', 'claim': "Il ravvedimento operoso è regolato dall'articolo 132 del decreto legge 12 gennaio 2019, n. 14.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel packet riguardanti il ravvedimento operoso.

*Citazioni: {'source_id': '', 'claim': 'Non ci sono giurisprudenze specifiche menzionate nel packet riguardanti il ravvedimento operoso.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica sul ravvedimento operoso, ma manca di giurisprudenza per confermare l'interpretazione.

### GAP ANALYSIS

Il packet non contiene giurisprudenze relative al ravvedimento operoso.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art109` | -1.3607 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art102` | -2.7462 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art40` | -3.0196 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge:2000-07-27;212~art3` | -3.1905 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art116` | -3.6920 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art132` | -4.1253 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art62` | -5.0787 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art102` | -5.1579 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art94` | -6.8840 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art109` | -7.4934 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-12-18;472~art13`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art109`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  1. 3. I creditori muniti di privilegio, pegno o ipoteca, ancorchè la garanzia sia contestata, dei quali la proposta di concordato prevede l'integrale pagamento, non hanno diritto al voto se non rinunciano in tutto od in parte al diritto di prelazione. Qual

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art102`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 ottato, per una o più annualità tra i periodi d'imposta 2018, 2019, 2020 e 2021, il regime di ravvedimento di cui al comma 1 del presente articolo, i termini di decadenza per l'accertamento, di cui all' articolo 43 del decreto del Presi

**[3]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art40`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165 que anni, a condizione che adottino o abbiano adottato le misure di contenimento della spesa di cui all' articolo 4, comma 1, del decreto-legge 6 marzo 2014, n. 16 , dimostrino l'effettivo conseguimento delle riduzioni di spesa previste dalle predette misure

**[4]** `urn:nir:stato:legge:2000-07-27;212~art3`

> LEGGE 27 luglio 2000, n. 212 , n. 600 , e all' articolo 57 del decreto del Presidente della Repubblica 26 ottobre 1972, n. 633 , relativi alle annualità oggetto di ravvedimento sono prorogati al 31 dicembre 2028. In ogni caso, per i soggetti a cui si applicano gli ISA che aderiscono al concordato pr

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art116`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  cui al comma 1, non può essere pronunciata e gli effetti delle operazioni sono irreversibili. Resta salvo il diritto al risarcimento del danno eventualmente cagionato dalla invalidità della deliberazione e il credito è soddisfatto come credito prededucibil

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art132`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 132 Integrazione dei poteri del curatore 1. Le riduzioni di crediti, le transazioni, i compromessi, le rinunzie alle liti, le ricognizioni di diritti di terzi, la cancellazione di ipoteche, la restituzione di pegni, lo svincolo delle cauzioni, l'accett

**[7]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art62`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  atta a valorizzare la specificità professionali, con particolare riguardo alle competenze di tipo tecnico. Il regolamento disciplina inoltre le modalità di svolgimento in sede periferica da parte degli uffici territoriali del governo di funzioni e compiti d

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art102`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633  essere utilizzati come carburanti per motori, ad eccezione delle cessioni di carburante per autotrazione presso gli impianti stradali di distribuzione, per le quali il comma 920 si applica dal 1° gennaio 2019". -------------- AGGIORNAM

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art94`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 licità e alle procedure competitive quando può essere compromesso irreparabilmente l'interesse dei creditori al miglior soddisfacimento. Del provvedimento e del compimento dell'atto deve comunque essere data adeguata pubblicità e comunicazione ai creditori.

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art109`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  di cui all' articolo 2751-bis, n. 1, del codice civile , il termine di cui al quarto periodo è di trenta giorni. Se non ricorrono le condizioni di cui al ((terzo e quarto)) periodo, i creditori muniti di diritto di prelazione votano e, per la parte incapie

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
