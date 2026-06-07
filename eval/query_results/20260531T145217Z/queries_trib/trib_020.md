# trib_020 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:25 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 27.3s (ret 0.3s + llm 26.8s) |

## Query

> Quali sono le esenzioni IVA per le operazioni in ambito sanitario?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **User Question:** "Quali sono le esenzioni IVA per le operazioni in ambito sanitario?" (What are the VAT exemptions for operations in the health sector?)
    *   **Research Packet Content:** I need to scan the provided `source_id` list and their texts to find information related to VAT (IVA) exemptions in the health sector.

2.  **Scan Research Packet for Keywords:**
    *   Keywords: "IVA", "imposta sul valore aggiunto", "esenzioni", "sanitario", "health".
    *   Source [1]: DLgs 206/2005 Art. 16 - Price indication exemptions (consumer protection). Not VAT.
    *   Source [2]: RD 1398/1930 Art. 590-sexies - Criminal liability in health sector. Not VAT.
    *   Source [3]: DLgs 206/2005 Art. 16 (continued) - Exemptions for non-food products. Not VAT.
    *   Source [4]: DLgs 14/2019 Art. 324 - Bankruptcy exemptions. Not VAT.
    *   Source [5]: DLgs 104/2010 Art. 126 - Electoral jurisdiction. Not VAT.
    *   Source [6]: DLgs 33/2013 Art. 41 - Transparency of National Health Service (SSN). Mentions "amministrazioni e gli enti del servizio sanitario nazionale". Does not explicitly mention VAT exemptions in the text provided, though it relates to health sector administration.
    *   Source [7]: Legge 300/1970 Art. 41 - Fiscal exemptions (bollo, imposte di registro). Not specifically IVA on operations.
    *   Source [8]: DPR 447/1988 Art. 382-bis - Criminal procedure in health sector (arrests). Not VAT.
    *   Source [9]: DPR 633/1972 Art. 54-quater - Liquidation of tax for non-residents (VAT context implied by "imposta dovuta", but text is cut off/fragmented). Title mentions "Liquidazione dell'imposta dovuta...". This looks like VAT related (DPR 633 is the main VAT code in Italy), but the text provided doesn't explicitly list health sector exemptions. It talks about non-residents and automated procedures.
    *   Source [10]: DPR 600/1973 Art. 18 - VAT registers (registri ai fini dell'imposta sul valore aggiunto). Mentions "contribuenti possono tenere i registri...". Does not list exemptions for health sector operations specifically in the text provided.

3.  **Evaluate Findings:**
    *   The Research Packet contains sources related to VAT (DPR 633/1972, DPR 600/1973) and Health Sector (DLgs 33/2013, RD 1398/1930).
    *   However, NONE of the provided text snippets explicitly list "IVA exemptions for operations in the health sector".
    *   Source [6] mentions transparency of SSN.
    *   Source [7] mentions fiscal exemptions (bollo, registro) but not IVA specifically on services/goods for health.
    *   Source [9] is from DPR 633/1972 (VAT Code), Art. 54-quater, but the text provided discusses non-residents and liquidation procedures, not specific exemptions for health operations.
    *   Source [10] is DPR 600/1973 (Income Tax/VAT registers), mentions VAT registers but no exemptions list.

    *   **Critical Constraint:** "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Critical Constraint:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id from the Packet).

    *   Since the Packet does not contain specific text defining VAT exemptions for health sector operations, I cannot cite a source that says "Health services are exempt from VAT".
    *   If I state general knowledge about VAT exemptions in health (e.g., medical acts are exempt), I would be violating the citation contract because there is no `source_id` supporting that specific claim in the provided text.
    *   Therefore, the analysis must reflect that the Packet does not contain this information, or rely on what IS present (e.g., general VAT rules mentioned in [9] and [10] but noting the lack of specific exemption list).
    *   However, usually, in these tasks, if the info isn't there, I should state based on the available text. The prompt asks "Quali sono le esenzioni IVA...". If the packet doesn't say, I must report that limitation or analyze what is present regarding VAT/Health intersection.
    *   Looking closely at Source [6]: It talks about transparency of SSN entities. No VAT exemption mentioned in text.
    *   Looking closely at Source [7]: Fiscal exemptions (bollo, registro). Not IVA.
    *   Looking closely at Source [9] & [10]: Mention VAT ("imposta sul valore aggiunto", "imposta dovuta"). But no specific health exemption list.

    *   **Strategy:** I must adhere strictly to the packet. If the packet doesn't have the answer, I cannot invent it. I will analyze what is available regarding VAT and Health in the packet.
    *   Actually, looking at Source [9], title says "Liquidazione dell'imposta dovuta...". Text mentions "soggetti non residenti". Not health exemptions.
    *   Looking at Source [10], text mentions "registri ai fini dell'imposta sul valore aggiunto".
    *   There is no source in the packet that explicitly lists VAT exemptions for health operations (e.g., medical acts, pharmaceuticals).
    *   Therefore, I must conclude based on the provided text that specific VAT exemption details are not detailed in this Packet, or cite the general VAT references available ([9], [10]) while noting the gap.
    *   Wait, the instruction says "Ragioni SOLO sui fatti nel Research Packet." If I answer with external knowledge (e.g., "Medical acts are exempt"), I violate the citation rule because there is no source_id for that claim in the packet.
    *   So, the `VALUTAZIONE` step must reflect this limitation using `ungrounded_reasoning` if necessary, or simply state what is found.
    *   Actually, looking at Source [1], it talks about "Esenzioni" (Exemptions) but regarding price indication (Art. 16 DLgs 206/2005). Not VAT.
    *   Looking at Source [7], "Esenzioni fiscali" (Fiscal exemptions), but for bollo/imposte di registro, not IVA.

    *   **Conclusion:** The Research Packet does not contain the specific information requested (VAT exemptions for health operations). I must report this finding based on the sources provided.
    *   However, I need to structure the JSON according to the CoT schema.
    *   Step 1: QUALIFICAZIONE - Define the legal issue (VAT exemptions in health) and search packet.

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers/articles/years.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **User Question:** "Quali sono le esenzioni IVA per le operazioni in ambito sanitario?" (What are the VAT exemptions for operations in the health sector?)
    *   **Research Packet Content:** I need to scan the provided `source_id` list and their texts to find information related to VAT (IVA) exemptions in the health sector.

2.  **Scan Research Packet for Keywords:**
    *   Keywords: "IVA", "imposta sul valore aggiunto", "esenzioni", "sanitario", "health".
    *   Source [1]: DLgs 206/2005 Art. 16 - Price indication exemptions (consumer protection). Not VAT.
    *   Source [2]: RD 1398/1930 Art. 590-sexies - Criminal liability in health sector. Not VAT.
    *   Source [3]: DLgs 206/2005 Art. 16 (continued) - Exemptions for non-food products. Not VAT.
    *   Source [4]: DLgs 14/2019 Art. 324 - Bankruptcy exemptions. Not VAT.
    *   Source [5]: DLgs 104/2010 Art. 126 - Electoral jurisdiction. Not VAT.
    *   Source [6]: DLgs 33/2013 Art. 41 - Transparency of National Health Service (SSN). Mentions "amministrazioni e gli enti del servizio sanitario nazionale". Does not explicitly mention VAT exemptions in the text provided, though it relates to health sector administration.
    *   Source [7]: Legge 300/1970 Art. 41 - Fiscal exemptions (bollo, imposte di registro). Not specifically IVA on operations.
    *   Source [8]: DPR 447/1988 Art. 382-bis - Criminal procedure in health sector (arrests). Not VAT.
    *   Source [9]: DPR 633/1972 Art. 54-quater - Liquidation of tax for non-residents (VAT context implied by "imposta dovuta", but text is cut off/fragmented). Title mentions "Liquidazione dell'imposta dovuta...". This looks like VAT related (DPR 633 is the main VAT code in Italy), but the text provided doesn't explicitly list health sector exemptions. It talks about non-residents and automated procedures.
    *   Source [10]: DPR 600/1973 Art. 18 - VAT registers (registri ai fini dell'imposta sul valore aggiunto). Mentions "contribuenti possono tenere i registri...". Does not list exemptions for health sector operations specifically in the text provided.

3.  **Evaluate Findings:**
    *   The Research Packet contains sources related to VAT (DPR 633/1972, DPR 600/1973) and Health Sector (DLgs 33/2013, RD 1398/1930).
    *   However, NONE of the provided text snippets explicitly list "IVA exemptions for operations in the health sector".
    *   Source [6] mentions transparency of SSN.
    *   Source [7] mentions fiscal exemptions (bollo, registro) but not IVA specifically on services/goods for health.
    *   Source [9] is from DPR 633/1972 (VAT Code), Art. 54-quater, but the text provided discusses non-residents and liquidation procedures, not specific exemptions for health operations.
    *   Source [10] is DPR 600/1973 (Income Tax/VAT registers), mentions VAT registers but no exemptions list.

    *   **Critical Constraint:** "Ragioni SOLO sui fatti nel Research Packet." (Reason ONLY on facts in the Research Packet).
    *   **Critical Constraint:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id from the Packet).

    *   Since the Packet does not contain specific text defining VAT exemptions for health sector operations, I cannot cite a source that says "Health services are exempt from VAT".
    *   If I state general knowledge about VAT exemptions in health (e.g., medical acts are exempt), I would be violating the citation contract because there is no `source_id` supporting that specific claim in the provided text.
    *   Therefore, the analysis must reflect that the Packet does not contain this information, or rely on what IS present (e.g., general VAT rules mentioned in [9] and [10] but noting the lack of specific exemption list).
    *   However, usually, in these tasks, if the info isn't there, I should state based on the available text. The prompt asks "Quali sono le esenzioni IVA...". If the packet doesn't say, I must report that limitation or analyze what is present regarding VAT/Health intersection.
    *   Looking closely at Source [6]: It talks about transparency of SSN entities. No VAT exemption mentioned in text.
    *   Looking closely at Source [7]: Fiscal exemptions (bollo, registro). Not IVA.
    *   Looking closely at Source [9] & [10]: Mention VAT ("imposta sul valore aggiunto", "imposta dovuta"). But no specific health exemption list.

    *   **Strategy:** I must adhere strictly to the packet. If the packet doesn't have the answer, I cannot invent it. I will analyze what is available regarding VAT and Health in the packet.
    *   Actually, looking at Source [9], title says "Liquidazione dell'imposta dovuta...". Text mentions "soggetti non residenti". Not health exemptions.
    *   Looking at Source [10], text mentions "registri ai fini dell'imposta sul valore aggiunto".
    *   There is no source in the packet that explicitly lists VAT exemptions for health operations (e.g., medical acts, pharmaceuticals).
    *   Therefore, I must conclude based on the provided text that specific VAT exemption details are not detailed in this Packet, or cite the general VAT references available ([9], [10]) while noting the gap.
    *   Wait, the instruction says "Ragioni SOLO sui fatti nel Research Packet." If I answer with external knowledge (e.g., "Medical acts are exempt"), I violate the citation rule because there is no source_id for that claim in the packet.
    *   So, the `VALUTAZIONE` step must reflect this limitation using `ungrounded_reasoning` if necessary, or simply state what is found.
    *   Actually, looking at Source [1], it talks about "Esenzioni" (Exemptions) but regarding price indication (Art. 16 DLgs 206/2005). Not VAT.
    *   Looking at Source [7], "Esenzioni fiscali" (Fiscal exemptions), but for bollo/imposte di registro, not IVA.

    *   **Conclusion:** The Research Packet does not contain the specific information requested (VAT exemptions for health operations). I must report this finding based on the sources provided.
    *   However, I need to structure the JSON according to the CoT schema.
    *   Step 1: QUALIFICAZIONE - Define the legal issue (VAT exemptions in health) and search packet.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16` | 4.0225 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art763` | 3.9675 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16` | 2.0647 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324` | 1.6976 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art131` | 1.4517 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41` | 1.3517 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge:1970-05-20;300~art41` | -0.2600 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art455` | -2.1035 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art98` | -2.1592 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art20` | -2.7925 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 16 Esenzioni 1. Sono esenti dall'obbligo dell'indicazione del prezzo per unità di misura i prodotti per i quali tale indicazione non risulti utile a motivo della loro natura o della loro destinazione, o sia di natura tale da dare luogo a confusione.

**[2]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art763`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 590-sexies. (( (Responsabilità colposa per morte o lesioni personali in ambito sanitario).)) ((Se i fatti di cui agli articoli 589 e 590 sono commessi nell'esercizio della professione sanitaria, si applicano le pene ivi previste salvo quanto disposto dal s

**[3]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art16`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 are espressamente prodotti o categorie di prodotti non alimentari ai quali non si applicano le predette esenzioni. ((25)) ------------- AGGIORNAMENTO (25) Il D.Lgs. 6 agosto 2015, n. 130 ha disposto (con l'art. 2, comma 1) che "Le disposizioni del present

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 324 Esenzioni dai reati di bancarotta 1. Le disposizioni di cui agli articoli 322, comma 3 e 323 non si applicano ai pagamenti e alle operazioni computi in esecuzione di un concordato preventivo o di accordi di ristrutturazione dei debiti omologati o d

**[5]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art131`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 126 Ambito della giurisdizione sul contenzioso elettorale 1. Il giudice amministrativo ha giurisdizione in materia di operazioni elettorali relative al rinnovo degli organi elettivi dei comuni, delle province, delle regioni e all'elezione dei membri del

**[6]** `urn:nir:stato:decreto.legislativo:2013-03-14;33~art41`

> DECRETO LEGISLATIVO 14 marzo 2013, n. 33 Art. 41 Trasparenza del servizio sanitario nazionale 1. Le amministrazioni e gli enti del servizio sanitario nazionale, dei servizi sanitari regionali, ivi comprese le aziende sanitarie territoriali ed ospedaliere, le agenzie e gli altri enti ed organismi pub

**[7]** `urn:nir:stato:legge:1970-05-20;300~art41`

> LEGGE 20 maggio 1970, n. 300 Art. 41 (Esenzioni fiscali) Tutti gli atti e documenti necessari per la attuazione della presente legge e per l'esercizio dei diritti connessi, nonchè tutti gli atti e documenti relativi ai giudizi nascenti dalla sua applicazione sono esenti da bollo, imposte di registro

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art455`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447  o a causa di tali attività, ovvero commessi su cose ivi esistenti o comunque destinate al servizio sanitario o socio-sanitario, quando non è possibile procedere immediatamente all'arresto per ragioni di sicurezza o incolumità pubblic

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art98`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 26 ottobre 1972, n. 633 (Liquidazione dell'imposta dovuta relativamente ((alle operazioni effettuate nell'ambito dei regimi speciali di cui agli articoli 74-quinquies e seguenti)) da soggetti non residenti). ((209)) 1. Avvalendosi di procedure automatizzate l'

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art20`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600  i contribuenti possono tenere i registri ai fini dell'imposta sul valore aggiunto senza operare annotazioni relative a incassi e pagamenti, fermo restando l'obbligo della separata annotazione delle operazioni non soggette a registraz

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
