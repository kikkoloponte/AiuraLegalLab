# trib_006 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:13 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.5s (ret 0.2s + llm 65.1s) |

## Query

> Quali sono le operazioni imponibili ai fini IVA?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Quali sono le operazioni imponibili ai fini IVA?" (What are the taxable operations for VAT purposes?)
    *   **Input Packet:** Contains 10 source snippets (DPR, DLgs, RD) with specific articles and texts.

2.  **Analyze the Research Packet Sources:**
    *   [1] DPR 447/88 Art. 268: Execution of interception operations (wiretapping). Irrelevant to VAT taxable operations.
    *   [2] DLgs 206/205 Art. 13 Definitions: Defines "price of sale" including VAT and other taxes. Relevant context for price definition, but doesn't list taxable operations directly.
    *   [3] DPR 633/72 Art. 64 (Text snippet): Customs offices execute controls for violations of art. 46, fifth comma... reference to VAT tax offices. Snippet cuts off ("Per le controversie relative alla quali"). This source is about customs/VAT control but doesn't define taxable operations explicitly in the visible text.
    *   [4] DLgs 218/97 Art. 17: Abrogates old articles (Art. 2-bis Accertamento con adesione). Mentions "imposte sul reddito" (income tax) and fiscal assessment. Irrelevant to VAT taxable operations definition.
    *   [5] DPR 633/72 Art. 98 (Text snippet): Liquidation of tax due... special regimes (art. 74-quinquies...). Reference to non-residents. Snippet cuts off ("da soggetti non residenti"). Mentions automated procedures. Irrelevant to general definition of taxable operations in the visible text.
    *   [6] DLgs 218/97 Art. 17 (Text snippet): Continuation of abrogation list... mentions "imposta sul reddito" (income tax). Irrelevant to VAT.
    *   [7] DPR 447/88 Art. 228: Expert activities (perito). Irrelevant to VAT taxable operations.
    *   [8] DPR 917/86 Art. 179: Fiscal neutrality regime for specific operations (letters a, b, b-bis of art. 178). References art. 172 and 173. Irrelevant to general VAT taxable operations definition in the visible text.
    *   [9] DPR 633/72 Art. 90: Data elements acquired... references art. 52, 63, 54-quater (from source [5]). Snippet cuts off ("I dati ed elementi attinenti ai rapporti ed alle operazioni acquisiti e rilevati rispettivamente a norma del numero 7) e dell'articolo 52..."). Irrelevant to definition of taxable operations.
    *   [10] RD 262/42 Art. 2391-bis: Related party transactions for listed companies (Consob rules). Irrelevant to VAT taxable operations.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks: "Quali sono le operazioni imponibili ai fini IVA?" (What are the taxable operations for VAT purposes?)
    *   I need to check if any source in the packet explicitly lists or defines "operazioni imponibili" (taxable operations) under VAT law.
    *   Source [2] defines "prezzo di vendita" including VAT, but doesn't list the types of operations.
    *   Source [3], [5], [9] refer to DPR 633/72 (the main VAT code), but the visible text snippets do not contain the definition of taxable operations (usually found in Art. 1 or similar general provisions, or specific lists). The snippets provided are about controls, liquidation, data acquisition, etc.
    *   Source [8] mentions "Regime di neutralità fiscale" for specific operations but doesn't define them generally.
    *   **Crucial Constraint:** I must reason ONLY on facts in the Research Packet. I cannot access external knowledge (e.g., knowing that Art. 1 of DPR 633/72 defines taxable operations).
    *   Therefore, based *strictly* on the provided text, there is no explicit list or definition of "operazioni imponibili" available in the snippets.
    *   However, Source [2] mentions "prezzo di vendita... comprensivo dell'IVA". This implies VAT applies to sales at a price.
    *   Source [3], [5], [9] refer to DPR 633/72 regarding VAT operations/data.
    *   Since I cannot invent facts, and the packet does not contain the specific definition of taxable operations (e.g., "supply of goods", "provision of services"), I must state that the information is missing or limited based on the provided text.
    *   Wait, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   If the packet doesn't have the answer, I cannot hallucinate it. I must report what is there or state the gap.
    *   The prompt asks me to analyze according to the CoT schema.
    *   In `VALUTAZIONE`, if I lack info, I should use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:"? No, that's for when I don't have a source for a claim. If the answer isn't in the packet, I must report the gap or state low confidence based on available text.
    *   Actually, looking closely at Source [2]: It defines "prezzo di vendita" (price of sale) including VAT. This implies sales are taxable events where price includes VAT. But it doesn't list all operations.
    *   Looking at Source [3], [5], [9]: They reference DPR 633/72 (VAT Code). Source [3] mentions "violazioni di cui al quinto comma dell'art. 46" and "uffici dell'imposta sul valore aggiunto". This confirms the context is VAT, but doesn't list operations.
    *   Conclusion: The packet does not contain a definitive list of taxable operations. I must report this limitation in `GAP ANALYSIS` or `VALUTAZIONE`.
    *   However, usually, in these tasks, if the info isn't there, I should state that based on the provided text, specific definitions are not found, but context exists (e.g., price includes VAT).
    *   Let's check the constraint: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
    *   If I say "Sales are taxable", do I have a source? Source [2] says "prezzo di vendita... comprensivo dell'IVA". This implies VAT applies to sales.
    *   But the question is "Quali sono le operazioni imponibili" (What are the operations).
    *

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Quali sono le operazioni imponibili ai fini IVA?" (What are the taxable operations for VAT purposes?)
    *   **Input Packet:** Contains 10 source snippets (DPR, DLgs, RD) with specific articles and texts.

