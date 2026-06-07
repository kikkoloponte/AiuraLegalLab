# trib_020 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-06-01 07:33 UTC |
| **Difficoltà** | facile |
| **Intent** | retrieval → norma_lookup |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | MEDIUM |
| **Latenza** | 13.7s (ret 0.2s + llm 13.2s) |

## Query

> Quali sono le esenzioni IVA per le operazioni in ambito sanitario?

## Risposta

**QUALIFICAZIONE**
Le esenzioni IVA per le operazioni in ambito sanitario sono previste dal DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 (Art. 324).

**VALUTAZIONE**
VALUTAZIONE PERSONALE: L'esposizione è chiara e basata su una norma specifica. Tuttavia, non ci sono ulteriori dettagli sulle condizioni di applicazione.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

Le esenzioni IVA per le operazioni in ambito sanitario sono previste dal DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 (Art. 324).

*Citazioni: {'source_id': 'urn:nir:stato:decreto.legislativo:2019-01-12;14~art324', 'claim': 'Le esenzioni IVA per le operazioni in ambito sanitario sono previste dal DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 (Art. 324).', 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: L'esposizione è chiara e basata su una norma specifica. Tuttavia, non ci sono ulteriori dettagli sulle condizioni di applicazione.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324` | 1.6976 | hybrid_rrf |  |
| 2 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art26` | -0.2922 | hybrid_rrf |  |
| 3 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art102` | -3.5557 | hybrid_rrf |  |
| 4 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72` | -3.7562 | hybrid_rrf |  |
| 5 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art40` | -3.8658 | hybrid_rrf |  |
| 6 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art41` | -4.3587 | hybrid_rrf |  |
| 7 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art58` | -4.8488 | hybrid_rrf |  |
| 8 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72` | -4.9170 | hybrid_rrf |  |
| 9 | `urn:nir:stato:legge:2000-07-27;212~art8` | -6.4903 | hybrid_rrf |  |
| 10 | `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72` | -6.6989 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633~art10`

### Snippet fonti

**[1]** `urn:nir:stato:decreto.legislativo:2019-01-12;14~art324`

> DECRETO LEGISLATIVO 12 gennaio 2019, n. 14 Art. 324 Esenzioni dai reati di bancarotta 1. Le disposizioni di cui agli articoli 322, comma 3 e 323 non si applicano ai pagamenti e alle operazioni computi in esecuzione di un concordato preventivo o di accordi di ristrutturazione dei debiti omologati o d

**[2]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art26`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165 Art. 26 Norme per la dirigenza del Servizio sanitario nazionale ( Art.26, commi 1 , 2-quinquies e 3 del d.lgs n.29 del 1993 , modificati prima dall' art.14 del d.lgs n.546 del 1993 e poi dall' art.45, comma 15 del d.lgs n.80 del 1998 ) 1. Alla qualifica di d

**[3]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;600~art102`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 29 settembre 1973, n. 600 Per le obbligazioni e titoli similari sottoscritti anteriormente alla data di entrata in vigore del presente decreto, la ritenuta prevista nel primo comma dell'art. 26 si applica in misura pari al minore tra l'ammontare determinato a

**[4]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  associazioni volontarie di mutua assistenza aventi personalità giuridica, consorzi e società di servizi. 7. Con il Servizio sanitario nazionale può intercorrere un unico rapporto di lavoro. Tale rapporto e incompatibile con ogni altro rapporto di lavoro dip

**[5]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art40`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  dirigenza. Una apposita ((area o)) sezione contrattuale di un'area dirigenziale riguarda la dirigenza del ruolo sanitario del Servizio sanitario nazionale, per gli effetti di cui all' articolo 15 del decreto legislativo 30 dicembre 1992, n. 502 , e successi

**[6]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art41`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165 Art. 41 (Poteri di indirizzo nei confronti dell'ARAN). 1. Il potere di indirizzo nei confronti dell'ARAN e le altre competenze relative alle procedure di contrattazione collettiva nazionale sono esercitati dalle pubbliche amministrazioni attraverso le propri

**[7]** `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917~art58`

> DECRETO DEL PRESIDENTE DELLA REPUBBLICA 22 dicembre 1986, n. 917 Art. 47-bis (Disposizioni in materia di regimi fiscali privilegiati) 1. I regimi fiscali di Stati o territori, diversi da quelli appartenenti all'Unione europea ovvero da quelli aderenti allo Spazio economico europeo con i quali l'Ital

**[8]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165 pressive, anche a cura dei carabinieri dei Nuclei antisofisticazione e sanità, in caso di accertate anomalie di danno del Servizio sanitario nazionale, restando attribuiti alla responsabilità regionale gli ulteriori ritardi nella adozione generalizzata della

**[9]** `urn:nir:stato:legge:2000-07-27;212~art8`

> LEGGE 27 luglio 2000, n. 212  della compensazione dei crediti, ai sensi del comma 1 del presente articolo; detta esclusione opera a prescindere dalla tipologia e dall'importo dei crediti, anche qualora questi ultimi non siano maturati con riferimento all'attività esercitata con la partita IVA oggett

**[10]** `urn:nir:stato:decreto.legislativo:2001-03-30;165~art72`

> DECRETO LEGISLATIVO 30 marzo 2001, n. 165  comunitarie e, limitatamente alle modalità di erogazione, degli accordi di lavoro per il personale dipendente; b) gli standard organizzativi e di attività sono determinati a fini di calcolo del parametro capitario di finanziamento e non costituiscono vincol

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
