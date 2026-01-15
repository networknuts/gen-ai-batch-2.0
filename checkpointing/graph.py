from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

from state import SupportState
from llm import llm_with_tools
from tools import ask_human


def chatbot_node(state: SupportState):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}


def build_graph(checkpointer):
    builder = StateGraph(SupportState)

    builder.add_node("chatbot", chatbot_node)
    builder.add_node("tools", ToolNode(tools=[ask_human]))

    builder.add_edge(START, "chatbot")
    builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_edge("tools", "chatbot")
    builder.add_edge("chatbot", END)

    return builder.compile(checkpointer=checkpointer)
