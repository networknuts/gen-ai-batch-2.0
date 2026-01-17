"""
LangGraph Checkpointing with MongoDB (Auto Detection)
----------------------------------------------------

Features:
- Auto-detect NEW vs RESUME execution using MongoDB
- User input saved once per thread_id
- Resume without re-asking input
- Production-correct checkpointing semantics
"""

import time
from typing import TypedDict

from pymongo import MongoClient
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.mongodb import MongoDBSaver


# ---------------------------------------------------------
# Runtime State (checkpointed)
# ---------------------------------------------------------
class ChatState(TypedDict):
    question: str
    answer: str


# ---------------------------------------------------------
# Auto-detection helper (APPLICATION responsibility)
# ---------------------------------------------------------
def is_new_run(
    mongo_client: MongoClient,
    db_name: str,
    collection_name: str,
    thread_id: str,
) -> bool:
    """
    Returns True if NO checkpoint exists for this thread_id.
    """
    collection = mongo_client[db_name][collection_name]
    return collection.find_one({"thread_id": thread_id}) is None


# ---------------------------------------------------------
# Node 1: Get or reuse user question (IDEMPOTENT)
# ---------------------------------------------------------
def get_user_question(state: ChatState) -> ChatState:
    print("\n[Node 1] Fetching user question")

    if state.get("question"):
        print("Question already checkpointed. Skipping input.")
        return state

    question = input("Enter your question: ")

    return {
        "question": question,
        "answer": ""
    }


# ---------------------------------------------------------
# Node 2: Slow processing (failure-prone)
# ---------------------------------------------------------
def slow_processing(state: ChatState) -> ChatState:
    print("\n[Node 2] Starting slow processing (10 seconds)")
    time.sleep(10)
    print("[Node 2] Slow processing completed")
    return state


# ---------------------------------------------------------
# Node 3: Solve query
# ---------------------------------------------------------
def solve_question(state: ChatState) -> ChatState:
    print("\n[Node 3] Solving user query")

    return {
        "question": state["question"],
        "answer": f"Answer generated for: {state['question']}"
    }


# ---------------------------------------------------------
# Build LangGraph with MongoDB Checkpointing
# ---------------------------------------------------------
def build_graph(mongo_client: MongoClient):
    checkpointer = MongoDBSaver(
        client=mongo_client,
        db_name="langgraph_db",
        collection_name="checkpoints"
    )

    builder = StateGraph(ChatState)

    builder.add_node("get_question", get_user_question)
    builder.add_node("slow", slow_processing)
    builder.add_node("solve", solve_question)

    builder.set_entry_point("get_question")

    builder.add_edge("get_question", "slow")
    builder.add_edge("slow", "solve")
    builder.add_edge("solve", END)

    return builder.compile(checkpointer=checkpointer)


# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    # MongoDB connection (AUTH ENABLED)
    mongo_client = MongoClient(
        "mongodb://admin:admin@localhost:27017/?authSource=admin"
    )

    graph = build_graph(mongo_client)

    # Change this to start a new workflow
    thread_id = "user-session-001"

    DB_NAME = "langgraph_db"
    COLLECTION_NAME = "checkpoints"

    print("\n=== LangGraph Checkpointing Demo (Auto Detect) ===")

    if is_new_run(mongo_client, DB_NAME, COLLECTION_NAME, thread_id):
        print("No checkpoint found. Starting NEW execution.")
        result = graph.invoke(
            {"question": "", "answer": ""},
            config={"configurable": {"thread_id": thread_id}}
        )
    else:
        print("Checkpoint found. RESUMING execution.")
        result = graph.invoke(
            None,
            config={"configurable": {"thread_id": thread_id}}
        )

    print("\n=== Final Output ===")
    print(result)
