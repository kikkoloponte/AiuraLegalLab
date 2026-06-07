# trib_007 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 16:15 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 68.7s (ret 0.2s + llm 68.3s) |

## Query

> Come si applica il principio del contraddittorio endoprocedimentale?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "Il principio del contraddittorio endoprocedimentale si riferisce alla garanzia che le parti possano intervenire e presentare osservazioni durante lo svolgimento del procedimento, non solo all'inizio. Questo principio opera in ambito civile (R.D. 1443/1940) e amministrativo (D.Lgs. 104/2010).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art111",
          "claim": "Il giudice non può statuire sopra alcuna domanda se la parte contro la quale è proposta non è stata regolarmente citata e non è comparsa",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art52",
          "claim": "L'integrazione del contraddittorio nei confronti degli altri controinteressati quando il ricorso sia stato proposto solo contro taluno di essi",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art30",
          "claim": "Il contraddittorio è integralmente costituito quando l'atto introduttivo è notificato all'amministrazione resistente e, ove esistenti, ai controinteressati",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme principali sono: Art. 101 R.D. 1443/1940 (principio generale del contraddittorio), Art. 49 D.Lgs. 104/2010 (integrazione del contraddittorio in procedimenti amministrativi), Art. 27 D.Lgs. 104/2010 (definizione di contraddittorio integrale), Art. 419 R.D. 1443/1940 (intervento volontario per integrazione necessaria).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art111",
          "claim": "Art. 101 R.D. 1443/1940 - Principio del contraddittorio generale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art52",
          "claim": "Art. 49 D.Lgs. 104/2010 - Integrazione del contraddittorio nei confronti degli altri controinteressati",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art30",
          "claim": "Art. 27 D.Lgs. 104/2010 - Contraddittorio integralmente costituito con notifica atto introduttivo",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art479",
          "claim": "Art. 419 R.D. 1443/1940 - Intervento del terzo salvo che sia effettuato per l'integrazione necessaria del contraddittorio",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "Il principio del contraddittorio endoprocedimentale si riferisce alla garanzia che le parti possano intervenire e presentare osservazioni durante lo svolgimento del procedimento, non solo all'inizio. Questo principio opera in ambito civile (R.D. 1443/1940) e amministrativo (D.Lgs. 104/2010).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art111",
          "claim": "Il giudice non può statuire sopra alcuna domanda se la parte contro la quale è proposta non è stata regolarmente citata e non è comparsa",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art52",
          "claim": "L'integrazione del contraddittorio nei confronti degli altri controinteressati quando il ricorso sia stato proposto solo contro taluno di essi",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art30",
          "claim": "Il contraddittorio è integralmente costituito quando l'atto introduttivo è notificato all'amministrazione resistente e, ove esistenti, ai controinteressati",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme principali sono: Art. 101 R.D. 1443/1940 (principio generale del contraddittorio), Art. 49 D.Lgs. 104/2010 (integrazione del contraddittorio in procedimenti amministrativi), Art. 27 D.Lgs. 104/2010 (definizione di contraddittorio integrale), Art. 419 R.D. 1443/1940 (intervento volontario per integrazione necessaria).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art111",
          "claim": "Art. 101 R.D. 1443/1940 - Principio del contraddittorio generale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art52",
          "claim": "Art. 49 D.Lgs. 104/2010 - Integrazione del contraddittorio nei confronti degli altri controinteressati",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art30",
          "claim": "Art. 27 D.Lgs. 104/2010 - Contraddittorio integralmente costituito con notifica atto introduttivo",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art479",
          "claim": "Art. 419 R.D. 1443/1940 - Intervento del terzo salvo che sia effettuato per l'integrazione necessaria del contraddittorio",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art111` | 2.3989 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art52` | 2.1218 | hybrid_rrf |  |
| 3 | `urn:nir:stato:legge.costituzionale:1999-11-23;2~art1` | 2.0215 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art30` | 1.6607 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art479` | 1.1213 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art831` | 1.0520 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art436` | 0.6822 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art420` | 0.5293 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724` | 0.3331 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art409` | -0.8413 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art6bis`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art111`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 101. (Principio del contraddittorio). Il giudice, salvo che la legge disponga altrimenti, non può statuire sopra alcuna domanda, se la parte contro la quale è proposta non è stata regolarmente citata e non è comparsa. Il giudice assicura il rispetto del co

**[2]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art52`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 49 Integrazione del contraddittorio 1. Quando il ricorso sia stato proposto solo contro taluno dei controinteressati, il presidente o il collegio ordina l'integrazione del contraddittorio nei confronti degli altri. 2. L'integrazione del contraddittorio

**[3]** `urn:nir:stato:legge.costituzionale:1999-11-23;2~art1`

> LEGGE COSTITUZIONALE 23 novembre 1999, n. 2 'acquisizione di ogni altro mezzo di prova a suo favore; sia assistita da un interprete se non comprende o non parla la lingua impiegata nel processo. Il processo penale è regolato dal principio del contraddittorio nella formazione della prova. La colpevol

**[4]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art30`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 27 Contraddittorio 1. Il contraddittorio è integralmente costituito quando l'atto introduttivo è notificato all'amministrazione resistente e, ove esistenti, ai controinteressati. 2. Se il giudizio è promosso solo contro alcune delle parti e non si è ver

**[5]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art479`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 419. (Intervento volontario). Salvo che sia effettuato per l'integrazione necessaria del contraddittorio, l'intervento del terzo ai sensi dell'articolo 105 non può aver luogo oltre il termine stabilito per la costituzione del convenuto, con le modalità pre

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art831`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 669-sexies. (Procedimento) Il giudice, sentite le parti, omessa ogni formalità non essenziale al contraddittorio, procede nel modo che ritiene più opportuno agli atti di istruzione indispensabili in relazione ai presupposti e ai fini del provvedimento rich

**[7]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art436`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 384. (Enunciazione del principio di diritto e decisione della causa nel merito). La Corte enuncia il principio di diritto quando decide il ricorso proposto a norma dell'articolo 360, primo comma, n. 3), e in ogni altro caso in cui, decidendo su altri motiv

**[8]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art420`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 371-bis (Deposito dell'atto di integrazione del contraddittorio) Qualora la Corte abbia ordinato l'integrazione del contraddittorio, assegnando alle parti un termine perentorio per provvedervi, il ricorso notificato, contenente nell'intestazione le parole

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-bis (( (Principio del mutuo riconoscimento). )) (( 1. Il principio del mutuo riconoscimento è disciplinato dalle norme del presente titolo e dalle altre disposizioni di legge attuative del diritto dell'Unione europea. 2. Le d

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art409`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 363. (( (Principio di diritto nell'interesse della legge). )) ((Quando le parti non hanno proposto ricorso nei termini di legge o vi hanno rinunciato, ovvero quando il provvedimento non è ricorribile in cassazione e non è altrimenti impugnabile, il Procura

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
