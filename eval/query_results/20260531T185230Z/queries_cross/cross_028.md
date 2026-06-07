# cross_028 — civile+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:08 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 66.2s (ret 0.1s + llm 65.9s) |

## Query

> Qual è il regime della prescrizione del diritto al risarcimento del danno derivante da reato?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda il regime di prescrizione del diritto al risarcimento del danno derivante da reato (azione civile nel processo penale). Si tratta di un'azione risarcitoria che può essere esercitata nel processo penale dal soggetto danneggiato.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90",
          "claim": "L'azione civile per le restituzioni e per il risarcimento del danno può essere esercitata nel processo penale dal soggetto al quale il reato ha recato danno",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "DPR 22 settembre 1988, n. 447"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art209",
          "claim": "Ogni reato che abbia cagionato un danno patrimoniale o non patrimoniale obbliga al risarcimento il colpevole e le persone che, a norma delle leggi civili, sono tenute a rispondere del fatto",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "RD 19 ottobre 1930, n. 1398"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Per la prescrizione del diritto al risarcimento del danno derivante da fatto illecito si applica l'art. 2947 c.c. (5 anni dal giorno in cui il fatto si è verificato). Per il risarcimento del danno prodotto dalla circolazione dei veicoli si applica il DLgs 206/2005 art. 125 (3 anni dal giorno in cui il danneggiato ha avuto o avrebbe dovuto avere conoscenza del danno, del difetto e dell'identità del responsabile).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3177",
          "claim": "Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2005-09-06;206~art125",
          "claim": "Il diritto al risarcimento si prescrive in tre anni dal giorno in cui il danneggiato ha avuto o avrebbe dovuto avere conoscenza del danno, del difetto e dell'

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda il regime di prescrizione del diritto al risarcimento del danno derivante da reato (azione civile nel processo penale). Si tratta di un'azione risarcitoria che può essere esercitata nel processo penale dal soggetto danneggiato.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90",
          "claim": "L'azione civile per le restituzioni e per il risarcimento del danno può essere esercitata nel processo penale dal soggetto al quale il reato ha recato danno",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "DPR 22 settembre 1988, n. 447"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art209",
          "claim": "Ogni reato che abbia cagionato un danno patrimoniale o non patrimoniale obbliga al risarcimento il colpevole e le persone che, a norma delle leggi civili, sono tenute a rispondere del fatto",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "RD 19 ottobre 1930, n. 1398"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Per la prescrizione del diritto al risarcimento del danno derivante da fatto illecito si applica l'art. 2947 c.c. (5 anni dal giorno in cui il fatto si è verificato). Per il risarcimento del danno prodotto dalla circolazione dei veicoli si applica il DLgs 206/2005 art. 125 (3 anni dal giorno in cui il danneggiato ha avuto o avrebbe dovuto avere conoscenza del danno, del difetto e dell'identità del responsabile).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3177",
          "claim": "Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2005-09-06;206~art125",
          "claim": "Il diritto al risarcimento si prescrive in tre anni dal giorno in cui il danneggiato ha avuto o avrebbe dovuto avere conoscenza del danno, del difetto e dell'

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3177` | 7.1858 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art125` | 6.5833 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1263` | 4.4642 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art671` | 3.7679 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art175` | 3.4598 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90` | 3.3744 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3184` | 3.0871 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art209` | 1.7250 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art176` | 1.6319 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art887` | 0.4174 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3177`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2947. (Prescrizione del diritto al risarcimento del danno). Il diritto al risarcimento del danno derivante da fatto illecito si prescrive in cinque anni dal giorno in cui il fatto si è verificato. Per il risarcimento del danno prodotto dalla circolazione dei

**[2]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art125`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 125 Prescrizione 1. Il diritto al risarcimento si prescrive in tre anni dal giorno in cui il danneggiato ha avuto o avrebbe dovuto avere conoscenza del danno, del difetto e dell'identità del responsabile. 2. Nel caso di aggravamento del danno, la pre

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1263`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1218. (Responsabilità del debitore). Il debitore che non esegue esattamente la prestazione dovuta è tenuto al risarcimento del danno, se non prova che l'inadempimento o il ritardo è stato determinato da impossibilità della prestazione derivante da causa a lui

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art671`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 647 Risarcimento del danno e riparazione 1. Nel caso previsto dall'articolo 630 comma 1 lettera d), lo Stato, se ha corrisposto la riparazione, si surroga, fino alla concorrenza della somma pagata, nel diritto al risarcimento dei

**[5]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art175`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 157. (Prescrizione. Tempo necessario a prescrivere). La prescrizione estingue il reato decorso il tempo corrispondente al massimo della pena edittale stabilita dalla legge e comunque un tempo non inferiore a sei anni se si tratta di delitto e a quattro ann

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 74 Legittimazione all'azione civile 1. L'azione civile per le restituzioni e per il risarcimento del danno di cui all' articolo 185 del codice penale può essere esercitata nel processo penale dal soggetto al quale il reato ha rec

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3184`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2954. (Prescrizione di sei mesi). Si prescrive in sei mesi il diritto degli albergatori e degli osti per l'alloggio e il vitto che somministrano, e si prescrive nello stesso termine il diritto di tutti coloro che danno alloggio con o senza pensione.

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art209`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 185. (Restituzioni e risarcimento del danno) Ogni reato obbliga alle restituzioni, a norma delle leggi civili. Ogni reato, che abbia cagionato un danno patrimoniale o non patrimoniale, obbliga al risarcimento il colpevole e le persone che, a norma delle le

**[9]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art176`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 158. (Decorrenza del termine della prescrizione) ((Il termine della prescrizione decorre, per il reato consumato, dal giorno della consumazione; per il reato tentato, dal giorno in cui è cessata l'attività del colpevole; per il reato permanente o continuat

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art887`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 644-ter. (( (Prescrizione del reato di usura).)) ((La prescrizione del reato di usura decorre dal giorno dell'ultima riscossione sia degli interessi che del capitale)) .

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
