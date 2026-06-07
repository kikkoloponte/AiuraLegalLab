# cross_022 — amministrativo+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 15:36 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.6s (ret 0.3s + llm 65.2s) |

## Query

> Come interagiscono il danno da occupazione illegittima e l'acquisizione sanante ex art. 42-bis TU espropri?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda richiede l'analisi dell'interazione tra danno da occupazione illegittima e acquisizione sanante ex art. 42-bis TU espropri. Il Research Packet contiene fonti sul codice civile (RD 262/1942) che trattano occupazione, espropriazione e indennità (source_id: [2], [3], [5], [8], [10]), ma NON contiene riferimenti all'art. 42-bis TU espropri né alla disciplina specifica dell'acquisizione sanante in materia di espropri.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art867",
          "claim": "Il RD 262/1942 disciplina l'espropriazione e l'occupazione temporanea di terreni vincolati per rimboschimento",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1020",
          "claim": "L'usufrutto si trasferisce sull'indennità relativa quando la cosa è requisita o espropriata per pubblico interesse",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme presenti nel Packet rilevanti sono: RD 262/1942 Art. 867 (espropriazione per rimboschimento), Art. 923 (cose mobili acquistate con occupazione - cose abbandonate, caccia/pesca), Art. 1053 (indennità per passaggio), Art. 1020 (requisizione/espropriazione trasferisce usufrutto sull'indennità). Tuttavia, l'art. 42-bis TU espropri NON è presente nel Packet.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art867",
          "claim": "Art. 867 RD 262/1942 disciplina sistemazione e rimboschimento dei terreni vincolati con espropriazione o occupazione temporanea",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1058",
          "claim": "Art. 1058 RD 262/1942 prevede indennità proporzionata al danno cagionato dal passaggio in casi di espropriazione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Research Packet non contiene alcuna fonte giurisprudenziale o sentenza che analizzi l'interazione tra danno da occupazione illegittima e acquisizione sanante. Le fonti disponibili sono esclusivamente normative (codice civile, codice penale, decreti legislativi).",
      "citations": []
    },
    {
      "step": "VALUTAZIONE",
      "content": "VALUTAZIONE PERSONALE: L'analisi è LIMITATA perché l'art. 42-bis TU espropri non è presente nel Research Packet. Non posso citare norme su acquisizione sanante, né stabilire come interagisca con il danno da occupazione illegittima senza fonti normative specifiche sul TU espropri. Le fonti disponibili (RD 262/1942) trattano occupazione e indennità ma non l'acquisizione sanante.",
      "citations": []
    },
    {
      "step": "GAP ANALYSIS",
      "content": "MANCANZA CRITICA: L'art. 42-bis TU espropri NON è presente nel Research Packet. Senza questa fonte, non posso qualificare l'acquisizione sanante né stabilire il regime di inter

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda richiede l'analisi dell'interazione tra danno da occupazione illegittima e acquisizione sanante ex art. 42-bis TU espropri. Il Research Packet contiene fonti sul codice civile (RD 262/1942) che trattano occupazione, espropriazione e indennità (source_id: [2], [3], [5], [8], [10]), ma NON contiene riferimenti all'art. 42-bis TU espropri né alla disciplina specifica dell'acquisizione sanante in materia di espropri.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art867",
          "claim": "Il RD 262/1942 disciplina l'espropriazione e l'occupazione temporanea di terreni vincolati per rimboschimento",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1020",
          "claim": "L'usufrutto si trasferisce sull'indennità relativa quando la cosa è requisita o espropriata per pubblico interesse",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme presenti nel Packet rilevanti sono: RD 262/1942 Art. 867 (espropriazione per rimboschimento), Art. 923 (cose mobili acquistate con occupazione - cose abbandonate, caccia/pesca), Art. 1053 (indennità per passaggio), Art. 1020 (requisizione/espropriazione trasferisce usufrutto sull'indennità). Tuttavia, l'art. 42-bis TU espropri NON è presente nel Packet.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art867",
          "claim": "Art. 867 RD 262/1942 disciplina sistemazione e rimboschimento dei terreni vincolati con espropriazione o occupazione temporanea",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1058",
          "claim": "Art. 1058 RD 262/1942 prevede indennità proporzionata al danno cagionato dal passaggio in casi di espropriazione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Research Packet non contiene alcuna fonte giurisprudenziale o sentenza che analizzi l'interazione tra danno da occupazione illegittima e acquisizione sanante. Le fonti disponibili sono esclusivamente normative (codice civile, codice penale, decreti legislativi).",
      "citations": []
    },
    {
      "step": "VALUTAZIONE",
      "content": "VALUTAZIONE PERSONALE: L'analisi è LIMITATA perché l'art. 42-bis TU espropri non è presente nel Research Packet. Non posso citare norme su acquisizione sanante, né stabilire come interagisca con il danno da occupazione illegittima senza fonti normative specifiche sul TU espropri. Le fonti disponibili (RD 262/1942) trattano occupazione e indennità ma non l'acquisizione sanante.",
      "citations": []
    },
    {
      "step": "GAP ANALYSIS",
      "content": "MANCANZA CRITICA: L'art. 42-bis TU espropri NON è presente nel Research Packet. Senza questa fonte, non posso qualificare l'acquisizione sanante né stabilire il regime di inter

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2015-06-15;81~art29` | -0.1088 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art963` | -3.3024 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1020` | -3.8464 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art864` | -4.2611 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1198` | -4.3107 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art190` | -4.7491 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art211` | -4.9646 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1091` | -4.9926 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2005-09-06;206~art132` | -5.0770 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1058` | -5.6135 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-08;327~art42bis`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2015-06-15;81~art29`

> DECRETO LEGISLATIVO 15 giugno 2015, n. 81 a la conversione in contratti a tempo indeterminato. Il lavoratore interessato ha diritto al risarcimento del danno derivante dalla prestazione di lavoro in violazione di disposizioni imperative. Le fondazioni hanno l'obbligo di recuperare le somme pagate a

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art963`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 867. (Sistemazione e rimboschimento dei terreni vincolati). Al fine del rimboschimento e del rinsaldamento i terreni vincolati possono essere assoggettati a espropriazione, a occupazione temporanea o a sospensione dell'esercizio del pascolo, nei modi e con le

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1020`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 923. (Cose suscettibili di occupazione). Le cose mobili che non sono proprietà di alcuno si acquistano con l'occupazione. Tali sono le cose abbandonate e gli animali che formano oggetto di caccia o di pesca.

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art864`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 634-bis. (( (Occupazione arbitraria di immobile destinato a domicilio altrui).)) ((Chiunque, mediante violenza o minaccia, occupa o detiene senza titolo un immobile destinato a domicilio altrui o sue pertinenze, ovvero impedisce il rientro nel medesimo imm

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1198`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1154. (Conoscenza dell'illegittima provenienza della cosa). A colui che ha acquistato conoscendo l'illegittima provenienza della cosa non giova l'erronea credenza che il suo autore o un precedente possessore ne sia divenuto proprietario.

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art190`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 190 Trattamento NASpI 1. La cessazione del rapporto di lavoro ai sensi dell'articolo 189 costituisce perdita involontaria dell'occupazione ai fini di cui all' articolo 3 del decreto legislativo 4 marzo 2015, n. 22 e al lavoratore è riconosciuto il trat

**[7]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art211`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 187. (Indivisibilità e solidarietà nelle obbligazioni ex delicto) L'obbligo alle restituzioni e alla pubblicazione della sentenza penale di condanna è indivisibile. I condannati per uno stesso reato sono obbligati in solido al risarcimento del danno patrim

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1091`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1053. (Indennità). Nei casi previsti dai due articoli precedenti è dovuta un'indennità proporzionata al danno cagionato dal passaggio. Qualora, per attuare il passaggio, sia necessario occupare con opere stabili o lasciare incolta una zona del fondo servente,

**[9]** `urn:nir:stato:decreto.legislativo:2005-09-06;206~art132`

> DECRETO LEGISLATIVO 6 settembre 2005, n. 206 Art. 132 (( (Diritti dei terzi). )) ((1. I rimedi di cui all'articolo 135-bis si estendono ai casi di impedimento o limitazione d'uso del bene venduto in conformità a quanto previsto dagli articoli 129 e 130, conseguenti ad una restrizione derivante dalla

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1058`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1020. (Requisizione o espropriazione). Se la cosa è requisita o espropriata per pubblico interesse, l'usufrutto si trasferisce sull'indennità relativa.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
