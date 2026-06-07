# trib_016 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:23 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 25.7s (ret 0.2s + llm 25.2s) |

## Query

> Quali sono i limiti alla compensazione dei crediti fiscali?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 sources (Regio Decreto 262/1942, DLgs 14/2019, Legge 212/2000, Regio Decreto 1443/1940, DPR 917/1986).
    *   **Question:** "Quali sono i limiti alla compensazione dei crediti fiscali?" (What are the limits to offsetting tax credits?)

2.  **Analyze the Research Packet for Relevant Information:**
    *   Source [1]: Art. 1824 R.D. 262/1942 (Civil Code). Excludes non-compensable credits from current account; excludes foreign to enterprise credits between entrepreneurs. Not directly about tax limits, but general compensation rules.
    *   Source [2]: DLgs 14/2019 Art. 6. Prededucibility of credits (expenses/remuneration for functions). Mentions "compensazione dei crediti" in context of liquidation? Text cuts off ("nell'esercizio delle funzioni rientranti nella competenza dell'organi").
    *   Source [3]: Legge 212/2000 Art. 8. Exclusion from compensation of tax credits (imposte sui redditi e quelle per le quali è prevista la rivalsa). Text: "della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti...". This is crucial.
    *   Source [4]: R.D. 1443/1940 Art. 817-bis (Civil Procedure Code). Arbitrators competent for compensation exception even if counter-credit not in arbitration agreement. Procedural aspect.
    *   Source [5]: DLgs 14/2019 Art. 155. Compensation in judicial liquidation. Creditors can offset debts against debtor's assets subject to liquidation, even if credits not due before opening.
    *   Source [6]: DPR 917/1986 Art. 99 (Tax Code). Fiscal and contributory burdens. "Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione." (Income taxes and those with clawback are not deductible). This is about deduction/offsetting against income tax liability, often linked to compensation concepts but specifically about deductibility.
    *   Source [7]: R.D. 262/1942 Art. 1250 (Civil Code). Compensation prejudicial to third parties (usufruct/pawn rights).
    *   Source [8]: R.D. 262/1942 Art. 1302 (Civil Code). Solidary debtors/creditors compensation limits.
    *   Source [9]: DLgs 14/2019 Art. 156. Non-interest bearing credits in liquidation.
    *   Source [10]: R.D. 262/1942 Art. 1246 (Civil Code). Cases where compensation does not occur (restitution of unjustly deprived things, etc.).

3.  **Synthesize the Answer based on Sources:**
    *   The core question is about limits to offsetting tax credits (*compensazione dei crediti fiscali*).
    *   Source [3] (Legge 212/2000 Art. 8) explicitly mentions exclusion from compensation for certain tax credits ("della compensazione dei crediti... detta esclusione opera a prescindere dalla tipologia e dall'importo"). This is the primary limit found in the packet regarding tax credits specifically.
    *   Source [6] (DPR 917/1986 Art. 99) mentions income taxes and those with clawback are not deductible ("non sono ammesse in deduzione"). While "deduction" isn't exactly "compensation", it relates to the ability to offset tax liabilities against other debts/income, often treated as a limit on fiscal credits' utility or deductibility. However, Source [3] is more direct about *compensazione*.
    *   General Civil Code rules apply (Source [1], [7], [8], [10]) regarding general compensation limits (third parties, solidary debtors, non-compensable titles). These are general limits applicable to tax credits unless specified otherwise.
    *   Source [5] mentions compensation in judicial liquidation context for creditors against debtor's assets.

4.  **Drafting the JSON Content:**
    *   **Step 1: QUALIFICAZIONE.** Define the legal issue (limits on offsetting tax credits). Cite general civil code rules and specific fiscal exclusion laws found in packet.
        *   Claim: General compensation rules apply unless excluded. Source [1], [7], [8], [10].
        *   Claim: Specific exclusion for income taxes/clawback taxes from deduction/compensation context. Source [3], [6].
    *   **Step 2: NORMA APPLICABILE.** List specific articles.
        *   Art. 8 Legge 212/2000 (Source [3]).
        *   Art. 99 DPR 917/1986 (Source [6]).
        *   Civil Code Articles on compensation limits (Source [1], [7], [8], [10]).
    *   **Step 3: GIURISPRUDENZA.** The packet does not contain case law/jurisprudence text, only statutes. I must state this limitation or rely on statutory interpretation if no jurisprudence source exists. Since the instruction says "Reason ONLY on facts in the Research Packet", and there are no case law sources (source_id like "Cassazione n. ..."), I cannot cite jurisprudence. I will note the absence of specific case law in the packet or focus on statutory interpretation. Wait, Source [4] mentions arbitrators competence for compensation exception. That's procedural. I should mention that general civil rules apply unless fiscal laws exclude them.
    *   **Step 4: VALUTAZIONE.** Assess confidence based on available sources. High confidence on the exclusion rule (Source [3]), Medium on general limits due to lack of specific tax jurisprudence in packet.
    *   **Step 5: GAP ANALYSIS.** What is missing? Specific case law on tax compensation limits, detailed text of Art. 8 comma 1 of Law 212/2000 (text cuts off), distinction between deduction and compensation in tax context beyond Source [6].

