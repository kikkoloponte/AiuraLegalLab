# trib_010 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:40 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.1s (ret 0.1s + llm 66.9s) |

## Query

> Quali sono i presupposti per l'iscrizione ipotecaria da parte dell'agente della riscossione?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 sources (mostly Codice Civile articles and some DPR/legge).
    *   **Question:** "Quali sono i presupposti per l'iscrizione ipotecaria da parte dell'agente della riscossione?" (What are the prerequisites for mortgage registration by the collection agent?)

2.  **Analyze the Research Packet Sources:**
    *   [1] RD 1942 n. 262 Art. 2854: Creditors with mortgage of same rank on same property concur in proportion to amount. (Relevant to mortgages/concurrence).
    *   [2] Legge 2000 n. 212 Art. 7: Tax administration acts must be motivated, otherwise annulable. (General administrative law).
    *   [3] RD 1942 n. 262 Art. 1745: Agent representation (declarations/reclaims made to agent are valid).
    *   [4] RD 1942 n. 262 Art. 1748: Agent rights (commission due when operation concluded via intervention, even if done by substitute).
    *   [5] RD 1942 n. 262 Art. 1746: Agent obligations (protect interests of principal, act in good faith, follow instructions).
    *   [6] RD 1942 n. 262 Art. 1702: Last carrier represents previous carriers for collection of credits arising from transport contract and privilege on transported goods. (Specific to transport/carriers).
    *   [7] RD 1942 n. 262 Art. 2856: Subrogation of losing creditor (creditor with mortgage loses if satisfied by prior creditor, subrogated rights extend to other assets).
    *   [8] RD 1942 n. 262 Art. 1751: Agent indemnity/termination rules.
    *   [9] RD 1942 n. 262 Art. 1749: Principal obligations (act in good faith, provide documentation).
    *   [10] DPR 1972 n. 633 Art. 54-quinquies: Tax assessment notice constitutes executive title for collection.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about prerequisites for mortgage registration ("iscrizione ipotecaria") by a "collection agent" ("agente della riscossione").
    *   The packet contains sources about general agency law (Art. 1745, 1746, 1748, 1749, 1751 of CC) and specific transport carrier representation (Art. 1702).
    *   It also contains sources about mortgages/concurrence/subrogation (Art. 2854, 2856 of CC).
    *   It contains a source about tax administration acts needing motivation (Legge 2000 n. 212 Art. 7) and executive titles for collection (DPR 1972 n. 633 Art. 54-quinquies).
    *   **Critical Gap:** The packet does *not* contain specific articles defining the prerequisites for mortgage registration by a tax collection agent (Agente della Riscossione - AR). Usually, this involves specific laws like D.Lgs. 27/2010 or Art. 54 of DPR 633/1972 regarding the *right* to register mortgages on behalf of the State/Tax Authority, often linked to the "privilegio" (privilege) over assets.
    *   Source [6] mentions "ultimo vettore rappresenta i vettori precedenti... per la riscossione dei rispettivi crediti che nascono dal contratto di trasporto e per l'esercizio del privilegio". This is about transport carriers, not tax agents generally.
    *   Source [10] mentions "L'avviso di accertamento... costituisce titolo esecutivo ai fini della riscossione." (Assessment notice constitutes executive title).
    *   There is no direct source in the packet that explicitly lists the prerequisites for an *agente della riscossione* to register a mortgage. The standard legal knowledge would point to Art. 2809 CC or specific tax laws, but I must rely *only* on the Packet.
    *   Source [1] and [7] discuss mortgages (ipoteche) generally within the Codice Civile context provided in the packet.
    *   Source [3], [5], [9] discuss agency obligations/rights.
    *   There is a mismatch: The question asks about "agente della riscossione" (tax collection agent), but the packet provides general agency rules (Art. 1745-1751 CC) and specific transport carrier rules (Art. 1702 CC). It does not explicitly link the "Agente della Riscossione" to mortgage registration prerequisites in a direct citation within this specific text block, except perhaps by inference of general agency + executive title.
    *   However, I must answer based *only* on the packet. If the packet doesn't have the info, I must state the gap or use "VALUTAZIONE PERSONALE" for reasoning not grounded in sources (but factual claims need source_id).
    *   Actually, looking closely at Source [10]: It mentions "titolo esecutivo ai fini della riscossione". This is a prerequisite for enforcement actions which might include mortgages.
    *   Looking at Source [6]: Mentions "riscossione dei rispettivi crediti... e per l'esercizio del privilegio".
    *   The packet does not explicitly contain the specific article (e.g., Art. 2809 CC or specific tax decree) defining the prerequisites for mortgage registration by a collection agent specifically.
    *   Therefore, I must qualify based on what is available: General agency rules + Mortgage concurrence/subrogation rules + Executive title availability.
    *   Wait, the instruction says "Reason ONLY on facts in the Research Packet". If the specific legal answer isn't in the packet, I cannot invent it. I must analyze what *is* there regarding agents and mortgages.
    *   Actually, Source [1] is Art. 2854 CC (Mortgages concurrence). Source [7] is Art. 2856 CC (Subrogation). These define how mortgages work once registered or in relation to other creditors. They don't define the *prerequisites* for registration itself by an agent.
    *   Source [3], [5], [9] define agency obligations/rights generally.
    *   There is a significant gap: The specific prerequisites for mortgage registration by a tax collection agent (often requiring a judicial title or specific administrative act) are not explicitly detailed in the provided text snippets, other than general executive title mention in [10].
    *   However, I need to follow the CoT schema.
    *   Step 1: QUALIFICAZIONE - Identify the legal relationship (Agency + Mortgage). Sources available: CC Art. 2854/285

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Data:** Research Packet containing 10 sources (mostly Codice Civile articles and some DPR/legge).
    *   **Question:** "Quali sono i presupposti per l'iscrizione ipotecaria da parte dell'agente della riscossione?" (What are the prerequisites for mortgage registration by the collection agent?)

