# trib_016 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:46 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 69.8s (ret 0.1s + llm 69.6s) |

## Query

> Quali sono i limiti alla compensazione dei crediti fiscali?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Quali sono i limiti alla compensazione dei crediti fiscali?" (What are the limits to tax credit compensation?)

2.  **Analyze the Research Packet:**
    *   [1] Art. 1824 R.D. 1942 n. 262 (Codice Civile): Credits excluded from current account (not susceptible to set-off, or extraneous to business between entrepreneurs).
    *   [2] D.Lgs. 14/2019 Art. 6: Prededucibility of credits (public administration context).
    *   [3] L. 27 luglio 2000 n. 212 Art. 8: Compensation exclusion for tax debts (specifically mentions "detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti"). This looks crucial for tax credits.
    *   [4] R.D. 1940 n. 1443 Art. 817-bis (Codice Proc. Civile): Arbiters competence on set-off exception.
    *   [5] D.Lgs. 14/2019 Art. 155: Set-off in bankruptcy proceedings (creditors can oppose debts even if not due before opening).
    *   [6] R.D. 1942 n. 262 Art. 1250 (Codice Civile): Set-off prejudice to third parties (usufruct/pledge).
    *   [7] R.D. 1942 n. 262 Art. 1302 (Codice Civile): Solidary debtors/creditors set-off limits.
    *   [8] R.D. 1942 n. 262 Art. 1246 (Codice Civile): Cases where set-off does not occur (e.g., unjust enrichment).
    *   [9] D.Lgs. 14/2019 Art. 224: Priority credits in bankruptcy liquidation.
    *   [10] R.D. 1940 n. 1443 Art. 35 (Codice Proc. Civile): Exception of set-off when contested credit exceeds competence.

3.  **Evaluate the Question against the Packet:**
    *   The question asks about limits to tax credit compensation ("limiti alla compensazione dei crediti fiscali").
    *   Source [3] (L. 212/2000 Art. 8) explicitly mentions "compensazione dei crediti" and "esclusione opera a prescindere dalla tipologia e dall'importo dei crediti". This suggests tax debts might be excluded from set-off or have specific rules regarding compensation.
    *   Source [1] (Art. 1295/1824 CC) discusses general exclusions from current account/set-off (not susceptible to compensation).
    *   Source [6], [7], [8] discuss general civil law limits on set-off (third parties, solidary debtors, specific cases like unjust enrichment).
    *   Source [5], [9] discuss bankruptcy/liquidation contexts.
    *   Source [10] discusses procedural limits regarding contested credits exceeding competence.

4.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Identify the legal nature of tax credits and their interaction with set-off rules based on the packet. The packet contains specific provisions about tax credit compensation exclusions or limitations (Source [3]). It also contains general civil law limits (Sources [1], [6], [8]).
    *   **NORMA APPLICABILE:** Cite Source [3] for the specific exclusion regarding tax debts ("esclusione opera a prescindere dalla tipologia e dall'importo dei crediti"). Cite Source [1] and [8] for general civil law limits (current account exclusions, cases where set-off doesn't occur).
    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza) explicitly. It contains normative texts. I must check if any source implies jurisprudence or if I need to state the absence of specific case law in the packet while relying on norms. Source [4] mentions arbiters competence, but that's procedural. Since the instruction says "Reason ONLY on facts in the Research Packet", and there are no actual court decisions (sentenze) listed with source_ids like "Cassazione n. ...", I cannot invent jurisprudence. I must state what is available or note the gap if specific case law isn't present. However, Source [3] text implies a legislative rule ("detta esclusione"). I will focus on the normative limits provided in the packet.
    *   **VALUTAZIONE:** Assess confidence based on the sources. Source [3] seems to directly address tax credit compensation exclusion. Sources [1], [6], [8] provide general civil law context. Confidence might be MEDIUM because specific "tax credit" jurisprudence isn't in the packet, only statutory text.
    *   **GAP ANALYSIS:** What is missing? Specific case law on tax set-off limits beyond Art. 8 L. 212/2000. Details on specific tax codes (TUIR) not present in this packet.

