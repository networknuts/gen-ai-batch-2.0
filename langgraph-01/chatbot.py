from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Literal, TypedDict

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from langgraph.graph import StateGraph, END


# =========================================================
# State Definition
# =========================================================

Category = Literal["product", "billing", "technical"]

class AgentState(TypedDict):
    user_query: str
    category: Category
    answer: str


# =========================================================
# Environment & Config
# =========================================================

load_dotenv()

# Models
CLASSIFIER_MODEL = os.getenv("CLASSIFIER_MODEL", "gpt-4o-mini")
RAG_MODEL = os.getenv("RAG_MODEL", "gpt-4.1")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

# Email
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

FINANCE_TICKET_TO = os.getenv("FINANCE_TICKET_TO")
TECH_TICKET_TO = os.getenv("TECH_TICKET_TO")
FROM_NAME = os.getenv("TICKET_FROM_NAME", "Support Bot")


# =========================================================
# LLMs
# =========================================================

classifier_llm = ChatOpenAI(
    model=CLASSIFIER_MODEL,
)

rag_llm = ChatOpenAI(
    model=RAG_MODEL,
)


# =========================================================
# Vector DB (Direct similarity search)
# =========================================================

embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

vector_db = QdrantVectorStore.from_existing_collection(
    url=QDRANT_URL,
    collection_name=QDRANT_COLLECTION,
    embedding=embeddings,
)


# =========================================================
# Email Utility
# =========================================================

def send_email(to: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = f"{FROM_NAME} <{SMTP_USERNAME}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)


# =========================================================
# LangGraph Nodes
# =========================================================

def classify_node(state: AgentState) -> dict:
    prompt = f"""
You are a customer support classifier.

Classify the user query into exactly ONE category:

- product
- billing
- technical

Example classifications:
- Password resets, Account creation, Account access - product
- Payment issue, Payment failure, Credit card, Net banking - billing
- Unable to watch videos, Unable to join class, Unable to access - technical


Rules:
- Respond with only one lowercase word
- No explanation

User query:
{state["user_query"]}
"""

    category = classifier_llm.invoke(prompt).content.strip()

    return {"category": category}


def rag_answer_node(state: AgentState) -> dict:
    query = state["user_query"]

    docs = vector_db.similarity_search(query, k=4)

    context = "\n\n---\n\n".join(
        f"Source: {doc.metadata}\n{doc.page_content}"
        for doc in docs
    )

    system_prompt = """
You are a product support assistant.
Answer strictly using the provided context.
If the answer is not present, say so clearly.
"""

    user_prompt = f"""
CONTEXT:
{context}

QUESTION:
{query}
"""

    answer = rag_llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    ).content.strip()

    return {"answer": answer}


def billing_ticket_node(state: AgentState) -> dict:
    send_email(
        to=FINANCE_TICKET_TO,
        subject="[Billing Ticket] New request",
        body=f"User message:\n\n{state['user_query']}"
    )

    return {
        "answer": "Your billing request has been raised with the finance team."
    }


def technical_ticket_node(state: AgentState) -> dict:
    send_email(
        to=TECH_TICKET_TO,
        subject="[Technical Ticket] New issue",
        body=f"User message:\n\n{state['user_query']}"
    )

    return {
        "answer": "Your technical issue has been raised with the tech team."
    }


def router(state: AgentState) -> str:
    return state["category"]


# =========================================================
# LangGraph Construction
# =========================================================

graph = StateGraph(AgentState)

graph.add_node("classify", classify_node)
graph.add_node("rag_answer", rag_answer_node)
graph.add_node("billing_ticket", billing_ticket_node)
graph.add_node("technical_ticket", technical_ticket_node)

graph.set_entry_point("classify")

graph.add_conditional_edges(
    "classify",
    router,
    {
        "product": "rag_answer",
        "billing": "billing_ticket",
        "technical": "technical_ticket",
    },
)

graph.add_edge("rag_answer", END)
graph.add_edge("billing_ticket", END)
graph.add_edge("technical_ticket", END)

app = graph.compile()


# =========================================================
# CLI Chat Loop
# =========================================================

def main():
    print("Support Bot started. Type 'exit' to quit.\n")

    while True:
        user_query = input("User: ").strip()
        if user_query.lower() in {"exit", "quit"}:
            break

        result = app.invoke({"user_query": user_query})
        print(f"\nBot: {result['answer']}\n")


if __name__ == "__main__":
    main()
