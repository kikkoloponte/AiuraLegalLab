# cross_002 — civile+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 15:14 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 29.5s (ret 0.2s + llm 29.2s) |

## Query

> Come interagiscono l'annullamento del provvedimento amministrativo e il risarcimento del danno civile?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda l'interazione tra annullamento del provvedimento amministrativo e risarcimento del danno civile. Si tratta di una questione che coinvolge sia il diritto amministrativo (giurisdizione esclusiva del giudice amministrativo) sia il diritto civile (risarcimento del danno da fatto illecito).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art138",
          "claim": "Le controversie in materia di risarcimento del danno ingiusto cagionato in conseguenza dell'invalidità di un provvedimento amministrativo sono devolute alla giurisdizione esclusiva del giudice amministrativo.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art209",
          "claim": "Ogni reato che abbia cagionato un danno patrimoniale o non patrimoniale obbliga al risarcimento il colpevole.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme applicabili sono: DLgs 2 luglio 2010 n.104 Art.37 (sentenze di merito del giudice amministrativo), RD 16 marzo 1942 n.262 Art.2947 (prescrizione del diritto al risarcimento del danno - 5 anni dal giorno in cui il fatto si è verificato), DPR 22 settembre 1988 n.447 Art.651 (efficacia della sentenza penale di condanna nel giudizio civile o amministrativo di danno) e DLgs 12 gennaio 2019 n.14 Art.116 (risarcimento del danno dalla invalidità della deliberazione).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art37",
          "claim": "In caso di accoglimento del ricorso il giudice annulla in tutto o in parte il provvedimento impugnato e ordina all'amministrazione di provvedere entro un termine.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3177",
          "claim": "Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675",
          "claim": "La sentenza penale irrevocabile di condanna pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accertamento dei fatti.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2019-01-12;14~art116",
          "claim": "Resta salvo il diritto al risarcimento del danno eventualmente cagionato dalla invalidità della deliberazione.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Packet non contiene fonti di giurisprudenza (sentenze della Corte Costituzionale, Cassazione o

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda l'interazione tra annullamento del provvedimento amministrativo e risarcimento del danno civile. Si tratta di una questione che coinvolge sia il diritto amministrativo (giurisdizione esclusiva del giudice amministrativo) sia il diritto civile (risarcimento del danno da fatto illecito).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art138",
          "claim": "Le controversie in materia di risarcimento del danno ingiusto cagionato in conseguenza dell'invalidità di un provvedimento amministrativo sono devolute alla giurisdizione esclusiva del giudice amministrativo.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art209",
          "claim": "Ogni reato che abbia cagionato un danno patrimoniale o non patrimoniale obbliga al risarcimento il colpevole.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme applicabili sono: DLgs 2 luglio 2010 n.104 Art.37 (sentenze di merito del giudice amministrativo), RD 16 marzo 1942 n.262 Art.2947 (prescrizione del diritto al risarcimento del danno - 5 anni dal giorno in cui il fatto si è verificato), DPR 22 settembre 1988 n.447 Art.651 (efficacia della sentenza penale di condanna nel giudizio civile o amministrativo di danno) e DLgs 12 gennaio 2019 n.14 Art.116 (risarcimento del danno dalla invalidità della deliberazione).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art37",
          "claim": "In caso di accoglimento del ricorso il giudice annulla in tutto o in parte il provvedimento impugnato e ordina all'amministrazione di provvedere entro un termine.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3177",
          "claim": "Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675",
          "claim": "La sentenza penale irrevocabile di condanna pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accertamento dei fatti.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2019-01-12;14~art116",
          "claim": "Resta salvo il diritto al risarcimento del danno eventualmente cagionato dalla invalidità della deliberazione.",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Packet non contiene fonti di giurisprudenza (sentenze della Corte Costituzionale, Cassazione o

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art37` | 1.7945 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3177` | 1.4014 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art676` | 0.9955 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545` | 0.8095 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art547` | 0.3536 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675` | 0.2035 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art116` | -0.2388 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677` | -0.4962 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138` | -0.5962 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art209` | -0.8780 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art37`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 34 Sentenze di merito 1. In caso di accoglimento del ricorso il giudice, nei limiti della domanda: a) annulla in tutto o in parte il provvedimento impugnato; b) ordina all'amministrazione, rimasta inerte, di provvedere entro un termine; c) condanna al p

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3177`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2947. (Prescrizione del diritto al risarcimento del danno). Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato. Per il risarcimento del danno prodotto dalla circolazione dei

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art676`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 651-bis ((Efficacia della sentenza di proscioglimento per particolare tenuità del fatto nel giudizio civile o amministrativo di danno.)) (( 1. La sentenza penale irrevocabile di proscioglimento pronunciata per particolare tenuità

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art545`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 538 Condanna per la responsabilità civile 1. Quando pronuncia sentenza di condanna, il giudice decide sulla domanda per le restituzioni e il risarcimento del danno, proposta a norma degli articoli 74 e seguenti. 2. Se pronuncia c

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art547`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 540 Provvisoria esecuzione delle disposizioni civili 1. La condanna alle restituzioniu e al risarcimento del danno è dichiarata provvisoriamente esecutiva, a richiesta della parte civile, quando ricorrono giustificati motivi. 2.

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art675`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 651 Efficacia della sentenza penale di condanna nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di condanna pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accertamento

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art116`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  cui al comma 1, non può essere pronunciata e gli effetti delle operazioni sono irreversibili. Resta salvo il diritto al risarcimento del danno eventualmente cagionato dalla invalidità della deliberazione e il credito è soddisfatto come credito prededucibil

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art677`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 652 Efficacia della sentenza penale di assoluzione nel giudizio civile o amministrativo di danno 1. La sentenza penale irrevocabile di assoluzione pronunciata in seguito a dibattimento ha efficacia di giudicato, quanto all'accert

**[9]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 133 Materie di giurisdizione esclusiva 1. Sono devolute alla giurisdizione esclusiva del giudice amministrativo, salvo ulteriori previsioni di legge: a) le controversie in materia di: 1) risarcimento del danno ingiusto cagionato in conseguenza dell'inos

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art209`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 185. (Restituzioni e risarcimento del danno) Ogni reato obbliga alle restituzioni, a norma delle leggi civili. Ogni reato, che abbia cagionato un danno patrimoniale o non patrimoniale, obbliga al risarcimento il colpevole e le persone che, a norma delle le

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