2.  **Analyze the Research Packet Sources:**
    *   [1] RD 1942 n. 262 Art. 2854: Creditors with mortgage of same rank on same property concur in proportion to amount. (Relevant to mortgages/concurrence).
    *   [2] Legge 2000 n. 212 Art. 7: Tax administration acts must be motivated, otherwise annulable. (General administrative law).
    *   [3] RD 1942 n. 262 Art. 1745: Agent representation (declarations/reclaims made to agent are valid).
    *   [4] RD 1942 n. 262 Art. 1748: Agent rights (commission due when operation concluded via intervention, even if done by substitute).
    *   [5] RD 1942 n. 262 Art. 1746: Agent obligations (protect interests of principal, act in good faith, follow instructions).
    *   [6] RD 1942 n. 262 Art. 1702: Last carrier represents previous carriers for collection of credits arising from transport contract and privilege on transported goods. (Specific to transport/carriers).
    *   [7] RD 1942 n. 262 Art. 2856: Subrogation of losing creditor (creditor with mortgage loses if satisfied by prior creditor, subrogated rights extend to other assets).
    *   [8] RD 1942 n. 262 Art. 1751: Agent indemnity/termination rules.
    *   [9] RD 1942 n. 262 Art. 1749: Principal obligations (act in good faith, provide documentation).
    *   [10] DPR 1972 n. 633 Art. 54-quinquies: Tax assessment notice constitutes executive title for collection.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about prerequisites for mortgage registration ("iscrizione ipotecaria") by a "collection agent" ("agente della riscossione").
    *   The packet contains sources about general agency law (Art. 1745, 1746, 1748, 1749, 1751 of CC) and specific transport carrier representation (Art. 1702).
    *   It also contains sources about mortgages/concurrence/subrogation (Art. 2854, 2856 of CC).
    *   It contains a source about tax administration acts needing motivation (Legge 2000 n. 212 Art. 7) and executive titles for collection (DPR 1972 n. 633 Art. 54-quinquies).
    *   **Critical Gap:** The packet does *not* contain specific articles defining the prerequisites for mortgage registration by a tax collection agent (Agente della Riscossione - AR). Usually, this involves specific laws like D.Lgs. 27/2010 or Art. 54 of DPR 633/1972 regarding the *right* to register mortgages on behalf of the State/Tax Authority, often linked to the "privilegio" (privilege) over assets.
    *   Source [6] mentions "ultimo vettore rappresenta i vettori precedenti... per la riscossione dei rispettivi crediti che nascono dal contratto di trasporto e per l'esercizio del privilegio". This is about transport carriers, not tax agents generally.
    *   Source [10] mentions "L'avviso di accertamento... costituisce titolo esecutivo ai fini della riscossione." (Assessment notice constitutes executive title).
    *   There is no direct source in the packet that explicitly lists the prerequisites for an *agente della riscossione* to register a mortgage. The standard legal knowledge would point to Art. 2809 CC or specific tax laws, but I must rely *only* on the Packet.
    *   Source [1] and [7] discuss mortgages (ipoteche) generally within the Codice Civile context provided in the packet.
    *   Source [3], [5], [9] discuss agency obligations/rights.
    *   There is a mismatch: The question asks about "agente della riscossione" (tax collection agent), but the packet provides general agency rules (Art. 1745-1751 CC) and specific transport carrier rules (Art. 1702 CC). It does not explicitly link the "Agente della Riscossione" to mortgage registration prerequisites in a direct citation within this specific text block, except perhaps by inference of general agency + executive title.
    *   However, I must answer based *only* on the packet. If the packet doesn't have the info, I must state the gap or use "VALUTAZIONE PERSONALE" for reasoning not grounded in sources (but factual claims need source_id).
    *   Actually, looking closely at Source [10]: It mentions "titolo esecutivo ai fini della riscossione". This is a prerequisite for enforcement actions which might include mortgages.
    *   Looking at Source [6]: Mentions "riscossione dei rispettivi crediti... e per l'esercizio del privilegio".
    *   The packet does not explicitly contain the specific article (e.g., Art. 2809 CC or specific tax decree) defining the prerequisites for mortgage registration by a collection agent specifically.
    *   Therefore, I must qualify based on what is available: General agency rules + Mortgage concurrence/subrogation rules + Executive title availability.
    *   Wait, the instruction says "Reason ONLY on facts in the Research Packet". If the specific legal answer isn't in the packet, I cannot invent it. I must analyze what *is* there regarding agents and mortgages.
    *   Actually, Source [1] is Art. 2854 CC (Mortgages concurrence). Source [7] is Art. 2856 CC (Subrogation). These define how mortgages work once registered or in relation to other creditors. They don't define the *prerequisites* for registration itself by an agent.
    *   Source [3], [5], [9] define agency obligations/rights generally.
    *   There is a significant gap: The specific prerequisites for mortgage registration by a tax collection agent (often requiring a judicial title or specific administrative act) are not explicitly detailed in the provided text snippets, other than general executive title mention in [10].
    *   However, I need to follow the CoT schema.
    *   Step 1: QUALIFICAZIONE - Identify the legal relationship (Agency + Mortgage). Sources available: CC Art. 2854/285

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3083` | 3.1532 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art7` | 1.5750 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1804` | 1.5568 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1807` | -0.9267 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1805` | -1.5672 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1761` | -2.0453 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3085` | -3.6729 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1810` | -4.3652 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1808` | -4.8581 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99` | -5.0331 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602~art77`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3083`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2854. (Ipoteche iscritte nello stesso grado). I crediti con iscrizione ipotecaria dello stesso grado sugli stessi beni concorrono tra loro in proporzione dell'importo relativo.

