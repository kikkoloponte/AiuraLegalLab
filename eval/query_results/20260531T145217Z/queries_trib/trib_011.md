# trib_011 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:19 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 70.3s (ret 0.2s + llm 69.9s) |

## Query

> Qual è la disciplina dell'accertamento con adesione?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 source snippets (mostly from D.Lgs 218/1997 and L. 300/1970).
    *   **Question:** "Qual è la disciplina dell'accertamento con adesione?" (What is the discipline of assessment with consent?)

2.  **Analyze the Research Packet Sources:**
    *   [1] DLgs 218/1997 Art. 1: Mentions invitation to submit observations or request for assessment with consent instead of observations.
    *   [2] DLgs 218/1997 Art. 13: Definition perfection according to Arts 7, 8, 9. Payment within 20 days (refers to Art 8).
    *   [3] DLgs 218/1997 Art. 7: Assessment with consent is written in duplicate, signed by taxpayer and head/delegate of office. Indicates tax separately.
    *   [4] DLgs 218/1997 Art. 8: Payment within 20 days from drafting (Art 7). Can be paid installments.
    *   [5] DLgs 218/1997 Art. 12: Mentions conditions for assessment with consent, parties can agree to proceed. Paragraph 1-ter mentions taxpayer who used the facility cannot... (text cut off).
    *   [6] DLgs 218/1997 Art. 17: Mentions organization of revenue offices, determination of modalities based on objective parameters, presumptive coefficients, sector studies.
    *   [7] L. 300/1970 Art. 18: Labor law (dismissal justification). Irrelevant to tax assessment with consent directly, likely noise or context for general legal reasoning but not specific to DLgs 218.
    *   [8] DLgs 218/1997 Art. 17: Abrogated paragraph regarding net income definition via non-objection.
    *   [9] DLgs 218/1997 Art. 17: Definition with consent applicable under conditions of Art 2-bis for succession, donation, registration, mortgage, cadastral taxes.
    *   [10] DLgs 218/1997 Art. 12: Request by taxpayer in case of notice of assessment... (text cut off).

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Define what "accertamento con adesione" is based on the text.
        *   Source [3] Art. 7: Written act, duplicate, signed by taxpayer and office head/delegate. Indicates tax separately.
        *   Source [1] Art. 1: Can be requested instead of observations (invitation to submit request).
        *   Source [9] Art. 17: Applicable under conditions of Art 2-bis for specific taxes (successions, donations, registration, etc.).
    *   **NORMA APPLICABILE:** Specific articles governing the process.
        *   Source [3] Art. 7: Drafting requirements.
        *   Source [4] Art. 8: Payment deadlines (20 days) and installments.
        *   Source [2] Art. 13: Definition perfection references Arts 7, 8, 9.
        *   Source [5] Art. 12: Taxpayer request conditions.
    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza). It only contains legislative texts (DLgs and Legge). I must state this limitation or rely on the text provided. Since I cannot access external KB, I must note the absence of specific jurisprudence in the Packet.
        *   Wait, instruction says: "Ragioni SOLO sui fatti nel Research Packet." If there is no jurisprudence in the packet, I should not invent it. I will state that the provided sources are legislative norms without citing external case law.
    *   **VALUTAZIONE:** Assess the solidity of the information based on available sources.
        *   Sources [3], [4], [2] provide clear procedural rules (Art 7, 8, 13).
        *   Source [9] limits scope to specific taxes for Art 17 context.
        *   Overall confidence depends on completeness of the packet regarding Art 2-bis mentioned in [9].
    *   **GAP ANALYSIS:** What is missing?
        *   Full text of Art 2-bis (mentioned in [9]).
        *   Full text of Art 9 (mentioned in [2] but not provided).
        *   Jurisprudence on interpretation.

4.  **Constructing the JSON:**

    *   Ensure `source_id` matches exactly (e.g., `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7`).
    *   Ensure steps are uppercase and exact names.
    *   Ensure no text outside JSON.

5.  **Refining Citations:**
    *   Claim: Assessment is written in duplicate, signed by taxpayer and office head/delegate. Source [3].
    *   Claim: Payment deadline is 20 days from drafting. Source [4] (and [2]).
    *   Claim: Can be paid installments. Source [4].
    *   Claim: Applicable to specific taxes under Art 17 conditions. Source [9].
    *   Claim: Definition perfection follows Arts 7, 8, 9. Source [2].

