const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
  LevelFormat, Header, Footer, PageNumber, TableOfContents, PageBreak
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 100, bottom: 100, left: 120, right: 120 };
const CONTENT_W = 9026;

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial" })],
    spacing: { before: 360, after: 200 },
  });
}
function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial" })],
    spacing: { before: 280, after: 120 },
  });
}
function h3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text, bold: true, size: 24, font: "Arial" })],
    spacing: { before: 200, after: 100 },
  });
}
function para(text, opts) {
  opts = opts || {};
  return new Paragraph({
    children: [new TextRun(Object.assign({ text, size: 22, font: "Arial" }, opts))],
    spacing: { after: 100 },
  });
}
function mono(text) {
  return new Paragraph({
    children: [new TextRun({ text, size: 20, font: "Courier New", color: "1F497D" })],
    spacing: { after: 60 },
    indent: { left: 720 },
    shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
  });
}
function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, size: 22, font: "Arial" })],
    spacing: { after: 80 },
  });
}
function numbered(text) {
  return new Paragraph({
    numbering: { reference: "numbers", level: 0 },
    children: [new TextRun({ text, size: 22, font: "Arial" })],
    spacing: { after: 80 },
  });
}
function note(text) {
  return new Paragraph({
    children: [new TextRun({ text: "Nota: " + text, size: 20, font: "Arial", color: "595959", italics: true })],
    spacing: { after: 120 },
    indent: { left: 360 },
    border: { left: { style: BorderStyle.SINGLE, size: 6, color: "4472C4", space: 8 } },
  });
}
function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: 160 } });
}
function pageBreak() {
  return new Paragraph({ children: [new PageBreak()] });
}

function headerRow(cells, colWidths) {
  return new TableRow({
    children: cells.map(function(text, i) {
      return new TableCell({
        borders: borders,
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: "1F3864", type: ShadingType.CLEAR },
        margins: cellMargins,
        children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", size: 20, font: "Arial" })] })]
      });
    })
  });
}
function dataRow(cells, colWidths, shade) {
  return new TableRow({
    children: cells.map(function(text, i) {
      return new TableCell({
        borders: borders,
        width: { size: colWidths[i], type: WidthType.DXA },
        shading: { fill: shade ? "EBF0F8" : "FFFFFF", type: ShadingType.CLEAR },
        margins: cellMargins,
        children: [new Paragraph({ children: [new TextRun({ text: text || "", size: 20, font: "Arial" })] })]
      });
    })
  });
}
function makeTable(headers, rows, colWidths) {
  var tableRows = [headerRow(headers, colWidths)];
  rows.forEach(function(r, i) {
    tableRows.push(dataRow(r, colWidths, i % 2 === 0));
  });
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: tableRows
  });
}

