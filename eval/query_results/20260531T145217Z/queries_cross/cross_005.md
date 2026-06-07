# cross_005 — civile+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 15:17 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.3s (ret 0.3s + llm 64.9s) |

## Query

> Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (Regio Decreto 262/1942, DPR 917/1986, DLgs 14/2019).
    *   **Question:** "Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?" (What is the opposability to tax authorities of corporate transfer acts and the tax solidarity of the assignee?)

2.  **Analyze the Research Packet Sources:**
    *   [1] Art. 1248 CC: Inopponibilità della compensazione (assignment of claims). Not directly about tax or company transfer opposability to fisco.
    *   [2] Art. 2559 CC: Assignment of credits relative to the transferred business, effect vis-à-vis third parties upon registration in the register (not necessarily tax authority specific, but mentions registration).
    *   [3] Art. 1264 CC: Effect of assignment regarding debtor (notification/acceptance).
    *   [4] DPR 917/1986 Art. 57 (actually text says Art. 47 in title, but content mentions stratification of reserves): Mentions transfer of participations and tax implications (stratificazione delle riserve), D.Lgs 2018 n. 142 update.
    *   [5] Art. 2112 CC: Maintenance of workers' rights in case of business transfer.
    *   [6] Art. 2112 CC (duplicate/continuation): Continuity of identity of rights, usufruct/lease included.
    *   [7] DPR 917/1986 Art. 58 (actually text says Art. 79 in title? No, title says Art. 79 but text starts "Plusvalenze" and references Art. 86 comma 4): Tax implications on capital gains from business transfer. Mentions tax separation.
    *   [8] Art. 2536 CC: Liability of outgoing partner (partnership).
    *   [9] DLgs 14/2019 Art. 212: Collective agreements substitution in case of transfer.
    *   [10] Art. 2506 CC: Forms of spin-off/scission.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "opponibilità al fisco" (opposability to tax authorities) and "solidarietà tributaria del cessionario" (tax solidarity of the assignee).
    *   I need to check if the packet contains information specifically addressing *tax opposability* or *tax solidarity* in the context of business transfer (*cessione d'azienda*).
    *   Source [4] mentions tax implications regarding stratification of reserves and D.Lgs 2018 n. 142 update, but doesn't explicitly define "opponibilità al fisco" rules or general tax solidarity for assignees in a business transfer context (usually Art. 13 of TUIR or specific provisions on VAT/Income Tax).
    *   Source [7] mentions capital gains taxation ("Plusvalenze") and tax separation, but doesn't explicitly state the rule on "opponibilità al fisco" of the act itself or general solidarity liability for unpaid taxes.
    *   Sources [1], [2], [3], [5], [6], [8], [9], [10] are Civil Code (CC) and Labor/Collective agreements, not Tax Law (TUIR). They deal with civil opposability to debtors or workers, not tax authorities.
    *   **Critical Finding:** The Research Packet does NOT contain specific norms defining the "opponibilità al fisco" of business transfer acts nor the general rule on "solidarietà tributaria del cessionario" (tax solidarity). It contains Civil Code provisions about assignment effects and some Tax DPR provisions about capital gains/reserves.
    *   **Constraint:** I must reason ONLY on facts in the Research Packet. If information is missing, I cannot invent it. I must use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" if I need to state something not grounded in a source_id for that specific claim, OR I must acknowledge the gap.
    *   **Instruction:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id from the Packet).
    *   **Instruction:** "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." (If you don't have the source -> field `ungrounded_reasoning` with prefix... never as a citation). Wait, looking at the JSON schema provided in the prompt:
        ```json
        {
          "analysis_sections": [ ... ],
          "overall_confidence": "...",
          "escalation_recommended": false,
          "gaps": []
        }
        ```
        The `citations` array inside sections expects `source_id`. If I cannot cite a source for a claim because it's not in the packet, how do I handle it?
        The instruction says: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This implies if I make a claim without a source, I must mark it as personal evaluation in the content or reasoning field. However, the JSON schema provided for `analysis_sections` has a `citations` array.
        Actually, looking closely at the instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." -> This is strict. If I cannot find it, I should probably indicate in the `gaps` section or use `ungrounded_reasoning` within the content if necessary to explain limitations, but strictly speaking, I shouldn't make factual claims without sources.
        However, the prompt asks me to answer the question based *only* on the packet. If the packet doesn't have the answer (which it seems not to fully), I must report that gap or use personal evaluation for what is missing.
        Let's look at Source [4] and [7]. They are tax-related (DPR 917). Source [4] mentions "In caso di cessione delle partecipazioni...". Source [7] mentions "Per le plusvalenze derivanti da cessione delle aziende...". These touch on the *tax consequences* but not necessarily the *opponibilità al fisco* of the act itself (which is usually a matter of registration/communication to Revenue Agency) or general solidarity liability.
        Source [2] mentions "iscrizione del trasferimento nel registro" for assignment of credits relative to business. This touches on opposability to third parties, but not specifically tax authorities.

    *   **Strategy:** I must analyze what is in the packet regarding the question. Since the packet lacks specific norms on "opponibilità al fisco" (Tax Code) or general "solidarietà tributaria", I will cite the available Tax DPR sources for what

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent article numbers, years, sections, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (Regio Decreto 262/1942, DPR 917/1986, DLgs 14/2019).
    *   **Question:** "Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?" (What is the opposability to tax authorities of corporate transfer acts and the tax solidarity of the assignee?)

2.  **Analyze the Research Packet Sources:**
    *   [1] Art. 1248 CC: Inopponibilità della compensazione (assignment of claims). Not directly about tax or company transfer opposability to fisco.
    *   [2] Art. 2559 CC: Assignment of credits relative to the transferred business, effect vis-à-vis third parties upon registration in the register (not necessarily tax authority specific, but mentions registration).
    *   [3] Art. 1264 CC: Effect of assignment regarding debtor (notification/acceptance).
    *   [4] DPR 917/1986 Art. 57 (actually text says Art. 47 in title, but content mentions stratification of reserves): Mentions transfer of participations and tax implications (stratificazione delle riserve), D.Lgs 2018 n. 142 update.
    *   [5] Art. 2112 CC: Maintenance of workers' rights in case of business transfer.
    *   [6] Art. 2112 CC (duplicate/continuation): Continuity of identity of rights, usufruct/lease included.
    *   [7] DPR 917/1986 Art. 58 (actually text says Art. 79 in title? No, title says Art. 79 but text starts "Plusvalenze" and references Art. 86 comma 4): Tax implications on capital gains from business transfer. Mentions tax separation.
    *   [8] Art. 2536 CC: Liability of outgoing partner (partnership).
    *   [9] DLgs 14/2019 Art. 212: Collective agreements substitution in case of transfer.
    *   [10] Art. 2506 CC: Forms of spin-off/scission.

3.  **Evaluate the Question vs. Packet:**
    *   The question asks about "opponibilità al fisco" (opposability to tax authorities) and "solidarietà tributaria del cessionario" (tax solidarity of the assignee).
    *   I need to check if the packet contains information specifically addressing *tax opposability* or *tax solidarity* in the context of business transfer (*cessione d'azienda*).
    *   Source [4] mentions tax implications regarding stratification of reserves and D.Lgs 2018 n. 142 update, but doesn't explicitly define "opponibilità al fisco" rules or general tax solidarity for assignees in a business transfer context (usually Art. 13 of TUIR or specific provisions on VAT/Income Tax).
    *   Source [7] mentions capital gains taxation ("Plusvalenze") and tax separation, but doesn't explicitly state the rule on "opponibilità al fisco" of the act itself or general solidarity liability for unpaid taxes.
    *   Sources [1], [2], [3], [5], [6], [8], [9], [10] are Civil Code (CC) and Labor/Collective agreements, not Tax Law (TUIR). They deal with civil opposability to debtors or workers, not tax authorities.
    *   **Critical Finding:** The Research Packet does NOT contain specific norms defining the "opponibilità al fisco" of business transfer acts nor the general rule on "solidarietà tributaria del cessionario" (tax solidarity). It contains Civil Code provisions about assignment effects and some Tax DPR provisions about capital gains/reserves.
    *   **Constraint:** I must reason ONLY on facts in the Research Packet. If information is missing, I cannot invent it. I must use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:" if I need to state something not grounded in a source_id for that specific claim, OR I must acknowledge the gap.
    *   **Instruction:** "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." (Every factual claim MUST have a source_id from the Packet).
    *   **Instruction:** "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." (If you don't have the source -> field `ungrounded_reasoning` with prefix... never as a citation). Wait, looking at the JSON schema provided in the prompt:
        ```json
        {
          "analysis_sections": [ ... ],
          "overall_confidence": "...",
          "escalation_recommended": false,
          "gaps": []
        }
        ```
        The `citations` array inside sections expects `source_id`. If I cannot cite a source for a claim because it's not in the packet, how do I handle it?
        The instruction says: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This implies if I make a claim without a source, I must mark it as personal evaluation in the content or reasoning field. However, the JSON schema provided for `analysis_sections` has a `citations` array.
        Actually, looking closely at the instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." -> This is strict. If I cannot find it, I should probably indicate in the `gaps` section or use `ungrounded_reasoning` within the content if necessary to explain limitations, but strictly speaking, I shouldn't make factual claims without sources.
        However, the prompt asks me to answer the question based *only* on the packet. If the packet doesn't have the answer (which it seems not to fully), I must report that gap or use personal evaluation for what is missing.
        Let's look at Source [4] and [7]. They are tax-related (DPR 917). Source [4] mentions "In caso di cessione delle partecipazioni...". Source [7] mentions "Per le plusvalenze derivanti da cessione delle aziende...". These touch on the *tax consequences* but not necessarily the *opponibilità al fisco* of the act itself (which is usually a matter of registration/communication to Revenue Agency) or general solidarity liability.
        Source [2] mentions "iscrizione del trasferimento nel registro" for assignment of credits relative to business. This touches on opposability to third parties, but not specifically tax authorities.

    *   **Strategy:** I must analyze what is in the packet regarding the question. Since the packet lacks specific norms on "opponibilità al fisco" (Tax Code) or general "solidarietà tributaria", I will cite the available Tax DPR sources for what

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1293` | 1.6713 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2769` | 1.1295 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1309` | -1.5010 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art57` | -1.6456 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.8660 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.9100 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art79` | -2.5745 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2729` | -3.3090 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art212` | -3.4738 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2692` | -3.7633 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art14`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1293`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1248. (Inopponibilità della compensazione). Il debitore, se ha accettato puramente e semplicemente la cessione che il creditore ha fatta delle sue ragioni a un terzo, non può opporre al cessionario la compensazione che avrebbe potuto opporre al cedente. La ce

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2769`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2559. (Crediti relativi all'azienda ceduta). La cessione dei crediti relativi all'azienda ceduta, anche in mancanza di notifica al debitore o di sua accettazione, ha effetto, nei confronti dei terzi, dal momento dell'iscrizione del trasferimento nel registro

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1309`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1264. (Efficacia della cessione riguardo al debitore ceduto). La cessione ha effetto nei confronti del debitore ceduto quando questi l'ha accettata o quando gli è stata notificata. Tuttavia, anche prima della notificazione, il debitore che paga al cedente non

**[4]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art57`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 . 917 del 1986 . In caso di cessione delle partecipazioni la preesistente stratificazione delle riserve di utili si trasferisce al cessionario". ------------ AGGIORNAMENTO (192) Il D.Lgs. 29 novembre 2018, n. 142 , ha disposto (con l'a

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2112. (Mantenimento dei diritti dei lavoratori in caso di trasferimento d'azienda). In caso di trasferimento d'azienda, il rapporto di lavoro continua con il cessionario ed il lavoratore conserva tutti i diritti che ne derivano. Il cedente ed il cessionario s

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 , preesistente al trasferimento e che conserva nel trasferimento la propria identità a prescindere dalla tipologia negoziale o dal provvedimento sulla base del quale il trasferimento è attuato ivi compresi l'usufrutto o l'affitto di azienda. Le disposizioni del pr

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art79`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 58 Plusvalenze 1. Per le plusvalenze derivanti da cessione delle aziende, le disposizioni del comma 4 dell'articolo 86 non si applicano quando è richiesta la tassazione separata a norma del comma 2 dell'articolo 17. Il trasferimen

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2729`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2536. (( (Responsabilità del socio uscente e dei suoi eredi). )) ((Il socio che cessa di far parte della società risponde verso questa per il pagamento dei conferimenti non versati, per un anno dal giorno in cui il recesso, la esclusione o la cessione della q

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art212`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 uiti da altri contratti collettivi applicabili all'impresa del cessionario. L'effetto di sostituzione si produce esclusivamente fra contratti collettivi del medesimo livello. Ferma restando la facoltà di esercitare il recesso ai sensi della normativa in mat

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2692`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2506. (Forme di scissione). Con la scissione una società assegna l'intero suo patrimonio a più società, preesistenti o di nuova costituzione, o parte del suo patrimonio, in tal caso anche ad una sola società, e le relative azioni o quote ai suoi soci. È conse

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
