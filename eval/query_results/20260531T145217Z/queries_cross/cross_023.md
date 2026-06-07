# cross_023 — tributario+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 15:37 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.4s (ret 0.3s + llm 64.9s) |

## Query

> Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** Valid JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (L. 212/2000, R.D. 262/1942, D.P.R. 447/1988, R.D. 1398/1930, D.P.R. 917/1986, D.Lgs. 14/2019, D.P.R. 633/1972, D.P.R. 447/1988 (art 59), L. 212/2000 (art 1), D.P.R. 600/1973).
    *   **Question:** "Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?" (What are the relationships between the principle of ne bis in idem and the dual punitive regime tax-criminal?)

2.  **Evaluate the Research Packet vs. Question:**
    *   The question asks about "ne bis in idem" and the "dual punitive regime" (tributario-penale).
    *   I need to check if the provided sources contain information about this specific legal relationship.
    *   Source [1] (L. 212/2000 Art. 10): Discusses good faith, no sanctions/interests for taxpayer errors. Not directly about ne bis in idem vs dual regime.
    *   Source [2] (R.D. 262/1942 Art. 2516): Cooperative societies principle of equal treatment. Irrelevant.
    *   Source [3] (D.P.R. 447/1988 Art. 696-bis): Mutual recognition principle in criminal procedure (EU law). Mentions EU law implementation but doesn't explicitly discuss ne bis in idem vs tax/criminal dual regime relationship in detail within the text provided.
    *   Source [4] (R.D. 1398/1930 Art. 3-bis): Reservation of code for new crimes. Irrelevant to ne bis in idem specifically regarding tax.
    *   Source [5] (D.P.R. 917/1986 Art. 99): Tax deductions. Irrelevant.
    *   Source [6] (D.Lgs. 14/2019 Art. 317): Prevalence of real precautionary measures in bankruptcy. Irrelevant.
    *   Source [7] (D.P.R. 633/1972 Art. 60-bis): Solidarity in tax payment. Irrelevant.
    *   Source [8] (D.P.R. 447/1988 Art. 59): Mentions fines increased up to double, inadmissibility of request. Doesn't explicitly link ne bis in idem and dual regime.
    *   Source [9] (L. 212/2000 Art. 1): General principles. Irrelevant.
    *   Source [10] (D.P.R. 600/1973 Art. 31-bis.1): Administrative cooperation tools. Irrelevant.

    *   **Critical Finding:** None of the provided sources explicitly discuss the relationship between "ne bis in idem" and the "dual punitive regime" (tributario-penale). The text snippets are truncated or irrelevant to this specific legal doctrine.
    *   **Constraint Check:** I must reason ONLY on facts in the Research Packet. If there is no source for a factual claim, I cannot cite it as fact. I must use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" if I need to state something not supported by the packet (but ideally, I should acknowledge the gap).
    *   **Instruction:** "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Instruction:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id present in the Packet).
    *   **Instruction:** "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." (If you don't have the source → field `ungrounded_reasoning` with prefix... never as a citation).

    *   **Problem:** The question asks about a legal relationship that is not explicitly detailed in the provided text snippets.
    *   **Strategy:** I must analyze what IS in the packet regarding sanctions and principles, but acknowledge the lack of specific information on "ne bis in idem" vs "dual regime" using the `ungrounded_reasoning` or `GAP ANALYSIS`. However, the instruction says "Reason ONLY on facts in the Research Packet". If I answer the question directly without sources, it violates the citation contract.
    *   **Correction:** I must state that the packet does not contain information to fully answer this specific legal relationship based on the provided text. Or, I can look for general principles mentioned (like Art 10 L.212/2000 regarding good faith/sanctions) and see if they touch upon it.
    *   Actually, looking closely at Source [3] (D.P.R. 447/1988 Art. 696-bis): It mentions "Principio del mutuo riconoscimento" and "norme... attuative del diritto dell'Unione europea". Ne bis in idem is an EU principle, but the text doesn't explicitly link it to tax/criminal dual regime.
    *   Source [1] (L. 212/2000 Art. 10) talks about "Tutela dell'affidamento e della buona fede" and "Non sono irrogate sanzioni nè richiesti interessi moratori". This touches on sanctions but not the specific ne bis in idem vs dual regime conflict.
    *   Since I cannot invent facts, I must report that the packet does not contain explicit information linking these two concepts directly, or use `ungrounded_reasoning` to explain the general legal context if allowed (but the instruction says "Reason ONLY on facts... If no source -> ungrounded_reasoning").
    *   Wait, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet). This implies I should not bring outside knowledge. However, to answer the prompt's question ("What are the relationships..."), if the packet doesn't have it, I must state that limitation.
    *   The `GAP ANALYSIS` section is specifically for "cosa manca nel Packet" (what is missing in the Packet). This is the perfect place to admit the lack of information on ne bis in idem vs dual regime.
    *   For the analysis sections, I should try to cite what IS there regarding sanctions/principles if relevant, but acknowledge the specific question's answer isn't fully supported by the packet text provided.
    *   However, strict adherence: "Ogni affermazione fattuale DEVE avere un source_id". If I say "The law says X", it must be from the packet. Since

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** Valid JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (L. 212/2000, R.D. 262/1942, D.P.R. 447/1988, R.D. 1398/1930, D.P.R. 917/1986, D.Lgs. 14/2019, D.P.R. 633/1972, D.P.R. 447/1988 (art 59), L. 212/2000 (art 1), D.P.R. 600/1973).
    *   **Question:** "Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?" (What are the relationships between the principle of ne bis in idem and the dual punitive regime tax-criminal?)

