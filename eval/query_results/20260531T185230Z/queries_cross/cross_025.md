# cross_025 — penale+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:05 UTC |
| **Difficoltà** | media |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.2s (ret 0.1s + llm 64.9s) |

## Query

> Come si coordina il procedimento penale con la sospensione cautelare del dipendente pubblico?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda il coordinamento tra procedimento penale e sospensione cautelare del dipendente pubblico. Il Packet contiene norme sulla sospensione della prescrizione (Art. 159 CP), effetti della sospensione nel processo civile (Art. 298 CPC), e proroga custodia cautelare per perizia (Art. 305 CPP). Tuttavia, nessuna fonte nel Packet tratta specificamente la 'sospensione cautelare del dipendente pubblico' come istituto giuridico autonomo.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art177",
          "claim": "Art. 159 Codice Penale disciplina la sospensione del corso della prescrizione quando imposta da disposizione di legge",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.263 del 04/11/1930"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art339",
          "claim": "Art. 298 Codice Procedura Civile stabilisce che durante la sospensione non possono essere compiuti atti del procedimento",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.301 del 04/11/1940"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art364",
          "claim": "Art. 305 Codice Procedura Penale disciplina la proroga della custodia cautelare in caso di perizia sullo stato di mente dell'imputato",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.267 del 04/11/1988"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme rilevanti nel Packet sono: Art. 159 CP (sospensione prescrizione), Art. 298 CPC (effetti sospensione), Art. 305 CPP (proroga custodia cautelare). Nessuna norma specifica tratta il coordinamento tra procedimento penale e sospensione amministrativa del dipendente pubblico.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art177",
          "claim": "Art. 159 CP - Sospensione del corso della prescrizione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.263 del 04/11/1930"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art339",
          "claim": "Art. 298 CPC - Effetti della sospensione (atti non compiibili)",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.301 del 04/11/1940"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art364",
          "claim": "Art. 305 CPP - Proroga custodia cautelare per perizia",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.267 del 04/11/1988"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Packet non contiene fonti giurisprudenziali (sentenze Corte Costituzionale, Cassazione) che traccino l'orientamento prevalente sul coordinamento tra procedimento penale e sospensione del dipendente pubblico. La fonte [8] menziona una sentenza della Corte Costit

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda il coordinamento tra procedimento penale e sospensione cautelare del dipendente pubblico. Il Packet contiene norme sulla sospensione della prescrizione (Art. 159 CP), effetti della sospensione nel processo civile (Art. 298 CPC), e proroga custodia cautelare per perizia (Art. 305 CPP). Tuttavia, nessuna fonte nel Packet tratta specificamente la 'sospensione cautelare del dipendente pubblico' come istituto giuridico autonomo.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art177",
          "claim": "Art. 159 Codice Penale disciplina la sospensione del corso della prescrizione quando imposta da disposizione di legge",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.263 del 04/11/1930"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art339",
          "claim": "Art. 298 Codice Procedura Civile stabilisce che durante la sospensione non possono essere compiuti atti del procedimento",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.301 del 04/11/1940"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art364",
          "claim": "Art. 305 Codice Procedura Penale disciplina la proroga della custodia cautelare in caso di perizia sullo stato di mente dell'imputato",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.267 del 04/11/1988"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Le norme rilevanti nel Packet sono: Art. 159 CP (sospensione prescrizione), Art. 298 CPC (effetti sospensione), Art. 305 CPP (proroga custodia cautelare). Nessuna norma specifica tratta il coordinamento tra procedimento penale e sospensione amministrativa del dipendente pubblico.",
      "citations": [
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art177",
          "claim": "Art. 159 CP - Sospensione del corso della prescrizione",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.263 del 04/11/1930"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1940-10-28;1443~art339",
          "claim": "Art. 298 CPC - Effetti della sospensione (atti non compiibili)",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.301 del 04/11/1940"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art364",
          "claim": "Art. 305 CPP - Proroga custodia cautelare per perizia",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.267 del 04/11/1988"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Packet non contiene fonti giurisprudenziali (sentenze Corte Costituzionale, Cassazione) che traccino l'orientamento prevalente sul coordinamento tra procedimento penale e sospensione del dipendente pubblico. La fonte [8] menziona una sentenza della Corte Costit

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art177` | 5.2814 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art802` | 3.8294 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art339` | 2.7085 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art444` | 1.9748 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art362` | 1.9088 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art1016` | 1.8206 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1940-10-28;1443~art838` | 1.7181 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art681` | 1.1914 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art558` | 0.7453 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art364` | 0.2466 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2001-03-30;165~art55ter`
- `urn:nir:stato:decreto.legislativo:2001-03-30;165~art55quater`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art177`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 159. (Sospensione del corso della prescrizione). Il corso della prescrizione rimane sospeso in ogni caso in cui la sospensione del procedimento o del processo penale o dei termini di custodia cautelare è imposta da una particolare disposizione di legge, ol

**[2]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art802`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 746-quater (( (Trasferimento di procedimenti penali all'estero).)) (( 1. Quando il pubblico ministero ha notizia della pendenza di un procedimento penale all'estero, per gli stessi fatti per i quali si è proceduto all'iscrizione

**[3]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art339`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 298. (Effetti della sospensione). Durante la sospensione non possono essere compiuti atti del procedimento. La sospensione interrompe i termini in corso, i quali ricominciano a decorrere dal giorno della nuova udienza fissata nel provvedimento di sospensio

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art444`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 371-bis. (False informazioni al pubblico ministero ((o al procuratore della Corte penale internazionale)) ) Chiunque, nel corso di un procedimento penale, richiesto dal pubblico ministero ((o dal procuratore della Corte penale internazionale)) di fornire i

**[5]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art362`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 1, comma 3) che "I termini previsti dall' articolo 303, comma 1, del codice di procedura penale sono sospesi dalla data del provvedimento che accoglie la dichiarazione di astensione o di ricusazione a quella in cui il dibattimento dav

**[6]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art1016`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 819-bis. (( (Sospensione del procedimento arbitrale). )) ((Ferma l'applicazione dell'articolo 816-sexies, gli arbitri sospendono il procedimento arbitrale con ordinanza motivata nei seguenti casi: 1) quando il processo dovrebbe essere sospeso a norma del c

**[7]** `urn:nir:stato:regio.decreto:1940-10-28;1443~art838`

> REGIO DECRETO 28 ottobre 1940, n. 1443 Art. 669-terdecies. (Reclamo contro i provvedimenti cautelari) ((Contro l'ordinanza con la quale è stato concesso o negato il provvedimento cautelare è ammesso reclamo nel termine perentorio di quindici giorni dalla pronuncia in udienza ovvero dalla comunicazio

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art681`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 ura penale , nella parte in cui non consente la sospensione dell'esecuzione della pena detentiva nei confronti dei minorenni condannati per i delitti ivi elencati". ------------- AGGIORNAMENTO (257) La Corte Costituzionale, con senten

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art558`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447  (290) 3. Se il pubblico ministero ha esercitato l'azione penale con citazione diretta per un reato per il quale è prevista l'udienza preliminare e la relativa eccezione è proposta entro il termine indicato dall'articolo 491, comma 1,

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art364`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 305 Proroga della custodia cautelare 1. In ogni stato e grado del procedimento di merito, quando è disposta perizia sullo stato di mente dell'imputato, i termini di custodia cautelare sono prorogati per il periodo di tempo assegn

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
