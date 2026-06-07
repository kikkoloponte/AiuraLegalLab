# cross_014 — tributario+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:52 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 68.3s (ret 0.1s + llm 68.0s) |

## Query

> Come interagiscono le procedure concorsuali (fallimento) con i crediti tributari?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Come interagiscono le procedure concorsuali (fallimento) con i crediti tributari?" (How do insolvency proceedings (bankruptcy) interact with tax credits?)
    *   **Input Packet:** Contains 10 sources (Regio Decreto 262/1942, DLgs 14/2019 various articles).

2.  **Analyze the Research Packet Sources:**
    *   [1] RD 262/1942 Art. 2394-bis: Actions of liability in insolvency proceedings (liquidazione giudiziale, concordato liquidatorio, etc.). Not directly about tax credits priority.
    *   [2] DLgs 14/2019 Art. 288: Group companies in separate insolvency procedures. Not directly about tax credits.
    *   [3] DLgs 14/2019 Art. 88: Treatment of tax and contributory credits in concordato (proposal for payment, partial or deferred). This is relevant to tax credits interaction with insolvency (specifically concordato).
    *   [4] DLgs 14/2019 Art. 349: Substitution of terms "fallimento", "procedura fallimentare", "fallito" with new terms (liquidazione giudiziale, etc.). Relevant for terminology in bankruptcy context.
    *   [5] DLgs 14/2019 Art. 158: Non-monetary credits ranking according to value at opening date. Not specifically tax credits priority rules but general ranking.
    *   [6] DLgs 14/2019 Art. 390: Transitional discipline for bankruptcy and concordato appeals.
    *   [7] RD 262/1942 Art. 506 (labeled as Art. 506 in text but source says Art. 595? Wait, check text): Text says "Art. 506." Title says "Art. 595". This is a discrepancy in the packet provided. I must use the `source_id` and respect the text provided. The text mentions publication under art. 498, continuation of executions, residual price. Not directly about tax credits priority.
    *   [8] DPR 917/1986 Art. 227 (labeled as Art. 183 in source_id? Wait, check text): Title says "Art. 183". Text mentions income of enterprise between start and declaration of bankruptcy or liquidation coatta. Relevant to tax treatment during insolvency.
    *   [9] DLgs 14/2019 Art. 6: Prededucibilità dei crediti (Priority of credits). Lists expenses, compensation for functions in organs. Does not explicitly list tax credits here as priority over others, but mentions "Oltre ai crediti così espressamente qualificati dalla legge" (Besides credits expressly qualified by law).
    *   [10] DLgs 14/2019 Art. 366: Evidence and documents in proceedings.

3.  **Synthesize the Answer based on Packet:**
    *   The question asks about interaction between insolvency (fallimento) and tax credits.
    *   Source [3] explicitly mentions "Trattamento dei crediti tributari e contributivi" (Treatment of tax and contributory credits) in concordato proceedings, allowing payment proposals for taxes.
    *   Source [4] notes the substitution of terms like "fallimento" with new terminology (liquidazione giudiziale), implying a shift in context but maintaining the concept of insolvency procedures.
    *   Source [9] discusses priority credits ("prededucibili"), mentioning expenses and organ functions, but refers to other laws for expressly qualified credits (which might include taxes under general law not fully detailed here).
    *   Source [8] mentions income treatment during bankruptcy/liquidation coatta.
    *   Source [1], [2], [5], [6], [7], [10] are less directly relevant to the specific "tax credit interaction" question but provide context on liability, group procedures, non-monetary credits, transitional rules, execution suspension, and evidence.

4.  **Drafting the JSON Content (adhering to constraints):**
    *   **Step 1: QUALIFICAZIONE:** Define the legal issue (interaction of tax credits with insolvency). Cite sources that define the context (e.g., [3] for concordato treatment, [4] for terminology shift from fallimento).
    *   **Step 2: NORMA APPLICABILE:** Specific articles. Source [3] Art. 88 is key for tax credits in concordato. Source [9] Art. 6 mentions priority credits generally. Source [4] Art. 349 defines the terminology shift (fallimento -> liquidazione giudiziale).
    *   **Step 3: GIURISPRUDENZA:** The packet does not contain case law/jurisprudence sources. I must state this limitation or use `ungrounded_reasoning` if needed, but better to note absence in GAP ANALYSIS. Wait, instruction says "If no source -> ungrounded_reasoning". But for Jurisprudence step, if there is no jurisprudence in the packet, I should probably indicate that based on available text or use `ungrounded_reasoning` prefix if making a claim about case law not present. However, the prompt asks to analyze *according to the schema*. If the packet lacks jurisprudence, I cannot cite one. I will note the absence or focus on statutory interpretation from the provided texts. Actually, looking at the instruction: "Ogni affermazione fattuale DEVE avere un source_id". If I claim there is no jurisprudence, that's a fact about the packet. But usually, this step requires citing case law if available. Since none are in the packet, I will state that the analysis relies on statutory provisions provided.
    *   **Step 4: VALUTAZIONE:** Assess confidence based on sources. Source [3] is specific to tax credits in concordato. Source [9] mentions priority but doesn't explicitly list taxes as priority here (refers to law). Confidence might be MEDIUM because the packet focuses more on procedural aspects and concordato than general bankruptcy tax priority rules which are often in RD 262/1942 or TUIR not fully detailed.
    *   **Step 5: GAP ANALYSIS:** What is missing? Specific articles of RD 262/1942 regarding tax credit priority (e.g., Art. 73, etc.) are not in the packet. The packet lacks explicit text on "fallimento" vs "liquidazione giudiziale" specific tax rules beyond terminology substitution.