5.  **Refining Citations & Claims:**
    *   Claim: Tax credits have exclusion rules regarding compensation. Source [3].
    *   Claim: General set-off limits apply to third parties or unjust enrichment cases. Sources [6], [8].
    *   Claim: Current account exclusions exist for non-compensable credits. Source [1].

    *Wait, I need to be careful.* The prompt says "Reason ONLY on facts in the Research Packet".
    Source [3] text: "...della compensazione dei crediti... detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti..." This looks like it refers to tax debts (implied by context of L. 212/2000 which is often about VAT/Tax).
    Source [1] Art. 1824 CC: Credits excluded from current account are not susceptible to compensation.

    *Constraint Check:* "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
    I cannot say "Tax credits are generally exempt" without citing the packet. The packet has Source [3] which mentions "compensazione dei crediti... esclusione".
    I must not invent article numbers if not in the text (e.g., Art. 1295 is mentioned in source title but text says Art. 1250). Wait, look closely at Source [6]: Title says Art. 1250, Text says "Art. 1250". Source [1] Title says Art. 1824, Text says "Art. 1824".
    I must use the `source_id` provided in the list (e.g., `urn:nir:stato:...`).

6.  **Constructing JSON:**
    *   Ensure valid JSON.
    *   Ensure steps match exactly: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   Ensure citations array in each step (or empty if none).
    *   Ensure `overall_confidence` is HIGH|MEDIUM|LOW.
    *   Ensure `escalation_recommended` boolean.
    *   Ensure `gaps` array.

7.

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Question:** "Quali sono i limiti alla compensazione dei crediti fiscali?" (What are the limits to tax credit compensation?)

2.  **Analyze the Research Packet:**
    *   [1] Art. 1824 R.D. 1942 n. 262 (Codice Civile): Credits excluded from current account (not susceptible to set-off, or extraneous to business between entrepreneurs).
    *   [2] D.Lgs. 14/2019 Art. 6: Prededucibility of credits (public administration context).
    *   [3] L. 27 luglio 2000 n. 212 Art. 8: Compensation exclusion for tax debts (specifically mentions "detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti"). This looks crucial for tax credits.
    *   [4] R.D. 1940 n. 1443 Art. 817-bis (Codice Proc. Civile): Arbiters competence on set-off exception.
    *   [5] D.Lgs. 14/2019 Art. 155: Set-off in bankruptcy proceedings (creditors can oppose debts even if not due before opening).
    *   [6] R.D. 1942 n. 262 Art. 1250 (Codice Civile): Set-off prejudice to third parties (usufruct/pledge).
    *   [7] R.D. 1942 n. 262 Art. 1302 (Codice Civile): Solidary debtors/creditors set-off limits.
    *   [8] R.D. 1942 n. 262 Art. 1246 (Codice Civile): Cases where set-off does not occur (e.g., unjust enrichment).
    *   [9] D.Lgs. 14/2019 Art. 224: Priority credits in bankruptcy liquidation.
    *   [10] R.D. 1940 n. 1443 Art. 35 (Codice Proc. Civile): Exception of set-off when contested credit exceeds competence.

3.  **Evaluate the Question against the Packet:**
    *   The question asks about limits to tax credit compensation ("limiti alla compensazione dei crediti fiscali").
    *   Source [3] (L. 212/2000 Art. 8) explicitly mentions "compensazione dei crediti" and "esclusione opera a prescindere dalla tipologia e dall'importo dei crediti". This suggests tax debts might be excluded from set-off or have specific rules regarding compensation.
    *   Source [1] (Art. 1295/1824 CC) discusses general exclusions from current account/set-off (not susceptible to compensation).
    *   Source [6], [7], [8] discuss general civil law limits on set-off (third parties, solidary debtors, specific cases like unjust enrichment).
    *   Source [5], [9] discuss bankruptcy/liquidation contexts.
    *   Source [10] discusses procedural limits regarding contested credits exceeding competence.

