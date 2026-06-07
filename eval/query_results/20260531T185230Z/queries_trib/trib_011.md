# trib_011 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:41 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 69.8s (ret 0.1s + llm 69.5s) |

## Query

> Qual è la disciplina dell'accertamento con adesione?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 source snippets (mostly from D.Lgs 19/1997 n. 218 and L. 300/1970).
    *   **Question:** "Qual è la disciplina dell'accertamento con adesione?" (What is the discipline of assessment with consent?)

2.  **Analyze the Research Packet Sources:**
    *   [1] D.Lgs 19/1997 n. 218 Art. 1: Mentions invitation to submit observations or request for assessment with consent instead of observations. (Incomplete text).
    *   [2] D.Lgs 19/1997 n. 218 Art. 13: Definition perfects according to arts 7, 8, 9. Payment within office.
    *   [3] D.Lgs 19/1997 n. 218 Art. 7: Assessment with consent is written in duplicate, signed by taxpayer and head/delegate of office. Indicates separately for each tax.
    *   [4] D.Lgs 19/1997 n. 218 Art. 8: Payment within 20 days from drafting (Art. 7). Can be paid in installments.
    *   [5] D.Lgs 19/1997 n. 218 Art. 12: Mentions conditions for assessment with consent, parties can agree to proceed. (Incomplete text).
    *   [6] D.Lgs 19/1997 n. 218 Art. 17: Mentions organization of revenue offices, determination of modes based on objective parameters, presumptive coefficients, sector studies. (Seems administrative rules context).
    *   [7] L. 300/1970 Art. 18: Labor law context (dismissal justification). Irrelevant to tax assessment with consent directly, but present in packet.
    *   [8] D.Lgs 19/1997 n. 218 Art. 17: Mentions abrogation of old rule about net income definition via non-impugnation or waiver before intervention. (Incomplete text).
    *   [9] D.Lgs 19/1997 n. 218 Art. 17: Definition with consent applicable under conditions of art. 2-bis for succession, donation, registration, mortgage, cadastral taxes.
    *   [10] D.Lgs 19/1997 n. 218 Art. 12: Request by taxpayer in case of notice of assessment or rectification where no prior adversarial procedure applies. (Incomplete text).

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Identify the legal instrument and its nature. It's D.Lgs 19/1997 n. 218, specifically regarding "accertamento con adesione".
        *   Source: [3] Art. 7 defines it as written act in duplicate signed by taxpayer and office head/delegate.
        *   Source: [2] Art. 13 states definition perfects according to arts 7, 8, 9.
        *   Source: [9] Art. 17 mentions applicability conditions (taxes like succession, donation, etc.).

    *   **NORMA APPLICABILE:** Specific articles governing the procedure.
        *   Art. 7 (Redazione atto) -> Source [3].
        *   Art. 8 (Versamento somme) -> Source [4] (20 days deadline).
        *   Art. 13 (Definizione e adempimenti) -> Source [2].
        *   Art. 17 (Ambito di applicazione/condizioni) -> Source [9].

    *   **GIURISPRUDENZA:** The packet does not contain any case law or judicial decisions (only legislative texts). I must state this limitation based on the packet content. No external knowledge allowed.
        *   Constraint: "Ragioni SOLO sui fatti nel Research Packet." -> Cannot invent jurisprudence if not in packet.
        *   Action: State that no jurisprudential sources are present in the provided packet for this specific topic, or rely solely on statutory text as per instruction to reason only on facts in packet. Since I cannot access KB, I must note the absence of case law in the packet.

    *   **VALUTAZIONE:** Assess the solidity based on available sources.
        *   The regulation is clear (Art 7, 8, 13).
        *   Confidence should be HIGH regarding the statutory framework provided in the text.
        *   Must use `ungrounded_reasoning` prefix if making a general assessment not directly cited? No, the instruction says "If you don't have the source -> field ungrounded_reasoning...". But for VALUTAZIONE step, I can cite the sources that support the solidity. However, the schema requires specific structure.
        *   Wait, looking at the Output Schema: `citations` array inside each section.
        *   For VALUTAZIONE step in JSON: `content`: "VALUTAZIONE PERSONALE: ...", `citations`: []. (Based on example provided in prompt).
        *   Actually, the prompt example shows:
            ```json
            {
              "step": "VALUTAZIONE",
              "content": "VALUTAZIONE PERSONALE: ...",
              "citations": []
            }
            ```
            So for VALUTAZIONE step, citations should be empty? Or can I cite sources in other steps? The example shows `citations` inside the object.
            Let's check the instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
            In the JSON schema provided in the prompt description:
            ```json
            {
              "analysis_sections": [
                {
                  "step": "QUALIFICAZIONE",
                  "content": "...",
                  "citations": [...]
                },
                ...
                {
                  "step": "VALUTAZIONE",
                  "content": "VALUTAZIONE PERSONALE: ...",
                  "citations": []
                }
              ],
            ```
            The example explicitly shows `citations` as empty for VALUTAZIONE. I will follow the schema structure provided in the prompt description strictly, even if it conflicts slightly with the general citation rule (which applies to factual claims). Since the content field is prefixed "VALUTAZIONE PERSONALE:", it implies personal assessment logic which might not need specific source_id citations inside that block according to the example. However, I must ensure factual claims in QUALIFICAZIONE/NORMA APPLICABILE have sources.

    *   **GAP ANALYSIS:** What is missing?
        *   No case law (Giurisprudenza) in packet.
        *   Some text snippets are incomplete (e.g., Art 1, Art 5/6 context).
        *   Source [7] is labor law (irrelevant gap?).

