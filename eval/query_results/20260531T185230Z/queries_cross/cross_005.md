# cross_005 — civile+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:43 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.1s (ret 0.2s + llm 66.7s) |

## Query

> Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?" (What is the opposability to tax authorities of acts of business transfer and the tax solidarity of the assignee?)

2.  **Analyze the Research Packet:**
    *   Source [1]: Art. 1248 CC (Inopponibilità della compensazione). Debitore che accetta cessione non può opporre compensazione al cessionario.
    *   Source [2]: Art. 2559 CC (Crediti relativi all'azienda ceduta). Cessione crediti azienda ha effetto verso terzi dal momento iscrizione registro, anche senza notifica.
    *   Source [3]: Art. 1264 CC (Efficacia cessione riguardo al debitore ceduto). Cessione ha effetto verso debitore quando accettata o notificata. Pagamento a cedente prima notifica è valido.
    *   Source [4]: DPR 917/86, Art. 57 (actually text says Art. 47 in title but text mentions stratificazione riserve). Mentions D.Lgs 2018 n. 142 update.
    *   Source [5]: Art. 2112 CC (Mantenimento diritti lavoratori trasferimento azienda). Rapporto continua con cessionario.
    *   Source [6]: Art. 2112 CC (continuation text about identity of rights).
    *   Source [7]: D.Lgs 14/2019, Art. 212 (Collective agreements substitution).
    *   Source [8]: D.Lgs 206/2005, Art. 146 (Consumer credit acts).
    *   Source [9]: Art. 1263 CC (Accessori del credito). Credito trasferito con privilegi/garanzie.
    *   Source [10]: D.Lgs 14/2019, Art. 214 (Liquidazione beni vendita azienda).

3.  **Evaluate the Question against the Packet:**
    *   The question asks about "opponibilità al fisco" (opposability to tax authorities) and "solidarietà tributaria del cessionario" (tax solidarity of the assignee).
    *   I need to check if the Research Packet contains information regarding *Tax Law* (TUIR, D.P.R. 633/72, etc.) or specific provisions about tax liability transfer in business transfers (*trasferimento d'azienda*).
    *   Scanning sources:
        *   [1] CC Art. 1248 (Compensation). Civil law.
        *   [2] CC Art. 2559 (Assignment of credits). Civil law.
        *   [3] CC Art. 1264 (Effect on debtor). Civil law.
        *   [4] DPR 917/86 (TUIR - Tax Code). Text mentions "stratificazione delle riserve di utili". This is relevant to corporate tax but doesn't explicitly discuss the transfer of tax liability or solidarity in business transfers. It's a snippet about reserves.
        *   [5] CC Art. 2112 (Labor rights). Civil law.
        *   [6] CC Art. 2112 (Continuation). Civil law.
        *   [7] D.Lgs 14/2019 (Collective agreements). Labor law.
        *   [8] D.Lgs 206/2005 (Consumer credit). Consumer law.
        *   [9] CC Art. 1263 (Accessories). Civil law.
        *   [10] D.Lgs 14/2019 (Liquidation of assets). Corporate/Business law snippet.

    *   **Critical Finding:** The Research Packet does *not* contain specific articles regarding the transfer of tax liability (*trasferimento del debito tributario*) or tax solidarity in business transfers (*solidarietà tributaria*).
    *   Source [4] is from the Tax Code (DPR 917/86), but the text provided ("In caso di cessione delle partecipazioni la preesistente stratificazione delle riserve di utili si trasferisce al cessionario") refers to corporate reserves, not tax debt solidarity.
    *   There are no sources in the packet that explicitly state rules about "opponibilità al fisco" or "solidarietà tributaria del cessionario".

4.  **Formulate the Analysis (CoT):**
    *   **QUALIFICAZIONE:** The question asks about tax liability transfer and solidarity upon business assignment (*trasferimento d'azienda*). This falls under Tax Law principles regarding succession of obligations.
    *   **NORMA APPLICABILE:** I must check if any source in the packet applies. Source [4] is from TUIR (DPR 917/86), but the text provided does not support claims about tax solidarity or opposability to tax authorities regarding business transfers specifically, only reserves transfer for participations. Sources [1], [2], [3], [5], [9] are Civil Code (CC) regarding assignment of credits/debts generally, not specific tax liability succession rules.
    *   **GIURISPRUDENZA:** No case law sources in the packet.
    *   **VALUTAZIONE:** Since there is no source in the packet supporting claims about tax solidarity or opposability to tax authorities for business transfers, I cannot cite a source for these specific facts. According to the Citation Contract: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." However, the instruction says "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I make a claim about tax law not in the packet, I must use the personal reasoning prefix. But wait, the instruction also says "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Constraint Check:** The prompt says "Ragioni SOLO sui fatti nel Research Packet." and "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I state that there is no rule, or if I try to answer based on general knowledge without a source, it violates the contract.
    *   **Strategy:** I must analyze what IS in the packet regarding this topic. The packet contains Civil Code articles about assignment of credits/debts (Art 1248, 1263, 1264) and Labor/Corporate law (Art 2112). It contains a snippet from TUIR (DPR 917/86 Art. 57 text says Art 47 in title but mentions reserves).
    *   **Conclusion:** The packet does not contain the specific legal basis for tax solidarity or opposability to tax authorities regarding business transfers. I must report this gap. I cannot invent a source_id like "TUIR_ART_123". I can only use the provided IDs.
    *   **Handling the lack of info:** In the `VALUTAZIONE` step, if I need to state

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?" (What is the opposability to tax authorities of acts of business transfer and the tax solidarity of the assignee?)

2.  **Analyze the Research Packet:**
    *   Source [1]: Art. 1248 CC (Inopponibilità della compensazione). Debitore che accetta cessione non può opporre compensazione al cessionario.
    *   Source [2]: Art. 2559 CC (Crediti relativi all'azienda ceduta). Cessione crediti azienda ha effetto verso terzi dal momento iscrizione registro, anche senza notifica.
    *   Source [3]: Art. 1264 CC (Efficacia cessione riguardo al debitore ceduto). Cessione ha effetto verso debitore quando accettata o notificata. Pagamento a cedente prima notifica è valido.
    *   Source [4]: DPR 917/86, Art. 57 (actually text says Art. 47 in title but text mentions stratificazione riserve). Mentions D.Lgs 2018 n. 142 update.
    *   Source [5]: Art. 2112 CC (Mantenimento diritti lavoratori trasferimento azienda). Rapporto continua con cessionario.
    *   Source [6]: Art. 2112 CC (continuation text about identity of rights).
    *   Source [7]: D.Lgs 14/2019, Art. 212 (Collective agreements substitution).
    *   Source [8]: D.Lgs 206/2005, Art. 146 (Consumer credit acts).
    *   Source [9]: Art. 1263 CC (Accessori del credito). Credito trasferito con privilegi/garanzie.
    *   Source [10]: D.Lgs 14/2019, Art. 214 (Liquidazione beni vendita azienda).

3.  **Evaluate the Question against the Packet:**
    *   The question asks about "opponibilità al fisco" (opposability to tax authorities) and "solidarietà tributaria del cessionario" (tax solidarity of the assignee).
    *   I need to check if the Research Packet contains information regarding *Tax Law* (TUIR, D.P.R. 633/72, etc.) or specific provisions about tax liability transfer in business transfers (*trasferimento d'azienda*).
    *   Scanning sources:
        *   [1] CC Art. 1248 (Compensation). Civil law.
        *   [2] CC Art. 2559 (Assignment of credits). Civil law.
        *   [3] CC Art. 1264 (Effect on debtor). Civil law.
        *   [4] DPR 917/86 (TUIR - Tax Code). Text mentions "stratificazione delle riserve di utili". This is relevant to corporate tax but doesn't explicitly discuss the transfer of tax liability or solidarity in business transfers. It's a snippet about reserves.
        *   [5] CC Art. 2112 (Labor rights). Civil law.
        *   [6] CC Art. 2112 (Continuation). Civil law.
        *   [7] D.Lgs 14/2019 (Collective agreements). Labor law.
        *   [8] D.Lgs 206/2005 (Consumer credit). Consumer law.
        *   [9] CC Art. 1263 (Accessories). Civil law.
        *   [10] D.Lgs 14/2019 (Liquidation of assets). Corporate/Business law snippet.

    *   **Critical Finding:** The Research Packet does *not* contain specific articles regarding the transfer of tax liability (*trasferimento del debito tributario*) or tax solidarity in business transfers (*solidarietà tributaria*).
    *   Source [4] is from the Tax Code (DPR 917/86), but the text provided ("In caso di cessione delle partecipazioni la preesistente stratificazione delle riserve di utili si trasferisce al cessionario") refers to corporate reserves, not tax debt solidarity.
    *   There are no sources in the packet that explicitly state rules about "opponibilità al fisco" or "solidarietà tributaria del cessionario".

4.  **Formulate the Analysis (CoT):**
    *   **QUALIFICAZIONE:** The question asks about tax liability transfer and solidarity upon business assignment (*trasferimento d'azienda*). This falls under Tax Law principles regarding succession of obligations.
    *   **NORMA APPLICABILE:** I must check if any source in the packet applies. Source [4] is from TUIR (DPR 917/86), but the text provided does not support claims about tax solidarity or opposability to tax authorities regarding business transfers specifically, only reserves transfer for participations. Sources [1], [2], [3], [5], [9] are Civil Code (CC) regarding assignment of credits/debts generally, not specific tax liability succession rules.
    *   **GIURISPRUDENZA:** No case law sources in the packet.
    *   **VALUTAZIONE:** Since there is no source in the packet supporting claims about tax solidarity or opposability to tax authorities for business transfers, I cannot cite a source for these specific facts. According to the Citation Contract: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." However, the instruction says "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I make a claim about tax law not in the packet, I must use the personal reasoning prefix. But wait, the instruction also says "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Constraint Check:** The prompt says "Ragioni SOLO sui fatti nel Research Packet." and "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I state that there is no rule, or if I try to answer based on general knowledge without a source, it violates the contract.
    *   **Strategy:** I must analyze what IS in the packet regarding this topic. The packet contains Civil Code articles about assignment of credits/debts (Art 1248, 1263, 1264) and Labor/Corporate law (Art 2112). It contains a snippet from TUIR (DPR 917/86 Art. 57 text says Art 47 in title but mentions reserves).
    *   **Conclusion:** The packet does not contain the specific legal basis for tax solidarity or opposability to tax authorities regarding business transfers. I must report this gap. I cannot invent a source_id like "TUIR_ART_123". I can only use the provided IDs.
    *   **Handling the lack of info:** In the `VALUTAZIONE` step, if I need to state

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1293` | 1.6713 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2769` | 1.1295 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1309` | -1.5010 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art57` | -1.6456 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.8660 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.9100 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art212` | -3.4738 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art146` | -4.9637 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1308` | -5.1872 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art214` | -5.8299 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art14`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1293`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1248. (Inopponibilità della compensazione). Il debitore, se ha accettato puramente e semplicemente la cessione che il creditore ha fatta delle sue ragioni a un terzo, non può opporre al cessionario la compensazione che avrebbe potuto opporre al cedente. La ce

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2769`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2559. (Crediti relativi all'azienda ceduta). La cessione dei crediti relativi all'azienda ceduta, anche in mancanza di notifica al debitore o di sua accettazione, ha effetto, nei confronti dei terzi, dal momento dell'iscrizione del trasferimento nel registro

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1309`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1264. (Efficacia della cessione riguardo al debitore ceduto). La cessione ha effetto nei confronti del debitore ceduto quando questi l'ha accettata o quando gli è stata notificata. Tuttavia, anche prima della notificazione, il debitore che paga al cedente non

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art57`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 . 917 del 1986 . In caso di cessione delle partecipazioni la preesistente stratificazione delle riserve di utili si trasferisce al cessionario". ------------ AGGIORNAMENTO (192) Il D.Lgs. 29 novembre 2018, n. 142 , ha disposto (con l'a

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2112. (Mantenimento dei diritti dei lavoratori in caso di trasferimento d'azienda). In caso di trasferimento d'azienda, il rapporto di lavoro continua con il cessionario ed il lavoratore conserva tutti i diritti che ne derivano. Il cedente ed il cessionario s

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 , preesistente al trasferimento e che conserva nel trasferimento la propria identità a prescindere dalla tipologia negoziale o dal provvedimento sulla base del quale il trasferimento è attuato ivi compresi l'usufrutto o l'affitto di azienda. Le disposizioni del pr

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art212`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 uiti da altri contratti collettivi applicabili all'impresa del cessionario. L'effetto di sostituzione si produce esclusivamente fra contratti collettivi del medesimo livello. Ferma restando la facoltà di esercitare il recesso ai sensi della normativa in mat

**[8]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art146`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 atti di credito al consumo a fronte dei quali sia stato concesso un diritto reale di garanzia sul bene acquistato con il denaro ricevuto in prestito. 2. Le facoltà di adempiere in via anticipata o di recedere dal contratto senza penalità spettano unicamen

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1308`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1263. (Accessori del credito). Per effetto della cessione, il credito è trasferito al cessionario con i privilegi, con le garanzie personali e reali e con gli altri accessori. Il cedente non può trasferire al cessionario, senza il consenso del costituente, il

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art214`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 214 Vendita dell'azienda o di suoi rami o di beni o rapporti in blocco 1. La liquidazione dei singoli beni ai sensi delle disposizioni del presente capo è disposta quando risulta prevedibile che la vendita dell'intero complesso aziendale, di suoi rami,

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
