# Pilot di valutazione Headroom per compressione context_budget

Data: 2026-06-28

## Contesto

[Headroom](https://github.com/headroomlabs-ai/headroom) (`pip install headroom-ai`) è un layer di compressione
per agenti AI: riduce i token che arrivano all'LLM comprimendo JSON, codice e testo (modello
`kompress-v2-base`, addestrato su "agentic traces"). Promette 60–95% di risparmio token a parità di
risposta.

AiUraLegalLab usa già [`ContextBudgetManager`](../../../aiura_legal/core/retrieval/context_budget.py) per
assemblare il research packet entro `n_ctx=8192` (LLM locale via LMStudio/Ollama): un numero fisso di slot
full-text + sommario per corpus, con troncamento token-based (`tiktoken`, `cl100k_base`).

**Obiettivo**: il truncamento crudo perde informazione (un chunk normativa troncato a 400 token può
tagliare a metà un comma rilevante). Vogliamo verificare se Headroom può comprimere semanticamente i chunk
(mantenendo il contenuto giuridicamente rilevante) entro lo stesso budget di token, invece di troncarli.

**Rischio principale**: `kompress-v2-base` non ha documentazione di supporto per l'italiano né per testo
giuridico specialistico. Una compressione che altera un numero di articolo, una data, un riferimento URN o
un estremo di sentenza rompe il Citation Contract (principio fondamentale del progetto: ogni citazione deve
restare grounded e verificabile). Per questo si procede con un **pilot di valutazione isolato**, non con
un'integrazione diretta.

## Perimetro

Questo spec copre **solo il pilot di valutazione**. Non modifica `context_budget.py` né alcun codice di
produzione. La decisione di integrare (o scartare) Headroom verrà presa dopo aver visto il report del pilot.

Fuori scope: integrazione MCP/proxy, compressione di tool output/log degli agenti Pi Skills, riduzione costi
su LLM cloud — idee da riconsiderare solo se il pilot conferma che la compressione è affidabile su testo
giuridico italiano.

## Componenti

### 1. `scripts/pilot_headroom.py`

Script CLI standalone che:

1. Estrae un campione di chunk reali da `aiura_legal_lab_db.chunks` (MongoDB), filtrati per
   `corpus in {normattiva, giurisprudenza, dottrina}` — campione configurabile via `--sample-size` (default
   50 per corpus).
2. Applica `headroom.compress()` a ciascun chunk con un budget di token equivalente a quello già definito in
   `ContextBudgetManager.BUDGETS` (400 tok normativa, 500 tok giurisprudenza, 200 tok dottrina).
3. Confronta testo compresso vs originale e produce gli artefatti del Gate 1 e Gate 2 (sotto).

Dipendenza: `pip install "headroom-ai[ml]"` aggiunta solo come extra opzionale (non in `pyproject.toml`
principale) finché il pilot non conferma l'adozione.

### 2. Gate 1 — Integrità testuale (deterministico)

Per ciascun chunk compresso, verifica con regex che i pattern critici presenti nell'originale siano ancora
presenti nel compresso:

- numero articolo: `Art\.\s*\d+`
- riferimenti URN normattiva: `urn:nir:[\w:.\-]+`
- date (formati `\d{1,2}/\d{1,2}/\d{4}`, `\d{4}-\d{2}-\d{2}`)
- estremi sentenza (numero/anno, es. `n\.\s*\d+/\d{4}`)
- marcatori di citazione nel research packet (`\[\d+\]`)

Output: tabella per corpus con % di chunk che preservano **tutti** i pattern critici rilevati
nell'originale, con elenco dei chunk falliti (diff originale/compresso) per ispezione manuale.

**Soglia di avanzamento al Gate 2**: ≥95% di integrità per corpus. Sotto soglia, il pilot si ferma e
riporta solo i risultati del Gate 1.

### 3. Gate 2 — Eval end-to-end (solo se Gate 1 passa)

- Branch isolato nello script pilot (flag `--use-headroom`) che sostituisce
  `ContextBudgetManager.budget_texts()` con l'output di Headroom durante l'assemblaggio del research packet,
  solo per la durata dello script — nessuna modifica a `context_budget.py`.
- Esegue `eval/run_eval.py` due volte sullo stesso sottoinsieme di query (es. da
  `tests/script_json/test_aiura_01.jsonl`, eventualmente filtrato con `--module`):
  - baseline: troncamento attuale (`ContextBudgetManager`)
  - sperimentale: compressione Headroom
- Confronta `pass_rate`, groundedness/citazioni corrette tra le due run, a parità di query e modulo.

### 4. Report finale

Markdown o JSON generato dallo script, con:

- % integrità testuale per corpus (Gate 1)
- pass_rate baseline vs Headroom (Gate 2, se eseguito)
- token medi risparmiati per corpus
- raccomandazione: procedere con integrazione reale / scartare / limitare a corpus meno sensibili
  (dottrina/prassi) dove il rischio di alterare una citazione diretta è minore

## Testing

Il pilot stesso è uno strumento di valutazione, non richiede test unitari propri oltre a una verifica
manuale che lo script gira end-to-end su un campione piccolo (`--sample-size 5`) prima del run completo.

## Decisione successiva

Solo dopo aver visto il report si decide se e come integrare Headroom in `context_budget.py`. Questa fase
non è coperta da questo spec.
