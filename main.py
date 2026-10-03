from langgraph.graph import END, START, StateGraph

from models import GraphInput, GraphOutput, GraphState
from nodes.analyze_documents import analyze_documents
from nodes.check_duplicate import check_duplicate
from nodes.check_policy import check_policy
from nodes.recommend_decision import recommend_decision


def route_after_policy(state: GraphState) -> str:
    return "check_duplicate" if state.policy_valid else "recommend_decision"


def route_after_duplicate(state: GraphState) -> str:
    return "recommend_decision" if state.is_duplicate else "analyze_documents"


builder = StateGraph(GraphState, input=GraphInput, output=GraphOutput)

builder.add_node("check_policy", check_policy)
builder.add_node("check_duplicate", check_duplicate)
builder.add_node("analyze_documents", analyze_documents)
builder.add_node("recommend_decision", recommend_decision)

builder.add_edge(START, "check_policy")
builder.add_conditional_edges(
    "check_policy", route_after_policy, ["check_duplicate", "recommend_decision"]
)
builder.add_conditional_edges(
    "check_duplicate", route_after_duplicate, ["analyze_documents", "recommend_decision"]
)
builder.add_edge("analyze_documents", "recommend_decision")
builder.add_edge("recommend_decision", END)

graph = builder.compile()