6.  **Handling "Giurisprudenza":** Since the packet has no case law, I will state that the analysis relies on legislative text provided in the packet and note the absence of specific judicial interpretation within the provided sources. Or simply leave it empty if strict adherence to "facts in Packet" means I can't claim there *is* jurisprudence. Better to explicitly mention the lack of jurisprudential data in the packet for this step or state that the packet focuses on legislative norms. Given the instruction "Ragioni SOLO sui fatti nel Research Packet", I cannot invent case law. I will note the absence.

7.  **Handling "VALUTAZIONE":** Must use `ungrounded_reasoning` prefix if no source supports a specific evaluation claim? No, the instruction says: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to claims. For the overall confidence step in JSON, I need to decide HIGH/MEDIUM/LOW.
    *   The packet covers Art 7 (drafting), Art 8 (payment), Art 13 (definition). It seems sufficient for a general overview of the discipline. Confidence: MEDIUM (due to missing full text of referenced articles like Art 2-bis and Art 9 mentioned in snippets).
    *   Wait, looking at the instruction again: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
    *   In the JSON structure provided in the prompt example: `analysis_sections` contains objects with `step`, `content`, `citations`.
    *   The `VALUTAZIONE` step content should probably be a summary assessment. If I make an evaluative claim, it needs a source or

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 source snippets (mostly from D.Lgs 218/1997 and L. 300/1970).
    *   **Question:** "Qual è la disciplina dell'accertamento con adesione?" (What is the discipline of assessment with consent?)

2.  **Analyze the Research Packet Sources:**
    *   [1] DLgs 218/1997 Art. 1: Mentions invitation to submit observations or request for assessment with consent instead of observations.
    *   [2] DLgs 218/1997 Art. 13: Definition perfection according to Arts 7, 8, 9. Payment within 20 days (refers to Art 8).
    *   [3] DLgs 218/1997 Art. 7: Assessment with consent is written in duplicate, signed by taxpayer and head/delegate of office. Indicates tax separately.
    *   [4] DLgs 218/1997 Art. 8: Payment within 20 days from drafting (Art 7). Can be paid installments.
    *   [5] DLgs 218/1997 Art. 12: Mentions conditions for assessment with consent, parties can agree to proceed. Paragraph 1-ter mentions taxpayer who used the facility cannot... (text cut off).
    *   [6] DLgs 218/1997 Art. 17: Mentions organization of revenue offices, determination of modalities based on objective parameters, presumptive coefficients, sector studies.
    *   [7] L. 300/1970 Art. 18: Labor law (dismissal justification). Irrelevant to tax assessment with consent directly, likely noise or context for general legal reasoning but not specific to DLgs 218.
    *   [8] DLgs 218/1997 Art. 17: Abrogated paragraph regarding net income definition via non-objection.
    *   [9] DLgs 218/1997 Art. 17: Definition with consent applicable under conditions of Art 2-bis for succession, donation, registration, mortgage, cadastral taxes.
    *   [10] DLgs 218/1997 Art. 12: Request by taxpayer in case of notice of assessment... (text cut off).

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Define what "accertamento con adesione" is based on the text.
        *   Source [3] Art. 7: Written act, duplicate, signed by taxpayer and office head/delegate. Indicates tax separately.
        *   Source [1] Art. 1: Can be requested instead of observations (invitation to submit request).
        *   Source [9] Art. 17: Applicable under conditions of Art 2-bis for specific taxes (successions, donations, registration, etc.).
    *   **NORMA APPLICABILE:** Specific articles governing the process.
        *   Source [3] Art. 7: Drafting requirements.
        *   Source [4] Art. 8: Payment deadlines (20 days) and installments.
        *   Source [2] Art. 13: Definition perfection references Arts 7, 8, 9.
        *   Source [5] Art. 12: Taxpayer request conditions.
    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza). It only contains legislative texts (DLgs and Legge). I must state this limitation or rely on the text provided. Since I cannot access external KB, I must note the absence of specific jurisprudence in the Packet.
        *   Wait, instruction says: "Ragioni SOLO sui fatti nel Research Packet." If there is no jurisprudence in the packet, I should not invent it. I will state that the provided sources are legislative norms without citing external case law.
    *   **VALUTAZIONE:** Assess the solidity of the information based on available sources.
        *   Sources [3], [4], [2] provide clear procedural rules (Art 7, 8, 13).
        *   Source [9] limits scope to specific taxes for Art 17 context.
        *   Overall confidence depends on completeness of the packet regarding Art 2-bis mentioned in [9].
    *   **GAP ANALYSIS:** What is missing?
        *   Full text of Art 2-bis (mentioned in [9]).
        *   Full text of Art 9 (mentioned in [2] but not provided).
        *   Jurisprudence on interpretation.

