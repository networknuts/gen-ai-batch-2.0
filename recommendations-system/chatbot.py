from dotenv import load_dotenv
from mem0 import Memory
from openai import OpenAI
import os
import json

# ------------------------
# Environment
# ------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------
# Memory configuration
# ------------------------
config = {
    "version": "v1.1",
    "embedder": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "text-embedding-3-small"
        }
    },
    "llm": {
        "provider": "openai",
        "config": {
            "api_key": OPENAI_API_KEY,
            "model": "gpt-4.1"
        }
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": "localhost",
            "port": "6333"
        }
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": "bolt://localhost:7687",
            "username": "neo4j",
            "password": "spray-margin-modular-mega-minus-5203"
        }
    }
}

memory = Memory.from_config(config)

# ------------------------
# Chat loop
# ------------------------
def chat():
    user_id = input("User ID: ").strip()
    print("\nMemory-aware chat started (type 'exit')\n")

    while True:
        user_query = input("> ")
        if user_query.lower() == "exit":
            break

        # 🔹 Retrieve relevant memories (Neo4j + Qdrant automatically)
        relevant_memories = memory.search(
            query=user_query,
            user_id=user_id
        )

        memories = [
            mem["memory"]
            for mem in relevant_memories.get("results", [])
        ]

        system_prompt = f"""
You are a memory-aware assistant.
You have access to past interactions and facts about the user.

User memory:
{json.dumps(memories, indent=2)}
"""

        # 🔹 OpenAI call (direct SDK)
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        )

        ai_reply = response.choices[0].message.content
        print(f"🤖: {ai_reply}")

        # 🔹 Persist memory (Neo4j auto-graphs)
        memory.add(
            [
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": ai_reply}
            ],
            user_id=user_id
        )

if __name__ == "__main__":
    chat()
