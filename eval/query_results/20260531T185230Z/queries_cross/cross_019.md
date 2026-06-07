# cross_019 — tributario+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:58 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 68.4s (ret 0.1s + llm 68.1s) |

## Query

> Come si impugna il diniego di autotutela tributaria?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Question:** "Come si impugna il diniego di autotutela tributaria?" (How to appeal a denial of tax self-correction/autotutela?)
    *   **Research Packet:** Contains 10 sources (Legge 212/2000, D.P.R. 447/1988, DLgs 104/2010, R.D. 1443/1940, etc.).

2.  **Analyze the Research Packet for Relevant Information:**
    *   Source [1] & [10]: Legge 27 luglio 2000, n. 212 (Legge Finanziaria 2001 / Norme sulla trasparenza e motivazione). Art. 7 talks about motivation of acts and notification. It mentions "atti dell'amministrazione finanziaria autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria".
    *   Source [2]: D.P.R. 447/1988 (Codice Proc Penale Tributario). Art. 186 talks about inobservance of tax norms not making acts inadmissible. Not directly about appeal procedure for autotutela denial.
    *   Source [3]: Legge 212/2000, Art. 4. About decree-law usage. Irrelevant to appeal procedure.
    *   Source [4]: DLgs 104/2010 (Riforma Processo Tributario). Art. 18 mentions "regolamento di competenza". Art. 106 mentions "ricorso in appello" content. This is relevant for general tax appeal structure but specific to autotutela denial?
    *   Source [5]: DLgs 104/2010, Art. 101 (Ricorso in appello). Content of appeal.
    *   Source [6]: R.D. 1443/1940 (Codice Proc Civile). Art. 264 (Impugnazione e discussione) - about contesting accounts. Irrelevant to tax autotutela.
    *   Source [7]: DLgs 218/1997 (Procedimento Tributario Amministrativo). Art. 12 talks about "Istanza del contribuente" regarding notification of assessment/rectification/recovery acts where no prior adversarial procedure applies. It mentions "anteriormente all'impugnazione dell'atto innanzi alla C...". This is crucial for tax appeals (Commissione Tributaria).
    *   Source [8]: R.D. 1443/1940, Art. 43 (Regolamento facoltativo di competenza). About jurisdiction regulation appeal. Irrelevant to autotutela denial specifically unless it's a competence issue.
    *   Source [9]: DLgs 14/2019. Art. 70 about homologation sentence. Irrelevant.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks: "How to appeal a denial of tax self-correction (autotutela)?"
    *   The packet contains general procedural rules for tax appeals (DLgs 218/1997 Art. 12, DLgs 104/2010 Art. 101/18), and motivation requirements (Legge 212/2000).
    *   However, the packet *does not* explicitly contain a specific article detailing the exact appeal procedure for a "diniego di autotutela" (denial of self-correction) specifically. Usually, this falls under general tax appeal rules (Ricorso alla Commissione Tributaria Provinciale/Regionale).
    *   Source [7] mentions: "In caso di notifica di avviso di accertamento... per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C[ommissione Tributaria]". This implies the general rule for tax acts.
    *   Source [1] mentions: "Gli atti dell'amministrazione finanziaria autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria sono motivati...".
    *   There is a significant gap: The packet does not explicitly state the specific time limits (30 days) or the exact body (Commissione Tributaria Provinciale) for appealing an autotutela denial, nor does it explicitly mention "autotutela" in the text provided. It mentions general tax acts.
    *   I must strictly use the sources provided. If the specific info isn't there, I cannot invent it. I must state what is available or note the gap.
    *   Actually, looking closely at Source [7], it refers to "impugnazione dell'atto innanzi alla C[ommissione Tributaria]". This supports the qualification that tax acts are appealed before the Tax Commission.
    *   Source [1] confirms these acts are "autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria".

4.  **Drafting the Analysis (CoT):**

    *   **QUALIFICAZIONE:** The act is a denial of autotutela by tax administration. It falls under general tax administrative acts subject to judicial review. Source [1] confirms financial administration acts are autonomously appealable before tax jurisdiction organs. Source [7] mentions the taxpayer can appeal an act before the Tax Commission (C[ommissione Tributaria]).
    *   **NORMA APPLICABILE:** The procedural framework for appealing tax acts is found in DLgs 218/1997 (Source [7]) and general rules on motivation (Legge 212/2000 Source [1]). Specifically, the appeal must be filed before the Tax Commission.
    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza). I cannot cite jurisprudence from the packet if it's not there. I must note this or rely on statutory interpretation. Since the instruction says "Reason ONLY on facts in the Research Packet", and there is no jurisprudence source, I should indicate the lack of specific case law in the packet for this step or focus on the statutory text available. Wait, Source [4] mentions "ordinanza che pronuncia sulla competenza... può essere impugnata col regolamento di competenza". This is about jurisdiction.
    *   **VALUTAZIONE:** Based on the provided sources, the procedural path points to a tax appeal (Ricorso) before the Tax Commission. However, specific details like time limits or exact form for "autotutela denial" are not explicitly detailed in the packet text provided (Source [7] is general about assessment/rectification).
    *   **GAP ANALYSIS:** The packet lacks explicit mention of "autotutela" and specific appeal deadlines (e.g., 30 days) or the specific body name beyond "organi della giurisdizione tributaria".