2.  **Evaluate the Research Packet vs. Question:**
    *   The question asks about "ne bis in idem" and the "dual punitive regime" (tributario-penale).
    *   I need to check if the provided sources contain information about this specific legal relationship.
    *   Source [1] (L. 212/2000 Art. 10): Discusses good faith, no sanctions/interests for taxpayer errors. Not directly about ne bis in idem vs dual regime.
    *   Source [2] (R.D. 262/1942 Art. 2516): Cooperative societies principle of equal treatment. Irrelevant.
    *   Source [3] (D.P.R. 447/1988 Art. 696-bis): Mutual recognition principle in criminal procedure (EU law). Mentions EU law implementation but doesn't explicitly discuss ne bis in idem vs tax/criminal dual regime relationship in detail within the text provided.
    *   Source [4] (R.D. 1398/1930 Art. 3-bis): Reservation of code for new crimes. Irrelevant to ne bis in idem specifically regarding tax.
    *   Source [5] (D.P.R. 917/1986 Art. 99): Tax deductions. Irrelevant.
    *   Source [6] (D.Lgs. 14/2019 Art. 317): Prevalence of real precautionary measures in bankruptcy. Irrelevant.
    *   Source [7] (D.P.R. 633/1972 Art. 60-bis): Solidarity in tax payment. Irrelevant.
    *   Source [8] (D.P.R. 447/1988 Art. 59): Mentions fines increased up to double, inadmissibility of request. Doesn't explicitly link ne bis in idem and dual regime.
    *   Source [9] (L. 212/2000 Art. 1): General principles. Irrelevant.
    *   Source [10] (D.P.R. 600/1973 Art. 31-bis.1): Administrative cooperation tools. Irrelevant.

    *   **Critical Finding:** None of the provided sources explicitly discuss the relationship between "ne bis in idem" and the "dual punitive regime" (tributario-penale). The text snippets are truncated or irrelevant to this specific legal doctrine.
    *   **Constraint Check:** I must reason ONLY on facts in the Research Packet. If there is no source for a factual claim, I cannot cite it as fact. I must use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" if I need to state something not supported by the packet (but ideally, I should acknowledge the gap).
    *   **Instruction:** "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Instruction:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id present in the Packet).
    *   **Instruction:** "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." (If you don't have the source → field `ungrounded_reasoning` with prefix... never as a citation).

    *   **Problem:** The question asks about a legal relationship that is not explicitly detailed in the provided text snippets.
    *   **Strategy:** I must analyze what IS in the packet regarding sanctions and principles, but acknowledge the lack of specific information on "ne bis in idem" vs "dual regime" using the `ungrounded_reasoning` or `GAP ANALYSIS`. However, the instruction says "Reason ONLY on facts in the Research Packet". If I answer the question directly without sources, it violates the citation contract.
    *   **Correction:** I must state that the packet does not contain information to fully answer this specific legal relationship based on the provided text. Or, I can look for general principles mentioned (like Art 10 L.212/2000 regarding good faith/sanctions) and see if they touch upon it.
    *   Actually, looking closely at Source [3] (D.P.R. 447/1988 Art. 696-bis): It mentions "Principio del mutuo riconoscimento" and "norme... attuative del diritto dell'Unione europea". Ne bis in idem is an EU principle, but the text doesn't explicitly link it to tax/criminal dual regime.
    *   Source [1] (L. 212/2000 Art. 10) talks about "Tutela dell'affidamento e della buona fede" and "Non sono irrogate sanzioni nè richiesti interessi moratori". This touches on sanctions but not the specific ne bis in idem vs dual regime conflict.
    *   Since I cannot invent facts, I must report that the packet does not contain explicit information linking these two concepts directly, or use `ungrounded_reasoning` to explain the general legal context if allowed (but the instruction says "Reason ONLY on facts... If no source -> ungrounded_reasoning").
    *   Wait, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet). This implies I should not bring outside knowledge. However, to answer the prompt's question ("What are the relationships..."), if the packet doesn't have it, I must state that limitation.
    *   The `GAP ANALYSIS` section is specifically for "cosa manca nel Packet" (what is missing in the Packet). This is the perfect place to admit the lack of information on ne bis in idem vs dual regime.
    *   For the analysis sections, I should try to cite what IS there regarding sanctions/principles if relevant, but acknowledge the specific question's answer isn't fully supported by the packet text provided.
    *   However, strict adherence: "Ogni affermazione fattuale DEVE avere un source_id". If I say "The law says X", it must be from the packet. Since

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art10` | 3.4052 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2709` | 0.8772 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724` | -0.2436 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art7` | -1.4396 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | -1.8089 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317` | -3.6633 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art106` | -4.2392 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59` | -4.6592 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge:2000-07-27;212~art1` | -5.7070 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47` | -6.0516 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art20`
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art13`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art10`

