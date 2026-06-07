# trib_016 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:32 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 19.7s (ret 0.2s + llm 19.3s) |

## Query

> Quali sono i limiti alla compensazione dei crediti fiscali?

## Risposta

**QUALIFICAZIONE**
La domanda riguarda i limiti alla compensazione dei crediti fiscali.

**NORMA APPLICABILE**
I limiti alla compensazione dei crediti fiscali sono stabiliti dall'articolo 155 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente ai limiti della compensazione dei crediti fiscali.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: I limiti alla compensazione dei crediti fiscali sono chiaramente stabiliti dalla norma, ma la mancanza di giurisprudenza specifica potrebbe ridurre la solidità dell'analisi.

**GAP ANALYSIS**
Il Packet non contiene giurisprudenze che potrebbero fornire ulteriori dettagli o contesto sui limiti della compensazione dei crediti fiscali.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La domanda riguarda i limiti alla compensazione dei crediti fiscali.

### NORMA APPLICABILE

I limiti alla compensazione dei crediti fiscali sono stabiliti dall'articolo 155 del DECRETO LEGISLATIVO 12 gennaio 2019, n. 14.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art155', 'claim': "I creditori possono opporre in compensazione dei loro debiti verso il debitore il cui patrimonio è sottoposto alla liquidazione giudiziale i propri crediti verso quest'ultimo, ancorchè non scaduti prima dell'apertura della procedura.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente ai limiti della compensazione dei crediti fiscali.

### VALUTAZIONE

VALUTAZIONE PERSONALE: I limiti alla compensazione dei crediti fiscali sono chiaramente stabiliti dalla norma, ma la mancanza di giurisprudenza specifica potrebbe ridurre la solidità dell'analisi.

### GAP ANALYSIS

Il Packet non contiene giurisprudenze che potrebbero fornire ulteriori dettagli o contesto sui limiti della compensazione dei crediti fiscali.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art221` | 3.2052 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6` | 3.1663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art8` | 2.6132 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155` | 2.0325 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art118` | 1.1244 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art268` | -1.1753 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art224` | -2.0446 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art1` | -3.0528 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art63` | -3.2206 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art102` | -4.1631 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art221`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 177-ter (Disciplina del riporto delle perdite fiscali infragruppo) 1. I limiti e le condizioni al riporto delle perdite fiscali di cui agli articoli 84, comma 3, 172, commi 7 e 7-bis, ((173, comma 10, e 176, comma 5-bis)) , non si

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 6 (Prededucibilità dei crediti) 1. Oltre ai crediti così espressamente qualificati dalla legge, sono prededucibili: a) i crediti relativi a spese e compensi per le prestazioni rese ((nell'esercizio delle funzioni rientranti nella competenza dell'organi

**[3]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 155 Compensazione 1. I creditori possono opporre in compensazione dei loro debiti verso il debitore il cui patrimonio è sottoposto alla liquidazione giudiziale i propri crediti verso quest'ultimo, ancorchè non scaduti prima dell'apertura della procedur

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art118`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 azione dei beni indicati nell'articolo 85, comma 1, lettere c), d) ed e), operata in base alla corretta applicazione di tali principi assume rilievo anche ai fini fiscali. (133) 5. In caso di aumento del capitale della società emittent

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art268`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  creditori, anche mediante l'esercizio di azioni giudiziarie.)) 4. Non sono compresi nella liquidazione: a) i crediti impignorabili ai sensi dell' articolo 545 del codice di procedura civile ; b) i crediti aventi carattere alimentare e di mantenimento, gli

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art224`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 224 Crediti assistiti da prelazione 1. I crediti assistiti da privilegio generale hanno diritto di prelazione per il capitale, le spese e gli interessi, nei limiti di cui agli articoli 153 e 154, sul prezzo ricavato dalla liquidazione del patrimonio mo

**[8]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art1`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 amento; b) unificazione dei criteri di determinazione delle basi imponibili fiscali e di queste con quelle contributive e delle relative procedure di liquidazione, riscossione, accertamento e contenzioso; effettuazione di versamenti unitari, anche in unica s

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 ) l'atto di cui alla lettera a), emesso a seguito del controllo degli importi a credito indicati nei modelli di pagamento unificato per la riscossione di crediti non spettanti e inesistenti, di cui all' articolo 13, commi 4 e 5, del d

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art102`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 80 Riporto o rimborso delle eccedenze 1. Se l'ammontare complessivo dei ((crediti per le imposte pagate all'estero)) , delle ritenute d'acconto e dei versamenti in acconto di cui ai precedenti articoli è superiore a quello dell'im

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
