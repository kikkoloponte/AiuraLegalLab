# cross_030 — tributario+civile+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:29 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.67 ⚠️ (2/3) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 25.2s (ret 0.3s + llm 24.7s) |

## Query

> Come si coordinano la dichiarazione di fallimento, i crediti tributari privilegiati e l'azione dell'agente della riscossione?

## Risposta

**QUALIFICAZIONE**
La domanda riguarda la coordinazione tra la dichiarazione di fallimento, i crediti tributari privilegiati e l'azione dell'agente della riscossione.

**NORMA APPLICABILE**
Il Regio Decreto del 16 marzo 1942, n. 262, Art. 2782 regola la concorrenza tra crediti egualmente privilegiati.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente a questa situazione.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e non ci sono contrasti giurisprudenziali rilevanti. La solidità della valutazione è ALTA.

**GAP ANALYSIS**
Non ci sono gap notevoli nel Packet, ma sarebbe utile avere una giurisprudenza specifica per confermare la concorrenza tra i crediti tributari privilegiati e l'azione dell'agente della riscossione.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La domanda riguarda la coordinazione tra la dichiarazione di fallimento, i crediti tributari privilegiati e l'azione dell'agente della riscossione.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art3008', 'claim': 'I crediti egualmente privilegiati concorrono tra loro in proporzione del rispettivo importo.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### NORMA APPLICABILE

Il Regio Decreto del 16 marzo 1942, n. 262, Art. 2782 regola la concorrenza tra crediti egualmente privilegiati.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art3008', 'claim': 'I crediti egualmente privilegiati concorrono tra loro in proporzione del rispettivo importo.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'REGIO DECRETO 16 marzo 1942, n. 262'}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano direttamente a questa situazione.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e non ci sono contrasti giurisprudenziali rilevanti. La solidità della valutazione è ALTA.

### GAP ANALYSIS

Non ci sono gap notevoli nel Packet, ma sarebbe utile avere una giurisprudenza specifica per confermare la concorrenza tra i crediti tributari privilegiati e l'azione dell'agente della riscossione.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art390` | 2.5141 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art75` | 0.7630 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3131` | -0.0428 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art150` | -0.2895 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art17` | -0.5490 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3008` | -0.6663 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art292` | -1.7998 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3006` | -2.7815 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3000` | -2.8578 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art153` | -2.9329 | hybrid_rrf | ✅ |

**Recall@10**: 0.67 — trovate 2/3

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602~art87`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art390`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 390 Disciplina transitoria 1. I ricorsi per dichiarazione di fallimento e le proposte di concordato fallimentare, i ricorsi per l'omologazione degli accordi di ristrutturazione, per l'apertura del concordato preventivo, per l'accertamento dello stato d

**[2]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art75`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 75 Documentazione e trattamento dei crediti privilegiati 1. Il debitore deve allegare alla domanda: a) il piano con i bilanci, le scritture contabili e fiscali obbligatorie, le dichiarazioni dei redditi, le dichiarazioni IRAP e le dichiarazioni annuali

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3131`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2902. (Effetti). Il creditore, ottenuta la dichiarazione di inefficacia, può promuovere nei confronti dei terzi acquirenti le azioni esecutive o conservative sui beni che formano oggetto dell'atto impugnato. Il terzo contraente, che abbia verso il debitore ra

**[4]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art150`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 150 Divieto di azioni esecutive e cautelari individuali 1. Salvo diversa disposizione della legge, dal giorno della dichiarazione di apertura della liquidazione giudiziale nessuna azione individuale esecutiva o cautelare anche per crediti maturati dura

**[5]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art17`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 'indicazione dei rispettivi crediti scaduti e a scadere e dell'esistenza di diritti reali e personali di garanzia; (( d) una dichiarazione resa ai sensi dell'articolo 46 del testo unico di cui al decreto del Presidente della Repubblica n. 445 del 2000 sulla

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3008`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2782. (Concorso di crediti egualmente privilegiati). I crediti egualmente privilegiati concorrono tra loro in proporzione del rispettivo importo. La stessa disposizione si osserva quando concorrono tra loro più crediti privilegiati ai quali le leggi speciali

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art292`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 292 Postergazione del rimborso dei crediti da finanziamenti infragruppo 1. I crediti che la società o l'ente o la persona fisica esercente l'attività di direzione e o coordinamento vanta, anche a seguito di escussione di garanzie, nei confronti delle i

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3006`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2780. Ordine dei privilegi sugli immobili. Quando sul prezzo dello stesso immobile concorrono più crediti privilegiati, la prelazione ha luogo secondo l'ordine seguente: 1) i crediti per le imposte sui redditi immobiliari, indicati dall'articolo 2771; 2) i cr

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3000`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2775. (Contributi per opere di bonifica e di miglioramento). I crediti per i contributi indicati dall'art. 864 sono privilegiati sugli immobili che traggono beneficio dalle opere di bonifica o di miglioramento. La costituzione del privilegio per le opere di m

**[10]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art153`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 153 Diritto dei creditori privilegiati nella ripartizione dell'attivo 1. I creditori garantiti da ipoteca, pegno o privilegio fanno valere il loro diritto di prelazione sul prezzo dei beni vincolati per il capitale, gli interessi e le spese; se non son

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
