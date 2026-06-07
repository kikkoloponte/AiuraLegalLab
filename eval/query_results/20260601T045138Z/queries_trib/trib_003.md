# trib_003 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:26 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 23.4s (ret 0.2s + llm 22.9s) |

## Query

> Come si propone ricorso alla Corte di giustizia tributaria di primo grado?

## Risposta

**QUALIFICAZIONE**
Il ricorso alla Corte di giustizia tributaria di primo grado si propone in caso di impugnazione dell'atto innanzi a questa istanza.

**NORMA APPLICABILE**
Il ricorso alla Corte di giustizia tributaria di primo grado è regolato dal DECRETO LEGISLATIVO 19 giugno 1997, n. 218, Art. 6.

**GIURISPRUDENZA**
Non ci sono disposizioni giurisprudenziali specifiche che si riferiscano al ricorso alla Corte di giustizia tributaria di primo grado in questo contesto.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, quindi la solidità della valutazione è ALTA.

**GAP ANALYSIS**
Non ci sono gap nel Packet per quanto riguarda il ricorso alla Corte di giustizia tributaria di primo grado.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Il ricorso alla Corte di giustizia tributaria di primo grado si propone in caso di impugnazione dell'atto innanzi a questa istanza.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art6', 'claim': "Il termine per l'impugnazione dell'atto innanzi alla Corte di Giustizia tributaria è sospeso ai sensi del comma 3.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### NORMA APPLICABILE

Il ricorso alla Corte di giustizia tributaria di primo grado è regolato dal DECRETO LEGISLATIVO 19 giugno 1997, n. 218, Art. 6.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art6', 'claim': "Il termine per l'impugnazione dell'atto innanzi alla Corte di Giustizia tributaria è sospeso ai sensi del comma 3.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### GIURISPRUDENZA

Non ci sono disposizioni giurisprudenziali specifiche che si riferiscano al ricorso alla Corte di giustizia tributaria di primo grado in questo contesto.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, quindi la solidità della valutazione è ALTA.

### GAP ANALYSIS

Non ci sono gap nel Packet per quanto riguarda il ricorso alla Corte di giustizia tributaria di primo grado.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | 3.3484 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art53` | 0.9766 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art247` | 0.8021 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art38` | -1.6681 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art64` | -2.1987 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art51` | -2.6434 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art52` | -3.5971 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art51` | -3.9418 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art366` | -4.7711 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | -6.9696 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art18`
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art21`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 ertamento o di rettifica ovvero dell'atto di recupero, che sia stato preceduto dalla comunicazione dello schema di atto. In tale ultimo caso, il termine per l'impugnazione dell'atto innanzi alla Corte di Giustizia tributaria è sospeso ai sensi del comma 3 p

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art53`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 istrutturazione dei debiti ((la corte d'appello, in accoglimento della domanda di uno dei soggetti legittimati proposta in primo grado e)) accertati i presupposti di cui all'articolo 121, dichiara aperta la liquidazione giudiziale e rimette gli atti al trib

**[3]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art247`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 247 Reclamo 1. Il decreto del tribunale è reclamabile dinanzi alla corte di appello che pronuncia in camera di consiglio. 2. Il reclamo è proposto con ricorso da depositarsi nella cancelleria della corte di appello nel termine perentorio di trenta gior

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art38`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 38 (( (Iniziativa del pubblico ministero). )) (( 1. Il pubblico ministero presenta il ricorso per l'apertura della liquidazione giudiziale in ogni caso in cui ha notizia dell'esistenza di uno stato di insolvenza. 2. L'autorità giudiziaria che rileva l'

**[5]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art64`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  cancelleria. 6. In pendenza del giudizio davanti alla Corte di cassazione, possono essere sospesi i processi la cui definizione dipende dalla risoluzione della medesima questione sulla quale la Corte è chiamata a pronunciarsi. Intervenuta la decisione della

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art51`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 , in quanto compatibile, l'articolo 52 se il ricorso è promosso contro la sentenza con la quale la corte di appello ha rigettato il reclamo. (( 15. In caso di società o enti, il giudice accerta, con la sentenza che decide l'impugnazione, se sussiste mala fe

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art52`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 52 Sospensione della liquidazione, dell'esecuzione del piano o degli accordi 1. Proposto il reclamo, la corte di appello, su richiesta di parte o del curatore, può, quando ricorrono gravi e fondati motivi, sospendere, in tutto o in parte o temporaneame

**[8]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art51`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  dal deposito del ricorso. 6. Il ricorso, unitamente al decreto di fissazione dell'udienza, è notificato ((a cura del reclamante)) al curatore o al commissario giudiziale e alle altre parti entro dieci giorni ((dalla comunicazione del decreto)) . 7. Tra la

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art366`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 366 Modifica all' articolo 147 del Testo unico in materia di spese di giustizia 1. L' articolo 147 del decreto del Presidente della Repubblica 30 maggio 2002, n. 115 , è sostituito dal seguente: «Art. 147 (L) (Recupero delle spese in caso di revoca del

**[10]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
