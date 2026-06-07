# trib_012 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:42 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 66.7s (ret 0.1s + llm 66.4s) |

## Query

> Come si determina la base imponibile IRES per le società di capitali?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, R.D. 262/42, D.Lgs 14/19).
    *   **Question:** "Come si determina la base imponibile IRES per le società di capitali?" (How is the taxable base for IRES determined for joint-stock companies?)

2.  **Analyze the Research Packet Sources:**
    *   [1] DPR 917/86 Art. 130: Subject eligible to determine unique tax base for non-resident group of enterprises. Mentions Art. 73 (companies/entities).
    *   [2] DPR 917/86 Art. 136: Determination of tax due. Summation of taxable income of controlling company and foreign subsidiaries according to previous articles.
    *   [3] R.D. 262/42 Art. 2504-bis: Transformation of capital companies (mentions liability).
    *   [4] R.D. 262/42 Art. 2500-ter: Transformation of partnerships into capital companies.
    *   [5] R.D. 262/42 Art. 2500-sexies: Transformation of capital companies into partnerships.
    *   [6] DPR 917/86 Art. 140: Coordination with Art. 167 (regarding foreign subsidiaries included in taxable income).
    *   [7] D.Lgs 14/19 Art. 380: Causes for dissolution of capital companies (liquidation judicial, etc.).
    *   [8] R.D. 262/42 Art. 2500-octies: Heterogeneous transformation into capital companies.
    *   [9] R.D. 262/42 Art. 2500-septies: Heterogeneous transformation from capital companies.
    *   [10] R.D. 1443/40 Art. 12: Jurisdiction for obligations (not relevant to IRES base determination directly).

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "base imponibile IRES per le società di capitali" (IRES taxable base for joint-stock companies) in general.
    *   Source [1] and [2] refer to DPR 917/86, which is the TUIR (Testo Unico delle Imposte sui Redditi). Art. 130 talks about "unica base imponibile per il gruppo di imprese non residenti" (unique tax base for non-resident enterprise group) - this refers to the *consolidated* taxation regime (regime di consolidamento fiscale), not necessarily the general determination of IRES base for a single company, though it implies the mechanism.
    *   Source [2] Art. 136 talks about "Determinazione dell'imposta dovuta" (Determination of tax due) via summation of taxable income of controlling and foreign subsidiaries. This is specific to the consolidated regime or cross-border groups.
    *   Sources [3]-[9] are from R.D. 262/42 (Civil Code provisions on transformations, dissolution). They do not define IRES base determination rules directly.
    *   Source [10] is procedural jurisdiction.

    *Critical Observation:* The Research Packet does *not* contain the general rule for determining the IRES taxable base for a standard Italian joint-stock company (e.g., Art. 96 DPR 917/86 regarding profit calculation, or general accounting rules). It only contains specific provisions about consolidated taxation (DPR 917/86 Arts 130, 136) and corporate transformations/dissolution (R.D. 262/42).
    *   Source [1] mentions "Le società e gli enti di cui all'articolo 73... possono esercitare l'opzione per includere..." (Companies/entities of Art. 73 can exercise option to include...). This hints at the consolidated regime.
    *   Source [2] says "La società controllante, effettuando la somma algebrica del proprio imponibile e di quelli delle controllate estere determinati secondo i criteri di cui agli articoli precedenti..." (The controlling company, by summing up its taxable income and those of foreign subsidiaries determined according to previous articles...).

    *Constraint Check:* I must reason ONLY on facts in the Research Packet. I cannot bring outside knowledge about Art. 96 TUIR or general accounting rules if they are not in the packet.
    *   The question asks "How is it determined?".
    *   Based *only* on the packet, the relevant information regarding IRES base determination for groups (which involves capital companies) is found in DPR 917/86 Arts 130 and 136.
    *   However, if the question implies general IRES rules, the packet might be insufficient. But I must answer based on the packet.
    *   The packet explicitly mentions "Determinazione dell'imposta dovuta" (Determination of tax due) in Art. 136 via summation of taxable income of controlling and foreign subsidiaries.
    *   It also mentions eligibility for consolidated taxation in Art. 130.

