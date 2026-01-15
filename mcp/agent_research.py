from openai import OpenAI
from mcp.client import MCPClient

client = OpenAI()

# Same MCP server, same tool
mcp = MCPClient(
    transport="http",
    url="http://rag-server:8000"
)

SYSTEM_PROMPT = """
You are a research assistant.

Rules:
- Use ONLY the provided document content
- Explain concepts clearly
- Mention relevant page numbers
- Do not add outside knowledge
"""

query = input("> ")

# ---------------------------------------------------------
# Call MCP RAG Tool
# ---------------------------------------------------------
chunks = mcp.call_tool(
    "rag_search",
    {"query": query, "top_k": 8}
)

# ---------------------------------------------------------
# Build Context
# ---------------------------------------------------------
context = "\n\n---\n\n".join(
    f"""
Excerpt:
{c['content']}

Page: {c['page']}
Source: {c['source']}
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
