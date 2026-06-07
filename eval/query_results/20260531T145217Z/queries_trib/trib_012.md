# trib_012 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:20 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.0s (ret 0.2s + llm 66.6s) |

## Query

> Come si determina la base imponibile IRES per le società di capitali?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, R.D. 262/42, D.Lgs 14/19).
    *   **Question:** "Come si determina la base imponibile IRES per le società di capitali?" (How is the IRES taxable base determined for joint-stock companies?)

2.  **Analyze the Research Packet Sources:**
    *   [1] DPR 917/86 Art. 75: Base imponibile applies to net comprehensive income, determined according to Section I of Chapter II, for companies/entities under Art. 73(1)(a) and (b).
    *   [2] DPR 917/86 Art. 130: Companies/entities under Art. 73(1)(a) and (b) can opt for a single taxable base for non-resident groups.
    *   [3] DPR 917/86 Art. 136: Determination of tax due (algebraic sum of controlling company's income and foreign subsidiaries' income).
    *   [4] R.D. 262/42 Art. 2504-bis: Mentioned in context of capital age or incorporation, liability for obligations prior to registration. (Seems less relevant to IRES base determination directly, more corporate law).
    *   [5] R.D. 262/42 Art. 2500-ter: Transformation of partnership companies into capital companies (consent majority).
    *   [6] R.D. 262/42 Art. 2500-sexies: Transformation of capital companies into partnerships (statute provisions).
    *   [7] DPR 917/86 Art. 140: Coordination with Art. 167 regarding foreign subsidiaries included in taxable base.
    *   [8] D.Lgs 14/19 Art. 380: Causes of dissolution (insolvency, etc.).
    *   [9] DPR 917/86 Art. 45: Capital income determination (interests, profits, etc., without deduction).
    *   [10] DPR 917/86 Art. 94: Mention of assets under Art. 85(1)(c), d), e) and increase in capital.

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** The question asks about IRES taxable base for capital companies (*società di capitali*).
        *   Source [1] defines the general rule: Art. 75 DPR 917/86 states tax applies to net comprehensive income determined per Section I Chapter II for entities under Art. 73(1)(a) and (b).
        *   Source [4], [5], [6] define what constitutes a capital company (*società di capitali*) in the Civil Code context (though the packet text is truncated, it references transformation rules). I need to be careful not to invent details about Art. 2301 etc., but rely on provided text. Source [4] mentions "società di capitali".
        *   Claim: IRES applies to net comprehensive income of capital companies.
        *   Citation: [1].

    *   **NORMA APPLICABILE:** Specific articles defining the calculation.
        *   Source [1] Art. 75 defines "Base imponibile" (Taxable Base).
        *   Source [9] Art. 45 defines "Determinazione del reddito di capitale" (Capital income determination) as part of the comprehensive income.
        *   Claim: The base is determined according to Section I Chapter II rules, including capital income without deduction per Art. 45.
        *   Citation: [1], [9].

    *   **GIURISPRUDENZA:** There are no specific case law sources in the packet (only statutes). I must state this limitation or rely on statutory interpretation if available. The prompt says "Reason ONLY on facts in the Research Packet". If there is no jurisprudence source, I cannot invent one. I will note the absence of specific case law in the packet but focus on statutory provisions provided.
        *   Wait, the instruction says: "If you don't have the source → field `ungrounded_reasoning` with prefix 'VALUTAZIONE PERSONALE:' — never as a citation." This applies to claims without sources. For the GIURISPRUDENZA step, if there is no jurisprudence in the packet, I should state that based on the provided text, only statutory rules are available.
        *   Actually, looking at the schema: `citations` array inside each section. If I claim something about jurisprudence and don't have a source, I must use `ungrounded_reasoning`. However, usually, for this task, if no jurisprudence exists in the packet, I should indicate "Nessuna giurisprudenza nel Packet" or similar within content, but citations array might be empty.
        *   Let's check the constraint: "Ogni affermazione fattuale DEVE avere un source_id". If I say "There is no case law", that's a fact about the packet. But usually, this step expects external knowledge if allowed? No, "Ragioni SOLO sui fatti nel Research Packet." So I must state based on the packet.
        *   Strategy: Acknowledge the statutory framework provided in the packet without inventing case names.

    *   **VALUTAZIONE:** Assess confidence. Since sources are truncated (e.g., Art 75 text cuts off, Art 94 text cuts off), confidence might be MEDIUM regarding specific calculation details, but HIGH on general applicability of DPR 917/86.
        *   Wait, the instruction says: "VALUTAZIONE — solidità ALTA/MEDIA/BASSA (non citata)". This means I don't cite a source for the confidence level itself in the JSON structure? No, looking at the schema example: `"content": "VALUTAZIONE PERSONALE: ...", "citations": []`.
        *   So in the VALUTAZIONE step content, I can use `ungrounded_reasoning` prefix if needed. But here I am evaluating the packet's completeness.
        *   Actually, looking at the instruction: "VALUTAZIONE — solidità ALTA/MEDIA/BASSA (non citata)". This likely refers to the confidence score in the JSON root (`overall_confidence`). The step content should probably reflect the analysis.
        *   Wait, re-reading: `analysis_sections` -> `{step: "VALUTAZIONE", content: "...", citations: []}`.
        *   Instruction: "VALUTAZIONE — solidità ALTA/MEDIA/BASSA (non citata)". This instruction seems to describe the field `overall_confidence`. But in the CoT schema, there is a step called VALUTAZIONE. I need to follow the CoT steps exactly.
        *   So Step 4 "VALUTAZIONE" content should discuss the solidity

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, R.D. 262/42, D.Lgs 14/19).
    *   **Question:** "Come si determina la base imponibile IRES per le società di capitali?" (How is the IRES taxable base determined for joint-stock companies?)

