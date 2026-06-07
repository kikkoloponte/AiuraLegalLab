# cross_012 — civile+amministrativo

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 19:50 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_cross)* |
| **Recall@10** | 0.50 ⚠️ (1/2) |
| **Reviewer** | ❌ FAIL / RE_RETRIEVAL |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | LOW |
| **Latenza** | 53.4s (ret 0.1s + llm 53.1s) |

## Query

> Come si risolvono i conflitti tra vincoli urbanistici e diritto di proprietà privata?

## Risposta

**QUALIFICAZIONE**
La domanda riguarda i conflitti tra vincoli urbanistici e diritto di proprietà privata. Il Research Packet fornito non contiene fonti normative che disciplinino specificamente i 'vincoli urbanistici' o le loro relazioni con la proprietà immobiliare.

**NORMA APPLICABILE**
Il Packet contiene articoli del codice civile su: trascrizione atti (Art. 2645-quater), ipoteche (Art. 2815, 2816), acquisto di diritti (Art. 649, 1376), forme scritte (Art. 1350), vendita (Art. 1470), vincoli su crediti (Art. 1997), beni d'interesse storico (Art. 839). Nessuna norma tratta esplicitamente 'vincoli urbanistici'.

**GIURISPRUDENZA**
Il Research Packet non contiene alcuna fonte giurisprudenziale o normativa che affronti la risoluzione dei conflitti tra vincoli urbanistici e proprietà privata. Le fonti disponibili riguardano esclusivamente il codice civile (diritto privato) senza riferimenti al diritto amministrativo/urbanistico.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: Il Research Packet fornito è insufficiente per rispondere alla domanda posta. Non esistono fonti nel Packet che disciplinino i 'vincoli urbanistici' - questi rientrano tipicamente nella legislazione amministrativa (T.U.E., leggi regionali, piani regolatori) non presente nel codice civile del Packet.

**GAP ANALYSIS**
Cosa manca nel Packet: 1) Norme sul diritto amministrativo/urbanistico; 2) Fonti su vincoli urbanistici (art. 143-bis T.U.E., leggi regionali); 3) Giurisprudenza sulla compatibilità tra vincoli e proprietà; 4) Disposizioni sul principio di proporzionalità dei vincoli.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

La domanda riguarda i conflitti tra vincoli urbanistici e diritto di proprietà privata. Il Research Packet fornito non contiene fonti normative che disciplinino specificamente i 'vincoli urbanistici' o le loro relazioni con la proprietà immobiliare.

### NORMA APPLICABILE

Il Packet contiene articoli del codice civile su: trascrizione atti (Art. 2645-quater), ipoteche (Art. 2815, 2816), acquisto di diritti (Art. 649, 1376), forme scritte (Art. 1350), vendita (Art. 1470), vincoli su crediti (Art. 1997), beni d'interesse storico (Art. 839). Nessuna norma tratta esplicitamente 'vincoli urbanistici'.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art2815', 'claim': 'Art. 2815 disciplina ipoteche su diritti reali immobiliari', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}, {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art839', 'claim': "Art. 839 disciplina beni d'interesse storico e artistico sottoposti a leggi speciali", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'GU n.79 del 04/04/1942'}*

### GIURISPRUDENZA

Il Research Packet non contiene alcuna fonte giurisprudenziale o normativa che affronti la risoluzione dei conflitti tra vincoli urbanistici e proprietà privata. Le fonti disponibili riguardano esclusivamente il codice civile (diritto privato) senza riferimenti al diritto amministrativo/urbanistico.

### VALUTAZIONE

VALUTAZIONE PERSONALE: Il Research Packet fornito è insufficiente per rispondere alla domanda posta. Non esistono fonti nel Packet che disciplinino i 'vincoli urbanistici' - questi rientrano tipicamente nella legislazione amministrativa (T.U.E., leggi regionali, piani regolatori) non presente nel codice civile del Packet.

### GAP ANALYSIS

Cosa manca nel Packet: 1) Norme sul diritto amministrativo/urbanistico; 2) Fonti su vincoli urbanistici (art. 143-bis T.U.E., leggi regionali); 3) Giurisprudenza sulla compatibilità tra vincoli e proprietà; 4) Disposizioni sul principio di proporzionalità dei vincoli.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2866` | 2.3523 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3043` | 2.2451 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art738` | 1.8570 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1421` | 1.5886 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1395` | -0.4194 | hybrid_rrf | ✅ |
| 6 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art32` | -1.6449 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art2037` | -2.0936 | hybrid_rrf | ✅ |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3044` | -2.2013 | hybrid_rrf | ✅ |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1520` | -2.7174 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art935` | -4.0817 | hybrid_rrf | ✅ |

**Recall@10**: 0.50 — trovate 1/2

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:2001-06-06;380~art12`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2866`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2645-quater. (( (Trascrizione di atti costitutivi di vincolo). )) ((Si devono trascrivere, se hanno per oggetto beni immobili, gli atti di diritto privato, i contratti e gli altri atti di diritto privato, anche unilaterali, nonché le convenzioni e i contratti

**[2]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3043`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2815. (Ipoteca sul diritto del concedente e sul diritto dell'enfiteuta). Nel caso di affrancazione, le ipoteche gravanti sul diritto del concedente si risolvono sul prezzo dovuto per l'affrancazione; le ipoteche gravanti sul diritto dell'enfiteuta si estendon

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art738`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 649. (Acquisto del legato). Il legato si acquista senza bisogno di accettazione, salva la facoltà di rinunziare. Quando oggetto del legato è la proprietà di una cosa determinata o altro diritto appartenente al testatore, la proprietà o il diritto si trasmette

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1421`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1376. (Contratto con effetti reali). Nei contratti che hanno per oggetto il trasferimento della proprietà di una cosa determinata, la costituzione o il trasferimento di un diritto reale ovvero il trasferimento di un altro diritto, la proprietà o il diritto si

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1395`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1350. (Atti che devono farsi per iscritto). Devono farsi per atto pubblico o per scrittura privata, sotto pena di nullità: 1) i contratti che trasferiscono la proprietà di beni immobili; 2) i contratti che costituiscono, modificano o trasferiscono il diritto

**[6]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447~art32`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 settembre 1988, n. 447 Art. 29 Cessazione del conflitto 1. I conflitti previsti dall'articolo 28 cessano per effetto del provvedimento di uno dei giudici che dichiara, anche di ufficio, la propria competenza o la propria incompetenza.

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art2037`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1997. (Efficacia dei vincoli sul credito). Il pegno, il sequestro, il pignoramento e ogni altro vincolo sul diritto menzionato in un titolo di credito o sulle merci da esso rappresentate non hanno effetto se non si attuano sul titolo.

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3044`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2816. (Ipoteca sul diritto di superficie). Le ipoteche che hanno per oggetto il diritto di superficie si estinguono nel caso di devoluzione della superficie al proprietario del suolo per decorso del termine. Se però il superficiario ha diritto a un corrispett

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1520`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1470. (Nozione). La vendita è il contratto che ha per oggetto il trasferimento della proprietà di una cosa o il trasferimento di un altro diritto verso il corrispettivo di un prezzo.

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art935`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 839. (Beni d'interesse storico e artistico). Le cose di proprietà privata, immobili e mobili, che presentano interesse artistico, storico, archeologico o etnografico, sono sottoposte alle disposizioni delle leggi speciali.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ❌ FAIL |
| Action | RE_RETRIEVAL |
| Warnings | — |
