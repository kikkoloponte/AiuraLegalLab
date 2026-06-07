# cross_026 — civile+penale+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:06 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.3s (ret 0.1s + llm 65.0s) |

## Query

> Come opera il sequestro conservativo a garanzia dei crediti tributari nel processo penale?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "Il sequestro conservativo è un istituto giuridico che permette al creditore di garantire il proprio credito su beni del debitore o terzi, prevenendo la dispersione dei beni. Nel contesto tributario e processuale penale, si tratta di una misura cautelare patrimoniale.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art841",
          "claim": "Il giudice può autorizzare il sequestro conservativo di beni mobili o immobili del debitore a garanzia del credito",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3134",
          "claim": "Il sequestro conservativo può essere chiesto anche nei confronti del terzo acquirente",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme principali sul sequestro conservativo sono contenute nel codice di procedura civile (R.D. 1940 n. 1443). L'esecuzione sui mobili segue le norme del pignoramento presso debitore o terzi (Art. 678), sugli immobili con trascrizione al conservatore dei registri (Art. 679). La conversione in pignoramento avviene al momento della sentenza di condanna esecutiva (Art. 686).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art848",
          "claim": "Il sequestro conservativo sui mobili e crediti si esegue secondo norme stabilite per il pignoramento presso debitore o terzi",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art849",
          "claim": "Il sequestro conservativo sugli immobili si esegue con trascrizione presso l'ufficio del conservatore dei registri immobiliari",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art856",
          "claim": "Il sequestro conservativo si converte in pignoramento al momento della sentenza di condanna esecutiva",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Research Packet non contiene riferimenti a sent

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "Il sequestro conservativo è un istituto giuridico che permette al creditore di garantire il proprio credito su beni del debitore o terzi, prevenendo la dispersione dei beni. Nel contesto tributario e processuale penale, si tratta di una misura cautelare patrimoniale.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art841",
          "claim": "Il giudice può autorizzare il sequestro conservativo di beni mobili o immobili del debitore a garanzia del credito",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art3134",
          "claim": "Il sequestro conservativo può essere chiesto anche nei confronti del terzo acquirente",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme principali sul sequestro conservativo sono contenute nel codice di procedura civile (R.D. 1940 n. 1443). L'esecuzione sui mobili segue le norme del pignoramento presso debitore o terzi (Art. 678), sugli immobili con trascrizione al conservatore dei registri (Art. 679). La conversione in pignoramento avviene al momento della sentenza di condanna esecutiva (Art. 686).",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art848",
          "claim": "Il sequestro conservativo sui mobili e crediti si esegue secondo norme stabilite per il pignoramento presso debitore o terzi",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art849",
          "claim": "Il sequestro conservativo sugli immobili si esegue con trascrizione presso l'ufficio del conservatore dei registri immobiliari",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art856",
          "claim": "Il sequestro conservativo si converte in pignoramento al momento della sentenza di condanna esecutiva",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Research Packet non contiene riferimenti a sent

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art841` | 4.1687 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3134` | 3.4618 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art848` | 3.0900 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art319` | 2.3918 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art319` | 2.3743 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art849` | 1.8276 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art856` | 1.8198 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art470` | 1.6636 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art854` | 1.0037 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art250` | 0.8475 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art316`
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602~art22`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art841`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 671. (Sequestro conservativo). Il giudice, su istanza del creditore che ha fondato timore di perdere la garanzia del proprio credito, può autorizzare il sequestro conservativo di beni mobili o immobili del debitore o delle somme e cose a lui dovute, nei li

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3134`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2905. (Sequestro nei confronti del debitore o del terzo). Il creditore può chiedere il sequestro conservativo dei beni del debitore, secondo le regole stabilite dal codice di procedura civile . Il sequestro può essere chiesto anche nei confronti del terzo acq

**[3]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art848`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 678. (Esecuzione del sequestro conservativo sui mobili). Il sequestro conservativo sui mobili e sui crediti si esegue secondo le norme stabilite per il pignoramento presso il debitore o presso terzi. In quest'ultimo caso il sequestrante deve, con l'atto di

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art319`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14  economicamente non autosufficienti e, in ogni stato e grado del procedimento, chiede il sequestro conservativo dei beni di cui al comma 1, a garanzia del risarcimento dei danni civili subiti dai figli delle vittime. 2. Se vi è fondata ragione di ritenere c

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art319`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 319 Sequestro conservativo 1. In pendenza della procedura di liquidazione giudiziale non può essere disposto sequestro conservativo ai sensi dell' articolo 316 del codice di procedura penale sulle cose di cui all'articolo 142. 2. Quando, disposto seque

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art849`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 679. (Esecuzione del sequestro conservativo sugli immobili). Il sequestro conservativo sugli immobili si esegue con la trascrizione del provvedimento ((presso l'ufficio del conservatore dei registri immobiliari)) del luogo in cui i beni sono situati. Per l

**[7]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art856`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 686. (Conversione del sequestro conservativo in pignoramento). Il sequestro conservativo si converte in pignoramento al momento in cui il creditore sequestrante ottiene sentenza di condanna esecutiva. Se i beni sequestrati sono stati oggetto di esecuzione

**[8]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art470`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 388-bis. (( (Violazione colposa dei doveri inerenti alla custodia di cose sottoposte a pignoramento ovvero a sequestro giudiziario o conservativo). )) ((Chiunque, avendo in custodia una cosa sottoposta a pignoramento ovvero a sequestro giudiziario o conser

**[9]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art854`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 684. (Revoca del sequestro). Il debitore può ottenere dal giudice istruttore, con ordinanza non impugnabile, la revoca del sequestro conservativo, prestando idonea cauzione per l'ammontare del credito che ha dato causa al sequestro e per le spese, in ragio

**[10]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art250`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 224. (Sequestro del documento). Se il documento impugnato di falso si trova presso un depositario, il giudice istruttore può ordinarne il sequestro con le forme previste nel codice di procedura penale , dopo di che si redige il processo verbale di cui all'

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
