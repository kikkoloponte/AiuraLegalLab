# trib_004 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:11 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.8s (ret 0.3s + llm 67.4s) |

## Query

> Quali sono i presupposti per l'accertamento sintetico del reddito?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Specific Question:** "Quali sono i presupposti per l'accertamento sintetico del reddito?" (What are the prerequisites for synthetic income assessment?)
    *   **Research Packet Content:** A list of 10 sources (DPR 917/86, DLgs 218/97, DPR 600/73, RD 262/42) with specific articles and texts provided.

2.  **Analyze the Research Packet for Keywords:**
    *   I need to find information regarding "accertamento sintetico" (synthetic assessment).
    *   Scanning Source [1] (DPR 917/86 Art 39): Mentions revisioni, decorrenza variazioni. No mention of "accertamento sintetico".
    *   Scanning Source [2] (DLgs 218/97 Art 17): Mentions "Disposizioni comuni in materia di accertamento", abrogato. Mentions "accertamento con adesione". No explicit "sintetico".
    *   Scanning Source [3] (DPR 917/86 Art 204 - labeled Art 165 in text): Credit d'imposta estero. Irrelevant.
    *   Scanning Source [4] (DPR 600/73 Art 15 - labeled Art 13 in text): Tenuta di scritture contabili. Irrelevant to "sintetico".
    *   Scanning Source [5] (DPR 917/86 Art 92 - labeled Art 71 in text): Altri redditi, royalty. Irrelevant.
    *   Scanning Source [6] (DLgs 218/97 Art 12): Accertamento con adesione. Irrelevant to "sintetico".
    *   Scanning Source [7] (DPR 600/73 Art 62 - labeled Art 38 in text): Rettifica dichiarazioni. Irrelevant to "sintetico".
    *   Scanning Source [8] (RD 262/42 Art 2984 - labeled Art 2759 in text): Crediti imposte. Irrelevant.
    *   Scanning Source [9] (DPR 917/86 Art 2 - labeled Art 1 in text): Presupposto dell'imposta (possesso redditi). General, not specific to "accertamento sintetico".
    *   Scanning Source [10] (DPR 917/86 Art 10 - labeled Art 9 in text): Determinazione dei redditi e delle perdite. Irrelevant.

3.  **Evaluate Findings:**
    *   The term "accertamento sintetico" does not appear explicitly in the provided Research Packet text snippets.
    *   Source [2] mentions "Disposizioni comuni in materia di accertamento" but notes it is abrogated and talks about "accertamento con adesione".
    *   Source [9] defines general prerequisites for tax ("Presupposto dell'imposta... è il possesso di redditi").
    *   There is no specific legal text in the packet defining the prerequisites specifically for an "accertamento sintetico" (synthetic assessment). This procedure usually relates to simplified procedures where the taxpayer declares income without detailed accounting, often linked to specific thresholds or categories not explicitly detailed in these snippets.
    *   Since I cannot access external KB and must rely ONLY on the Packet, I must state that the packet does not contain specific information on "accertamento sintetico" prerequisites beyond general tax prerequisites found in Source [9].

4.  **Drafting the Analysis (CoT):**

    *   **QUALIFICAZIONE:** The user asks about prerequisites for "accertamento sintetico". I need to check if the packet defines this.
        *   Fact: The packet contains norms on general tax assessment and income determination.
        *   Source [9] defines general prerequisite for tax (possession of income).
        *   Source [2] mentions general provisions on assessment but notes abrogation regarding specific clauses.
        *   Claim: The provided text does not explicitly define the "accertamento sintetico" procedure prerequisites, only general tax prerequisites exist in Source [9].

    *   **NORMA APPLICABILE:** Which norms apply?
        *   Source [9] (DPR 917/86 Art. 1) defines the prerequisite for income tax generally.
        *   Source [2] (DLgs 218/97 Art. 17) mentions general provisions on assessment but is abrogated regarding specific clauses.
        *   Claim: DPR 917/86 Art. 1 sets the general prerequisite for income tax liability.

    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza). It only contains normative texts (DPR, DLgs, RD).
        *   Claim: No jurisprudential sources available in the Packet to contrast or support specific interpretations of "sintetico".

    *   **VALUTAZIONE:** Solidity of the answer based on packet.
        *   Since the term is not found, confidence regarding specific prerequisites for "accertamento sintetico" is LOW based *only* on this packet. I must use `ungrounded_reasoning` if I make a claim about what it usually implies without source, but the instruction says: "If you don't have the source → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
        *   However, for the JSON structure, I need to fill `content`. If I state that info is missing, I should reflect that.
        *   Wait, the instruction says: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
        *   So if I say "The packet does not contain...", that's a meta-statement about the packet content (which is fact). But for legal claims about the law itself, I need sources.
        *   Since there are no sources defining "accertamento sintetico", I must indicate this gap or rely on general tax prerequisites available.
        *   Actually, looking closely at Source [2], it mentions "Disposizioni comuni in materia di accertamento" but says it's abrogated. It doesn't define "sintetico".
        *   Conclusion: The packet does not support a specific answer for "accertamento sintetico". I must report this limitation.

    *   **GAP ANALYSIS:** What is missing?
        *   Specific definition of "accertamento sintetico" and its prerequisites are absent from the provided sources.

