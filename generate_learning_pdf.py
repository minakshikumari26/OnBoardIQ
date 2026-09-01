"""Generate a comprehensive 1-week learning roadmap PDF for OnBoardIQ."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether,
)
from reportlab.lib.enums import TA_JUSTIFY

OUTPUT = "/Users/minakshikumari/Library/CloudStorage/OneDrive/Desktop/OnBoardIQ_Learning_Roadmap.pdf"

styles = getSampleStyleSheet()
title_style = ParagraphStyle("TitleBig", parent=styles["Title"], fontSize=22,
    leading=26, textColor=colors.HexColor("#0B3D91"), spaceAfter=12)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, leading=20,
    textColor=colors.HexColor("#0B3D91"), spaceBefore=14, spaceAfter=8)
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, leading=17,
    textColor=colors.HexColor("#1F4E79"), spaceBefore=10, spaceAfter=6)
h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, leading=14,
    textColor=colors.HexColor("#2E5F8A"), spaceBefore=6, spaceAfter=3)
body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5,
    leading=14.5, alignment=TA_JUSTIFY, spaceAfter=5)
bullet = ParagraphStyle("Bullet", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=2)
note = ParagraphStyle("Note", parent=body, textColor=colors.HexColor("#7A4E00"),
    backColor=colors.HexColor("#FFF7E0"), borderPadding=6,
    leftIndent=6, rightIndent=6, spaceBefore=6, spaceAfter=6)
code = ParagraphStyle("Code", parent=styles["Code"], fontSize=9, leading=12,
    backColor=colors.HexColor("#F2F2F2"), borderPadding=6,
    leftIndent=6, rightIndent=6, spaceBefore=4, spaceAfter=6)
mod = ParagraphStyle("Mod", parent=body, fontSize=10, leading=13.5,
    leftIndent=8, spaceAfter=6)

story = []

def P(txt, style=body): story.append(Paragraph(txt, style))
def SP(pts=6): story.append(Spacer(1, pts))
def bullets(items):
    story.append(ListFlowable(
        [ListItem(Paragraph(t, bullet), leftIndent=10) for t in items],
        bulletType="bullet", start="•"))

# ========================= Cover =========================
P("OnBoardIQ", title_style)
P("A 1-Week Learning Roadmap for a Complete Beginner", h1)
P("Project: <b>AI-powered Account Onboarding platform</b> using LangChain + "
  "LangGraph multi-agent orchestration, FastAPI, Streamlit, PostgreSQL, "
  "Tesseract OCR, and the OpenSanctions API. This guide covers <b>every "
  "module</b> in the repository and a day-by-day plan to go from zero to "
  "interview-ready in seven days.")

P("Is one week enough?", h2)
P("<b>Yes — for an interview.</b> One week is enough to <i>run</i> the "
  "project, <i>read</i> the code end-to-end, and <i>explain</i> the "
  "architecture confidently. It is not enough to become an expert in every "
  "underlying technology. Aim for <b>working comprehension</b>, not mastery.")
P("<b>If you already know Python:</b> 7 days is realistic.<br/>"
  "<b>If Python is also new:</b> budget 2 weeks — spend week 1 on Python.",
  note)

# ========================= Prerequisites =========================
P("Prerequisites (before Day 1)", h1)
bullets([
    "Basic Python: variables, functions, dicts/lists, imports, virtualenv.",
    "Terminal basics: <code>cd</code>, <code>ls</code>, running Python scripts.",
    "Git basics: clone, branch, commit.",
    "Any editor (VS Code recommended).",
    "Installed locally: Python 3.11, PostgreSQL 14+, Docker (optional), Tesseract OCR.",
])

# ========================= Big picture =========================
P("The 5-Minute Big Picture", h1)
P("OnBoardIQ takes a loan/account applicant's data (name, PAN, Aadhaar, DOB, "
  "income, employment, ID document image) and runs it through a chain of "
  "specialist AI agents to produce a decision: <b>Approved</b>, "
  "<b>Rejected</b>, or <b>Review</b>. The agents run inside a "
  "<b>LangGraph state machine</b> with short-circuit edges — if KYC fails, "
  "later agents are skipped to save API calls.")

data = [
    ["Layer", "Technology", "Files"],
    ["UI", "Streamlit (port 8501)", "ui/app.py, ui/pages/admin_dashboard.py"],
    ["API", "FastAPI (port 8000)", "backend/api/main.py, backend/api/routes/*"],
    ["Service", "Plain Python", "backend/services/onboarding_service.py"],
    ["Orchestrator", "LangGraph state machine", "backend/agents/orchestrator_agent.py"],
    ["Agents", "Rules + OCR + external API", "backend/agents/{kyc,document,compliance,risk}_agent.py"],
    ["LLM (optional)", "Groq (Llama 3.3 70B)", "explain node in orchestrator"],
    ["Database", "PostgreSQL 15", "backend/db/*"],
    ["Config", "python-dotenv", "backend/config/settings.py, .env"],
    ["Tests", "pytest + pytest-mock", "tests/*"],
    ["Deploy", "Docker Compose", "Dockerfile, Dockerfile.ui, docker-compose.yml"],
]
tbl = Table(data, colWidths=[3.0*cm, 5.5*cm, 8.7*cm])
tbl.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0B3D91")),
    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTSIZE",(0,0),(-1,-1),9.2),
    ("GRID",(0,0),(-1,-1),0.4,colors.grey),
    ("VALIGN",(0,0),(-1,-1),"TOP"),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke,colors.HexColor("#EEF3FA")]),
    ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
    ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
]))
story.append(tbl); SP(8)

P("Request flow", h2)
P("<b>Streamlit form &rarr; POST /onboarding/apply &rarr; "
  "onboarding_service.process_onboarding &rarr; run_agents (LangGraph) &rarr; "
  "kyc &rarr; document &rarr; compliance &rarr; risk &rarr; decide &rarr; "
  "explain (LLM) &rarr; save to Postgres &rarr; JSON response &rarr; UI renders.</b>")

story.append(PageBreak())

# ========================= Every Module =========================
P("Every Module in the Repo", h1)
P("This section is the reference. On Day 6 you should be able to explain "
  "any file below in one sentence without opening it.")

def module(path, what, key, note_txt):
    P(f"<b>{path}</b>", h3)
    P(f"<b>What:</b> {what}", mod)
    P(f"<b>Key:</b> {key}", mod)
    P(f"<b>Beginner note:</b> {note_txt}", mod)

# --- Root ---
P("Root files", h2)
module("README.md",
    "Comprehensive project overview: features, architecture, tech stack, setup.",
    "Diagrams of agent pipeline, LangGraph state machine, tech stack list.",
    "Read this first. The 'How a request flows' section is the whole app in one page.")
module("CLAUDE.md",
    "Guidance file for Claude Code with commands, DB structure, and architecture notes.",
    "Commands: uvicorn, streamlit, pytest. Lists 'things that will trip you up'.",
    "Slightly out of date vs. the code, but the gotchas section is gold.")
module("DEPLOYMENT.md",
    "Step-by-step free-tier deployment guide: Neon (Postgres) + Render (API) + Streamlit Cloud (UI).",
    "Docker build, env vars, 750 hrs/month Render free tier, cold-start ~30 s.",
    "Skip on day 1. Return on day 7 only if the interview asks about deployment.")
module("requirements.txt",
    "Pinned Python dependencies for pip.",
    "FastAPI 0.110, Streamlit 1.35, psycopg2-binary, pytesseract, langchain, langgraph, pytest.",
    "If pip install fails on psycopg2, try <code>psycopg2-binary</code> instead.")
module("environment.yml",
    "Conda environment definition (Python 3.11) — installs Tesseract binary automatically.",
    "Mirrors requirements.txt; adds tesseract from conda-forge; LangChain via pip.",
    "Recommended over pip because it handles the Tesseract native binary for you.")
module("pytest.ini",
    "Pytest configuration for test discovery and output formatting.",
    "testpaths=tests, python_files=test_*.py, addopts=-v --tb=short.",
    "You rarely edit this. Just know it points pytest to the <code>tests/</code> folder.")
module("Dockerfile",
    "Docker image for the FastAPI backend.",
    "python:3.11-slim base, installs tesseract-ocr + libpq-dev + gcc, runs uvicorn on port 8000.",
    "System deps matter — Tesseract binary and Postgres client libs are installed before pip.")
module("Dockerfile.ui",
    "Lightweight Docker image for the Streamlit UI.",
    "python:3.11-slim, only Streamlit + requests + pandas, port 8501.",
    "UI image is thin because it only makes HTTP calls to the backend.")
module("docker-compose.yml",
    "Orchestration for three services: Postgres, backend API, Streamlit UI.",
    "postgres:15-alpine with named volume, backend depends on healthy DB, UI depends on backend.",
    "<code>docker compose up --build</code> starts everything. Schema auto-loads from schema.sql.")
module(".env.example",
    "Template environment file listing required secrets/config.",
    "GROQ_API_KEY (optional — enables LLM explanation node).",
    "Copy to <code>.env</code>. Without a Groq key the pipeline still works; only the explanation is skipped.")

# --- backend/api ---
P("backend/api/", h2)
module("main.py",
    "FastAPI app entry point. Mounts the three route modules and a health check.",
    "app = FastAPI(title='OnBoardIQ'); include_router(customer/onboarding/admin); GET / returns health.",
    "Thin composition file. No business logic here — real code is in routes and services.")
module("routes/customer.py",
    "Customer registration + lookup endpoints; defines Pydantic input schema.",
    "POST /customer/register (CustomerRegister model), GET /customer/{pan} → 404 if missing.",
    "The Pydantic model is where input validation happens — trust nothing from the client.")
module("routes/onboarding.py",
    "Main workflow endpoint — accepts form fields + uploaded document, runs the agent pipeline.",
    "POST /onboarding/apply with multipart form + UploadFile; calls process_onboarding(); returns full decision JSON.",
    "<code>await document.read()</code> is how a Streamlit-uploaded file becomes bytes here.")
module("routes/admin.py",
    "Admin-only list endpoints for the dashboard.",
    "GET /admin/customers, GET /admin/applications (joined with customers).",
    "No auth. In a real system, add JWT or role checks — mention this in interviews.")

# --- backend/agents ---
P("backend/agents/", h2)
module("orchestrator_agent.py",
    "LangGraph state machine wiring the 6 nodes and conditional (short-circuit) edges.",
    "OnboardingState TypedDict, nodes: run_kyc → run_document → run_compliance → run_risk → decide → explain. run_agents(data) returns the final state dict.",
    "The graph is compiled once at import time. Short-circuit edges skip later agents when KYC fails, document is invalid, or compliance is flagged.")
module("kyc_agent.py",
    "Identity validation — PAN, Aadhaar, mobile, age, name match.",
    "evaluate_kyc(data): PAN 10 chars, Aadhaar 12 digits (optional), mobile 10 digits, age ≥ 18, name match against DB. Returns kyc_status + reason.",
    "Format checks happen before DB lookup. DB errors are caught silently — onboarding continues.")
module("document_agent.py",
    "OCR-based document verification. Extracts PAN/DOB/Aadhaar from an ID image and matches against applicant input.",
    "Regex patterns for PAN/DOB/AADHAAR. _extract_fields(text). verify_document(data) → 'valid' / 'invalid' / 'unreadable'.",
    "Uses Tesseract (Python binding: <code>pytesseract</code>). OCR failure returns 'unreadable' (pipeline continues); PAN/name mismatch is 'invalid' (short-circuit).")
module("compliance_agent.py",
    "AML/sanctions screening via the public OpenSanctions API.",
    "check_compliance(data) → HTTP GET to api.opensanctions.org, 5 s timeout, matches with score > 0.7. Returns 'flagged' or 'clear' + matches list.",
    "Network errors fall back to 'clear' so the pipeline never hangs. Empty name skips the API call entirely.")
module("risk_agent.py",
    "Rule-based risk scoring — combines age, income, employment, KYC, and document quality into a 0-100 score.",
    "assess_risk(data) starts at 50, applies factor deltas, clips to [0,100]. Thresholds: ≥70 Low, 45-69 Medium, <45 High. Returns risk_level, risk_score, factors list.",
    "Deterministic — no randomness, no external calls. Factors are surfaced to the UI so users see WHY they scored what they did.")

# --- backend/db ---
P("backend/db/", h2)
module("connection.py",
    "Factory for psycopg2 database connections.",
    "get_connection() reads DB_* env vars from settings and returns a new connection.",
    "No connection pooling — every query opens/closes its own connection. Fine for a demo, not for production scale.")
module("queries.py",
    "All SQL lives here. CRUD for customers, applications, documents + list views for the admin dashboard.",
    "get_customer_by_pan, insert_customer, save_application, save_document, list_customers, list_applications (JOIN).",
    "Parameterized queries — safe from SQL injection. Column order matters: the UI unpacks list results by tuple index.")
module("schema.sql",
    "DDL to create the three tables. Auto-loaded by Postgres on first docker compose up.",
    "customers (PAN UNIQUE), onboarding_applications (FK to customers, one row per attempt), documents (FK to application).",
    "PAN uniqueness means one PAN = one customer, but a customer can have many applications.")

# --- backend/services ---
P("backend/services/", h2)
module("onboarding_service.py",
    "Business-logic layer between routes and agents. Parses dates, masks Aadhaar, calls run_agents, persists results.",
    "_parse_dob (age calc), _mask_aadhaar (XXXX-XXXX-1234), register_new_customer, process_onboarding.",
    "Services should stay thin — they translate HTTP inputs to agent payloads and persist outputs. Real logic lives in agents.")

# --- backend/config ---
P("backend/config/", h2)
module("settings.py",
    "Central configuration loader. Reads env vars with sensible defaults.",
    "DB_NAME='loan_db', DB_USER='postgres', DB_PASSWORD='0921', DB_HOST='localhost'. GROQ_API_KEY, LLM_MODEL='llama-3.3-70b-versatile'. OPENSANCTIONS_API_URL + timeout.",
    "In production, remove default password and require env vars to be set explicitly.")

# --- UI ---
P("ui/", h2)
module("app.py",
    "Main Streamlit onboarding wizard. Two-column layout: form left, results right.",
    "Form (name/pan/aadhaar/dob/income/employment + document upload) → POST /onboarding/apply → renders decision banner, agent metrics, OCR text, risk factors chart.",
    "Streamlit re-runs the whole script on every interaction. The <code>if submit:</code> block only runs when the user clicks Submit.")
module("pages/admin_dashboard.py",
    "Streamlit admin page: system stats, customer list, application list with filters.",
    "fetch_customers() and fetch_applications() call /admin/*. @st.cache_data(ttl=30) caches results 30 s. Filter dropdown by decision.",
    "Files inside <code>ui/pages/</code> become extra pages automatically — Streamlit convention.")

# --- Notebooks ---
P("notebooks/", h2)
module("seed_customers.py",
    "One-shot script to populate the customers table with 50 fake Indian applicants using Faker.",
    "fake_pan(), fake_aadhaar_masked(), loops insert_customer() with realistic names, ages 21-65, incomes 15k-200k.",
    "Run once before showing the admin dashboard: <code>python notebooks/seed_customers.py</code>.")

# --- Tests ---
P("tests/", h2)
module("conftest.py",
    "Shared pytest fixtures: reusable test data payloads and mocked API responses.",
    "valid_applicant, mock_pan_card_text, sanctions_hit_response, sanctions_clear_response.",
    "Fixtures are injected into tests by argument name — you don't import them.")
module("test_orchestrator.py",
    "Integration tests for the LangGraph pipeline: happy path + all short-circuit branches.",
    "5 tests: happy path, KYC fail, document fail, sanctions hit, processing time reported.",
    "All external calls (DB, Tesseract, OpenSanctions, LLM) are mocked. Tests run in 1-2 s.")
module("test_kyc_agent.py",
    "Unit tests for identity validation.",
    "8 tests: PAN length, Aadhaar digits, mobile format, underage, name mismatch, DB down, empty optional fields.",
    "Every validation rule is isolated to a single test. Read these to <i>learn</i> the rules.")
module("test_document_agent.py",
    "Unit tests for OCR regex extraction and document verification.",
    "11 tests split across TestExtractFields and TestVerifyDocument.",
    "Regex tests use word boundaries to ensure long alphanumerics don't false-match a PAN.")
module("test_risk_agent.py",
    "Unit tests for risk scoring.",
    "5 tests: low-risk profile, high-risk profile, score bounds, factors reported, government-employment boost.",
    "Deterministic — no mocks needed. These tests <b>are</b> the specification of the scoring rules.")
module("test_compliance_agent.py",
    "Unit tests for AML sanctions screening.",
    "5 tests: no matches, high-score match, low-score match ignored, network fallback, empty name skip.",
    "OpenSanctions API is mocked. Verifies the pipeline never crashes on network errors.")

story.append(PageBreak())

# ========================= Day plan =========================
P("The 7-Day Plan", h1)
P("Each day = 4-6 focused hours. Each day ends with a concrete deliverable "
  "you can show. Do not skip Days 1-2 — they are load-bearing.")

def day(num, title, goal, learn, do, deliverable):
    story.append(KeepTogether([Paragraph(f"Day {num} — {title}", h2)]))
    P(f"<b>Goal:</b> {goal}")
    P("<b>Learn:</b>"); bullets(learn)
    P("<b>Do:</b>"); bullets(do)
    P(f"<b>Deliverable:</b> {deliverable}")

day(1, "Python + HTTP + FastAPI basics",
    "Run the API and hit one endpoint.",
    ["Python: functions, type hints, dict/list, exceptions, venv.",
     "HTTP: methods (GET/POST), paths, JSON body, status codes.",
     "FastAPI: <code>@app.get</code>, <code>@app.post</code>, Pydantic models, auto-docs at <code>/docs</code>."],
    ["Install deps, then <code>uvicorn backend.api.main:app --reload</code>.",
     "Open <code>http://127.0.0.1:8000/docs</code>. Click every endpoint.",
     "Skim <code>backend/api/main.py</code> and each file in <code>backend/api/routes/</code>."],
    "You can describe every endpoint in one sentence.")

day(2, "PostgreSQL + the data model",
    "Understand the three tables and where data flows in and out.",
    ["SQL: <code>SELECT</code>, <code>INSERT</code>, <code>WHERE</code>, light joins.",
     "psycopg2: connect, cursor, execute, commit, fetchall.",
     "The three tables: customers, onboarding_applications, documents."],
    ["Load <code>backend/db/schema.sql</code> into <code>loan_db</code>.",
     "Read <code>connection.py</code>, <code>queries.py</code>, <code>schema.sql</code>.",
     "Run <code>python notebooks/seed_customers.py</code> to insert 50 fake customers.",
     "Query them with <code>psql</code> or DBeaver."],
    "50 customer rows visible in Postgres, and you can name every column.")

day(3, "Streamlit UI end-to-end",
    "Submit an application through the UI and trace it from click to database.",
    ["Streamlit basics: <code>st.text_input</code>, <code>st.form</code>, <code>st.file_uploader</code>, <code>st.metric</code>, pages.",
     "How the UI calls the API: <code>requests.post()</code> with hardcoded URL.",
     "Session state and re-runs — Streamlit reruns the whole script on any interaction."],
    ["With the API running, <code>streamlit run ui/app.py</code>.",
     "Submit an application. Watch logs on both servers.",
     "Open <code>ui/pages/admin_dashboard.py</code> — refresh and see your application."],
    "A screenshot of a decision (Approved/Rejected/Review) rendered in the UI.")

day(4, "The four agents — what each check does",
    "Read every agent and predict its output on paper.",
    ["KYC: format validation + name match against DB.",
     "Document: Tesseract OCR + regex extraction + field matching.",
     "Compliance: OpenSanctions API + score threshold 0.7.",
     "Risk: rule-based additive scoring (starts at 50, thresholds 45/70)."],
    ["Read each agent file (<code>kyc/document/compliance/risk_agent.py</code>).",
     "Craft applicant payloads that produce every possible verdict.",
     "Run the pytest for each agent: <code>pytest tests/test_kyc_agent.py -v</code>."],
    "4 example payloads that produce 4 different outcomes, with your explanation of why.")

day(5, "The orchestrator — LangGraph state machine",
    "Understand why this is called 'agentic' and how nodes/edges compose the workflow.",
    ["What LangGraph is: a graph of nodes (functions) connected by edges (routing rules).",
     "Conditional edges: how <code>kyc_status == 'failed'</code> skips ahead to <code>decide</code>.",
     "The 6 nodes: run_kyc, run_document, run_compliance, run_risk, decide, explain.",
     "Why short-circuiting matters: fewer API calls, lower cost, faster response."],
    ["Read <code>orchestrator_agent.py</code> top-to-bottom.",
     "Draw the graph on paper: 6 nodes + 3 short-circuit edges.",
     "Run <code>pytest tests/test_orchestrator.py -v</code> and read what each test asserts."],
    "A one-page diagram of the state machine + your own words on when each short-circuit fires.")

day(6, "Full-stack integration + the sharp edges",
    "See the whole system as one thing, know where it breaks.",
    ["Model/config coupling: env vars in settings.py drive everything.",
     "UI ↔ API coupling by column order — changing SELECT * breaks the UI silently.",
     "Optional dependencies: Groq LLM is optional; OCR falls back to 'unreadable'; sanctions falls back to 'clear'.",
     "Tesseract native binary must be installed separately if using pip."],
    ["Reproduce one failure on purpose (wrong DB password, missing Tesseract, no Groq key) — read the traceback.",
     "Add one new field to the applicant form and thread it through UI → route → service → agent payload.",
     "Run <code>pytest</code> — all tests should still pass."],
    "A green end-to-end run after your plumbing change.")

day(7, "Make a real change + write about it",
    "Prove you understand it by extending it.",
    ["How to add a new agent: write the function, add a node to the graph, add an edge.",
     "How to add a rule: edit the appropriate agent's thresholds and update its pytest.",
     "How to write a minimal pytest: one input → one assertion."],
    ["Pick ONE: (a) add an 'employment stability' agent; (b) tighten compliance to score > 0.5; (c) show the top-3 risk factors as a bar chart in the UI.",
     "Write a 1-page README section: what, why, how to test.",
     "Write at least one pytest for your change."],
    "A working feature + a paragraph you could show to a teammate for review.")

story.append(PageBreak())

# ========================= Interview cheatsheet =========================
P("Interview Cheatsheet", h1)

P("If asked: 'Walk me through the architecture'", h2)
P("<i>Answer in this order:</i> "
  "(1) A user submits a form in Streamlit with their KYC info and an ID image. "
  "(2) The form POSTs multipart data to FastAPI at <code>/onboarding/apply</code>. "
  "(3) The route hands off to <code>onboarding_service.process_onboarding</code>, which parses inputs, masks Aadhaar, and calls <code>run_agents</code>. "
  "(4) <code>run_agents</code> is a compiled LangGraph state machine with six nodes: KYC → Document → Compliance → Risk → Decide → Explain. "
  "(5) Each agent adds its own status to a shared state dict. Short-circuit edges skip later agents if KYC fails, the document is invalid, or compliance flags a hit — this saves external API calls. "
  "(6) The Decide node produces Approved / Rejected / Review; Explain (optional, Groq LLM) writes a plain-English reason. "
  "(7) The service persists the customer, application, and document rows in Postgres, and returns the full decision JSON to the UI, which renders it with color-coded banners and metrics.")

P("If asked: 'Why agentic AI here?'", h2)
P("Each agent has one narrow responsibility (identity, document, sanctions, risk). "
  "That gives us <b>separation of concerns</b>, <b>independent testability</b> "
  "(every agent has its own unit tests), and <b>graceful degradation</b> — if "
  "OpenSanctions is down, only that check falls back to 'clear'; the pipeline "
  "still runs. LangGraph makes the composition explicit and adds short-circuits "
  "as first-class edges in the graph, not scattered if-statements.")

P("If asked: 'What would you improve for production?'", h2)
bullets([
    "Authentication + authorization on the admin endpoints (currently public).",
    "Connection pooling (each query opens/closes a psycopg2 connection).",
    "Async DB driver (psycopg2 blocks the FastAPI event loop).",
    "Structured logging + request IDs to trace one onboarding across all agents.",
    "Rate limits on the OpenSanctions call and a proper circuit breaker.",
    "Store the ID image in object storage (S3), not just the extracted text.",
    "Move sensitive config out of settings defaults; require env vars.",
    "Add mypy / ruff to CI; add coverage reporting to pytest.",
])

P("If asked: 'What did YOU do on this project?'", h2)
P("Practice a truthful, specific answer. Example structure: <i>'I understood "
  "the LangGraph orchestrator and the four agent contracts. I added feature "
  "X — it required a new node in the graph, a service-layer change to pass "
  "the new field, and a unit test. I also cleaned up Y and documented Z.'</i>")

P("Common gotcha questions", h2)
bullets([
    "<b>Why LangGraph and not just a for-loop over agents?</b> Short-circuit edges are declarative in a graph; a loop would need scattered if/break. Graphs also visualize cleanly.",
    "<b>Why Tesseract and not a cloud OCR API?</b> Free, offline, deterministic; fine for a demo. In production we'd compare accuracy vs. AWS Textract / Google Document AI.",
    "<b>Why hardcoded thresholds?</b> Rule-based scoring is explainable and auditable — regulators care about this. A learned model comes later once we have labeled outcome data.",
    "<b>What happens if two agents disagree?</b> They can't — each writes its own field. The Decide node applies precedence: fraud/compliance overrides risk.",
    "<b>Why short-circuit on KYC failure?</b> No point paying for OCR + sanctions API if the identity is already invalid.",
])

# ========================= Cheatsheet =========================
P("One-Page Command Cheatsheet", h1)
P("Run everything locally (two terminals, from repo root):", h2)
P("# terminal 1 — API<br/>"
  "uvicorn backend.api.main:app --reload<br/><br/>"
  "# terminal 2 — UI<br/>"
  "streamlit run ui/app.py", code)
P("Or with Docker (one terminal):", h2)
P("docker compose up --build", code)
P("Seed the database:", h2)
P("python notebooks/seed_customers.py", code)
P("Run tests:", h2)
P("pytest                       # all tests<br/>"
  "pytest tests/test_kyc_agent.py -v   # one file<br/>"
  "pytest -k orchestrator       # by keyword", code)
P("Environment variables (create .env from .env.example):", h2)
P("GROQ_API_KEY=...   # optional; enables the explain node<br/>"
  "DB_NAME=loan_db  DB_USER=postgres  DB_PASSWORD=0921<br/>"
  "DB_HOST=localhost  DB_PORT=5432", code)
P("Verdict thresholds worth memorizing:", h2)
bullets([
    "<b>KYC:</b> PAN 10 chars, Aadhaar 12 digits, mobile 10 digits, age ≥ 18.",
    "<b>Compliance:</b> OpenSanctions match score > 0.7 → flagged.",
    "<b>Risk:</b> score ≥ 70 = Low, 45-69 = Medium, &lt; 45 = High.",
    "<b>Decide:</b> KYC fail / doc invalid / compliance flagged → Rejected; else map risk to Approved / Review.",
])

# ========================= Success criteria =========================
P("What 'done' looks like after Day 7", h1)
P("<b>You should be able to, unaided:</b>")
bullets([
    "Start the whole stack locally and via docker compose.",
    "Explain the full request flow from a UI click to a Postgres row in under 3 minutes.",
    "Name all four agents, their inputs, outputs, and thresholds.",
    "Point at the exact file + function that decides Approved / Rejected / Review.",
    "Trace why any given short-circuit fired.",
    "Add a small feature (field, rule, or agent) without breaking pytest.",
])
P("<b>You will NOT be:</b>")
bullets([
    "A LangGraph, FastAPI, or Streamlit expert.",
    "Able to tune the OCR or replace it with a better model.",
    "Fluent in production concerns (auth, migrations, observability, CI/CD).",
])
P("That is completely fine. The goal of week 1 is to <b>own the story of "
  "this project</b> — enough to walk an interviewer through it, answer "
  "'why' questions, and extend it live. Depth comes from the second and "
  "third project you build.", note)

# ========================= Build =========================
doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
    title="OnBoardIQ - 1-Week Learning Roadmap", author="OnBoardIQ")
doc.build(story)
print(f"Wrote {OUTPUT}")
