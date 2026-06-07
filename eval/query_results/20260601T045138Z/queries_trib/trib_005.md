# trib_005 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:27 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 1.00 ✅ (1/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 29.2s (ret 0.2s + llm 28.6s) |

## Query

> Come funziona l'istituto dell'interpello tributario?

## Risposta

**QUALIFICAZIONE**
L'istituto dell'interpello tributario permette al contribuente di richiedere una risposta riguardante fattispecie concrete e personali relative all'applicazione delle disposizioni tributarie.

**NORMA APPLICABILE**
Il diritto di interpello è regolato dall'articolo 11 della legge 27 luglio 2000, n. 212.

**GIURISPRUDENZA**
Non sono presenti giurisprudenze specifiche sulla funzione dell'interpello tributario nel Packet.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La norma è chiara e specifica sul diritto di interpello, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

**GAP ANALYSIS**
Il Packet non contiene giurisprudenze relative all'interpello tributario, che potrebbero fornire ulteriori orientamenti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'istituto dell'interpello tributario permette al contribuente di richiedere una risposta riguardante fattispecie concrete e personali relative all'applicazione delle disposizioni tributarie.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art11', 'claim': "Il contribuente può interpellare l'amministrazione finanziaria per ottenere una risposta riguardante fattispecie concrete e personali relativamente alla applicazione delle disposizioni tributarie.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'LEGGE 27 luglio 2000, n. 212'}*

### NORMA APPLICABILE

Il diritto di interpello è regolato dall'articolo 11 della legge 27 luglio 2000, n. 212.

*Citazioni: {'source_id': 'urn:nir:stato:legge:2000-07-27;212~art11', 'claim': "Il diritto di interpello è regolato dall'articolo 11 della legge 27 luglio 2000, n. 212.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': 'LEGGE 27 luglio 2000, n. 212'}*

### GIURISPRUDENZA

Non sono presenti giurisprudenze specifiche sulla funzione dell'interpello tributario nel Packet.

*Citazioni: {'source_id': 'VALUTAZIONE PERSONALE:', 'claim': 'Non sono presenti giurisprudenze specifiche sul tema.', 'claim_type': 'OPINION', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La norma è chiara e specifica sul diritto di interpello, ma la mancanza di giurisprudenza rende l'interpretazione un po' più incerta.

### GAP ANALYSIS

Il Packet non contiene giurisprudenze relative all'interpello tributario, che potrebbero fornire ulteriori orientamenti.

*Citazioni: {'source_id': 'VALUTAZIONE PERSONALE:', 'claim': "Il Packet non contiene giurisprudenze relative all'interpello tributario.", 'claim_type': 'OPINION', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:legge:2000-07-27;212~art11` | 0.8690 | hybrid_rrf | ✅ |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art19` | 0.0195 | hybrid_rrf | ✅ |
| 3 | `urn:nir:stato:legge:2000-07-27;212~art2` | -1.6211 | hybrid_rrf | ✅ |
| 4 | `urn:nir:stato:legge:2000-07-27;212~art11` | -2.1892 | hybrid_rrf | ✅ |
| 5 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art25` | -4.5951 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art363` | -5.0105 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88` | -6.8045 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art68` | -7.4772 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge:2000-07-27;212~art11` | -7.6359 | hybrid_rrf | ✅ |
| 10 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207` | -7.9044 | hybrid_rrf |  |

**Recall@10**: 1.00 — trovate 1/1

### Snippet fonti

**[1]** `urn:nir:stato:legge:2000-07-27;212~art11`

> LEGGE 27 luglio 2000, n. 212 Art. 11 (Interpello) 1. Il contribuente può interpellare l'amministrazione finanziaria per ottenere una risposta riguardante fattispecie concrete e personali relativamente alla: a) applicazione delle disposizioni tributarie, quando vi sono condizioni di obiettiva incerte

**[2]** `urn:nir:stato:legge:2000-07-27;212~art19`

> LEGGE 27 luglio 2000, n. 212 Art. 19 Attuazione del diritto di interpello del contribuente 1. L'amministrazione finanziaria, nel quadro dell'attuazione del decreto legislativo 30 luglio 1999, n. 300 , adotta ogni opportuno adeguamento della struttura organizzativa ed individua l'occorrente riallocaz

**[3]** `urn:nir:stato:legge:2000-07-27;212~art2`

> LEGGE 27 luglio 2000, n. 212 Art. 2 Chiarezza e trasparenza delle disposizioni tributarie 1. Le leggi e gli altri atti aventi forza di legge che contengono disposizioni tributarie devono menzionarne l'oggetto nel titolo; la rubrica delle partizioni interne e dei singoli articoli deve menzionare l'og

**[4]** `urn:nir:stato:legge:2000-07-27;212~art11`

> LEGGE 27 luglio 2000, n. 212 , e ai soggetti che presentano le istanze di interpello di cui all' articolo 2 del decreto legislativo 14 settembre 2015, n. 147 . 3. ((La presentazione delle istanze di interpello, in relazione a fattispecie particolarmente complesse, è in ogni caso subordinata al versa

**[5]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art25`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165 istituzione scolastica, coordinando il relativo personale. (48) 6. Il dirigente presenta periodicamente al consiglio di circolo o al consiglio di istituto motivata relazione sulla direzione e il coordinamento dell'attività formativa, organizzativa e amminist

**[6]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art363`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 363 Certificazione dei debiti contributivi e per premi assicurativi 1. L'Istituto nazionale per la previdenza sociale e l'Istituto nazionale per gli infortuni sul lavoro, su richiesta del debitore o del tribunale, comunicano i crediti dagli stessi vant

**[7]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art88`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 88 (( (Trattamento dei crediti tributari e contributivi). )) (( 1. Con il piano di concordato il debitore, esclusivamente mediante proposta presentata ai sensi del presente articolo, può proporre il pagamento, parziale o anche dilazionato, dei tributi

**[8]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art68`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 licato per un parametro corrispondente al numero dei componenti il nucleo familiare della scala di equivalenza dell'ISEE di cui al decreto del Presidente del Consiglio dei ministri del 5 dicembre 2013, n. 159 . 4. L'OCC, entro sette giorni dall'avvenuto con

**[9]** `urn:nir:stato:legge:2000-07-27;212~art11`

> LEGGE 27 luglio 2000, n. 212  che cade il sabato o un giorno festivo è senz'altro prorogato al primo giorno successivo non festivo. La risposta, scritta e motivata, vincola ogni organo dell'amministrazione finanziaria con esclusivo riferimento alla questione oggetto dell'istanza e limitatamente al r

**[10]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art207`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 genzia delle Entrate, prima di procedere all'emissione dell'avviso di accertamento d'imposta o di maggiore imposta, deve notificare all'interessato un apposito avviso con il quale viene concessa al medesimo la possibilità di fornire, n

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
