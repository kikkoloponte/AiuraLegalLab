# trib_002 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:31 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 65.1s (ret 0.2s + llm 64.8s) |

## Query

> Qual è il termine di decadenza per la notifica degli avvisi di accertamento ai fini IRPEF?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Qual è il termine di decadenza per la notifica degli avvisi di accertamento ai fini IRPEF?" (What is the statute of limitations for notification of assessment notices for income tax purposes?)

2.  **Analyze the Research Packet:**
    *   [1] DPR 600/1973, Art. 43: "Gli avvisi di accertamento devono essere notificati, a pena di decadenza, entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione." (Assessment notices must be notified within the 5th year following the declaration submission).
    *   [2] DPR 633/1972, Art. 57: Similar text regarding VAT ("avvisi relativi alle rettifiche e agli accertamenti..."). Not directly IRPEF but related context.
    *   [3] DLgs 218/1997, Art. 12: Procedural aspects (preliminary hearing).
    *   [4] DLgs 218/1997, Art. 11: Initiation of procedure.
    *   [5] DPR 600/1973, Art. 43 (duplicate text in packet): Mentions "decadenza per l'accertamento di cui all'articolo 43 del decreto...".
    *   [6] RD 1398/1930, Art. 14: General rules on time computation (calendar).
    *   [7] DLgs 218/1997, Art. 6: Suspension of terms.
    *   [8] DPR 600/1973, Art. 53 (actually text seems to be about third parties): Mentions "Art. 43 del decreto...".
    *   [9] DLgs 14/2019, Art. 88: Consolidation procedures.
    *   [10] DPR 917/1986, Art. 152 (actually text says Art. 119): Conditions for option effectiveness.

