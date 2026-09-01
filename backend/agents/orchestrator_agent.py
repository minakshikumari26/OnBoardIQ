"""
LangGraph state-machine orchestrator.

Each sub-agent is a node in the graph. Conditional edges short-circuit to the
final decision node when a check fails, so we don't waste API calls on an
applicant who has already been rejected.

A final `explain` node uses Groq (Llama 3.3 70B) to turn the raw decision into
a friendly natural-language message for the customer. If GROQ_API_KEY is
missing or Groq is unreachable, the graph still returns a valid decision;
the explanation just comes back empty.
"""

import time
from typing import Optional, TypedDict

from langgraph.graph import StateGraph, END

from backend.agents.kyc_agent import evaluate_kyc
from backend.agents.document_agent import verify_document
from backend.agents.compliance_agent import check_compliance
from backend.agents.risk_agent import assess_risk
from backend.config.settings import GROQ_API_KEY, LLM_MODEL


# ── State schema ──────────────────────────────────────────────────────────────
class OnboardingState(TypedDict, total=False):
    # Applicant input
    name: str
    pan: str
    aadhaar: str
    mobile: str
    age: int
    monthly_income: int
    employment_type: str
    file_bytes: Optional[bytes]

    # Agent outputs (filled in by nodes)
    kyc: dict
    document: dict
    compliance: dict
    risk: dict

    # Final result
    decision: str
    reason: str
    explanation: str
    llm_used: bool
    processing_time_seconds: float


# ── Nodes ─────────────────────────────────────────────────────────────────────
def kyc_node(state: OnboardingState) -> dict:
    return {"kyc": evaluate_kyc(state)}


def document_node(state: OnboardingState) -> dict:
    return {"document": verify_document(state)}


def compliance_node(state: OnboardingState) -> dict:
    return {"compliance": check_compliance(state)}


def risk_node(state: OnboardingState) -> dict:
    # Feed earlier results into the risk agent's input dict
    data = dict(state)
    data["kyc_status"] = state.get("kyc", {}).get("kyc_status", "failed")
    data["document_status"] = state.get("document", {}).get("document_status", "invalid")
    return {"risk": assess_risk(data)}


def decide_node(state: OnboardingState) -> dict:
    """Apply the decision waterfall based on whichever agent outputs are set."""
    kyc = state.get("kyc", {}).get("kyc_status", "failed")
    doc = state.get("document", {}).get("document_status", "invalid")
    comp = state.get("compliance", {}).get("compliance_status", "clear")
    risk = state.get("risk", {}).get("risk_level", "High")

    if kyc == "failed":
        return {"decision": "Rejected", "reason": "KYC failed"}
    if doc == "invalid":
        return {"decision": "Rejected", "reason": "Document invalid"}
    if doc == "unreadable":
        return {"decision": "Needs Review", "reason": "Document could not be read"}
    if comp == "flagged":
        return {"decision": "Rejected", "reason": "Compliance issue found"}
    if risk == "Low":
        return {"decision": "Approved", "reason": "All checks passed"}
    if risk == "Medium":
        return {"decision": "Needs Review", "reason": "Medium risk profile"}
    return {"decision": "Rejected", "reason": "High risk profile"}


def explain_node(state: OnboardingState) -> dict:
    """Generative-AI explanation of the decision. Optional — no key = no call."""
    if not GROQ_API_KEY:
        return {"explanation": "", "llm_used": False}

    try:
        from langchain_groq import ChatGroq

        llm = ChatGroq(model=LLM_MODEL, temperature=0.3)
        prompt = (
            "You are a bank customer service assistant. In 2-3 friendly sentences, "
            "explain this onboarding outcome to the applicant. Do not use JSON. "
            "Be empathetic if rejected, warm if approved, clear if review is needed.\n\n"
            f"Applicant name: {state.get('name')}\n"
            f"Decision: {state.get('decision')}\n"
            f"Reason: {state.get('reason')}\n"
            f"Risk level: {state.get('risk', {}).get('risk_level', 'N/A')}"
        )
        response = llm.invoke(prompt)
        return {"explanation": response.content, "llm_used": True}
    except Exception as e:
        print(f"[orchestrator] explain node fell back: {e}")
        return {"explanation": "", "llm_used": False}


# ── Conditional edges ─────────────────────────────────────────────────────────
def after_kyc(state: OnboardingState) -> str:
    """If KYC failed, skip the rest and go straight to decision."""
    if state.get("kyc", {}).get("kyc_status") == "failed":
        return "decide"
    return "run_document"


def after_document(state: OnboardingState) -> str:
    """If document is outright invalid, short-circuit. 'Unreadable' still continues."""
    if state.get("document", {}).get("document_status") == "invalid":
        return "decide"
    return "run_compliance"


def after_compliance(state: OnboardingState) -> str:
    """If sanctions match, short-circuit."""
    if state.get("compliance", {}).get("compliance_status") == "flagged":
        return "decide"
    return "run_risk"


# ── Build the graph once at import time ───────────────────────────────────────
def _build_graph():
    graph = StateGraph(OnboardingState)

    # Node names must not collide with state keys, so we prefix with "run_"
    graph.add_node("run_kyc", kyc_node)
    graph.add_node("run_document", document_node)
    graph.add_node("run_compliance", compliance_node)
    graph.add_node("run_risk", risk_node)
    graph.add_node("decide", decide_node)
    graph.add_node("explain", explain_node)

    graph.set_entry_point("run_kyc")

    graph.add_conditional_edges("run_kyc", after_kyc,
                                {"run_document": "run_document", "decide": "decide"})
    graph.add_conditional_edges("run_document", after_document,
                                {"run_compliance": "run_compliance", "decide": "decide"})
    graph.add_conditional_edges("run_compliance", after_compliance,
                                {"run_risk": "run_risk", "decide": "decide"})
    graph.add_edge("run_risk", "decide")
    graph.add_edge("decide", "explain")
    graph.add_edge("explain", END)

    return graph.compile()


_GRAPH = _build_graph()


# ── Public entrypoint (unchanged signature for the API layer) ─────────────────
def run_agents(data: dict) -> dict:
    start = time.time()
    final_state = _GRAPH.invoke(data)

    # Fill in placeholders for any agents the graph short-circuited past.
    # UI and API downstream code assume each block has a status field.
    kyc_default = {"kyc_status": "skipped", "reason": "Not evaluated"}
    doc_default = {"document_status": "skipped", "reason": "Not evaluated"}
    comp_default = {"compliance_status": "skipped", "reason": "Not evaluated", "matches": []}
    risk_default = {"risk_level": "skipped", "risk_score": 0, "factors": []}

    return {
        "decision":               final_state.get("decision"),
        "reason":                 final_state.get("reason"),
        "explanation":            final_state.get("explanation", ""),
        "kyc":                    final_state.get("kyc")        or kyc_default,
        "document":               final_state.get("document")   or doc_default,
        "compliance":             final_state.get("compliance") or comp_default,
        "risk":                   final_state.get("risk")       or risk_default,
        "llm_used":               final_state.get("llm_used", False),
        "processing_time_seconds": round(time.time() - start, 2),
    }