5.  **Refining Citations:**
    *   Must use `source_id` exactly as provided (e.g., `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`).
    *   Claim type must be FACT.
    *   Source authority: NORMATTIVA for laws, maybe others if applicable (but all seem normative).
    *   GU reference: Only available in source [1] ("GU n.79 del 04/04/1942"). Others don't have it explicitly in the text provided, but I should check if I can infer or leave blank? The schema example shows

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Come interagiscono le procedure concorsuali (fallimento) con i crediti tributari?" (How do insolvency proceedings (bankruptcy) interact with tax credits?)
    *   **Input Packet:** Contains 10 sources (Regio Decreto 262/1942, DLgs 14/2019 various articles).

2.  **Analyze the Research Packet Sources:**
    *   [1] RD 262/1942 Art. 2394-bis: Actions of liability in insolvency proceedings (liquidazione giudiziale, concordato liquidatorio, etc.). Not directly about tax credits priority.
    *   [2] DLgs 14/2019 Art. 288: Group companies in separate insolvency procedures. Not directly about tax credits.
    *   [3] DLgs 14/2019 Art. 88: Treatment of tax and contributory credits in concordato (proposal for payment, partial or deferred). This is relevant to tax credits interaction with insolvency (specifically concordato).
    *   [4] DLgs 14/2019 Art. 349: Substitution of terms "fallimento", "procedura fallimentare", "fallito" with new terms (liquidazione giudiziale, etc.). Relevant for terminology in bankruptcy context.
    *   [5] DLgs 14/2019 Art. 158: Non-monetary credits ranking according to value at opening date. Not specifically tax credits priority rules but general ranking.
    *   [6] DLgs 14/2019 Art. 390: Transitional discipline for bankruptcy and concordato appeals.
    *   [7] RD 262/1942 Art. 506 (labeled as Art. 506 in text but source says Art. 595? Wait, check text): Text says "Art. 506." Title says "Art. 595". This is a discrepancy in the packet provided. I must use the `source_id` and respect the text provided. The text mentions publication under art. 498, continuation of executions, residual price. Not directly about tax credits priority.
    *   [8] DPR 917/1986 Art. 227 (labeled as Art. 183 in source_id? Wait, check text): Title says "Art. 183". Text mentions income of enterprise between start and declaration of bankruptcy or liquidation coatta. Relevant to tax treatment during insolvency.
    *   [9] DLgs 14/2019 Art. 6: Prededucibilità dei crediti (Priority of credits). Lists expenses, compensation for functions in organs. Does not explicitly list tax credits here as priority over others, but mentions "Oltre ai crediti così espressamente qualificati dalla legge" (Besides credits expressly qualified by law).
    *   [10] DLgs 14/2019 Art. 366: Evidence and documents in proceedings.

3.  **Synthesize the Answer based on Packet:**
    *   The question asks about interaction between insolvency (fallimento) and tax credits.
    *   Source [3] explicitly mentions "Trattamento dei crediti tributari e contributivi" (Treatment of tax and contributory credits) in concordato proceedings, allowing payment proposals for taxes.
    *   Source [4] notes the substitution of terms like "fallimento" with new terminology (liquidazione giudiziale), implying a shift in context but maintaining the concept of insolvency procedures.
    *   Source [9] discusses priority credits ("prededucibili"), mentioning expenses and organ functions, but refers to other laws for expressly qualified credits (which might include taxes under general law not fully detailed here).
    *   Source [8] mentions income treatment during bankruptcy/liquidation coatta.
    *   Source [1], [2], [5], [6], [7], [10] are less directly relevant to the specific "tax credit interaction" question but provide context on liability, group procedures, non-monetary credits, transitional rules, execution suspension, and evidence.

