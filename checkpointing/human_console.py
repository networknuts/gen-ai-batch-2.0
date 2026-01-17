import json
from langgraph.types import Command
from langgraph.checkpoint.mongodb import MongoDBSaver

from graph import build_graph
from config import DB_URI, GRAPH_CONFIG


def human_support_console():
    with MongoDBSaver.from_conn_string(DB_URI) as cp:
        graph = build_graph(cp)

        state = graph.get_state(config=GRAPH_CONFIG)
        last_message = state.values["messages"][-1]

        tool_calls = last_message.additional_kwargs.get("tool_calls", [])
        user_query = None

        for call in tool_calls:
            if call["function"]["name"] == "ask_human":
                args = json.loads(call["function"]["arguments"])
                user_query = args.get("query")

        print("\n--- HUMAN SUPPORT REQUIRED ---")
        print("Customer Query:", user_query)

        reply = input("Human Reply > ")

        resume_cmd = Command(resume={"data": reply})

        for event in graph.stream(resume_cmd, GRAPH_CONFIG, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


human_support_console()
