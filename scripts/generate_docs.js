const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, HeadingLevel, PageBreak,
} = require("docx");
const fs = require("fs");

const today = "3 giugno 2026";

const C = {
  blu:       "1F4E79", blucell: "D6E4F0", bluheader: "2E75B6",
  verde:     "1E7145", verdecell: "D9EDD4",
  rosso:     "C00000", rossocell: "FADADD",
  arancione: "C55A11", arancell:  "FCE4D6",
  grigio:    "F2F2F2", grigiosc:  "595959",
  bianco:    "FFFFFF", nero:      "000000",
  giallo:    "7D5A00", giallocell:"FFF3CD",
};

function hr(color) {
  return new Paragraph({
    spacing: { before: 120, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: color || C.bluheader } },
    children: [],
  });
}
function spacer(pts) {
  return new Paragraph({ spacing: { before: pts || 80, after: 0 }, children: [] });
}
function p(text, opts) {
  opts = opts || {};
  return new Paragraph({
    pageBreakBefore: opts.pageBreak || false,
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: opts.sb || 60, after: opts.sa || 60 },
    indent: opts.indent,
    children: [new TextRun({
      text: text, bold: opts.bold || false, italics: opts.italic || false,
      size: opts.size || 22, color: opts.color || C.nero, font: "Arial",
    })],
  });
}
function h1(text, pageBreak) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    pageBreakBefore: pageBreak || false,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 36, color: C.blu, font: "Arial" })],
  });
}
function h2(text) {
  return new Paragraph({
    spacing: { before: 200, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.bluheader } },
    children: [new TextRun({ text, bold: true, size: 26, color: C.bluheader, font: "Arial" })],
  });
}
function h3(text, color) {
  return new Paragraph({
    spacing: { before: 140, after: 60 },
    children: [new TextRun({ text, bold: true, size: 23, color: color || C.arancione, font: "Arial" })],
  });
}
function bullet(text, level) {
  level = level || 0;
  return new Paragraph({
    spacing: { before: 30, after: 30 },
    indent: { left: 720 * (level + 1), hanging: 360 },
    numbering: { reference: "bullets", level: level },
    children: [new TextRun({ text, size: 21, font: "Arial" })],
  });
}
function code(text) {
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    indent: { left: 720 },
    children: [new TextRun({ text, size: 19, font: "Courier New", color: "1F3864" })],
  });
}
function cell(text, fill, opts) {
  opts = opts || {};
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  return new TableCell({
    borders: { top: border, bottom: border, left: border, right: border },
    width: opts.w ? { size: opts.w, type: WidthType.DXA } : undefined,
    shading: { fill: fill, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text, bold: opts.bold || false, size: opts.size || 20,
        color: opts.color || C.nero, font: "Arial" })]
    })],
  });
}
function twoCol(label, value, dark) {
  const bg = dark ? "E8EEF4" : C.bianco;
  return new TableRow({ children: [
    cell(label, bg, { w: 3200, bold: true, size: 19 }),
    cell(value, bg, { w: 5760, size: 19 }),
  ]});
}
function statusRow(item, status, note, dark) {
  const bg = dark ? "E8EEF4" : C.bianco;
  const sc = status === "FATTO" ? C.verde : status === "IN CORSO" ? C.arancione :
             status === "PIANIFICATO" ? C.blu : C.grigiosc;
  const sb = status === "FATTO" ? C.verdecell : status === "IN CORSO" ? C.arancell :
             status === "PIANIFICATO" ? C.blucell : C.grigio;
  return new TableRow({ children: [
    cell(item, bg, { w: 4500, size: 19 }),
    cell(status, sb, { w: 1400, bold: true, color: sc, center: true, size: 19 }),
    cell(note, bg, { w: 3060, size: 18 }),
  ]});
}

