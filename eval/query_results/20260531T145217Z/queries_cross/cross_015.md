# cross_015 — amministrativo+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 15:28 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.6s (ret 0.2s + llm 65.2s) |

## Query

> Qual è la disciplina dell'espropriazione per pubblica utilità e l'indennità dovuta?

## Risposta

**ANALISI**
Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (Regio Decreto 262/1942, Legge Costituzionale 2/1993, Regio Decreto 1443/1940, Regio Decreto 1398/1930).
    *   **User Question:** "Qual è la disciplina dell'espropriazione per pubblica utilità e l'indennità dovuta?" (What is the discipline of expropriation for public utility and the due indemnity?)

2.  **Analyze the Research Packet Sources:**
    *   [1] RD 262/1942 Art. 1020: Usufruct transfers to indemnity if requisitioned/expropriated.
    *   [2] RD 262/1942 Art. 1638: Tenant has right to part of indemnity for fruits not perceived in case of expropriation/temporary occupation.
    *   [3] RD 262/1942 Art. 834 (labeled as Art. 834 in text, title says Art. 834): Expropriation requires public interest, legal declaration, and just indemnity.
    *   [4] LC 2/1993 Art. 5: Lists expropriation for public utility not concerning State works as a regional competence (item 11).
    *   [5] RD 1443/1940 Art. 795 (labeled as Art. 795 in text, title says Art. 795): Judge orders expropriation procedure if request is made and conditions met.
    *   [6] RD 1443/1940 Art. 602: Expropriation of property burdened by pledge/mortgage or revoked alienation applies specific provisions.
    *   [7] RD 262/1942 Art. 838 (labeled as Art. 838 in text, title says Art. 838): Expropriation of goods affecting national production/public interest.
    *   [8] RD 1398/1930 Art. 420: Attentat to public utility plants (criminal).
    *   [9] RD 262/1942 Art. 865 (labeled as Art. 865 in text, title says Art. 865): Expropriation for non-compliance with obligations affecting land reclamation plan.
    *   [10] RD 262/1942 Art. 2245 (labeled as Art. 2245 in text, title says Art. 2245): Indemnity of seniority for labor contract cessation.

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Define expropriation for public utility based on the packet.
        *   Fact: Expropriation requires public interest, legal declaration, and just indemnity. Source [3].
        *   Fact: It can apply to goods affecting national production/public interest. Source [7].
        *   Fact: Usufruct transfers to indemnity. Source [1].

    *   **NORMA APPLICABILE:** Specific articles regarding the process and indemnity.
        *   Art. 834 (RD 262/1942) sets the core requirement (public interest, legal declaration, just indemnity). Source [3].
        *   Art. 795 (RD 1443/1940) mentions judge's role in ordering procedure if conditions met. Source [5].
        *   Art. 1638 (RD 262/1942) regarding tenant rights to indemnity part for fruits. Source [2].

    *   **GIURISPRUDENZA:** The packet does not contain case law/jurisprudence sources. It only contains statutes/regios decrees.
        *   I must state that the packet lacks jurisprudential sources.
        *   Constraint: If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". However, the instruction says "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." and "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
        *   Since I cannot invent jurisprudence, I will note the absence in the content or use the valuation step for this limitation. But strictly speaking, for the "Giurisprudenza" section, if there is no source in the packet, I should probably indicate that based on the available text (which has none).
        *   Wait, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." and "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
        *   If there is no jurisprudence in the packet, I cannot cite one. I should state that the provided material focuses on statutory norms rather than case law.
        *   However, looking at the JSON schema example: `citations` array inside each step.
        *   For "GIURISPRUDENZA", if there are no sources in the packet about jurisprudence, I might have to leave citations empty or state that none is available in the packet. But I must follow the citation contract. If I make a claim like "There is no case law provided", do I need a source? No, because it's an observation of the packet content itself.
        *   Actually, looking at the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to factual claims about law if I don't have a source. But stating "The packet does not contain case law" is meta-analysis of the packet, which might be allowed without citation or with `ungrounded_reasoning`.
        *   Better approach: Since the prompt asks me to analyze based on the packet, and the packet has no jurisprudence sources, I will note that the analysis relies on statutory norms provided in the packet. I will not invent case law.
        *   Wait, strict instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I say "There is no jurisprudence", is that a factual claim about the world or the packet? It's about the packet content. But to be safe on the citation contract regarding legal facts, I should avoid making claims about external law not in the packet.
        *   Let's check the JSON schema example provided in the system prompt: `citations` array is inside each step object.
        *   For "GIURISPRUDENZA", if there are no sources, I will set citations to empty and content explaining that the packet provides statutory norms instead of case law. But wait, if I claim "The packet lacks jurisprudence", do I need a source? No, because it's an observation of the input data.
        *   However, to be strictly compliant with "Reason ONLY on facts in Research Packet", I should focus on what IS there.

