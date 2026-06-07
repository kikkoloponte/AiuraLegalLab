# trib_015 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:23 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 23.8s (ret 0.2s + llm 23.4s) |

## Query

> Qual è il regime IVA delle prestazioni di servizi intracomunitarie?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, RD 262/42, DLgs 33/13, etc.).
    *   **Question:** "Qual è il regime IVA delle prestazioni di servizi intracomunitarie?" (What is the VAT regime for cross-border services?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917/86 Art. 145 (Regime forfetario, cessione beni/servizi). Text mentions "cessione ovvero la costituzione in garanzia", "prestazioni di servizi".
    *   Source [2]: RD 262/42 Art. 1677 (Prestazione continuativa o periodica di servizi - Appalto/Somministrazione).
    *   Source [3]: DLgs 33/13 Art. 32 (Obblighi di pubblicazione servizi pubblici).
    *   Source [4]: RD 262/42 Art. 2223 (Prestazione della materia - Appalto/Somministrazione).
    *   Source [5]: DPR 917/86 Art. 51 (Tassazione valori beni/servizi ceduti/prestati).
    *   Source [6]: DLgs 33/13 Art. 41 (Trasparenza servizio sanitario nazionale).
    *   Source [7]: DLgs 104/10 Art. 133 (Concessioni di pubblici servizi, indennità, canoni).
    *   Source [8]: DPR 917/86 Art. 145 (Regime forfetario enti non commerciali).
    *   Source [9]: DLgs 81/15 Art. 13 (Lavoro intermittente).
    *   Source [10]: DPR 917/86 Art. 51 (Somministrazioni di vitto, mense).

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "regime IVA delle prestazioni di servizi intracomunitarie" (VAT regime for cross-border services).
    *   I need to check if any source in the packet discusses VAT (*Imposta sul Valore Aggiunto*) specifically regarding *intracomunitario* (cross-border/within EU) rules.
    *   Scanning sources:
        *   DPR 917/86 is the TUIR (Testo Unico delle Imposte sui Redditi), not primarily VAT (IVA). It deals with income tax, forfetario regime, etc. Source [1] mentions "cessione ovvero la costituzione in garanzia" and "prestazioni di servizi". Source [5] mentions "tassazione nel periodo d'imposta".
        *   RD 262/42 is the Civil Code (Codice Civile). Deals with contracts (appalto, somministrazione), not VAT.
        *   DLgs 33/13 is about transparency of public services.
        *   DLgs 104/10 is about concessions/public services.
        *   DLgs 81/15 is about labor law (intermittent work).
    *   **Critical Finding:** None of the provided sources explicitly mention "IVA" (VAT), "intracomunitario", "reverse charge", or EU VAT directives regarding cross-border services. The packet contains tax income rules (DPR 917/86) and civil code contract rules, but not VAT legislation (which is usually in DPR 633/72).
    *   **Constraint Check:** I must reason ONLY on facts in the Research Packet. If there is no source for a specific claim (like "VAT regime exists"), I cannot invent it. However, the instruction says: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
    *   Wait, the instruction says "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id). If I cannot find the answer in the packet, I must state that based on the provided text.
    *   However, looking closely at Source [1] and [5], they are from DPR 917/86 (TUIR). They discuss taxation ("tassazione", "regime forfetario"). But do they cover VAT? Usually, TUIR covers Income Tax (IRPEF/IRES), while VAT is covered by DPR 633/72. The packet does *not* contain DPR 633/72.
    *   Therefore, based strictly on the provided Packet, I cannot confirm the specific VAT regime for cross-border services because that information is absent from the sources.
    *   However, I must answer the prompt using the CoT schema and JSON format.
    *   If the packet doesn't contain the answer, I should indicate a GAP or state that the provided text does not cover this specific topic (VAT/Intracomunitario).
    *   Actually, looking at Source [1] text: "canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi." This is about distinguishing revenue types for tax purposes.
    *   Looking at Source [5]: "tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia... valori di cui al comma 1, compresi quelli dei beni ceduti e dei servizi prestati".
    *   None of these explicitly define the VAT regime for cross-border services.
    *   **Strategy:** I must adhere to the "CITATION CONTRACT". If I make a claim about VAT rules not in the packet, I violate the contract unless I use `ungrounded_reasoning`. But the instruction says "Reason ONLY on facts in the Research Packet." This implies if the info isn't there, I can't answer factually.
    *   However, usually in these tasks, if the knowledge is missing from the RAG packet, I should report that gap or state low confidence based on available text.
    *   Let's check if any source mentions "IVA". Scanning... No "IVA" keyword found in the provided text snippets (DPR 917/86 Art 145, 51; RD 262/42 Art 1677, 2223; DLgs 33/13 Art 32, 41; DLgs 104/10 Art 133; DLgs 81/15 Art 13).
    *   Therefore, the packet does not contain the answer to "Qual è il regime IVA delle prestazioni di servizi intracomunitarie?".
    *   I must follow the CoT schema.
    *   **QUALIFICAZIONE:** Define the legal issue (VAT cross-border services) and note that the provided sources focus on Income Tax (DPR 917/86) and Civil Code contracts, not VAT legislation. Source [1] mentions "prestazioni di servizi" in tax context.
    *   **NORMA APPLICABILE:** State that based *only* on the packet, no specific VAT article is cited. However, I can cite sources regarding service taxation generally found

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (DPR 917/86, RD 262/42, DLgs 33/13, etc.).
    *   **Question:** "Qual è il regime IVA delle prestazioni di servizi intracomunitarie?" (What is the VAT regime for cross-border services?)

2.  **Analyze the Research Packet:**
    *   Source [1]: DPR 917/86 Art. 145 (Regime forfetario, cessione beni/servizi). Text mentions "cessione ovvero la costituzione in garanzia", "prestazioni di servizi".
    *   Source [2]: RD 262/42 Art. 1677 (Prestazione continuativa o periodica di servizi - Appalto/Somministrazione).
    *   Source [3]: DLgs 33/13 Art. 32 (Obblighi di pubblicazione servizi pubblici).
    *   Source [4]: RD 262/42 Art. 2223 (Prestazione della materia - Appalto/Somministrazione).
    *   Source [5]: DPR 917/86 Art. 51 (Tassazione valori beni/servizi ceduti/prestati).
    *   Source [6]: DLgs 33/13 Art. 41 (Trasparenza servizio sanitario nazionale).
    *   Source [7]: DLgs 104/10 Art. 133 (Concessioni di pubblici servizi, indennità, canoni).
    *   Source [8]: DPR 917/86 Art. 145 (Regime forfetario enti non commerciali).
    *   Source [9]: DLgs 81/15 Art. 13 (Lavoro intermittente).
    *   Source [10]: DPR 917/86 Art. 51 (Somministrazioni di vitto, mense).

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "regime IVA delle prestazioni di servizi intracomunitarie" (VAT regime for cross-border services).
    *   I need to check if any source in the packet discusses VAT (*Imposta sul Valore Aggiunto*) specifically regarding *intracomunitario* (cross-border/within EU) rules.
    *   Scanning sources:
        *   DPR 917/86 is the TUIR (Testo Unico delle Imposte sui Redditi), not primarily VAT (IVA). It deals with income tax, forfetario regime, etc. Source [1] mentions "cessione ovvero la costituzione in garanzia" and "prestazioni di servizi". Source [5] mentions "tassazione nel periodo d'imposta".
        *   RD 262/42 is the Civil Code (Codice Civile). Deals with contracts (appalto, somministrazione), not VAT.
        *   DLgs 33/13 is about transparency of public services.
        *   DLgs 104/10 is about concessions/public services.
        *   DLgs 81/15 is about labor law (intermittent work).
    *   **Critical Finding:** None of the provided sources explicitly mention "IVA" (VAT), "intracomunitario", "reverse charge", or EU VAT directives regarding cross-border services. The packet contains tax income rules (DPR 917/86) and civil code contract rules, but not VAT legislation (which is usually in DPR 633/72).
    *   **Constraint Check:** I must reason ONLY on facts in the Research Packet. If there is no source for a specific claim (like "VAT regime exists"), I cannot invent it. However, the instruction says: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
    *   Wait, the instruction says "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id). If I cannot find the answer in the packet, I must state that based on the provided text.
    *   However, looking closely at Source [1] and [5], they are from DPR 917/86 (TUIR). They discuss taxation ("tassazione", "regime forfetario"). But do they cover VAT? Usually, TUIR covers Income Tax (IRPEF/IRES), while VAT is covered by DPR 633/72. The packet does *not* contain DPR 633/72.
    *   Therefore, based strictly on the provided Packet, I cannot confirm the specific VAT regime for cross-border services because that information is absent from the sources.
    *   However, I must answer the prompt using the CoT schema and JSON format.
    *   If the packet doesn't contain the answer, I should indicate a GAP or state that the provided text does not cover this specific topic (VAT/Intracomunitario).
    *   Actually, looking at Source [1] text: "canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi." This is about distinguishing revenue types for tax purposes.
    *   Looking at Source [5]: "tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia... valori di cui al comma 1, compresi quelli dei beni ceduti e dei servizi prestati".
    *   None of these explicitly define the VAT regime for cross-border services.
    *   **Strategy:** I must adhere to the "CITATION CONTRACT". If I make a claim about VAT rules not in the packet, I violate the contract unless I use `ungrounded_reasoning`. But the instruction says "Reason ONLY on facts in the Research Packet." This implies if the info isn't there, I can't answer factually.
    *   However, usually in these tasks, if the knowledge is missing from the RAG packet, I should report that gap or state low confidence based on available text.
    *   Let's check if any source mentions "IVA". Scanning... No "IVA" keyword found in the provided text snippets (DPR 917/86 Art 145, 51; RD 262/42 Art 1677, 2223; DLgs 33/13 Art 32, 41; DLgs 104/10 Art 133; DLgs 81/15 Art 13).
    *   Therefore, the packet does not contain the answer to "Qual è il regime IVA delle prestazioni di servizi intracomunitarie?".
    *   I must follow the CoT schema.
    *   **QUALIFICAZIONE:** Define the legal issue (VAT cross-border services) and note that the provided sources focus on Income Tax (DPR 917/86) and Civil Code contracts, not VAT legislation. Source [1] mentions "prestazioni di servizi" in tax context.
    *   **NORMA APPLICABILE:** State that based *only* on the packet, no specific VAT article is cited. However, I can cite sources regarding service taxation generally found

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | 5.4400 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1735` | 2.0740 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art32` | -0.0720 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2264` | -0.8574 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -1.4138 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41` | -1.8904 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138` | -2.2640 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182` | -2.5758 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13` | -2.7596 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63` | -3.1340 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art7ter`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 canza della distinta annotazione dei ricavi si considerano prevalenti le attività di prestazioni di servizi. 3. Il regime forfetario previsto nel presente articolo si estende di anno in anno qualora i limiti indicati al comma 1 non ven

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1735`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1677. (Prestazione continuativa o periodica di servizi). Se l'appalto ha per oggetto prestazioni continuative o periodiche di servizi, si osservano, in quanto compatibili, le norme di questo capo e quelle relative al contratto di somministrazione.

**[3]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art32`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 32 Obblighi di pubblicazione concernenti i servizi erogati 1. Le pubbliche amministrazioni ((e i gestori di pubblici servizi)) pubblicano la carta dei servizi o il documento contenente gli standard di qualità dei servizi pubblici. 2. Le pubbliche amminis

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2264`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2223. (Prestazione della materia). Le disposizioni di questo capo si osservano anche se la materia è fornita dal prestatore d'opera, purché le parti non abbiano avuto prevalentemente in considerazione la materia, nel qual caso si applicano le norme sulla vend

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  tassazione nel periodo d'imposta in cui avviene la cessione ovvero la costituzione in garanzia. (126) 3. Ai fini della determinazione in denaro dei valori di cui al comma 1, compresi quelli dei beni ceduti e dei servizi prestati al co

**[6]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 Trasparenza del servizio sanitario nazionale 1. Le amministrazioni e gli enti del servizio sanitario nazionale, dei servizi sanitari regionali, ivi comprese le aziende sanitarie territoriali ed ospedaliere, le agenzie e gli altri enti ed organismi pub

**[7]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 lici servizi relative a concessioni di pubblici servizi, escluse quelle concernenti indennità, canoni ed altri corrispettivi, ovvero relative a provvedimenti adottati dalla pubblica amministrazione o dal gestore di un pubblico servizio in un procedimento amm

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art182`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 145 ((Regime forfetario degli enti non commerciali )) (( 1. Fatto salvo quanto previsto, per le associazioni sportive dilettantistiche, dalla legge 16 dicembre 1991, n. 398 , e, per le associazioni senza scopo di lucro e per le pr

**[9]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art13`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 Art. 13 Definizione e casi di ricorso al lavoro intermittente 1. Il contratto di lavoro intermittente è il contratto, anche a tempo determinato, mediante il quale un lavoratore si pone a disposizione di un datore di lavoro che ne può utilizzare la prestazion

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art63`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  MODIFICAZIONI DALLA L. 24 LUGLIO 2008, N. 126 ; c) le somministrazioni di vitto da parte del datore di lavoro nonché quelle in mense organizzate direttamente dal datore di lavoro o gestite da terzi; le prestazioni sostitutive delle so

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