4.  **Constructing the JSON:**

    *   **Step 1: QUALIFICAZIONE**
        *   Content: Identify D.Lgs 218/1997 as the governing norm for assessment with consent. Art. 7 defines the act structure (duplicate, signed).

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 source snippets (mostly from D.Lgs 19/1997 n. 218 and L. 300/1970).
    *   **Question:** "Qual è la disciplina dell'accertamento con adesione?" (What is the discipline of assessment with consent?)

2.  **Analyze the Research Packet Sources:**
    *   [1] D.Lgs 19/1997 n. 218 Art. 1: Mentions invitation to submit observations or request for assessment with consent instead of observations. (Incomplete text).
    *   [2] D.Lgs 19/1997 n. 218 Art. 13: Definition perfects according to arts 7, 8, 9. Payment within office.
    *   [3] D.Lgs 19/1997 n. 218 Art. 7: Assessment with consent is written in duplicate, signed by taxpayer and head/delegate of office. Indicates separately for each tax.
    *   [4] D.Lgs 19/1997 n. 218 Art. 8: Payment within 20 days from drafting (Art. 7). Can be paid in installments.
    *   [5] D.Lgs 19/1997 n. 218 Art. 12: Mentions conditions for assessment with consent, parties can agree to proceed. (Incomplete text).
    *   [6] D.Lgs 19/1997 n. 218 Art. 17: Mentions organization of revenue offices, determination of modes based on objective parameters, presumptive coefficients, sector studies. (Seems administrative rules context).
    *   [7] L. 300/1970 Art. 18: Labor law context (dismissal justification). Irrelevant to tax assessment with consent directly, but present in packet.
    *   [8] D.Lgs 19/1997 n. 218 Art. 17: Mentions abrogation of old rule about net income definition via non-impugnation or waiver before intervention. (Incomplete text).
    *   [9] D.Lgs 19/1997 n. 218 Art. 17: Definition with consent applicable under conditions of art. 2-bis for succession, donation, registration, mortgage, cadastral taxes.
    *   [10] D.Lgs 19/1997 n. 218 Art. 12: Request by taxpayer in case of notice of assessment or rectification where no prior adversarial procedure applies. (Incomplete text).

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Identify the legal instrument and its nature. It's D.Lgs 19/1997 n. 218, specifically regarding "accertamento con adesione".
        *   Source: [3] Art. 7 defines it as written act in duplicate signed by taxpayer and office head/delegate.
        *   Source: [2] Art. 13 states definition perfects according to arts 7, 8, 9.
        *   Source: [9] Art. 17 mentions applicability conditions (taxes like succession, donation, etc.).

    *   **NORMA APPLICABILE:** Specific articles governing the procedure.
        *   Art. 7 (Redazione atto) -> Source [3].
        *   Art. 8 (Versamento somme) -> Source [4] (20 days deadline).
        *   Art. 13 (Definizione e adempimenti) -> Source [2].
        *   Art. 17 (Ambito di applicazione/condizioni) -> Source [9].

    *   **GIURISPRUDENZA:** The packet does not contain any case law or judicial decisions (only legislative texts). I must state this limitation based on the packet content. No external knowledge allowed.
        *   Constraint: "Ragioni SOLO sui fatti nel Research Packet." -> Cannot invent jurisprudence if not in packet.
        *   Action: State that no jurisprudential sources are present in the provided packet for this specific topic, or rely solely on statutory text as per instruction to reason only on facts in packet. Since I cannot access KB, I must note the absence of case law in the packet.

    *   **VALUTAZIONE:** Assess the solidity based on available sources.
        *   The regulation is clear (Art 7, 8, 13).
        *   Confidence should be HIGH regarding the statutory framework provided in the text.
        *   Must use `ungrounded_reasoning` prefix if making a general assessment not directly cited? No, the instruction says "If you don't have the source -> field ungrounded_reasoning...". But for VALUTAZIONE step, I can cite the sources that support the solidity. However, the schema requires specific structure.
        *   Wait, looking at the Output Schema: `citations` array inside each section.
        *   For VALUTAZIONE step in JSON: `content`: "VALUTAZIONE PERSONALE: ...", `citations`: []. (Based on example provided in prompt).
        *   Actually, the prompt example shows:
            ```json
            {
              "step": "VALUTAZIONE",
              "content": "VALUTAZIONE PERSONALE: ...",
              "citations": []
            }
            ```
            So for VALUTAZIONE step, citations should be empty? Or can I cite sources in other steps? The example shows `citations` inside the object.
            Let's check the instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
            In the JSON schema provided in the prompt description:
            ```json
            {
              "analysis_sections": [
                {
                  "step": "QUALIFICAZIONE",
                  "content": "...",
                  "citations": [...]
                },
                ...
                {
                  "step": "VALUTAZIONE",
                  "content": "VALUTAZIONE PERSONALE: ...",
                  "citations": []
                }
              ],
            ```
            The example explicitly shows `citations` as empty for VALUTAZIONE. I will follow the schema structure provided in the prompt description strictly, even if it conflicts slightly with the general citation rule (which applies to factual claims). Since the content field is prefixed "VALUTAZIONE PERSONALE:", it implies personal assessment logic which might not need specific source_id citations inside that block according to the example. However, I must ensure factual claims in QUALIFICAZIONE/NORMA APPLICABILE have sources.

    *   **GAP ANALYSIS:** What is missing?
        *   No case law (Giurisprudenza) in packet.
        *   Some text snippets are incomplete (e.g., Art 1, Art 5/6 context).
        *   Source [7] is labor law (irrelevant gap?).

4.  **Constructing the JSON:**

    *   **Step 1: QUALIFICAZIONE**
        *   Content: Identify D.Lgs 218/1997 as the governing norm for assessment with consent. Art. 7 defines the act structure (duplicate, signed).

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
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