2.  **Analyze the Research Packet Sources:**
    *   [1] DPR 447/88 Art. 268: Execution of interception operations (wiretapping). Irrelevant to VAT taxable operations.
    *   [2] DLgs 206/205 Art. 13 Definitions: Defines "price of sale" including VAT and other taxes. Relevant context for price definition, but doesn't list taxable operations directly.
    *   [3] DPR 633/72 Art. 64 (Text snippet): Customs offices execute controls for violations of art. 46, fifth comma... reference to VAT tax offices. Snippet cuts off ("Per le controversie relative alla quali"). This source is about customs/VAT control but doesn't define taxable operations explicitly in the visible text.
    *   [4] DLgs 218/97 Art. 17: Abrogates old articles (Art. 2-bis Accertamento con adesione). Mentions "imposte sul reddito" (income tax) and fiscal assessment. Irrelevant to VAT taxable operations definition.
    *   [5] DPR 633/72 Art. 98 (Text snippet): Liquidation of tax due... special regimes (art. 74-quinquies...). Reference to non-residents. Snippet cuts off ("da soggetti non residenti"). Mentions automated procedures. Irrelevant to general definition of taxable operations in the visible text.
    *   [6] DLgs 218/97 Art. 17 (Text snippet): Continuation of abrogation list... mentions "imposta sul reddito" (income tax). Irrelevant to VAT.
    *   [7] DPR 447/88 Art. 228: Expert activities (perito). Irrelevant to VAT taxable operations.
    *   [8] DPR 917/86 Art. 179: Fiscal neutrality regime for specific operations (letters a, b, b-bis of art. 178). References art. 172 and 173. Irrelevant to general VAT taxable operations definition in the visible text.
    *   [9] DPR 633/72 Art. 90: Data elements acquired... references art. 52, 63, 54-quater (from source [5]). Snippet cuts off ("I dati ed elementi attinenti ai rapporti ed alle operazioni acquisiti e rilevati rispettivamente a norma del numero 7) e dell'articolo 52..."). Irrelevant to definition of taxable operations.
    *   [10] RD 262/42 Art. 2391-bis: Related party transactions for listed companies (Consob rules). Irrelevant to VAT taxable operations.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks: "Quali sono le operazioni imponibili ai fini IVA?" (What are the taxable operations for VAT purposes?)
    *   I need to check if any source in the packet explicitly lists or defines "operazioni imponibili" (taxable operations) under VAT law.
    *   Source [2] defines "prezzo di vendita" including VAT, but doesn't list the types of operations.
    *   Source [3], [5], [9] refer to DPR 633/72 (the main VAT code), but the visible text snippets do not contain the definition of taxable operations (usually found in Art. 1 or similar general provisions, or specific lists). The snippets provided are about controls, liquidation, data acquisition, etc.
    *   Source [8] mentions "Regime di neutralità fiscale" for specific operations but doesn't define them generally.
    *   **Crucial Constraint:** I must reason ONLY on facts in the Research Packet. I cannot access external knowledge (e.g., knowing that Art. 1 of DPR 633/72 defines taxable operations).
    *   Therefore, based *strictly* on the provided text, there is no explicit list or definition of "operazioni imponibili" available in the snippets.
    *   However, Source [2] mentions "prezzo di vendita... comprensivo dell'IVA". This implies VAT applies to sales at a price.
    *   Source [3], [5], [9] refer to DPR 633/72 regarding VAT operations/data.
    *   Since I cannot invent facts, and the packet does not contain the specific definition of taxable operations (e.g., "supply of goods", "provision of services"), I must state that the information is missing or limited based on the provided text.
    *   Wait, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   If the packet doesn't have the answer, I cannot hallucinate it. I must report what is there or state the gap.
    *   The prompt asks me to analyze according to the CoT schema.
    *   In `VALUTAZIONE`, if I lack info, I should use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:"? No, that's for when I don't have a source for a claim. If the answer isn't in the packet, I must report the gap or state low confidence based on available text.
    *   Actually, looking closely at Source [2]: It defines "prezzo di vendita" (price of sale) including VAT. This implies sales are taxable events where price includes VAT. But it doesn't list all operations.
    *   Looking at Source [3], [5], [9]: They reference DPR 633/72 (VAT Code). Source [3] mentions "violazioni di cui al quinto comma dell'art. 46" and "uffici dell'imposta sul valore aggiunto". This confirms the context is VAT, but doesn't list operations.
    *   Conclusion: The packet does not contain a definitive list of taxable operations. I must report this limitation in `GAP ANALYSIS` or `VALUTAZIONE`.
    *   However, usually, in these tasks, if the info isn't there, I should state that based on the provided text, specific definitions are not found, but context exists (e.g., price includes VAT).
    *   Let's check the constraint: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
    *   If I say "Sales are taxable", do I have a source? Source [2] says "prezzo di vendita... comprensivo dell'IVA". This implies VAT applies to sales.
    *   But the question is "Quali sono le operazioni imponibili" (What are the operations).
    *

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315` | -0.3473 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13` | -2.1999 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art110` | -2.2781 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -4.3410 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art98` | -4.9576 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -5.0279 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art266` | -5.3164 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art223` | -5.3428 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art90` | -5.5782 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2458` | -6.0164 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art315`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 268 Esecuzione delle operazioni 1. Le comunicazioni intercettate sono registrate e delle operazioni è redatto verbale. 2. Nel verbale è trascritto, anche sommariamente, soltanto il contenuto delle comunicazioni intercettate rilev

**[2]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art13`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 13 Definizioni 1. Ai fini del presente capo si intende per: a) prezzo di vendita: il prezzo finale, valido per una unità di prodotto o per una determinata quantità del prodotto, comprensivo dell'IVA e di ogni altra imposta; b) prezzo per unità di mis

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art110`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 ((Gli uffici doganali eseguono i controlli necessari per l'accertamento delle violazioni di cui al quinto comma dell'art. 46 e ne riferiscono ai competenti uffici dell'imposta sul valore aggiunto. Per le controversie relative alla quali

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 30 settembre 1994, n. 564 (Disposizioni urgenti in materia fiscale), convertito, con modificazioni, dalla legge 30 novembre 1994, n. 656 , abrogati dal presente articolo: "Art. 2-bis (Accertamento con adesione del contribuente ai fini delle imposte sul redd

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art98`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 (Liquidazione dell'imposta dovuta relativamente ((alle operazioni effettuate nell'ambito dei regimi speciali di cui agli articoli 74-quinquies e seguenti)) da soggetti non residenti). ((209)) 1. Avvalendosi di procedure automatizzate l'

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  gennaio 1929, n. 4 , e successive modificazioni, e dal relativo decreto ministeriale di attuazione del 1 settenibre 1931, la quale ha effetto, con unico atto ai sensi del comma 1 e del presente comma, anche ai fini delle imposte sul reddito. L'imposta sul

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art266`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 228 Attività del perito 1. Il perito procede alle operazioni necessarie per rispondere ai quesiti. A tal fine può essere autorizzato dal giudice a prendere visione degli atti, dei documenti e delle cose prodotti dalle parti dei q

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art223`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 179 Regime di neutralità fiscale 1. Alle operazioni indicate nelle lettere a), b) e b-bis) dell'articolo 178 si applicano le disposizioni di cui agli articoli 172 e 173. (132) 2. Ai conferimenti di cui alla lettera c) del comma 1

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art90`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 26 ottobre 1995, n. 504 . I dati ed elementi attinenti ai rapporti ed alle operazioni acquisiti e rilevati rispettivamente a norma del numero 7) e dell'articolo 52, ultimo comma, o dell'articolo 63, primo comma, o acquisiti ai sensi del

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2458`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2391-bis. (Operazioni con parti correlate). Gli organi di amministrazione delle società con azioni quotate in mercati regolamentati adottano, secondo principi generali indicati dalla Consob, regole che assicurano la trasparenza e la correttezza sostanziale e

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
