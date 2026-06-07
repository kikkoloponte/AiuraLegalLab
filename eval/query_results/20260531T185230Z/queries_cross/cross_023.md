# cross_023 — tributario+penale

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 20:02 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 67.3s (ret 0.2s + llm 67.0s) |

## Query

> Quali sono i rapporti tra il principio del ne bis in idem e il doppio binario sanzionatorio tributario-penale?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda il rapporto tra il principio del ne bis in idem (non due volte per la stessa cosa) e il doppio binario sanzionatorio tributario-penale. Il Research Packet non contiene fonti che disciplinino direttamente il principio del ne bis in idem o il rapporto specifico tra sanzioni amministrative-tributarie e penali per lo stesso fatto.",
      "citations": []
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Dalle fonti disponibili nel Packet, l'Art. 10 della Legge 27 luglio 2000, n. 212 (source_id: urn:nir:stato:legge:2000-07-27;212~art10) stabilisce che i rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede, ma non affronta il ne bis in idem. L'Art. 3-bis del Codice Penale (source_id: urn:nir:stato:regio.decreto:1930-10-19;1398~art7) riguarda la riserva di codice per nuove disposizioni che prevedono reati, ma non disciplina il rapporto tra sanzioni tributarie e penali.",
      "citations": [
        {
          "source_id": "urn:nir:stato:legge:2000-07-27;212~art10",
          "claim": "I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.236 del 10/10/2000"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art7",
          "claim": "Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.301 del 25/10/1930"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Research Packet non contiene alcuna giurisprudenza o orientamento prevalente sul principio del ne bis in idem applicato al doppio binario sanzionatorio tributario-penale. Le fonti disponibili (source_id: urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59, source_id: urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757) riguardano il codice di procedura penale ma non affrontano specificamente la questione del ne bis in idem nel contesto tributario-penale.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59",
          "claim": "Disposizioni del codice di procedura penale relative a sanzioni e importi adeguati ogni due anni",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.264 del 05/10/1988"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757",
          "claim": "Disposizioni del codice di procedura penale relative a persone estratate e restrizione della libertà personale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.264 del 05/10/1988"
        }
      ]
    },
    {
      "step": "VALUTAZIONE",
      "content": "VALUTAZIONE PERSONALE: Il Research Packet fornito non contiene informazioni sufficienti per rispondere alla domanda sul rapporto tra

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "La domanda riguarda il rapporto tra il principio del ne bis in idem (non due volte per la stessa cosa) e il doppio binario sanzionatorio tributario-penale. Il Research Packet non contiene fonti che disciplinino direttamente il principio del ne bis in idem o il rapporto specifico tra sanzioni amministrative-tributarie e penali per lo stesso fatto.",
      "citations": []
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Dalle fonti disponibili nel Packet, l'Art. 10 della Legge 27 luglio 2000, n. 212 (source_id: urn:nir:stato:legge:2000-07-27;212~art10) stabilisce che i rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede, ma non affronta il ne bis in idem. L'Art. 3-bis del Codice Penale (source_id: urn:nir:stato:regio.decreto:1930-10-19;1398~art7) riguarda la riserva di codice per nuove disposizioni che prevedono reati, ma non disciplina il rapporto tra sanzioni tributarie e penali.",
      "citations": [
        {
          "source_id": "urn:nir:stato:legge:2000-07-27;212~art10",
          "claim": "I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.236 del 10/10/2000"
        },
        {
          "source_id": "urn:nir:stato:regio.decreto:1930-10-19;1398~art7",
          "claim": "Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.301 del 25/10/1930"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Il Research Packet non contiene alcuna giurisprudenza o orientamento prevalente sul principio del ne bis in idem applicato al doppio binario sanzionatorio tributario-penale. Le fonti disponibili (source_id: urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59, source_id: urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757) riguardano il codice di procedura penale ma non affrontano specificamente la questione del ne bis in idem nel contesto tributario-penale.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59",
          "claim": "Disposizioni del codice di procedura penale relative a sanzioni e importi adeguati ogni due anni",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.264 del 05/10/1988"
        },
        {
          "source_id": "urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757",
          "claim": "Disposizioni del codice di procedura penale relative a persone estratate e restrizione della libertà personale",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.264 del 05/10/1988"
        }
      ]
    },
    {
      "step": "VALUTAZIONE",
      "content": "VALUTAZIONE PERSONALE: Il Research Packet fornito non contiene informazioni sufficienti per rispondere alla domanda sul rapporto tra

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art10` | 3.4052 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2709` | 0.8772 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724` | -0.2436 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art7` | -1.4396 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317` | -3.6633 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59` | -4.6593 | hybrid_rrf |  |
| 7 | `urn:nir:stato:legge:2000-07-27;212~art1` | -5.7070 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47` | -6.0516 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757` | -6.7800 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art449` | -7.6958 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.legislativo:2000-03-10;74~art20`
- `urn:nir:stato:decreto.legislativo:1997-12-18;471~art13`

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art10`

> LEGGE 27 luglio 2000, n. 212 Art. 10 Tutela dell'affidamento e della buona fede. Errori del contribuente 1. I rapporti tra contribuente e amministrazione finanziaria sono improntati al principio della collaborazione e della buona fede. 2. Non sono irrogate sanzioni nè richiesti interessi moratori al

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2709`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2516. (( (Rapporti con i soci).)) ((Nella costituzione e nell'esecuzione dei rapporti mutualistici deve essere rispettato il principio di parità di trattamento.))

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art724`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 696-bis (( (Principio del mutuo riconoscimento). )) (( 1. Il principio del mutuo riconoscimento è disciplinato dalle norme del presente titolo e dalle altre disposizioni di legge attuative del diritto dell'Unione europea. 2. Le d

**[4]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art7`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 3-bis. (( (Principio della riserva di codice). )) ((Nuove disposizioni che prevedono reati possono essere introdotte nell'ordinamento solo se modificano il codice penale ovvero sono inserite in leggi che disciplinano in modo organico la materia.))

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art317`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 317 Principio di prevalenza delle misure cautelari reali e tutela dei terzi 1. Le condizioni e i criteri di prevalenza rispetto alla gestione concorsuale delle misure cautelari reali sulle cose indicate dall'articolo 142 sono regolate dalle disposizion

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art59`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 ((, che può essere aumentata fino al doppio, tenuto conto della causa di inammissibilità della richiesta)) . ((6-bis. Gli importi di cui al comma 6 sono adeguati ogni due anni con decreto del Ministro della giustizia, di concerto con

**[7]** `urn:nir:stato:legge:2000-07-27;212~art1`

> LEGGE 27 luglio 2000, n. 212 La Camera dei deputati ed il Senato della Repubblica hanno approvato; IL PRESIDENTE DELLA REPUBBLICA Promulga la seguente legge: Art. 1 Principi generali 1. Le disposizioni della presente legge, in attuazione ((delle norme della Costituzione, dei principi dell'ordinament

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art47`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Art. 31-bis.1 (( (Strumenti di cooperazione amministrativa avanzata). )) (( 1. L'Amministrazione finanziaria, in attuazione del principio di economicità dell'azione amministrativa, si avvale di strumenti di cooperazione amministrativa

**[9]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art757`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 721 (( (Principio di specialità).)) (( 1. La persona estradata non può essere sottoposta a restrizione della libertà personale in esecuzione di una pena o di una misura di sicurezza detentiva, né assoggettata ad altra misura rest

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art449`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 374-bis. (False dichiarazioni o attestazioni in atti destinati all'autorità giudiziaria ((o alla Corte penale internazionale)) ). Salvo che il fatto costituisca più grave reato, è punito con la reclusione da uno a cinque anni chiunque dichiara o attesta fa

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
