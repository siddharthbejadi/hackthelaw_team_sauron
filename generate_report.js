/**
 * Legal AI Supervisor — Full Project Report
 * Run: node generate_report.js
 * Requires: npm install -g docx
 * Output: Legal_AI_Supervisor_Report.docx
 */
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat,
  TableOfContents,
} = require("docx");
const fs = require("fs");

// ── Helpers ───────────────────────────────────────────────────
const FONT  = "Calibri";
const MONO  = "Courier New";
const W     = 9360;  // content width in DXA (US Letter, 1" margins)
const bdr   = (c) => ({ style: BorderStyle.SINGLE, size: 1, color: c });
const allBorders = (c) => ({ top: bdr(c), bottom: bdr(c), left: bdr(c), right: bdr(c) });
const noBorders  = () => ({ top: bdr("FFFFFF"), bottom: bdr("FFFFFF"), left: bdr("FFFFFF"), right: bdr("FFFFFF") });

// ── Style builders ────────────────────────────────────────────
const h1 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  children: [new TextRun({ text, font: FONT, bold: true })],
  spacing: { before: 360, after: 120 },
});
const h2 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  children: [new TextRun({ text, font: FONT, bold: true })],
  spacing: { before: 240, after: 80 },
});
const h3 = (text) => new Paragraph({
  heading: HeadingLevel.HEADING_3,
  children: [new TextRun({ text, font: FONT, bold: true })],
  spacing: { before: 160, after: 60 },
});
const body = (text, opts={}) => new Paragraph({
  children: [new TextRun({ text, font: FONT, size: 22, ...opts })],
  spacing: { after: 120 },
});
const bullet = (text, opts={}) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  children: [new TextRun({ text, font: FONT, size: 22, ...opts })],
  spacing: { after: 80 },
});
const numbered = (text, opts={}) => new Paragraph({
  numbering: { reference: "numbers", level: 0 },
  children: [new TextRun({ text, font: FONT, size: 22, ...opts })],
  spacing: { after: 80 },
});
const code = (text) => new Paragraph({
  children: [new TextRun({ text, font: MONO, size: 18, color: "1E40AF" })],
  spacing: { after: 60 },
  indent: { left: 720 },
});
const spacer = (n=120) => new Paragraph({ children: [new TextRun("")], spacing: { after: n } });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });

// ── Table builders ─────────────────────────────────────────────
const makeCell = (text, opts={}) => new TableCell({
  borders: allBorders("D1D5DB"),
  width: { size: opts.w || 4680, type: WidthType.DXA },
  shading: opts.shade ? { fill: opts.shade, type: ShadingType.CLEAR } : undefined,
  margins: { top: 80, bottom: 80, left: 120, right: 120 },
  verticalAlign: VerticalAlign.TOP,
  children: [new Paragraph({
    children: [new TextRun({
      text,
      font: FONT,
      size: opts.size || 20,
      bold: opts.bold || false,
      color: opts.color || "374151",
    })],
    spacing: { after: 0 },
  })],
});
const makeHeaderCell = (text, w=4680) => makeCell(text, { w, shade: "2563EB", bold: true, color: "FFFFFF", size: 20 });

// ── Comparison table helper ───────────────────────────────────
const compTable = (rows, widths=[3120,3120,3120]) => new Table({
  width: { size: W, type: WidthType.DXA },
  columnWidths: widths,
  rows: rows.map((row, ri) => new TableRow({
    children: row.map((cell, ci) => {
      const isHeader = ri === 0;
      return new TableCell({
        borders: allBorders("D1D5DB"),
        width: { size: widths[ci], type: WidthType.DXA },
        shading: { fill: isHeader ? "1E3A5F" : (ri%2===0 ? "F8FAFC" : "FFFFFF"), type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: cell, font: FONT, size: 20, bold: isHeader, color: isHeader ? "FFFFFF" : "374151" })],
          spacing: { after: 0 },
        })],
      });
    }),
  })),
});

// ── Two-col comparison table ──────────────────────────────────
const twoColTable = (rows) => new Table({
  width: { size: W, type: WidthType.DXA },
  columnWidths: [4680, 4680],
  rows: rows.map((row, ri) => new TableRow({
    children: row.map((cell, ci) => {
      const isHeader = ri === 0;
      const shade = isHeader
        ? (ci===0 ? "B91C1C" : "15803D")
        : (ci===0 ? "FEF2F2" : "F0FDF4");
      return new TableCell({
        borders: allBorders("D1D5DB"),
        width: { size: 4680, type: WidthType.DXA },
        shading: { fill: shade, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({ text: cell, font: FONT, size: 20, bold: isHeader, color: isHeader ? "FFFFFF" : "374151" })],
          spacing: { after: 0 },
        })],
      });
    }),
  })),
});


// ═══════════════════════════════════════════════════════════════
// DOCUMENT SECTIONS
// ═══════════════════════════════════════════════════════════════

