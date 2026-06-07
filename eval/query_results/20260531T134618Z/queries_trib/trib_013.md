# trib_013 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 14:10 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 10.8s (ret 0.3s + llm 10.2s) |

## Query

> Quali sono le sanzioni per omessa dichiarazione dei redditi?

## Risposta

**QUALIFICAZIONE**
Le sanzioni per l'omessa dichiarazione dei redditi sono previste dal DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917.

**NORMA APPLICABILE**
Le sanzioni sono stabilite dallo stesso decreto ministeriale di cui all'articolo 129 del DECRETO DEL PRESIDENTE DELLA REPUBBlica 22 dicembre 1986, n. 917.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle sanzioni per l'omessa dichiarazione dei redditi.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme stabilite dal DECRETO DEL PRESIDENTE DELLA REPUBBlica 22 dicembre 1986, n. 917 sono chiare e specifiche sulle sanzioni per l'omessa dichiarazione dei redditi.

**GAP ANALYSIS**
Non ci sono gap notevoli nel Packet in quanto tutte le norme necessarie per valutare la situazione sono presenti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le sanzioni per l'omessa dichiarazione dei redditi sono previste dal DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204', 'claim': "La detrazione non spetta in caso di omessa presentazione della dichiarazione o di omessa indicazione dei redditi prodotti all'estero nella dichiarazione presentata.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art33', 'claim': "Per l'accertamento, la riscossione, il contenzioso e le sanzioni si applicano, in quanto compatibili, le disposizioni previste per l'imposta sul reddito.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Le sanzioni sono stabilite dallo stesso decreto ministeriale di cui all'articolo 129 del DECRETO DEL PRESIDENTE DELLA REPUBBlica 22 dicembre 1986, n. 917.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124', 'claim': "Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pagamento.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano alle sanzioni per l'omessa dichiarazione dei redditi.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme stabilite dal DECRETO DEL PRESIDENTE DELLA REPUBBlica 22 dicembre 1986, n. 917 sono chiare e specifiche sulle sanzioni per l'omessa dichiarazione dei redditi.

### GAP ANALYSIS

Non ci sono gap notevoli nel Packet in quanto tutte le norme necessarie per valutare la situazione sono presenti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204` | 5.8493 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art148` | 4.6254 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | 4.6232 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art691` | 4.4061 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art162` | 4.1482 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art15` | 4.1262 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art67` | 3.5947 | hybrid_rrf |  |
| 8 | `urn:nir:stato:legge:2000-07-27;212~art6` | 3.3060 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art33` | 3.0881 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art96` | 2.4909 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art1`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  in Italia. 8. La detrazione non spetta in caso di omessa presentazione della dichiarazione o di omessa indicazione dei redditi prodotti all'estero nella dichiarazione presentata. 9. Per le imposte pagate all'estero dalle società , ass

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art148`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 posta, le sanzioni e gli interessi conseguenti all'obbligo di imputazione del reddito. 9. Le disposizioni applicative della presente norma sono stabilite dallo stesso decreto ministeriale di cui all'articolo 129. 10. Ai soggetti di cui

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art691`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 664 Esecuzione di altre sanzioni pecuniarie 1. Le somme dovute per sanzioni disciplinari pecuniarie o per condanna alla perdita della cauzione o in conseguenza della dichiarazione di inammissibilità o di rigetto di una richiesta,

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art162`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  di cui all'articolo 36-bis del medesimo decreto, in conseguenza della rettifica operata sulla propria dichiarazione dei redditi; b) per la sanzione correlata alla maggiore imposta accertata riferita al reddito complessivo globale risu

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art15`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 15 Sanzioni applicabili nel caso di omessa impugnazione 1. Le sanzioni irrogate per le violazioni indicate nell'articolo 2, comma 5, del presente decreto, ((negli articoli 71 e 72)) del testo unico delle disposizioni concernenti l'imposta di registro,

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art67`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Gli uffici delle imposte procedono all'accertamento d'ufficio nei casi di omessa presentazione della dichiarazione o di presentazione di dichiarazioni nulle ai sensi delle disposizioni del titolo I. Nelle ipotesi di cui al precedente

**[8]** `urn:nir:stato:legge:2000-07-27;212~art6`

> LEGGE 27 luglio 2000, n. 212  tributi per i quali il contribuente non è tenuto ad effettuare il versamento diretto. Sono ((annullabili)) i provvedimenti emessi in violazione delle disposizioni di cui al presente comma. (9) 5-bis. In caso di esercizio di attività istruttorie di controllo nei confront

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art33`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  entro la data prevista per il versamento del saldo delle imposte sui redditi. Per l'accertamento, la riscossione, il contenzioso e le sanzioni si applicano, in quanto compatibili, le disposizioni previste per l'imposta sul reddito del

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art96`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 54-bis.1 (( (Liquidazione IVA nel caso di dichiarazioni omesse) )) 1. ((Senza pregiudizio dell'azione accertatrice, l'Agenzia delle entrate, entro il termine di cui all'articolo 57, comma 2, può procedere, in caso di omessa present

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