> LEGGE 27 luglio 2000, n. 212 Art. 10 Tutela dell'affidamento e della buona fede. Errori del contribuente 1. I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede. 2. Non sono irrogate sanzioni nè richiesti interessi moratori al

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2709`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516. (( (Rapporti con i soci).)) ((Nella costituzione e nell'esecuzione dei rapporti mutualistici deve essere rispettato il principio di parità di trattamento.))

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-bis (( (Principio del mutuo riconoscimento). )) (( 1. Il principio del mutuo riconoscimento è disciplinato dalle norme del presente titolo e dalle altre disposizioni di legge attuative del diritto dell'Unione europea. 2. Le d

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art7`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis. (( (Principio della riserva di codice). )) ((Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia.))

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 317 Principio di prevalenza delle misure cautelari reali e tutela dei terzi 1. Le condizioni e i criteri di prevalenza rispetto alla gestione concorsuale delle misure cautelari reali sulle cose indicate dall'articolo 142 sono regolate dalle disposizion

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art106`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 Art. 60-bis (Solidarietà nel pagamento dell'imposta) 1. Con decreto del Ministro dell'economia e delle finanze, su proposta degli organi competenti al controllo, sulla base di analisi effettuate su fenomeni di frode, sono individuati i

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 ((, che può essere aumentata fino al doppio, tenuto conto della causa di inammissibilità della richiesta)) . ((6-bis. Gli importi di cui al comma 6 sono adeguati ogni due anni con decreto del Ministro della giustizia, di concerto con

**[9]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis.1 (( (Strumenti di cooperazione amministrativa avanzata). )) (( 1. L'Amministrazione finanziaria, in attuazione del principio di economicità dell'azione amministrativa, si avvale di strumenti di cooperazione amministrativa

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
