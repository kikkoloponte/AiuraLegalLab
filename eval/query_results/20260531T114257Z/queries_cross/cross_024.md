# cross_024 — civile+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 11:56 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 20.7s (ret 0.2s + llm 19.5s) |

## Query

> Qual è la giurisdizione sulle controversie relative a concessioni di beni pubblici?

## Risposta

**QUALIFICAZIONE**
Le controversie relative a concessioni di beni pubblici sono devolute alla giurisdizione amministrativa.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 138.

**GIURISPRUDENZA**
Non ci sono specifiche giurisprudenze menzionate nel Packet che si riferiscono esplicitamente alle controversie relative a concessioni di beni pubblici.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica, quindi la solidità della valutazione è ALTA.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le controversie relative a concessioni di beni pubblici sono devolute alla giurisdizione amministrativa.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2010-07-02;104~art138', 'claim': 'Le controversie relative a concessioni di beni pubblici sono devolute alla giurisdizione esclusiva del giudice amministrativo.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 138.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2010-07-02;104~art138', 'claim': 'Le controversie relative a concessioni di beni pubblici sono devolute alla giurisdizione esclusiva del giudice amministrativo.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono specifiche giurisprudenze menzionate nel Packet che si riferiscono esplicitamente alle controversie relative a concessioni di beni pubblici.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica, quindi la solidità della valutazione è ALTA.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138` | 4.8519 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art477` | 4.6506 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art131` | 3.5561 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art140` | 3.3414 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art10` | 2.1606 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art930` | 1.9157 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art919` | 1.4094 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138` | 1.3548 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art139` | 1.3261 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art10` | 0.3401 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 lici servizi relative a concessioni di pubblici servizi, escluse quelle concernenti indennità, canoni ed altri corrispettivi, ovvero relative a provvedimenti adottati dalla pubblica amministrazione o dal gestore di un pubblico servizio in un procedimento amm

**[2]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art477`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 417-bis (Difesa delle pubbliche amministrazioni). Nelle controversie relative ai rapporti di lavoro dei dipendenti delle pubbliche amministrazioni di cui al quinto comma dell'articolo 413, limitatamente al giudizio di primo grado le amministrazioni stesse

**[3]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art131`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 126 Ambito della giurisdizione sul contenzioso elettorale 1. Il giudice amministrativo ha giurisdizione in materia di operazioni elettorali relative al rinnovo degli organi elettivi dei comuni, delle province, delle regioni e all'elezione dei membri del

**[4]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art140`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 i al rilascio di autorizzazioni in materia di giochi pubblici con vincita in denaro. (12) q-quinquies) le controversie relative alle decisioni adottate ai sensi dell' articolo 24, paragrafo 2, lettera b), del regolamento (CE) n. 1987/2006 del Parlamento euro

**[5]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art10`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 7 Giurisdizione amministrativa 1. Sono devolute alla giurisdizione amministrativa le controversie, nelle quali si faccia questione di interessi legittimi e, nelle particolari materie indicate dalla legge, di diritti soggettivi, concernenti l'esercizio o

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art930`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 834. (Espropriazione per pubblico interesse). Nessuno può essere privato in tutto o in parte dei beni di sua proprietà, se non per causa di pubblico interesse, legalmente dichiarata, e contro il pagamento di una giusta indennità. Le norme relative all'espropr

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art919`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 823. (Condizione giuridica del demanio pubblico). I beni che fanno parte del demanio pubblico sono inalienabili e non possono formare oggetto di diritti a favore di terzi, se non nei modi e nei limiti stabiliti dalle leggi che li riguardano. Spetta all'autori

**[8]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art138`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 133 Materie di giurisdizione esclusiva 1. Sono devolute alla giurisdizione esclusiva del giudice amministrativo, salvo ulteriori previsioni di legge: a) le controversie in materia di: 1) risarcimento del danno ingiusto cagionato in conseguenza dell'inos

**[9]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art139`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 134 Materie di giurisdizione estesa al merito 1. Il giudice amministrativo esercita giurisdizione con cognizione estesa al merito nelle controversie aventi ad oggetto: a) l'attuazione delle pronunce giurisdizionali esecutive o del giudicato nell'ambito

**[10]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art10`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 'esercizio di tale giurisdizione il giudice amministrativo può sostituirsi all'amministrazione. 7. Il principio di effettività è realizzato attraverso la concentrazione davanti al giudice amministrativo di ogni forma di tutela degli interessi legittimi e, ne

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