// ── COPERTINA ────────────────────────────────────────────────────────────
function cover() {
  return [
    spacer(600),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 80 },
      children: [new TextRun({ text: "AiUra LegalLab", bold: true, size: 64, color: C.blu, font: "Arial" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 200 },
      children: [new TextRun({ text: "Documentazione tecnica", size: 30, color: C.grigiosc, font: "Arial" })] }),
    hr(C.bluheader),
    spacer(60),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: today, size: 22, color: C.grigiosc, font: "Arial", italics: true })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 60 },
      children: [new TextRun({ text: "Versione 0.1.0-dev — Uso interno riservato", size: 20, color: C.grigiosc, font: "Arial", italics: true })] }),
    spacer(300),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [2240, 2240, 2240, 2240],
      rows: [new TableRow({ children: [
        cell("166.822\nart. normativa", C.blucell, { w: 2240, bold: true, size: 22, color: C.blu, center: true }),
        cell("58.845\nsentenze", C.verdecell, { w: 2240, bold: true, size: 22, color: C.verde, center: true }),
        cell("6 / 10\nPASS Reviewer", C.verdecell, { w: 2240, bold: true, size: 22, color: C.verde, center: true }),
        cell("733.598\narchi nel grafo", C.blucell, { w: 2240, bold: true, size: 22, color: C.blu, center: true }),
      ]})],
    }),
  ];
}

