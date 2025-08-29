import json
from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END

# STATE (shared across all stages)

class SupportState(TypedDict, total=False):
    customer_name: str
    email: str
    query: str
    priority: str
    ticket_id: str
    structured_query: dict
    entities: dict
    normalized: bool
    ticket_history: list
    sla_risk: str
    clarification_requested: bool
    clarification_answer: str
    kb_result: str
    solution_score: int
    escalated: bool
    ticket_status: str
    draft_response: str
    api_executed: bool
    notification_sent: bool



# MCP Clients (Stubbed)

class CommonMCPClient:
    def run(self, ability: str, state: SupportState) -> SupportState:
        print(f"[COMMON] {ability}")
        if ability == "parse_request_text":
            state["structured_query"] = {"intent": "password reset"}
        elif ability == "normalize_fields":
            state["normalized"] = True
        elif ability == "add_flags_calculations":
            state["sla_risk"] = "low"
        elif ability == "solution_evaluation":
            state["solution_score"] = 95
        elif ability == "response_generation":
            state["draft_response"] = f"Dear {state['customer_name']}, we have resolved your issue."
        return state


class AtlasMCPClient:
    def run(self, ability: str, state: SupportState) -> SupportState:
        print(f"[ATLAS] {ability}")
        if ability == "extract_entities":
            state["entities"] = {"product": "Email Service"}
        elif ability == "enrich_records":
            state["ticket_history"] = ["T123", "T124"]
        elif ability == "clarify_question":
            state["clarification_requested"] = True
        elif ability == "extract_answer":
            state["clarification_answer"] = "User provided missing account ID."
        elif ability == "knowledge_base_search":
            state["kb_result"] = "Password reset instructions found."
        elif ability == "escalation_decision":
            state["escalated"] = state.get("solution_score", 0) < 90
        elif ability == "update_ticket":
            state["ticket_status"] = "In Progress"
        elif ability == "close_ticket":
            state["ticket_status"] = "Closed"
        elif ability == "execute_api_calls":
            state["api_executed"] = True
        elif ability == "trigger_notifications":
            state["notification_sent"] = True
        return state


common = CommonMCPClient()
atlas = AtlasMCPClient()








def intake(state: SupportState) -> SupportState:
    print("Stage 1: INTAKE")
    return state

def understand(state: SupportState) -> SupportState:
    print("Stage 2: UNDERSTAND")
    state = common.run("parse_request_text", state)
    state = atlas.run("extract_entities", state)
    return state

def prepare(state: SupportState) -> SupportState:
    print("Stage 3: PREPARE")
    state = common.run("normalize_fields", state)
    state = atlas.run("enrich_records", state)
    state = common.run("add_flags_calculations", state)
    return state

def ask(state: SupportState) -> SupportState:
    print("Stage 4: ASK")
    state = atlas.run("clarify_question", state)
    return state

def wait(state: SupportState) -> SupportState:
    print("Stage 5: WAIT")
    state = atlas.run("extract_answer", state)
    return state

def retrieve(state: SupportState) -> SupportState:
    print("Stage 6: RETRIEVE")
    state = atlas.run("knowledge_base_search", state)
    return state

def decide(state: SupportState) -> SupportState:
    print("Stage 7: DECIDE")
    state = common.run("solution_evaluation", state)
    if state["solution_score"] < 90:
        state = atlas.run("escalation_decision", state)
    else:
        print("Score >= 90, no escalation")
        state["escalated"] = False
    return state

def update(state: SupportState) -> SupportState:
    print("Stage 8: UPDATE")
    state = atlas.run("update_ticket", state)
    state = atlas.run("close_ticket", state)
    return state

def create(state: SupportState) -> SupportState:
    print("Stage 9: CREATE")
    state = common.run("response_generation", state)
    return state

def do(state: SupportState) -> SupportState:
    print("Stage 10: DO")
    state = atlas.run("execute_api_calls", state)
    state = atlas.run("trigger_notifications", state)
    return state

def complete(state: SupportState) -> SupportState:
    print("Stage 11: COMPLETE")
    print("\n=== FINAL PAYLOAD ===")
    print(json.dumps(state, indent=2))
    return state




workflow = StateGraph(SupportState)

workflow.add_node("INTAKE", intake)
workflow.add_node("UNDERSTAND", understand)
workflow.add_node("PREPARE", prepare)
workflow.add_node("ASK", ask)
workflow.add_node("WAIT", wait)
workflow.add_node("RETRIEVE", retrieve)
workflow.add_node("DECIDE", decide)
workflow.add_node("UPDATE", update)
workflow.add_node("CREATE", create)
workflow.add_node("DO", do)
workflow.add_node("COMPLETE", complete)


workflow.set_entry_point("INTAKE")
workflow.add_edge("INTAKE", "UNDERSTAND")
workflow.add_edge("UNDERSTAND", "PREPARE")
workflow.add_edge("PREPARE", "ASK")
workflow.add_edge("ASK", "WAIT")
workflow.add_edge("WAIT", "RETRIEVE")
workflow.add_edge("RETRIEVE", "DECIDE")
workflow.add_edge("DECIDE", "UPDATE")
workflow.add_edge("UPDATE", "CREATE")
workflow.add_edge("CREATE", "DO")
workflow.add_edge("DO", "COMPLETE")
workflow.add_edge("COMPLETE", END)

app = workflow.compile()




if __name__ == "__main__":
    sample = {
        "customer_name": "Alice",
        "email": "alice@example.com",
        "query": "I cannot log in to my email account",
        "priority": "high",
        "ticket_id": "T125"
    }
    result = app.invoke(sample)
