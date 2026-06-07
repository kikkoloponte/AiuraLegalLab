# trib_019 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:50 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 66.0s (ret 0.1s + llm 65.7s) |

## Query

> Come si applica la tassazione separata ai redditi pluriennali?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains excerpts from DPR 22 dicembre 1986, n. 917 (Testo Unico delle imposte sui redditi). Specific source_ids provided (urn:nir:stato...).
    *   **Question:** "Come si applica la tassazione separata ai redditi pluriennali?" (How is separate taxation applied to multi-year incomes?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917 Art. 17 (Tassazione separata). Mentions treatment of end-of-service pay (Art. 2120 CC) and equivalent indemnities.
    *   Source [2]: DPR 917 Art. 21 (Determinazione dell'imposta per gli altri redditi tassati separatamente). Mentions heirs/legatees, succession tax deduction.
    *   Source [3]: DPR 917 Art. 4 (Coniugi e figli minori). Mentions community property for separate taxation determination.
    *   Source [4]: DPR 917 Art. 21 (Determinazione dell'imposta per gli altri redditi tassati separatamente). Excludes certain items from letter g) of comma 1 of Art. 17 and imputed to shareholders.
    *   Source [5]: DPR 917 Art. 167 (Tassazione effettiva...). Mentions group taxation, minimum tax.
    *   Source [6]: DPR 917 Art. 118 (Effetti dell'esercizio dell'opzione). Group taxation option effects.
    *   Source [7]: DPR 917 Art. 136 (Distribuzione redditi...). Mentions foreign companies, group taxation abroad.
    *   Source [8]: DPR 917 Art. 167 (Tassazione effettiva...). Deductions from tax determined under comma 8.
    *   Source [9]: DPR 917 Art. 144 (Determinazione dei redditi). Non-commercial entities, distinct categories.
    *   Source [10]: DPR 917 Art. 117 (Tassazione di gruppo...). Group taxation option reference.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "redditi pluriennali" (multi-year incomes).
    *   I need to scan the provided text for keywords like "plurennale", "anni", "periodo", "accumulato".
    *   Source [1] mentions "trattamento di fine rapporto... commisurate alla durata" (duration), but doesn't explicitly discuss multi-year income taxation rules in a general sense.
    *   Source [2], [3], [4], [5], [6], [7], [8], [9], [10] discuss group taxation, heirs, non-commercial entities, etc. None of them explicitly define the rule for "redditi pluriennali" (multi-year incomes) in the context of separate taxation *specifically* as a general rule found in these snippets.
    *   Source [1] Art. 17 mentions specific items taxed separately (TFR). TFR is often calculated based on duration, but the text provided cuts off ("commisurate alla durata").
    *   Crucially, none of the provided source_ids explicitly contain information about "redditi pluriennali" (multi-year incomes) in relation to separate taxation rules beyond specific items like TFR or group taxation.
    *   The packet does not seem to contain the specific article defining how multi-year income is taxed separately (often Art. 17, comma 2 or similar provisions regarding "redditi pluriennali" are usually found in DPR 917 but might be missing from these specific snippets).
    *   Wait, I must check if any snippet implies it. Source [4] mentions "Per gli altri redditi tassati separatamente...". It doesn't mention multi-year.
    *   Since the instruction says "Reason ONLY on facts in the Research Packet", and there is no explicit text about "redditi pluriennali" in the provided snippets, I cannot cite a source for that specific fact if it's not there.
    *   However, I must answer the question based on the packet. If the packet doesn't have the info, I need to state the gap or use `ungrounded_reasoning` (VALUTAZIONE PERSONALE) only if no source exists for a claim. But the instruction says "Every factual claim MUST have a source_id".
    *   Actually, looking closely at Source [1], it talks about Art. 17 Tassazione separata. It lists specific items (TFR). It does not mention multi-year income generally.
    *   Looking at Source [4] (Art. 21), it says "Per gli altri redditi tassati separatamente...".
    *   There is no explicit text in the provided packet that defines the application of separate taxation to *multi-year incomes* specifically as a distinct category beyond what might be implied by TFR or group taxation.
    *   Therefore, I must identify this lack of information in the GAP ANALYSIS section and potentially use `ungrounded_reasoning` for the conclusion if I cannot find a source, OR state that based on the packet, there is no specific rule found.
    *   Wait, the instruction says: "If you don't have the source -> field `ungrounded_reasoning` with prefix 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to claims. If I claim something not in the text, I must mark it as personal evaluation.
    *   However, for a legal analysis task where the packet is limited, if the answer isn't in the packet, I should report that limitation (GAP).
    *   Let's check if "redditi pluriennali" appears in any snippet text provided.
        *   Snippet 1: "...commisurate alla durata" (duration).
        *   Snippet 2: "...successioni..." (successions).
        *   Snippet 3: "...comunione legale..." (community property).
        *   Snippet 4: "...altri redditi tassati separatamente..." (other separately taxed incomes).
        *   Snippet 5-10: Group taxation, non-commercial entities.
    *   None of the snippets explicitly mention "redditi pluriennali".
    *   Therefore, I cannot make a factual claim about how it applies based on these sources without violating the citation contract (unless I use `ungrounded_reasoning` for that specific part).
    *   Best approach: Qualify the scope of separate taxation found in the packet (Art. 17), note the absence of explicit multi-year rules in the provided text, and conclude based on available info or state the gap.
    *   Actually, looking at Source [4] (which is labeled Art. 21 in the metadata but text says "Per gli altri redditi tassati separatamente"), it might be relevant to general separate taxation rules excluding specific ones. But still no mention of "pluriennali".

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains excerpts from DPR 22 dicembre 1986, n. 917 (Testo Unico delle imposte sui redditi). Specific source_ids provided (urn:nir:stato...).
    *   **Question:** "Come si applica la tassazione separata ai redditi pluriennali?" (How is separate taxation applied to multi-year incomes?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917 Art. 17 (Tassazione separata). Mentions treatment of end-of-service pay (Art. 2120 CC) and equivalent indemnities.
    *   Source [2]: DPR 917 Art. 21 (Determinazione dell'imposta per gli altri redditi tassati separatamente). Mentions heirs/legatees, succession tax deduction.
    *   Source [3]: DPR 917 Art. 4 (Coniugi e figli minori). Mentions community property for separate taxation determination.
    *   Source [4]: DPR 917 Art. 21 (Determinazione dell'imposta per gli altri redditi tassati separatamente). Excludes certain items from letter g) of comma 1 of Art. 17 and imputed to shareholders.
    *   Source [5]: DPR 917 Art. 167 (Tassazione effettiva...). Mentions group taxation, minimum tax.
    *   Source [6]: DPR 917 Art. 118 (Effetti dell'esercizio dell'opzione). Group taxation option effects.
    *   Source [7]: DPR 917 Art. 136 (Distribuzione redditi...). Mentions foreign companies, group taxation abroad.
    *   Source [8]: DPR 917 Art. 167 (Tassazione effettiva...). Deductions from tax determined under comma 8.
    *   Source [9]: DPR 917 Art. 144 (Determinazione dei redditi). Non-commercial entities, distinct categories.
    *   Source [10]: DPR 917 Art. 117 (Tassazione di gruppo...). Group taxation option reference.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "redditi pluriennali" (multi-year incomes).
    *   I need to scan the provided text for keywords like "plurennale", "anni", "periodo", "accumulato".
    *   Source [1] mentions "trattamento di fine rapporto... commisurate alla durata" (duration), but doesn't explicitly discuss multi-year income taxation rules in a general sense.
    *   Source [2], [3], [4], [5], [6], [7], [8], [9], [10] discuss group taxation, heirs, non-commercial entities, etc. None of them explicitly define the rule for "redditi pluriennali" (multi-year incomes) in the context of separate taxation *specifically* as a general rule found in these snippets.
    *   Source [1] Art. 17 mentions specific items taxed separately (TFR). TFR is often calculated based on duration, but the text provided cuts off ("commisurate alla durata").
    *   Crucially, none of the provided source_ids explicitly contain information about "redditi pluriennali" (multi-year incomes) in relation to separate taxation rules beyond specific items like TFR or group taxation.
    *   The packet does not seem to contain the specific article defining how multi-year income is taxed separately (often Art. 17, comma 2 or similar provisions regarding "redditi pluriennali" are usually found in DPR 917 but might be missing from these specific snippets).
    *   Wait, I must check if any snippet implies it. Source [4] mentions "Per gli altri redditi tassati separatamente...". It doesn't mention multi-year.
    *   Since the instruction says "Reason ONLY on facts in the Research Packet", and there is no explicit text about "redditi pluriennali" in the provided snippets, I cannot cite a source for that specific fact if it's not there.
    *   However, I must answer the question based on the packet. If the packet doesn't have the info, I need to state the gap or use `ungrounded_reasoning` (VALUTAZIONE PERSONALE) only if no source exists for a claim. But the instruction says "Every factual claim MUST have a source_id".
    *   Actually, looking closely at Source [1], it talks about Art. 17 Tassazione separata. It lists specific items (TFR). It does not mention multi-year income generally.
    *   Looking at Source [4] (Art. 21), it says "Per gli altri redditi tassati separatamente...".
    *   There is no explicit text in the provided packet that defines the application of separate taxation to *multi-year incomes* specifically as a distinct category beyond what might be implied by TFR or group taxation.
    *   Therefore, I must identify this lack of information in the GAP ANALYSIS section and potentially use `ungrounded_reasoning` for the conclusion if I cannot find a source, OR state that based on the packet, there is no specific rule found.
    *   Wait, the instruction says: "If you don't have the source -> field `ungrounded_reasoning` with prefix 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to claims. If I claim something not in the text, I must mark it as personal evaluation.
    *   However, for a legal analysis task where the packet is limited, if the answer isn't in the packet, I should report that limitation (GAP).
    *   Let's check if "redditi pluriennali" appears in any snippet text provided.
        *   Snippet 1: "...commisurate alla durata" (duration).
        *   Snippet 2: "...successioni..." (successions).
        *   Snippet 3: "...comunione legale..." (community property).
        *   Snippet 4: "...altri redditi tassati separatamente..." (other separately taxed incomes).
        *   Snippet 5-10: Group taxation, non-commercial entities.
    *   None of the snippets explicitly mention "redditi pluriennali".
    *   Therefore, I cannot make a factual claim about how it applies based on these sources without violating the citation contract (unless I use `ungrounded_reasoning` for that specific part).
    *   Best approach: Qualify the scope of separate taxation found in the packet (Art. 17), note the absence of explicit multi-year rules in the provided text, and conclude based on available info or state the gap.
    *   Actually, looking at Source [4] (which is labeled Art. 21 in the metadata but text says "Per gli altri redditi tassati separatamente"), it might be relevant to general separate taxation rules excluding specific ones. But still no mention of "pluriennali".

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23` | 5.6302 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29` | 3.8535 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art5` | 3.4786 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29` | 2.6748 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207` | -0.2570 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art151` | -0.6571 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172` | -1.1077 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207` | -1.9599 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art181` | -2.4764 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art150` | -2.8269 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 17 Tassazione separata 1. L'imposta si applica separatamente sui seguenti redditi: a) trattamento di fine rapporto di cui all' articolo 2120 del codice civile e indennità equipollenti, comunque denominate, commisurate alla durata

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 7 si procede alla tassazione separata nei confronti degli eredi e dei legatari; l'imposta dovuta da ciascuno di essi è determinata applicando all'ammontare percepito, diminuito della quota dell'imposta sulle successioni proporzionale a

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art5`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 4 ((Coniugi e figli minori 1. Ai Fini della determinazione del reddito complessivo o della tassazione separata: a) i redditi dei beni che formano oggetto della comunione legale di cui agli articoli 177 e seguenti del codice civile

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 21 Determinazione dell'imposta per gli altri redditi tassati separatamente 1. Per gli altri redditi tassati separatamente, ad esclusione di quelli in cui alla lettera g) del comma 1 dell'articolo 17 e di quelli imputati ai soci in

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  redditi)) rilevanti relativi alle imprese ed entità del gruppo soggette all'imposta minima nazionale equivalente calcolata in maniera unitaria con il soggetto controllato non residente. (227) ((238)) 4-ter. La tassazione effettiva di

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art151`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 118 Effetti dell'esercizio dell'opzione 1. L'esercizio dell'opzione per la tassazione di gruppo di cui all'articolo 117 comporta la determinazione di un reddito complessivo globale corrispondente alla somma algebrica dei redditi c

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  distribuiti i redditi prodotti negli esercizi più recenti. ((6. Nel caso in cui nello stesso Paese estero siano presenti più società controllate e la legislazione locale preveda una forma di tassazione di gruppo analoga a quella di cu

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 'aliquota media applicata sul reddito del soggetto cui sono imputati e, comunque, non inferiore all'aliquota ordinaria dell'imposta sul reddito delle società. 9. Dall'imposta determinata ai sensi del comma 8 sono ammesse in detrazione,

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art181`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 144 Determinazione dei redditi 1. I redditi e le perdite che concorrono a formare il reddito complessivo degli enti non commerciali sono determinati distintamente per ciascuna categoria in base al risultato complessivo di tutti i

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art150`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 articolo 117 del testo unico delle imposte sui redditi approvato con decreto del Presidente della Repubblica 22 dicembre 1986, n. 917 . Il medesimo provvedimento disciplina l'applicazione della disposizione di cui al presente articolo

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