## Analisi (Chain of Thought)

### ANALISI

Thinking Process:

1.  **Analyze the Request:**
    *   **Role:** Legal Analyst [S3].
    *   **Constraint:** Reason ONLY on facts in the Research Packet. No direct KB access.
    *   **Citation Contract:** Every factual claim MUST have a `source_id` from the Packet. If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". Never invent numbers, articles, years, etc.
    *   **Schema CoT:** Steps must be EXACTLY: QUALIFICAZIONE, NORMA APPLICABILE, GIURISPRUDENZA, VALUTAZIONE, GAP ANALYSIS.
    *   **Output Format:** JSON only. No text before or after.
    *   **Input Packet:** Contains 10 sources (Regio Decreto 262/1942, Legge Costituzionale 2/1993, Regio Decreto 1443/1940, Regio Decreto 1398/1930).
    *   **User Question:** "Qual è la disciplina dell'espropriazione per pubblica utilità e l'indennità dovuta?" (What is the discipline of expropriation for public utility and the due indemnity?)

2.  **Analyze the Research Packet Sources:**
    *   [1] RD 262/1942 Art. 1020: Usufruct transfers to indemnity if requisitioned/expropriated.
    *   [2] RD 262/1942 Art. 1638: Tenant has right to part of indemnity for fruits not perceived in case of expropriation/temporary occupation.
    *   [3] RD 262/1942 Art. 834 (labeled as Art. 834 in text, title says Art. 834): Expropriation requires public interest, legal declaration, and just indemnity.
    *   [4] LC 2/1993 Art. 5: Lists expropriation for public utility not concerning State works as a regional competence (item 11).
    *   [5] RD 1443/1940 Art. 795 (labeled as Art. 795 in text, title says Art. 795): Judge orders expropriation procedure if request is made and conditions met.
    *   [6] RD 1443/1940 Art. 602: Expropriation of property burdened by pledge/mortgage or revoked alienation applies specific provisions.
    *   [7] RD 262/1942 Art. 838 (labeled as Art. 838 in text, title says Art. 838): Expropriation of goods affecting national production/public interest.
    *   [8] RD 1398/1930 Art. 420: Attentat to public utility plants (criminal).
    *   [9] RD 262/1942 Art. 865 (labeled as Art. 865 in text, title says Art. 865): Expropriation for non-compliance with obligations affecting land reclamation plan.
    *   [10] RD 262/1942 Art. 2245 (labeled as Art. 2245 in text, title says Art. 2245): Indemnity of seniority for labor contract cessation.

