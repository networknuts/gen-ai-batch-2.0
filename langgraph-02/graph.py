from langgraph.graph import StateGraph, END
from state import AgentState
from agents import architect_plan, coder, architect_review


def review_router(state: AgentState) -> str:
    if state["score"] >= 8:
        return "end"
    return "improve"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("architect_plan", architect_plan)
    graph.add_node("coder", coder)
    graph.add_node("architect_review", architect_review)

    graph.set_entry_point("architect_plan")

    graph.add_edge("architect_plan", "coder")
    graph.add_edge("coder", "architect_review")

    graph.add_conditional_edges(
        "architect_review",
        review_router,
        {
            "improve": "coder",
            "end": END
        }
    )

    return graph.compile()
