# trib_010 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:29 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 13.9s (ret 0.2s + llm 13.5s) |

## Query

> Quali sono i presupposti per l'iscrizione ipotecaria da parte dell'agente della riscossione?

## Risposta

**QUALIFICAZIONE**
Il presupposto per l'iscrizione ipotecaria da parte dell'agente della riscossione è la presenza di un avviso di accertamento emesso dall'amministrazione finanziaria.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica il presupposto per l'iscrizione ipotecaria.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il presupposto per l'iscrizione ipotecaria da parte dell'agente della riscossione è la presenza di un avviso di accertamento emesso dall'amministrazione finanziaria.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99', 'claim': "L'avviso di accertamento costituisce titolo esecutivo per l'iscrizione ipotecaria.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633'}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica il presupposto per l'iscrizione ipotecaria.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art7` | 1.5750 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 0.5515 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art17` | -4.5485 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99` | -5.0331 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | -5.1167 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art63` | -5.6414 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -6.0367 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge:2000-07-27;212~art7` | -6.1536 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -6.2653 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art68` | -6.8324 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602~art77`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 Art. 7 Chiarezza e motivazione degli atti 1. Gli atti dell'amministrazione finanziaria ((, autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria,)) sono motivati ((, a pena di annullabilità, indicando specificamente i presupposti, i mezzi di prova)

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[3]** `urn:nir:stato:legge:2000-07-27;212~art17`

> LEGGE 27 luglio 2000, n. 212 Art. 17 Concessionari della riscossione 1. Le disposizioni della presente legge si applicano anche nei confronti dei soggetti che rivestono la qualifica di concessionari e di organi indiretti dell'amministrazione finanziaria, ivi compresi i soggetti che esercitano l'atti

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 i dell'articolo 55. ((209)) 3. L'avviso di accertamento di cui ai commi 1 e 2, emesso entro i termini di cui all'articolo 57, costituisce titolo esecutivo ai fini della riscossione. 4. Qualora l'Amministrazione finanziaria verifichi sul

**[5]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 ertamento o di rettifica ovvero dell'atto di recupero, che sia stato preceduto dalla comunicazione dello schema di atto. In tale ultimo caso, il termine per l'impugnazione dell'atto innanzi alla Corte di Giustizia tributaria è sospeso ai sensi del comma 3 p

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art63`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  particolare riguardo alle poste attive del patrimonio. Si applicano le disposizioni di cui all'articolo 88, comma 5, terzo e quarto periodo. L'adesione alla proposta è espressa con la sottoscrizione dell'atto negoziale da parte del Direttore della competen

**[7]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  La definizione in contraddittorio, con adesione del contribuente, è applicabile, alle medesime condizioni di cui all'art. 2-bis, nei confronti dei contribuenti, con riferimento alle imposte sulle successioni e donazioni, di registro, ipotecaria, catastale

**[8]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 ici e dipendenti, fermo l'obbligo di autonoma notificazione della cartella di pagamento nei loro confronti. )) 2. Gli atti dell'amministrazione finanziaria e dei concessionari della riscossione devono tassativamente indicare: a) l'ufficio presso il quale è possibile otte

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 i avvisi di irregolarità, di accertamento, di liquidazione e di addebito, unitamente a una certificazione attestante l'entità del debito derivante da atti di accertamento, ancorchè non definitivi, per la parte non iscritta a ruolo, nonchè dai ruoli vistati

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art68`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 licato per un parametro corrispondente al numero dei componenti il nucleo familiare della scala di equivalenza dell'ISEE di cui al decreto del Presidente del Consiglio dei ministri del 5 dicembre 2013, n. 159 . 4. L'OCC, entro sette giorni dall'avvenuto con

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