var scripts = [
  {
    nome: "mirror_normattiva.py",
    categoria: "Setup / Dati",
    scopo: "Copia i 166.822 articoli normativi da legal_lab.normattiva_docs ad aiura_legal_lab_db.normattiva_docs e li suddivide in chunk indicizzabili.",
    quando: "Una tantum al primo setup e ogni volta che la sorgente legal_lab viene aggiornata con nuovi atti normativi.",
    dipendenze: "MongoDB (entrambi i database attivi e raggiungibili), .env con LEGALAGENTLAB_MONGODB_DATABASE=legal_lab",
    durata: "~10s per il mirror + ~20-30 min per il chunking (278k chunk)",
    comandi: [
      "python scripts/mirror_normattiva.py --workspace mio-studio",
      "python scripts/mirror_normattiva.py --workspace mio-studio --dry-run",
      "python scripts/mirror_normattiva.py --workspace mio-studio --skip-chunks",
    ],
    flags: "--dry-run  Conta i doc senza scrivere\n--skip-chunks  Solo mirror, non genera chunk\n--only-chunks  Solo chunking (mirror gia eseguito)\n--limit N  Limita a N doc (per test)\n--skip-formule  Esclude articoli di tipo formula"
  },
  {
    nome: "build_indexes.py",
    categoria: "Setup / Indici",
    scopo: "Costruisce gli indici BM25 (full-text keyword) e ChromaDB (vettoriale semantico) dai chunk in MongoDB. Indispensabile per il retrieval dell'app.",
    quando: "Dopo mirror_normattiva.py al primo setup. Da rieseguire quando i chunk normativi cambiano significativamente.",
    dipendenze: "mirror_normattiva.py completato, chunk presenti in MongoDB",
    durata: "~30 min con --testo-tipo normativo e modello MiniLM (CPU)",
    comandi: [
      "python scripts/build_indexes.py --workspace mio-studio --testo-tipo normativo",
      "python scripts/build_indexes.py --workspace mio-studio --skip-vector",
      "python scripts/build_indexes.py --workspace mio-studio --skip-bm25",
    ],
    flags: "--testo-tipo normativo  Solo chunk normativi, escluse formule (consigliato)\n--skip-vector  Salta ChromaDB, solo BM25 (~2 min)\n--skip-bm25  Salta BM25, solo ChromaDB\n--corpus normattiva  Filtra per corpus\n--fonte legge dlgs  Filtra per tipo atto\n--all-workspaces  Indicizza tutti i workspace (default: solo quello specificato)"
  },
  {
    nome: "build_graph.py",
    categoria: "Setup / Indici",
    scopo: "Costruisce il grafo giuridico NetworkX con nodi articolo e provvedimento e archi APPARTIENE_A, RINVIA, MODIFICA, ABROGA. Gli agenti lo usano per navigare le relazioni normative.",
    quando: "Dopo build_indexes.py al primo setup. Da rigenerare se cambiano in modo sostanziale i chunk normativi.",
    dipendenze: "Chunk normativi in MongoDB (mirror_normattiva.py completato)",
    durata: "~25 secondi per 278k chunk",
    comandi: [
      "python scripts/build_graph.py --workspace mio-studio",
      "python scripts/build_graph.py --workspace mio-studio --reset",
      "python scripts/build_graph.py --workspace mio-studio --dry-run",
    ],
    flags: "--reset  Elimina il grafo esistente prima di ricostruire\n--dry-run  Simula il build senza scrivere su disco\n--chunk-filter '{\"corpus\":\"normattiva\"}'  Filtra i chunk da includere"
  },
  {
    nome: "sync_jurisprudence.py",
    categoria: "Aggiornamento periodico",
    scopo: "Scarica le nuove sentenze dalle fonti pubbliche (Cassazione, TAR, Consiglio di Stato, Corte Costituzionale) e le salva in MongoDB. Usa un watermark: riprende dall'ultima data sincronizzata.",
    quando: "Settimanalmente (es. ogni lunedi mattina). Gestito automaticamente da weekly_jurisprudence_update.py.",
    dipendenze: "Connessione internet, MongoDB",
    durata: "~5-15 min per aggiornamento settimanale; ~2 ore per caricamento storico iniziale",
    comandi: [
      "python scripts/sync_jurisprudence.py",
      "python scripts/sync_jurisprudence.py --source cassazione",
      "python scripts/sync_jurisprudence.py --since 2024-01-01",
      "python scripts/sync_jurisprudence.py --initial-load",
    ],
    flags: "--source  Fonte specifica (cassazione, tar, consiglio_stato, corte_cost)\n--since  Data di partenza (YYYY-MM-DD)\n--initial-load  Caricamento storico 2 anni\n--dry-run  Simula senza scrivere"
  },
  {
    nome: "build_jurisprudence_indexes.py",
    categoria: "Aggiornamento periodico",
    scopo: "Indicizza in BM25 e ChromaDB le sentenze giurisprudenziali. Modalita incrementale: aggiunge solo i nuovi documenti senza reindicizzare tutto. Riprendibile in caso di interruzione.",
    quando: "Subito dopo sync_jurisprudence.py. Gestito automaticamente da weekly_jurisprudence_update.py.",
    dipendenze: "sync_jurisprudence.py completato, jurisprudence collection in MongoDB",
    durata: "~45-90 min al primo setup (249k sentenze); ~5-10 min per aggiornamenti settimanali",
    comandi: [
      "python scripts/build_jurisprudence_indexes.py --workspace mio-studio",
      "python scripts/build_jurisprudence_indexes.py --workspace mio-studio --rebuild",
      "python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione",
    ],
    flags: "--rebuild  Ricostruisce da zero (non incrementale)\n--organo  Filtra per organo (cassazione, tar, consiglio_stato, corte_cost)\n--checkpoint-every N  Salva indici ogni N batch (default 10)"
  },
  {
    nome: "build_jurisprudence_graph.py",
    categoria: "Aggiornamento periodico",
    scopo: "Costruisce il grafo sentenza verso norma con archi INTERPRETA, APPLICATA_IN, CITA. Arricchisce il grafo giuridico con i riferimenti giurisprudenziali per il ragionamento degli agenti.",
    quando: "Dopo build_jurisprudence_indexes.py. Consigliato anche settimanalmente insieme al workflow giurisprudenziale.",
    dipendenze: "jurisprudence collection popolata in MongoDB",
    durata: "~2-5 min",
    comandi: [
      "python scripts/build_jurisprudence_graph.py",
      "python scripts/build_jurisprudence_graph.py --rebuild",
    ],
    flags: "--rebuild  Ricostruisce il grafo da zero"
  },
  {
    nome: "weekly_jurisprudence_update.py",
    categoria: "Aggiornamento periodico",
    scopo: "Workflow completo settimanale: esegue in sequenza sync_jurisprudence, build_jurisprudence_indexes e stampa un riepilogo. Script principale da schedulare come task automatico.",
    quando: "Ogni settimana (es. cron del lunedi alle 02:00). Sostituisce i tre script precedenti in contesto automatizzato.",
    dipendenze: "Connessione internet, MongoDB, build_jurisprudence_indexes.py eseguito almeno una volta",
    durata: "~10-20 min (solo delta settimanale)",
    comandi: [
      "python scripts/weekly_jurisprudence_update.py --workspace mio-studio",
      "python scripts/weekly_jurisprudence_update.py --workspace mio-studio --dry-run",
    ],
    flags: "--dry-run  Simula senza scrivere"
  },
  {
    nome: "backfill_cassazione.py",
    categoria: "Backfill storico",
    scopo: "Scarica storicamente le sentenze della Cassazione per finestre mensili in parallelo. Supera il limite di paginazione del Solr di italgiure (~50k risultati per query). Riprendibile in caso di interruzione grazie al watermark.",
    quando: "Una tantum per caricare lo storico pluriennale della Cassazione. Non serve ripetere.",
    dipendenze: "Connessione internet, MongoDB",
    durata: "~12 min per 1 anno con concurrency 4; ~45 min per 5 anni",
    comandi: [
      "python scripts/backfill_cassazione.py --from 2020-01-01",
      "python scripts/backfill_cassazione.py --from 2024-01-01 --to 2024-12-31",
      "python scripts/backfill_cassazione.py --dry-run",
    ],
    flags: "--from  Data inizio (YYYY-MM-DD)\n--to  Data fine (default: ieri)\n--concurrency N  Mesi in parallelo (default 4)\n--dry-run  Conta senza scrivere"
  },
  {
    nome: "sync_prassi.py",
    categoria: "Aggiornamento periodico",
    scopo: "Scarica circolari e risoluzioni dell'Agenzia delle Entrate e le salva in prassi_docs. Particolarmente utile per studi con contenzioso tributario.",
    quando: "Periodicamente (mensile) per mantenere aggiornata la prassi amministrativa tributaria.",
    dipendenze: "Connessione internet, MongoDB",
    durata: "~5-20 min",
    comandi: [
      "python scripts/sync_prassi.py",
      "python scripts/sync_prassi.py --since 2020-01-01",
      "python scripts/sync_prassi.py --tipo circolare",
    ],
    flags: "--since  Data di partenza (YYYY-MM-DD)\n--tipo  circolare oppure risoluzione\n--dry-run  Simula senza scrivere"
  },
  {
    nome: "fetch_normattiva.py",
    categoria: "Dati / Aggiornamento",
    scopo: "Scarica atti specifici dall'API pubblica Normattiva e li salva in normattiva_docs. Utile per aggiungere singoli provvedimenti nuovi o non presenti nella sorgente.",
    quando: "Ad hoc, quando entra in vigore un nuovo atto o si vuole aggiungere una legge specifica non ancora presente.",
    dipendenze: "Connessione internet, MongoDB",
    durata: "Variabile (da pochi secondi per un singolo atto a ore per un anno intero)",
    comandi: [
      "python scripts/fetch_normattiva.py --urn urn:nir:stato:decreto.legislativo:2010-07-02;104",
      "python scripts/fetch_normattiva.py --tipo legge --anno 2024",
      "python scripts/fetch_normattiva.py --codici cc cp cpc cpp",
    ],
    flags: "--urn  URN Normattiva dell'atto\n--tipo  Tipo NIR (legge, decreto.legislativo, dpr...)\n--anno  Anno di emanazione\n--codici cc cp cpc cpp  Scarica i 4 codici maggiori\n--dry-run  Conta senza scrivere"
  },
  {
    nome: "run_tier2_worker.py",
    categoria: "Runtime",
    scopo: "Worker che consuma la coda di embedding (ingestion_queue) per processare i documenti caricati dall'avvocato tramite l'interfaccia web. Va tenuto in esecuzione in parallelo all'API.",
    quando: "Sempre attivo durante l'utilizzo dell'app. Avviare in un terminale separato insieme all'API.",
    dipendenze: "API in esecuzione, MongoDB attivo",
    durata: "Processo continuo (gira indefinitamente fino a Ctrl+C)",
    comandi: [
      "python scripts/run_tier2_worker.py",
      "python scripts/run_tier2_worker.py --once",
    ],
    flags: "--once  Un ciclo poi esci (utile per test)\n--poll-interval N  Secondi tra i cicli (default 5)\n--batch-size N  Documenti per ciclo (default 10)"
  },
  {
    nome: "wiki_bootstrap.py",
    categoria: "Utilita",
    scopo: "Popola la wiki con le pagine degli articoli normativi direttamente da normattiva_docs senza chiamare il LLM. Il contenuto iniziale e il testo verbatim dell'articolo; l'app lo arricchisce automaticamente dopo ogni query.",
    quando: "Una tantum dopo il primo setup, per avere una wiki di base. Le pagine vengono poi arricchite automaticamente dall'app.",
    dipendenze: "normattiva_docs popolato in MongoDB",
    durata: "~1-3 min per 500 pagine; ~10-20 min per il corpus completo",
    comandi: [
      "python scripts/wiki_bootstrap.py --workspace mio-studio",
      "python scripts/wiki_bootstrap.py --workspace mio-studio --limit 500",
    ],
    flags: "--limit N  Crea solo N pagine (utile per test)"
  },
  {
    nome: "wiki_export.py",
    categoria: "Utilita",
    scopo: "Esporta le pagine wiki da MongoDB come file Markdown su disco. Utile per backup, condivisione o integrazione con altri strumenti.",
    quando: "Ad hoc, per esportare la knowledge base in formato leggibile o per backup periodico.",
    dipendenze: "wiki_pages presenti in MongoDB",
    durata: "Pochi secondi",
    comandi: [
      "python scripts/wiki_export.py --workspace mio-studio",
      "python scripts/wiki_export.py --workspace mio-studio --clean",
    ],
    flags: "--out-dir  Cartella di output personalizzata\n--clean  Elimina l'export precedente prima di riscrivere"
  },
  {
    nome: "wiki_lint_cron.py",
    categoria: "Utilita",
    scopo: "Verifica la qualita delle pagine wiki (pagine vuote, titoli duplicati, link rotti). Progettato per essere schedulato come cron job di controllo qualita.",
    quando: "Periodicamente (es. settimanale) come check automatico della wiki.",
    dipendenze: "wiki_pages in MongoDB",
    durata: "Pochi secondi",
    comandi: [
      "python scripts/wiki_lint_cron.py --workspace mio-studio",
      "python scripts/wiki_lint_cron.py --workspace mio-studio --fail-on-issues",
    ],
    flags: "--fail-on-issues  Exit code 2 se ci sono problemi (utile in CI o task schedulati)"
  },
  {
    nome: "verify_indexes.py",
    categoria: "Diagnostica",
    scopo: "Verifica la correttezza degli indici BM25 e ChromaDB su un campione reale di documenti. Esegue smoke test con query legali e produce un report JSON con il verdetto.",
    quando: "Dopo build_indexes.py per confermare la correttezza degli indici. Utile anche per diagnosticare problemi di retrieval.",
    dipendenze: "build_indexes.py completato",
    durata: "~1-2 min",
    comandi: [
      "python scripts/verify_indexes.py",
      "python scripts/verify_indexes.py --smoke-queries \"responsabilita contrattuale\" \"locazione\"",
    ],
    flags: "--limit N  Campione di N chunk da verificare\n--workspace  Workspace da testare\n--smoke-queries  Query di test personalizzate\n--output  Percorso del report JSON"
  },
  {
    nome: "test_jurisprudence_retrieval.py",
    categoria: "Diagnostica",
    scopo: "Test end-to-end del retrieval giurisprudenziale: verifica MongoDB, ricerca ibrida BM25 e Vector, Citation Contract e link nel grafo sentenza verso norma.",
    quando: "Dopo build_jurisprudence_indexes.py per verificare che le sentenze siano recuperabili correttamente.",
    dipendenze: "build_jurisprudence_indexes.py completato",
    durata: "~1-2 min",
    comandi: [
      "python scripts/test_jurisprudence_retrieval.py --workspace mio-studio",
      "python scripts/test_jurisprudence_retrieval.py --workspace mio-studio --verbose",
    ],
    flags: "--verbose  Output dettagliato per ogni query di test"
  },
  {
    nome: "run_query_suite.py",
    categoria: "Valutazione qualita",
    scopo: "Esegue una suite di query da file JSONL sull'API e salva un report Markdown per ogni risposta. Permette di misurare la qualita delle risposte su un insieme predefinito di domande legali.",
    quando: "Ad hoc, per valutare le risposte del sistema prima di aggiornamenti importanti o per benchmark periodici.",
    dipendenze: "API in esecuzione su porta 8765",
    durata: "Variabile (dipende dal numero di query e dalla velocita del LLM)",
    comandi: [
      "python scripts/run_query_suite.py",
      "python scripts/run_query_suite.py --jsonl tests/queries.jsonl --workspace mio-studio",
    ],
    flags: "--jsonl  File JSONL con le query di test\n--workspace  Workspace da usare\n--out-dir  Cartella di output dei report"
  },
  {
    nome: "visualize_graph.py",
    categoria: "Analisi e visualizzazione",
    scopo: "Genera un file HTML con una visualizzazione interattiva del grafo sentenza verso norma. Apri il file nel browser per esplorare visivamente le relazioni giurisprudenziali.",
    quando: "Ad hoc, per analisi visive del grafo o presentazioni allo studio.",
    dipendenze: "build_jurisprudence_graph.py completato, pyvis installato",
    durata: "Pochi secondi",
    comandi: [
      "python scripts/visualize_graph.py",
      "python scripts/visualize_graph.py --top-norme 20 --sentenze-per-norma 8",
    ],
    flags: "--top-norme N  Mostra le N norme piu citate\n--sentenze-per-norma N  Numero massimo di sentenze per norma nel grafo"
  },
  {
    nome: "migrate_chunks_typing.py",
    categoria: "Migrazioni one-shot",
    scopo: "Aggiunge retroattivamente i campi di tipizzazione (corpus, fonte, testo_tipo) ai chunk esistenti che ne sono privi. Script di migrazione per allineare dati storici.",
    quando: "Una tantum, solo se esistono chunk creati prima dell'introduzione della tipizzazione (versioni precedenti del sistema).",
    dipendenze: "MongoDB con chunk pre-esistenti",
    durata: "~5-10 min",
    comandi: [
      "python scripts/migrate_chunks_typing.py",
      "python scripts/migrate_chunks_typing.py --dry-run",
    ],
    flags: "--dry-run  Mostra quanti chunk verrebbero modificati senza scrivere\n--workspace  Limita la migrazione a un workspace specifico"
  },
];

