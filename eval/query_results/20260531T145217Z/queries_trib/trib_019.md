# trib_019 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:25 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 26.1s (ret 0.3s + llm 25.6s) |

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
    *   **Input Packet:** Contains excerpts from DPR 917/1986 (and one older DPR 600/1973).
    *   **Question:** "Come si applica la tassazione separata ai redditi pluriennali?" (How is separate taxation applied to multi-year incomes?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917/86, Art. 17 (Tassazione separata). Mentions TFR (Art. 2120 CC) and equivalent indemnities commensurate with duration.
    *   Source [2]: DPR 917/86, Art. 24 (Non residenti). Tax on total income + separately taxed incomes, except where specified.
    *   Source [3]: DPR 917/86, Art. 21 (Eredi e legatari). Separate taxation for heirs/legatees.
    *   Source [4]: DPR 917/86, Art. 4 (Coniugi e figli minori). Community property rules.
    *   Source [5]: DPR 917/86, Art. 21 (Other separately taxed incomes). Excludes Art. 17(g) and imputed to shareholders.
    *   Source [6]: DPR 917/86, Art. 3 (Base imponibile). Total income for residents vs non-residents.
    *   Source [7]: DPR 917/86, Art. 167 (Group taxation context?). Text seems fragmented ("redditi rilevanti relativi alle imprese...").
    *   Source [8]: DPR 917/86, Art. 118 (Effects of group option). Global income determination.
    *   Source [9]: DPR 917/86, Art. 136 (Distribution of profits?). Text fragmented ("distribuiti i redditi prodotti negli esercizi più recenti").
    *   Source [10]: DPR 600/73, Art. 40 (Rectification of declarations).

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "redditi pluriennali" (multi-year incomes).
    *   I need to check if any source in the packet explicitly discusses "redditi pluriennali".
    *   Scanning sources:
        *   [1] DPR 917/86 Art. 17: Mentions TFR and indemnities commensurate with duration (commisurate alla durata). This implies a link to time/duration, but doesn't explicitly say "pluriennali" in the text provided.
        *   [2] DPR 917/86 Art. 24: Non-residents.
        *   [3] DPR 917/86 Art. 21: Heirs/legatees.
        *   [4] DPR 917/86 Art. 4: Spouses/minors.
        *   [5] DPR 917/86 Art. 21: Other separately taxed incomes.
        *   [6] DPR 917/86 Art. 3: Base taxable income.
        *   [7] DPR 917/86 Art. 167: Group taxation context (fragmented).
        *   [8] DPR 917/86 Art. 118: Group option effects.
        *   [9] DPR 917/86 Art. 136: Distribution of profits (fragmented).
        *   [10] DPR 600/73 Art. 40: Rectification.
    *   **Critical Finding:** None of the provided text snippets explicitly mention "redditi pluriennali" (multi-year incomes) in a way that defines their taxation rules directly within the context of the question's specific phrasing, except potentially under the umbrella of TFR or indemnities commensurate with duration (Source [1]). However, standard Italian tax law knowledge suggests TFR is often treated as separate taxation. The packet text for Source [1] says "indennità equipollenti... commisurate alla durata".
    *   **Constraint Check:** I must reason ONLY on facts in the Research Packet. If the packet does not contain information about "redditi pluriennali" specifically, I cannot invent it. I must state what is available or note the gap.
    *   The question asks "How is separate taxation applied to multi-year incomes?".
    *   Source [1] mentions TFR and indemnities commensurate with duration (Art. 2120 CC). This is a form of income often associated with long-term service, but the text doesn't explicitly use the term "pluriennali".
    *   Source [5] mentions "Per gli altri redditi tassati separatamente... ad esclusione di quelli in cui alla lettera g) del comma 1 dell'articolo 17". This implies there are other separately taxed incomes.
    *   There is no explicit text defining the application to "redditi pluriennali" specifically (e.g., averaging over years, specific rates for multi-year).
    *   Therefore, I must qualify based on what IS in the packet regarding separate taxation generally and note if specific info on "pluriennali" is missing or infer from TFR/duration clauses.
    *   Actually, looking closely at Source [1]: "indennità equipollenti... commisurate alla durata". This touches on duration.
    *   However, the prompt instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   If the packet doesn't explicitly define rules for "redditi pluriennali", I cannot claim specific rules exist based on external knowledge. I must report what is in the text or identify the gap.
    *   Wait, Source [1] Art 17 lists TFR and indemnities commensurate with duration as subject to separate taxation. This is the closest link.
    *   The question asks about "redditi pluriennali". In Italian tax law, this often refers to specific scenarios (like certain bonuses or deferred income). But based *strictly* on the packet provided:
        *   Source [1] establishes TFR and duration-based indemnities are taxed separately.
        *   Source [5] establishes other separately taxed incomes exist but excludes Art 17(g) and shareholder imputed ones.
    *   I need to be careful not to hallucinate rules about "pluriennali" if the text doesn't say it. I will focus on the TFR/Duration aspect found in Source [1] as the relevant separate taxation mechanism for income linked to duration (which implies multi-year service).
    *   Actually, looking at the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
    *   So if I can't find a source for "pluriennali", I must use

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains excerpts from DPR 917/1986 (and one older DPR 600/1973).
    *   **Question:** "Come si applica la tassazione separata ai redditi pluriennali?" (How is separate taxation applied to multi-year incomes?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917/86, Art. 17 (Tassazione separata). Mentions TFR (Art. 2120 CC) and equivalent indemnities commensurate with duration.
    *   Source [2]: DPR 917/86, Art. 24 (Non residenti). Tax on total income + separately taxed incomes, except where specified.
    *   Source [3]: DPR 917/86, Art. 21 (Eredi e legatari). Separate taxation for heirs/legatees.
    *   Source [4]: DPR 917/86, Art. 4 (Coniugi e figli minori). Community property rules.
    *   Source [5]: DPR 917/86, Art. 21 (Other separately taxed incomes). Excludes Art. 17(g) and imputed to shareholders.
    *   Source [6]: DPR 917/86, Art. 3 (Base imponibile). Total income for residents vs non-residents.
    *   Source [7]: DPR 917/86, Art. 167 (Group taxation context?). Text seems fragmented ("redditi rilevanti relativi alle imprese...").
    *   Source [8]: DPR 917/86, Art. 118 (Effects of group option). Global income determination.
    *   Source [9]: DPR 917/86, Art. 136 (Distribution of profits?). Text fragmented ("distribuiti i redditi prodotti negli esercizi più recenti").
    *   Source [10]: DPR 600/73, Art. 40 (Rectification of declarations).

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "redditi pluriennali" (multi-year incomes).
    *   I need to check if any source in the packet explicitly discusses "redditi pluriennali".
    *   Scanning sources:
        *   [1] DPR 917/86 Art. 17: Mentions TFR and indemnities commensurate with duration (commisurate alla durata). This implies a link to time/duration, but doesn't explicitly say "pluriennali" in the text provided.
        *   [2] DPR 917/86 Art. 24: Non-residents.
        *   [3] DPR 917/86 Art. 21: Heirs/legatees.
        *   [4] DPR 917/86 Art. 4: Spouses/minors.
        *   [5] DPR 917/86 Art. 21: Other separately taxed incomes.
        *   [6] DPR 917/86 Art. 3: Base taxable income.
        *   [7] DPR 917/86 Art. 167: Group taxation context (fragmented).
        *   [8] DPR 917/86 Art. 118: Group option effects.
        *   [9] DPR 917/86 Art. 136: Distribution of profits (fragmented).
        *   [10] DPR 600/73 Art. 40: Rectification.
    *   **Critical Finding:** None of the provided text snippets explicitly mention "redditi pluriennali" (multi-year incomes) in a way that defines their taxation rules directly within the context of the question's specific phrasing, except potentially under the umbrella of TFR or indemnities commensurate with duration (Source [1]). However, standard Italian tax law knowledge suggests TFR is often treated as separate taxation. The packet text for Source [1] says "indennità equipollenti... commisurate alla durata".
    *   **Constraint Check:** I must reason ONLY on facts in the Research Packet. If the packet does not contain information about "redditi pluriennali" specifically, I cannot invent it. I must state what is available or note the gap.
    *   The question asks "How is separate taxation applied to multi-year incomes?".
    *   Source [1] mentions TFR and indemnities commensurate with duration (Art. 2120 CC). This is a form of income often associated with long-term service, but the text doesn't explicitly use the term "pluriennali".
    *   Source [5] mentions "Per gli altri redditi tassati separatamente... ad esclusione di quelli in cui alla lettera g) del comma 1 dell'articolo 17". This implies there are other separately taxed incomes.
    *   There is no explicit text defining the application to "redditi pluriennali" specifically (e.g., averaging over years, specific rates for multi-year).
    *   Therefore, I must qualify based on what IS in the packet regarding separate taxation generally and note if specific info on "pluriennali" is missing or infer from TFR/duration clauses.
    *   Actually, looking closely at Source [1]: "indennità equipollenti... commisurate alla durata". This touches on duration.
    *   However, the prompt instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   If the packet doesn't explicitly define rules for "redditi pluriennali", I cannot claim specific rules exist based on external knowledge. I must report what is in the text or identify the gap.
    *   Wait, Source [1] Art 17 lists TFR and indemnities commensurate with duration as subject to separate taxation. This is the closest link.
    *   The question asks about "redditi pluriennali". In Italian tax law, this often refers to specific scenarios (like certain bonuses or deferred income). But based *strictly* on the packet provided:
        *   Source [1] establishes TFR and duration-based indemnities are taxed separately.
        *   Source [5] establishes other separately taxed incomes exist but excludes Art 17(g) and shareholder imputed ones.
    *   I need to be careful not to hallucinate rules about "pluriennali" if the text doesn't say it. I will focus on the TFR/Duration aspect found in Source [1] as the relevant separate taxation mechanism for income linked to duration (which implies multi-year service).
    *   Actually, looking at the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
    *   So if I can't find a source for "pluriennali", I must use

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23` | 5.6302 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art32` | 4.2418 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29` | 3.8535 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art5` | 3.4786 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29` | 2.6748 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art4` | 1.8673 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207` | -0.2570 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art151` | -0.6571 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172` | -1.1077 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65` | -1.5843 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art23`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 17 Tassazione separata 1. L'imposta si applica separatamente sui seguenti redditi: a) trattamento di fine rapporto di cui all' articolo 2120 del codice civile e indennità equipollenti, comunque denominate, commisurate alla durata

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art32`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 24 Determinazione dell'imposta dovuta dai non residenti 1. Nei confronti dei non residenti l'imposta si applica sul reddito complessivo e sui redditi tassati separatamente a norma dei precedenti articoli, salvo il disposto dei com

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 7 si procede alla tassazione separata nei confronti degli eredi e dei legatari; l'imposta dovuta da ciascuno di essi è determinata applicando all'ammontare percepito, diminuito della quota dell'imposta sulle successioni proporzionale a

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art5`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 4 ((Coniugi e figli minori 1. Ai Fini della determinazione del reddito complessivo o della tassazione separata: a) i redditi dei beni che formano oggetto della comunione legale di cui agli articoli 177 e seguenti del codice civile

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art29`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 21 Determinazione dell'imposta per gli altri redditi tassati separatamente 1. Per gli altri redditi tassati separatamente, ad esclusione di quelli in cui alla lettera g) del comma 1 dell'articolo 17 e di quelli imputati ai soci in

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art4`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 3 Base imponibile 1. L'imposta si applica sul reddito complessivo del soggetto, formato per i residenti da tutti i redditi posseduti al netto degli oneri deducibili indicati nell'articolo 10 e per i non residenti soltanto da quell

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  redditi)) rilevanti relativi alle imprese ed entità del gruppo soggette all'imposta minima nazionale equivalente calcolata in maniera unitaria con il soggetto controllato non residente. (227) ((238)) 4-ter. La tassazione effettiva di

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art151`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 118 Effetti dell'esercizio dell'opzione 1. L'esercizio dell'opzione per la tassazione di gruppo di cui all'articolo 117 comporta la determinazione di un reddito complessivo globale corrispondente alla somma algebrica dei redditi c

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art172`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  distribuiti i redditi prodotti negli esercizi più recenti. ((6. Nel caso in cui nello stesso Paese estero siano presenti più società controllate e la legislazione locale preveda una forma di tassazione di gruppo analoga a quella di cu

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art65`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Alla rettifica delle dichiarazioni presentate dai soggetti all'imposta sul reddito delle persone giuridiche si procede con unico atto agli effetti di tale imposta e dell'imposta locale sui redditi, con riferimento unitario al reddito

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
