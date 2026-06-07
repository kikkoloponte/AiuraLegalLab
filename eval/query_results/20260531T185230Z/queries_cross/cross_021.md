# cross_021 — penale+civile

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:00 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.8s (ret 0.1s + llm 67.5s) |

## Query

> Come si configura la responsabilità dell'ente ex D.Lgs. 231/2001 e i suoi rapporti con la responsabilità civile della società?

## Risposta

**ANALISI**
```json
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La responsabilità dell'ente ex D.Lgs. 231/2001 riguarda la responsabilità amministrativa del soggetto giuridico per reati commessi nel suo interesse o a suo vantaggio da soggetti apicali o dipendenti. La responsabilità civile della società si riferisce invece al risarcimento danni verso terzi in base alle norme generali di diritto societario.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2740",
          "claim": "Il debitore risponde dell'adempimento delle obbligazioni con tutti i suoi beni presenti e futuri",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2497",
          "claim": "Le società o gli enti che esercitano attività di direzione e coordinamento in violazione dei principi di corretta gestione societaria sono responsabili",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme applicabili alla responsabilità dell'ente e della società sono: Art. 2740 c.c. (responsabilità patrimoniale generale), Art. 18 c.c. (responsabilità amministratori verso l'ente), Art. 2396-terdecies c.c. (azione sociale di responsabilità), Art. 2409-decies c.c. (azione del consiglio di sorveglianza), Art. 2497 c.c. (violazione principi gestione societaria).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2740",
          "claim": "Art. 2740 c.c. - Responsabilità patrimoniale generale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art51",
          "claim": "Art. 18 c.c. - Responsabilità amministratori verso l'ente secondo norme del mandato",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2477",
          "claim": "Art. 2396-terdecies c.c. - Azione sociale di responsabilità promovibile dal collegio sindacale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2500",
          "claim": "Art. 2409-decies c.c. - Azione sociale di responsabilità promovibile dal consiglio di sorveglianza",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2649",
          "claim": "Art. 2497 c.c. - Responsabilità società per violazione principi di corretta gestione societaria",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Non sono presenti nel Research Packet fonti giurisprudenziali specifiche che collegano esplicitamente D.Lgs. 231/2001 con la responsabilità civile della società. Le

## Analisi (Chain of Thought)

### ANALISI

```json
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La responsabilità dell'ente ex D.Lgs. 231/2001 riguarda la responsabilità amministrativa del soggetto giuridico per reati commessi nel suo interesse o a suo vantaggio da soggetti apicali o dipendenti. La responsabilità civile della società si riferisce invece al risarcimento danni verso terzi in base alle norme generali di diritto societario.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2740",
          "claim": "Il debitore risponde dell'adempimento delle obbligazioni con tutti i suoi beni presenti e futuri",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2497",
          "claim": "Le società o gli enti che esercitano attività di direzione e coordinamento in violazione dei principi di corretta gestione societaria sono responsabili",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme applicabili alla responsabilità dell'ente e della società sono: Art. 2740 c.c. (responsabilità patrimoniale generale), Art. 18 c.c. (responsabilità amministratori verso l'ente), Art. 2396-terdecies c.c. (azione sociale di responsabilità), Art. 2409-decies c.c. (azione del consiglio di sorveglianza), Art. 2497 c.c. (violazione principi gestione societaria).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2740",
          "claim": "Art. 2740 c.c. - Responsabilità patrimoniale generale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art51",
          "claim": "Art. 18 c.c. - Responsabilità amministratori verso l'ente secondo norme del mandato",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2477",
          "claim": "Art. 2396-terdecies c.c. - Azione sociale di responsabilità promovibile dal collegio sindacale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2500",
          "claim": "Art. 2409-decies c.c. - Azione sociale di responsabilità promovibile dal consiglio di sorveglianza",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2649",
          "claim": "Art. 2497 c.c. - Responsabilità società per violazione principi di corretta gestione societaria",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Non sono presenti nel Research Packet fonti giurisprudenziali specifiche che collegano esplicitamente D.Lgs. 231/2001 con la responsabilità civile della società. Le

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2964` | -0.1690 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art43` | -0.4936 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art214` | -0.6300 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art255` | -1.0348 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art51` | -1.8227 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2477` | -1.8663 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2338` | -1.9948 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2500` | -2.3800 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2649` | -2.5757 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3179` | -2.9647 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2001-06-08;231~art5`
- `urn:nir:stato:decreto.legislativo:2001-06-08;231~art6`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2964`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2740. (Responsabilità patrimoniale). Il debitore risponde dell'adempimento delle obbligazioni con tutti i suoi beni presenti e futuri. Le limitazioni della responsabilità non sono ammesse se non nei casi stabiliti dalla legge.

**[2]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art43`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 34. (Decadenza dalla responsabilità genitoriale e sospensione dall'esercizio di essa). La legge determina i casi nei quali la condanna importa la decadenza dalla responsabilità genitoriale. La condanna per delitti commessi con abuso della responsabilità ge

**[3]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art214`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 imento in una o più società, eventualmente di nuova costituzione, dell'azienda o di rami della stessa, ovvero di beni o crediti, con i relativi rapporti contrattuali in corso, esclusa la responsabilità dell'alienante ai sensi dell' articolo 2560 del codice

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art255`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 255 Azioni di responsabilità 1. Il curatore, autorizzato ai sensi dell'articolo 128, comma 2, può promuovere o proseguire: a) l'azione sociale di responsabilità; b) l'azione dei creditori sociali prevista dall' articolo 2394 e dall' articolo 2476, sest

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art51`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 18. (Responsabilità degli amministratori). Gli amministratori sono responsabili verso l'ente secondo le norme del mandato. È però esente da responsabilità quello degli amministratori il quale non abbia partecipato all'atto che ha causato il danno, salvo il ca

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2477`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2396-terdecies. (( (Azione sociale di responsabilità).)) . ((L'azione di responsabilità può essere promossa anche a seguito di deliberazione del collegio sindacale, assunta con la maggioranza dei due terzi dei suoi componenti.))

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2338`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2297. (Mancata registrazione). Fino a quando la società non è iscritta nel registro delle imprese, i rapporti tra la società e i terzi, ferma restando la responsabilità illimitata e solidale di tutti i soci, sono regolati dalle disposizioni relative alla soci

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2500`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2409-decies. (( (Azione sociale di responsabilità). )) . ((L'azione sociale di responsabilità può anche essere proposta a seguito di deliberazione del consiglio di sorveglianza. La deliberazione è assunta dalla maggioranza dei componenti del consiglio di sorv

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2649`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2497. (Responsabilità). Le società o gli enti che, esercitando attività di direzione e coordinamento di società, agiscono nell'interesse imprenditoriale proprio o altrui in violazione dei principi di corretta gestione societaria e imprenditoriale delle societ

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3179`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2949. (Prescrizione in materia di società). Si prescrivono in cinque anni i diritti che derivano dai rapporti sociali, se la società è iscritta nel registro delle imprese. Nello stesso termine si prescrive l'azione di responsabilità che spetta ai creditori so

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
