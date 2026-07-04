# Prompt operativo — Rimozione rami morti e file non più utilizzati

> Come usare questo prompt: incollalo per intero in una sessione con
> accesso al filesystem del progetto AiUra LegalLab, a Bash/Grep e a git.
> Questa sessione **modifica ed elimina file** — crea sempre un branch
> dedicato (mai lavorare direttamente su `main` o sul branch di lavoro
> corrente dell'utente), non forzare mai push, e fai eseguire i test prima
> e dopo ogni batch di rimozioni. Se non sai su quale branch ti trovi,
> controllalo prima di iniziare.

---

## Contesto

AiUra LegalLab è un backend Python (FastAPI + agenti + retrieval ibrido) con
frontend React/TypeScript. Non ha tool di dead-code detection già
configurati (niente `vulture`/`deptry` in Python, niente `knip`/`ts-prune`
in frontend) — la verifica va fatta principalmente per lettura/grep
incrociato, non fidandosi ciecamente di un singolo tool automatico.

Il codice ha diverse zone con caricamento **dinamico non rilevabile da un
semplice grep sugli import Python/TS**: skill prompt (`.pi/skills/*.md`)
caricati per nome stringa, route FastAPI esposte via decoratori, pagine
frontend montate da un router, fixture pytest richiamate per nome. Un file
o una funzione possono sembrare "non referenziati" a un grep ingenuo e
invece essere vivi. Vedi la sezione "Falsi positivi noti" prima di
eliminare qualunque cosa.

## Obiettivo

Trovare ed eliminare in sicurezza:
- **Rami morti**: branch `if`/`else`, funzioni, parametri, flag mai
  raggiungibili nel percorso di produzione reale (non solo nei test).
- **File non più utilizzati**: moduli Python, componenti/hook React, script
  in `scripts/`, skill in `.pi/skills/` che non sono referenziati da nessun
  percorso vivo (app, CLI documentata, test che verificano comportamento
  reale — non un test orfano che testa codice morto).

Non è un obiettivo di questo prompt: refactoring, rinominazioni, o pulizia
di stile. Solo rimozione di cose morte.

## Metodologia — due fasi, mai eliminare al volo

### Fase 1 — Inventario (nessuna modifica al codice)

Per ogni candidato "morto", raccogli evidenza concreta prima di decidere:

1. **Grep incrociato**: cerca ogni riferimento al simbolo/file (import,
   chiamata, stringa literal per i casi dinamici — vedi sotto) in tutto il
   repo, `frontend/` incluso.
2. **Git blame/log**: `git log -1 --format=%ci -- <file>` — se il file è
   stato toccato negli ultimi giorni, trattalo con più cautela (potrebbe
   essere lavoro in corso, non morto). Non eliminare nulla modificato nelle
   ultime 2 settimane senza segnalarlo esplicitamente nel report invece di
   agire.
3. **Reachability reale, non solo test**: un percorso testato da un test
   ma mai raggiungibile dall'API/frontend in produzione è comunque un
   candidato forte a "morto" — ma verifica prima se è un'API pubblica
   dello script/libreria (es. endpoint REST esposto ma non ancora
   consumato dal frontend — potrebbe essere intenzionale, non morto).
4. Per i tool automatici (opzionali, solo come generatori di candidati,
   mai come verdetto finale):
   - Python: puoi installare `vulture` in un venv temporaneo
     (`pip install vulture && vulture aiura_legal/`) — alto tasso di falsi
     positivi su codice Pydantic/FastAPI, verifica ogni riga a mano.
   - Frontend: `npx ts-prune` o `npx knip` nella cartella `frontend/` —
     stesso principio, solo candidati da verificare.

Produci una tabella (vedi "Formato del report") PRIMA di toccare qualunque
file. Classifica ogni candidato: **ALTA confidenza** (nessun riferimento
trovato in nessuna forma, nessuna modifica recente, nessun dubbio) / **MEDIA**
(sembra morto ma con qualche dubbio, es. potrebbe essere un entry point
documentato) / **BASSA** (probabilmente vivo, scartalo dalla lista).

### Fase 2 — Esecuzione (solo su candidati ALTA confidenza)

1. Crea un branch dedicato: `git checkout -b chore/rimozione-codice-morto`.
2. Esegui la suite di test PRIMA di iniziare (`pytest tests/ -v` e, se
   pertinente, `npm run lint`/`npm run build` in `frontend/`) e salva
   l'esito come baseline.
3. Elimina in piccoli batch tematici (es. "un intero modulo alla volta",
   non "tutto insieme") — un commit per batch, messaggio che elenca cosa e
   perché ("rimuove X: nessun riferimento trovato, ultima modifica Y,
   verificato che Z non lo richiama").
4. Dopo ogni batch: rilancia i test. Se qualcosa si rompe, il batch ha
   trovato un falso positivo — annulla quel singolo batch (`git revert` o
   `git reset` sul solo commit, non su tutto il branch) e sposta quella
   voce a "NON eliminato — falso positivo scoperto in Fase 2" nel report.
5. I candidati **MEDIA confidenza** NON vanno eliminati in questa sessione:
   finiscono nel report come proposta, non come azione eseguita.
6. Non fare mai `git push --force`, non toccare `main`. Se il branch è
   pronto, fermati e lascia che sia l'utente ad aprire la PR/mergiare —
   non farlo autonomamente.

## Falsi positivi noti — verifica SEMPRE prima di eliminare

- **`.pi/skills/*.md`**: non sono importati da Python, sono caricati per
  nome file/stringa a runtime. Prima di considerarne uno morto, grep per
  il suo nome (con e senza estensione `.md`) in tutto `aiura_legal/` —
  non solo `import`.
- **`aiura_legal/agents/analyst.py` — percorsi multipli**: `AnalystAgent`
  ha tre metodi di analisi (`analyze()` standard, `analyze_deep()` legacy
  a 2 fasi con skill `legal_analyst_fase1.md`/`legal_analyst_fase2.md`,
  `analyze_sequential()` — l'architettura corrente Sequential IQRAC a 4
  fasi documentata in CLAUDE.md). `analyze_deep()` è raggiungibile solo se
  un caller passa `mode="deep"` a `LegalOrchestrator.run()`/`req.mode`
  nell'API (`aiura_legal/api/app.py`). Verifica se il frontend
  (`frontend/src/hooks/useChat.ts`) invia mai `mode="deep"` in un percorso
  utente reale, o se resta solo in `req.mode` come default mai esercitato
  se non dai test (`tests/test_orchestrator.py`). Se è morto in
  produzione, elimina `analyze_deep()` **e** le due skill fase1/fase2 **e**
  il ramo `mode="deep"` in `orchestrator.py`/`app.py` insieme, non a metà —
  altrimenti lasci un percorso rotto raggiungibile ma non testato.
- **Endpoint FastAPI**: cercali per path stringa (`@router.post("/...")`),
  non per nome funzione — il frontend li chiama per URL, non per import
  Python.
- **Pagine/route frontend**: verifica il router centrale (dove sono
  registrate le route, tipo `App.tsx` o equivalente) oltre al semplice
  grep sugli import del componente — un componente puo' essere importato
  solo lì.
- **Fixture pytest** (`conftest.py`): richiamate per nome dalla firma dei
  test (`def test_x(mia_fixture):`), non da un `import` esplicito — grep
  per il nome della fixture come parametro, non come simbolo importato.
- **Script in `scripts/`**: non sono mai importati da `aiura_legal/` (sono
  entry point CLI). "Non referenziato da nient'altro" NON è prova di
  morte per questi — controlla invece se sono citati in
  `docs/wiki/`, `README.md`, `CLAUDE.md`, o in altri script come parte di
  una pipeline documentata. Gli script di migrazione/fix one-off
  (`scripts/fix_*.py`) hanno valore storico anche se non più necessari da
  rilanciare: se dubbi, proponili come "candidato a spostare in
  `scripts/_dev/`" (debito tecnico DT-3 già noto) invece di eliminarli, e
  chiedi conferma nel report invece di agire.
- **`docs/superpowers/specs/*.md`**: documentazione di decisioni di design
  storiche, non codice — non rientrano in questo prompt, non toccarle mai
  anche se descrivono feature poi cambiate.
- **`ontology/`, dati in `download/`, file generati (`*.pkl`, indici
  Qdrant/BM25)**: mai candidati a "codice morto" — sono dati/artefatti, non
  codice. Escludili a priori.

## Cosa NON toccare in nessun caso

- `.venv/`, `node_modules/`, `dist/`, `build/`, qualunque cartella generata.
- File di configurazione anche se sembrano ridondanti (`.env.example`,
  file di CI) — fuori scope, chiedi invece di eliminarli.
- Migrazioni/script one-off in `scripts/` (vedi sopra) — proponi, non
  eliminare.
- Qualunque file modificato nelle ultime 2 settimane (vedi Fase 1.2).
- Test — anche un test che sembra ridondante non va eliminato in questa
  sessione: se il codice che testa risulta morto ed eliminato, il test
  associato va rimosso nello stesso commit (non lasciarlo a testare nulla),
  ma non eliminare test di codice ancora vivo.

## Formato del report finale

1. **Tabella Fase 1** (prima di ogni azione): file/simbolo | tipo (ramo
   morto / file inutilizzato) | evidenza (comando+output) | ultima
   modifica git | confidenza (ALTA/MEDIA/BASSA).
2. **Eliminazioni eseguite** (solo ALTA confidenza): elenco commit con
   hash, cosa è stato rimosso, esito test prima/dopo.
3. **Falsi positivi scoperti in Fase 2**: cosa sembrava morto e non lo era,
   con la prova che lo ha smentito — utile per non ripetere l'errore in
   futuro.
4. **Candidati MEDIA confidenza non eliminati**: proposta esplicita,
   lasciata a giudizio dell'utente, con la ragione del dubbio.
5. **Branch finale**: nome branch, comando per l'utente per rivedere il
   diff (`git diff main...chore/rimozione-codice-morto`) — non aprire PR
   né mergiare autonomamente.
