# trib_013 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:31 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 23.3s (ret 0.2s + llm 22.9s) |

## Query

> Quali sono le sanzioni per omessa dichiarazione dei redditi?

## Risposta

**QUALIFICAZIONE**
L'omessa dichiarazione dei redditi può portare a sanzioni in base alle normative vigenti.

**NORMA APPLICABILE**
Il decreto del Presidente della Repubblica 22 dicembre 1986, n. 917, articolo 162.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Le norme esistenti non specificano sanzioni precise per l'omessa dichiarazione, ma indicano che la detrazione non spetta in caso di omessa presentazione.

**GAP ANALYSIS**
Il Packet manca delle norme che specificano le sanzioni per l'omessa dichiarazione dei redditi.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'omessa dichiarazione dei redditi può portare a sanzioni in base alle normative vigenti.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-07-09;241~art3', 'claim': "I redditi per i quali manca l'indicazione si considerano non dichiarati.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}, {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art162', 'claim': 'La detrazione non spetta in caso di omessa presentazione della dichiarazione.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il decreto del Presidente della Repubblica 22 dicembre 1986, n. 917, articolo 162.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art162', 'claim': 'La detrazione non spetta in caso di omessa presentazione della dichiarazione.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Le norme esistenti non specificano sanzioni precise per l'omessa dichiarazione, ma indicano che la detrazione non spetta in caso di omessa presentazione.

### GAP ANALYSIS

Il Packet manca delle norme che specificano le sanzioni per l'omessa dichiarazione dei redditi.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art3` | 6.9978 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art3` | 6.2869 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204` | 5.8493 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art162` | 4.1482 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art67` | 3.5947 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art96` | 2.4909 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art16` | 2.3097 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art156` | 2.2741 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:1997-07-09;241~art15` | 1.4885 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204` | 1.3767 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art1`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art3`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241  imposte stesse. I redditi per i quali manca tale indicazione si considerano non dichiarati ai fini dell'accertamento e delle sanzioni. La dichiarazione delle persone fisiche è unica per i redditi propri del soggetto e per quelli di altre persone a lui imput

**[2]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art3`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 is, con le modalità previste dall'art. 12 ed entro il termine stabilito per la presentazione della dichiarazione dei redditi. Ai fini della lettera c) del comma precedente sono assimilati ai redditi di lavoro dipendente soltanto i compensi dei lavoratori soc

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  in Italia. 8. La detrazione non spetta in caso di omessa presentazione della dichiarazione o di omessa indicazione dei redditi prodotti all'estero nella dichiarazione presentata. 9. Per le imposte pagate all'estero dalle società , ass

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art162`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  di cui all'articolo 36-bis del medesimo decreto, in conseguenza della rettifica operata sulla propria dichiarazione dei redditi; b) per la sanzione correlata alla maggiore imposta accertata riferita al reddito complessivo globale risu

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art67`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Gli uffici delle imposte procedono all'accertamento d'ufficio nei casi di omessa presentazione della dichiarazione o di presentazione di dichiarazioni nulle ai sensi delle disposizioni del titolo I. Nelle ipotesi di cui al precedente

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art96`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 54-bis.1 (( (Liquidazione IVA nel caso di dichiarazioni omesse) )) 1. ((Senza pregiudizio dell'azione accertatrice, l'Agenzia delle entrate, entro il termine di cui all'articolo 57, comma 2, può procedere, in caso di omessa present

**[7]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art16`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 16 Controlli sulla base della copia delle dichiarazioni 1. Qualora successivamente all'accertamento le dichiarazioni presentate ai fini delle imposte sui redditi e dell'imposta sul valore aggiunto risultino difformi dalle copie acquisite nel corso dell

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art156`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 122 (( (Obblighi della società o ente controllante).)) ((1. La società o ente controllante presenta la dichiarazione dei redditi del consolidato, calcolando il reddito complessivo globale risultante dalla somma algebrica dei reddi

**[9]** `urn:nir:stato:decreto.legislativo:1997-07-09;241~art15`

> DECRETO LEGISLATIVO 9 luglio 1997, n. 241 Art. 15 (Modifica dei termini per l'accertamento delle imposte sui redditi) 1. All' articolo 43 del decreto del Presidente della Repubblica 29 settembre 1973, n. 600 , sono apportate le seguenti modificazioni: a) al primo comma, riguardante il termine per l'

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 165 Credito d'imposta per i redditi prodotti all'estero 1. Se alla formazione del reddito complessivo concorrono redditi prodotti all'estero, le imposte ivi pagate a titolo definitivo su tali redditi sono ammesse in detrazione dal

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
