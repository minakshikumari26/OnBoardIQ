# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Run from the repo root — package imports are `backend.*` (see `pytest.ini`, `docker-compose.yml`).

```bash
# Backend (FastAPI, port 8000)
uvicorn backend.api.main:app --reload

# Frontend (Streamlit, port 8501) — needs backend running
streamlit run ui/app.py

# Tests (pytest-mock isolates DB / Tesseract / OpenSanctions / Groq)
pytest                                        # all tests
pytest tests/test_orchestrator.py             # single file
pytest tests/test_kyc_agent.py::test_underage_fails   # single test

# Seed ~50 fake Indian customers into the customers table
python notebooks/seed_customers.py

# Full stack via Docker (Postgres + backend + UI on one network)
GROQ_API_KEY=<key> docker compose up --build
```

`environment.yml` is preferred over `requirements.txt` for local setup — it also installs the `tesseract` binary that `pytesseract` needs. Pip users must install Tesseract separately (`brew install tesseract` on macOS).

## Database

Postgres. Defaults in `backend/config/settings.py` (overridable via `.env`):
`dbname=loan_db`, `user=postgres`, `password=0921`, `host=localhost`, `port=5432`.

Schema lives in `backend/db/schema.sql` and defines three tables:
- `customers` — applicant identity + financial info (PAN is UNIQUE)
- `onboarding_applications` — one row per pipeline run, records the decision + each agent's status
- `documents` — OCR text + validity, linked to an application

`schema.sql` **drops the legacy `users` and `loans` tables** on run — it's destructive by design because the repo used to be a loan-approval system. Apply it once manually (`psql -U postgres -d loan_db -f backend/db/schema.sql`), or let docker-compose apply it automatically on first Postgres boot via the entrypoint mount.

## Architecture

Request flow: **Streamlit UI → FastAPI route → service → LangGraph orchestrator → agents → DB**.

Routes are thin (parse input, call service, return JSON). Services own business logic + DB writes. Agents are pure functions: `dict → dict`.

### Layered layout

- `backend/api/main.py` — FastAPI app, mounts three routers only (`customer`, `onboarding`, `admin`). It's 14 lines; all endpoint code lives in `backend/api/routes/`.
- `backend/api/routes/loan_route.py` and `user_route.py` are **empty leftovers** from the pre-refactor loan system. Do not add routes there — use the domain-split files (`customer.py`, `onboarding.py`, `admin.py`).
- `backend/services/onboarding_service.py` — the only real service. `process_onboarding` runs the pipeline then persists to all three tables in one call. `backend/services/loan_service.py` is empty (also a leftover).
- `backend/db/queries.py` — all SQL. Every function opens+closes its own connection; there is no connection pool.
- `backend/utils/helper.py` and `backend/validators/loan_validator.py` are empty scaffolding — do not import from them.

### The LangGraph pipeline (`backend/agents/orchestrator_agent.py`)

The orchestrator is a compiled `StateGraph` built once at **import time** (module-level `_GRAPH = _build_graph()`). Nodes:

```
run_kyc → run_document → run_compliance → run_risk → decide → explain → END
```

Conditional edges short-circuit to `decide` on failure:
- `kyc_status == "failed"` → skip everything else
- `document_status == "invalid"` → skip compliance + risk (`"unreadable"` still continues)
- `compliance_status == "flagged"` → skip risk

`run_agents(data)` is the public entrypoint. It invokes the graph, then **fills in `"skipped"` placeholders** for any agent block the graph never reached, so downstream code (UI, `save_application`) can always read `result["kyc"]["kyc_status"]` etc. without KeyError.

Agents (all in `backend/agents/`):

| Agent | Returns key | Values |
|---|---|---|
| `kyc_agent.evaluate_kyc` | `kyc_status` | `verified` / `failed` |
| `document_agent.verify_document` | `document_status` | `valid` / `invalid` / `unreadable` |
| `compliance_agent.check_compliance` | `compliance_status` | `clear` / `flagged` |
| `risk_agent.assess_risk` | `risk_level` | `Low` / `Medium` / `High` (from a 0–100 rule-based score) |

The `risk` node reads `kyc_status` and `document_status` out of the graph state and injects them into its own input — the risk score gets a +10 boost from each. Order matters: risk always runs last.

The `explain` node calls Groq (Llama 3.3 70B via `langchain-groq`) to generate a customer-friendly message. **The graph always finishes even if this fails**: no `GROQ_API_KEY`, network error, or import failure all fall back to `explanation=""` and `llm_used=False`. Never make the pipeline depend on the LLM output.

### Decision waterfall (`decide_node`)

Rejection order: KYC fail → doc invalid → doc unreadable (→ Needs Review) → compliance flagged → then risk-based:
- Low risk → **Approved**
- Medium → **Needs Review**
- High → **Rejected**

## External services

- **OpenSanctions** (`api.opensanctions.org/search/default`) — no key needed. `compliance_agent` uses a 5s timeout and **falls back to `clear` on any exception**, so onboarding never blocks on network flakiness. Match threshold is `score > 0.7`.
- **Groq** — used only for the natural-language explanation. See above; optional.
- **Tesseract** — invoked by `document_agent` via `pytesseract`. If the binary is missing, `pytesseract.image_to_string` raises and the doc comes back `"unreadable"`, which routes the applicant to **Needs Review** (not Rejected).

## Things that will trip you up

- **The graph is built at import time.** Importing anything from `backend.agents.orchestrator_agent` (directly or transitively via routes/services) triggers `_build_graph()`. This is cheap, but it means the LangGraph deps must be installed even for lint/typecheck.
- **Node names are prefixed `run_*` on purpose** — a LangGraph node cannot share a name with a state key, and the state keys are `kyc`, `document`, `compliance`, `risk`. Don't rename the nodes to match the keys.
- **`kyc_agent` swallows DB exceptions** (`try: get_customer_by_pan… except Exception: existing = None`). This is intentional so the pipeline works when Postgres is down — but it means a broken query silently disables the bureau name-match check. Tests cover this path (`test_db_down_doesnt_crash`).
- **`get_customer_by_pan` returns a raw tuple**, not a dict — `kyc_agent` reads `existing[1]` for the name, and `onboarding_service` reads `existing[0]` for the id. Column order comes from `SELECT *` on the `customers` table (see `schema.sql`). If you change the column order in `schema.sql`, both call sites break silently.
- **DOB is parsed in one place** (`onboarding_service._parse_dob`) and it raises `ValueError` on bad input. Both `/customer/register` and `/onboarding/apply` catch that specifically and return `{"error": "DOB must be in YYYY-MM-DD format"}`. Preserve that contract.
- **PAN is uppercased in three places** — the route (`pan.upper()`), the service (`pan.strip().upper()`), and every query. If you add a new PAN entry point, uppercase it too, because the DB column is compared case-sensitively.
- **UI unpacks `/customer/{pan}` as raw tuple**, not a dict — same fragility as above applies to any UI code touching customer records.
- **`admin_dashboard.py` uses fixed column lists** for its DataFrames (10 columns for applications, 9 for customers). Those must stay in sync with `list_customers` / `list_applications` in `queries.py`.
- **Docker compose auto-applies `schema.sql`** on the first Postgres boot via a volume-mounted entrypoint script. If you re-run against an existing `pgdata` volume, the schema will *not* re-apply — drop the volume (`docker compose down -v`) if you need a fresh schema.
- **`generate_learning_pdf.py`** at the repo root is a one-off doc generator — not part of the app. Ignore it unless the user asks.
