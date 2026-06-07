# Golden Test Set — Design Spec
**Data:** 2026-05-31
**Milestone:** 1D
**Scope:** Prima sessione di validazione con avvocato specializzato in penale tributario
**Stato:** Approvato

---

## 1. Obiettivo

Costruire un Golden Test Set di 10 query validate da un avvocato esperto in penale
tributario, da usare come benchmark di qualità per AiUra LegalLab. Le query alimentano
`eval/queries.jsonl` con `expected_source_ids` definiti da un umano anziché
auto-generati, rendendo le metriche recall@k e `lawyer_pass_rate` ecologicamente valide.

---

## 2. Formato sessione — Ibrido

### 2.1 Videocall (30 min)

| Minuti | Attività |
|--------|----------|
| 0–5    | Orientamento: cosa fa il sistema, cosa NON fa (no giurisprudenza ancora, solo normativa), cosa si chiede di valutare |
| 5–25   | Co-costruzione query: 2 min × 10. Per ognuna: scenario proposto dall'avvocato → formulazione concordata → norme attese annotate |
| 25–30  | Accordo sulla rubrica di valutazione e termine di restituzione (48–72h) |

**Regola:** non eseguire il sistema live in videocall. L'obiettivo è costruire le query, non valutare le risposte.

### 2.2 Valutazione asincrona

Dopo la videocall:
1. Eseguire le 10 query su AiUra LegalLab
2. Montare il pacchetto di valutazione (PDF o Google Doc — una scheda per query)
3. Inviare all'avvocato con termine di restituzione concordato

---

## 3. Le 10 query — Distribuzione tematica

Specializzazione: **penale tributario** (D.Lgs. 74/2000 + CP + TUIR + IVA + D.Lgs. 472/1997)

| # | Sotto-area | Norma cardine | Difficoltà |
|---|-----------|---------------|------------|
| 1 | Dichiarazione fraudolenta con fatture false | D.Lgs. 74/2000 art. 2 | easy |
| 2 | Dichiarazione infedele: soglia di punibilità | D.Lgs. 74/2000 art. 4 | medium |
| 3 | Omesso versamento IVA: soglia e termine | D.Lgs. 74/2000 art. 10-ter | easy |
| 4 | Indebita compensazione con crediti non spettanti | D.Lgs. 74/2000 art. 10-quater | medium |
| 5 | Cause di non punibilità: ravvedimento operoso | D.Lgs. 74/2000 artt. 13–13-bis | medium |
| 6 | Confisca per equivalente in materia tributaria | D.Lgs. 74/2000 art. 12-bis | hard |
| 7 | Responsabilità 231 per reati tributari | D.Lgs. 231/2001 art. 25-quinquiesdecies | hard |
| 8 | Cumulo sanzioni amministrative e penali (ne bis in idem) | D.Lgs. 472/1997 + D.Lgs. 74/2000 art. 19 | hard |
| 9 | Sequestro preventivo: presupposti in reato tributario | D.Lgs. 74/2000 + c.p.p. | medium |
| 10 | **Cross**: base imponibile TUIR e dichiarazione infedele | TUIR DPR 917/86 + D.Lgs. 74/2000 art. 4 | hard |

**Logica della distribuzione:**
- 3 easy / 4 medium / 3 hard — stress test progressivo
- Query 10 è deliberatamente cross-modulo (TUIR + penale): diagnostica il punto debole `cross: 0.372` del run2
- Query 7 e 8 coprono le aree con recall più basso nel run2

---

## 4. Pacchetto di valutazione asincrona

Una scheda per query. Struttura fissa:

```
[Scheda query #N]

Scenario:
> testo della query concordata in videocall

Risposta del sistema:
> testo integrale generato da AiUra

Fonti citate dal sistema:
| # | Fonte | Articolo | Snippet |
|---|-------|----------|---------|
| 1 | ...   | ...      | ...     |

Norme attese (concordate in videocall):
> lista libera
```

### Rubrica di valutazione (compilata dall'avvocato)

| Dimensione | Valutazione |
|------------|-------------|
| La risposta è giuridicamente corretta? | ✅ Sì / ⚠️ Parziale / ❌ No |
| Le fonti citate sono pertinenti? | ✅ Tutte / ⚠️ Alcune / ❌ Nessuna / 🚨 Fonti errate |
| Mancano norme importanti? | testo libero |
| Il sistema ha inventato qualcosa? | ✅ No / 🚨 Sì — cosa |
| Commento libero | testo libero |

---

## 5. Schema queries.jsonl aggiornato

Tre campi nuovi rispetto allo schema attuale, retrocompatibili con l'evaluator
esistente (vengono ignorati se non gestiti):

```jsonl
{
  "id": "pen_trib_001",
  "module": "pen_trib",
  "difficulty": "hard",
  "query": "...",
  "workspace": "default",
  "intent": "norma_lookup",
  "expected_source_ids": ["urn:nir:stato:decreto.legislativo:2000-03-10;74!vig=..."],
  "top_k": 10,
  "lawyer_verdict": "partial",
  "lawyer_notes": "manca art. 1 D.Lgs. 74 sul dolo specifico"
}
```

---

## 6. Metriche post-sessione

| Metrica | Calcolo | Cosa misura |
|---------|---------|-------------|
| `recall@10` | fonti attese ∩ fonti ritrovate / fonti attese | copertura del corpus |
| `lawyer_pass_rate` | schede con verdict ≠ "no" / totale | qualità percepita |
| `hallucination_rate` | schede "sistema ha inventato = Sì" / totale | rischio Citation Contract |
| `missing_norm_rate` | schede con "mancano norme" non vuoto / totale | gap del corpus |

---

## 7. Ciclo di feedback

```
videocall
  → queries.jsonl (expected_source_ids da umano)
  → run_eval.py
  → pacchetto PDF/Doc
  → avvocato (valutazione asincrona)
  → queries.jsonl aggiornato (lawyer_verdict + lawyer_notes)
  → run_eval.py run4
  → delta rispetto a run3
```

Ogni sessione con l'avvocato produce un run numerato con metriche confrontabili.

---

## 8. Corpus richiesto (verifica pre-sessione)

Prima della videocall verificare che questi corpus siano indicizzati in `aiura_legal.chunks`:

| Corpus | URN | Stato |
|--------|-----|-------|
| D.Lgs. 74/2000 (reati tributari) | `urn:nir:stato:decreto.legislativo:2000-03-10;74` | ✅ mirrored |
| D.Lgs. 472/1997 (sanzioni amm.) | `urn:nir:stato:decreto.legislativo:1997-12-18;472` | ✅ mirrored |
| D.Lgs. 231/2001 (resp. enti) | `urn:nir:stato:decreto.legislativo:2001-06-08;231` | ⚠️ da verificare |
| TUIR DPR 917/1986 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917` | ✅ fetched |
| IVA DPR 633/1972 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1972-10-26;633` | ✅ fetched |
| Codice Penale RD 1930 | `urn:nir:stato:regio.decreto:1930-10-19;1398` | ✅ mirrored |
| c.p.p. DPR 447/1988 | `urn:nir:stato:decreto.del.presidente.della.repubblica:1988-09-22;447` | ✅ mirrored |

**Azione richiesta prima della videocall:** verificare D.Lgs. 231/2001 con
`db.chunks.countDocuments({fonte: {$regex: "231"}})` su `aiura_legal`.

---

## 9. Non incluso in questa sessione

- Giurisprudenza (Cassazione penale tributaria) — backlog M2
- Circolari Agenzia delle Entrate — backlog M2
- Prassi amministrativa — backlog M2
- Valutazione qualità del drafting (S4) — sessione separata