4.  **Drafting the Analysis Sections:**

    *   **QUALIFICAZIONE:** Identify the legal regime mentioned in the packet regarding IRES base determination. The packet focuses on the consolidated taxation regime (DPR 917/86) and corporate transformations (R.D. 262/42).
        *   Claim: DPR 917/86 regulates specific aspects of taxable income determination for groups involving capital companies. Source [1], [2].
    *   **NORMA APPLICABILE:** Cite the specific articles in the packet that define the mechanism.
        *   Art. 130 (Source [1]) defines subjects eligible for unique tax base option.
        *   Art. 136 (Source [2]) defines the calculation method (summation of controlling and foreign subsidiaries).
    *   **GIURISPRUDENZA:** The packet does not contain case law or jurisprudence sources. It only contains statutes/regulations. I must state this limitation or note absence. Since I cannot invent, I will note that no specific jurisprudence is in the packet. Wait, instruction says "Reason ONLY on facts in Research Packet". If there is no jurisprudence source, I should not fabricate one. I can mention the lack of it in GAP ANALYSIS. In GIURISPRUDENZA step, if empty, content might reflect absence or general orientation based *only* text (which implies statutory interpretation). Better to state "Nessuna giurisprudenza presente nel Packet".
    *   **VALUTAZIONE:** Assess confidence. Since the packet only covers consolidated taxation and transformations, not general IRES base rules for single companies, confidence regarding a *general* question is LOW/MEDIUM based on available text. However, strictly following the "Reason ONLY on facts" rule:

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" (never as citation). Do not invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, R.D. 262/42, D.Lgs 14/19).
    *   **Question:** "Come si determina la base imponibile IRES per le società di capitali?" (How is the taxable base for IRES determined for joint-stock companies?)

2.  **Analyze the Research Packet Sources:**
    *   [1] DPR 917/86 Art. 130: Subject eligible to determine unique tax base for non-resident group of enterprises. Mentions Art. 73 (companies/entities).
    *   [2] DPR 917/86 Art. 136: Determination of tax due. Summation of taxable income of controlling company and foreign subsidiaries according to previous articles.
    *   [3] R.D. 262/42 Art. 2504-bis: Transformation of capital companies (mentions liability).
    *   [4] R.D. 262/42 Art. 2500-ter: Transformation of partnerships into capital companies.
    *   [5] R.D. 262/42 Art. 2500-sexies: Transformation of capital companies into partnerships.
    *   [6] DPR 917/86 Art. 140: Coordination with Art. 167 (regarding foreign subsidiaries included in taxable income).
    *   [7] D.Lgs 14/19 Art. 380: Causes for dissolution of capital companies (liquidation judicial, etc.).
    *   [8] R.D. 262/42 Art. 2500-octies: Heterogeneous transformation into capital companies.
    *   [9] R.D. 262/42 Art. 2500-septies: Heterogeneous transformation from capital companies.
    *   [10] R.D. 1443/40 Art. 12: Jurisdiction for obligations (not relevant to IRES base determination directly).

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "base imponibile IRES per le società di capitali" (IRES taxable base for joint-stock companies) in general.
    *   Source [1] and [2] refer to DPR 917/86, which is the TUIR (Testo Unico delle Imposte sui Redditi). Art. 130 talks about "unica base imponibile per il gruppo di imprese non residenti" (unique tax base for non-resident enterprise group) - this refers to the *consolidated* taxation regime (regime di consolidamento fiscale), not necessarily the general determination of IRES base for a single company, though it implies the mechanism.
    *   Source [2] Art. 136 talks about "Determinazione dell'imposta dovuta" (Determination of tax due) via summation of taxable income of controlling and foreign subsidiaries. This is specific to the consolidated regime or cross-border groups.
    *   Sources [3]-[9] are from R.D. 262/42 (Civil Code provisions on transformations, dissolution). They do not define IRES base determination rules directly.
    *   Source [10] is procedural jurisdiction.

    *Critical Observation:* The Research Packet does *not* contain the general rule for determining the IRES taxable base for a standard Italian joint-stock company (e.g., Art. 96 DPR 917/86 regarding profit calculation, or general accounting rules). It only contains specific provisions about consolidated taxation (DPR 917/86 Arts 130, 136) and corporate transformations/dissolution (R.D. 262/42).
    *   Source [1] mentions "Le società e gli enti di cui all'articolo 73... possono esercitare l'opzione per includere..." (Companies/entities of Art. 73 can exercise option to include...). This hints at the consolidated regime.
    *   Source [2] says "La società controllante, effettuando la somma algebrica del proprio imponibile e di quelli delle controllate estere determinati secondo i criteri di cui agli articoli precedenti..." (The controlling company, by summing up its taxable income and those of foreign subsidiaries determined according to previous articles...).

    *Constraint Check:* I must reason ONLY on facts in the Research Packet. I cannot bring outside knowledge about Art. 96 TUIR or general accounting rules if they are not in the packet.
    *   The question asks "How is it determined?".
    *   Based *only* on the packet, the relevant information regarding IRES base determination for groups (which involves capital companies) is found in DPR 917/86 Arts 130 and 136.
    *   However, if the question implies general IRES rules, the packet might be insufficient. But I must answer based on the packet.
    *   The packet explicitly mentions "Determinazione dell'imposta dovuta" (Determination of tax due) in Art. 136 via summation of taxable income of controlling and foreign subsidiaries.
    *   It also mentions eligibility for consolidated taxation in Art. 130.

