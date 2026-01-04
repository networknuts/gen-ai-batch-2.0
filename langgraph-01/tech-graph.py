from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END
from openai import OpenAI
from dotenv import load_dotenv

# -----------------------------------
# ENV SETUP
# -----------------------------------
load_dotenv()
client = OpenAI()

# -----------------------------------
# STATE DEFINITION
# -----------------------------------
class AgentState(TypedDict):
    question: str
    category: Literal["tech", "non-tech"]
    answer: str

# -----------------------------------
# NODE 1: CLASSIFIER (LLM)
# -----------------------------------
def classify_question(state: AgentState) -> AgentState:
    prompt = f"""
Classify the following user question strictly as either:
- tech
- non-tech

Return ONLY one word.

Question:
{state['question']}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # cheap + fast for classification
        messages=[{"role": "user", "content": prompt}]
    )

    category = response.choices[0].message.content.strip().lower()

    return {
        **state,
        "category": category
    }

# -----------------------------------
# NODE 2A: TECH ANSWER (EXPENSIVE MODEL)
# -----------------------------------
def answer_tech(state: AgentState) -> AgentState:
    response = client.chat.completions.create(
        model="gpt-4.1",  # expensive / capable model
        messages=[
            {"role": "system", "content": "You are a senior technical expert."},
            {"role": "user", "content": state["question"]}
        ]
    )

    return {
        **state,
        "answer": response.choices[0].message.content
    }

# -----------------------------------
# NODE 2B: NON-TECH ANSWER (CHEAP MODEL)
# -----------------------------------
def answer_non_tech(state: AgentState) -> AgentState:
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # cheaper model
        messages=[
            {"role": "system", "content": "You are a helpful general assistant."},
            {"role": "user", "content": state["question"]}
        ]
    )

    return {
        **state,
        "answer": response.choices[0].message.content
    }

# -----------------------------------
# ROUTER FUNCTION
# -----------------------------------
def route_by_category(state: AgentState):
    if state["category"] == "tech":
        return "tech_answer"
    else:
        return "non_tech_answer"

# -----------------------------------
# BUILD LANGGRAPH
# -----------------------------------
graph = StateGraph(AgentState)

graph.add_node("classifier", classify_question)
graph.add_node("tech_answer", answer_tech)
graph.add_node("non_tech_answer", answer_non_tech)

graph.set_entry_point("classifier")

graph.add_conditional_edges(
    "classifier",
    route_by_category,
    {
        "tech_answer": "tech_answer",
        "non_tech_answer": "non_tech_answer"
    }
)

graph.add_edge("tech_answer", END)
graph.add_edge("non_tech_answer", END)

app = graph.compile()

# -----------------------------------
# RUN
# -----------------------------------
if __name__ == "__main__":
    user_input = input("Ask something: ")

    result = app.invoke({
        "question": user_input
    })

    print("\nAnswer:\n")
    print(result["answer"])
