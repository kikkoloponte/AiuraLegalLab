# cross_005 — civile+tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:16 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 22.2s (ret 0.3s + llm 21.7s) |

## Query

> Qual è l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario?

## Risposta

**QUALIFICAZIONE**
Si tratta di determinare l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

**NORMA APPLICABILE**
Il Regio Decreto 16 marzo 1942, n. 262 Art. 2536 regola la responsabilità del socio uscente e dei suoi eredi in caso di cessione dell'azienda.

**GIURISPRUDENZA**
Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'opponibilità al fisco degli atti di cessione d'azienda o alla solidarietà tributaria del cessionario.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma applicabile è chiara ma non ci sono giurisprudenze specifiche per questo caso. La valutazione della solidarietà tributaria del cessionario richiede ulteriori indagini.

**GAP ANALYSIS**
Il Packet manca di giurisprudenza specifica sull'opponibilità al fisco degli atti di cessione d'azienda e sulla solidarietà tributaria del cessionario.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Si tratta di determinare l'opponibilità al fisco degli atti di cessione d'azienda e la solidarietà tributaria del cessionario.

### NORMA APPLICABILE

Il Regio Decreto 16 marzo 1942, n. 262 Art. 2536 regola la responsabilità del socio uscente e dei suoi eredi in caso di cessione dell'azienda.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2729', 'claim': 'Il socio che cessa di far parte della società risponde verso questa per il pagamento dei conferimenti non versati, per un anno dal giorno in cui il recesso, la esclusione o la cessione della quota.', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### GIURISPRUDENZA

Non ci sono giurisprudenze specifiche menzionate nel Packet che si riferiscano esplicitamente all'opponibilità al fisco degli atti di cessione d'azienda o alla solidarietà tributaria del cessionario.

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma applicabile è chiara ma non ci sono giurisprudenze specifiche per questo caso. La valutazione della solidarietà tributaria del cessionario richiede ulteriori indagini.

### GAP ANALYSIS

Il Packet manca di giurisprudenza specifica sull'opponibilità al fisco degli atti di cessione d'azienda e sulla solidarietà tributaria del cessionario.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1293` | 1.6713 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2769` | 1.1295 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1309` | -1.5010 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.8660 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2152` | -1.9100 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2729` | -3.3090 | hybrid_rrf | ✅ |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art212` | -3.4738 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2770` | -3.5700 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2692` | -3.7633 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1306` | -4.2660 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art14`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1293`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1248. (Inopponibilità della compensazione). Il debitore, se ha accettato puramente e semplicemente la cessione che il creditore ha fatta delle sue ragioni a un terzo, non può opporre al cessionario la compensazione che avrebbe potuto opporre al cedente. La ce

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2769`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2559. (Crediti relativi all'azienda ceduta). La cessione dei crediti relativi all'azienda ceduta, anche in mancanza di notifica al debitore o di sua accettazione, ha effetto, nei confronti dei terzi, dal momento dell'iscrizione del trasferimento nel registro

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1309`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1264. (Efficacia della cessione riguardo al debitore ceduto). La cessione ha effetto nei confronti del debitore ceduto quando questi l'ha accettata o quando gli è stata notificata. Tuttavia, anche prima della notificazione, il debitore che paga al cedente non

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2112. (Mantenimento dei diritti dei lavoratori in caso di trasferimento d'azienda). In caso di trasferimento d'azienda, il rapporto di lavoro continua con il cessionario ed il lavoratore conserva tutti i diritti che ne derivano. Il cedente ed il cessionario s

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2152`

> REGIO DECRETO 16 marzo 1942, n. 262 , preesistente al trasferimento e che conserva nel trasferimento la propria identità a prescindere dalla tipologia negoziale o dal provvedimento sulla base del quale il trasferimento è attuato ivi compresi l'usufrutto o l'affitto di azienda. Le disposizioni del pr

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2729`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2536. (( (Responsabilità del socio uscente e dei suoi eredi). )) ((Il socio che cessa di far parte della società risponde verso questa per il pagamento dei conferimenti non versati, per un anno dal giorno in cui il recesso, la esclusione o la cessione della q

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art212`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 uiti da altri contratti collettivi applicabili all'impresa del cessionario. L'effetto di sostituzione si produce esclusivamente fra contratti collettivi del medesimo livello. Ferma restando la facoltà di esercitare il recesso ai sensi della normativa in mat

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2770`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2560. (Debiti relativi all'azienda ceduta). L'alienante non è liberato dai debiti, inerenti all'esercizio dell'azienda ceduta anteriori al trasferimento, se non risulta che i creditori vi hanno consentito. Nel trasferimento di un'azienda commerciale risponde

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2692`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2506. (Forme di scissione). Con la scissione una società assegna l'intero suo patrimonio a più società, preesistenti o di nuova costituzione, o parte del suo patrimonio, in tal caso anche ad una sola società, e le relative azioni o quote ai suoi soci. È conse

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1306`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1261. (Divieti di cessione). I magistrati dell'ordine giudiziario, i funzionari delle cancellerie e segreterie giudiziarie, gli ufficiali giudiziari, gli avvocati, i procuratori, i patrocinatori e i notai non possono, neppure per interposta persona, rendersi

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