4.  **Drafting the JSON Content (adhering to constraints):**
    *   **Step 1: QUALIFICAZIONE:** Define the legal issue (interaction of tax credits with insolvency). Cite sources that define the context (e.g., [3] for concordato treatment, [4] for terminology shift from fallimento).
    *   **Step 2: NORMA APPLICABILE:** Specific articles. Source [3] Art. 88 is key for tax credits in concordato. Source [9] Art. 6 mentions priority credits generally. Source [4] Art. 349 defines the terminology shift (fallimento -> liquidazione giudiziale).
    *   **Step 3: GIURISPRUDENZA:** The packet does not contain case law/jurisprudence sources. I must state this limitation or use `ungrounded_reasoning` if needed, but better to note absence in GAP ANALYSIS. Wait, instruction says "If no source -> ungrounded_reasoning". But for Jurisprudence step, if there is no jurisprudence in the packet, I should probably indicate that based on available text or use `ungrounded_reasoning` prefix if making a claim about case law not present. However, the prompt asks to analyze *according to the schema*. If the packet lacks jurisprudence, I cannot cite one. I will note the absence or focus on statutory interpretation from the provided texts. Actually, looking at the instruction: "Ogni affermazione fattuale DEVE avere un source_id". If I claim there is no jurisprudence, that's a fact about the packet. But usually, this step requires citing case law if available. Since none are in the packet, I will state that the analysis relies on statutory provisions provided.
    *   **Step 4: VALUTAZIONE:** Assess confidence based on sources. Source [3] is specific to tax credits in concordato. Source [9] mentions priority but doesn't explicitly list taxes as priority here (refers to law). Confidence might be MEDIUM because the packet focuses more on procedural aspects and concordato than general bankruptcy tax priority rules which are often in RD 262/1942 or TUIR not fully detailed.
    *   **Step 5: GAP ANALYSIS:** What is missing? Specific articles of RD 262/1942 regarding tax credit priority (e.g., Art. 73, etc.) are not in the packet. The packet lacks explicit text on "fallimento" vs "liquidazione giudiziale" specific tax rules beyond terminology substitution.

5.  **Refining Citations:**
    *   Must use `source_id` exactly as provided (e.g., `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`).
    *   Claim type must be FACT.
    *   Source authority: NORMATTIVA for laws, maybe others if applicable (but all seem normative).
    *   GU reference: Only available in source [1] ("GU n.79 del 04/04/1942"). Others don't have it explicitly in the text provided, but I should check if I can infer or leave blank? The schema example shows

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2463` | 0.3055 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art288` | 0.0924 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -0.5600 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art349` | -2.8503 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art158` | -3.6778 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art390` | -4.1087 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art595` | -4.9697 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227` | -5.1816 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6` | -7.0740 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art366` | -7.1898 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art19`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2463`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2394-bis. (Azioni di responsabilità nelle procedure concorsuali). In caso ((di liquidazione giudiziale, concordato liquidatorio,)) , liquidazione coatta amministrativa e amministrazione straordinaria le azioni di responsabilità previste dai precedenti articol

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art288`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 288 Procedure concorsuali autonome di imprese appartenenti allo stesso gruppo 1. Nel caso in cui più imprese appartenenti a un medesimo gruppo siano assoggettate a separate procedure di liquidazione giudiziale ovvero a separate procedure di concordato

**[3]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 88 (( (Trattamento dei crediti tributari e contributivi). )) (( 1. Con il piano di concordato il debitore, esclusivamente mediante proposta presentata ai sensi del presente articolo, può proporre il pagamento, parziale o anche dilazionato, dei tributi

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art349`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 349 Sostituzione dei termini fallimento e fallito 1. Nelle disposizioni normative vigenti i termini «fallimento», «procedura fallimentare», «fallito» nonchè le espressioni dagli stessi termini derivate devono intendersi sostituite, rispettivamente, con

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art158`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 158 Crediti non pecuniari 1. I crediti non scaduti, aventi per oggetto una prestazione in danaro determinata con riferimento ad altri valori o aventi per oggetto una prestazione diversa dal danaro, concorrono secondo il loro valore alla data di apertur

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art390`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 390 Disciplina transitoria 1. I ricorsi per dichiarazione di fallimento e le proposte di concordato fallimentare, i ricorsi per l'omologazione degli accordi di ristrutturazione, per l'apertura del concordato preventivo, per l'accertamento dello stato d

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art595`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 506. (Procedure individuali). Eseguita la pubblicazione prescritta dal terzo comma dell'art. 498, non possono essere promosse procedure esecutive a istanza dei creditori. Possono tuttavia essere continuate quelle in corso, ma la parte di prezzo che residua do

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 183 Fallimento e liquidazione coatta 1. Nei casi di fallimento e di liquidazione coatta amministrativa il reddito di impresa relativo al periodo compreso tra l'inizio dell'esercizio e la dichiarazione di fallimento o il provvedime

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 6 (Prededucibilità dei crediti) 1. Oltre ai crediti così espressamente qualificati dalla legge, sono prededucibili: a) i crediti relativi a spese e compensi per le prestazioni rese ((nell'esercizio delle funzioni rientranti nella competenza dell'organi

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art366`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 è l'indicazione dei mezzi di prova e dei documenti prodotti. L'intervento di qualunque interessato non può avere luogo oltre il termine stabilito per la costituzione delle parti resistenti con le modalità per queste previste. All'udienza, il collegio, senti

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
