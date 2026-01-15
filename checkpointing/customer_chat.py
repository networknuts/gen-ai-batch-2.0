from langgraph.checkpoint.mongodb import MongoDBSaver
from graph import build_graph
from config import DB_URI, GRAPH_CONFIG
import time

def poll_for_human_response(graph, config, poll_interval=2):
    """
    Poll MongoDB until the graph reaches END after human resume.
    """
    print("Waiting for human response...")

    while True:
        state = graph.get_state(config=config)

        # LangGraph marks completion when next node is END
        if state.next is None:
            messages = state.values.get("messages", [])
            if messages:
                print("\n--- Response from Support ---")
                messages[-1].pretty_print()
            return

        time.sleep(poll_interval)



from langgraph.checkpoint.mongodb import MongoDBSaver
from graph import build_graph
from config import DB_URI, GRAPH_CONFIG


def customer_chat():
    with MongoDBSaver.from_conn_string(DB_URI) as cp:
        graph = build_graph(cp)

        while True:
            user_input = input("Customer > ")

            state = {
                "messages": [{"role": "user", "content": user_input}]
            }

            interrupted = False

            for event in graph.stream(state, GRAPH_CONFIG, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()

            # After execution, check if graph is waiting for resume
            current_state = graph.get_state(config=GRAPH_CONFIG)

            if current_state.next is not None:
                interrupted = True

            if interrupted:
                poll_for_human_response(graph, GRAPH_CONFIG)

