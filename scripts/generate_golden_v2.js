const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, HeadingLevel, PageBreak,
  TableOfContents, ExternalHyperlink,
} = require("docx");
const fs = require("fs");

const data = JSON.parse(fs.readFileSync("docs/golden_v2_clean.json", "utf-8"));
const today = "2 giugno 2026";

// ── Colori ─────────────────────────────────────────────────────────────
const C = {
  blu:       "1F4E79",
  blucell:   "D6E4F0",
  bluheader: "2E75B6",
  verde:     "1E7145",
  verdecell: "D9EDD4",
  rosso:     "C00000",
  rossocell: "FADADD",
  giallo:    "7D5A00",
  giallocell:"FFF3CD",
  grigio:    "F2F2F2",
  grigiosc:  "595959",
  bianco:    "FFFFFF",
};

// ── Helpers ─────────────────────────────────────────────────────────────
function para(text, opts = {}) {
  const { bold, italic, size, color, align, spacing, indent, heading, pageBreakBefore } = opts;
  return new Paragraph({
    heading: heading,
    pageBreakBefore: pageBreakBefore || false,
    alignment: align || AlignmentType.LEFT,
    spacing: { before: spacing?.before ?? 60, after: spacing?.after ?? 60 },
    indent: indent,
    children: [new TextRun({ text, bold: bold||false, italics: italic||false,
      size: size||22, color: color||"000000", font: "Arial" })],
  });
}

function spacer(pts = 60) {
  return new Paragraph({ spacing: { before: pts, after: 0 }, children: [] });
}

function sectionHeader(text, color = C.bluheader) {
  return new Paragraph({
    spacing: { before: 160, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: color } },
    children: [new TextRun({ text, bold: true, size: 26, color, font: "Arial" })],
  });
}

function cell(text, fill, opts = {}) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new TableCell({
    borders,
    width: opts.width ? { size: opts.width, type: WidthType.DXA } : undefined,
    shading: { fill, type: ShadingType.CLEAR },
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({
        text, bold: opts.bold||false, size: opts.size||20,
        color: opts.color||"000000", font: "Arial"
      })]
    })],
  });
}

function verdictColor(v) {
  return v === "PASS" ? C.verde : v === "FAIL" ? C.rosso : C.grigiosc;
}
function verdictBg(v) {
  return v === "PASS" ? C.verdecell : v === "FAIL" ? C.rossocell : C.grigio;
}
function confColor(c) {
  if (c === "HIGH") return C.verde;
  if (c === "MEDIUM") return C.giallo;
  return C.rosso;
}

// ── Tabella fonti ────────────────────────────────────────────────────────
function sourcesTable(sources) {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      cell("N.", C.bluheader.replace(/^/,""), {width:400, bold:true, color:C.bianco, center:true}),
      cell("Source ID / Organo", C.bluheader, {width:4200, bold:true, color:C.bianco}),
      cell("Score", C.bluheader, {width:700, bold:true, color:C.bianco, center:true}),
      cell("Estratto", C.bluheader, {width:3660, bold:true, color:C.bianco}),
    ],
  });
  const rows = sources.map((s, i) => {
    const isJur = !!s.organo;
    const bg = isJur ? (i % 2 === 0 ? "EAF4FB" : C.bianco) : (i % 2 === 0 ? C.grigio : C.bianco);
    const label = isJur
      ? `${s.organo.toUpperCase()} n.${s.numero}/${s.anno}\n[${s.chunk_type||""}]`
      : s.source_id.replace("urn:nir:", "").substring(0, 55);
    return new TableRow({ children: [
      cell(String(s.rank), bg, { width:400, center:true, size:18 }),
      cell(label, bg, { width:4200, size:17 }),
      cell(String(s.score), bg, { width:700, center:true, size:17 }),
      cell(s.snippet, bg, { width:3660, size:17 }),
    ]});
  });
  return new Table({
    width: { size: 8960, type: WidthType.DXA },
    columnWidths: [400, 4200, 700, 3660],
    rows: [headerRow, ...rows],
  });
}

