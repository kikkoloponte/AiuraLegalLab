# cross_030 — tributario+civile+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:10 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.67 ⚠️ (2/3) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 66.6s (ret 0.1s + llm 66.3s) |

## Query

> Come si coordinano la dichiarazione di fallimento, i crediti tributari privilegiati e l'azione dell'agente della riscossione?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La dichiarazione di fallimento (fallimento) è disciplinata dal DPR n. 917/1986, art. 183 che tratta fallimento e liquidazione coatta amministrativa. I crediti tributari privilegiati sono regolati dal Codice Civile (RD 262/1942), in particolare gli articoli 2770-2780 che definiscono l'ordine dei privilegi sugli immobili, inclusi i crediti per imposte sui redditi immobiliari e le spese di giustizia. L'agente della riscossione è disciplinato dall'art. 1744 del Codice Civile che limita la facoltà di riscuotere crediti del preponente senza autorizzazione.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227",
          "claim": "Il DPR 917/1986, art. 183 disciplina fallimento e liquidazione coatta amministrativa",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2995",
          "claim": "L'ordine dei privilegi sugli immobili è disciplinato dal Codice Civile art. 2770 e seguenti",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1803",
          "claim": "L'agente della riscossione non ha facoltà di riscuotere i crediti del preponente senza autorizzazione (art. 1744)",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme applicabili sono: 1) DPR 917/1986, art. 183 per la dichiarazione di fallimento; 2) RD 262/1942, art. 2770-2780 per i crediti tributari privilegiati sugli immobili (imposte sui redditi immobiliari hanno prelazione); 3) DLGS 14/2019, art. 150 che vieta azioni esecutive individuali dal giorno della dichiarazione di apertura della liquidazione giudiziale; 4) RD 262/1942, art. 2782 per il concorso dei crediti egualmente privilegiati in proporzione del rispettivo importo.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227",
          "claim": "DPR 917/1986, art. 183 disciplina fallimento e liquidazione coatta amministrativa",
          "claim_type": "FACT",
          "source

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La dichiarazione di fallimento (fallimento) è disciplinata dal DPR n. 917/1986, art. 183 che tratta fallimento e liquidazione coatta amministrativa. I crediti tributari privilegiati sono regolati dal Codice Civile (RD 262/1942), in particolare gli articoli 2770-2780 che definiscono l'ordine dei privilegi sugli immobili, inclusi i crediti per imposte sui redditi immobiliari e le spese di giustizia. L'agente della riscossione è disciplinato dall'art. 1744 del Codice Civile che limita la facoltà di riscuotere crediti del preponente senza autorizzazione.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227",
          "claim": "Il DPR 917/1986, art. 183 disciplina fallimento e liquidazione coatta amministrativa",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art2995",
          "claim": "L'ordine dei privilegi sugli immobili è disciplinato dal Codice Civile art. 2770 e seguenti",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1942-03-16;262~art1803",
          "claim": "L'agente della riscossione non ha facoltà di riscuotere i crediti del preponente senza autorizzazione (art. 1744)",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": ""
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme applicabili sono: 1) DPR 917/1986, art. 183 per la dichiarazione di fallimento; 2) RD 262/1942, art. 2770-2780 per i crediti tributari privilegiati sugli immobili (imposte sui redditi immobiliari hanno prelazione); 3) DLGS 14/2019, art. 150 che vieta azioni esecutive individuali dal giorno della dichiarazione di apertura della liquidazione giudiziale; 4) RD 262/1942, art. 2782 per il concorso dei crediti egualmente privilegiati in proporzione del rispettivo importo.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227",
          "claim": "DPR 917/1986, art. 183 disciplina fallimento e liquidazione coatta amministrativa",
          "claim_type": "FACT",
          "source

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227` | 2.2929 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art150` | -0.2895 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art17` | -0.5490 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3008` | -0.6663 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3006` | -2.7815 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3000` | -2.8578 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1761` | -3.8594 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2999` | -4.5218 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1803` | -5.2490 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2995` | -5.2885 | hybrid_rrf | ✅ |

**Recall@10**: 0.67 — trovate 2/3

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602~art87`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art227`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 183 Fallimento e liquidazione coatta 1. Nei casi di fallimento e di liquidazione coatta amministrativa il reddito di impresa relativo al periodo compreso tra l'inizio dell'esercizio e la dichiarazione di fallimento o il provvedime

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art150`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 150 Divieto di azioni esecutive e cautelari individuali 1. Salvo diversa disposizione della legge, dal giorno della dichiarazione di apertura della liquidazione giudiziale nessuna azione individuale esecutiva o cautelare anche per crediti maturati dura

**[3]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art17`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 'indicazione dei rispettivi crediti scaduti e a scadere e dell'esistenza di diritti reali e personali di garanzia; (( d) una dichiarazione resa ai sensi dell'articolo 46 del testo unico di cui al decreto del Presidente della Repubblica n. 445 del 2000 sulla

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3008`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2782. (Concorso di crediti egualmente privilegiati). I crediti egualmente privilegiati concorrono tra loro in proporzione del rispettivo importo. La stessa disposizione si osserva quando concorrono tra loro più crediti privilegiati ai quali le leggi speciali

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3006`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2780. Ordine dei privilegi sugli immobili. Quando sul prezzo dello stesso immobile concorrono più crediti privilegiati, la prelazione ha luogo secondo l'ordine seguente: 1) i crediti per le imposte sui redditi immobiliari, indicati dall'articolo 2771; 2) i cr

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3000`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2775. (Contributi per opere di bonifica e di miglioramento). I crediti per i contributi indicati dall'art. 864 sono privilegiati sugli immobili che traggono beneficio dalle opere di bonifica o di miglioramento. La costituzione del privilegio per le opere di m

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1761`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1702. (Riscossione dei crediti da parte dell'ultimo vettore). L'ultimo vettore rappresenta i vettori precedenti per la riscossione dei rispettivi crediti che nascono dal contratto di trasporto e per l'esercizio del privilegio sulle cose trasportate. Se egli o

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2999`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2774. (Crediti per concessione di acque). I crediti dello Stato per i canoni dovuti dai concessionari di acque pubbliche o di acque derivate da canali demaniali ovvero per i lavori eseguiti d'ufficio sono privilegiati sugli impianti, in conformità delle leggi

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1803`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1744. (Riscossioni). L'agente non ha facoltà di riscuotere i crediti del preponente. Se questa facoltà gli è stata attribuita, egli non può concedere sconti o dilazioni senza speciale autorizzazione.

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2995`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2770. (Crediti per atti conservativi o di espropriazione). I crediti per le spese di giustizia fatte per atti conservativi o per l'espropriazione di beni immobili nell'interesse comune dei creditori sono privilegiati sul prezzo degli immobili stessi. Del pari

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
