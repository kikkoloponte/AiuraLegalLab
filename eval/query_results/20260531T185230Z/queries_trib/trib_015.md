# trib_015 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:45 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 68.1s (ret 0.1s + llm 67.8s) |

## Query

> Qual è il regime IVA delle prestazioni di servizi intracomunitarie?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, RD 262/42, DLgs 33/13, etc.).
    *   **Question:** "Qual è il regime IVA delle prestazioni di servizi intracomunitarie?" (What is the VAT regime for intra-community services?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917/86 Art. 145 (Regime forfetario, cessione servizi). Text mentions "canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi." and limits extending year by year.
    *   Source [2]: RD 262/42 Art. 1677 (Prestazione continuativa o periodica di servizi). Civil Code rules on service contracts.
    *   Source [3]: RD 262/42 Art. 2223 (Prestazione della materia). Civil Code rules on supply of materials vs services.
    *   Source [4]: DPR 917/86 Art. 51 (Taxation period, goods/services transferred). Text mentions "tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia." and values determination.
    *   Source [5]: DLgs 33/13 Art. 41 (Transparency of national health service). Unrelated to VAT intra-community services generally.
    *   Source [6]: DPR 917/86 Art. 145 (Regime forfetario degli enti non commerciali). Mentions associations, etc.
    *   Source [7]: DLgs 81/15 Art. 13 (Intermittent work contract). Unrelated to VAT regime.
    *   Source [8]: DPR 917/86 Art. 51 (Modifications from L. 24 July 2008, n. 126; c) catering services...). Mentions "somministrazioni di vitto".
    *   Source [9]: DPR 633/72 Art. 17-bis (Online advertising purchase). Unrelated to intra-community services regime specifically.
    *   Source [10]: DLgs 81/15 Art. 52 (Exclusions from provisions, occasional performances...).

    **Critical Observation:** The Research Packet provided does *not* contain specific information about the VAT regime for *intra-community services* (B2C or B2B reverse charge mechanisms, place of supply rules under EU Directive 2008/8/EC or similar). The sources are mostly Italian domestic tax law (DPR 917/86 - TUIR), Civil Code contracts, and specific sectoral laws. None explicitly define the "regime IVA delle prestazioni di servizi intracomunitarie" (e.g., reverse charge, place of supply rules for services to non-taxable persons vs taxable persons).

    **Constraint Check:** I must reason ONLY on facts in the Research Packet. If the packet doesn't have the answer, I cannot invent it. I must state what is available or note the gap.
    However, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    And: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id present in the Packet).

    If I answer based on general knowledge about EU VAT rules (e.g., reverse charge), I violate the citation contract because there is no `source_id` for that fact in the packet.
    Therefore, I must analyze what *is* in the packet regarding services and tax, acknowledge the limitation, or state that the specific regime isn't covered by this packet while citing relevant domestic provisions found (like Art 51 DPR 917/86 regarding taxation period).

    Actually, looking closely at Source [4] and [1]: They discuss DPR 917/86 (TUIR - Testo Unico delle Imposte sui Redditi) which is Income Tax law, not VAT law (IVA is governed by DPR 633/72).
    Source [9] cites DPR 633/72 Art. 17-bis but about online advertising purchase.
    None of the sources explicitly define the "regime IVA delle prestazioni di servizi intracomunitarie".

    **Strategy:** I must follow the CoT schema. Since the packet lacks specific info on *intra-community services VAT regime*, I cannot make a factual claim with a source_id about that specific rule.
    However, I can analyze what sources *do* say about services (DPR 917/86 Art 51, RD 262/42).
    But the question asks specifically for the VAT regime of intra-community services.
    If I answer "The packet does not contain this information", that is a valid analysis based on the packet content.
    However, usually in these tasks, if the info isn't there, I should highlight the GAP.

    Let's draft the JSON structure.
    Step 1: QUALIFICAZIONE - Identify the legal nature of services and tax context found in packet (DPR 917/86, RD 262).
    Step 2: NORMA APPLICABILE - Cite relevant articles from packet regarding services taxation (e.g., DPR 917/86 Art. 51 for timing, RD 262 for contract nature). Note that specific EU VAT rules are not in the packet.
    Step 3: GIURISPRUDENZA - No jurisprudence sources in packet.
    Step 4: VALUTAZIONE - Assess confidence based on available text (LOW because packet doesn't cover intra-community specifics). Use "VALUTAZIONE PERSONALE:" prefix if no source for the conclusion about the missing info.
    Step 5: GAP ANALYSIS - Explicitly state that DPR 633/72 rules on intra-community services are not in the packet.

    Wait, I need to check if Source [9] (DPR 633/72) implies anything. It's about online advertising purchase obligation. Not general VAT regime for intra-community services.
    So, strictly adhering to "Reason ONLY on facts in the Research Packet", I cannot state the actual EU VAT rules (like Art 145 of Directive 2008/8). I must report what is in the packet or lack thereof.

    Actually, looking at the instruction: "Ragioni SOLO sui fatti nel Research Packet."
    If I say "The regime is reverse charge", that fact has no source_id in the packet. That violates the citation contract.
    So I must conclude based on what IS there.
    The most honest analysis is to state that the provided packet contains provisions on services (RD 262, DPR 917) but does not explicitly detail the specific VAT regime for intra-community services in the text provided.

    Let's refine the JSON content to reflect this limitation while using valid citations for what *is* there (definitions of services).

    **Plan:**
    1.  QUALIFICAZIONE: Define "prestazioni di servizi" based on

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, RD 262/42, DLgs 33/13, etc.).
    *   **Question:** "Qual è il regime IVA delle prestazioni di servizi intracomunitarie?" (What is the VAT regime for intra-community services?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917/86 Art. 145 (Regime forfetario, cessione servizi). Text mentions "canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi." and limits extending year by year.
    *   Source [2]: RD 262/42 Art. 1677 (Prestazione continuativa o periodica di servizi). Civil Code rules on service contracts.
    *   Source [3]: RD 262/42 Art. 2223 (Prestazione della materia). Civil Code rules on supply of materials vs services.
    *   Source [4]: DPR 917/86 Art. 51 (Taxation period, goods/services transferred). Text mentions "tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia." and values determination.
    *   Source [5]: DLgs 33/13 Art. 41 (Transparency of national health service). Unrelated to VAT intra-community services generally.
    *   Source [6]: DPR 917/86 Art. 145 (Regime forfetario degli enti non commerciali). Mentions associations, etc.
    *   Source [7]: DLgs 81/15 Art. 13 (Intermittent work contract). Unrelated to VAT regime.
    *   Source [8]: DPR 917/86 Art. 51 (Modifications from L. 24 July 2008, n. 126; c) catering services...). Mentions "somministrazioni di vitto".
    *   Source [9]: DPR 633/72 Art. 17-bis (Online advertising purchase). Unrelated to intra-community services regime specifically.
    *   Source [10]: DLgs 81/15 Art. 52 (Exclusions from provisions, occasional performances...).

    **Critical Observation:** The Research Packet provided does *not* contain specific information about the VAT regime for *intra-community services* (B2C or B2B reverse charge mechanisms, place of supply rules under EU Directive 2008/8/EC or similar). The sources are mostly Italian domestic tax law (DPR 917/86 - TUIR), Civil Code contracts, and specific sectoral laws. None explicitly define the "regime IVA delle prestazioni di servizi intracomunitarie" (e.g., reverse charge, place of supply rules for services to non-taxable persons vs taxable persons).

    **Constraint Check:** I must reason ONLY on facts in the Research Packet. If the packet doesn't have the answer, I cannot invent it. I must state what is available or note the gap.
    However, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    And: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id present in the Packet).

    If I answer based on general knowledge about EU VAT rules (e.g., reverse charge), I violate the citation contract because there is no `source_id` for that fact in the packet.
    Therefore, I must analyze what *is* in the packet regarding services and tax, acknowledge the limitation, or state that the specific regime isn't covered by this packet while citing relevant domestic provisions found (like Art 51 DPR 917/86 regarding taxation period).

    Actually, looking closely at Source [4] and [1]: They discuss DPR 917/86 (TUIR - Testo Unico delle Imposte sui Redditi) which is Income Tax law, not VAT law (IVA is governed by DPR 633/72).
    Source [9] cites DPR 633/72 Art. 17-bis but about online advertising purchase.
    None of the sources explicitly define the "regime IVA delle prestazioni di servizi intracomunitarie".

    **Strategy:** I must follow the CoT schema. Since the packet lacks specific info on *intra-community services VAT regime*, I cannot make a factual claim with a source_id about that specific rule.
    However, I can analyze what sources *do* say about services (DPR 917/86 Art 51, RD 262/42).
    But the question asks specifically for the VAT regime of intra-community services.
    If I answer "The packet does not contain this information", that is a valid analysis based on the packet content.
    However, usually in these tasks, if the info isn't there, I should highlight the GAP.

    Let's draft the JSON structure.
    Step 1: QUALIFICAZIONE - Identify the legal nature of services and tax context found in packet (DPR 917/86, RD 262).
    Step 2: NORMA APPLICABILE - Cite relevant articles from packet regarding services taxation (e.g., DPR 917/86 Art. 51 for timing, RD 262 for contract nature). Note that specific EU VAT rules are not in the packet.
    Step 3: GIURISPRUDENZA - No jurisprudence sources in packet.
    Step 4: VALUTAZIONE - Assess confidence based on available text (LOW because packet doesn't cover intra-community specifics). Use "VALUTAZIONE PERSONALE:" prefix if no source for the conclusion about the missing info.
    Step 5: GAP ANALYSIS - Explicitly state that DPR 633/72 rules on intra-community services are not in the packet.

    Wait, I need to check if Source [9] (DPR 633/72) implies anything. It's about online advertising purchase obligation. Not general VAT regime for intra-community services.
    So, strictly adhering to "Reason ONLY on facts in the Research Packet", I cannot state the actual EU VAT rules (like Art 145 of Directive 2008/8). I must report what is in the packet or lack thereof.

    Actually, looking at the instruction: "Ragioni SOLO sui fatti nel Research Packet."
    If I say "The regime is reverse charge", that fact has no source_id in the packet. That violates the citation contract.
    So I must conclude based on what IS there.
    The most honest analysis is to state that the provided packet contains provisions on services (RD 262, DPR 917) but does not explicitly detail the specific VAT regime for intra-community services in the text provided.

    Let's refine the JSON content to reflect this limitation while using valid citations for what *is* there (definitions of services).

    **Plan:**
    1.  QUALIFICAZIONE: Define "prestazioni di servizi" based on

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | 5.4400 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1735` | 2.0740 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2264` | -0.8574 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -1.4138 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41` | -1.8904 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | -2.5758 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13` | -2.7596 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -3.1340 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art30` | -4.6296 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art52` | -5.3578 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi. 3. Il regime forfetario previsto nel presente articolo si estende di anno in anno qualora i limiti indicati al comma 1 non ven

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1735`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1677. (Prestazione continuativa o periodica di servizi). Se l'appalto ha per oggetto prestazioni continuative o periodiche di servizi, si osservano, in quanto compatibili, le norme di questo capo e quelle relative al contratto di somministrazione.

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2264`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2223. (Prestazione della materia). Le disposizioni di questo capo si osservano anche se la materia è fornita dal prestatore d'opera, purché le parti non abbiano avuto prevalentemente in considerazione la materia, nel qual caso si applicano le norme sulla vend

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia. (126) 3. Ai fini della determinazione in denaro dei valori di cui al comma 1, compresi quelli dei beni ceduti e dei servizi prestati al co

**[5]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 Trasparenza del servizio sanitario nazionale 1. Le amministrazioni e gli enti del servizio sanitario nazionale, dei servizi sanitari regionali, ivi comprese le aziende sanitarie territoriali ed ospedaliere, le agenzie e gli altri enti ed organismi pub

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 145 ((Regime forfetario degli enti non commerciali )) (( 1. Fatto salvo quanto previsto, per le associazioni sportive dilettantistiche, dalla legge 16 dicembre 1991, n. 398 , e, per le associazioni senza scopo di lucro e per le pr

**[7]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 Art. 13 Definizione e casi di ricorso al lavoro intermittente 1. Il contratto di lavoro intermittente è il contratto, anche a tempo determinato, mediante il quale un lavoratore si pone a disposizione di un datore di lavoro che ne può utilizzare la prestazion

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  MODIFICAZIONI DALLA L. 24 LUGLIO 2008, N. 126 ; c) le somministrazioni di vitto da parte del datore di lavoro nonché quelle in mense organizzate direttamente dal datore di lavoro o gestite da terzi; le prestazioni sostitutive delle so

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art30`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 17-bis (( (Acquisto di pubblicità on line) )) (( 1. I soggetti passivi che intendano acquistare servizi di pubblicità e link sponsorizzati on line, anche attraverso centri media e operatori terzi, sono obbligati ad acquistarli da s

**[10]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art52`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 , che possono essere individuati dai contratti collettivi stipulati dalle organizzazioni sindacali comparativamente più rappresentative sul piano nazionale. 2. Dalla disposizione di cui al comma 1 sono escluse le prestazioni occasionali, intendendosi per tal

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