5.  **Constructing JSON:**
    *   Must follow schema exactly.
    *   `analysis_sections` array with steps: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   Citations must use `source_id`.
    *   If no source for a claim (like the missing info), I should probably not make that specific legal claim as fact without a source

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Specific Question:** "Quali sono i presupposti per l'accertamento sintetico del reddito?" (What are the prerequisites for synthetic income assessment?)
    *   **Research Packet Content:** A list of 10 sources (DPR 917/86, DLgs 218/97, DPR 600/73, RD 262/42) with specific articles and texts provided.

2.  **Analyze the Research Packet for Keywords:**
    *   I need to find information regarding "accertamento sintetico" (synthetic assessment).
    *   Scanning Source [1] (DPR 917/86 Art 39): Mentions revisioni, decorrenza variazioni. No mention of "accertamento sintetico".
    *   Scanning Source [2] (DLgs 218/97 Art 17): Mentions "Disposizioni comuni in materia di accertamento", abrogato. Mentions "accertamento con adesione". No explicit "sintetico".
    *   Scanning Source [3] (DPR 917/86 Art 204 - labeled Art 165 in text): Credit d'imposta estero. Irrelevant.
    *   Scanning Source [4] (DPR 600/73 Art 15 - labeled Art 13 in text): Tenuta di scritture contabili. Irrelevant to "sintetico".
    *   Scanning Source [5] (DPR 917/86 Art 92 - labeled Art 71 in text): Altri redditi, royalty. Irrelevant.
    *   Scanning Source [6] (DLgs 218/97 Art 12): Accertamento con adesione. Irrelevant to "sintetico".
    *   Scanning Source [7] (DPR 600/73 Art 62 - labeled Art 38 in text): Rettifica dichiarazioni. Irrelevant to "sintetico".
    *   Scanning Source [8] (RD 262/42 Art 2984 - labeled Art 2759 in text): Crediti imposte. Irrelevant.
    *   Scanning Source [9] (DPR 917/86 Art 2 - labeled Art 1 in text): Presupposto dell'imposta (possesso redditi). General, not specific to "accertamento sintetico".
    *   Scanning Source [10] (DPR 917/86 Art 10 - labeled Art 9 in text): Determinazione dei redditi e delle perdite. Irrelevant.

3.  **Evaluate Findings:**
    *   The term "accertamento sintetico" does not appear explicitly in the provided Research Packet text snippets.
    *   Source [2] mentions "Disposizioni comuni in materia di accertamento" but notes it is abrogated and talks about "accertamento con adesione".
    *   Source [9] defines general prerequisites for tax ("Presupposto dell'imposta... è il possesso di redditi").
    *   There is no specific legal text in the packet defining the prerequisites specifically for an "accertamento sintetico" (synthetic assessment). This procedure usually relates to simplified procedures where the taxpayer declares income without detailed accounting, often linked to specific thresholds or categories not explicitly detailed in these snippets.
    *   Since I cannot access external KB and must rely ONLY on the Packet, I must state that the packet does not contain specific information on "accertamento sintetico" prerequisites beyond general tax prerequisites found in Source [9].