// Raggruppa per categoria
var categoryOrder = [
  { key: "Setup / Dati",               title: "3.1  Setup — Dati normativi" },
  { key: "Setup / Indici",              title: "3.2  Setup — Indici e grafo" },
  { key: "Aggiornamento periodico",     title: "3.3  Aggiornamento periodico" },
  { key: "Backfill storico",            title: "3.4  Backfill storico" },
  { key: "Dati / Aggiornamento",        title: "3.5  Aggiornamento normativa ad hoc" },
  { key: "Runtime",                     title: "3.6  Script runtime" },
  { key: "Diagnostica",                 title: "3.7  Diagnostica e test" },
  { key: "Valutazione qualita",         title: "3.8  Valutazione qualita" },
  { key: "Utilita",                     title: "3.9  Utilita" },
  { key: "Analisi e visualizzazione",   title: "3.10 Analisi e visualizzazione" },
  { key: "Migrazioni one-shot",         title: "3.11 Migrazioni one-shot" },
];

var scriptBlocks = [];
categoryOrder.forEach(function(cat) {
  var catScripts = scripts.filter(function(s) { return s.categoria === cat.key; });
  if (catScripts.length === 0) return;
  scriptBlocks.push(h2(cat.title));

  catScripts.forEach(function(s) {
    scriptBlocks.push(h3(s.nome));
    scriptBlocks.push(makeTable(
      ["Campo", "Dettaglio"],
      [
        ["Scopo", s.scopo],
        ["Quando eseguire", s.quando],
        ["Dipendenze", s.dipendenze],
        ["Durata stimata", s.durata],
      ],
      [2000, 7026]
    ));
    scriptBlocks.push(spacer());
    scriptBlocks.push(para("Comandi:", { bold: true }));
    s.comandi.forEach(function(cmd) { scriptBlocks.push(mono(cmd)); });
    if (s.flags) {
      scriptBlocks.push(spacer());
      scriptBlocks.push(para("Flag principali:", { bold: true }));
      s.flags.split('\n').forEach(function(line) {
        var parts = line.split('  ');
        scriptBlocks.push(new Paragraph({
          numbering: { reference: "bullets", level: 0 },
          children: [
            new TextRun({ text: parts[0] + "  ", size: 20, font: "Courier New", bold: true, color: "1F497D" }),
            new TextRun({ text: parts.slice(1).join("  "), size: 20, font: "Arial" }),
          ],
          spacing: { after: 60 },
        }));
      });
    }
    scriptBlocks.push(spacer());
  });
});

