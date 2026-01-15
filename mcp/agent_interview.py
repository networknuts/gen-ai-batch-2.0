from openai import OpenAI
from mcp.client import MCPClient

client = OpenAI()

# Connect to shared MCP RAG server
mcp = MCPClient(
    transport="http",
    url="http://rag-server:8000"
)

SYSTEM_PROMPT = """
You are an interview preparation assistant.

Rules:
- Answer ONLY from the provided document context
- Be concise and factual
- Mention page numbers
- If answer is not found, say so clearly
"""

query = input("> ")

# ---------------------------------------------------------
# Call MCP RAG Tool
# ---------------------------------------------------------
chunks = mcp.call_tool(
    "rag_search",
    {"query": query, "top_k": 4}
)

# ---------------------------------------------------------
# Build Context (same logic you had)
# ---------------------------------------------------------
context = "\n\n---\n\n".join(
    f"""
Page Content:
{c['content']}

Page Number: {c['page']}
Source File: {c['source']}
""".strip()
    for c in chunks
)

# ---------------------------------------------------------
# LLM Call
# ---------------------------------------------------------
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT + "\n\nDocument Context:\n" + context},
        {"role": "user", "content": query},
    ]
)

print(response.choices[0].message.content)
