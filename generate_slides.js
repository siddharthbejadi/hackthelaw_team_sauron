/**
 * Legal AI Supervisor — Hackathon Presentation
 * Run: node generate_slides.js
 * Requires: npm install -g pptxgenjs
 * Output: Legal_AI_Supervisor_Hackathon.pptx
 */
const pptxgen = require("pptxgenjs");

// ── Palette ────────────────────────────────────────────────────
const C = {
  navy:    "0F172A", navyMid: "1E293B",
  blue:    "2563EB", blueLt:  "DBEAFE",
  purple:  "7C3AED", purpleLt:"EDE9FE",
  green:   "16A34A", greenLt: "DCFCE7",
  red:     "DC2626", redLt:   "FEE2E2",
  amber:   "D97706", amberLt: "FEF3C7",
  white:   "FFFFFF", light:   "F8FAFC",
  slate:   "475569", silver:  "94A3B8",
};
const F = "Calibri";
const makeShadow = () => ({ type:"outer", color:"000000", blur:8, offset:2, angle:45, opacity:0.12 });

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author  = "Legal AI Supervisor";
pres.title   = "Legal AI Supervisor — Clifford Chance Hackathon";

// ═══════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.navy };

  // Motif: three coloured squares top-left
  [[0.45,0.32,C.blue],[0.72,0.32,C.purple],[0.99,0.32,C.green]].forEach(([x,y,c])=>{
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:0.18,h:0.18,fill:{color:c},line:{color:c},rectRadius:0.04});
  });

  s.addText("Legal AI Supervisor",{
    x:0.5,y:0.95,w:9,h:1.1,fontFace:F,fontSize:50,bold:true,color:C.white,align:"left",margin:0
  });
  s.addText("Transparent · Risk-Proportionate · Human-Controlled",{
    x:0.5,y:2.1,w:8,h:0.45,fontFace:F,fontSize:17,color:C.silver,align:"left",margin:0
  });
  s.addShape(pres.shapes.RECTANGLE,{x:0.5,y:2.68,w:3.5,h:0.04,fill:{color:C.blue},line:{color:C.blue}});
  s.addText("Clifford Chance Hackathon  ·  How Do We Supervise Legal AI Agents?",{
    x:0.5,y:2.82,w:9,h:0.38,fontFace:F,fontSize:13,color:C.silver,align:"left",margin:0
  });

  [["🤖","NVIDIA Nemotron-Ultra"],["⚖️","Law Firm Workflow"],["🛡️","AI Transparency"]].forEach(([icon,label],i)=>{
    const x = 0.5 + i*3.1;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:4.38,w:2.82,h:0.72,fill:{color:C.navyMid},line:{color:C.blue+"66"},rectRadius:0.1});
    s.addText(`${icon}  ${label}`,{x,y:4.38,w:2.82,h:0.72,fontFace:F,fontSize:12,color:C.silver,align:"center",valign:"middle",margin:0});
  });
  s.addNotes("Welcome. This presentation covers the full Legal AI Supervisor system built for the Clifford Chance hackathon.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 2 — The Problem
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.navy };

  s.addText("The Problem",{x:0.5,y:0.38,w:9,h:0.6,fontFace:F,fontSize:32,bold:true,color:C.white,align:"left",margin:0});

  const probs = [
    {c:C.red,   bg:"2D0F0F",icon:"⚠️",title:"AI Hallucinations",
     body:"Legal AI agents can fabricate case law citations and produce confident-sounding but incorrect advice — catastrophic in legal practice where liability is real."},
    {c:C.amber, bg:"2D1F00",icon:"🔓",title:"No Oversight Layer",
     body:"Current AI tools operate as black boxes: no confidence scoring, no risk thresholds, no escalation path, no audit trail. Lawyers bear the risk with no visibility."},
    {c:C.blue,  bg:"0D1A3A",icon:"⚖️",title:"Regulation Gap",
     body:"The SRA requires lawyers to verify AI outputs. But no standard workflow exists for AI supervision in law firm practice — leaving firms exposed and non-compliant."},
  ];
  probs.forEach((p,i)=>{
    const x = 0.45 + i*3.13;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:1.15,w:2.9,h:3.75,fill:{color:p.bg},line:{color:p.c},rectRadius:0.12});
    s.addText(p.icon,{x,y:1.25,w:2.9,h:0.6,fontFace:F,fontSize:28,align:"center",margin:0});
    s.addText(p.title,{x:x+0.12,y:1.95,w:2.66,h:0.44,fontFace:F,fontSize:14,bold:true,color:p.c,align:"left",margin:0});
    s.addText(p.body,{x:x+0.12,y:2.44,w:2.66,h:2.28,fontFace:F,fontSize:10.5,color:C.silver,align:"left",valign:"top",margin:0});
  });
  s.addNotes("Three core problems our system solves: hallucinations, no oversight, and the regulatory compliance gap.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 3 — Our Solution
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addText("Our Solution: The Legal AI Supervisor",{x:0.4,y:0.22,w:9.2,h:0.52,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});
  s.addText("A risk-proportionate AI supervision framework for law firm workflows — with human controls at every step.",{
    x:0.4,y:0.78,w:9.2,h:0.38,fontFace:F,fontSize:12,color:C.slate,align:"left",margin:0
  });

  const pillars = [
    {c:C.blue,  bg:C.blueLt, icon:"🧠",title:"AI Transparency",
     body:"Every agent shows its reasoning chain, confidence score (0-100%), risk level, and verified citations — visible to every human actor at every stage."},
    {c:C.purple,bg:C.purpleLt,icon:"🛡️",title:"Supervisor Loop",
     body:"An AI Supervisor orchestrates all agents, retries on low confidence with feedback, and auto-escalates to senior lawyers when risk thresholds are exceeded."},
    {c:C.green, bg:C.greenLt, icon:"✋",title:"Human Override",
     body:"Senior lawyers approve, reject, or modify any AI decision. Partners track every action. Juniors control how much AI involvement they want. Nothing auto-ships."},
    {c:C.amber, bg:C.amberLt, icon:"📊",title:"Full Auditability",
     body:"Every action — Human ✋ or AI 🤖 — logged with timestamp, actor type, confidence %, risk %, and citations. Complete SRA-compliant audit trail per matter."},
  ];
  pillars.forEach((p,i)=>{
    const x = 0.38 + i*2.37;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:1.3,w:2.18,h:3.9,fill:{color:p.bg},line:{color:p.c+"44"},rectRadius:0.12,shadow:makeShadow()});
    s.addText(p.icon,{x,y:1.4,w:2.18,h:0.56,fontFace:F,fontSize:26,align:"center",margin:0});
    s.addText(p.title,{x:x+0.1,y:2.02,w:1.98,h:0.4,fontFace:F,fontSize:12,bold:true,color:p.c,align:"left",margin:0});
    s.addText(p.body,{x:x+0.1,y:2.46,w:1.98,h:2.6,fontFace:F,fontSize:10,color:C.slate,align:"left",valign:"top",margin:0});
  });
  s.addNotes("Four pillars: transparency, supervisor loop, human override, full auditability.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 4 — End-to-End Workflow
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };

  s.addText("End-to-End Workflow",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});

  const steps = [
    {label:"👔 Partner",    sub:"Submits matter\n+ instructions",   c:C.green, bg:C.greenLt},
    {label:"🤖 AI Router",  sub:"Assigns to best\njunior lawyer",   c:C.blue,  bg:C.blueLt},
    {label:"📝 Junior",     sub:"Chooses mode\n& writes/edits",     c:C.green, bg:C.greenLt},
    {label:"🔬 AI Agents",  sub:"4 agents run\nin parallel",        c:C.blue,  bg:C.blueLt},
    {label:"🧠 Supervisor", sub:"Quality gate\n+ decision",         c:C.purple,bg:C.purpleLt},
    {label:"👁️ Senior",     sub:"Approve or\nreject + notes",      c:C.green, bg:C.greenLt},
    {label:"📊 Dashboard",  sub:"Full audit\ntrail logged",         c:C.amber, bg:C.amberLt},
  ];

  const bW=1.14, bH=1.12, startX=0.28, y=0.88, gap=0.14;
  steps.forEach((st,i)=>{
    const x = startX + i*(bW+gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:bW,h:bH,fill:{color:st.bg},line:{color:st.c},rectRadius:0.1,shadow:makeShadow()});
    s.addText(st.label,{x,y:y+0.06,w:bW,h:0.42,fontFace:F,fontSize:9.5,bold:true,color:st.c,align:"center",margin:0});
    s.addText(st.sub,{x,y:y+0.5,w:bW,h:0.56,fontFace:F,fontSize:8.5,color:C.slate,align:"center",valign:"top",margin:0});
    if(i<steps.length-1){
      const ax=x+bW+0.01;
      s.addShape(pres.shapes.LINE,{x:ax,y:y+bH/2,w:gap-0.02,h:0,line:{color:C.silver,width:1.5}});
      s.addText("›",{x:ax+gap-0.15,y:y+bH/2-0.14,w:0.16,h:0.28,fontFace:F,fontSize:14,color:C.silver,margin:0});
    }
  });

  // Step annotations
  const notes2=[
    ["① Partner","Submits client instructions via Partner View. Sets matter type, priority, and team."],
    ["② AI Router","Reads the matter, picks the best junior based on specialisation. Returns structured JSON with reasoning."],
    ["③ Junior Lawyer","Receives matter + instructions. Chooses Manual / Hybrid / Autonomous mode via card UI."],
    ["④ AI Agents","Research, Drafting, Review, Risk Analysis run in parallel. Each returns JSON with confidence + flags."],
    ["⑤ AI Supervisor","Aggregates all agent results. Checks thresholds. Retries if needed. Escalates HIGH-risk to senior."],
    ["⑥ Senior Lawyer","Reviews AI summary, all HIGH flags, and citations. Approves or rejects with written decision."],
    ["⑦ Dashboard","Every action logged — Human ✋ or AI 🤖 — with timestamp, confidence, risk, and citations."],
  ];
  notes2.slice(0,4).forEach(([lbl,txt],i)=>{
    const y2 = 2.18+i*0.74;
    s.addText(lbl,{x:0.38,y:y2,w:1.1,h:0.26,fontFace:F,fontSize:9,bold:true,color:C.navy,align:"left",margin:0});
    s.addText(txt,{x:1.5,y:y2,w:4.1,h:0.68,fontFace:F,fontSize:8.5,color:C.slate,align:"left",valign:"top",margin:0});
  });
  notes2.slice(4).forEach(([lbl,txt],i)=>{
    const y2 = 2.18+i*0.82;
    s.addText(lbl,{x:5.7,y:y2,w:1.1,h:0.26,fontFace:F,fontSize:9,bold:true,color:C.navy,align:"left",margin:0});
    s.addText(txt,{x:6.85,y:y2,w:2.85,h:0.76,fontFace:F,fontSize:8.5,color:C.slate,align:"left",valign:"top",margin:0});
  });
  s.addNotes("Full flow: Partner → AI Router → Junior → 4 parallel AI Agents → Supervisor → Senior → Dashboard.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 5 — Role Architecture
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Role Architecture",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});

  const roles=[
    {icon:"👔",title:"Partner",c:C.green,bg:C.greenLt,name:"Sarah Chen / David Okafor",
     acts:["Submit client matters + detailed instructions","Set matter type, urgency, and team","Track all matters via real-time pipeline viz","Full audit trail: every AI + human action"]},
    {icon:"📝",title:"Junior Lawyer",c:C.blue,bg:C.blueLt,name:"Priya Patel / Tom Davies / Aisha Mensah",
     acts:["Receive routed matters with partner instructions","Choose work mode: Manual / Hybrid / Autonomous","AI chat assistant scoped per matter","Submit draft for AI Supervisor review"]},
    {icon:"👁️",title:"Senior Lawyer",c:C.purple,bg:C.purpleLt,name:"James Wright / Meera Nair",
     acts:["Review AI-summarised flags and risk scores","See all HIGH flags and verified citations","Approve or reject with written decision notes","Feed back to junior if redraft is required"]},
    {icon:"📊",title:"Dashboard",c:C.amber,bg:C.amberLt,name:"Firm-wide visibility layer",
     acts:["Live pipeline view per active matter","Human ✋ vs AI 🤖 labels throughout","Conf %, risk %, HIGH flags at a glance","Full document + audit trail per matter"]},
  ];
  roles.forEach((r,i)=>{
    const x = 0.28+i*2.4;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:0.85,w:2.22,h:4.55,fill:{color:r.bg},line:{color:r.c+"66"},rectRadius:0.12,shadow:makeShadow()});
    s.addText(r.icon,{x,y:0.93,w:2.22,h:0.5,fontFace:F,fontSize:22,align:"center",margin:0});
    s.addText(r.title,{x:x+0.1,y:1.47,w:2.02,h:0.36,fontFace:F,fontSize:13,bold:true,color:r.c,align:"left",margin:0});
    s.addText(r.name,{x:x+0.1,y:1.83,w:2.02,h:0.28,fontFace:F,fontSize:8,color:C.silver,italic:true,align:"left",margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+0.1,y:2.15,w:2.02,h:0.03,fill:{color:r.c+"44"},line:{color:r.c+"44"}});
    r.acts.forEach((a,j)=>{
      s.addText(`• ${a}`,{x:x+0.1,y:2.24+j*0.53,w:2.02,h:0.5,fontFace:F,fontSize:9.5,color:C.slate,align:"left",valign:"top",margin:0});
    });
  });
  s.addNotes("4 roles: Partner (submits), Junior (drafts), Senior (approves), Dashboard (monitors). AI assists at every layer.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 6 — The 4 AI Specialist Agents
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("The 4 AI Specialist Agents",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});
  s.addText("All run in parallel · Each returns structured JSON: output · confidence · risk · citations · flags",{
    x:0.4,y:0.74,w:9.2,h:0.32,fontFace:F,fontSize:11,color:C.slate,align:"left",margin:0
  });

  const agents=[
    {icon:"🔍",name:"Research Agent",    c:C.blue,  bg:C.blueLt,
     role:"Finds UK case law, statutes, and legal principles",
     prompt:'"Never fabricate citations — mark as \'citation unverified\'"',
     outs:["Relevant precedent cases","Applicable statutes (UCTA, GDPR)","Jurisdiction gaps flagged","Unverified citations marked"]},
    {icon:"✍️",name:"Drafting Agent",    c:"9333EA",bg:"FAF5FF",
     role:"Drafts precise contract clauses and legal language",
     prompt:'"Flag every assumption a lawyer must verify"',
     outs:["Professional legal text","Jurisdiction-specific clauses","All assumptions flagged","Redraft-ready output"]},
    {icon:"🔎",name:"Review Agent",      c:C.amber, bg:C.amberLt,
     role:"Reviews documents for errors, gaps, compliance issues",
     prompt:'"Do not give clean bill of health unless genuinely confident"',
     outs:["Issue list with severity","HIGH / MEDIUM / LOW flags","Clause-level analysis","Compliance gap identification"]},
    {icon:"⚠️",name:"Risk Analysis Agent",c:C.red,  bg:C.redLt,
     role:"Identifies and classifies legal risks with legal backing",
     prompt:'"Every risk MUST be backed by statute, case law, or principle"',
     outs:["Risk register with legal basis","Statutory / case references","UNVERIFIED risks flagged","Over-flagging preferred to missing"]},
  ];

  const pos=[[0.3,1.15],[5.18,1.15],[0.3,3.22],[5.18,3.22]];
  agents.forEach((a,i)=>{
    const [x,y]=pos[i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:4.62,h:1.9,fill:{color:a.bg},line:{color:a.c+"66"},rectRadius:0.1,shadow:makeShadow()});
    s.addShape(pres.shapes.OVAL,{x:x+0.12,y:y+0.12,w:0.5,h:0.5,fill:{color:a.c+"22"},line:{color:a.c+"55"}});
    s.addText(a.icon,{x:x+0.12,y:y+0.12,w:0.5,h:0.5,fontFace:F,fontSize:16,align:"center",valign:"middle",margin:0});
    s.addText(a.name,{x:x+0.72,y:y+0.1,w:2.6,h:0.3,fontFace:F,fontSize:12,bold:true,color:a.c,align:"left",margin:0});
    s.addText(a.role,{x:x+0.72,y:y+0.42,w:3.78,h:0.28,fontFace:F,fontSize:9,color:C.slate,align:"left",margin:0});
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:x+0.12,y:y+0.76,w:4.38,h:0.3,fill:{color:a.c+"11"},line:{color:a.c+"33"},rectRadius:0.06});
    s.addText(a.prompt,{x:x+0.18,y:y+0.78,w:4.26,h:0.26,fontFace:F,fontSize:8.5,color:a.c,italic:true,align:"left",margin:0});
    s.addText(`✓ ${a.outs[0]}    ✓ ${a.outs[1]}`,{x:x+0.12,y:y+1.13,w:4.38,h:0.22,fontFace:F,fontSize:8.5,color:C.slate,margin:0});
    s.addText(`✓ ${a.outs[2]}    ✓ ${a.outs[3]}`,{x:x+0.12,y:y+1.37,w:4.38,h:0.22,fontFace:F,fontSize:8.5,color:C.slate,margin:0});
  });
  s.addNotes("4 agents: Research, Drafting, Review, Risk. All use NVIDIA Nemotron-Ultra with specialist system prompts.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 7 — Supervisor Quality Gate
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("AI Supervisor: The Quality Gate",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});

  // Flow diagram (left side)
  const flowItems=[
    {x:0.9, y:0.82,w:3.6,h:0.75,bg:"F5F3FF",bc:C.purple,txt:"🧠 AI SUPERVISOR",tsz:14,tbold:true,tc:C.purple},
    {x:0.9, y:2.08,w:3.6,h:0.72,bg:C.blueLt, bc:C.blue, txt:"🤖 Specialist Agent",tsz:13,tbold:true,tc:C.blue},
    {x:0.98,y:3.22,w:3.44,h:0.72,bg:C.amberLt,bc:C.amber,txt:"📊 Conf ≥ 80%  &  Risk ≤ 20%  &  No HIGH flags?",tsz:10,tbold:true,tc:C.amber},
  ];
  flowItems.forEach(fi=>{
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:fi.x,y:fi.y,w:fi.w,h:fi.h,fill:{color:fi.bg},line:{color:fi.bc},rectRadius:0.1,shadow:makeShadow()});
    s.addText(fi.txt,{x:fi.x,y:fi.y,w:fi.w,h:fi.h,fontFace:F,fontSize:fi.tsz,bold:fi.tbold,color:fi.tc,align:"center",valign:"middle",margin:0});
  });

  // Arrows between flow items
  [[2.7,1.57,0.51,"dispatch"],[2.7,2.8,0.42,"evaluate"]].forEach(([x,y,h,lbl])=>{
    s.addShape(pres.shapes.LINE,{x,y,w:0,h,line:{color:C.purple,width:1.5}});
    s.addText(lbl,{x:x+0.05,y:y+h/2-0.1,w:0.8,h:0.2,fontFace:F,fontSize:7.5,color:C.silver,margin:0});
  });

  // YES branch
  s.addShape(pres.shapes.LINE,{x:4.42,y:3.58,w:0.75,h:0,line:{color:C.green,width:1.5}});
  s.addText("YES",{x:4.48,y:3.36,w:0.6,h:0.22,fontFace:F,fontSize:9,bold:true,color:C.green,margin:0});
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.17,y:3.22,w:1.88,h:0.72,fill:{color:C.greenLt},line:{color:C.green},rectRadius:0.1,shadow:makeShadow()});
  s.addText("✅ ACCEPTED",{x:5.17,y:3.22,w:1.88,h:0.72,fontFace:F,fontSize:12,bold:true,color:C.green,align:"center",valign:"middle",margin:0});

  // NO branch
  s.addShape(pres.shapes.LINE,{x:2.7,y:3.94,w:0,h:0.36,line:{color:C.red,width:1.5}});
  s.addText("NO",{x:2.75,y:4.0,w:0.5,h:0.2,fontFace:F,fontSize:9,bold:true,color:C.red,margin:0});
  [[0.35,4.35,2.1,0.62,C.redLt,C.red,"🔁 Retry with feedback\n(max 3 attempts)"],
   [2.62,4.35,2.18,0.62,C.amberLt,C.amber,"🚩 Escalate to\nSenior Lawyer"]].forEach(([x,y,w,h,bg,bc,txt])=>{
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,fill:{color:bg},line:{color:bc},rectRadius:0.1,shadow:makeShadow()});
    s.addText(txt,{x,y,w,h,fontFace:F,fontSize:10,color:bc,align:"center",valign:"middle",margin:0});
  });

  // Right panel: thresholds
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.45,y:0.82,w:4.2,h:4.35,fill:{color:"F8FAFC"},line:{color:"E2E8F0"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("Supervision Thresholds",{x:5.6,y:0.93,w:3.9,h:0.34,fontFace:F,fontSize:12,bold:true,color:C.navy,margin:0});

  [["Confidence minimum","≥ 80%",C.green],["Risk maximum","≤ 20%",C.green],
   ["HIGH flags","→ auto-escalate",C.red],["Max retries","3 attempts",C.amber],
   ["Post-max action","→ human review",C.purple]].forEach(([lbl,val,col],i)=>{
    const ty=1.36+i*0.47;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.6,y:ty,w:3.9,h:0.4,fill:{color:C.white},line:{color:"E2E8F0"},rectRadius:0.06});
    s.addText(lbl,{x:5.7,y:ty+0.04,w:2.5,h:0.32,fontFace:F,fontSize:10,color:C.slate,margin:0});
    s.addText(val,{x:8.1,y:ty+0.04,w:1.3,h:0.32,fontFace:F,fontSize:10,bold:true,color:col,align:"right",margin:0});
  });

  s.addText("Agent JSON output structure",{x:5.6,y:3.73,w:3.9,h:0.3,fontFace:F,fontSize:10,bold:true,color:C.navy,margin:0});
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.6,y:4.06,w:3.9,h:0.96,fill:{color:C.navyMid},line:{color:C.blue+"44"},rectRadius:0.08});
  s.addText(`{"output":"...", "confidence": 85,\n "risk": 40, "citations": [...],\n "flags": ["HIGH - ...","MEDIUM - ..."]}`,{
    x:5.68,y:4.1,w:3.74,h:0.88,fontFace:"Courier New",fontSize:8.5,color:C.blue,align:"left",valign:"top",margin:0
  });
  s.addNotes("Supervisor loop: dispatch → evaluate → retry (max 3) → escalate. Thresholds: conf≥80%, risk≤20%, no HIGH flags.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 8 — Three Work Modes
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Three Work Modes for Junior Lawyers",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});
  s.addText("Junior chooses the level of AI involvement — AI auto-detects and logs the mode in the audit trail.",{
    x:0.4,y:0.74,w:9.2,h:0.32,fontFace:F,fontSize:11,color:C.slate,align:"left",margin:0
  });

  const modes=[
    {icon:"✋",name:"Manual Mode",c:C.green,bg:C.greenLt,tagline:"Human writes, AI reviews",
     steps:["Junior writes draft independently","Submits to AI Supervisor on completion","Supervisor runs Review + Risk agents only","Senior sees AI flags and approves or rejects"],
     ai:"AI: Review & Risk only"},
    {icon:"🤝",name:"Hybrid Mode",c:C.blue,bg:C.blueLt,tagline:"AI starts, human refines",
     steps:["Junior clicks 'Generate AI Draft'","Drafting agent creates initial text","Junior edits draft in text area","Submit refined draft for supervisor review"],
     ai:"AI: Draft + Review + Risk"},
    {icon:"🤖",name:"Autonomous Mode",c:"9333EA",bg:"FAF5FF",tagline:"AI handles everything",
     steps:["Junior clicks 'Let AI Handle It All'","All 4 agents run in parallel","Supervisor aggregates and summarises","Always escalates to senior — never auto-approved"],
     ai:"AI: All 4 agents"},
  ];
  modes.forEach((m,i)=>{
    const x=0.33+i*3.22;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:1.15,w:3.0,h:4.12,fill:{color:m.bg},line:{color:m.c+"66"},rectRadius:0.12,shadow:makeShadow()});
    s.addText(m.icon,{x,y:1.23,w:3.0,h:0.5,fontFace:F,fontSize:26,align:"center",margin:0});
    s.addText(m.name,{x:x+0.12,y:1.77,w:2.76,h:0.38,fontFace:F,fontSize:14,bold:true,color:m.c,align:"left",margin:0});
    s.addText(m.tagline,{x:x+0.12,y:2.15,w:2.76,h:0.28,fontFace:F,fontSize:9.5,color:C.silver,italic:true,margin:0});
    s.addShape(pres.shapes.RECTANGLE,{x:x+0.12,y:2.47,w:2.76,h:0.03,fill:{color:m.c+"44"},line:{color:m.c+"44"}});
    m.steps.forEach((st,j)=>{
      s.addText(`${j+1}. ${st}`,{x:x+0.12,y:2.55+j*0.38,w:2.76,h:0.35,fontFace:F,fontSize:9.5,color:C.slate,align:"left",valign:"top",margin:0});
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:x+0.12,y:4.57,w:2.76,h:0.38,fill:{color:m.c+"18"},line:{color:m.c+"44"},rectRadius:0.06});
    s.addText(`🤖 ${m.ai}`,{x:x+0.12,y:4.57,w:2.76,h:0.38,fontFace:F,fontSize:9,color:m.c,align:"center",valign:"middle",margin:0});
  });
  s.addNotes("3 modes. Autonomous always requires senior approval — never auto-ships. Mode is auto-detected from action and logged.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 9 — Section: Why NVIDIA Nemotron?
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.navyMid };

  s.addText("Model Selection",{x:0.5,y:1.1,w:9,h:0.44,fontFace:F,fontSize:14,color:C.silver,align:"center",margin:0});
  s.addText("Why NVIDIA Nemotron-Ultra?",{x:0.5,y:1.58,w:9,h:1.0,fontFace:F,fontSize:42,bold:true,color:C.white,align:"center",margin:0});
  s.addText("And why NOT dedicated legal AI agents?",{x:0.5,y:2.68,w:9,h:0.5,fontFace:F,fontSize:20,color:C.silver,align:"center",margin:0});

  [["550B","Parameters"],["Open-Weight","Architecture"],["Reasoning","Tokens Built-in"]].forEach(([v,l],i)=>{
    const x=1.8+i*2.52;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:3.62,w:2.04,h:1.45,fill:{color:"FFFFFF0D"},line:{color:C.blue+"66"},rectRadius:0.1});
    s.addText(v,{x,y:3.7,w:2.04,h:0.62,fontFace:F,fontSize:28,bold:true,color:C.blue,align:"center",margin:0});
    s.addText(l,{x,y:4.34,w:2.04,h:0.38,fontFace:F,fontSize:10,color:C.silver,align:"center",margin:0});
  });
  s.addNotes("Section divider for model selection rationale.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 10 — Dedicated vs Generalised
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Dedicated Legal AI vs. Generalised LLM",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:26,bold:true,color:C.navy,align:"left",margin:0});

  // Left: dedicated agents
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.38,y:0.82,w:4.32,h:4.55,fill:{color:C.redLt},line:{color:C.red+"66"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("⚠️  Dedicated Legal AI Agents",{x:0.52,y:0.92,w:4.0,h:0.38,fontFace:F,fontSize:13,bold:true,color:C.red,margin:0});
  s.addText("e.g. Harvey AI, CoCounsel, Clio Duo",{x:0.52,y:1.32,w:4.0,h:0.28,fontFace:F,fontSize:9,color:C.silver,italic:true,margin:0});

  ["Tailored to legal templates only — rigid scope",
   "Pre-set workflows, hard to customise for hackathon",
   "Closed-source — no reasoning chain visibility",
   "No real-time token streaming available",
   "Expensive API costs ($$$) per query",
   "Cannot expose confidence / risk scores natively",
   "Not open-weight — no self-hosting for demos",
   "Not designed for multi-agent supervisor loops",
  ].forEach((d,i)=>{
    s.addText(`✗  ${d}`,{x:0.52,y:1.68+i*0.4,w:4.0,h:0.36,fontFace:F,fontSize:9.5,color:C.slate,align:"left",valign:"top",margin:0});
  });

  // Right: Nemotron
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.1,y:0.82,w:4.55,h:4.55,fill:{color:C.greenLt},line:{color:C.green+"66"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("✅  NVIDIA Nemotron-Ultra",{x:5.25,y:0.92,w:4.25,h:0.38,fontFace:F,fontSize:13,bold:true,color:C.green,margin:0});
  s.addText("nvidia/nemotron-3-ultra-550b-a55b",{x:5.25,y:1.32,w:4.25,h:0.28,fontFace:F,fontSize:9,color:C.silver,italic:true,margin:0});

  ["Works across ALL agent types with role prompts",
   "System prompts make it a specialist on demand",
   "Streams thinking tokens (reasoning_content)",
   "Structured JSON: confidence, risk, citations, flags",
   "Open-weight via NVIDIA API — hackathon-friendly",
   "Real-time streaming powers live agent UI demo",
   "One model = consistent quality across all agents",
   "550B parameters = deep legal domain knowledge",
  ].forEach((g,i)=>{
    s.addText(`✓  ${g}`,{x:5.25,y:1.68+i*0.4,w:4.25,h:0.36,fontFace:F,fontSize:9.5,color:C.slate,align:"left",valign:"top",margin:0});
  });
  s.addNotes("Dedicated agents are rigid and closed. Nemotron-Ultra is directed by specialist prompts — best of both worlds.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 11 — NVIDIA Nemotron Technical Details
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("NVIDIA Nemotron-Ultra: Technical Details",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:26,bold:true,color:C.navy,align:"left",margin:0});

  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.38,y:0.85,w:5.35,h:4.55,fill:{color:C.blueLt},line:{color:C.blue+"55"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("Model Specifications",{x:0.52,y:0.95,w:5.05,h:0.32,fontFace:F,fontSize:12,bold:true,color:C.blue,margin:0});

  [["Model ID","nvidia/nemotron-3-ultra-550b-a55b"],
   ["Total Parameters","550 Billion (Mixture-of-Experts)"],
   ["Active per Token","~55B — efficient inference via MoE"],
   ["API Endpoint","integrate.api.nvidia.com/v1"],
   ["Compatibility","OpenAI-compatible (drop-in SDK)"],
   ["Reasoning","enable_thinking: True  +  reasoning_budget"],
   ["Streaming","stream=True  →  token-by-token SSE"],
   ["Key Pool","3-key round-robin via _get_client()"],
   ["Context Window","128K tokens"],
  ].forEach(([lbl,val],i)=>{
    const y=1.36+i*0.37;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.52,y,w:5.05,h:0.32,fill:{color:C.white},line:{color:"E2E8F0"},rectRadius:0.06});
    s.addText(lbl,{x:0.62,y:y+0.02,w:1.8,h:0.28,fontFace:F,fontSize:9.5,bold:true,color:C.navyMid,margin:0});
    s.addText(val,{x:2.46,y:y+0.02,w:3.01,h:0.28,fontFace:F,fontSize:9.5,color:C.slate,margin:0});
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.93,y:0.85,w:3.7,h:4.55,fill:{color:C.purpleLt},line:{color:C.purple+"55"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("How We Use It",{x:6.08,y:0.95,w:3.4,h:0.32,fontFace:F,fontSize:12,bold:true,color:C.purple,margin:0});

  [["Thinking Tokens","reasoning_content gives the model's internal thinking chain — shown to lawyers for transparency"],
   ["Specialist Prompts","4 different system prompts = 4 specialists. No fine-tuning required."],
   ["Structured Output","Instructed to return only valid JSON with confidence, risk, citations, flag severity"],
   ["Live Streaming","stream=True yields tokens as they generate — powers the live agent communication home page"],
   ["Rate Limit Pool","_get_client() rotates 3 API keys so parallel agents each use a different key"],
  ].forEach((u,i)=>{
    const y=1.36+i*0.8;
    s.addText(u[0],{x:6.08,y,w:3.4,h:0.28,fontFace:F,fontSize:10,bold:true,color:C.purple,margin:0});
    s.addText(u[1],{x:6.08,y:y+0.28,w:3.4,h:0.46,fontFace:F,fontSize:9,color:C.slate,align:"left",valign:"top",margin:0});
  });
  s.addNotes("Nemotron-Ultra: MoE 550B total, ~55B active. We use thinking tokens, structured JSON, streaming, and 3-key round-robin.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 12 — Full Tech Stack
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Full Tech Stack",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});

  const stacks=[
    {cat:"AI / Model Layer",c:C.blue,bg:C.blueLt,items:[
      ["NVIDIA Nemotron-Ultra","Core LLM for all 4 agents, supervisor, and AI router"],
      ["nvidia-openai SDK","OpenAI-compatible client with streaming and thinking tokens"],
      ["reasoning_content","Thinking tokens expose internal chain-of-thought to lawyers"],
      ["3-key round-robin","_get_client() distributes parallel calls across API keys"],
    ]},
    {cat:"Backend / Orchestration",c:C.purple,bg:C.purpleLt,items:[
      ["FastAPI","REST API with Pydantic models, async endpoints, validation"],
      ["asyncio.gather","Parallel agent execution — all 4 agents truly concurrent"],
      ["store.py + matters.json","Lightweight JSON file-based matter database"],
      ["python-dotenv","Secure API key management via .env file"],
    ]},
    {cat:"Frontend / UI",c:C.green,bg:C.greenLt,items:[
      ["Streamlit","Multi-page app: Partner, Junior, Senior, Dashboard, Live Demo"],
      ["streamlit.components.v1","Embeds self-contained animated HTML pipeline viz"],
      ["st.empty() streaming","Placeholder updated token-by-token for live agent output"],
      ["Custom CSS + Light theme","Colour-coded cards, pills, badges for every role"],
    ]},
    {cat:"Visualisation & Audit",c:C.amber,bg:C.amberLt,items:[
      ["viz.py (custom)","build_matter_flow_html() — animated HTML pipeline per matter"],
      ["CSS @keyframes","pulse + fadein animations for live pipeline feel"],
      ["Colour-coded nodes","Green=Human, Blue=AI, Purple=Supervisor, Red=Escalate"],
      ["Confidence / risk pills","Green ≥70% / Amber ≥50% / Red <50% — colour-coded"],
    ]},
  ];
  stacks.forEach((st,i)=>{
    const col=i%2, row=Math.floor(i/2);
    const x=0.33+col*4.88, y=0.85+row*2.32;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:4.62,h:2.12,fill:{color:st.bg},line:{color:st.c+"55"},rectRadius:0.1,shadow:makeShadow()});
    s.addText(st.cat,{x:x+0.12,y:y+0.1,w:4.38,h:0.3,fontFace:F,fontSize:11,bold:true,color:st.c,margin:0});
    st.items.forEach(([tool,desc],j)=>{
      const ty=y+0.47+j*0.38;
      s.addText(tool,{x:x+0.12,y:ty,w:1.65,h:0.34,fontFace:F,fontSize:9,bold:true,color:C.navyMid,margin:0});
      s.addText(desc,{x:x+1.82,y:ty,w:2.82,h:0.34,fontFace:F,fontSize:9,color:C.slate,margin:0});
    });
  });
  s.addNotes("Full stack: NVIDIA Nemotron + FastAPI + asyncio + Streamlit + custom viz.py pipeline visualisation.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 13 — Architecture & Data Flow
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Architecture & Data Flow",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});

  const layers=[
    {bg:C.greenLt, bc:C.green,  title:"🖥️  Streamlit Frontend",  detail:"app.py · 1_Partner.py · 2_Junior.py · 3_Senior.py · 4_Dashboard.py · viz.py"},
    {bg:C.purpleLt,bc:C.purple, title:"⚡  FastAPI Backend (api.py)",detail:"POST /matters/submit  ·  GET /matters  ·  POST /generate_draft  ·  POST /autonomous  ·  POST /chat  ·  PUT /decision"},
    {bg:C.blueLt,  bc:C.blue,   title:"🤖  agents.py — Supervisor + 4 Agents",detail:"run_supervised_task()  ·  route_matter()  ·  _call_agent()  ·  _get_client() [3-key round-robin]  ·  log_event()"},
    {bg:C.amberLt, bc:C.amber,  title:"🔮  NVIDIA API (integrate.api.nvidia.com/v1)",detail:"nvidia/nemotron-3-ultra-550b-a55b  ·  enable_thinking: True  ·  reasoning_budget: 4096  ·  stream: True"},
  ];
  layers.forEach((l,i)=>{
    const y=0.85+i*0.98;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.35,y,w:9.3,h:0.82,fill:{color:l.bg},line:{color:l.bc+"66"},rectRadius:0.1});
    s.addText(l.title,{x:0.52,y:y+0.08,w:5.5,h:0.3,fontFace:F,fontSize:11,bold:true,color:l.bc,margin:0});
    s.addText(l.detail,{x:0.52,y:y+0.42,w:8.96,h:0.28,fontFace:F,fontSize:8.8,color:C.slate,margin:0});
    if(i<layers.length-1){
      s.addShape(pres.shapes.LINE,{x:5.0,y:y+0.82,w:0,h:0.16,line:{color:C.silver,width:1.5}});
      s.addText("▼",{x:4.86,y:y+0.88,w:0.3,h:0.14,fontFace:F,fontSize:9,color:C.silver,align:"center",margin:0});
    }
  });

  // Bottom row: data stores
  [[0.35,"💾  store.py + matters.json","Matter database — all matters, actions, AI outputs, decisions"],
   [5.0, "📊  viz.py pipeline gen",    "build_matter_flow_html() → animated HTML per matter"]].forEach(([x,title,desc])=>{
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y:4.97,w:4.3,h:0.65,fill:{color:"F8FAFC"},line:{color:"E2E8F0"},rectRadius:0.1});
    s.addText(title,{x:x+0.12,y:5.0,w:4.06,h:0.3,fontFace:F,fontSize:9.5,bold:true,color:C.slate,margin:0});
    s.addText(desc,{x:x+0.12,y:5.32,w:4.06,h:0.22,fontFace:F,fontSize:8.5,color:C.silver,margin:0});
  });
  s.addNotes("4-layer: Streamlit → FastAPI → agents.py → NVIDIA API. Data persisted in JSON. Pipeline viz in viz.py.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 14 — Live Demo Features
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Live Demo Features",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});

  const feats=[
    {icon:"⚡",title:"Real-Time Agent Streaming",c:C.blue,bg:C.blueLt,
     body:"Home page shows token-by-token output from each agent live. You watch NVIDIA Nemotron-Ultra 'think and write' in real time using stream=True and st.empty() placeholders updated on every token.",
     code:"stream_agent_live() yields\ntokens from NVIDIA SSE"},
    {icon:"🔀",title:"Agent Communication Arrows",c:C.purple,bg:C.purpleLt,
     body:"Between each agent's output, direction arrows appear: '🧠 Supervisor → 🔍 Research: sending…' then '🔍 Research → 🧠 Supervisor: complete · conf 82% · risk 45%'. Visible inter-agent communication.",
     code:"send_placeholder updated\nbefore + after each agent"},
    {icon:"🗺️",title:"Pipeline Visualisation",c:C.green,bg:C.greenLt,
     body:"Every matter has an animated HTML pipeline showing the full flow — Partner, Router, Junior, 4 parallel agents side-by-side, Supervisor decision, Escalation flags, Senior approval — all with live confidence pills.",
     code:"build_matter_flow_html()\ncomponents.html() embed"},
    {icon:"💬",title:"Per-Matter AI Chat",c:C.amber,bg:C.amberLt,
     body:"Each junior has a scoped AI chat for their specific matter. The assistant has full matter context (client, instructions, prior review) as its system prompt. Last 10 turns sent as conversation history.",
     code:"POST /matters/chat\nfull matter as system prompt"},
  ];
  feats.forEach((f,i)=>{
    const x=0.33+(i%2)*4.88, y=0.85+Math.floor(i/2)*2.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:4.62,h:2.15,fill:{color:f.bg},line:{color:f.c+"55"},rectRadius:0.1,shadow:makeShadow()});
    s.addText(`${f.icon} ${f.title}`,{x:x+0.12,y:y+0.1,w:4.38,h:0.36,fontFace:F,fontSize:12,bold:true,color:f.c,margin:0});
    s.addText(f.body,{x:x+0.12,y:y+0.5,w:2.88,h:1.5,fontFace:F,fontSize:9.5,color:C.slate,align:"left",valign:"top",margin:0});
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:x+3.08,y:y+0.5,w:1.42,h:1.5,fill:{color:C.navyMid},line:{color:f.c+"44"},rectRadius:0.08});
    s.addText(f.code,{x:x+3.14,y:y+0.6,w:1.3,h:1.3,fontFace:"Courier New",fontSize:8.5,color:f.c,align:"left",valign:"top",margin:0});
  });
  s.addNotes("4 live features: token streaming, agent arrows, pipeline viz, per-matter AI chat.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 15 — Human Control & Auditability
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.light };
  s.addText("Human Control & Full Auditability",{x:0.4,y:0.22,w:9.2,h:0.5,fontFace:F,fontSize:27,bold:true,color:C.navy,align:"left",margin:0});
  s.addText("Every AI decision is reversible. Every action is logged. Lawyers stay in control.",{
    x:0.4,y:0.74,w:9.2,h:0.32,fontFace:F,fontSize:11,color:C.slate,margin:0
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:0.35,y:1.15,w:4.55,h:4.15,fill:{color:C.greenLt},line:{color:C.green+"66"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("✋  Human Override Controls",{x:0.5,y:1.25,w:4.25,h:0.36,fontFace:F,fontSize:13,bold:true,color:C.green,margin:0});

  [["Senior Approval Gate","No matter completes without senior lawyer sign-off — always"],
   ["Reject + Feedback","Senior rejects draft and sends notes back to junior for redraft"],
   ["Mode Selection","Junior chooses Manual/Hybrid/Autonomous — always their decision"],
   ["Configurable Thresholds","Conf/risk thresholds adjustable per matter and client sensitivity"],
   ["Never Auto-Ship","Autonomous mode ALWAYS goes to senior — no auto-completion"],
   ["Partner Visibility","Partner sees every action and can intervene at any stage"],
  ].forEach(([lbl,desc],i)=>{
    const y=1.7+i*0.56;
    s.addText(lbl,{x:0.5,y,w:4.25,h:0.26,fontFace:F,fontSize:10,bold:true,color:C.navyMid,margin:0});
    s.addText(desc,{x:0.5,y:y+0.26,w:4.25,h:0.24,fontFace:F,fontSize:9,color:C.slate,margin:0});
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.1,y:1.15,w:4.55,h:4.15,fill:{color:C.blueLt},line:{color:C.blue+"66"},rectRadius:0.12,shadow:makeShadow()});
  s.addText("📋  Audit Trail: Every Action Logged",{x:5.25,y:1.25,w:4.25,h:0.36,fontFace:F,fontSize:13,bold:true,color:C.blue,margin:0});

  [
    {badge:"Human",c:C.green, bg:C.greenLt,  text:"Partner submitted instructions for Nexus Ltd"},
    {badge:"AI",   c:C.blue,  bg:C.blueLt,   text:"Router → assigned Priya Patel (junior_1)"},
    {badge:"Human",c:C.green, bg:C.greenLt,  text:"Junior selected Hybrid mode"},
    {badge:"AI",   c:C.purple,bg:C.purpleLt, text:"Supervisor: 6 HIGH flags, risk 80%, conf 85%"},
    {badge:"AI",   c:C.red,   bg:C.redLt,    text:"Escalated to senior — threshold exceeded"},
    {badge:"Human",c:C.green, bg:C.greenLt,  text:"James Wright approved — UCTA analysis sound"},
  ].forEach((e,i)=>{
    const y=1.7+i*0.54;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.25,y,w:4.25,h:0.46,fill:{color:C.white},line:{color:"E2E8F0"},rectRadius:0.06});
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:5.33,y:y+0.08,w:0.7,h:0.3,fill:{color:e.bg},line:{color:e.c+"55"},rectRadius:0.04});
    s.addText(e.badge,{x:5.33,y:y+0.08,w:0.7,h:0.3,fontFace:F,fontSize:7.5,bold:true,color:e.c,align:"center",valign:"middle",margin:0});
    s.addText(e.text,{x:6.1,y:y+0.08,w:3.3,h:0.3,fontFace:F,fontSize:9,color:C.slate,align:"left",valign:"middle",margin:0});
  });
  s.addNotes("Human controls: senior gate, reject, mode choice, configurable thresholds. Audit trail labels every action Human or AI.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 16 — Key Innovations
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.navy };
  s.addText("Key Innovations",{x:0.4,y:0.28,w:9.2,h:0.58,fontFace:F,fontSize:34,bold:true,color:C.white,align:"left",margin:0});

  [
    {num:"01",icon:"🔁",title:"Supervisor Retry Loop",c:C.blue,
     body:"Not one-shot AI. If confidence <80% or risk >20%, the supervisor sends structured feedback and retries up to 3 times before escalating. No current legal AI tool does this."},
    {num:"02",icon:"⚡",title:"Live Token Streaming UI",c:C.purple,
     body:"Home page shows actual token-by-token inter-agent communication — not a simulation. You watch Nemotron-Ultra think in real time with supervisor↔agent direction arrows."},
    {num:"03",icon:"🎛️",title:"Risk-Proportionate Modes",c:C.green,
     body:"The same system adapts: manual for low-risk, hybrid assistance for complex clauses, or fully autonomous for initial analysis — all with complete audit logging of the mode chosen."},
    {num:"04",icon:"🗺️",title:"Self-Contained Pipeline Viz",c:C.amber,
     body:"build_matter_flow_html() generates a fully animated, self-contained HTML pipeline for any matter — showing every node (Human/AI), confidence pills, HIGH flags, and citations."},
  ].forEach((inv,i)=>{
    const x=0.38+(i%2)*4.88, y=1.05+Math.floor(i/2)*2.12;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:4.62,h:1.92,fill:{color:"FFFFFF0D"},line:{color:inv.c+"66"},rectRadius:0.12});
    s.addText(inv.num,{x:x+0.12,y:y+0.1,w:0.6,h:0.5,fontFace:F,fontSize:28,bold:true,color:inv.c,margin:0});
    s.addText(inv.icon,{x:x+0.76,y:y+0.1,w:0.5,h:0.5,fontFace:F,fontSize:24,margin:0});
    s.addText(inv.title,{x:x+0.12,y:y+0.64,w:4.38,h:0.34,fontFace:F,fontSize:13,bold:true,color:C.white,margin:0});
    s.addText(inv.body,{x:x+0.12,y:y+1.0,w:4.38,h:0.82,fontFace:F,fontSize:9.5,color:C.silver,align:"left",valign:"top",margin:0});
  });
  s.addNotes("4 key innovations: supervisor retry loop, live streaming UI, risk-proportionate modes, pipeline visualisation.");
}

