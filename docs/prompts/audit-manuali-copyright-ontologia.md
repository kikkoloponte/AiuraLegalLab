# Prompt di audit — Applicabilità strategia "ontologia + fonti aperte" ai manuali coperti da copyright

> Come usare questo prompt: incollalo per intero in una sessione con
> accesso al filesystem del progetto AiUra LegalLab (Read/Grep/Bash — es.
> Claude Code). Non è pensato per una chat senza accesso al repo: ogni
> verdetto richiede di leggere file reali del progetto. Rilancialo quando
> serve rivalutare la strategia (es. dopo mesi di sviluppo, o prima di
> decidere se costruire l'entità Manuale descritta al §3).

---

## Contesto

I manuali commerciali di diritto (es. Trabucchi, Torrente, Fiandaca-Musco)
sono la fonte dottrinale più autorevole per l'interpretazione giuridica,
ma sono coperti da copyright: non possono essere digitalizzati e inseriti
in una knowledge base.

È stata proposta una strategia per costruire comunque una KB dottrinale
legale, efficace e navigabile, spostando il focus da "copiare i testi" a
"mappare i concetti":

1. **Separare l'ontologia (struttura) dai dati (contenuto).** L'ontologia
   modella come i giuristi ragionano (classi come `Tesi_Dottrinale`,
   `Orientamento_Interpretativo`, relazioni come `ha_argomentazione_principale`),
   non copia le parole di nessuno.
2. **Sostituire i manuali privati con fonti aperte**: giurisprudenza
   pubblica (le sentenze riassumono spesso la dottrina nelle motivazioni),
   relazioni dell'Ufficio del Massimario, riviste giuridiche open access,
   tesi di dottorato in repository universitari aperti, atti parlamentari
   e relazioni illustrative.
3. **Tecnica del metadato per i manuali specifici**: quando un utente
   chiede cosa dice un manuale specifico, la KB contiene solo l'entità
   bibliografica (titolo, autore, anno) collegata all'istituto giuridico
   che tratta, più al massimo una brevissima citazione tra virgolette (ex
   art. 70 L. 633/1941) — mai il testo della pagina. La KB funziona da
   super-indice: l'utente scopre *dove* si parla di un concetto, poi va a
   sfogliare il libro fisico.
4. **Architettura**: fonti aperte → estrazione concetti via NLP/LLM →
   mappa concettuale dell'ontologia (OWL/RDF) → navigazione utente, con i
   metadati dei manuali coperti agganciati sullo stesso grafo; i concetti
   estratti si collegano agli articoli di Normattiva via standard NIR/URN.

Il tuo compito è verificare, **con evidenza concreta letta nel codice**,
quanto di questa strategia è già realizzato nel progetto AiUra LegalLab,
quanto manca, e se ci sono rischi legali nell'esistente.

## Regola trasversale

Ogni verdetto deve citare il file/riga o il comando eseguito che lo
supporta. Non scrivere "sembra a posto" senza aver letto il file
rilevante. Se durante l'audit trovi un rischio legale concreto — es. testo
integrale di un manuale commerciale trovato in un chunk, in un file
scaricato, o in un campo dell'ontologia — segnalalo come **BLOCKER** in
cima al report, prima di qualunque altra sezione.

Non implementare nulla. Questo è un audit, non un design né una sessione
di scrittura codice: se emergono gap che vale la pena colmare, il report
si ferma a suggerirli come prossimo passo, senza scriverli.

---

## §1 — Separazione ontologia/dati

**Domanda:** le strutture esistenti (ontologia TTL, registro istituti
giuridici, nodi del grafo) modellano solo concetti astratti (classi,
proprietà, relazioni) o contengono, per errore, testo copiato da fonti
protette?

**Da controllare:**
- Leggi `ontology/legal_kb_ontology.ttl` per intero: le classi/proprietà
  sono astratte o contengono stringhe lunghe che sembrano testo copiato?
- Leggi `aiura_legal/core/graph/istituti_models.py` e la collection
  `istituti_giuridici`: i campi testuali (es.
  `definizione_e_natura_giuridica.testo`) puntano a `source_mongo_id` di
  chunk già tracciati nella KB, o contengono testo incollato da fonte
  esterna non tracciata?
- Grep nel codice e nei dati (`ontology/`, `aiura_legal/`, eventuali
  export/dump) per nomi di manuali/autori noti (Trabucchi, Torrente,
  Mantovani, Fiandaca-Musco, Cian-Trabucchi, ecc.) per escludere presenze
  accidentali di materiale protetto.

**Verdetto:** ✅ coperto / 🟡 parziale / ❌ mancante — con evidenza
(file:riga o comando+output).

## §2 — Fonti aperte al posto dei manuali privati

**Domanda:** le pipeline di ingestione dottrina/massimario attingono
davvero solo a fonti pubbliche e aperte, o esiste il rischio che materiale
coperto sia entrato nel corpus?

**Da controllare:**
- Leggi `scripts/sync_dottrina.py` e `scripts/upload_dottrina.py`: quali
  riviste/fonti sono configurate? Dichiarano esplicitamente licenza open
  access (es. Diritto Penale Contemporaneo, Sistema Penale)?
- Leggi `scripts/sync_massimario.py` e ispeziona un campione di
  `download/massimario/`: sono davvero relazioni dell'Ufficio del
  Massimario della Cassazione (pubbliche per natura istituzionale) o
  altro?
- Leggi `aiura_legal/ingestion/dottrina/metadata_extractor.py`: il
  riconoscimento riviste ha un fallback silenzioso che accetterebbe fonti
  non verificate come "genériche" senza controllo di provenienza?
- Ispeziona un campione di titoli in `download/dottrina/` e
  `download/massimario/`: qualcuno somiglia a un manuale commerciale
  invece che a una rivista/relazione istituzionale?

**Verdetto:** come sopra. Se trovi materiale sospetto, è un **BLOCKER**,
non una nota a margine.

## §3 — Tecnica del "metadato" per manuali protetti

**Domanda:** esiste già un'entità che rappresenti un manuale con solo
riferimento bibliografico + citazione breve, collegata agli istituti
giuridici?

**Da controllare:**
- Grep su `Manuale`, `OperaDottrinale`, `manuale` (case-insensitive) in
  `aiura_legal/`, `ontology/`, negli schemi Mongo/Pydantic e nel frontend.
- Confronta con lo schema TTL (`ontology/legal_kb_ontology.ttl`): esiste
  già una classe compatibile non ancora popolata di istanze?

**Verdetto:** a una prima ricognizione (2026-07-02) risulta ❌ mancante —
conferma o smentisci con evidenza aggiornata al momento in cui esegui
l'audit, non dare per scontato che sia ancora vero.

## §4 — Architettura: NLP da sentenze → ontologia → Normattiva (URN/NIR)

**Domanda:** cosa esiste già del flusso "estrai dottrina dalle
motivazioni delle sentenze pubbliche, collega ai concetti dell'ontologia,
ancora agli articoli via URN/NIR", e cosa manca?

**Da controllare:**
- Leggi `docs/superpowers/specs/2026-06-25-ontology-kb-neo4j-migration-design.md`,
  in particolare §3-4 (archi `PERTINENTE_A`/`RISOLVE`/`ANCORATA_A`) e §7
  (fuori scope dichiarato): sono ancora curati manualmente, o è stata
  aggiunta estrazione automatica da allora?
- Verifica lo stato della Fase 3 IQRAC (step `GIURISPRUDENZA` e
  `MASSIMARIO` separati, commit `c5af661`): estrae già riassunti
  dottrinali dalle motivazioni delle sentenze, o il gap descritto nello
  spec è ancora aperto?
- Verifica il collegamento URN/NIR esistente (propagazione del campo
  `urn` nei chunk, `mirror_normattiva`) come base già pronta per
  l'aggancio concetti-articoli.

**Verdetto:** come sopra.

---

## Formato del report

Produci:

1. **Eventuali BLOCKER** (se presenti), in cima, prima di tutto il resto.
2. **Tabella riassuntiva**, una riga per sezione:

   | Punto | Verdetto | Evidenza | Gap/Rischio |
   |---|---|---|---|
   | §1 Ontologia/dati | ... | file:riga | ... |
   | §2 Fonti aperte | ... | file:riga | ... |
   | §3 Metadato manuali | ... | file:riga | ... |
   | §4 Architettura NLP→ontologia→URN | ... | file:riga | ... |

3. **Elenco dei gap** con impatto stimato (basso/medio/alto).
4. **Al massimo una riga di prossimo passo suggerito per punto** — non un
   piano di implementazione. Se un gap merita di essere colmato, dillo
   esplicitamente che serve un brainstorming/design dedicato separato,
   non procedere a scriverlo qui.

Non includere una valutazione legale formale (parere di un avvocato sul
perimetro esatto del diritto di citazione ex art. 70 L. 633/1941): segnala
solo i rischi tecnici osservabili nel codice/dati, che potranno poi essere
sottoposti a un legale.
