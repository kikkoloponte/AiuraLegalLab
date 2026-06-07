# cross_003 — tributario+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:40 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.00 ❌ (0/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 65.2s (ret 0.1s + llm 64.9s) |

## Query

> Qual è la natura giuridica dell'atto impositivo e i suoi rapporti con il provvedimento amministrativo?

## Risposta

**ANALISI**
{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "L'atto impositivo è un provvedimento amministrativo di natura tributaria che impone obblighi contributivi al contribuente. Il rapporto con il provvedimento amministrativo generale si configura come sottomodale: l'atto impositivo rappresenta una specifica applicazione del potere amministrativo in materia fiscale.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art5",
          "claim": "L'atto impositivo è disciplinato dal DLgs 19 giugno 1997, n. 218",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art11",
          "claim": "L'avvio del procedimento tributario avviene contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Gli articoli applicabili sono: DLgs 218/1997 Art. 5 (disciplina generale atti impositivi), DLgs 218/1997 Art. 11 (avvio procedimento), RD 262/1942 Codice Civile (per aspetti di responsabilità e gestione dell'impresa).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art5",
          "claim": "Art. 5 DLgs 218/1997 disciplina gli atti impositivi",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art11",
          "claim": "Art. 11 DLgs 218/1997 disciplina l'avvio del procedimento tributario",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decredo:1942-03-16;262~art2126",
          "claim": "RD 262/1942 Art. 2086 disciplina la gestione dell'impresa (assetto organizzativo)",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Non sono presenti nel Research Packet fonti giurisprudenziali specifiche che affrontino la natura giuridica dell'atto impositivo e il suo rapporto con i provvedimenti amministrativi generali. Le fonti disponibili si concentrano su aspetti procedurali (DLgs 218/1997) e di diritto societario/civile (RD 262/1942).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art123",
          "claim": "DLgs 104/2010 Art. 118 disciplina le controversie devolute alla giurisdizione esclusiva del giudice amministrativo",
          "claim_type": "FACT",
          "source_authority": "

## Analisi (Chain of Thought)

### ANALISI

{
  "analysis_sections": [
    {
      "step": "QUALIFICAZIONE",
      "content": "L'atto impositivo è un provvedimento amministrativo di natura tributaria che impone obblighi contributivi al contribuente. Il rapporto con il provvedimento amministrativo generale si configura come sottomodale: l'atto impositivo rappresenta una specifica applicazione del potere amministrativo in materia fiscale.",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art5",
          "claim": "L'atto impositivo è disciplinato dal DLgs 19 giugno 1997, n. 218",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art11",
          "claim": "L'avvio del procedimento tributario avviene contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "NORMA APPLICABILE",
      "content": "Gli articoli applicabili sono: DLgs 218/1997 Art. 5 (disciplina generale atti impositivi), DLgs 218/1997 Art. 11 (avvio procedimento), RD 262/1942 Codice Civile (per aspetti di responsabilità e gestione dell'impresa).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art5",
          "claim": "Art. 5 DLgs 218/1997 disciplina gli atti impositivi",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:decreto.legislativo:1997-06-19;218~art11",
          "claim": "Art. 11 DLgs 218/1997 disciplina l'avvio del procedimento tributario",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        },
        {
          "source_id": "urn:nir:stato:regio.decredo:1942-03-16;262~art2126",
          "claim": "RD 262/1942 Art. 2086 disciplina la gestione dell'impresa (assetto organizzativo)",
          "claim_type": "FACT",
          "source_authority": "NORMATTIVA",
          "gu_reference": "GU n.79 del 04/04/1942"
        }
      ]
    },
    {
      "step": "GIURISPRUDENZA",
      "content": "Non sono presenti nel Research Packet fonti giurisprudenziali specifiche che affrontino la natura giuridica dell'atto impositivo e il suo rapporto con i provvedimenti amministrativi generali. Le fonti disponibili si concentrano su aspetti procedurali (DLgs 218/1997) e di diritto societario/civile (RD 262/1942).",
      "citations": [
        {
          "source_id": "urn:nir:stato:decreto.legislativo:2010-07-02;104~art123",
          "claim": "DLgs 104/2010 Art. 118 disciplina le controversie devolute alla giurisdizione esclusiva del giudice amministrativo",
          "claim_type": "FACT",
          "source_authority": "

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art5` | 3.4935 | hybrid_rrf |  |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art74` | 2.9787 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art123` | 1.1831 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2126` | 1.1311 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2010-07-02;104~art15` | 0.3679 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art375` | -0.8631 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art60` | -1.4105 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11` | -1.5663 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art62` | -1.7855 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1930-10-19;1398~art407` | -2.1682 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/2

**Fonti attese non trovate:**
- `urn:nir:stato:legge:2000-07-27;212~art7`
- `urn:nir:stato:legge:1990-08-07;241~art3`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art5`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 EMBRE 2008, N. 185 , CONVERTITO CON MODIFICAZIONI DALLA L. 28 GENNAIO 2009, N. 2 . 3-bis. Qualora tra la data di comparizione, di cui al comma 1, lettera b), e quella di decadenza dell'amministrazione dal potere di notificazione dell'atto impositivo interco

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art74`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 41. (Responsabilità dei componenti. Rappresentanza in giudizio). Qualora il comitato non abbia ottenuto la personalità giuridica, i suoi componenti rispondono personalmente e solidalmente delle obbligazioni assunte. I sottoscrittori sono tenuti soltanto a eff

**[3]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art123`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 118 Decreto ingiuntivo 1. Nelle controversie devolute alla giurisdizione esclusiva del giudice amministrativo, aventi ad oggetto diritti soggettivi di natura patrimoniale, si applica il Capo I del Titolo I del Libro IV del codice di procedura civile . P

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2126`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2086. ((Gestione dell'impresa)) L'imprenditore è il capo dell'impresa e da lui dipendono gerarchicamente i suoi collaboratori. ((L'imprenditore, che operi in forma societaria o collettiva, ha il dovere di istituire un assetto organizzativo, amministrativo e c

**[5]** `urn:nir:stato:decreto.legislativo:2010-07-02;104~art15`

> DECRETO LEGISLATIVO 2 luglio 2010, n. 104 Art. 12 Rapporti con l'arbitrato 1. Le controversie concernenti diritti soggettivi devolute alla giurisdizione del giudice amministrativo possono essere risolte mediante arbitrato rituale di diritto ((ai sensi degli articoli 806 e seguenti del codice di proc

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art375`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 375 Assetti organizzativi dell'impresa 1. La rubrica dell' articolo 2086 del codice civile è sostituita dalla seguente: «Gestione dell'impresa». 2. All' articolo 2086 del codice civile , dopo il primo comma è aggiunto il seguente: «L'imprenditore, che

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art60`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 27. (Estinzione della persona giuridica). Oltre che per le cause previste nell'atto costitutivo e nello statuto, la persona giuridica si estingue quando lo scopo è stato raggiunto o è divenuto impossibile. Le associazioni si estinguono inoltre quando tutti gl

**[8]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art11`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 11 Avvio del procedimento 1. ((L'ufficio di iniziativa, nei casi di cui all' articolo 6-bis, comma 2, della legge n. 212 del 2000 , contestualmente alla notifica dell'avviso di accertamento o di rettifica ovvero dell'atto di recupero, ovvero su istanza

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art62`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 29. (Divieto di nuove operazioni). Gli amministratori non possono compiere nuove operazioni, appena è stato loro comunicato il provvedimento che dichiara l'estinzione della persona giuridica o il provvedimento con cui l'autorità, a norma di legge, ha ordinato

**[10]** `urn:nir:stato:regio.decreto:1930-10-19;1398~art407`

> REGIO DECRETO 19 ottobre 1930, n. 1398 Art. 339-bis. (( (Circostanza aggravante. Atti intimidatori di natura ritorsiva ai danni di un componente di un Corpo politico, amministrativo o giudiziario).)) ((Salvo che il fatto costituisca più grave reato, le pene stabilite per i delitti previsti dagli art

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