// ── Scheda singola query ─────────────────────────────────────────────────
function buildScheda(r, idx) {
  const verd = r.reviewer_verdict || "N/A";
  const act  = r.reviewer_action  || "N/A";
  const conf = r.overall_confidence || "N/A";
  const jur  = r.sources.filter(s => s.organo);
  const norme = r.sources.filter(s => !s.organo);
  const elapsed = Math.round(r.duration_total_s * 1000);

  const children = [
    // Intestazione scheda
    new Paragraph({
      pageBreakBefore: idx > 0,
      spacing: { before: 0, after: 100 },
      children: [
        new TextRun({ text: `Scheda ${r.id} di 10 — `, bold: true, size: 26, color: C.blu, font:"Arial" }),
        new TextRun({ text: r.modulo, bold: true, size: 26, color: C.bluheader, font:"Arial" }),
      ],
    }),
    // Metadata row
    new Table({
      width: { size: 8960, type: WidthType.DXA },
      columnWidths: [2240, 2240, 2240, 2240],
      rows: [new TableRow({ children: [
        cell(`Difficoltà: ${r.difficolta}`, C.grigio, { width:2240, bold:true, size:18 }),
        cell(`Norma: ${r.norma}`, C.grigio, { width:2240, size:18 }),
        cell(`Giurisprudenza: ${jur.length}/10 fonti`, C.verdecell, { width:2240, bold:true, size:18, color: C.verde }),
        cell(`Tempo: ${elapsed} ms`, C.grigio, { width:2240, size:18 }),
      ]})],
    }),
    spacer(120),

    // Scenario
    sectionHeader("Scenario (query sottoposta al sistema)"),
    para(r.query, { italic: true, size: 21, color: "333333", spacing:{before:80,after:80} }),
    spacer(80),

    // Risposta
    sectionHeader("Risposta del sistema"),
    ...r.answer.split(/\n+/).filter(l=>l.trim()).map(line => {
      const isSection = /^\*\*[A-Z]/.test(line);
      const cleaned = line.replace(/\*\*/g, "").trim();
      return para(cleaned, {
        bold: isSection,
        size: isSection ? 21 : 20,
        color: isSection ? C.blu : "222222",
        spacing: { before: isSection ? 120 : 40, after: isSection ? 40 : 30 },
        indent: isSection ? undefined : { left: 360 },
      });
    }),
    spacer(100),

    // Reviewer + Confidenza
    sectionHeader("Valutazione automatica"),
    new Table({
      width: { size: 8960, type: WidthType.DXA },
      columnWidths: [2240, 2240, 2240, 2240],
      rows: [new TableRow({ children: [
        cell("Reviewer", C.grigio, { width:2240, bold:true, size:18 }),
        cell(`${verd} → ${act}`, verdictBg(verd), { width:2240, bold:true, size:19, color: verdictColor(verd) }),
        cell("Confidenza", C.grigio, { width:2240, bold:true, size:18 }),
        cell(conf, C.grigio, { width:2240, bold:true, size:19, color: confColor(conf) }),
      ]})],
    }),
    spacer(80),
  ];

  // Gap analysis
  if (r.gaps && r.gaps.length > 0) {
    children.push(sectionHeader("Gap Analysis", C.rosso));
    r.gaps.forEach(g => {
      children.push(para(`• ${g}`, { size: 19, color: "444444", spacing:{before:40,after:30}, indent:{left:360} }));
    });
    children.push(spacer(80));
  }

  // Fonti — Giurisprudenza
  if (jur.length > 0) {
    children.push(sectionHeader("Fonti giurisprudenziali citate", C.verde));
    children.push(para(
      `Il sistema ha recuperato ${jur.length} sentenze dalla knowledge base giurisprudenziale.`,
      { size: 19, italic: true, color: C.verde, spacing:{before:60,after:80} }
    ));
    children.push(sourcesTable(jur));
    children.push(spacer(80));
  }

  // Fonti normative
  if (norme.length > 0) {
    children.push(sectionHeader("Fonti normative citate", C.bluheader));
    children.push(sourcesTable(norme));
    children.push(spacer(80));
  }

  // Rubrica valutazione avvocato
  children.push(sectionHeader("Rubrica di valutazione — da compilare"));
  const rubricaRows = [
    ["Correttezza giuridica", "1  2  3  4  5"],
    ["Pertinenza fonti normative", "1  2  3  4  5"],
    ["Qualità giurisprudenza citata", "1  2  3  4  5"],
    ["Allucinazioni / errori fattuali", "Sì / No"],
    ["Giurisprudenza mancante rilevante", ""],
    ["Note libere", ""],
  ];
  children.push(new Table({
    width: { size: 8960, type: WidthType.DXA },
    columnWidths: [4000, 4960],
    rows: [
      new TableRow({ tableHeader: true, children: [
        cell("Criterio", C.bluheader, { width:4000, bold:true, color:C.bianco }),
        cell("Valutazione", C.bluheader, { width:4960, bold:true, color:C.bianco }),
      ]}),
      ...rubricaRows.map(([label, val], i) => new TableRow({ children: [
        cell(label, i%2===0 ? C.grigio : C.bianco, { width:4000, bold:true, size:19 }),
        cell(val, i%2===0 ? C.grigio : C.bianco, { width:4960, size:19 }),
      ]})),
    ],
  }));

  return children;
}

