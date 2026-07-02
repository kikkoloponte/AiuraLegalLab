# Audit "Manuali & Ontologia" — Design Spec

**Data:** 2026-07-02

## Contesto

I manuali commerciali di diritto (es. Trabucchi, Torrente) sono la fonte
dottrinale più autorevole per l'interpretazione giuridica, ma sono coperti
da copyright: non possono essere digitalizzati e inseriti nella KB.
È emersa una strategia per aggirare il problema spostando il focus da
"copiare i testi" a "mappare i concetti": separare l'ontologia (struttura
astratta del dibattito dottrinale) dai dati (contenuto), popolare la KB
solo con fonti pubbliche aperte, e — quando serve referenziare un manuale
specifico — inserire solo il metadato bibliografico più una citazione
breve (ex art. 70 L. 633/1941), mai il testo integrale.

Esplorando il progetto è emerso che gran parte di questa strategia **esiste
già** in AIURA, costruita per altre ragioni (retrieval Fase 2/3 IQRAC,
corpus=dottrina/massimario, registro istituti giuridici). Serve un modo
per verificare in modo ripetibile, ancorato a evidenze reali nel codice,
cosa è già coperto e cosa manca — in particolare il punto 3 (manuale come
metadato), che a una prima ricognizione risulta assente.

## Obiettivo

Produrre **un prompt di audit** (non uno skill runtime, non un'implementazione)
che un agente con accesso al filesystem del progetto possa eseguire per
verificare l'applicabilità della strategia "ontologia + fonti aperte" ad
AIURA, con particolare attenzione al problema del copyright sui manuali.

Il prompt è un artefatto a sé, pensato per essere rilanciato quando serve
rivalutare la strategia (es. dopo mesi di sviluppo, o prima di una
decisione go/no-go sull'aggiunta dell'entità Manuale) — non fa parte della
pipeline runtime degli agenti legali (`.pi/skills/`).

## Deliverable

File singolo: `docs/prompts/audit-manuali-copyright-ontologia.md`.

Contiene il testo del prompt, pronto da incollare in una sessione con
accesso al repo (Read/Grep/Bash). Il prompt istruisce l'agente a produrre
un **report di audit**, non a implementare nulla.

## Struttura del prompt

### Framing iniziale

Il prompt apre spiegando il contesto (la strategia dei 4 punti, il
problema del copyright sui manuali) e la regola trasversale:

> Ogni verdetto deve citare il file/riga o il comando eseguito che lo
> supporta. Non concludere "sembra a posto" senza aver letto il file
> rilevante. Se emerge un rischio legale concreto (es. testo di un manuale
> coperto trovato in un chunk o in un file scaricato), segnalalo come
> **blocker** in cima al report, non come nota a margine.

### §1 — Separazione ontologia/dati

**Domanda:** le strutture esistenti (ontologia TTL, registro istituti
giuridici, nodi del grafo) modellano solo concetti astratti (classi,
proprietà, relazioni) o contengono testo copiato da fonti protette?

**Da controllare:**
- `ontology/legal_kb_ontology.ttl` — lettura diretta dello schema
- `docs/superpowers/specs/2026-06-30-istituti-giuridici-crud-design.md` e
  `aiura_legal/core/graph/istituti_models.py` — verificare che i campi
  testuali (`definizione_e_natura_giuridica.testo`, ecc.) puntino a
  `source_mongo_id` di chunk della KB (fonti già tracciate) e non
  contengano incollato testo di manuali esterni
- grep su nomi di autori/manuali noti (Trabucchi, Torrente, Mantovani,
  Fiandaca-Musco, ecc.) nel codice e nei dati per escludere presenze
  accidentali

**Verdetto atteso:** ✅ coperto / 🟡 parziale / ❌ mancante, con evidenza.

### §2 — Fonti aperte al posto dei manuali privati

**Domanda:** le pipeline di ingestione dottrina/massimario attingono
davvero solo a fonti pubbliche e aperte, o esiste un rischio che materiale
coperto sia entrato nel corpus?

**Da controllare:**
- `scripts/sync_dottrina.py`, `scripts/upload_dottrina.py` — quali
  riviste/fonti sono configurate, verificare che dichiarino licenza
  open-access (es. Diritto Penale Contemporaneo, Sistema Penale)
- `scripts/sync_massimario.py` e contenuto di `download/massimario/` —
  confermare che siano relazioni dell'Ufficio del Massimario (pubbliche
  per natura istituzionale)
- `aiura_legal/ingestion/dottrina/metadata_extractor.py` — verificare che
  il riconoscimento riviste non abbia fallback silenziosi che accettano
  fonti non verificate
- ispezione a campione di `download/dottrina/` e `download/massimario/`
  per titoli che facciano sospettare manuali commerciali invece che
  riviste/relazioni istituzionali

**Verdetto atteso:** come sopra; se viene trovato materiale sospetto,
è un **blocker**.

### §3 — Tecnica del "metadato" per manuali protetti

**Domanda:** esiste già un'entità che rappresenti un manuale con solo
riferimento bibliografico + citazione breve, collegata agli istituti
giuridici?

**Da controllare:**
- grep su `Manuale`, `OperaDottrinale`, `manuale` nel codice
  (`aiura_legal/`, `ontology/`) e nello schema Mongo
- confronto con lo schema TTL (`ontology/legal_kb_ontology.ttl`) per
  vedere se esiste già una classe compatibile non ancora popolata

**Verdetto atteso:** a una prima ricognizione risulta ❌ mancante — il
prompt deve confermarlo o smentirlo con evidenza aggiornata, non assumerlo
dato per scontato.

### §4 — Architettura (NLP da sentenze → ontologia → Normattiva via URN/NIR)

**Domanda:** cosa esiste già del flusso "estrai dottrina dalle motivazioni
delle sentenze pubbliche, collega ai concetti dell'ontologia, ancora agli
articoli via URN/NIR" e cosa manca?

**Da controllare:**
- `docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md`
  §3-4 e §7 — stato di `PERTINENTE_A`/`RISOLVE`/`ANCORATA_A` (oggi curati
  manualmente, non estratti via NLP/LLM)
- Fase 3 IQRAC (`GIURISPRUDENZA`/`MASSIMARIO` come step separati,
  `c5af661`) — verificare se già estrae riassunti dottrinali dalle
  motivazioni o se il gap è ancora aperto
- collegamento URN/NIR esistente (`mirror_normattiva`, propagazione
  `urn` nei chunk) come base già pronta per l'aggancio

**Verdetto atteso:** come sopra.

### Formato output del report

Tabella riassuntiva (4 righe, una per sezione) con colonne: Punto |
Verdetto | Evidenza (file:riga o comando) | Gap/Rischio. Sotto la tabella,
elenco dei gap con impatto stimato. Il report **non** propone un piano di
implementazione dettagliato — al massimo una riga di prossimo passo
suggerito per punto, da approfondire con un brainstorming separato se
l'audit conferma che serve.

## Fuori scope

- Implementazione dell'entità Manuale/OperaDottrinale (segue solo se
  l'audit lo raccomanda, con un brainstorming/design dedicato)
- Automazione dell'estrazione NLP dalla giurisprudenza per popolare
  `PERTINENTE_A`/`RISOLVE`/`ANCORATA_A` (già esplicitamente rimandata dallo
  spec Neo4j §7)
- Valutazione legale formale (parere di un avvocato sul perimetro esatto
  del diritto di citazione ex art. 70 L. 633/1941) — il prompt segnala
  rischi tecnici osservabili nel codice/dati, non sostituisce un parere
  legale