// ── 1. ARCHITETTURA ──────────────────────────────────────────────────────
function sezArchitettura() {
  return [
    h1("1. Architettura di sistema", true),
    p("AiUra LegalLab è un sistema multi-agente per la ricerca e l'analisi legale con Citation Contract. " +
      "L'architettura è organizzata in tre layer: knowledge base, pipeline di retrieval e agenti LLM.", { sa: 80 }),

    h2("1.1 Schema a blocchi"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [4480, 4480],
      rows: [
        new TableRow({ children: [
          cell("KNOWLEDGE BASE\n──────────────\nMongoDB: aiura_legal_lab_db\n• normattiva_docs (166.822)\n• jurisprudence (58.845)\n• documents (studio avvocato)\n\nIndici locali (workspace)\n• BM25 (rank-bm25) ~700 MB\n• ChromaDB (vector) ~2.9 GB\n• Grafo NetworkX JSON",
               C.blucell, { w: 4480, size: 19, color: C.blu }),
          cell("PIPELINE AGENTI (FastAPI :8765)\n──────────────────────────────\nS0  Router      classifica intent\nS1  Clarifier   richiede chiarimenti\nS2  Retriever   BM25+Vector+Graph\nS3  Analyst     CoT con LLM\nS4  Drafter     genera atti legali\nS5  Reviewer    Citation Contract\nS6  Annotator   intelligence doc.\n\nWiki layer (fire-and-forget)",
               C.verdecell, { w: 4480, size: 19, color: C.verde }),
        ]}),
      ],
    }),
    spacer(100),

    h2("1.2 Flusso query standard (Workflow A)"),
    p("Client → POST /query → S0 routing → S2 retrieval → S3 analysis → S5 review → risposta", { italic: true, size: 20, color: C.grigiosc }),
    spacer(40),
    bullet("S0 Router: classifica l'intent tra NORMA_LOOKUP / GIURISPRUDENZA_SEARCH / FATTISPECIE_ANALYSIS / REDAZIONE_ATTO"),
    bullet("S2 HybridRetriever: esegue BM25 (keyword) + Vector (semantico) + CrossEncoder (reranking) con pesi adattivi per intent"),
    bullet("S3 Analyst: genera risposta CoT (Chain-of-Thought) citando solo fonti nel Research Packet"),
    bullet("S5 CitationReviewer: verifica che ogni URN/ID nella risposta sia presente nel Research Packet — blocca allucinazioni"),
    bullet("Wiki layer: archivia le risposte PASS in MongoDB.wiki_pages (fire-and-forget)"),
    spacer(80),

    h2("1.3 Flusso documento studio (Workflow B)"),
    p("POST /ingest → Tier1Pipeline → MongoDB.documents + chunks → POST /annotate → S6 AnnotatorAgent", { italic: true, size: 20, color: C.grigiosc }),
    spacer(40),
    bullet("Tier1Pipeline: estrae testo (PDF/DOCX/TXT) → anonimizza PII con LegalAnonymizer → salva in MongoDB → chunking sliding window"),
    bullet("PII Vault: entity_map cifrata in pii_vault — il testo in chiaro non esce mai dalla collection documents"),
    bullet("S6 Annotator: analizza sezioni del documento, rileva rischi legali, suggerisce correzioni con fonti grounded"),
    spacer(80),

    h2("1.4 Pesi retrieval per intent"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [3000, 1700, 1700, 1700, 860],
      rows: [
        new TableRow({ children: [
          cell("Intent", C.bluheader, { w: 3000, bold: true, color: C.bianco }),
          cell("BM25", C.bluheader, { w: 1700, bold: true, color: C.bianco, center: true }),
          cell("Vector", C.bluheader, { w: 1700, bold: true, color: C.bianco, center: true }),
          cell("Graph", C.bluheader, { w: 1700, bold: true, color: C.bianco, center: true }),
          cell("top-k", C.bluheader, { w: 860, bold: true, color: C.bianco, center: true }),
        ]}),
        new TableRow({ children: [
          cell("NORMA_LOOKUP", C.grigio, { w: 3000, size: 19 }),
          cell("0.60", C.grigio, { w: 1700, center: true, size: 19 }),
          cell("0.30", C.grigio, { w: 1700, center: true, size: 19 }),
          cell("0.10", C.grigio, { w: 1700, center: true, size: 19 }),
          cell("15", C.grigio, { w: 860, center: true, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("GIURISPRUDENZA_SEARCH", C.bianco, { w: 3000, size: 19 }),
          cell("0.20", C.bianco, { w: 1700, center: true, size: 19 }),
          cell("0.70", C.bianco, { w: 1700, center: true, size: 19 }),
          cell("0.10", C.bianco, { w: 1700, center: true, size: 19 }),
          cell("15", C.bianco, { w: 860, center: true, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("FATTISPECIE_ANALYSIS", C.grigio, { w: 3000, size: 19 }),
          cell("0.40", C.grigio, { w: 1700, center: true, size: 19 }),
          cell("0.50", C.grigio, { w: 1700, center: true, size: 19 }),
          cell("0.10", C.grigio, { w: 1700, center: true, size: 19 }),
          cell("20", C.grigio, { w: 860, center: true, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("REDAZIONE_ATTO", C.bianco, { w: 3000, size: 19 }),
          cell("0.50", C.bianco, { w: 1700, center: true, size: 19 }),
          cell("0.40", C.bianco, { w: 1700, center: true, size: 19 }),
          cell("0.10", C.bianco, { w: 1700, center: true, size: 19 }),
          cell("12", C.bianco, { w: 860, center: true, size: 19 }),
        ]}),
      ],
    }),
  ];
}

// ── 2. SORGENTI CONOSCENZA ───────────────────────────────────────────────
function sezSorgenti() {
  return [
    h1("2. Sorgenti della conoscenza", true),

    h2("2.1 Normattiva (read-only)"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [3200, 5760],
      rows: [
        twoCol("Origine", "normattiva.it — portale ufficiale Governo italiano", false),
        twoCol("Collezione MongoDB", "aiura_legal_lab_db.normattiva_docs (copiata da legal_lab)", true),
        twoCol("Volume", "166.822 articoli normativi", false),
        twoCol("Tipi documento", "normativo 150k | formula 13k | formula_ridondante 328 | formula_unica 221", true),
        twoCol("Campo testo", "text (campo principale)", false),
        twoCol("Identificatore", "urn (URN NIR univoco, es. urn:nir:stato:legge:...)", true),
        twoCol("Aggiornamento", "Manuale — script scripts/fetch_normattiva.py", false),
      ],
    }),
    spacer(100),

    h2("2.2 Giurisprudenza (scraped)"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [3200, 5760],
      rows: [
        twoCol("Origine", "Portali pubblici (Cassazione, TAR/CdS, Corte dei Conti)", false),
        twoCol("Collezione MongoDB", "aiura_legal_lab_db.jurisprudence", true),
        twoCol("Volume totale", "58.845 sentenze", false),
        twoCol("Cassazione", "58.408 — via Solr API diretta (httpx, no Playwright)", true),
        twoCol("TAR + Cons. Stato", "164 — via Liferay portlet (Playwright, 6 termini)", false),
        twoCol("Corte dei Conti", "267 — via CdcWebApi + download PDF reale", true),
        twoCol("Corte Costituzionale", "0 — bloccata da hCaptcha (servizio 2captcha necessario)", false),
        twoCol("Copertura anni", "2024 – 2026", true),
        twoCol("Aggiornamento", "Settimanale — scripts/sync_jurisprudence.py", false),
        twoCol("Grafo sentenza→norma", "58.845 nodi sentenza | 61.852 nodi norma | 733.598 archi", true),
      ],
    }),
    spacer(100),

    h2("2.3 Documenti studio avvocato"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [3200, 5760],
      rows: [
        twoCol("Origine", "Upload manuale dallo studio (POST /ingest o POST /jurisprudence/upload)", false),
        twoCol("Collezione MongoDB", "aiura_legal_lab_db.documents + chunks", true),
        twoCol("Volume attuale", "0 documenti (ambiente di test)", false),
        twoCol("Formati supportati", "PDF, DOCX, TXT", true),
        twoCol("Anonimizzazione PII", "Automatica — LegalAnonymizer con spaCy it_core_news_lg", false),
        twoCol("PII Vault", "aiura_legal_lab_db.pii_vault — entity_map cifrata AES", true),
      ],
    }),
    spacer(100),

    h2("2.4 Wiki (auto-generata)"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [3200, 5760],
      rows: [
        twoCol("Origine", "Risposte PASS del CitationReviewer (fire-and-forget)", false),
        twoCol("Collezione MongoDB", "aiura_legal_lab_db.wiki_pages (da creare)", true),
        twoCol("Meccanismo", "WikiEngine estrae concetti → WikiWriter → WikiStore", false),
        twoCol("Volume attuale", "109 pagine (da sessioni precedenti)", true),
        twoCol("Utilizzo", "Knowledge base cumulativa per query future", false),
      ],
    }),
  ];
}

