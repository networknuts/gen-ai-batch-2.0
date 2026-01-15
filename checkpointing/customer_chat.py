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

            for event in graph.stream(state, GRAPH_CONFIG, stream_mode="values"):
                if "messages" in event:
                    event["messages"][-1].pretty_print()