4.  **Drafting the Analysis (CoT):**

    *   **QUALIFICAZIONE:** The user asks about prerequisites for "accertamento sintetico". I need to check if the packet defines this.
        *   Fact: The packet contains norms on general tax assessment and income determination.
        *   Source [9] defines general prerequisite for tax (possession of income).
        *   Source [2] mentions general provisions on assessment but notes abrogation regarding specific clauses.
        *   Claim: The provided text does not explicitly define the "accertamento sintetico" procedure prerequisites, only general tax prerequisites exist in Source [9].

    *   **NORMA APPLICABILE:** Which norms apply?
        *   Source [9] (DPR 917/86 Art. 1) defines the prerequisite for income tax generally.
        *   Source [2] (DLgs 218/97 Art. 17) mentions general provisions on assessment but is abrogated regarding specific clauses.
        *   Claim: DPR 917/86 Art. 1 sets the general prerequisite for income tax liability.

    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza). It only contains normative texts (DPR, DLgs, RD).
        *   Claim: No jurisprudential sources available in the Packet to contrast or support specific interpretations of "sintetico".

    *   **VALUTAZIONE:** Solidity of the answer based on packet.
        *   Since the term is not found, confidence regarding specific prerequisites for "accertamento sintetico" is LOW based *only* on this packet. I must use `ungrounded_reasoning` if I make a claim about what it usually implies without source, but the instruction says: "If you don't have the source → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
        *   However, for the JSON structure, I need to fill `content`. If I state that info is missing, I should reflect that.
        *   Wait, the instruction says: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
        *   So if I say "The packet does not contain...", that's a meta-statement about the packet content (which is fact). But for legal claims about the law itself, I need sources.
        *   Since there are no sources defining "accertamento sintetico", I must indicate this gap or rely on general tax prerequisites available.
        *   Actually, looking closely at Source [2], it mentions "Disposizioni comuni in materia di accertamento" but says it's abrogated. It doesn't define "sintetico".
        *   Conclusion: The packet does not support a specific answer for "accertamento sintetico". I must report this limitation.

    *   **GAP ANALYSIS:** What is missing?
        *   Specific definition of "accertamento sintetico" and its prerequisites are absent from the provided sources.

5.  **Constructing JSON:**
    *   Must follow schema exactly.
    *   `analysis_sections` array with steps: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   Citations must use `source_id`.
    *   If no source for a claim (like the missing info), I should probably not make that specific legal claim as fact without a source

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49` | 4.3310 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | 3.6035 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204` | 2.9212 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15` | 2.5928 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art92` | 2.5850 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 2.4579 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art62` | 1.8095 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2984` | 1.7977 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art2` | 1.4035 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art10` | 1.1734 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 39 ((Decorrenza delle variazioni 1. Le variazioni del reddito risultanti dalle revisioni effettuate a norma dell'articolo 35 hanno effetto dal 1 gennaio dell'anno successivo al triennio in cui si sono verificati i presupposti per

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art204`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 165 Credito d'imposta per i redditi prodotti all'estero 1. Se alla formazione del reddito complessivo concorrono redditi prodotti all'estero, le imposte ivi pagate a titolo definitivo su tali redditi sono ammesse in detrazione dal

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Ai fini dell'accertamento sono obbligati alla tenuta di scritture contabili, secondo le disposizioni di questo titolo: a) le società soggette all'imposta sul reddito delle persone giuridiche; b) gli enti pubblici e privati diversi dal

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art92`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 71 Altri redditi 1. I redditi di cui alla lettera g) del comma 1 dell'articolo 81 costituiscono reddito per l'ammontare percepito nel periodo di imposta, ridotto del 25 per cento se i diritti dalla cui utilizzazione derivano sono

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art62`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 L'ufficio delle imposte procede alla rettifica delle dichiarazioni presentate dalle persone fisiche quando il reddito complessivo dichiarato risulta inferiore a quello effettivo o non sussistono o non spettano, in tutto o in parte, le

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2984`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2759. ((Crediti per le imposte sul reddito.)) ((I crediti dello Stato per l'imposta sul reddito delle persone fisiche, sul reddito delle persone giuridiche e per l'imposta locale sui redditi, dovuta per i due anni anteriori a quello in cui si procede, hanno p

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art2`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 1 ((Presupposto dell'imposta )) (( 1. Presupposto dell'imposta sul reddito delle persone fisiche è il possesso di redditi in denaro o in natura rientranti nelle categorie indicate nell'articolo 6. ))

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art10`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 9 Determinazione dei redditi e delle perdite 1. I redditi e le perdite che concorrono a formare il reddito complessivo sono determinati distintamente per ciascuna categoria, secondo le disposizioni dei successivi capi, in base al

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
