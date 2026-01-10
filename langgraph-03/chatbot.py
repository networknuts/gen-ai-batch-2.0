from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from state import ChatState
from db import save_message, load_history

# ----------------------------------
# Setup
# ----------------------------------
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini"
)

# ----------------------------------
# LangGraph node
# ----------------------------------
def chat_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {
        "messages": state["messages"] + [response]
    }

# ----------------------------------
# Build LangGraph
# ----------------------------------
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

app = graph.compile()

# ----------------------------------
# Chat runner
# ----------------------------------
def run_chat():
    thread_id = "user-1"

    print("Chat started (type 'exit' to quit)\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Load chat history from MongoDB
        history = load_history(thread_id)

        messages = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

        # Add current user message
        messages.append(HumanMessage(content=user_input))
        save_message(thread_id, "user", user_input)

        # Invoke LangGraph
        result = app.invoke({"messages": messages})

        ai_reply = result["messages"][-1].content
        print("Bot:", ai_reply)

        save_message(thread_id, "assistant", ai_reply)

# ----------------------------------
# Entry point
# ----------------------------------
if __name__ == "__main__":
    run_chat()