3.  **Drafting the Analysis (CoT Steps):**

    *   **QUALIFICAZIONE:** Define expropriation for public utility based on the packet.
        *   Fact: Expropriation requires public interest, legal declaration, and just indemnity. Source [3].
        *   Fact: It can apply to goods affecting national production/public interest. Source [7].
        *   Fact: Usufruct transfers to indemnity. Source [1].

    *   **NORMA APPLICABILE:** Specific articles regarding the process and indemnity.
        *   Art. 834 (RD 262/1942) sets the core requirement (public interest, legal declaration, just indemnity). Source [3].
        *   Art. 795 (RD 1443/1940) mentions judge's role in ordering procedure if conditions met. Source [5].
        *   Art. 1638 (RD 262/1942) regarding tenant rights to indemnity part for fruits. Source [2].

    *   **GIURISPRUDENZA:** The packet does not contain case law/jurisprudence sources. It only contains statutes/regios decrees.
        *   I must state that the packet lacks jurisprudential sources.
        *   Constraint: If no source, use `ungrounded_reasoning` with prefix "VALUTAZIONE PERSONALE:". However, the instruction says "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." and "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione."
        *   Since I cannot invent jurisprudence, I will note the absence in the content or use the valuation step for this limitation. But strictly speaking, for the "Giurisprudenza" section, if there is no source in the packet, I should probably indicate that based on the available text (which has none).
        *   Wait, the instruction says: "Ragioni SOLO sui fatti nel Research Packet." and "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet."
        *   If there is no jurisprudence in the packet, I cannot cite one. I should state that the provided material focuses on statutory norms rather than case law.
        *   However, looking at the JSON schema example: `citations` array inside each step.
        *   For "GIURISPRUDENZA", if there are no sources in the packet about jurisprudence, I might have to leave citations empty or state that none is available in the packet. But I must follow the citation contract. If I make a claim like "There is no case law provided", do I need a source? No, because it's an observation of the packet content itself.
        *   Actually, looking at the instruction: "Se non hai la fonte → campo `ungrounded_reasoning` con prefisso 'VALUTAZIONE PERSONALE:' — mai come citazione." This applies to factual claims about law if I don't have a source. But stating "The packet does not contain case law" is meta-analysis of the packet, which might be allowed without citation or with `ungrounded_reasoning`.
        *   Better approach: Since the prompt asks me to analyze based on the packet, and the packet has no jurisprudence sources, I will note that the analysis relies on statutory norms provided in the packet. I will not invent case law.
        *   Wait, strict instruction: "Ogni affermazione fattuale DEVE avere un source_id presente nel Packet." If I say "There is no jurisprudence", is that a factual claim about the world or the packet? It's about the packet content. But to be safe on the citation contract regarding legal facts, I should avoid making claims about external law not in the packet.
        *   Let's check the JSON schema example provided in the system prompt: `citations` array is inside each step object.
        *   For "GIURISPRUDENZA", if there are no sources, I will set citations to empty and content explaining that the packet provides statutory norms instead of case law. But wait, if I claim "The packet lacks jurisprudence", do I need a source? No, because it's an observation of the input data.
        *   However, to be strictly compliant with "Reason ONLY on facts in Research Packet", I should focus on what IS there.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1058` | 4.1465 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1696` | 3.3418 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art930` | 2.8008 | hybrid_rrf |  |
| 4 | `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5` | 2.6091 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art975` | 1.2605 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art754` | 0.7490 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art934` | -0.3306 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art511` | -0.8607 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art961` | -1.7358 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2286` | -2.7511 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art32`
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art37`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1058`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1020. (Requisizione o espropriazione). Se la cosa è requisita o espropriata per pubblico interesse, l'usufrutto si trasferisce sull'indennità relativa.

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1696`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1638. (Espropriazione per pubblico interesse). In caso di espropriazione per pubblico interesse o di occupazione temporanea del fondo locato, l'affittuario ha diritto di ottenere dal locatore la parte d'indennità a questo corrisposta per i frutti non percepit

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art930`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 834. (Espropriazione per pubblico interesse). Nessuno può essere privato in tutto o in parte dei beni di sua proprietà, se non per causa di pubblico interesse, legalmente dichiarata, e contro il pagamento di una giusta indennità. Le norme relative all'espropr

**[4]** `urn:nir:stato:legge.costituzionale:1993-09-23;2~art5`

> LEGGE COSTITUZIONALE 23 settembre 1993, n. 2  di programmi di sviluppo economico; 10) miniere, cave e torbiere; 11) espropriazione per pubblica utilità non riguardanti opere a carico dello Stato; 12) linee marittime di cabotaggio tra gli scali della regione; 13) polizia locale, urbana e rurale; 14)

**[5]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art975`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 795. (Espropriazione). Se è fatta istanza di espropriazione, il giudice, verificate le condizioni stabilite dalla legge per l'ammissibilità di essa, dispone con decreto che si proceda a norma degli articoli 567 e seguenti. La vendita non può essere fatta c

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art754`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 602. (Modo dell'espropriazione). Quando oggetto dell'espropriazione è un bene gravato da pegno o da ipoteca per un debito altrui, oppure un bene la cui alienazione da parte del debitore è stata revocata per frode, si applicano le disposizioni contenute nei

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art934`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 838. (Espropriazione di beni che interessano la produzione nazionale o di prevalente interesse pubblico). Salve le disposizioni delle leggi penali e di polizia, nonché le norme dell'ordinamento corporativo e le disposizioni particolari concernenti beni determ

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art511`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 420. (Attentato a impianti di pubblica utilità). Chiunque commette un fatto diretto a danneggiare o distruggere impianti di pubblica utilità, è punito, salvo che il fatto costituisca più grave reato, con la reclusione da uno a quattro anni. ((COMMA ABROGAT

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art961`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 865. (Espropriazione per inosservanza degli obblighi). Quando l'inosservanza degli obblighi imposti ai proprietari risulta tale da compromettere l'attuazione del piano di bonifica, può farsi luogo all'espropriazione parziale o totale del fondo appartenente al

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2286`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2245. (Indennità di anzianità). In caso di cessazione del contratto è dovuta al prestatore di lavoro un'indennità proporzionale agli anni di servizio, salvo il caso di licenziamento per colpa di lui o di dimissioni volontarie. L'ammontare dell'indennità è det

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