var children = [
  // COPERTINA
  new Paragraph({ children: [new TextRun("")], spacing: { after: 2000 } }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "AiUra LegalLab", bold: true, size: 56, font: "Arial", color: "1F3864" })],
    spacing: { after: 240 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Manuale degli Script di Manutenzione", bold: true, size: 36, font: "Arial", color: "2E75B6" })],
    spacing: { after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Guida operativa per l'amministratore del sistema", size: 26, font: "Arial", color: "7F7F7F", italics: true })],
    spacing: { after: 120 },
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: "Versione 1.0  —  Giugno 2026", size: 22, font: "Arial", color: "7F7F7F" })],
    spacing: { after: 2400 },
  }),
  pageBreak(),

  // INDICE
  new TableOfContents("Indice", { hyperlink: true, headingStyleRange: "1-2" }),
  pageBreak(),

  // 1. INTRODUZIONE
  h1("1. Introduzione"),
  para("Questo documento descrive tutti gli script di manutenzione di AiUra LegalLab: scopo, quando eseguirli e comandi disponibili. Destinatari: il responsabile tecnico dello studio che amministra il sistema."),
  para("AiUra LegalLab e' un sistema multi-agente di ricerca legale che combina retrieval ibrido (BM25 + ChromaDB), un grafo giuridico NetworkX e un LLM locale (qwen2.5-7b via LM Studio) per rispondere a quesiti normativi e giurisprudenziali con citazione delle fonti."),
  spacer(),

  h2("1.1  Prerequisiti di sistema"),
  bullet("MongoDB in esecuzione su localhost:27017"),
  bullet("Python 3.11+ con virtualenv attivato (.venv\\Scripts\\activate)"),
  bullet("LM Studio con modello qwen2.5-7b-instruct su porta 1234"),
  bullet("Node.js (per il frontend Vite)"),
  bullet("Connessione internet per gli script di sincronizzazione dati"),
  spacer(),

  h2("1.2  Database MongoDB"),
  makeTable(
    ["Database", "Descrizione", "Modificabile"],
    [
      ["legal_lab", "Sorgente normattiva READ-ONLY (LegalAgentLab originale)", "No — mai scrivere"],
      ["aiura_legal_lab_db", "Database principale AiUra (chunks, jurisprudence, wiki, history...)", "Si"],
    ],
    [2500, 4400, 2126]
  ),
  spacer(),

  h2("1.3  Ordine di setup al primo avvio"),
  numbered("mirror_normattiva.py  —  copia e chunking della normativa (166k articoli)"),
  numbered("build_indexes.py  —  indici BM25 + ChromaDB per la normativa"),
  numbered("build_graph.py  —  grafo normativo (nodi articolo, archi rinvio)"),
  numbered("backfill_cassazione.py  —  storico sentenze Cassazione (opzionale, consigliato)"),
  numbered("build_jurisprudence_indexes.py  —  indici BM25 + ChromaDB per la giurisprudenza"),
  numbered("build_jurisprudence_graph.py  —  grafo sentenza → norma"),
  spacer(),
  note("Gli script di setup richiedono in totale 2-4 ore alla prima esecuzione. Gli aggiornamenti successivi sono molto piu rapidi."),
  pageBreak(),

  // 2. AVVIO SISTEMA
  h1("2. Avvio del sistema"),
  para("Per avviare AiUra LegalLab servono tre terminali separati, da aprire nell'ordine indicato:"),
  spacer(),
  makeTable(
    ["Terminale", "Comando", "Indirizzo"],
    [
      ["1 — API Backend (FastAPI)", "python -m aiura_legal.api", "http://127.0.0.1:8765"],
      ["2 — Worker Embedding", "python scripts/run_tier2_worker.py", "(processo background)"],
      ["3 — Frontend (Vite)", "cd frontend && npm run dev", "http://localhost:5173"],
    ],
    [2800, 3600, 2626]
  ),
  spacer(),
  note("LM Studio deve essere gia in esecuzione con il modello caricato prima di avviare il Backend API. MongoDB si avvia automaticamente come servizio Windows."),
  spacer(),
  para("Aprire il browser su http://localhost:5173 per accedere all'interfaccia."),
  pageBreak(),

  // 3. RIFERIMENTO SCRIPT
  h1("3. Riferimento completo degli script"),
].concat(scriptBlocks).concat([
  pageBreak(),

  // 4. CALENDARIO
  h1("4. Calendario di manutenzione consigliato"),
  spacer(),

  h2("4.1  Setup una tantum (primo avvio)"),
  makeTable(
    ["Ordine", "Script", "Durata stimata"],
    [
      ["1", "mirror_normattiva.py --workspace mio-studio", "~30 min"],
      ["2", "build_indexes.py --workspace mio-studio --testo-tipo normativo", "~30 min"],
      ["3", "build_graph.py --workspace mio-studio", "~1 min"],
      ["4", "backfill_cassazione.py --from 2020-01-01 (opzionale)", "~45 min"],
      ["5", "build_jurisprudence_indexes.py --workspace mio-studio", "~90 min"],
      ["6", "build_jurisprudence_graph.py", "~5 min"],
    ],
    [800, 5526, 2700]
  ),
  spacer(),

  h2("4.2  Aggiornamento settimanale (ogni lunedi)"),
  makeTable(
    ["Script", "Cosa fa", "Durata"],
    [
      ["weekly_jurisprudence_update.py --workspace mio-studio", "Sync nuove sentenze + re-index incrementale", "~15 min"],
      ["sync_prassi.py (se utile per lo studio)", "Nuove circolari e risoluzioni AdE", "~10 min"],
      ["wiki_lint_cron.py --workspace mio-studio", "Verifica qualita wiki", "~1 min"],
    ],
    [3800, 3126, 2100]
  ),
  spacer(),

  h2("4.3  Aggiornamento mensile (normativa)"),
  note("Normattiva.it viene aggiornato continuamente. Si consiglia di rieseguire mirror_normattiva.py + build_indexes.py ogni mese oppure quando entra in vigore una norma rilevante per lo studio."),
  mono("python scripts/mirror_normattiva.py --workspace mio-studio"),
  mono("python scripts/build_indexes.py --workspace mio-studio --testo-tipo normativo"),
  mono("python scripts/build_graph.py --workspace mio-studio --reset"),
  spacer(),
  pageBreak(),

  // 5. DIAGNOSTICA
  h1("5. Diagnostica e risoluzione problemi"),
  spacer(),

  h2("5.1  Verifica stato indici"),
  mono("python scripts/verify_indexes.py"),
  mono("python scripts/test_jurisprudence_retrieval.py --workspace mio-studio"),
  spacer(),

  h2("5.2  Errori comuni"),
  makeTable(
    ["Sintomo", "Causa", "Soluzione"],
    [
      ["pickle data was truncated", "bm25.pkl corrotto (interruzione durante salvataggio)", "Eliminare bm25.pkl e rieseguire build_indexes.py"],
      ["IndexKeySpecsConflict", "Indice MongoDB gia esistente con opzioni diverse", "mirror_normattiva.py fa drop automatico degli indici"],
      ["ChromaDB > 100%", "Run precedente non pulito, delete_collection non svuota disco", "Eliminare workspaces/mio-studio/indices/chromadb/ e ricostruire"],
      ["Sorgente non raggiungibile", "LEGALAGENTLAB_MONGODB_DATABASE errato in .env", "Verificare che .env abbia LEGALAGENTLAB_MONGODB_DATABASE=legal_lab"],
      ["Nessuna giurisprudenza nelle fonti", "build_jurisprudence_indexes.py non eseguito", "Eseguire build_jurisprudence_indexes.py --workspace mio-studio"],
      ["App non risponde", "API non avviata o LM Studio non in esecuzione", "Verificare i 3 terminali e che LM Studio abbia il modello caricato"],
    ],
    [2500, 2900, 3626]
  ),
  spacer(),

  h2("5.3  Rebuild completo degli indici"),
  para("Se il sistema e' in uno stato inconsistente, per ripartire da zero:"),
  mono("Remove-Item -Recurse -Force workspaces\\mio-studio\\indices"),
  mono("python scripts/build_indexes.py --workspace mio-studio --testo-tipo normativo"),
  mono("python scripts/build_graph.py --workspace mio-studio"),
  mono("python scripts/build_jurisprudence_indexes.py --workspace mio-studio --rebuild"),
  mono("python scripts/build_jurisprudence_graph.py --rebuild"),
  spacer(),
  note("Il rebuild completo richiede circa 2-3 ore. L'app e' inutilizzabile durante il processo."),
]);

var doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0,
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "2E75B6", space: 4 } } } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "1F497D" },
        paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1418, right: 1134, bottom: 1418, left: 1134 },
      },
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 8 } },
          children: [new TextRun({ text: "AiUra LegalLab  —  Manuale Script di Manutenzione", size: 18, font: "Arial", color: "7F7F7F" })],
        })
      ] }),
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 8 } },
          children: [
            new TextRun({ text: "Pagina ", size: 18, font: "Arial", color: "7F7F7F" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "Arial", color: "7F7F7F" }),
            new TextRun({ text: " di ", size: 18, font: "Arial", color: "7F7F7F" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 18, font: "Arial", color: "7F7F7F" }),
          ],
        })
      ] }),
    },
    children: children,
  }],
});

var outPath = "C:/project/AiUraLegalLab/docs/manuale_script.docx";
Packer.toBuffer(doc).then(function(buf) {
  fs.writeFileSync(outPath, buf);
  console.log("OK: " + outPath);
}).catch(function(err) {
  console.error("ERRORE:", err);
  process.exit(1);
});
