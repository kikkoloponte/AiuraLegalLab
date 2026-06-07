# trib_001 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:08 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 66.9s (ret 0.2s + llm 66.5s) |

## Query

> Quali sono i principi fondamentali dello Statuto del contribuente?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **User Question:** "Quali sono i principi fondamentali dello Statuto del contribuente?" (What are the fundamental principles of the Taxpayer's Statute?)
    *   **Research Packet:** Contains 10 sources (Laws, DPRs) with specific IDs and text snippets.

2.  **Analyze the Research Packet for Relevant Information:**
    *   Source [1]: L.C. 1948 n.5 Art. 4 (Minorities). Irrelevant to Taxpayer Statute principles directly, though mentions Constitution harmony.
    *   Source [2]: L.C. 1971 n.1 Art. 2 (Modifies T.A. Statute Art. 4). Irrelevant.
    *   Source [3]: L.C. 1999 n.1 Art. 3 (Constitution Art. 123 modification). Irrelevant.
    *   Source [4]: L.C. 1971 n.1 Art. 3 (Modifies T.A. Statute Art. 5). Irrelevant.
    *   Source [5]: DPR 1973 n.600 Art. 60 (Text snippet mentions "Statuto dei diritti del contribuente" in title context or reference, but text is about interposed persons and tax payments). Wait, looking closely at Source [5] text: "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 ... recante lo Statuto dei diritti del contribuente))". The title mentions it, but the text snippet provided is about Art. 60 (likely old numbering or specific article). Actually, looking at the text: "Le persone interposte... possono chi...". This looks like a fragment of Art. 37 mentioned in the `articolo` field ("Art. 37"). The title says DPR 1973 n. 600. This is the famous "Statuto dei diritti del contribuente" (DPR 600/1973). However, the text provided doesn't explicitly list the *principles* in a clear way like "Principle of Equality", etc., but mentions tax payment rules and interposed persons.
    *   Source [6]: DPR 1986 n. 917 Art. 124 (Tax deductions). Irrelevant to fundamental principles definition.
    *   Source [7]: DPR 1988 n. 447 Art. 725 (Criminal Procedure Code, Mutual recognition). Irrelevant.
    *   Source [8]: DPR 1986 n. 917 Art. 138 (Accounting principles for tax purposes). Irrelevant.
    *   Source [9]: DPR 1986 n. 917 Art. 140 (Normal value of goods/services). Irrelevant.
    *   Source [10]: L. 2000 n. 212 Art. 1 ("Principi generali"). Text: "Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione...". This is the Law implementing Constitutional principles (likely regarding tax procedure or similar).

    *   **Critical Observation:** The Research Packet contains Source [5] which explicitly mentions "Statuto dei diritti del contribuente" in its title/context within the text provided ("recante lo Statuto dei diritti del contribuente")). However, the specific *principles* listed (e.g., burden of proof, right to defense, etc.) are not fully detailed in the snippets provided for Source [5]. The snippet cuts off.
    *   Source [10] mentions "Principi generali" and "attuazione delle norme della Costituzione".
    *   There is no source in the packet that explicitly lists the specific fundamental principles (like Art. 3 of DPR 600/1973, or general principles like legality, equality) with full text definitions other than the title reference in Source [5] and the general constitutional link in Source [10].
    *   Wait, I must reason ONLY on facts in the Research Packet. If the packet doesn't contain the specific list of principles (e.g., "Principle of Legality", "Principle of Equality"), I cannot invent them based on external knowledge. I can only cite what is there.
    *   Source [5] Title: "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600". Text snippet mentions "recante lo Statuto dei diritti del contribuente". This identifies the source of the principles.
    *   Source [10] Title: "LEGGE 27 luglio 2000, n. 212". Art. 1 "Principi generali". Text: "Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione...". This suggests the law implements constitutional norms regarding taxpayers (likely tax procedure).
    *   Source [1] mentions L.C. 1948 n.5 Art. 4 regarding harmony with Constitution and principles of legal order.

    *   **Problem:** The user asks for "principi fondamentali dello Statuto del contribuente". The packet identifies DPR 600/1973 as the source (Source [5]), but the text snippet doesn't list the specific principles (like Art. 2, 3, etc. of that statute). It only mentions the title and a fragment about interposed persons.
    *   **Constraint:** "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Constraint:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id from the Packet).
    *   **Strategy:** I must state what is available in the packet. I can identify DPR 600/1973 as the Statuto dei diritti del contribuente based on Source [5]. I can mention that L.C. 1948 n.5 Art. 4 requires harmony with Constitution (Source [1]). I must avoid claiming specific principles not explicitly in the text if they aren't there, or use "VALUTAZIONE PERSONALE" for reasoning about what is missing/implicit without inventing facts.
    *   Actually, looking at Source [5] again: `titolo`: ... `testo`: ... `recante lo Statuto dei diritti del contribuente`. This confirms the document identity.
    *   Looking at Source [10]: `Art. 1 Principi generali`. Text mentions implementation of Constitution norms.
    *   I need to answer the question based *only* on the packet. If the packet doesn't list the principles explicitly (e.g., "Principle of Equality"), I cannot cite them as facts from the packet unless they are in the text. The text for Source [5] is truncated ("... possono chi").
    *   However, I can state that DPR 600/1973 is the Statuto dei diritti del contribuente (Source [5]). I can mention L.C. 1948 n.5 Art. 4

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **User Question:** "Quali sono i principi fondamentali dello Statuto del contribuente?" (What are the fundamental principles of the Taxpayer's Statute?)
    *   **Research Packet:** Contains 10 sources (Laws, DPRs) with specific IDs and text snippets.

2.  **Analyze the Research Packet for Relevant Information:**
    *   Source [1]: L.C. 1948 n.5 Art. 4 (Minorities). Irrelevant to Taxpayer Statute principles directly, though mentions Constitution harmony.
    *   Source [2]: L.C. 1971 n.1 Art. 2 (Modifies T.A. Statute Art. 4). Irrelevant.
    *   Source [3]: L.C. 1999 n.1 Art. 3 (Constitution Art. 123 modification). Irrelevant.
    *   Source [4]: L.C. 1971 n.1 Art. 3 (Modifies T.A. Statute Art. 5). Irrelevant.
    *   Source [5]: DPR 1973 n.600 Art. 60 (Text snippet mentions "Statuto dei diritti del contribuente" in title context or reference, but text is about interposed persons and tax payments). Wait, looking closely at Source [5] text: "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 ... recante lo Statuto dei diritti del contribuente))". The title mentions it, but the text snippet provided is about Art. 60 (likely old numbering or specific article). Actually, looking at the text: "Le persone interposte... possono chi...". This looks like a fragment of Art. 37 mentioned in the `articolo` field ("Art. 37"). The title says DPR 1973 n. 600. This is the famous "Statuto dei diritti del contribuente" (DPR 600/1973). However, the text provided doesn't explicitly list the *principles* in a clear way like "Principle of Equality", etc., but mentions tax payment rules and interposed persons.
    *   Source [6]: DPR 1986 n. 917 Art. 124 (Tax deductions). Irrelevant to fundamental principles definition.
    *   Source [7]: DPR 1988 n. 447 Art. 725 (Criminal Procedure Code, Mutual recognition). Irrelevant.
    *   Source [8]: DPR 1986 n. 917 Art. 138 (Accounting principles for tax purposes). Irrelevant.
    *   Source [9]: DPR 1986 n. 917 Art. 140 (Normal value of goods/services). Irrelevant.
    *   Source [10]: L. 2000 n. 212 Art. 1 ("Principi generali"). Text: "Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione...". This is the Law implementing Constitutional principles (likely regarding tax procedure or similar).

    *   **Critical Observation:** The Research Packet contains Source [5] which explicitly mentions "Statuto dei diritti del contribuente" in its title/context within the text provided ("recante lo Statuto dei diritti del contribuente")). However, the specific *principles* listed (e.g., burden of proof, right to defense, etc.) are not fully detailed in the snippets provided for Source [5]. The snippet cuts off.
    *   Source [10] mentions "Principi generali" and "attuazione delle norme della Costituzione".
    *   There is no source in the packet that explicitly lists the specific fundamental principles (like Art. 3 of DPR 600/1973, or general principles like legality, equality) with full text definitions other than the title reference in Source [5] and the general constitutional link in Source [10].
    *   Wait, I must reason ONLY on facts in the Research Packet. If the packet doesn't contain the specific list of principles (e.g., "Principle of Legality", "Principle of Equality"), I cannot invent them based on external knowledge. I can only cite what is there.
    *   Source [5] Title: "DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600". Text snippet mentions "recante lo Statuto dei diritti del contribuente". This identifies the source of the principles.
    *   Source [10] Title: "LEGGE 27 luglio 2000, n. 212". Art. 1 "Principi generali". Text: "Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione...". This suggests the law implements constitutional norms regarding taxpayers (likely tax procedure).
    *   Source [1] mentions L.C. 1948 n.5 Art. 4 regarding harmony with Constitution and principles of legal order.

    *   **Problem:** The user asks for "principi fondamentali dello Statuto del contribuente". The packet identifies DPR 600/1973 as the source (Source [5]), but the text snippet doesn't list the specific principles (like Art. 2, 3, etc. of that statute). It only mentions the title and a fragment about interposed persons.
    *   **Constraint:** "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Constraint:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id from the Packet).
    *   **Strategy:** I must state what is available in the packet. I can identify DPR 600/1973 as the Statuto dei diritti del contribuente based on Source [5]. I can mention that L.C. 1948 n.5 Art. 4 requires harmony with Constitution (Source [1]). I must avoid claiming specific principles not explicitly in the text if they aren't there, or use "VALUTAZIONE PERSONALE" for reasoning about what is missing/implicit without inventing facts.
    *   Actually, looking at Source [5] again: `titolo`: ... `testo`: ... `recante lo Statuto dei diritti del contribuente`. This confirms the document identity.
    *   Looking at Source [10]: `Art. 1 Principi generali`. Text mentions implementation of Constitution norms.
    *   I need to answer the question based *only* on the packet. If the packet doesn't list the principles explicitly (e.g., "Principle of Equality"), I cannot cite them as facts from the packet unless they are in the text. The text for Source [5] is truncated ("... possono chi").
    *   However, I can state that DPR 600/1973 is the Statuto dei diritti del contribuente (Source [5]). I can mention L.C. 1948 n.5 Art. 4

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4` | 3.4835 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2` | 0.3663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3` | -0.0998 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3` | -0.2036 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60` | -0.3100 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124` | -0.4634 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725` | -1.5843 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art138` | -2.0774 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art140` | -2.0966 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:2000-07-27;212~art1` | -3.3706 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:legge.costituzionale:1948-02-26;5~art4`

> LEGGE COSTITUZIONALE 26 febbraio 1948, n. 5 Art. 4 ((In armonia con la Costituzione e i principi dell'ordinamento giuridico dello Stato e col rispetto degli obblighi internazionali e degli interessi nazionali - tra i quali è compreso quello della tutela delle minoranze linguistiche locali - nonchè d

**[2]** `urn:nir:stato:legge.costituzionale:1971-11-10;1~art2`

> LEGGE COSTITUZIONALE 10 novembre 1971, n. 1 Art. 2 L'articolo 4 dello Statuto speciale per il Trentino-Alto Adige, approvato con legge costituzionale 26 febbraio 1948, n. 5 , è sostituito dal seguente: "In armonia con la Costituzione e i principi dell'ordinamento giuridico dello Stato e col rispetto

**[3]** `urn:nir:stato:legge.costituzionale:1999-11-22;1~art3`

> LEGGE COSTITUZIONALE 22 novembre 1999, n. 1 Art. 3 (Modifica dell'articolo 123 della Costituzione) 1. L' articolo 123 della Costituzione è sostituito dal seguente: "Art. 123. - Ciascuna Regione ha uno statuto che, in armonia con la Costituzione, ne determina la forma di governo e i principi fondamen

**[4]** `urn:nir:stato:legge.costituzionale:1971-11-10;1~art3`

> LEGGE COSTITUZIONALE 10 novembre 1971, n. 1 Art. 3 L'articolo 5 dello Statuto speciale per il Trentino-Alto Adige, approvato con legge costituzionale 26 febbraio 1948, n. 5 , è sostituito dal seguente: "La regione, nei limiti del precedente articolo e dei principi stabiliti dalle leggi dello Stato,

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art60`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  2000, n. 212 , recante lo Statuto dei diritti del contribuente)) . Le persone interposte, che provino di aver pagato imposte in relazione a redditi successivamente imputati, a norma del comma terzo, ad altro contribuente, possono chi

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art124`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 99 ((Oneri fiscali e contributivi )) (( 1. Le imposte sui redditi e quelle per le quali è prevista la rivalsa, anche facoltativa, non sono ammesse in deduzione. Le altre imposte sono deducibili nell'esercizio in cui avviene il pag

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art725`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-ter (( (Tutela dei diritti fondamentali della persona nel mutuo riconoscimento). )) (( 1. L'autorità giudiziaria provvede al riconoscimento e all'esecuzione se non sussistono fondate ragioni per ritenere che l'imputato o il c

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art138`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 quinquies. I commi 3-bis, 3-ter e 3-quater non si applicano ai soggetti che redigono il bilancio in base ai principi contabili internazionali di cui al regolamento (CE) n. 1606/2002 del Parlamento europeo e del Consiglio, del 19 luglio

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art140`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917  alla corretta applicazione di tali principi, delle passività assumono rilievo anche ai fini fiscali. (133) 2. Per la determinazione del valore normale dei beni e dei servizi e, con riferimento alla data in cui si considerano conseguit

**[10]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
