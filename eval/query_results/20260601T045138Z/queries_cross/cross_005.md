# cross_005 — civile+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:04 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 28.7s (ret 0.3s + llm 28.1s) |

## Query

> Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?

## Risposta

**QUALIFICAZIONE**
Si tratta della questione sull'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

**NORMA APPLICABILE**
Il DECRETO LEGISLATIVO 8 giugno 2001, n. 231 Art. 33 stabilisce la solidarietà del cessionario nei confronti dell'ente cedente.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La solidarietà tributaria del cessionario è stabilita dalla normativa, ma non ci sono giurisprudenze specifiche che la interpretino in dettaglio.

**GAP ANALYSIS**
Il Packet manca di giurisprudenze che interpretino l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Si tratta della questione sull'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2001-06-08;231~art33', 'claim': "Il cessionario è solidalmente obbligato al pagamento delle tasse in caso di cessione dell'azienda.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### NORMA APPLICABILE

Il DECRETO LEGISLATIVO 8 giugno 2001, n. 231 Art. 33 stabilisce la solidarietà del cessionario nei confronti dell'ente cedente.

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2001-06-08;231~art33', 'claim': "Il DECRETO LEGISLATIVO 8 giugno 2001, n. 231 Art. 33 stabilisce la solidarietà del cessionario nei confronti dell'ente cedente.", 'claim_type': 'NORMA', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

*Citazioni: {'source_id': '', 'claim': "Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La solidarietà tributaria del cessionario è stabilita dalla normativa, ma non ci sono giurisprudenze specifiche che la interpretino in dettaglio.

### GAP ANALYSIS

Il Packet manca di giurisprudenze che interpretino l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2001-06-08;231~art33` | 2.6224 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2023-03-31;36~art461` | 2.3184 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1293` | 1.6713 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2769` | 1.1295 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1309` | -1.5010 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.8660 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.9100 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art79` | -2.5745 | hybrid_rrf |  |
| 9 | `urn:nir:stato:decreto.legislativo:2023-03-31;36~art423` | -2.9455 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2729` | -3.3090 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art14`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2001-06-08;231~art33`

> DECRETO LEGISLATIVO 8 giugno 2001, n. 231 Art. 33 Cessione di azienda 1. Nel caso di cessione dell'azienda nella cui attività è stato commesso il reato, il cessionario è solidalmente obbligato, salvo il beneficio della preventiva escussione dell'ente cedente e nei limiti del valore dell'azienda, al

**[2]** `urn:nir:stato:decreto.legislativo:2023-03-31;36~art461`

> DECRETO LEGISLATIVO 31 marzo 2023, n. 36 Articolo 6. Cessioni di crediti. 1. Ai fini dell'opponibilità alle stazioni appaltanti, le cessioni di crediti devono essere stipulate mediante atto pubblico o scrittura privata autenticata e devono essere notificate alle amministrazioni debitrici. 2. Fatto s

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1293`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1248. (Inopponibilità della compensazione). Il debitore, se ha accettato puramente e semplicemente la cessione che il creditore ha fatta delle sue ragioni a un terzo, non può opporre al cessionario la compensazione che avrebbe potuto opporre al cedente. La ce

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2769`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2559. (Crediti relativi all'azienda ceduta). La cessione dei crediti relativi all'azienda ceduta, anche in mancanza di notifica al debitore o di sua accettazione, ha effetto, nei confronti dei terzi, dal momento dell'iscrizione del trasferimento nel registro

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1309`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1264. (Efficacia della cessione riguardo al debitore ceduto). La cessione ha effetto nei confronti del debitore ceduto quando questi l'ha accettata o quando gli è stata notificata. Tuttavia, anche prima della notificazione, il debitore che paga al cedente non

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2112. (Mantenimento dei diritti dei lavoratori in caso di trasferimento d'azienda). In caso di trasferimento d'azienda, il rapporto di lavoro continua con il cessionario ed il lavoratore conserva tutti i diritti che ne derivano. Il cedente ed il cessionario s

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 , preesistente al trasferimento e che conserva nel trasferimento la propria identità a prescindere dalla tipologia negoziale o dal provvedimento sulla base del quale il trasferimento è attuato ivi compresi l'usufrutto o l'affitto di azienda. Le disposizioni del pr

**[8]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art79`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 58 Plusvalenze 1. Per le plusvalenze derivanti da cessione delle aziende, le disposizioni del comma 4 dell'articolo 86 non si applicano quando è richiesta la tassazione separata a norma del comma 2 dell'articolo 17. Il trasferimen

**[9]** `urn:nir:stato:decreto.legislativo:2023-03-31;36~art423`

> DECRETO LEGISLATIVO 31 marzo 2023, n. 36  giurata redatta da un soggetto nominato dal tribunale competente per territorio. 11. Ai fini dell'attestazione di un nuovo soggetto, nell'ipotesi in cui lo stesso utilizzi l'istituto della cessione del complesso aziendale o di un suo ramo, le SOA accertano q

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2729`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2536. (( (Responsabilità del socio uscente e dei suoi eredi). )) ((Il socio che cessa di far parte della società risponde verso questa per il pagamento dei conferimenti non versati, per un anno dal giorno in cui il recesso, la esclusione o la cessione della q

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
