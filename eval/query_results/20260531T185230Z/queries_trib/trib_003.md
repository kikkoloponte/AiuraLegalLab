# trib_003 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:32 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.0s (ret 0.1s + llm 66.7s) |

## Query

> Come si propone ricorso alla Corte di giustizia tributaria di primo grado?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda la procedura per proporre ricorso alla Corte di giustizia tributaria di primo grado. Il Packet contiene fonti sul codice di procedura civile (R.D. 1443/1940), codice di procedura penale (D.P.R. 447/1988) e diritto amministrativo (D.Lgs. 104/2010), ma nessuna fonte specifica sulla giurisdizione tributaria.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art53",
          "claim": "Procedimento del regolamento di competenza alla corte di cassazione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art47",
          "claim": "Regolamento di giurisdizione presso sezioni unite Corte di cassazione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art405",
          "claim": "Sentenze impugnabili con ricorso per cassazione per motivi di giurisdizione e competenza",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Nel Packet non sono presenti norme specifiche sulla Corte di giustizia tributaria di primo grado. Le fonti disponibili (R.D. 1443/1940, D.P.R. 447/1988, D.Lgs. 104/2010) riguardano rispettivamente codice procedura civile, penale e amministrativo, non tributario.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art582",
          "claim": "Ricorso immediato per cassazione nel codice di procedura penale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n. 1988"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art628",
          "claim": "Cognizione della corte di cassazione limitata ai motivi proposti",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n. 1988"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda la procedura per proporre ricorso alla Corte di giustizia tributaria di primo grado. Il Packet contiene fonti sul codice di procedura civile (R.D. 1443/1940), codice di procedura penale (D.P.R. 447/1988) e diritto amministrativo (D.Lgs. 104/2010), ma nessuna fonte specifica sulla giurisdizione tributaria.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art53",
          "claim": "Procedimento del regolamento di competenza alla corte di cassazione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art47",
          "claim": "Regolamento di giurisdizione presso sezioni unite Corte di cassazione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art405",
          "claim": "Sentenze impugnabili con ricorso per cassazione per motivi di giurisdizione e competenza",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Nel Packet non sono presenti norme specifiche sulla Corte di giustizia tributaria di primo grado. Le fonti disponibili (R.D. 1443/1940, D.P.R. 447/1988, D.Lgs. 104/2010) riguardano rispettivamente codice procedura civile, penale e amministrativo, non tributario.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art582",
          "claim": "Ricorso immediato per cassazione nel codice di procedura penale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n. 1988"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art628",
          "claim": "Cognizione della corte di cassazione limitata ai motivi proposti",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n. 1988"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art53` | 3.8758 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art47` | 3.1984 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art582` | 3.0898 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art628` | 2.4538 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art405` | 1.0557 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art118` | 1.0259 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art8` | 0.9075 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art858` | 0.6384 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art593` | 0.3132 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art435` | -0.6378 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art18`
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art21`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art53`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 47. (Procedimento del regolamento di competenza). L'istanza di regolamento di competenza si propone alla corte di cassazione con ricorso sottoscritto dal procuratore o dalla parte, se questa si è costituita personalmente. Il ricorso deve essere notificato

**[2]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art47`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 41. (Regolamento di giurisdizione). Finchè la causa non sia decisa nel merito in primo grado, ciascuna parte può chiedere alle sezioni unite della Corte di cassazione che risolvano le questioni di giurisdizione di cui all'articolo 37. L'istanza si propone

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art582`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 569 Ricorso immediato per cassazione 1. La parte che ha diritto di appellare la sentenza di primo grado può proporre direttamente ricorso per cassazione. 2. Se la sentenza è appellata da una delle altre parti, si applica la dispo

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art628`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 609 Cognizione della corte di cassazione 1. Il ricorso attribuisce alla corte di cassazione la cognizione del procedimento limitatamente ai motivi proposti. 2. La corte decide altresì le questioni rilevabili di ufficio in ogni st

**[5]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art405`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 360. (Sentenze impugnabili e motivi di ricorso). Le sentenze pronunciate in grado d'appello o in unico grado possono essere impugnate con ricorso per cassazione: 1) per motivi attinenti alla giurisdizione; 2) per violazione delle norme sulla competenza, qu

**[6]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art118`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 113 Giudice dell'ottemperanza 1. Il ricorso si propone, nel caso di cui all'articolo 112, comma 2, lettere a) e b), al giudice che ha emesso il provvedimento della cui ottemperanza si tratta; la competenza è del tribunale amministrativo regionale anche

**[7]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art8`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 5 Tribunali amministrativi regionali 1. Sono organi di giurisdizione amministrativa di primo grado i tribunali amministrativi regionali e il Tribunale regionale di giustizia amministrativa per la regione autonoma del Trentino - Alto Adige. 2. Il tribuna

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art858`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 688. (Forma dell'istanza). La denuncia di nuova opera o di danno temuto si propone con ricorso al giudice competente a norma dell'articolo 21. (88) ((90)) Quando vi è causa pendente per il merito, la denuncia si propone a norma dell'articolo 669-quater. (6

**[9]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art593`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 473-bis.52 (Forma della domanda). La domanda per interdizione o inabilitazione si propone con ricorso diretto al tribunale del luogo in cui la persona nei confronti della quale è proposta ha residenza o domicilio. Il ricorso contiene le indicazioni di cui

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art435`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 383. (Cassazione con rinvio). La corte, quando accoglie il ricorso per motivi diversi da quelli richiamati nell'articolo precedente, rinvia la causa ad altro giudice di grado pari a quello che ha pronunciato la sentenza cassata. Nel caso previsto nell'arti

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