4.  **Drafting the Analysis Sections:**

    *   **QUALIFICAZIONE:** Identify the legal regime mentioned in the packet regarding IRES base determination. The packet focuses on the consolidated taxation regime (DPR 917/86) and corporate transformations (R.D. 262/42).
        *   Claim: DPR 917/86 regulates specific aspects of taxable income determination for groups involving capital companies. Source [1], [2].
    *   **NORMA APPLICABILE:** Cite the specific articles in the packet that define the mechanism.
        *   Art. 130 (Source [1]) defines subjects eligible for unique tax base option.
        *   Art. 136 (Source [2]) defines the calculation method (summation of controlling and foreign subsidiaries).
    *   **GIURISPRUDENZA:** The packet does not contain case law or jurisprudence sources. It only contains statutes/regulations. I must state this limitation or note absence. Since I cannot invent, I will note that no specific jurisprudence is in the packet. Wait, instruction says "Reason ONLY on facts in Research Packet". If there is no jurisprudence source, I should not fabricate one. I can mention the lack of it in GAP ANALYSIS. In GIURISPRUDENZA step, if empty, content might reflect absence or general orientation based *only* text (which implies statutory interpretation). Better to state "Nessuna giurisprudenza presente nel Packet".
    *   **VALUTAZIONE:** Assess confidence. Since the packet only covers consolidated taxation and transformations, not general IRES base rules for single companies, confidence regarding a *general* question is LOW/MEDIUM based on available text. However, strictly following the "Reason ONLY on facts" rule:

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art166` | 5.5782 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172` | 2.6479 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2679` | 0.5050 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2660` | 0.3313 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2663` | -0.2083 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art177` | -0.4932 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380` | -0.5215 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2665` | -1.9425 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2664` | -2.0215 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art15` | -3.1247 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art166`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 130 ((Soggetti ammessi alla determinazione della unica base imponibile per il gruppo di imprese non residenti.)) (( 1. Le società e gli enti di cui all'articolo 73, comma 1, lettere a) e b), possono esercitare l'opzione per includ

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 136 Determinazione dell'imposta dovuta 1. La società controllante, effettuando la somma algebrica del proprio imponibile e di quelli delle controllate estere determinati secondo i criteri ((di cui agli articoli precedenti)) , dete

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2679`

> REGIO DECRETO 16 marzo 1942, n. 262 età di capitali ovvero mediante incorporazione in una società di capitali non libera i soci a responsabilità illimitata dalla responsabilità per le obbligazioni delle rispettive società partecipanti alla fusione anteriori all'ultima delle iscrizioni prescritte dal

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2660`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-ter. (Trasformazione di società di persone). Salvo diversa disposizione del contratto sociale, la trasformazione di società di persone in società di capitali è decisa con il consenso della maggioranza dei soci determinata secondo la parte attribuita a ci

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2663`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-sexies. (( (Trasformazione di società di capitali).)) ((Salvo diversa disposizione dello statuto, la deliberazione di trasformazione di società di capitali in società di persone è adottata con le maggioranze previste per le modifiche dello statuto. È com

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art177`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 140 ((Coordinamento con l'articolo 167 )) (( 1. Le disposizioni di cui all'articolo 167 non si applicano relativamente alle controllate estere il cui imponibile viene incluso in quello della società controllante per effetto dell'o

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 380 (( (Cause di scioglimento delle società di capitali).)) (( 1. All' articolo 2484, primo comma, del codice civile dopo il numero 7) è aggiunto il seguente: "7-bis) per l'apertura della procedura di liquidazione giudiziale e della liquidazione contro

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2665`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-octies. (( (Trasformazione eterogenea in società di capitali).)) ((I consorzi, le società consortili, le comunioni d'azienda, le associazioni riconosciute e le fondazioni possono trasformarsi in una delle società disciplinate nei capi V, VI e VII del pre

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2664`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-septies. (( (Trasformazione eterogenea da società di capitali).)) ((Le società disciplinate nei capi V, VI, VII del presente titolo possono trasformarsi in consorzi, società consortili, società cooperative, comunioni di azienda, associazioni non riconosc

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art15`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 12. (Cause relative a rapporti obbligatori, a locazioni e a divisioni). Il valore delle cause relative all'esistenza, alla validità o alla risoluzione di un rapporto giuridico obbligatorio si determina in base a quella parte del rapporto che è in contestaz

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