5.  **Refining Citations:**
    *   Must use `source_id` exactly as provided (e.g., "urn:nir:stato:legge:2000-07-27;212~art8").
    *   Claim type must be FACT.
    *   Source authority: NORMATTIVA for statutes, PROC_CIVILE for procedural codes, etc. (Based on `fonte` field in packet).
    *   GU reference: Only if present in source text. Source [1] has "GU n.79 del 04/04/1942". Others don't explicitly show it in the provided text snippet, but I should check if I can infer or leave blank. The instruction says "gu_reference": "GU n.79...". I

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 sources (Regio Decreto 262/1942, DLgs 14/2019, Legge 212/2000, Regio Decreto 1443/1940, DPR 917/1986).
    *   **Question:** "Quali sono i limiti alla compensazione dei crediti fiscali?" (What are the limits to offsetting tax credits?)

2.  **Analyze the Research Packet for Relevant Information:**
    *   Source [1]: Art. 1824 R.D. 262/1942 (Civil Code). Excludes non-compensable credits from current account; excludes foreign to enterprise credits between entrepreneurs. Not directly about tax limits, but general compensation rules.
    *   Source [2]: DLgs 14/2019 Art. 6. Prededucibility of credits (expenses/remuneration for functions). Mentions "compensazione dei crediti" in context of liquidation? Text cuts off ("nell'esercizio delle funzioni rientranti nella competenza dell'organi").
    *   Source [3]: Legge 212/2000 Art. 8. Exclusion from compensation of tax credits (imposte sui redditi e quelle per le quali è prevista la rivalsa). Text: "della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti...". This is crucial.
    *   Source [4]: R.D. 1443/1940 Art. 817-bis (Civil Procedure Code). Arbitrators competent for compensation exception even if counter-credit not in arbitration agreement. Procedural aspect.
    *   Source [5]: DLgs 14/2019 Art. 155. Compensation in judicial liquidation. Creditors can offset debts against debtor's assets subject to liquidation, even if credits not due before opening.
    *   Source [6]: DPR 917/1986 Art. 99 (Tax Code). Fiscal and contributory burdens. "Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione." (Income taxes and those with clawback are not deductible). This is about deduction/offsetting against income tax liability, often linked to compensation concepts but specifically about deductibility.
    *   Source [7]: R.D. 262/1942 Art. 1250 (Civil Code). Compensation prejudicial to third parties (usufruct/pawn rights).
    *   Source [8]: R.D. 262/1942 Art. 1302 (Civil Code). Solidary debtors/creditors compensation limits.
    *   Source [9]: DLgs 14/2019 Art. 156. Non-interest bearing credits in liquidation.
    *   Source [10]: R.D. 262/1942 Art. 1246 (Civil Code). Cases where compensation does not occur (restitution of unjustly deprived things, etc.).

3.  **Synthesize the Answer based on Sources:**
    *   The core question is about limits to offsetting tax credits (*compensazione dei crediti fiscali*).
    *   Source [3] (Legge 212/2000 Art. 8) explicitly mentions exclusion from compensation for certain tax credits ("della compensazione dei crediti... detta esclusione opera a prescindere dalla tipologia e dall'importo"). This is the primary limit found in the packet regarding tax credits specifically.
    *   Source [6] (DPR 917/1986 Art. 99) mentions income taxes and those with clawback are not deductible ("non sono ammesse in deduzione"). While "deduction" isn't exactly "compensation", it relates to the ability to offset tax liabilities against other debts/income, often treated as a limit on fiscal credits' utility or deductibility. However, Source [3] is more direct about *compensazione*.
    *   General Civil Code rules apply (Source [1], [7], [8], [10]) regarding general compensation limits (third parties, solidary debtors, non-compensable titles). These are general limits applicable to tax credits unless specified otherwise.
    *   Source [5] mentions compensation in judicial liquidation context for creditors against debtor's assets.

