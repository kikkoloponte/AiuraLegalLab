# trib_010 — tributario

| Campo | Valore |
|---|---|
| **Data** | 2026-05-31 13:39 UTC |
| **Difficoltà** | difficile |
| **Intent** | reasoning → fattispecie_analysis |
| **Workspace** | normattiva *(remappato da normattiva_tributario)* |
| **Recall@10** | 0.00 ❌ (0/1) |
| **Reviewer** | ✅ PASS / DELIVER |
| **Confidenza retrieval** | HIGH |
| **Confidenza analisi** | HIGH |
| **Latenza** | 6.8s (ret 0.3s + llm 6.0s) |

## Query

> Quali sono i presupposti per l'iscrizione ipotecaria da parte dell'agente della riscossione?

## Risposta

**QUALIFICAZIONE**
L'iscrizione ipotecaria da parte dell'agente della riscossione si basa sul fatto che l'agente ha eseguito un contratto di trasporto e rappresenta i vettori precedenti per la riscossione dei rispettivi crediti.

**VALUTAZIONE**
VALUTAZIONE PERSONALE: La valutazione è alta in quanto la norma è chiara e specifica sul ruolo dell'agente nella riscossione dei crediti.

## Analisi (Chain of Thought)

### QUALIFICAZIONE

L'iscrizione ipotecaria da parte dell'agente della riscossione si basa sul fatto che l'agente ha eseguito un contratto di trasporto e rappresenta i vettori precedenti per la riscossione dei rispettivi crediti.

*Citazioni: {'source_id': 'urn:nir:stato:regio.decreto:1942-03-16;262~art1761', 'claim': "L'ultimo vettore rappresenta i vettori precedenti per la riscossione dei rispettivi crediti che nascono dal contratto di trasporto e per l'esercizio del privilegio sulle cose trasportate.", 'claim_type': 'FACT', 'source_authority': 'NORMATTIVA', 'gu_reference': ''}*

### VALUTAZIONE

VALUTAZIONE PERSONALE: La valutazione è alta in quanto la norma è chiara e specifica sul ruolo dell'agente nella riscossione dei crediti.

## Fonti recuperate

| # | URN | Score | Metodo | Attesa |
|---|---|---|---|---|
| 1 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3083` | 3.1532 | hybrid_rrf |  |
| 2 | `urn:nir:stato:legge:2000-07-27;212~art7` | 1.5750 | hybrid_rrf |  |
| 3 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1804` | 1.5568 | hybrid_rrf |  |
| 4 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1807` | -0.9267 | hybrid_rrf |  |
| 5 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1805` | -1.5672 | hybrid_rrf |  |
| 6 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1761` | -2.0453 | hybrid_rrf |  |
| 7 | `urn:nir:stato:regio.decreto:1942-03-16;262~art3085` | -3.6729 | hybrid_rrf |  |
| 8 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1810` | -4.3652 | hybrid_rrf |  |
| 9 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1808` | -4.8581 | hybrid_rrf |  |
| 10 | `urn:nir:stato:regio.decreto:1942-03-16;262~art1812` | -4.9606 | hybrid_rrf |  |

**Recall@10**: 0.00 — trovate 0/1

**Fonti attese non trovate:**
- `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;602~art77`

### Snippet fonti

**[1]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3083`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2854. (Ipoteche iscritte nello stesso grado). I crediti con iscrizione ipotecaria dello stesso grado sugli stessi beni concorrono tra loro in proporzione dell'importo relativo.

**[2]** `urn:nir:stato:legge:2000-07-27;212~art7`

> LEGGE 27 luglio 2000, n. 212 Art. 7 Chiarezza e motivazione degli atti 1. Gli atti dell'amministrazione finanziaria ((, autonomamente impugnabili dinanzi agli organi della giurisdizione tributaria,)) sono motivati ((, a pena di annullabilità, indicando specificamente i presupposti, i mezzi di prova)

**[3]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1804`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1745. (Rappresentanza dell'agente). Le dichiarazioni che riguardano l'esecuzione del contratto concluso per il tramite dell'agente e i reclami relativi alle inadempienze contrattuali sono validamente fatti all'agente. L'agente può chiedere i provvedimenti cau

**[4]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1807`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1748. (( (Diritti dell'agente). )) ((Per tutti gli affari conclusi durante il contratto l'agente ha diritto alla provvigione quando l'operazione è stata conclusa per effetto del suo intervento. La provvigione è dovuta anche per gli affari conclusi dal prepone

**[5]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1805`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1746. (Obblighi dell'agente). Nell'esecuzione dell'incarico l'agente deve tutelare gli interessi del preponente e agire con lealtà e buona fede. In particolare, deve adempiere l'incarico affidatogli in conformità delle istruzioni ricevute e fornire al prepone

**[6]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1761`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1702. (Riscossione dei crediti da parte dell'ultimo vettore). L'ultimo vettore rappresenta i vettori precedenti per la riscossione dei rispettivi crediti che nascono dal contratto di trasporto e per l'esercizio del privilegio sulle cose trasportate. Se egli o

**[7]** `urn:nir:stato:regio.decreto:1942-03-16;262~art3085`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 2856. (Surrogazione del creditore perdente). Il creditore che ha ipoteca sopra uno o più immobili, qualora si trovi perdente perché sul loro prezzo si è in tutto o in parte soddisfatto un creditore anteriore, la cui ipoteca si estendeva ad altri beni dello st

**[8]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1810`

> REGIO DECRETO 16 marzo 1942, n. 262  concessione dell'indennità non priva comunque l'agente del diritto all'eventuale risarcimento dei danni. L'agente decade dal diritto all'indennità prevista dal presente articolo se, nel termine di un anno dallo scioglimento del rapporto, omette di comunicare al p

**[9]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1808`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1749. (( (Obblighi del preponente). )) ((Il preponente, nei rapporti con l'agente, deve agire con lealtà e buona fede. Egli deve mettere a disposizione dell'agente la documentazione necessaria relativa ai beni o servizi trattati e fornire all'agente le inform

**[10]** `urn:nir:stato:regio.decreto:1942-03-16;262~art1812`

> REGIO DECRETO 16 marzo 1942, n. 262 Art. 1752. (Agente con rappresentanza). Le disposizioni del presente capo si applicano anche nell'ipotesi in cui all'agente è conferita dal preponente la rappresentanza per la conclusione dei contratti.

## CitationReviewer

| Campo | Valore |
|---|---|
| Verdict | ✅ PASS |
| Action | DELIVER |
| Warnings | — |