4.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Identify the legal nature of tax credits and their interaction with set-off rules based on the packet. The packet contains specific provisions about tax credit compensation exclusions or limitations (Source [3]). It also contains general civil law limits (Sources [1], [6], [8]).
    *   **NORMA APPLICABILE:** Cite Source [3] for the specific exclusion regarding tax debts ("esclusione opera a prescindere dalla tipologia e dall'importo dei crediti"). Cite Source [1] and [8] for general civil law limits (current account exclusions, cases where set-off doesn't occur).
    *   **GIURISPRUDENZA:** The packet does not contain case law (Giurisprudenza) explicitly. It contains normative texts. I must check if any source implies jurisprudence or if I need to state the absence of specific case law in the packet while relying on norms. Source [4] mentions arbiters competence, but that's procedural. Since the instruction says "Reason ONLY on facts in the Research Packet", and there are no actual court decisions (sentenze) listed with source_ids like "Cassazione n. ...", I cannot invent jurisprudence. I must state what is available or note the gap if specific case law isn't present. However, Source [3] text implies a legislative rule ("detta esclusione"). I will focus on the normative limits provided in the packet.
    *   **VALUTAZIONE:** Assess confidence based on the sources. Source [3] seems to directly address tax credit compensation exclusion. Sources [1], [6], [8] provide general civil law context. Confidence might be MEDIUM because specific "tax credit" jurisprudence isn't in the packet, only statutory text.
    *   **GAP ANALYSIS:** What is missing? Specific case law on tax set-off limits beyond Art. 8 L. 212/2000. Details on specific tax codes (TUIR) not present in this packet.

5.  **Refining Citations & Claims:**
    *   Claim: Tax credits have exclusion rules regarding compensation. Source [3].
    *   Claim: General set-off limits apply to third parties or unjust enrichment cases. Sources [6], [8].
    *   Claim: Current account exclusions exist for non-compensable credits. Source [1].

    *Wait, I need to be careful.* The prompt says "Reason ONLY on facts in the Research Packet".
    Source [3] text: "...della compensazione dei crediti... detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti..." This looks like it refers to tax debts (implied by context of L. 212/2000 which is often about VAT/Tax).
    Source [1] Art. 1824 CC: Credits excluded from current account are not susceptible to compensation.

    *Constraint Check:* "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
    I cannot say "Tax credits are generally exempt" without citing the packet. The packet has Source [3] which mentions "compensazione dei crediti... esclusione".
    I must not invent article numbers if not in the text (e.g., Art. 1295 is mentioned in source title but text says Art. 1250). Wait, look closely at Source [6]: Title says Art. 1250, Text says "Art. 1250". Source [1] Title says Art. 1824, Text says "Art. 1824".
    I must use the `source_id` provided in the list (e.g., `urn:nir:stato:...`).

6.  **Constructing JSON:**
    *   Ensure valid JSON.
    *   Ensure steps match exactly: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   Ensure citations array in each step (or empty if none).
    *   Ensure `overall_confidence` is HIGH|MEDIUM|LOW.
    *   Ensure `escalation_recommended` boolean.
    *   Ensure `gaps` array.

7.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1888` | 3.9508 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6` | 3.1663 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art8` | 2.6132 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art1011` | 2.3236 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155` | 2.0325 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1295` | 0.1879 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1347` | -0.1364 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1291` | -1.5055 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art224` | -2.0446 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art41` | -3.1013 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:1997-07-09;241~art17`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1888`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1824. (Crediti esclusi dal conto corrente). Sono esclusi dal conto corrente i crediti che non sono suscettibili di compensazione. Qualora il contratto intervenga tra imprenditori, s'intendono esclusi dal conto i crediti estranei alle rispettive imprese.

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art6`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 6 (Prededucibilità dei crediti) 1. Oltre ai crediti così espressamente qualificati dalla legge, sono prededucibili: a) i crediti relativi a spese e compensi per le prestazioni rese ((nell'esercizio delle funzioni rientranti nella competenza dell'organi

**[3]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

**[4]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art1011`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 817-bis. (( (Compensazione).)) ((Gli arbitri sono competenti a conoscere dell'eccezione di compensazione, nei limiti del valore della domanda, anche se il controcredito non è compreso nell'ambito della convenzione di arbitrato.))

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art155`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 155 Compensazione 1. I creditori possono opporre in compensazione dei loro debiti verso il debitore il cui patrimonio è sottoposto alla liquidazione giudiziale i propri crediti verso quest'ultimo, ancorchè non scaduti prima dell'apertura della procedur

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1295`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1250. (Compensazione rispetto ai terzi). La compensazione non si verifica in pregiudizio dei terzi che hanno acquistato diritti di usufrutto o di pegno su uno dei crediti.

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1347`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1302. (Compensazione). Ciascuno dei debitori in solido può opporre in compensazione il credito di un condebitore solo fino alla concorrenza della parte di quest'ultimo. A uno dei creditori in solido il debitore può opporre in compensazione ciò che gli è dovut

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1291`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1246. (Casi in cui la compensazione non si verifica). La compensazione si verifica qualunque sia il titolo dell'uno o dell'altro debito, eccettuati i casi: 1) di credito per la restituzione di cose di cui il proprietario sia stato ingiustamente spogliato; 2)

**[9]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art224`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 224 Crediti assistiti da prelazione 1. I crediti assistiti da privilegio generale hanno diritto di prelazione per il capitale, le spese e gli interessi, nei limiti di cui agli articoli 153 e 154, sul prezzo ricavato dalla liquidazione del patrimonio mo

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art41`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 35. (Eccezione di compensazione). Quando è opposto in compensazione un credito che è contestato ed eccede la competenza per valore del giudice adito, questi, se la domanda è fondata su titolo non controverso o facilmente accertabile, può decidere su di ess

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