5.  **Refining Citations:**
    *   Must use `source_id` exactly as in the packet (e.g., `urn:nir:stato:legge:2000-07-27;212~art7`).
    *   Claim type must be FACT.
    *   Source Authority: NORMATTIVA, CODICE_PROC_PENALE, DLGS, etc. based on the source title.

6.  **Constructing JSON:**
    *   Ensure `analysis_sections` follows the exact

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Question:** "Come si impugna il diniego di autotutela tributaria?" (How to appeal a denial of tax self-correction/autotutela?)
    *   **Research Packet:** Contains 10 sources (Legge 212/2000, D.P.R. 447/1988, DLgs 104/2010, R.D. 1443/1940, etc.).

2.  **Analyze the Research Packet for Relevant Information:**
    *   Source [1] & [10]: Legge 27 luglio 2000, n. 212 (Legge Finanziaria 2001 / Norme sulla trasparenza e motivazione). Art. 7 talks about motivation of acts and notification. It mentions "atti dell'amministrazione finanziaria autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria".
    *   Source [2]: D.P.R. 447/1988 (Codice Proc Penale Tributario). Art. 186 talks about inobservance of tax norms not making acts inadmissible. Not directly about appeal procedure for autotutela denial.
    *   Source [3]: Legge 212/2000, Art. 4. About decree-law usage. Irrelevant to appeal procedure.
    *   Source [4]: DLgs 104/2010 (Riforma Processo Tributario). Art. 18 mentions "regolamento di competenza". Art. 106 mentions "ricorso in appello" content. This is relevant for general tax appeal structure but specific to autotutela denial?
    *   Source [5]: DLgs 104/2010, Art. 101 (Ricorso in appello). Content of appeal.
    *   Source [6]: R.D. 1443/1940 (Codice Proc Civile). Art. 264 (Impugnazione e discussione) - about contesting accounts. Irrelevant to tax autotutela.
    *   Source [7]: DLgs 218/1997 (Procedimento Tributario Amministrativo). Art. 12 talks about "Istanza del contribuente" regarding notification of assessment/rectification/recovery acts where no prior adversarial procedure applies. It mentions "anteriormente all'impugnazione dell'atto innanzi alla C...". This is crucial for tax appeals (Commissione Tributaria).
    *   Source [8]: R.D. 1443/1940, Art. 43 (Regolamento facoltativo di competenza). About jurisdiction regulation appeal. Irrelevant to autotutela denial specifically unless it's a competence issue.
    *   Source [9]: DLgs 14/2019. Art. 70 about homologation sentence. Irrelevant.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks: "How to appeal a denial of tax self-correction (autotutela)?"
    *   The packet contains general procedural rules for tax appeals (DLgs 218/1997 Art. 12, DLgs 104/2010 Art. 101/18), and motivation requirements (Legge 212/2000).
    *   However, the packet *does not* explicitly contain a specific article detailing the exact appeal procedure for a "diniego di autotutela" (denial of self-correction) specifically. Usually, this falls under general tax appeal rules (Ricorso alla Commissione Tributaria Provinciale/Regionale).
    *   Source [7] mentions: "In caso di notifica di avviso di accertamento... per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C[ommissione Tributaria]". This implies the general rule for tax acts.
    *   Source [1] mentions: "Gli atti dell'amministrazione finanziaria autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria sono motivati...".
    *   There is a significant gap: The packet does not explicitly state the specific time limits (30 days) or the exact body (Commissione Tributaria Provinciale) for appealing an autotutela denial, nor does it explicitly mention "autotutela" in the text provided. It mentions general tax acts.
    *   I must strictly use the sources provided. If the specific info isn't there, I cannot invent it. I must state what is available or note the gap.
    *   Actually, looking closely at Source [7], it refers to "impugnazione dell'atto innanzi alla C[ommissione Tributaria]". This supports the qualification that tax acts are appealed before the Tax Commission.
    *   Source [1] confirms these acts are "autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria".