**[2]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 Art. 7 Chiarezza e motivazione degli atti 1. Gli atti dell'amministrazione finanziaria ((, autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria,)) sono motivati ((, a pena di annullabilità, indicando specificamente i presupposti, i mezzi di prova)

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1804`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1745. (Rappresentanza dell'agente). Le dichiarazioni che riguardano l'esecuzione del contratto concluso per il tramite dell'agente e i reclami relativi alle inadempienze contrattuali sono validamente fatti all'agente. L'agente può chiedere i provvedimenti cau

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1807`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1748. (( (Diritti dell'agente). )) ((Per tutti gli affari conclusi durante il contratto l'agente ha diritto alla provvigione quando l'operazione è stata conclusa per effetto del suo intervento. La provvigione è dovuta anche per gli affari conclusi dal prepone

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1805`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1746. (Obblighi dell'agente). Nell'esecuzione dell'incarico l'agente deve tutelare gli interessi del preponente e agire con lealtà e buona fede. In particolare, deve adempiere l'incarico affidatogli in conformità delle istruzioni ricevute e fornire al prepone

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1761`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1702. (Riscossione dei crediti da parte dell'ultimo vettore). L'ultimo vettore rappresenta i vettori precedenti per la riscossione dei rispettivi crediti che nascono dal contratto di trasporto e per l'esercizio del privilegio sulle cose trasportate. Se egli o

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3085`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2856. (Surrogazione del creditore perdente). Il creditore che ha ipoteca sopra uno o più immobili, qualora si trovi perdente perché sul loro prezzo si è in tutto o in parte soddisfatto un creditore anteriore, la cui ipoteca si estendeva ad altri beni dello st

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1810`

> REGIO DECRETO 16 marzo 1942, n. 262  concessione dell'indennità non priva comunque l'agente del diritto all'eventuale risarcimento dei danni. L'agente decade dal diritto all'indennità prevista dal presente articolo se, nel termine di un anno dallo scioglimento del rapporto, omette di comunicare al p

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1808`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1749. (( (Obblighi del preponente). )) ((Il preponente, nei rapporti con l'agente, deve agire con lealtà e buona fede. Egli deve mettere a disposizione dell'agente la documentazione necessaria relativa ai beni o servizi trattati e fornire all'agente le inform

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art99`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 i dell'articolo 55. ((209)) 3. L'avviso di accertamento di cui ai commi 1 e 2, emesso entro i termini di cui all'articolo 57, costituisce titolo esecutivo ai fini della riscossione. 4. Qualora l'Amministrazione finanziaria verifichi sul

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