// ── Copertina ────────────────────────────────────────────────────────────
function buildCover() {
  const pass = data.filter(r => r.reviewer_verdict === "PASS").length;
  const fail = data.filter(r => r.reviewer_verdict === "FAIL").length;

  return [
    spacer(800),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing:{before:0,after:120},
      children: [new TextRun({ text:"AiUra LegalLab", bold:true, size:56, color:C.blu, font:"Arial" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing:{before:0,after:80},
      children: [new TextRun({ text:"Valutazione Sistema", size:32, color:C.grigiosc, font:"Arial" })] }),
    spacer(40),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing:{before:0,after:80},
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: C.bluheader } },
      children: [new TextRun({ text:"Golden Test Set — Seconda Sessione — Penale Tributario", bold:true, size:28, color:C.bluheader, font:"Arial" })] }),
    spacer(40),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing:{before:0,after:200},
      children: [new TextRun({ text:today, size:22, color:C.grigiosc, font:"Arial" })] }),
    spacer(200),

    // Riquadro novità
    new Paragraph({ spacing:{before:0,after:80},
      border: { left: { style: BorderStyle.SINGLE, size: 20, color: C.verde, space: 10 } },
      indent: { left: 400 },
      children: [new TextRun({ text:"NOVITÀ IN QUESTA SESSIONE", bold:true, size:24, color:C.verde, font:"Arial" })] }),
    para("Questa sessione introduce la giurisprudenza nella knowledge base: "+
      "58.845 sentenze (Cassazione, TAR, Corte dei Conti) sono ora consultabili dal sistema. "+
      "Tutte le 10 risposte includono fonti giurisprudenziali — nella prima sessione la sezione "+
      "Giurisprudenza era vuota per tutte le schede.",
      { size:20, color:"333333", spacing:{before:60,after:80}, indent:{left:400} }),
    spacer(100),

    // Statistiche
    sectionHeader("Riepilogo risultati"),
    new Table({
      width: { size: 8960, type: WidthType.DXA },
      columnWidths: [2240, 2240, 2240, 2240],
      rows: [new TableRow({ children: [
        cell("Query elaborate", C.grigio,  { width:2240, bold:true, size:20, center:true }),
        cell("PASS → DELIVER",  C.verdecell, { width:2240, bold:true, size:20, center:true, color:C.verde }),
        cell("FAIL → RE_RETRIEVAL", C.rossocell, { width:2240, bold:true, size:20, center:true, color:C.rosso }),
        cell("Fonti giurisprudenziali", C.blucell, { width:2240, bold:true, size:20, center:true, color:C.blu }),
      ]}),
      new TableRow({ children: [
        cell("10", C.grigio,   { width:2240, bold:true, size:36, center:true }),
        cell(String(pass),    C.verdecell, { width:2240, bold:true, size:36, center:true, color:C.verde }),
        cell(String(fail),    C.rossocell, { width:2240, bold:true, size:36, center:true, color:C.rosso }),
        cell("10 / 10",       C.blucell,   { width:2240, bold:true, size:36, center:true, color:C.blu }),
      ]}),
    ]}),
    spacer(100),

    // Istruzioni
    sectionHeader("Istruzioni per la valutazione"),
    para("Questo documento contiene 10 scenari in materia di penale tributario con le risposte "+
      "generate dal sistema AiUra LegalLab. Per ciascuno Le chiediamo di valutare la risposta "+
      "compilando la rubrica in fondo a ogni scheda.",
      { size:20, spacing:{before:80,after:60} }),
    para("La valutazione richiede circa 5-10 minuti per scheda (60-90 minuti totali).",
      { size:20, spacing:{before:40,after:60} }),
    spacer(60),
    para("COSA VALUTARE:", { bold:true, size:21, color:C.blu }),
    ...["Correttezza giuridica della risposta",
        "Pertinenza e qualità della giurisprudenza citata (NOVITÀ)",
        "Pertinenza delle fonti normative citate",
        "Presenza di affermazioni inventate o errate (allucinazioni)",
        "Sentenze importanti eventualmente mancanti"].map(t =>
      para("• " + t, { size:20, indent:{left:360}, spacing:{before:30,after:20} })),
    spacer(60),
    para("COSA NON VALUTARE: stile redazionale, lunghezza, formattazione.",
      { size:20, italic:true, color:C.grigiosc }),
    spacer(100),

    // Legenda reviewer
    sectionHeader("Legenda Reviewer automatico"),
    new Table({
      width: { size: 8960, type: WidthType.DXA },
      columnWidths: [2000, 6960],
      rows: [
        new TableRow({ children: [
          cell("PASS → DELIVER", C.verdecell, { width:2000, bold:true, color:C.verde }),
          cell("Il sistema ha approvato la risposta — tutte le citazioni sono verificate nella KB", C.verdecell, { width:6960, size:19 }),
        ]}),
        new TableRow({ children: [
          cell("FAIL → RE_RETRIEVAL", C.rossocell, { width:2000, bold:true, color:C.rosso }),
          cell("Il sistema ha rilevato citazioni non verificabili (possibile allucinazione) — risposta da rivedere", C.rossocell, { width:6960, size:19 }),
        ]}),
      ],
    }),
    spacer(60),
    para("Documento riservato — uso interno", { size:18, italic:true, color:C.grigiosc, align:AlignmentType.CENTER, spacing:{before:120,after:0} }),
  ];
}

// ── Documento ────────────────────────────────────────────────────────────
const allSchede = data.flatMap((r, i) => buildScheda(r, i));

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: C.blu },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: C.bluheader },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }],
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
          children: [
            new TextRun({ text: "AiUra LegalLab  |  Golden Test Set v2  |  Penale Tributario", size: 16, color: C.grigiosc, font: "Arial" }),
          ],
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
      ...buildCover(),
      ...allSchede,
    ],
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("docs/golden_test_set_v2_con_giurisprudenza.docx", buf);
  console.log("Documento generato: docs/golden_test_set_v2_con_giurisprudenza.docx");
});