// ── 3. INSTALLAZIONE ─────────────────────────────────────────────────────
function sezInstallazione() {
  return [
    h1("3. Installazione e configurazione", true),

    h2("3.1 Prerequisiti"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [2400, 2000, 4560],
      rows: [
        new TableRow({ children: [
          cell("Componente", C.bluheader, { w: 2400, bold: true, color: C.bianco }),
          cell("Versione minima", C.bluheader, { w: 2000, bold: true, color: C.bianco }),
          cell("Note", C.bluheader, { w: 4560, bold: true, color: C.bianco }),
        ]}),
        new TableRow({ children: [
          cell("Python", C.grigio, { w: 2400, size: 19 }),
          cell("3.11+", C.grigio, { w: 2000, size: 19, center: true }),
          cell("Testato con 3.14 su Windows", C.grigio, { w: 4560, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("MongoDB", C.bianco, { w: 2400, size: 19 }),
          cell("6.0+", C.bianco, { w: 2000, size: 19, center: true }),
          cell("Locale su porta 27017", C.bianco, { w: 4560, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("Node.js", C.grigio, { w: 2400, size: 19 }),
          cell("18+", C.grigio, { w: 2000, size: 19, center: true }),
          cell("Solo per generazione documenti Word (.docx)", C.grigio, { w: 4560, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("LMStudio / Ollama", C.bianco, { w: 2400, size: 19 }),
          cell("qualsiasi", C.bianco, { w: 2000, size: 19, center: true }),
          cell("LMStudio su :1234, Ollama su :11434 — configurabile in .env", C.bianco, { w: 4560, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("Playwright (browser)", C.grigio, { w: 2400, size: 19 }),
          cell("1.44+", C.grigio, { w: 2000, size: 19, center: true }),
          cell("Solo per scraping GA (Giustizia Amministrativa)", C.grigio, { w: 4560, size: 19 }),
        ]}),
      ],
    }),
    spacer(100),

    h2("3.2 Installazione Python"),
    h3("Clona e installa"),
    code("cd C:\\project\\AiUraLegalLab"),
    code("python -m venv .venv"),
    code(".venv\\Scripts\\activate"),
    code("pip install -e \".[dev]\""),
    code("python -m spacy download it_core_news_lg"),
    spacer(60),
    h3("Installa Playwright (per scraping GA)"),
    code("playwright install chromium"),
    spacer(100),

    h2("3.3 File .env — configurazione"),
    p("Crea o modifica il file .env nella root del progetto:", { sa: 60 }),
    code("# MongoDB — database unificato"),
    code("MONGODB_URI=mongodb://localhost:27017"),
    code("MONGODB_DATABASE=aiura_legal_lab_db"),
    code(""),
    code("# Normattiva (ora nello stesso DB)"),
    code("LEGALAGENTLAB_MONGODB_URI=mongodb://localhost:27017"),
    code("LEGALAGENTLAB_MONGODB_DATABASE=aiura_legal_lab_db"),
    code("LEGALAGENTLAB_CHUNKS_COLLECTION=normattiva_docs"),
    code("LEGALAGENTLAB_TEXT_FIELD=text"),
    code(""),
    code("# LLM Backend: 'lmstudio' oppure 'ollama'"),
    code("AIURA_LLM_BACKEND=lmstudio"),
    code("LMSTUDIO_BASE_URL=http://127.0.0.1:1234"),
    code("LMSTUDIO_MODEL=qwen2.5-7b-instruct"),
    code(""),
    code("# Ollama (alternativo)"),
    code("OLLAMA_BASE_URL=http://localhost:11434"),
    code("OLLAMA_MODEL_MAIN=qwen2.5:7b"),
    code(""),
    code("# Percorsi"),
    code("AIURA_WORKSPACES_PATH=C:/project/AiUraLegalLab/workspaces"),
    code("AIURA_API_HOST=127.0.0.1"),
    code("AIURA_API_PORT=8765"),
    spacer(100),

    h2("3.4 Node.js (per generazione documenti Word)"),
    code("npm install -g docx"),
    p("Per eseguire gli script .js, impostare NODE_PATH:", { sa: 40 }),
    code("$env:NODE_PATH=\"C:\\Users\\<utente>\\AppData\\Roaming\\npm\\node_modules\""),
    code("node scripts/generate_golden_v2.js"),
  ];
}

// ── 4. AVVIO PROCESSI ────────────────────────────────────────────────────
function sezAvvio() {
  return [
    h1("4. Avvio processi", true),

    h2("4.1 API principale"),
    p("Il server FastAPI espone tutti gli endpoint su porta 8765.", { sa: 60 }),
    code("# Avvio standard"),
    code(".venv\\Scripts\\activate"),
    code("python -m aiura_legal.api"),
    spacer(40),
    code("# Con reload automatico (sviluppo)"),
    code("uvicorn aiura_legal.api.app:app --host 127.0.0.1 --port 8765 --reload"),
    spacer(40),
    p("Verifica:", { bold: true, size: 20 }),
    code("curl http://127.0.0.1:8765/health"),
    code("# → {\"status\":\"ok\",\"mongodb\":true,\"ollama\":true}"),
    spacer(40),
    p("Documentazione Swagger interattiva:", { bold: true, size: 20 }),
    code("http://127.0.0.1:8765/docs"),
    spacer(100),

    h2("4.2 Sincronizzazione giurisprudenza"),
    h3("Aggiornamento settimanale (7 giorni)"),
    code("python scripts/sync_jurisprudence.py"),
    spacer(40),
    h3("Caricamento storico (2 anni — solo al primo setup)"),
    code("python scripts/sync_jurisprudence.py --initial-load"),
    spacer(40),
    h3("Singola fonte"),
    code("python scripts/sync_jurisprudence.py --source cassazione"),
    code("python scripts/sync_jurisprudence.py --source corte_conti"),
    code("python scripts/sync_jurisprudence.py --source tar"),
    spacer(40),
    p("Nota: Corte Costituzionale è esclusa automaticamente (hCaptcha). " +
      "Corte dei Conti scarica i PDF reali (~1.5s/sentenza).", { italic: true, size: 19, color: C.grigiosc }),
    spacer(100),

    h2("4.3 Costruzione indici di ricerca"),
    h3("Indicizza giurisprudenza (append — aggiunge solo i nuovi)"),
    code("python scripts/build_jurisprudence_indexes.py --workspace mio-studio"),
    spacer(40),
    h3("Filtra per organo"),
    code("python scripts/build_jurisprudence_indexes.py --workspace mio-studio --organo cassazione"),
    spacer(40),
    h3("Ricostruisci tutto da zero"),
    code("python scripts/build_jurisprudence_indexes.py --workspace mio-studio --rebuild"),
    spacer(40),
    h3("Indici normattiva (build_indexes.py — per normattiva_docs)"),
    code("python scripts/build_indexes.py --workspace mio-studio"),
    spacer(100),

    h2("4.4 Grafo sentenza → norma"),
    code("python scripts/build_jurisprudence_graph.py"),
    code("# Output: workspaces/jurisprudence_graph.json"),
    spacer(40),
    code("# Visualizzazione interattiva nel browser"),
    code("$env:NODE_PATH=\"...\\npm\\node_modules\""),
    code("python scripts/visualize_graph.py --top-norme 30"),
    code("# Output: workspaces/grafo_giurisprudenza.html"),
    spacer(100),

    h2("4.5 Update settimanale completo (sync + index)"),
    code("python scripts/weekly_jurisprudence_update.py --workspace mio-studio"),
    code("# Esegue in sequenza: sync (7 giorni) + indicizza solo i nuovi doc"),
    spacer(100),

    h2("4.6 Report knowledge base"),
    code("python scripts/_kb_report.py"),
    spacer(100),

    h2("4.7 Test retrieval end-to-end"),
    code("python scripts/test_jurisprudence_retrieval.py --workspace mio-studio --verbose"),
    p("Verifica: MongoDB counts, indici BM25/Vector, 5 query di test, Citation Contract, statistiche grafo.",
      { italic: true, size: 19, color: C.grigiosc }),
  ];
}

// ── 5. ENDPOINT API ──────────────────────────────────────────────────────
function sezEndpoint() {
  return [
    h1("5. Endpoint API", true),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [1200, 2600, 5160],
      rows: [
        new TableRow({ children: [
          cell("Metodo", C.bluheader, { w: 1200, bold: true, color: C.bianco }),
          cell("Path", C.bluheader, { w: 2600, bold: true, color: C.bianco }),
          cell("Descrizione", C.bluheader, { w: 5160, bold: true, color: C.bianco }),
        ]}),
        ...[
          ["GET",  "/health",                   "Stato sistema (MongoDB, LLM backend)", false],
          ["POST", "/query",                    "Query legale E2E: S0→S2→S3→S5 con Citation Contract", true],
          ["POST", "/ingest",                   "Upload documento studio (PDF/DOCX/TXT) → Tier1Pipeline", false],
          ["POST", "/annotate/{doc_id}",        "Avvia Document Intelligence S6 (asincrono, ritorna 202)", true],
          ["GET",  "/annotate/{doc_id}",        "Recupera risultato annotazione (queued/completed/error)", false],
          ["GET",  "/workspace",                "Lista workspace con statistiche", true],
          ["GET",  "/workspace/{name}",         "Dettagli workspace specifico", false],
          ["POST", "/workspace/{name}",         "Crea nuovo workspace", true],
          ["POST", "/jurisprudence/upload",     "Upload sentenza PDF dallo studio (sempre anonimizzata)", false],
          ["GET",  "/jurisprudence/sync",       "Stato last_sync per fonte", true],
          ["GET",  "/docs",                     "Swagger UI interattivo", false],
        ].map(([m, path, desc, dark]) => {
          const bg = dark ? "E8EEF4" : C.bianco;
          const mc = m === "GET" ? C.verde : m === "POST" ? C.blu : C.arancione;
          const mb = m === "GET" ? C.verdecell : m === "POST" ? C.blucell : C.arancell;
          return new TableRow({ children: [
            cell(m, mb, { w: 1200, bold: true, color: mc, center: true, size: 18 }),
            cell(path, bg, { w: 2600, size: 18 }),
            cell(desc, bg, { w: 5160, size: 18 }),
          ]});
        }),
      ],
    }),
  ];
}

// ── 6. BACKLOG ───────────────────────────────────────────────────────────
function sezBacklog() {
  return [
    h1("6. Backlog aggiornato", true),

    h2("6.1 Completato"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [4500, 1400, 3060],
      rows: [
        new TableRow({ children: [
          cell("Funzionalità", C.bluheader, { w: 4500, bold: true, color: C.bianco }),
          cell("Stato", C.bluheader, { w: 1400, bold: true, color: C.bianco, center: true }),
          cell("Note", C.bluheader, { w: 3060, bold: true, color: C.bianco }),
        ]}),
        statusRow("Architettura multi-agente (S0-S6)", "FATTO", "FastAPI + Orchestrator", false),
        statusRow("BM25 + Vector + CrossEncoder retrieval", "FATTO", "HybridRetriever con RRF fusion", true),
        statusRow("Citation Contract (CitationReviewer S5)", "FATTO", "Blocca allucinazioni", false),
        statusRow("MongoDB aiura_legal_lab_db (unificato)", "FATTO", "Migrazione da aiura_legal", true),
        statusRow("Normattiva 166.822 articoli", "FATTO", "Copiato da legal_lab", false),
        statusRow("Giurisprudenza Cassazione (58.408)", "FATTO", "Solr API, 2 anni storico", true),
        statusRow("Giurisprudenza TAR/CdS (164)", "FATTO", "6/10 termini Playwright", false),
        statusRow("Giurisprudenza Corte dei Conti (267)", "FATTO", "PDF reali via CdcWebApi", true),
        statusRow("Grafo sentenza→norma (733k archi)", "FATTO", "NetworkX JSON", false),
        statusRow("Visualizzazione grafo interattiva", "FATTO", "pyvis HTML", true),
        statusRow("Document Intelligence (S6 Annotator)", "FATTO", "Analisi rischio per sezione", false),
        statusRow("Wiki layer (auto-generazione)", "FATTO", "WikiEngine fire-and-forget", true),
        statusRow("PII Vault + anonimizzazione", "FATTO", "AES cifrato", false),
        statusRow("Golden Test Set v2 (con giurisprudenza)", "FATTO", "6/10 PASS, 10/10 fonti giurisp.", true),
      ],
    }),
    spacer(100),

    h2("6.2 In corso / prossimi sprint"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [4500, 1400, 3060],
      rows: [
        new TableRow({ children: [
          cell("Funzionalità", C.bluheader, { w: 4500, bold: true, color: C.bianco }),
          cell("Stato", C.bluheader, { w: 1400, bold: true, color: C.bianco, center: true }),
          cell("Note", C.bluheader, { w: 3060, bold: true, color: C.bianco }),
        ]}),
        statusRow("Frontend web (React/Vue)", "PIANIFICATO", "Vedi sezione 7", false),
        statusRow("Corte Costituzionale scraper", "PIANIFICATO", "Richiede servizio 2captcha", true),
        statusRow("TAR — 4 termini mancanti (annullamento, accesso...)", "PIANIFICATO", "Fix timeout Playwright", false),
        statusRow("Caricamento documenti studio reali", "PIANIFICATO", "POST /ingest con PDF avvocato", true),
        statusRow("Cron settimanale automatico", "PIANIFICATO", "weekly_jurisprudence_update.py", false),
        statusRow("Autenticazione API (JWT/API key)", "PIANIFICATO", "Multi-tenant per più studi", true),
        statusRow("Export wiki in PDF/DOCX", "PIANIFICATO", "scripts/wiki_export.py esiste", false),
        statusRow("Dashboard metriche (Reviewer pass rate, tempi)", "PIANIFICATO", "Monitoring operativo", true),
      ],
    }),
  ];
}

// ── 7. FRONTEND ──────────────────────────────────────────────────────────
function sezFrontend() {
  return [
    h1("7. Frontend — Roadmap", true),
    p("Il sistema è oggi accessibile solo via API REST (Swagger su /docs). " +
      "La prossima fase introduce un'interfaccia web per l'avvocato.", { sa: 80 }),

    h2("7.1 Funzionalità prioritarie (MVP)"),
    bullet("Chat legale — input query + risposta strutturata con fonti citate e colorate"),
    bullet("Visualizzazione Research Packet — tabella fonti con snippet, score e link"),
    bullet("Upload documento — drag & drop PDF con stato anonimizzazione e progress bar"),
    bullet("Workspace selector — switch tra studi diversi (multi-tenant)"),
    bullet("Reviewer badge — indicatore visivo PASS/FAIL/RE_RETRIEVAL per ogni risposta"),
    spacer(80),

    h2("7.2 Funzionalità secondarie"),
    bullet("Wiki viewer — naviga le pagine auto-generate per topic"),
    bullet("Grafo interattivo — embed del grafo sentenza→norma pyvis"),
    bullet("Cronologia query — storico per workspace con ricerca"),
    bullet("Export risposta — genera PDF/DOCX della risposta con fonti"),
    spacer(80),

    h2("7.3 Stack tecnologico suggerito"),
    new Table({
      width: { size: 8960, type: WidthType.DXA }, columnWidths: [2000, 3000, 3960],
      rows: [
        new TableRow({ children: [
          cell("Layer", C.bluheader, { w: 2000, bold: true, color: C.bianco }),
          cell("Tecnologia", C.bluheader, { w: 3000, bold: true, color: C.bianco }),
          cell("Motivazione", C.bluheader, { w: 3960, bold: true, color: C.bianco }),
        ]}),
        new TableRow({ children: [
          cell("Framework", C.grigio, { w: 2000, size: 19 }),
          cell("React + TypeScript", C.grigio, { w: 3000, size: 19 }),
          cell("Ecosistema maturo, tipizzazione robusta", C.grigio, { w: 3960, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("UI", C.bianco, { w: 2000, size: 19 }),
          cell("shadcn/ui + Tailwind CSS", C.bianco, { w: 3000, size: 19 }),
          cell("Componenti professionali, dark/light mode", C.bianco, { w: 3960, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("API client", C.grigio, { w: 2000, size: 19 }),
          cell("TanStack Query + Axios", C.grigio, { w: 3000, size: 19 }),
          cell("Cache, loading states, error handling", C.grigio, { w: 3960, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("Streaming", C.bianco, { w: 2000, size: 19 }),
          cell("Server-Sent Events (SSE)", C.bianco, { w: 3000, size: 19 }),
          cell("Risposta LLM in streaming dalla FastAPI", C.bianco, { w: 3960, size: 19 }),
        ]}),
        new TableRow({ children: [
          cell("Deploy", C.grigio, { w: 2000, size: 19 }),
          cell("Vite + serve statico / Electron", C.grigio, { w: 3000, size: 19 }),
          cell("Locale per ora (dati sensibili in studio)", C.grigio, { w: 3960, size: 19 }),
        ]}),
      ],
    }),
    spacer(100),

    h2("7.4 Integrazione con API esistente"),
    p("La FastAPI è già CORS-ready e non richiede modifiche per il frontend. " +
      "Le modifiche necessarie lato backend sono minime:", { sa: 60 }),
    bullet("Aggiungere endpoint SSE per streaming risposta LLM (POST /query/stream)"),
    bullet("Aggiungere autenticazione JWT per multi-tenant"),
    bullet("Aggiungere endpoint GET /wiki per browsing wiki_pages"),
    spacer(80),
    p("Stima sviluppo MVP: 2-3 settimane per uno sviluppatore frontend.",
      { italic: true, size: 19, color: C.grigiosc }),
  ];
}

// ── DOCUMENTO ─────────────────────────────────────────────────────────────
const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, font: "Arial", color: C.blu },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: C.bluheader },
        paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "◦", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
      ],
    }],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1134, right: 1134, bottom: 1134, left: 1134 },
      },
    },
    headers: {
      default: new Header({ children: [
        new Paragraph({
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: C.bluheader } },
          spacing: { before: 0, after: 80 },
          children: [new TextRun({ text: "AiUra LegalLab  |  Documentazione tecnica  |  " + today,
            size: 16, color: C.grigiosc, font: "Arial" })],
        }),
      ]}),
    },
    footers: {
      default: new Footer({ children: [
        new Paragraph({
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: C.bluheader } },
          spacing: { before: 80, after: 0 },
          alignment: AlignmentType.RIGHT,
          children: [
            new TextRun({ text: "Pagina ", size: 16, color: C.grigiosc, font: "Arial" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: C.grigiosc, font: "Arial" }),
            new TextRun({ text: " di ", size: 16, color: C.grigiosc, font: "Arial" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: C.grigiosc, font: "Arial" }),
          ],
        }),
      ]}),
    },
    children: [
      ...cover(),
      ...sezArchitettura(),
      ...sezSorgenti(),
      ...sezInstallazione(),
      ...sezAvvio(),
      ...sezEndpoint(),
      ...sezBacklog(),
      ...sezFrontend(),
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("docs/AiUra_LegalLab_Documentazione_v1.docx", buf);
  console.log("Documento generato: docs/AiUra_LegalLab_Documentazione_v1.docx");
});