// ── Common styles ─────────────────────────────────────────────
const styles = {
  default: { document: { run: { font: FONT, size: 22 } } },
  paragraphStyles: [
    { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: FONT, size: 36, bold: true, color: "1E3A5F" },
      paragraph: { spacing: { before: 400, after: 160 }, outlineLevel: 0,
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "2563EB", space: 6 } } } },
    { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: FONT, size: 28, bold: true, color: "1E3A5F" },
      paragraph: { spacing: { before: 280, after: 120 }, outlineLevel: 1 } },
    { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { font: FONT, size: 24, bold: true, color: "374151" },
      paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 } },
  ],
};

const numbering = {
  config: [
    { reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "numbers",
      levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "letters",
      levels: [{ level: 0, format: LevelFormat.LOWER_LETTER, text: "%1)",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 1080, hanging: 360 } } } }] },
  ],
};

const header = new Header({
  children: [new Paragraph({
    children: [
      new TextRun({ text: "Legal AI Supervisor  —  End-to-End Project Report", font: FONT, size: 18, color: "6B7280" }),
      new TextRun({ text: "\t", font: FONT }),
      new TextRun({ text: "Clifford Chance Hackathon 2024", font: FONT, size: 18, color: "2563EB" }),
    ],
    tabStops: [{ type: "right", position: 9360 }],
    spacing: { after: 0 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 2, color: "E5E7EB", space: 4 } },
  })],
});

const footer = new Footer({
  children: [new Paragraph({
    children: [
      new TextRun({ text: "Legal AI Supervisor  —  Confidential  —  Hackathon Submission", font: FONT, size: 16, color: "9CA3AF" }),
      new TextRun({ text: "\tPage ", font: FONT, size: 16, color: "9CA3AF" }),
      new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "2563EB" }),
      new TextRun({ text: " of ", font: FONT, size: 16, color: "9CA3AF" }),
      new TextRun({ children: [PageNumber.TOTAL_PAGES], font: FONT, size: 16, color: "2563EB" }),
    ],
    tabStops: [{ type: "right", position: 9360 }],
    spacing: { after: 0 },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: "E5E7EB", space: 4 } },
  })],
});

// ═══════════════════════════════════════════════════════════════
// BUILD DOCUMENT
// ═══════════════════════════════════════════════════════════════

