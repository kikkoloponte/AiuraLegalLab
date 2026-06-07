# trib_004 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:33 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 66.8s (ret 0.1s + llm 66.5s) |

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
    *   **Research Packet Content:** A list of 10 sources (DPR, DLgs, R.D.) with specific articles and texts.

2.  **Analyze the Research Packet for Keywords:**
    *   I need to find information regarding "accertamento sintetico" (synthetic assessment) or its prerequisites ("presupposti").
    *   Source [1]: DPR 917/86, Art. 39 (Decorrenza delle variazioni). Mentions revisions under Art. 35. No mention of "sintetico".
    *   Source [2]: DLgs 218/97, Art. 17 (Disposizioni comuni in materia di accertamento), abrogated text about net income definition upon non-appeal. Mentions "accertamento con adesione" (adhesion assessment). No explicit mention of "sintetico".
    *   Source [3]: DPR 600/73, Art. 13 (Obbligati alla tenuta di scritture contabili). Lists companies, public/private entities. This relates to bookkeeping obligations, not specifically the prerequisites for a specific type of assessment called "sintetico".
    *   Source [4]: DLgs 218/97, Art. 12 (Istanza del contribuente). Mentions adhesion assessment ("accertamento con adesione"). No mention of "sintetico".
    *   Source [5]: R.D. 262/42, Art. 2759 (Crediti per le imposte sul reddito). Statute of limitations for tax credits. Not about prerequisites for assessment type.
    *   Source [6]: DLgs 218/97, Art. 6 (Impugnazione dell'atto...). Mentions suspension terms. No mention of "sintetico".
    *   Source [7]: DLgs 218/97, Art. 12 (Istanza del contribuente). Pre-litigation request for non-contradictory acts. No mention of "sintetico".
    *   Source [8]: DPR 600/73, Art. 67 (Non doppia imposizione). No mention of "sintetico".
    *   Source [9]: DPR 600/73, Art. 41-bis (Accertamento parziale). Mentions partial assessment. Not explicitly "sintetico".
    *   Source [10]: R.D. 1443/40, Art. 121 (Libertà di forme). Procedural forms. No mention of "sintetico".

3.  **Evaluate Findings:**
    *   The term "accertamento sintetico" is NOT explicitly present in the provided Research Packet text.
    *   Source [9] mentions "Accertamento parziale" (partial assessment).
    *   Source [2], [4], [7] mention "accertamento con adesione" (adhesion assessment) or general assessment rules.
    *   There is no source in the packet that explicitly defines the prerequisites for an "accertamento sintetico".
    *   According to the Citation Contract: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I cannot find a source, I must use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (but wait, the instruction says "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione.").
    *   However, the Schema CoT requires specific steps. If I cannot find information in the packet to answer the question factually based on sources, I must acknowledge the gap or state that the packet does not contain this info.
    *   The instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   If the information is missing from the packet, I cannot invent it. I must report what is available or state the limitation.
    *   Looking closely at Source [9] (DPR 600/73 Art. 41-bis): It mentions "Accertamento parziale". Sometimes "sintetico" and "parziale" are confused in common parlance, but legally they might differ. However, I must stick to the text.
    *   Looking at Source [2] (DLgs 218/97 Art. 17): Mentions "accertamento con adesione".
    *   There is NO source mentioning "accertamento sintetico" specifically in the provided text snippets.
    *   Therefore, I cannot cite a source for the prerequisites of "sintetico" assessment because they are not in the packet.
    *   I must follow the Citation Contract: If no source -> `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". But wait, the instruction says "Ragioni SOLO sui fatti nel Research Packet." This implies if it's not there, I can't assert facts about it.
    *   However, the task is to answer the question based on the packet. If the packet doesn't have the answer, I should state that in the analysis (GAP ANALYSIS).
    *   In the `analysis_sections`, for steps like QUALIFICAZIONE or NORMA APPLICABILE, if there are no sources matching "sintetico", I might need to use VALUTAZIONE PERSONALE for the reasoning about what is missing or clarify based on available text (e.g., relating it to partial assessment if that's the closest match, but strictly speaking, I shouldn't conflate them without a source).
    *   Actually, looking at the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to claims. If I claim there are prerequisites X, Y, Z and they aren't in the packet, I can't cite them.
    *   Best approach: Acknowledge that the specific term "accertamento sintetico" is not explicitly detailed in the provided sources, but related concepts (partial assessment, adhesion) exist. Or simply state the gap.
    *   Wait, Source [9] title says "Accertamento parziale". Text starts "Senza pregiudizio dell'ulteriore azione accertatrice...". It doesn't define prerequisites for "sintetico".
    *   Since I cannot find specific info on "accertamento sintetico" in the packet, I must be honest about the limitation. The `overall_confidence` should likely be LOW or MEDIUM depending on how much I can infer from related terms (like Art 41-bis). But strictly, if the term isn't there, confidence is low regarding that specific term.
    *   However, usually in these tasks, if the info isn't there, I should state it's not found or use personal valuation for the conclusion about

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
    *   **Research Packet Content:** A list of 10 sources (DPR, DLgs, R.D.) with specific articles and texts.

2.  **Analyze the Research Packet for Keywords:**
    *   I need to find information regarding "accertamento sintetico" (synthetic assessment) or its prerequisites ("presupposti").
    *   Source [1]: DPR 917/86, Art. 39 (Decorrenza delle variazioni). Mentions revisions under Art. 35. No mention of "sintetico".
    *   Source [2]: DLgs 218/97, Art. 17 (Disposizioni comuni in materia di accertamento), abrogated text about net income definition upon non-appeal. Mentions "accertamento con adesione" (adhesion assessment). No explicit mention of "sintetico".
    *   Source [3]: DPR 600/73, Art. 13 (Obbligati alla tenuta di scritture contabili). Lists companies, public/private entities. This relates to bookkeeping obligations, not specifically the prerequisites for a specific type of assessment called "sintetico".
    *   Source [4]: DLgs 218/97, Art. 12 (Istanza del contribuente). Mentions adhesion assessment ("accertamento con adesione"). No mention of "sintetico".
    *   Source [5]: R.D. 262/42, Art. 2759 (Crediti per le imposte sul reddito). Statute of limitations for tax credits. Not about prerequisites for assessment type.
    *   Source [6]: DLgs 218/97, Art. 6 (Impugnazione dell'atto...). Mentions suspension terms. No mention of "sintetico".
    *   Source [7]: DLgs 218/97, Art. 12 (Istanza del contribuente). Pre-litigation request for non-contradictory acts. No mention of "sintetico".
    *   Source [8]: DPR 600/73, Art. 67 (Non doppia imposizione). No mention of "sintetico".
    *   Source [9]: DPR 600/73, Art. 41-bis (Accertamento parziale). Mentions partial assessment. Not explicitly "sintetico".
    *   Source [10]: R.D. 1443/40, Art. 121 (Libertà di forme). Procedural forms. No mention of "sintetico".

3.  **Evaluate Findings:**
    *   The term "accertamento sintetico" is NOT explicitly present in the provided Research Packet text.
    *   Source [9] mentions "Accertamento parziale" (partial assessment).
    *   Source [2], [4], [7] mention "accertamento con adesione" (adhesion assessment) or general assessment rules.
    *   There is no source in the packet that explicitly defines the prerequisites for an "accertamento sintetico".
    *   According to the Citation Contract: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I cannot find a source, I must use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (but wait, the instruction says "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione.").
    *   However, the Schema CoT requires specific steps. If I cannot find information in the packet to answer the question factually based on sources, I must acknowledge the gap or state that the packet does not contain this info.
    *   The instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   If the information is missing from the packet, I cannot invent it. I must report what is available or state the limitation.
    *   Looking closely at Source [9] (DPR 600/73 Art. 41-bis): It mentions "Accertamento parziale". Sometimes "sintetico" and "parziale" are confused in common parlance, but legally they might differ. However, I must stick to the text.
    *   Looking at Source [2] (DLgs 218/97 Art. 17): Mentions "accertamento con adesione".
    *   There is NO source mentioning "accertamento sintetico" specifically in the provided text snippets.
    *   Therefore, I cannot cite a source for the prerequisites of "sintetico" assessment because they are not in the packet.
    *   I must follow the Citation Contract: If no source -> `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". But wait, the instruction says "Ragioni SOLO sui fatti nel Research Packet." This implies if it's not there, I can't assert facts about it.
    *   However, the task is to answer the question based on the packet. If the packet doesn't have the answer, I should state that in the analysis (GAP ANALYSIS).
    *   In the `analysis_sections`, for steps like QUALIFICAZIONE or NORMA APPLICABILE, if there are no sources matching "sintetico", I might need to use VALUTAZIONE PERSONALE for the reasoning about what is missing or clarify based on available text (e.g., relating it to partial assessment if that's the closest match, but strictly speaking, I shouldn't conflate them without a source).
    *   Actually, looking at the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to claims. If I claim there are prerequisites X, Y, Z and they aren't in the packet, I can't cite them.
    *   Best approach: Acknowledge that the specific term "accertamento sintetico" is not explicitly detailed in the provided sources, but related concepts (partial assessment, adhesion) exist. Or simply state the gap.
    *   Wait, Source [9] title says "Accertamento parziale". Text starts "Senza pregiudizio dell'ulteriore azione accertatrice...". It doesn't define prerequisites for "sintetico".
    *   Since I cannot find specific info on "accertamento sintetico" in the packet, I must be honest about the limitation. The `overall_confidence` should likely be LOW or MEDIUM depending on how much I can infer from related terms (like Art 41-bis). But strictly, if the term isn't there, confidence is low regarding that specific term.
    *   However, usually in these tasks, if the info isn't there, I should state it's not found or use personal valuation for the conclusion about

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49` | 4.3310 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | 3.6035 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15` | 2.5928 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 2.4579 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2984` | 1.7977 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | 1.1299 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 0.8101 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art97` | -0.2312 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art68` | -0.5679 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art131` | -1.1193 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art49`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 39 ((Decorrenza delle variazioni 1. Le variazioni del reddito risultanti dalle revisioni effettuate a norma dell'articolo 35 hanno effetto dal 1 gennaio dell'anno successivo al triennio in cui si sono verificati i presupposti per

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art15`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Ai fini dell'accertamento sono obbligati alla tenuta di scritture contabili, secondo le disposizioni di questo titolo: a) le società soggette all'imposta sul reddito delle persone giuridiche; b) gli enti pubblici e privati diversi dal

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2984`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2759. ((Crediti per le imposte sul reddito.)) ((I crediti dello Stato per l'imposta sul reddito delle persone fisiche, sul reddito delle persone giuridiche e per l'imposta locale sui redditi, dovuta per i due anni anteriori a quello in cui si procede, hanno p

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  qualora ne ricorrano i presupposti, successivamente alla scadenza del termine di sospensione. L'impugnazione dell'atto comporta rinuncia all'istanza. (23) 4. Entro quindici giorni dalla ricezione dell'istanza di cui ai commi 2 e 2-bis, l'ufficio, anche tel

**[7]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art97`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 La stessa imposta non può essere applicata più volte in dipendenza dello stesso presupposto, neppure nei confronti di soggetti diversi. ((L'imposta personale pagata dal soggetto erogante a titolo definitivo a seguito di accertamento è

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art68`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 41-bis (Accertamento parziale) 1. Senza pregiudizio dell'ulteriore azione accertatrice nei termini stabiliti dall'articolo 43, i competenti uffici dell'Agenzia delle entrate, qualora ((dalle attività istruttorie di cui all'artico

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art131`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 121. (Libertà di forme). Chiarezza e sinteticità degli atti. (171) ((173)) Gli atti del processo, per i quali la legge non richiede forme determinate, possono essere compiuti nella forma più idonea al raggiungimento del loro scopo. Tutti gli atti del proce

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