2.  **Analyze the Research Packet Sources:**
    *   [1] DPR 917/86 Art. 75: Base imponibile applies to net comprehensive income, determined according to Section I of Chapter II, for companies/entities under Art. 73(1)(a) and (b).
    *   [2] DPR 917/86 Art. 130: Companies/entities under Art. 73(1)(a) and (b) can opt for a single taxable base for non-resident groups.
    *   [3] DPR 917/86 Art. 136: Determination of tax due (algebraic sum of controlling company's income and foreign subsidiaries' income).
    *   [4] R.D. 262/42 Art. 2504-bis: Mentioned in context of capital age or incorporation, liability for obligations prior to registration. (Seems less relevant to IRES base determination directly, more corporate law).
    *   [5] R.D. 262/42 Art. 2500-ter: Transformation of partnership companies into capital companies (consent majority).
    *   [6] R.D. 262/42 Art. 2500-sexies: Transformation of capital companies into partnerships (statute provisions).
    *   [7] DPR 917/86 Art. 140: Coordination with Art. 167 regarding foreign subsidiaries included in taxable base.
    *   [8] D.Lgs 14/19 Art. 380: Causes of dissolution (insolvency, etc.).
    *   [9] DPR 917/86 Art. 45: Capital income determination (interests, profits, etc., without deduction).
    *   [10] DPR 917/86 Art. 94: Mention of assets under Art. 85(1)(c), d), e) and increase in capital.

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** The question asks about IRES taxable base for capital companies (*società di capitali*).
        *   Source [1] defines the general rule: Art. 75 DPR 917/86 states tax applies to net comprehensive income determined per Section I Chapter II for entities under Art. 73(1)(a) and (b).
        *   Source [4], [5], [6] define what constitutes a capital company (*società di capitali*) in the Civil Code context (though the packet text is truncated, it references transformation rules). I need to be careful not to invent details about Art. 2301 etc., but rely on provided text. Source [4] mentions "società di capitali".
        *   Claim: IRES applies to net comprehensive income of capital companies.
        *   Citation: [1].

    *   **NORMA APPLICABILE:** Specific articles defining the calculation.
        *   Source [1] Art. 75 defines "Base imponibile" (Taxable Base).
        *   Source [9] Art. 45 defines "Determinazione del reddito di capitale" (Capital income determination) as part of the comprehensive income.
        *   Claim: The base is determined according to Section I Chapter II rules, including capital income without deduction per Art. 45.
        *   Citation: [1], [9].

    *   **GIURISPRUDENZA:** There are no specific case law sources in the packet (only statutes). I must state this limitation or rely on statutory interpretation if available. The prompt says "Reason ONLY on facts in the Research Packet". If there is no jurisprudence source, I cannot invent one. I will note the absence of specific case law in the packet but focus on statutory provisions provided.
        *   Wait, the instruction says: "If you don't have the source → field `ungrounded_reasoning` with prefix 'VALUTAZIONE PERSONALE:' — never as a citation." This applies to claims without sources. For the GIURISPRUDENZA step, if there is no jurisprudence in the packet, I should state that based on the provided text, only statutory rules are available.
        *   Actually, looking at the schema: `citations` array inside each section. If I claim something about jurisprudence and don't have a source, I must use `ungrounded_reasoning`. However, usually, for this task, if no jurisprudence exists in the packet, I should indicate "Nessuna giurisprudenza nel Packet" or similar within content, but citations array might be empty.
        *   Let's check the constraint: "Ogni affermazione fattuale DEVE avere un source_id". If I say "There is no case law", that's a fact about the packet. But usually, this step expects external knowledge if allowed? No, "Ragioni SOLO sui fatti nel Research Packet." So I must state based on the packet.
        *   Strategy: Acknowledge the statutory framework provided in the packet without inventing case names.

    *   **VALUTAZIONE:** Assess confidence. Since sources are truncated (e.g., Art 75 text cuts off, Art 94 text cuts off), confidence might be MEDIUM regarding specific calculation details, but HIGH on general applicability of DPR 917/86.
        *   Wait, the instruction says: "VALUTAZIONE — solidità ALTA/MEDIA/BASSA (non citata)". This means I don't cite a source for the confidence level itself in the JSON structure? No, looking at the schema example: `"content": "VALUTAZIONE PERSONALE: ...", "citations": []`.
        *   So in the VALUTAZIONE step content, I can use `ungrounded_reasoning` prefix if needed. But here I am evaluating the packet's completeness.
        *   Actually, looking at the instruction: "VALUTAZIONE — solidità ALTA/MEDIA/BASSA (non citata)". This likely refers to the confidence score in the JSON root (`overall_confidence`). The step content should probably reflect the analysis.
        *   Wait, re-reading: `analysis_sections` -> `{step: "VALUTAZIONE", content: "...", citations: []}`.
        *   Instruction: "VALUTAZIONE — solidità ALTA/MEDIA/BASSA (non citata)". This instruction seems to describe the field `overall_confidence`. But in the CoT schema, there is a step called VALUTAZIONE. I need to follow the CoT steps exactly.
        *   So Step 4 "VALUTAZIONE" content should discuss the solidity

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art96` | 5.7262 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art166` | 5.5782 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172` | 2.6479 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2679` | 0.5050 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2660` | 0.3313 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2663` | -0.2083 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art177` | -0.4932 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380` | -0.5215 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art55` | -0.8646 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art118` | -1.5984 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art96`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 75 Base imponibile 1. L'imposta si applica sul reddito complessivo netto, determinato secondo le disposizioni della sezione I del capo II, per le società e gli enti di cui alle lettere a) e b) del comma 1 dell'articolo 73, del cap

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art166`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 130 ((Soggetti ammessi alla determinazione della unica base imponibile per il gruppo di imprese non residenti.)) (( 1. Le società e gli enti di cui all'articolo 73, comma 1, lettere a) e b), possono esercitare l'opzione per includ

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 136 Determinazione dell'imposta dovuta 1. La società controllante, effettuando la somma algebrica del proprio imponibile e di quelli delle controllate estere determinati secondo i criteri ((di cui agli articoli precedenti)) , dete

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2679`

> REGIO DECRETO 16 marzo 1942, n. 262 età di capitali ovvero mediante incorporazione in una società di capitali non libera i soci a responsabilità illimitata dalla responsabilità per le obbligazioni delle rispettive società partecipanti alla fusione anteriori all'ultima delle iscrizioni prescritte dal

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2660`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-ter. (Trasformazione di società di persone). Salvo diversa disposizione del contratto sociale, la trasformazione di società di persone in società di capitali è decisa con il consenso della maggioranza dei soci determinata secondo la parte attribuita a ci

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2663`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2500-sexies. (( (Trasformazione di società di capitali).)) ((Salvo diversa disposizione dello statuto, la deliberazione di trasformazione di società di capitali in società di persone è adottata con le maggioranze previste per le modifiche dello statuto. È com

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art177`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 140 ((Coordinamento con l'articolo 167 )) (( 1. Le disposizioni di cui all'articolo 167 non si applicano relativamente alle controllate estere il cui imponibile viene incluso in quello della società controllante per effetto dell'o

**[8]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art380`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 380 (( (Cause di scioglimento delle società di capitali).)) (( 1. All' articolo 2484, primo comma, del codice civile dopo il numero 7) è aggiunto il seguente: "7-bis) per l'apertura della procedura di liquidazione giudiziale e della liquidazione contro

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art55`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 45 Determinazione del reddito di capitale 1. Il reddito di capitale è costituito dall'ammontare degli interessi, utili o altri proventi percepiti nel periodo di imposta, senza alcuna deduzione. Nei redditi di cui alle lettere a),

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art118`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 azione dei beni indicati nell'articolo 85, comma 1, lettere c), d) ed e), operata in base alla corretta applicazione di tali principi assume rilievo anche ai fini fiscali. (133) 5. In caso di aumento del capitale della società emittent

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