const doc = new Document({
  title: "Legal AI Supervisor — End-to-End Project Report",
  description: "Clifford Chance Hackathon submission: How Do We Supervise Legal AI Agents?",
  styles,
  numbering,
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 },
      },
    },
    headers: { default: header },
    footers: { default: footer },
    children: [

      // ── Cover page ────────────────────────────────────────────
      new Paragraph({
        children: [new TextRun({ text: "", font: FONT })],
        spacing: { after: 2880 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Legal AI Supervisor", font: FONT, size: 72, bold: true, color: "1E3A5F" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 240 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "End-to-End Project Report", font: FONT, size: 40, color: "2563EB" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 160 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Clifford Chance Hackathon  —  2024", font: FONT, size: 28, color: "6B7280" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 80 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Theme: How Do We Supervise Legal AI Agents?", font: FONT, size: 28, bold: true, color: "374151", italics: true })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 1440 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Core Technologies", font: FONT, size: 24, bold: true, color: "1E3A5F" })],
        alignment: AlignmentType.CENTER,
        spacing: { after: 160 },
      }),
      ...["NVIDIA Nemotron-Ultra 550B (MoE LLM)", "FastAPI  —  Python asyncio  —  Streamlit", "OpenAI-compatible Streaming API"].map(t =>
        new Paragraph({ children: [new TextRun({ text: t, font: FONT, size: 22, color: "374151" })], alignment: AlignmentType.CENTER, spacing: { after: 80 } })
      ),
      pageBreak(),

      // ── Table of Contents ─────────────────────────────────────
      h1("Table of Contents"),
      new TableOfContents("Contents", { hyperlink: true, headingStyleRange: "1-3" }),
      pageBreak(),

      // ═══════════════════════════════════════════════════════════
      // 1. EXECUTIVE SUMMARY
      // ═══════════════════════════════════════════════════════════
      h1("1. Executive Summary"),
      body("The Legal AI Supervisor is a risk-proportionate, multi-agent AI system designed for law firm workflows. Built for the Clifford Chance Hackathon under the theme ‘How Do We Supervise Legal AI Agents?’, it addresses three critical gaps in current legal AI adoption: hallucination risk, absence of oversight mechanisms, and regulatory compliance under SRA guidelines."),
      body("The system deploys four specialist AI agents (Research, Drafting, Review, Risk Analysis) coordinated by an AI Supervisor that enforces confidence and risk thresholds, retries on poor-quality outputs, and escalates to human lawyers when necessary. Human lawyers retain full override at every stage. Every action — whether taken by a human or an AI agent — is logged in a comprehensive audit trail with timestamp, actor type, confidence score, risk level, and citations."),
      body("The entire system is powered by a single large language model, NVIDIA Nemotron-Ultra 550B, accessed via an OpenAI-compatible API. A deliberate decision was made to use a generalised, large-scale model with specialist system prompts rather than dedicated fine-tuned legal AI agents — a choice that provides greater flexibility, transparency, and architectural simplicity without sacrificing output quality."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 2. PROBLEM STATEMENT
      // ═══════════════════════════════════════════════════════════
      h1("2. Problem Statement"),
      body("Law firms are under increasing pressure to adopt AI, but the legal profession faces unique challenges that make unsupervised AI adoption dangerous:"),
      spacer(80),
      h2("2.1 AI Hallucinations in Legal Contexts"),
      body("Large language models can produce fluent, confident-sounding legal output that is factually wrong. In law, a fabricated case citation or a misquoted statute can result in professional negligence claims, regulatory sanctions, or irreparable harm to clients. Unlike many domains, legal errors are not recoverable — submitting a document to a court or counterparty with false citations is a matter of professional responsibility."),
      h2("2.2 Absence of Oversight Infrastructure"),
      body("Current AI tools available to law firms (Harvey AI, CoCounsel, Clio Duo) provide AI-generated legal outputs but lack a structured oversight layer. There is no native confidence scoring, no risk threshold enforcement, no retry logic for poor-quality outputs, and no escalation path that routes genuinely uncertain or high-risk outputs to a human professional."),
      h2("2.3 Regulatory and Professional Obligation"),
      body("The Solicitors Regulation Authority (SRA) requires lawyers to apply professional judgement to AI outputs before using them. As of 2024, there is no industry-standard workflow for how law firms should structure the human review of AI-generated legal work. The absence of such a workflow leaves firms legally exposed when AI outputs are used without appropriate verification."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 3. SOLUTION OVERVIEW
      // ═══════════════════════════════════════════════════════════
      h1("3. Solution Overview"),
      body("The Legal AI Supervisor provides a structured, risk-proportionate framework for AI involvement in law firm workflows. It is built around four core principles:"),
      spacer(80),
      compTable([
        ["Principle",            "Description",                                              "Implementation"],
        ["AI Transparency",     "Every agent exposes its reasoning, confidence, and citations", "reasoning_content streaming + structured JSON output"],
        ["Supervisor Loop",     "Centralised quality gate with retry and escalation logic",     "AI Supervisor agent with configurable thresholds"],
        ["Human Override",      "Every AI decision is reversible; no auto-ship of outputs",     "Senior approval gate + reject-and-redraft pathway"],
        ["Full Auditability",   "Complete audit trail of every human and AI action",            "log_event() called on every action with actor_type"],
      ], [2400, 3480, 3480]),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 4. SYSTEM ARCHITECTURE
      // ═══════════════════════════════════════════════════════════
      h1("4. System Architecture"),
      h2("4.1 High-Level Architecture"),
      body("The system is structured as a four-layer architecture:"),
      spacer(80),
      compTable([
        ["Layer",               "Technology",              "Responsibility"],
        ["Frontend (UI)",       "Streamlit (Python)",      "Multi-page app with role-based views; streams AI output in real time"],
        ["Backend API",         "FastAPI (Python)",         "REST endpoints; orchestrates agent calls; persists matter state"],
        ["Agent Layer",         "agents.py",               "Supervisor + 4 specialist agents; quality gate; audit logging"],
        ["Model / API",         "NVIDIA API (OpenAI-compat)","Nemotron-Ultra 550B; streaming; thinking tokens; structured JSON"],
      ], [2200, 2800, 4360]),
      spacer(80),
      h2("4.2 File Structure"),
      body("The project is structured as follows:"),
      spacer(60),
      ...["app.py          — Home page: live streaming demo, agent communication arrows",
          "api.py          — FastAPI backend: all REST endpoints",
          "agents.py       — Agent definitions, supervisor loop, audit logging",
          "store.py        — Matter persistence (matters.json file store)",
          "viz.py          — build_matter_flow_html(): self-contained HTML pipeline viz",
          "pages/",
          "  1_Partner.py  — Submit matters + track all via pipeline viz",
          "  2_Junior.py   — Receive matters, choose mode, get AI assistance",
          "  3_Senior.py   — Review flagged matters, approve or reject",
          "  4_Dashboard.py — Firm-wide view: pipeline viz, audit trail, full doc",
          ".env            — NVIDIA API keys (3 keys for round-robin pool)",
         ].map(l => code(l)),
      spacer(),

      h2("4.3 Data Flow"),
      body("The end-to-end data flow for a typical matter proceeds as follows:"),
      spacer(60),
      numbered("Partner submits a client matter via the Partner View UI. They provide: client name, matter type, and detailed instructions to the team. This is sent via POST /matters/submit."),
      numbered("The FastAPI backend calls the AI Router agent (Nemotron-Ultra with a routing system prompt). The router reads all available junior lawyers and the matter details, then returns a structured JSON object specifying which junior to assign, which senior to assign, and the instruction to pass to the junior."),
      numbered("The Junior Lawyer receives the matter in their view, along with the partner’s original instructions and the router’s instruction. They choose a work mode: Manual (write themselves), Hybrid (get an AI draft to edit), or Autonomous (let AI handle everything)."),
      numbered("Depending on the mode, one or more AI agents are invoked. In Autonomous mode, all four agents (Research, Drafting, Review, Risk) run concurrently via asyncio.gather() and asyncio.to_thread(), each calling the NVIDIA API independently."),
      numbered("The AI Supervisor aggregates agent outputs, runs the quality check (confidence >= 80%, risk <= 20%, no HIGH flags), and if the check fails, sends structured feedback to the agent and retries (up to 3 times). If still failing, it escalates to the Senior Lawyer."),
      numbered("The Senior Lawyer reviews the AI Supervisor’s summary, all HIGH flags, verified citations, and the draft. They either approve (matter completed) or reject with written notes (matter returned to junior)."),
      numbered("Every action throughout this flow is logged via log_event() to the matter’s actions array, with: timestamp, actor_type (human/ai), role, and detail. This constitutes the complete audit trail, visible in both the Partner View and Dashboard."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 5. ROLE ARCHITECTURE
      // ═══════════════════════════════════════════════════════════
      h1("5. Role Architecture"),
      body("The system is built around a four-role hierarchy that mirrors the actual structure of a law firm team:"),
      spacer(80),

      h2("5.1 Partner"),
      body("Partners (Sarah Chen, David Okafor) are the entry point for all client matters. In the Partner View they:"),
      bullet("Submit client matters with full instructions, matter type, and assigned team"),
      bullet("Track all active matters via the real-time animated pipeline visualisation"),
      bullet("View the complete audit trail of every AI and human action on their matters"),
      bullet("See AI Router decisions: which junior was assigned, which senior will review, and the routing reasoning"),
      spacer(80),

      h2("5.2 Junior Lawyer"),
      body("Junior lawyers (Priya Patel, Tom Davies, Aisha Mensah) receive routed matters and choose their level of AI involvement:"),
      bullet("Manual Mode: Write the draft themselves. AI Review + Risk Analysis agents review on submission."),
      bullet("Hybrid Mode: Request an AI draft from the Drafting Agent, then edit it in the text area before submission."),
      bullet("Autonomous Mode: Let all four AI agents handle the work. Always escalates to senior for review — never auto-completes."),
      body("Junior lawyers also have access to a per-matter AI chat assistant, scoped to the specific matter context (client, instructions, prior AI review). The chat uses the full matter as a system prompt, and the last 10 conversational turns are passed as history."),
      spacer(80),

      h2("5.3 Senior Lawyer"),
      body("Senior lawyers (James Wright, Meera Nair) are the final human gate before any matter is completed. In the Senior View they:"),
      bullet("Review the AI Supervisor’s summary of all flagged issues, sorted by severity (HIGH / MEDIUM / LOW)"),
      bullet("See the overall confidence %, risk %, HIGH flag count, and citation count at a glance"),
      bullet("Read AI-verified citations linked to Google Scholar / case law search"),
      bullet("Approve (matter completed) or Reject with written notes (matter returned to junior)"),
      body("Senior approval is mandatory for every matter in every mode. There is no pathway to matter completion that bypasses senior review."),
      spacer(80),

      h2("5.4 Dashboard"),
      body("The Dashboard provides firm-wide visibility across all active matters. It displays:"),
      bullet("Summary metrics: total matters, active, flagged, completed, AI actions, Human actions"),
      bullet("Per-matter pipeline visualisation: the full animated HTML flow for any selected matter"),
      bullet("Audit trail tab: every action with Human/AI badge, timestamp, role, and detail text"),
      bullet("Document tab: the junior’s draft and AI citations, with expand controls for long content"),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 6. THE FOUR AI AGENTS
      // ═══════════════════════════════════════════════════════════
      h1("6. The Four AI Specialist Agents"),
      body("All four agents use NVIDIA Nemotron-Ultra 550B as the underlying model. Each agent is made ‘specialist’ through a detailed system prompt that defines its role, output constraints, and mandatory safeguards. All agents return structured JSON."),
      spacer(80),

      h2("6.1 Research Agent"),
      body("The Research Agent finds relevant UK case law, statutes, and legal principles applicable to the matter. Its core constraint is citation safety: it is explicitly instructed never to fabricate citations, and to mark any citation it cannot verify with the label ‘CITATION UNVERIFIED — must be checked by a qualified lawyer’. This makes citation risks explicit rather than hidden."),
      body("Output schema: { output, confidence, risk, citations: [...], flags: [...] }"),
      spacer(80),

      h2("6.2 Drafting Agent"),
      body("The Drafting Agent produces professional legal text: contract clauses, redlined provisions, legal summaries. Every assumption it makes in the draft must be flagged in the output. The agent is instructed to produce work that is ‘immediately usable by a qualified lawyer with verification’ — not a finished product, but a high-quality starting point."),
      body("The agent is constrained to flag jurisdiction-specific considerations, use precise legal language, and structure output clearly with clause numbers or section markers."),
      spacer(80),

      h2("6.3 Review Agent"),
      body("The Review Agent critically analyses documents for legal errors, compliance gaps, inconsistencies, and risks. It is explicitly instructed: ‘Do not give a clean bill of health unless you are genuinely confident the document is sound’. Every issue it identifies is classified as HIGH, MEDIUM, or LOW severity with a brief justification."),
      body("HIGH flags indicate issues that must be resolved before the matter can proceed. MEDIUM and LOW flags are advisory. The supervisor uses HIGH flag count as one of its quality gate criteria."),
      spacer(80),

      h2("6.4 Risk Analysis Agent"),
      body("The Risk Analysis Agent identifies and classifies legal risks. It is instructed that every risk identified must be backed by a statute, case law reference, or established legal principle — not a generic concern. Risks that cannot be backed this way must be labelled UNVERIFIED."),
      body("The agent is instructed to err on the side of over-flagging: ‘A lawyer can dismiss a risk; they cannot un-miss one.’ This deliberately sets the risk score higher, which triggers supervisor escalation and ensures senior review for genuinely risky matters."),
      spacer(80),

      h2("6.5 AI Supervisor"),
      body("The AI Supervisor is not a fifth specialist agent — it is an orchestrator. It:"),
      numbered("Dispatches tasks to specialist agents and collects their structured JSON outputs"),
      numbered("Aggregates results: merges citations, deduplicates flags, computes overall confidence and risk"),
      numbered("Applies the quality gate: confidence >= 80%, risk <= 20%, no HIGH flags"),
      numbered("If the gate fails: sends structured feedback to the failing agent and retries (max 3 attempts)"),
      numbered("If still failing after retries: generates a summary and escalates to the Senior Lawyer"),
      numbered("Logs every decision (dispatch, retry, escalation, accept) to the matter audit trail"),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 7. THREE WORK MODES
      // ═══════════════════════════════════════════════════════════
      h1("7. Three Work Modes"),
      body("A key design decision was to give junior lawyers control over AI involvement rather than imposing a single mandatory AI workflow. The mode is selected by the junior via card UI and logged in the audit trail. This respects professional autonomy while making AI assistance genuinely available."),
      spacer(80),
      compTable([
        ["Mode",        "Junior Action",                         "AI Agents Invoked",           "Senior Review"],
        ["Manual",      "Writes draft independently",             "Review + Risk Analysis only",  "Always required"],
        ["Hybrid",      "Edits an AI-generated starting draft",  "Drafting + Review + Risk",      "Always required"],
        ["Autonomous",  "Delegates entire task to AI",            "All 4 agents in parallel",      "Always required"],
      ], [1800, 3000, 2760, 1800]),
      spacer(80),
      body("Importantly, all three modes funnel through the AI Supervisor quality gate, and all three require Senior Lawyer approval. The modes differ only in how much AI is involved in the drafting phase — the oversight layer is constant."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 8. WHY NVIDIA NEMOTRON-ULTRA
      // ═══════════════════════════════════════════════════════════
      h1("8. Why NVIDIA Nemotron-Ultra?"),
      h2("8.1 Model Choice Rationale"),
      body("The most fundamental technical decision in the project was the choice of language model. The question was: should we use dedicated fine-tuned legal AI agents, or a large generalised model directed by specialist prompts?"),
      body("We chose NVIDIA Nemotron-Ultra (nvidia/nemotron-3-ultra-550b-a55b) — a 550-billion-parameter Mixture-of-Experts model accessible via an OpenAI-compatible API. This is a generalised model, not a legal-domain specialist."),
      spacer(80),
      h2("8.2 Technical Specifications"),
      spacer(60),
      compTable([
        ["Property",        "Value"],
        ["Model ID",        "nvidia/nemotron-3-ultra-550b-a55b"],
        ["Architecture",    "Mixture-of-Experts (MoE)"],
        ["Total Parameters","550 Billion"],
        ["Active per Token","~55 Billion (efficient inference via MoE routing)"],
        ["API Endpoint",    "https://integrate.api.nvidia.com/v1"],
        ["Compatibility",   "OpenAI API compatible (drop-in client)"],
        ["Reasoning Mode",  "enable_thinking: True with reasoning_budget: 4096"],
        ["Streaming",       "stream=True — token-by-token SSE streaming"],
        ["Context Window",  "128K tokens"],
      ], [3120, 6240]),
      spacer(80),

      h2("8.3 Dedicated Legal AI Agents vs. Generalised LLM"),
      body("The following comparison illustrates why a generalised model was preferred for this architecture:"),
      spacer(60),
      twoColTable([
        ["Dedicated Legal AI Agents (e.g. Harvey, CoCounsel)", "NVIDIA Nemotron-Ultra (Generalised LLM)"],
        ["Tailored to specific legal templates — rigid scope", "Works across all agent types with specialist prompts"],
        ["Closed-source: no visibility into model reasoning",    "reasoning_content exposes internal thinking chain"],
        ["No confidence or risk scoring available natively",     "Instructed to return JSON with confidence, risk, flags"],
        ["No token-by-token streaming for live agent UIs",       "Full streaming via stream=True and SSE"],
        ["Expensive per-query API pricing ($$$)",                "Open-weight accessible via NVIDIA API — cost-effective"],
        ["Not open-weight — cannot self-host for demos",         "Open-weight architecture: transparent and auditable"],
        ["Not designed for multi-agent supervisor loops",         "Fully composable in custom orchestration architectures"],
        ["Fine-tuned only for legal templates, not reasoning",   "550B params provides deep reasoning + legal knowledge"],
      ]),
      spacer(80),

      h2("8.4 How We Use the Model"),
      body("We exploit four specific capabilities of Nemotron-Ultra that are essential to the system’s transparency and quality:"),
      spacer(60),
      h3("Thinking Tokens (reasoning_content)"),
      body("By setting enable_thinking: True and a reasoning_budget of 4096 tokens, the model produces an internal reasoning chain (thinking tokens) before its final answer. In the live demo, these thinking tokens are optionally surfaced to lawyers, allowing them to see how the AI arrived at its output — removing the black-box problem entirely."),
      h3("Structured JSON Output"),
      body("Each agent is instructed to return only valid JSON conforming to a specific schema. The supervisor JSON-parses the output, extracts confidence, risk, citations, and flags, and uses these programmatically in the quality gate. This makes AI outputs machine-readable and auditable, not just human-readable text."),
      h3("Real-Time Token Streaming"),
      body("stream=True causes the model to emit tokens as they are generated, via Server-Sent Events. The Streamlit app consumes these via an async generator, updating st.empty() placeholders token-by-token. This powers the live agent communication demo on the home page — users watch agents ‘think and write’ in real time, with supervisor direction arrows appearing between outputs."),
      h3("Three-Key Round-Robin Pool"),
      body("Parallel agents each make concurrent NVIDIA API calls. A _get_client() function rotates through a pool of three API keys in sequence (using a module-level counter), distributing load across keys to avoid hitting per-key rate limits when four agents call simultaneously."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 9. FULL TECH STACK
      // ═══════════════════════════════════════════════════════════
      h1("9. Full Technology Stack"),
      spacer(60),
      compTable([
        ["Category",              "Technology",              "Version / Notes",                 "Why We Used It"],
        ["AI Model",              "NVIDIA Nemotron-Ultra",   "550B MoE via NVIDIA API",          "Streaming, reasoning tokens, open-weight, structured JSON"],
        ["Model SDK",             "openai (nvidia client)",  "OpenAI-compatible",                "Drop-in client for NVIDIA’s OpenAI-compat endpoint"],
        ["Backend Framework",     "FastAPI",                 "Python 3.11+",                     "Async-native, automatic OpenAPI docs, Pydantic validation"],
        ["Data Validation",       "Pydantic",                "v2 (FastAPI built-in)",             "Type-safe request/response models, JSON parsing"],
        ["Concurrency",           "asyncio / to_thread",    "Python stdlib",                    "True parallel agent execution without blocking the event loop"],
        ["Data Persistence",      "JSON file store",         "matters.json",                     "Lightweight, no DB setup, readable, portable for hackathon"],
        ["Frontend Framework",    "Streamlit",               "1.x",                              "Fast multi-page Python web UI with session state and streaming"],
        ["HTML Embedding",        "components.html()",       "Streamlit components",             "Embeds self-contained animated HTML for pipeline viz"],
        ["Streaming UI",          "st.empty()",              "Streamlit",                        "Placeholder updated token-by-token for live agent output"],
        ["Visualisation",         "viz.py (custom)",         "Hand-crafted HTML + CSS",          "Self-contained pipeline HTML for each matter, no JS frameworks"],
        ["Secret Management",     "python-dotenv",           "0.x",                              "Loads API keys from .env file, never hardcoded"],
        ["CSS / Theming",         "Custom CSS",              "Light theme palette",              "Consistent brand: navy, blue, purple, green, red, amber"],
      ], [2280, 2280, 2280, 2520]),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 10. DATA TYPES AND API USAGE
      // ═══════════════════════════════════════════════════════════
      h1("10. Data Types and API Usage"),
      h2("10.1 Input Data"),
      body("The system processes the following types of input data:"),
      spacer(60),
      compTable([
        ["Input Type",            "Source",                   "Format",        "Used By"],
        ["Client instructions",   "Partner (human)",          "Free text",     "AI Router, Agents, AI Chat"],
        ["Contract text",         "Junior (uploaded/pasted)",  "Free text",     "Drafting, Review, Risk agents"],
        ["Legal context",         "Matter JSON",              "Structured",    "All agents (via system prompt)"],
        ["Agent output history",  "Supervisor aggregation",   "JSON",          "Supervisor quality gate"],
        ["Chat history",          "Per-matter session state", "Message array", "AI Chat assistant"],
      ], [2600, 2200, 1560, 3000]),
      spacer(80),
      h2("10.2 NVIDIA API Data"),
      body("The primary external API call is to NVIDIA’s LLM inference endpoint. Each call includes:"),
      spacer(60),
      compTable([
        ["Field",               "Type",      "Value / Example"],
        ["model",               "string",    "nvidia/nemotron-3-ultra-550b-a55b"],
        ["messages",            "array",     "[{ role: system, content: <agent prompt> }, { role: user, content: <task> }]"],
        ["stream",              "boolean",   "True — token-by-token SSE streaming"],
        ["enable_thinking",     "boolean",   "True — activates reasoning_content"],
        ["reasoning_budget",    "integer",   "4096 tokens for thinking chain"],
        ["max_tokens",          "integer",   "8000 for final output"],
        ["temperature",         "float",     "0.2 for consistent, structured outputs"],
      ], [2600, 1560, 5200]),
      spacer(80),
      h2("10.3 Agent Output Schema"),
      body("Every agent is instructed to return a JSON object conforming to:"),
      spacer(60),
      code('{"output": "...",'),
      code(' "confidence": 85,          // integer 0-100'),
      code(' "risk": 40,                // integer 0-100'),
      code(' "citations": [             // verified references'),
      code('   "Smith v Jones [2022] EWCA Civ 123"'),
      code(' ],'),
      code(' "flags": [                 // issues with severity prefix'),
      code('   "HIGH - Missing indemnity cap: unlimited exposure under clause 8.2",'),
      code('   "MEDIUM - GDPR data processor agreement not addressed"'),
      code(' ]}'),
      spacer(80),
      h2("10.4 FastAPI Endpoints"),
      spacer(60),
      compTable([
        ["Method", "Endpoint",                    "Request Body",                        "Response"],
        ["POST",   "/matters/submit",              "client, instructions, partner_id, ...", "matter_id, routing decision"],
        ["GET",    "/matters",                     "—",                                       "Array of all matter objects"],
        ["POST",   "/generate_draft",              "matter_id, junior_id",               "draft text (streamed)"],
        ["POST",   "/matters/autonomous",          "matter_id, junior_id",               "ai_review JSON (streamed)"],
        ["POST",   "/matters/chat",               "matter_id, message, history",         "AI response (streamed)"],
        ["PUT",    "/matters/{id}/decision",       "senior_id, decision, notes",          "updated matter JSON"],
      ], [900, 2520, 3240, 2700]),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 11. LIVE FEATURES
      // ═══════════════════════════════════════════════════════════
      h1("11. Live Demo Features"),
      h2("11.1 Real-Time Agent Streaming (Home Page)"),
      body("The home page (app.py) demonstrates the system’s live AI agent communication. When a demo run is triggered, the system streams token-by-token output from each agent sequentially. Between agents, supervisor direction arrows appear: ‘🧠 Supervisor → 🔍 Research Agent: sending task…’ and then after completion ‘🔍 Research Agent → 🧠 Supervisor: complete · conf 82% · risk 45%’."),
      body("This is powered by st.empty() placeholders that are updated on every token received from the NVIDIA streaming endpoint. The effect is that users watch the AI agent ‘think and write’ in real time, with no pre-cached content — the tokens are live from the model."),
      h2("11.2 Pipeline Visualisation"),
      body("Every matter has a dedicated animated HTML pipeline generated by viz.py. The build_matter_flow_html() function takes a matter object and produces a complete, self-contained HTML page (no external dependencies) that shows:"),
      bullet("Partner node → AI Router node → Junior node"),
      bullet("Four parallel agent nodes (Research, Drafting, Review, Risk) arranged side-by-side"),
      bullet("AI Supervisor node with confidence pill, risk pill, HIGH flag count, and citation count"),
      bullet("Escalation path or auto-accept path based on supervisor decision"),
      bullet("Senior Lawyer node with decision label (APPROVED / REJECTED / PENDING)"),
      body("This HTML is embedded in Streamlit via components.html(), appearing in both the Partner View (inside matter expanders) and the Dashboard (in the Agent Pipeline tab)."),
      h2("11.3 Per-Matter AI Chat"),
      body("The Junior View includes a chat interface for each matter. The chat is scoped to the specific matter: the system prompt includes the client name, matter type, partner instructions, prior AI review results, and current draft. The last 10 conversational turns are passed as message history. This gives the junior lawyer a fully context-aware AI assistant without leaking other client data."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 12. HUMAN CONTROLS AND OVERSIGHT
      // ═══════════════════════════════════════════════════════════
      h1("12. Human Controls and Oversight"),
      h2("12.1 The Oversight Mechanisms"),
      body("The system is designed around the principle that AI assists but humans decide. The following controls are built into every pathway:"),
      spacer(60),
      compTable([
        ["Control",               "Mechanism",                              "Who Exercises It"],
        ["Mode Selection",        "Junior chooses Manual/Hybrid/Autonomous", "Junior Lawyer"],
        ["Senior Approval Gate",  "No matter completes without approval",    "Senior Lawyer"],
        ["Reject + Feedback",     "Return to junior with written notes",     "Senior Lawyer"],
        ["Audit Visibility",      "Full action log visible at all times",    "Partner + Dashboard"],
        ["Confidence Thresholds", "Configurable per-matter in supervisor",   "System (configurable)"],
        ["Override Autonomous",   "Senior always reviews autonomous outputs", "Senior Lawyer"],
      ], [2600, 3760, 3000]),
      spacer(80),
      h2("12.2 The Audit Trail"),
      body("The audit trail is the cornerstone of the oversight mechanism. Every action — whether taken by a human lawyer or an AI agent — is logged via log_event() with the following fields:"),
      bullet("timestamp: ISO 8601 datetime of the action"),
      bullet("actor_type: ‘human’ or ‘ai’ — always explicit"),
      bullet("role: the specific actor (e.g. partner_1, supervisor, research_agent, senior_1)"),
      bullet("detail: a human-readable description of the action (truncated to 80 chars in compact views)"),
      bullet("confidence: where applicable, the AI agent’s confidence score"),
      bullet("risk: where applicable, the AI agent’s risk score"),
      body("The audit trail is visible in the Senior View (last 4 actions), the Partner View (inside matter expanders), and the Dashboard (full audit tab, showing last 5 of N with ‘show all’ in the pipeline viz)."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 13. KEY DESIGN DECISIONS
      // ═══════════════════════════════════════════════════════════
      h1("13. Key Design Decisions"),
      spacer(80),
      h2("13.1 JSON File Store vs. Database"),
      body("We chose a JSON file store (matters.json) rather than a relational database. This decision was deliberate for the hackathon context: it requires no setup, is human-readable, can be committed to version control, and works identically on any machine. The cost is no concurrent write safety for production use, but for a demo system handling one matter at a time, this is acceptable. A PostgreSQL migration path is straightforward: replace store.py with a database-backed version."),
      h2("13.2 asyncio.gather + to_thread for Parallel Agents"),
      body("The four specialist agents must run concurrently to keep latency acceptable. Python’s asyncio.gather() is used to launch all four concurrently. Because the NVIDIA SDK calls are synchronous (they block the thread), each is wrapped in asyncio.to_thread() to avoid blocking the event loop. This pattern is cleaner than ProcessPoolExecutor for I/O-bound operations."),
      h2("13.3 Self-Contained HTML Visualisation"),
      body("The pipeline visualisation in viz.py is a single Python function that returns a complete HTML string with embedded CSS and no external dependencies. This was a deliberate choice: Streamlit’s components.html() embeds the HTML in an iframe, which means it cannot load external scripts. A self-contained approach means the pipeline viz works reliably in any Streamlit deployment, including offline environments."),
      h2("13.4 Light Theme with Semantic Colour Coding"),
      body("The entire UI uses a light theme with a consistent semantic colour palette: blue (#2563EB) for AI actions, green (#16A34A) for human actions, purple (#7C3AED) for the supervisor, red (#DC2626) for HIGH risk/flags, and amber (#D97706) for medium risk/warnings. This colour language is consistent across all views, the pipeline viz HTML, and the supervisor threshold display."),
      spacer(),

      // ═══════════════════════════════════════════════════════════
      // 14. CONCLUSION
      // ═══════════════════════════════════════════════════════════
      h1("14. Conclusion"),
      body("The Legal AI Supervisor directly answers the Clifford Chance hackathon question: ‘How Do We Supervise Legal AI Agents?’ The answer, as embodied in this system, has four components:"),
      spacer(60),
      numbered("Build a Supervisor Loop: not one-shot AI, but a quality gate that enforces thresholds, retries with feedback, and auto-escalates when it cannot achieve the required standard."),
      numbered("Make AI Transparent: surface the model’s reasoning chain (thinking tokens), return structured JSON with explicit confidence and risk scores, and label every action Human or AI in the audit trail."),
      numbered("Give Humans Full Override: senior approval gates are non-negotiable. Junior lawyers choose their own AI involvement level. Partners see everything. No AI output auto-ships."),
      numbered("Make Oversight Auditable: every action, timestamped and actor-typed, logged to a complete audit trail. This is the SRA compliance mechanism — a lawyer can always point to the audit trail and show exactly what was AI-generated, when, and who verified it."),
      spacer(80),
      body("The choice of NVIDIA Nemotron-Ultra as the single underlying model for all four agents and the supervisor provides a significant advantage in this architecture: the model’s thinking tokens enable genuine transparency, its scale (550B parameters) ensures high-quality legal reasoning without fine-tuning, and its OpenAI-compatible API enables real-time streaming that powers the live agent communication demo. A dedicated legal AI agent might perform better on a narrow template task, but it cannot provide the architectural flexibility, transparency, and composability that a supervision framework requires."),
      spacer(80),
      body("This project is a proof-of-concept for how law firms can deploy AI responsibly: not by removing lawyers from the loop, but by giving them better tools to supervise the AI agents working alongside them."),
      spacer(),

      // ── Appendix ──────────────────────────────────────────────
      pageBreak(),
      h1("Appendix: Security Note"),
      body("During development, NVIDIA API keys were pasted into a chat context and must be treated as compromised. Before deploying this system in any environment:"),
      bullet("Regenerate all three NVIDIA API keys at build.nvidia.com"),
      bullet("Update the .env file with the new keys"),
      bullet("Ensure the .env file is in .gitignore and has never been committed to version control"),
      body("Failure to rotate these keys before deployment would give anyone who saw the original chat context access to the NVIDIA API account."),
    ],
  }],
});

Packer.toBuffer(doc).then(buffer => {
  const path = require("path");
  const outPath = path.join(__dirname, "Legal_AI_Supervisor_Report.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("✅  Created: " + outPath);
}).catch(e => console.error("❌ Error:", e));