4.  **Drafting the Analysis (CoT):**

    *   **QUALIFICAZIONE:** The act is a denial of autotutela by tax administration. It falls under general tax administrative acts subject to judicial review. Source [1] confirms financial administration acts are autonomously appealable before tax jurisdiction organs. Source [7] mentions the taxpayer can appeal an act before the Tax Commission (C[ommissione Tributaria]).
    *   **NORMA APPLICABILE:** The procedural framework for appealing tax acts is found in DLgs 218/1997 (Source [7]) and general rules on motivation (Legge 212/2000 Source [1]). Specifically, the appeal must be filed before the Tax Commission.
    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza). I cannot cite jurisprudence from the packet if it's not there. I must note this or rely on statutory interpretation. Since the instruction says "Reason ONLY on facts in the Research Packet", and there is no jurisprudence source, I should indicate the lack of specific case law in the packet for this step or focus on the statutory text available. Wait, Source [4] mentions "ordinanza che pronuncia sulla competenza... può essere impugnata col regolamento di competenza". This is about jurisdiction.
    *   **VALUTAZIONE:** Based on the provided sources, the procedural path points to a tax appeal (Ricorso) before the Tax Commission. However, specific details like time limits or exact form for "autotutela denial" are not explicitly detailed in the packet text provided (Source [7] is general about assessment/rectification).
    *   **GAP ANALYSIS:** The packet lacks explicit mention of "autotutela" and specific appeal deadlines (e.g., 30 days) or the specific body name beyond "organi della giurisdizione tributaria".

5.  **Refining Citations:**
    *   Must use `source_id` exactly as in the packet (e.g., `urn:nir:stato:legge:2000-07-27;212~art7`).
    *   Claim type must be FACT.
    *   Source Authority: NORMATTIVA, CODICE_PROC_PENALE, DLGS, etc. based on the source title.

6.  **Constructing JSON:**
    *   Ensure `analysis_sections` follows the exact

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art7` | 0.4474 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art220` | -0.9493 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art4` | -1.8426 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art18` | -2.6144 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art106` | -3.2763 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art291` | -4.3655 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | -5.4019 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art49` | -8.5489 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art70` | -9.2540 | hybrid_rrf |  |
| 10 | `urn:nir:stato:legge:2000-07-27;212~art7` | -9.5048 | hybrid_rrf |  |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1992-12-31;546~art19`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 Art. 7 Chiarezza e motivazione degli atti 1. Gli atti dell'amministrazione finanziaria ((, autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria,)) sono motivati ((, a pena di annullabilità, indicando specificamente i presupposti, i mezzi di prova)

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art220`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 186 Inosservanza di norme tributarie 1. Quando la legge assoggetta un atto a una imposta o a una tassa, l'inosservanza della norma tributaria non rende inammissibile l'atto né impedisce il suo compimento, salve le sanzioni finanz

**[3]** `urn:nir:stato:legge:2000-07-27;212~art4`

> LEGGE 27 luglio 2000, n. 212 Art. 4 Utilizzo del decreto-legge in materia tributaria 1. Non si può disporre con decreto-legge l'istituzione di nuovi tributi nè prevedere l'applicazione di tributi esistenti ad altre categorie di soggetti.

**[4]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art18`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 , richiede d'ufficio il regolamento di competenza. L'ordinanza che pronuncia sulla competenza e sulla domanda cautelare può essere impugnata col regolamento di competenza, oppure nei modi ordinari quando insieme con la pronuncia sulla competenza si impugna q

**[5]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art106`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 101 Contenuto del ricorso in appello 1. Il ricorso in appello deve contenere l'indicazione del ricorrente, del difensore, delle parti nei confronti delle quali è proposta l'impugnazione, della sentenza che si impugna, nonché l'esposizione sommaria dei f

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art291`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 264. (Impugnazione e discussione). La parte che impugna il conto deve specificare le partite che intende contestare. Se chiede un termine per la specificazione, il giudice istruttore fissa un'udienza per tale scopo. Se le parti, in seguito alla discussione

**[7]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art49`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 43. (Regolamento facoltativo di competenza). ((Il provvedimento)) che ha pronunciato sulla competenza insieme col merito può essere ((impugnato)) con l'istanza di regolamento di competenza, oppure nei modi ordinari quando insieme con la pronuncia sulla com

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art70`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 )) 8. La sentenza ((che provvede sull'omologazione)) è comunicata ai creditori ed è pubblicata entro ((i due giorni successivi)) a norma del comma 1. La sentenza è impugnabile ai sensi dell'articolo 51. 9. ((COMMA ABROGATO DAL D.LGS. 13 SETTEMBRE 2024, N. 1

**[10]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 ici e dipendenti, fermo l'obbligo di autonoma notificazione della cartella di pagamento nei loro confronti. )) 2. Gli atti dell'amministrazione finanziaria e dei concessionari della riscossione devono tassativamente indicare: a) l'ufficio presso il quale è possibile otte

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