4.  **Drafting the JSON Content:**
    *   **Step 1: QUALIFICAZIONE.** Define the legal issue (limits on offsetting tax credits). Cite general civil code rules and specific fiscal exclusion laws found in packet.
        *   Claim: General compensation rules apply unless excluded. Source [1], [7], [8], [10].
        *   Claim: Specific exclusion for income taxes/clawback taxes from deduction/compensation context. Source [3], [6].
    *   **Step 2: NORMA APPLICABILE.** List specific articles.
        *   Art. 8 Legge 212/2000 (Source [3]).
        *   Art. 99 DPR 917/1986 (Source [6]).
        *   Civil Code Articles on compensation limits (Source [1], [7], [8], [10]).
    *   **Step 3: GIURISPRUDENZA.** The packet does not contain case law/jurisprudence text, only statutes. I must state this limitation or rely on statutory interpretation if no jurisprudence source exists. Since the instruction says "Reason ONLY on facts in the Research Packet", and there are no case law sources (source_id like "Cassazione n. ..."), I cannot cite jurisprudence. I will note the absence of specific case law in the packet or focus on statutory interpretation. Wait, Source [4] mentions arbitrators competence for compensation exception. That's procedural. I should mention that general civil rules apply unless fiscal laws exclude them.
    *   **Step 4: VALUTAZIONE.** Assess confidence based on available sources. High confidence on the exclusion rule (Source [3]), Medium on general limits due to lack of specific tax jurisprudence in packet.
    *   **Step 5: GAP ANALYSIS.** What is missing? Specific case law on tax compensation limits, detailed text of Art. 8 comma 1 of Law 212/2000 (text cuts off), distinction between deduction and compensation in tax context beyond Source [6].

5.  **Refining Citations:**
    *   Must use `source_id` exactly as provided (e.g., "urn:nir:stato:legge:2000-07-27;212~art8").
    *   Claim type must be FACT.
    *   Source authority: NORMATTIVA for statutes, PROC_CIVILE for procedural codes, etc. (Based on `fonte` field in packet).
    *   GU reference: Only if present in source text. Source [1] has "GU n.79 del 04/04/1942". Others don't explicitly show it in the provided text snippet, but I should check if I can infer or leave blank. The instruction says "gu_reference": "GU n.79...". I

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1888` | 3.9508 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6` | 3.1663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art8` | 2.6132 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art1011` | 2.3236 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155` | 2.0325 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | 1.9891 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1295` | 0.1879 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1347` | -0.1364 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art156` | -0.8046 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1291` | -1.5055 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-07-09;241~art17`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1888`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1824. (Crediti esclusi dal conto corrente). Sono esclusi dal conto corrente i crediti che non sono suscettibili di compensazione. Qualora il contratto intervenga tra imprenditori, s'intendono esclusi dal conto i crediti estranei alle rispettive imprese.

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 6 (Prededucibilità dei crediti) 1. Oltre ai crediti così espressamente qualificati dalla legge, sono prededucibili: a) i crediti relativi a spese e compensi per le prestazioni rese ((nell'esercizio delle funzioni rientranti nella competenza dell'organi

**[3]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

**[4]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art1011`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 817-bis. (( (Compensazione).)) ((Gli arbitri sono competenti a conoscere dell'eccezione di compensazione, nei limiti del valore della domanda, anche se il controcredito non è compreso nell'ambito della convenzione di arbitrato.))

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 155 Compensazione 1. I creditori possono opporre in compensazione dei loro debiti verso il debitore il cui patrimonio è sottoposto alla liquidazione giudiziale i propri crediti verso quest'ultimo, ancorchè non scaduti prima dell'apertura della procedur

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1295`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1250. (Compensazione rispetto ai terzi). La compensazione non si verifica in pregiudizio dei terzi che hanno acquistato diritti di usufrutto o di pegno su uno dei crediti.

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1347`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1302. (Compensazione). Ciascuno dei debitori in solido può opporre in compensazione il credito di un condebitore solo fino alla concorrenza della parte di quest'ultimo. A uno dei creditori in solido il debitore può opporre in compensazione ciò che gli è dovut

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art156`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 156 Crediti infruttiferi 1. I crediti infruttiferi non ancora scaduti alla data dell'apertura della liquidazione giudiziale sono ammessi al passivo per l'intera somma. Tuttavia ad ogni singola ripartizione saranno detratti gli interessi composti, in ra

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1291`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1246. (Casi in cui la compensazione non si verifica). La compensazione si verifica qualunque sia il titolo dell'uno o dell'altro debito, eccettuati i casi: 1) di credito per la restituzione di cose di cui il proprietario sia stato ingiustamente spogliato; 2)

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
