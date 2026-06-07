# trib_011 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:40 UTC |
| **Difficoltà** | media |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (2/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 10.5s (ret 0.6s + llm 9.5s) |

## Query

> Qual è la disciplina dell'accertamento con adesione?

## Risposta

**QUALIFICAZIONE**
L'accertamento con adesione è un procedimento amministrativo in cui il contribuente può accettare l'atto di accertamento redatto dall'ufficio delle entrate, evitando così la fase di contraddittorio.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 regola l'accertamento con adesione.

**GIURISPRUDENZA**
Non ci sono disposizioni giurisprudenziali specifiche sul tema dell'accertamento con adesione.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La normativa è chiara e dettagliata, ma la mancanza di giurisprudenza potrebbe ridurre la solidità del ragionamento.

**GAP ANALYSIS**
Il Packet non contiene giurisprudenza relativa all'accertamento con adesione, che potrebbe fornire ulteriori orientamenti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'accertamento con adesione è un procedimento amministrativo in cui il contribuente può accettare l'atto di accertamento redatto dall'ufficio delle entrate, evitando così la fase di contraddittorio.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art1', 'claim': "L'accertamento con adesione è redatto con atto scritto in duplice esemplare, sottoscritto dal contribuente e dal capo dell'ufficio o da un suo delegato.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 regola l'accertamento con adesione.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:1997-06-19;218~art1', 'claim': "Il DECRETO LEGISLATIVO 19 giugno 1997, n. 218 regola l'accertamento con adesione.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'DECRETO LEGISLATIVO 19 giugno 1997, n. 218'}*

### GIURISPRUDENZA

Non ci sono disposizioni giurisprudenziali specifiche sul tema dell'accertamento con adesione.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La normativa è chiara e dettagliata, ma la mancanza di giurisprudenza potrebbe ridurre la solidità del ragionamento.

### GAP ANALYSIS

Il Packet non contiene giurisprudenza relativa all'accertamento con adesione, che potrebbe fornire ulteriori orientamenti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art1` | 5.3336 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art13` | 5.1616 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7` | 5.1423 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art8` | 3.4214 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | 3.0552 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | 2.8168 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:legge:1970-05-20;300~art18` | 1.9636 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -0.5116 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17` | -1.6284 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12` | -2.1253 | hybrid_rrf | ✅ |

**Recall@10**: 1.00 — trovate 2/2

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art1`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 ito alla formulazione di osservazioni, anche quello alla presentazione di istanza per la definizione dell'accertamento con adesione, in luogo delle osservazioni. L'invito alla presentazione di istanza per la definizione dell'accertamento con adesione è in o

**[2]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art13`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 13 Atto di accertamento con adesione, adempimenti successivi e definizione 1. La definizione si perfeziona secondo quanto previsto dagli articoli 7, 8 e 9. Il versamento delle somme dovute per effetto dell'adesione è effettuato presso l'ufficio del reg

**[3]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art7`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 7 Atto di accertamento con adesione 1. L'accertamento con adesione è redatto con atto scritto in duplice esemplare, sottoscritto dal contribuente e dal capo dell'ufficio o da un suo delegato. Nell'atto sono indicati, separatamente per ciascun tributo,

**[4]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art8`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 8 (Adempimenti successivi). 1. Il versamento delle somme dovute per effetto dell'accertamento con adesione è eseguito entro venti giorni dalla redazione dell'atto di cui all'articolo 7. 2. Le somme dovute possono essere versate anche ratealmente in un

**[5]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  presupposti per un accertamento con adesione, le parti hanno sempre facoltà di dare corso, di comune accordo, al relativo procedimento.)) (23) 1-ter. Il contribuente che si è avvalso della facoltà di cui ((al comma 1-bis, primo e quarto periodo)) , non può

**[6]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 ffici delle entrate, e per la loro organizzazione, secondo criteri di efficienza e di trasparenza; b) per la determinazione delle modalità di accertamento con adesione basate su parametri oggettivi, coefficienti presuntivi e studi di settore nonchè delle mo

**[7]** `urn:nir:stato:legge:1970-05-20;300~art18`

> LEGGE 20 maggio 1970, n. 300  del lavoratore, accerti che vi è anche un difetto di giustificazione del licenziamento, nel qual caso applica, in luogo di quelle previste dal presente comma, le tutele di cui ai commi quarto, quinto o settimo. Il giudice applica la medesima disciplina di cui al quarto

**[8]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 . 600 (Disposizioni comuni in materia di accertamento), abrogato dal presente articolo, prevedeva che: "Quando il reddito netto è definito per mancata impugnazione dell'accertamento dell'ufficio o per rinuncia al proposto gravame prima che sia intervenuta l

**[9]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art17`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218  La definizione in contraddittorio, con adesione del contribuente, è applicabile, alle medesime condizioni di cui all'art. 2-bis, nei confronti dei contribuenti, con riferimento alle imposte sulle successioni e donazioni, di registro, ipotecaria, catastale

**[10]** `urn:nir:stato:decreto.legislativo:1997-06-19;218~art12`

> DECRETO LEGISLATIVO 19 giugno 1997, n. 218 Art. 12 Istanza del contribuente 1. In caso di notifica di avviso di accertamento, o di rettifica, ovvero di atto di recupero, per i quali non si applica il contraddittorio preventivo, il contribuente, anteriormente all'impugnazione dell'atto innanzi alla C

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