4.  **Constructing the JSON:**

    *   Ensure `source_id` matches exactly (e.g., `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7`).
    *   Ensure steps are uppercase and exact names.
    *   Ensure no text outside JSON.

5.  **Refining Citations:**
    *   Claim: Assessment is written in duplicate, signed by taxpayer and office head/delegate. Source [3].
    *   Claim: Payment deadline is 20 days from drafting. Source [4] (and [2]).
    *   Claim: Can be paid installments. Source [4].
    *   Claim: Applicable to specific taxes under Art 17 conditions. Source [9].
    *   Claim: Definition perfection follows Arts 7, 8, 9. Source [2].

6.  **Handling "Giurisprudenza":** Since the packet has no case law, I will state that the analysis relies on legislative text provided in the packet and note the absence of specific judicial interpretation within the provided sources. Or simply leave it empty if strict adherence to "facts in Packet" means I can't claim there *is* jurisprudence. Better to explicitly mention the lack of jurisprudential data in the packet for this step or state that the packet focuses on legislative norms. Given the instruction "Ragioni SOLO sui fatti nel Research Packet", I cannot invent case law. I will note the absence.

7.  **Handling "VALUTAZIONE":** Must use `ungrounded_reasoning` prefix if no source supports a specific evaluation claim? No, the instruction says: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to claims. For the overall confidence step in JSON, I need to decide HIGH/MEDIUM/LOW.
    *   The packet covers Art 7 (drafting), Art 8 (payment), Art 13 (definition). It seems sufficient for a general overview of the discipline. Confidence: MEDIUM (due to missing full text of referenced articles like Art 2-bis and Art 9 mentioned in snippets).
    *   Wait, looking at the instruction again: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
    *   In the JSON structure provided in the prompt example: `analysis_sections` contains objects with `step`, `content`, `citations`.
    *   The `VALUTAZIONE` step content should probably be a summary assessment. If I make an evaluative claim, it needs a source or

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art1` | 5.3336 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art13` | 5.1616 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7` | 5.1423 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art8` | 3.4214 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 3.0552 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | 2.8168 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:legge:1970-05-20;300~art18` | 1.9636 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -0.5116 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -1.6284 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | -2.1253 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art1`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 ito alla formulazione di osservazioni, anche quello alla presentazione di istanza per la definizione dell'accertamento con adesione, in luogo delle osservazioni. L'invito alla presentazione di istanza per la definizione dell'accertamento con adesione è in o

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art13`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 13 Atto di accertamento con adesione, adempimenti successivi e definizione 1. La definizione si perfeziona secondo quanto previsto dagli articoli 7, 8 e 9. Il versamento delle somme dovute per effetto dell'adesione è effettuato presso l'ufficio del reg

**[3]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 7 Atto di accertamento con adesione 1. L'accertamento con adesione è redatto con atto scritto in duplice esemplare, sottoscritto dal contribuente e dal capo dell'ufficio o da un suo delegato. Nell'atto sono indicati, separatamente per ciascun tributo,

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art8`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 8 (Adempimenti successivi). 1. Il versamento delle somme dovute per effetto dell'accertamento con adesione è eseguito entro venti giorni dalla redazione dell'atto di cui all'articolo 7. 2. Le somme dovute possono essere versate anche ratealmente in un

**[5]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 ffici delle entrate, e per la loro organizzazione, secondo criteri di efficienza e di trasparenza; b) per la determinazione delle modalità di accertamento con adesione basate su parametri oggettivi, coefficienti presuntivi e studi di settore nonchè delle mo

**[7]** `urn:nir:stato:legge:1970-05-20;300~art18`

> LEGGE 20 maggio 1970, n. 300  del lavoratore, accerti che vi è anche un difetto di giustificazione del licenziamento, nel qual caso applica, in luogo di quelle previste dal presente comma, le tutele di cui ai commi quarto, quinto o settimo. Il giudice applica la medesima disciplina di cui al quarto

**[8]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[9]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  La definizione in contraddittorio, con adesione del contribuente, è applicabile, alle medesime condizioni di cui all'art. 2-bis, nei confronti dei contribuenti, con riferimento alle imposte sulle successioni e donazioni, di registro, ipotecaria, catastale

**[10]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
