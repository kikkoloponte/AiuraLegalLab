# trib_007 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:36 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 69.5s (ret 0.1s + llm 69.2s) |

## Query

> Come si applica il principio del contraddittorio endoprocedimentale?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Question:** "Come si applica il principio del contraddittorio endoprocedimentale?" (How is the principle of internal procedural adversarialness applied?)
    *   **Research Packet:** Contains 10 sources (R.D. 1443, D.Lgs. 104/2010, L.C. 2/1999, etc.).

2.  **Analyze the Research Packet Sources:**
    *   [1] R.D. 1443 Art. 101 (Principio del contraddittorio): Judge cannot decide if party not cited/appeared.
    *   [2] D.Lgs. 104/2010 Art. 49 (Integrazione del contraddittorio): President/College orders integration when recourse against only some interested parties.
    *   [3] L.C. 2/1999 Art. 1 (Contraddittorio nella formazione della prova - Penale): Principle of adversarialness in evidence formation.
    *   [4] D.Lgs. 104/2010 Art. 27 (Contraddittorio): Adversarialness integral when introductory act notified to resistant admin and interested parties.
    *   [5] R.D. 1443 Art. 436 (Enunciazione del principio di diritto...): Court states principle of law when deciding recourse under art. 360(1) n. 3, etc.
    *   [6] R.D. 1443 Art. 420 (Deposito dell'atto di integrazione del contraddittorio): Deposit of integration act if Court ordered it.
    *   [7] D.P.R. 447/1988 Art. 724 (Principio del mutuo riconoscimento - Penale): Mutual recognition principle (EU law).
    *   [8] R.D. 1443 Art. 409 (Principio di diritto nell'interesse della legge): Public Prosecutor can intervene if parties didn't propose recourse or waived it, etc.
    *   [9] R.D. 262/1942 Art. 2941 (Codice Civile Art. 2717 - Valore probatorio di altre copie): Value of copies issued by public officials outside previous cases (Principle of proof).
    *   [10] L.C. 2/1999 Art. 1 (Contraddittorio...): Exception: no adversarialness by consent or objective impossibility or illicit conduct.

3.  **Drafting the Analysis (CoT Steps):**

    *   **Step 1: QUALIFICAZIONE**
        *   Define "principio del contraddittorio endoprocedimentale". It refers to the requirement that parties must be notified and allowed to participate before a decision is made, especially in administrative or specific civil contexts involving third parties.
        *   Source [1] (R.D. 1443 Art. 101) establishes the general principle: judge cannot decide if party not cited/appeared.
        *   Source [2] & [4] (D.Lgs. 104/2010) specifically address "integrazione del contraddittorio" in administrative/tax contexts (ricorso against admin).
        *   Claim: The principle ensures parties are notified and can respond before a decision is finalized.
        *   Citation: [1], [2], [4].

    *   **Step 2: NORMA APPLICABILE**
        *   Identify specific articles governing the application.
        *   R.D. 1443 Art. 101 (General civil procedure principle).
        *   D.Lgs. 104/2010 Art. 27 (Definition of integral adversarialness in administrative recourse).
        *   D.Lgs. 104/2010 Art. 49 (Ordering integration when recourse is against only some interested parties).
        *   R.D. 1443 Art. 420 (Deposit act of integration).
        *   Claim: The applicable norms define the conditions for integral adversarialness and procedures for its integration.
        *   Citation: [1], [2], [4], [6].

    *   **Step 3: GIURISPRUDENZA**
        *   Check Packet for case law.
        *   Scanning sources... None of the provided sources are case law (sentenze). They are statutes/regulations (R.D., D.Lgs, L.C.).
        *   Source [5] mentions Corte enuncia principio di diritto (Court states principle), but it's a statutory text about Cassation procedure.
        *   Source [8] mentions Procura intervention in interest of law.
        *   Since there is no specific case law (Giurisprudenza) in the packet, I must state that based on the provided packet, there are no specific judicial precedents cited, only statutory norms. Or I can interpret "Giurisdizione" broadly as the interpretation within the statutes if available, but strictly speaking, these are laws.
        *   Wait, the instruction says "Ragioni SOLO sui fatti nel Research Packet". If there is no jurisprudence in the packet, I cannot invent it. I must note the absence or rely on the statutory text as the authority.
        *   Actually, looking at Source [5], it talks about the Court stating principles of law. This isn't case law citation but a rule about Cassation decisions.
        *   Conclusion: No specific jurisprudence sources in packet. I will note this or focus on the statutory interpretation available. However, the schema requires "GIURISPRUDENZA". If no source exists for it, I must be careful not to hallucinate. I can state that the provided packet focuses on normative provisions rather than case law precedents regarding this specific principle.
        *   Correction: The prompt asks me to analyze based *only* on the Research Packet. If the packet doesn't contain jurisprudence, I cannot cite one. I will indicate the absence or rely on the statutory definitions which act as the rule of interpretation here.
        *   Better approach for "GIURISPRUDENZA" step when no cases exist: State that the provided sources are normative and do not include specific case law citations within the packet text, focusing instead on the legislative framework. Or simply leave it empty if strict citation is required? The schema says `citations` array. I can have an empty array or cite norms as "interpretative authority".
        *   Let's check Source [10] and [3]. They are Constitutional Laws (L.C.). These are higher hierarchy norms.
        *   Decision: Since the packet contains no case law texts (sentenze), I will note that the analysis relies on statutory provisions without specific judicial precedents in this packet. I will cite the normative sources as the basis for the "orientation" if applicable, or state the limitation.
        *   Actually, Source [5] mentions "La Corte enuncia il principio di diritto". This is a rule about Cassation courts.
        *   Okay, I will draft the content to reflect that the packet provides normative rules rather than case law precedents for this specific question.

    *   **Step 4: VALUTAZIONE**
        *   Assess the solidity of the principle based on the text.
        *   It is a fundamental principle (Art. 101 R.D. 144

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Question:** "Come si applica il principio del contraddittorio endoprocedimentale?" (How is the principle of internal procedural adversarialness applied?)
    *   **Research Packet:** Contains 10 sources (R.D. 1443, D.Lgs. 104/2010, L.C. 2/1999, etc.).

2.  **Analyze the Research Packet Sources:**
    *   [1] R.D. 1443 Art. 101 (Principio del contraddittorio): Judge cannot decide if party not cited/appeared.
    *   [2] D.Lgs. 104/2010 Art. 49 (Integrazione del contraddittorio): President/College orders integration when recourse against only some interested parties.
    *   [3] L.C. 2/1999 Art. 1 (Contraddittorio nella formazione della prova - Penale): Principle of adversarialness in evidence formation.
    *   [4] D.Lgs. 104/2010 Art. 27 (Contraddittorio): Adversarialness integral when introductory act notified to resistant admin and interested parties.
    *   [5] R.D. 1443 Art. 436 (Enunciazione del principio di diritto...): Court states principle of law when deciding recourse under art. 360(1) n. 3, etc.
    *   [6] R.D. 1443 Art. 420 (Deposito dell'atto di integrazione del contraddittorio): Deposit of integration act if Court ordered it.
    *   [7] D.P.R. 447/1988 Art. 724 (Principio del mutuo riconoscimento - Penale): Mutual recognition principle (EU law).
    *   [8] R.D. 1443 Art. 409 (Principio di diritto nell'interesse della legge): Public Prosecutor can intervene if parties didn't propose recourse or waived it, etc.
    *   [9] R.D. 262/1942 Art. 2941 (Codice Civile Art. 2717 - Valore probatorio di altre copie): Value of copies issued by public officials outside previous cases (Principle of proof).
    *   [10] L.C. 2/1999 Art. 1 (Contraddittorio...): Exception: no adversarialness by consent or objective impossibility or illicit conduct.

3.  **Drafting the Analysis (CoT Steps):**

    *   **Step 1: QUALIFICAZIONE**
        *   Define "principio del contraddittorio endoprocedimentale". It refers to the requirement that parties must be notified and allowed to participate before a decision is made, especially in administrative or specific civil contexts involving third parties.
        *   Source [1] (R.D. 1443 Art. 101) establishes the general principle: judge cannot decide if party not cited/appeared.
        *   Source [2] & [4] (D.Lgs. 104/2010) specifically address "integrazione del contraddittorio" in administrative/tax contexts (ricorso against admin).
        *   Claim: The principle ensures parties are notified and can respond before a decision is finalized.
        *   Citation: [1], [2], [4].

    *   **Step 2: NORMA APPLICABILE**
        *   Identify specific articles governing the application.
        *   R.D. 1443 Art. 101 (General civil procedure principle).
        *   D.Lgs. 104/2010 Art. 27 (Definition of integral adversarialness in administrative recourse).
        *   D.Lgs. 104/2010 Art. 49 (Ordering integration when recourse is against only some interested parties).
        *   R.D. 1443 Art. 420 (Deposit act of integration).
        *   Claim: The applicable norms define the conditions for integral adversarialness and procedures for its integration.
        *   Citation: [1], [2], [4], [6].

    *   **Step 3: GIURISPRUDENZA**
        *   Check Packet for case law.
        *   Scanning sources... None of the provided sources are case law (sentenze). They are statutes/regulations (R.D., D.Lgs, L.C.).
        *   Source [5] mentions Corte enuncia principio di diritto (Court states principle), but it's a statutory text about Cassation procedure.
        *   Source [8] mentions Procura intervention in interest of law.
        *   Since there is no specific case law (Giurisprudenza) in the packet, I must state that based on the provided packet, there are no specific judicial precedents cited, only statutory norms. Or I can interpret "Giurisdizione" broadly as the interpretation within the statutes if available, but strictly speaking, these are laws.
        *   Wait, the instruction says "Ragioni SOLO sui fatti nel Research Packet". If there is no jurisprudence in the packet, I cannot invent it. I must note the absence or rely on the statutory text as the authority.
        *   Actually, looking at Source [5], it talks about the Court stating principles of law. This isn't case law citation but a rule about Cassation decisions.
        *   Conclusion: No specific jurisprudence sources in packet. I will note this or focus on the statutory interpretation available. However, the schema requires "GIURISPRUDENZA". If no source exists for it, I must be careful not to hallucinate. I can state that the provided packet focuses on normative provisions rather than case law precedents regarding this specific principle.
        *   Correction: The prompt asks me to analyze based *only* on the Research Packet. If the packet doesn't contain jurisprudence, I cannot cite one. I will indicate the absence or rely on the statutory definitions which act as the rule of interpretation here.
        *   Better approach for "GIURISPRUDENZA" step when no cases exist: State that the provided sources are normative and do not include specific case law citations within the packet text, focusing instead on the legislative framework. Or simply leave it empty if strict citation is required? The schema says `citations` array. I can have an empty array or cite norms as "interpretative authority".
        *   Let's check Source [10] and [3]. They are Constitutional Laws (L.C.). These are higher hierarchy norms.
        *   Decision: Since the packet contains no case law texts (sentenze), I will note that the analysis relies on statutory provisions without specific judicial precedents in this packet. I will cite the normative sources as the basis for the "orientation" if applicable, or state the limitation.
        *   Actually, Source [5] mentions "La Corte enuncia il principio di diritto". This is a rule about Cassation courts.
        *   Okay, I will draft the content to reflect that the packet provides normative rules rather than case law precedents for this specific question.

    *   **Step 4: VALUTAZIONE**
        *   Assess the solidity of the principle based on the text.
        *   It is a fundamental principle (Art. 101 R.D. 144

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art111` | 2.3989 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art52` | 2.1218 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge.costituzionale:1999-11-23;2~art1` | 2.0215 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art30` | 1.6607 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art436` | 0.6822 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art420` | 0.5293 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724` | 0.3331 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art409` | -0.8413 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2941` | -1.2893 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge.costituzionale:1999-11-23;2~art1` | -2.4449 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art6bis`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art111`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 101. (Principio del contraddittorio). Il giudice, salvo che la legge disponga altrimenti, non può statuire sopra alcuna domanda, se la parte contro la quale è proposta non è stata regolarmente citata e non è comparsa. Il giudice assicura il rispetto del co

**[2]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art52`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 49 Integrazione del contraddittorio 1. Quando il ricorso sia stato proposto solo contro taluno dei controinteressati, il presidente o il collegio ordina l'integrazione del contraddittorio nei confronti degli altri. 2. L'integrazione del contraddittorio

**[3]** `urn:nir:stato:legge.costituzionale:1999-11-23;2~art1`

> LEGGE COSTITUZIONALE 23 novembre 1999, n. 2 'acquisizione di ogni altro mezzo di prova a suo favore; sia assistita da un interprete se non comprende o non parla la lingua impiegata nel processo. Il processo penale è regolato dal principio del contraddittorio nella formazione della prova. La colpevol

**[4]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art30`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 27 Contraddittorio 1. Il contraddittorio è integralmente costituito quando l'atto introduttivo è notificato all'amministrazione resistente e, ove esistenti, ai controinteressati. 2. Se il giudizio è promosso solo contro alcune delle parti e non si è ver

**[5]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art436`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 384. (Enunciazione del principio di diritto e decisione della causa nel merito). La Corte enuncia il principio di diritto quando decide il ricorso proposto a norma dell'articolo 360, primo comma, n. 3), e in ogni altro caso in cui, decidendo su altri motiv

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art420`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 371-bis (Deposito dell'atto di integrazione del contraddittorio) Qualora la Corte abbia ordinato l'integrazione del contraddittorio, assegnando alle parti un termine perentorio per provvedervi, il ricorso notificato, contenente nell'intestazione le parole

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-bis (( (Principio del mutuo riconoscimento). )) (( 1. Il principio del mutuo riconoscimento è disciplinato dalle norme del presente titolo e dalle altre disposizioni di legge attuative del diritto dell'Unione europea. 2. Le d

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art409`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 363. (( (Principio di diritto nell'interesse della legge). )) ((Quando le parti non hanno proposto ricorso nei termini di legge o vi hanno rinunciato, ovvero quando il provvedimento non è ricorribile in cassazione e non è altrimenti impugnabile, il Procura

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2941`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2717. (Valore probatorio di altre copie). Le copie rilasciate da pubblici ufficiali fuori dei casi contemplati dagli articoli precedenti hanno l'efficacia di un principio di prova per iscritto.

**[10]** `urn:nir:stato:legge.costituzionale:1999-11-23;2~art1`

> LEGGE COSTITUZIONALE 23 novembre 1999, n. 2  non ha luogo in contraddittorio per consenso dell'imputato o per accertata impossibilità di natura oggettiva o per effetto di provata condotta illecita". Avvertenza: Il testo della nota qui pubblicato è stato redatto dall'amministrazione competente per ma

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