3.  **Drafting the Analysis (CoT):**

    *   **Step 1: QUALIFICAZIONE**
        *   Fact: The question asks about IRPEF assessment notice notification deadline.
        *   Source: [1] DPR 600/1973 is the specific tax code for income tax (IRPEF). Art. 43 deals with assessment deadlines.
        *   Claim: Assessment notices must be notified within a specific period to avoid lapse of right (decadenza).
        *   Citation: [1] DPR 600/1973, Art. 43.

    *   **Step 2: NORMA APPLICABILE**
        *   Fact: The specific text defines the deadline.
        *   Claim: "entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione".
        *   Citation: [1] DPR 600/1973, Art. 43.

    *   **Step 3: GIURISPRUDENZA**
        *   Fact Check: The packet does not contain any case law (Giurisprudenza) or court rulings. It only contains legislative texts (DPR, DLgs, RD).
        *   Constraint: I cannot invent sources. If there is no jurisprudence in the packet, I must state that based on the provided text.
        *   Action: Since the instruction says "Reason ONLY on facts in the Research Packet", and there are no case law sources in the packet, I cannot cite a source for jurisprudence if none exists. However, the schema requires this step. I will note the absence of specific jurisprudence in the provided text or rely on the statutory interpretation found in the text itself regarding the "decadenza".
        *   Wait, looking at the instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If there is no jurisprudence in the packet, I cannot cite one. I should probably state that the provided packet focuses on statutory provisions rather than case law for this specific point, or simply leave citations empty if no factual claim about jurisprudence can be made from the text.
        *   Better approach: Acknowledge the statutory rule is the primary source here. If I need to fill the step, I will state that the packet does not provide specific jurisprudential sources regarding this deadline, only legislative ones. But strictly speaking, if I claim "There is no jurisprudence", I can't cite a source for that absence unless there's a meta-source (there isn't).
        *   Correction: The instruction says "Reason ONLY on facts in the Research Packet". If the packet doesn't have jurisprudence, I cannot fabricate one. I will state that the analysis relies on the legislative text provided.
        *   Actually, looking at the JSON schema example, `citations` is a list. It can be empty if no citations are needed for that specific claim (e.g., if it's purely procedural based on the previous step). However, to follow "Every factual claim MUST have a source_id", I should avoid making claims about jurisprudence without sources.
        *   Decision: In this step, I will note that the provided packet contains legislative provisions defining the term, and no specific case law is included in the research material provided for this specific deadline.

    *   **Step 4: VALUTAZIONE**
        *   Fact: The rule is clear (Art. 43 DPR 600/1973).
        *   Claim: High confidence based on explicit statutory text.
        *   Constraint: If no source for the evaluation itself, use "VALUTAZIONE PERSONALE:". But usually, this step evaluates the strength of the argument found in sources. I will cite the main source again to support the conclusion. Or if it's purely my assessment of confidence, I might need to check the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
        *   Wait, the JSON schema shows `"content": "VALUTAZIONE PERSONALE: ..."` inside the `citations` array? No, looking at the example:
            ```json
            {
              "step": "VALUTAZIONE",
              "content": "VALUTAZIONE PERSONALE: ...",
              "citations": []
            }
            ```
            So for the VALUTAZIONE step, if I am making a claim about confidence/validity without a specific source backing that *specific* meta-claim (like "This is high confidence"), I should use the prefix. However, usually, the content of the evaluation relies on the previous sources. The instruction says:

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Qual è il termine di decadenza per la notifica degli avvisi di accertamento ai fini IRPEF?" (What is the statute of limitations for notification of assessment notices for income tax purposes?)

2.  **Analyze the Research Packet:**
    *   [1] DPR 600/1973, Art. 43: "Gli avvisi di accertamento devono essere notificati, a pena di decadenza, entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione." (Assessment notices must be notified within the 5th year following the declaration submission).
    *   [2] DPR 633/1972, Art. 57: Similar text regarding VAT ("avvisi relativi alle rettifiche e agli accertamenti..."). Not directly IRPEF but related context.
    *   [3] DLgs 218/1997, Art. 12: Procedural aspects (preliminary hearing).
    *   [4] DLgs 218/1997, Art. 11: Initiation of procedure.
    *   [5] DPR 600/1973, Art. 43 (duplicate text in packet): Mentions "decadenza per l'accertamento di cui all'articolo 43 del decreto...".
    *   [6] RD 1398/1930, Art. 14: General rules on time computation (calendar).
    *   [7] DLgs 218/1997, Art. 6: Suspension of terms.
    *   [8] DPR 600/1973, Art. 53 (actually text seems to be about third parties): Mentions "Art. 43 del decreto...".
    *   [9] DLgs 14/2019, Art. 88: Consolidation procedures.
    *   [10] DPR 917/1986, Art. 152 (actually text says Art. 119): Conditions for option effectiveness.

3.  **Drafting the Analysis (CoT):**

    *   **Step 1: QUALIFICAZIONE**
        *   Fact: The question asks about IRPEF assessment notice notification deadline.
        *   Source: [1] DPR 600/1973 is the specific tax code for income tax (IRPEF). Art. 43 deals with assessment deadlines.
        *   Claim: Assessment notices must be notified within a specific period to avoid lapse of right (decadenza).
        *   Citation: [1] DPR 600/1973, Art. 43.

    *   **Step 2: NORMA APPLICABILE**
        *   Fact: The specific text defines the deadline.
        *   Claim: "entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione".
        *   Citation: [1] DPR 600/1973, Art. 43.

    *   **Step 3: GIURISPRUDENZA**
        *   Fact Check: The packet does not contain any case law (Giurisprudenza) or court rulings. It only contains legislative texts (DPR, DLgs, RD).
        *   Constraint: I cannot invent sources. If there is no jurisprudence in the packet, I must state that based on the provided text.
        *   Action: Since the instruction says "Reason ONLY on facts in the Research Packet", and there are no case law sources in the packet, I cannot cite a source for jurisprudence if none exists. However, the schema requires this step. I will note the absence of specific jurisprudence in the provided text or rely on the statutory interpretation found in the text itself regarding the "decadenza".
        *   Wait, looking at the instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If there is no jurisprudence in the packet, I cannot cite one. I should probably state that the provided packet focuses on statutory provisions rather than case law for this specific point, or simply leave citations empty if no factual claim about jurisprudence can be made from the text.
        *   Better approach: Acknowledge the statutory rule is the primary source here. If I need to fill the step, I will state that the packet does not provide specific jurisprudential sources regarding this deadline, only legislative ones. But strictly speaking, if I claim "There is no jurisprudence", I can't cite a source for that absence unless there's a meta-source (there isn't).
        *   Correction: The instruction says "Reason ONLY on facts in the Research Packet". If the packet doesn't have jurisprudence, I cannot fabricate one. I will state that the analysis relies on the legislative text provided.
        *   Actually, looking at the JSON schema example, `citations` is a list. It can be empty if no citations are needed for that specific claim (e.g., if it's purely procedural based on the previous step). However, to follow "Every factual claim MUST have a source_id", I should avoid making claims about jurisprudence without sources.
        *   Decision: In this step, I will note that the provided packet contains legislative provisions defining the term, and no specific case law is included in the research material provided for this specific deadline.

    *   **Step 4: VALUTAZIONE**
        *   Fact: The rule is clear (Art. 43 DPR 600/1973).
        *   Claim: High confidence based on explicit statutory text.
        *   Constraint: If no source for the evaluation itself, use "VALUTAZIONE PERSONALE:". But usually, this step evaluates the strength of the argument found in sources. I will cite the main source again to support the conclusion. Or if it's purely my assessment of confidence, I might need to check the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
        *   Wait, the JSON schema shows `"content": "VALUTAZIONE PERSONALE: ..."` inside the `citations` array? No, looking at the example:
            ```json
            {
              "step": "VALUTAZIONE",
              "content": "VALUTAZIONE PERSONALE: ...",
              "citations": []
            }
            ```
            So for the VALUTAZIONE step, if I am making a claim about confidence/validity without a specific source backing that *specific* meta-claim (like "This is high confidence"), I should use the prefix. However, usually, the content of the evaluation relies on the previous sources. The instruction says:

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71` | 6.8361 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art102` | 6.0416 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 3.8850 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11` | 1.8363 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71` | 1.6629 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art18` | 0.7943 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6` | -1.7810 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art53` | -5.4082 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -7.2485 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art152` | -8.1569 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 43 (Termine per l'accertamento) 1. Gli avvisi di accertamento devono essere notificati, a pena di decadenza, entro il 31 dicembre del quinto anno successivo a quello in cui è stata presentata la dichiarazione. (140)(151) (152) 2.

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art102`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 57 (Termine per gli accertamenti) 1. Gli avvisi relativi alle rettifiche e agli accertamenti previsti nell'articolo 54 e nel secondo comma dell'articolo 55 devono essere notificati, a pena di decadenza, entro il 31 dicembre del qui

**[3]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 11 Avvio del procedimento 1. ((L'ufficio di iniziativa, nei casi di cui all' articolo 6-bis, comma 2, della legge n. 212 del 2000 , contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero, ovvero su istanza

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art71`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  di decadenza per l'accertamento di cui all' articolo 43 del decreto del Presidente della Repubblica 29 settembre 1973, n. 600 , e all' articolo 57 del decreto del Presidente della Repubblica 26 ottobre 1972, n. 633 , nonché i termini

**[6]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art18`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 14. (Computo e decorrenza dei termini) Quando la legge penale fa dipendere un effetto giuridico dal decorso del tempo, per il computo di questo si osserva il calendario comune. Ogni qual volta la legge penale stabilisce un termine per il verificarsi di un

**[7]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art6`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  qualora ne ricorrano i presupposti, successivamente alla scadenza del termine di sospensione. L'impugnazione dell'atto comporta rinuncia all'istanza. (23) 4. Entro quindici giorni dalla ricezione dell'istanza di cui ai commi 2 e 2-bis, l'ufficio, anche tel

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art53`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 'imposta, rilevanti ai fini dell'accertamento, nei confronti di loro clienti, fornitori e prestatori di lavoro autonomo. 8-bis) invitare ogni altro soggetto ad esibire o trasmettere, anche in copia fotostatica, atti o documenti fiscal

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  tale adesione è determinante ai fini del raggiungimento della maggioranza delle classi prevista dall'articolo 112, comma 2, lettera d), oppure se la stessa maggioranza è raggiunta escludendo dal computo le classi dei creditori di cui al comma 1. In ogni ca

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art152`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 119 Condizioni per l'efficacia dell'opzione 1. L'opzione può essere esercitata da ciascuna entità legale solo in qualità di controllante o solo in qualità di controllata e la sua efficacia è subordinata al verificarsi delle seguen

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