// ═══════════════════════════════════════════════════════════════
// SLIDE 17 — Conclusion
// ═══════════════════════════════════════════════════════════════
{
  let s = pres.addSlide();
  s.background = { color: C.navyMid };

  s.addText("Legal AI Supervisor",{x:0.5,y:0.65,w:9,h:0.92,fontFace:F,fontSize:44,bold:true,color:C.white,align:"center",margin:0});
  s.addText("Answering the hackathon question:",{x:0.5,y:1.65,w:9,h:0.36,fontFace:F,fontSize:14,color:C.silver,align:"center",margin:0});
  s.addText('"How Do We Supervise Legal AI Agents?"',{x:0.5,y:2.05,w:9,h:0.52,fontFace:F,fontSize:20,bold:true,color:C.blue,align:"center",margin:0});

  [["🧠","By building an AI Supervisor that enforces confidence & risk thresholds automatically"],
   ["✋","By giving lawyers full override at every stage — no AI action is irreversible"],
   ["📋","By logging every AI and human action with full transparency and SRA-compliant audit trail"],
   ["⚡","By showing AI agent communication live in the UI — absolutely no black boxes"],
  ].forEach((a,i)=>{
    const x=0.5+(i%2)*4.65, y=2.8+Math.floor(i/2)*0.7;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w:4.35,h:0.58,fill:{color:"FFFFFF0F"},line:{color:C.blue+"44"},rectRadius:0.08});
    s.addText(`${a[0]}  ${a[1]}`,{x:x+0.12,y,w:4.11,h:0.58,fontFace:F,fontSize:11,color:C.white,align:"left",valign:"middle",margin:0});
  });

  s.addText("NVIDIA Nemotron-Ultra 550B  ·  FastAPI  ·  Streamlit  ·  Clifford Chance Hackathon",{
    x:0.5,y:5.1,w:9,h:0.3,fontFace:F,fontSize:10,color:C.silver,align:"center",margin:0
  });
  s.addNotes("Conclusion: we answer the hackathon theme through 4 mechanisms.");
}

// ── Write file ─────────────────────────────────────────────────
const path = require("path");
const outPath = path.join(__dirname, "Legal_AI_Supervisor_Hackathon.pptx");
pres.writeFile({ fileName: outPath })
  .then(()=>{ console.log("✅  Created: " + outPath); })
  .catch(e=>{ console.error("❌ Error:", e); });
