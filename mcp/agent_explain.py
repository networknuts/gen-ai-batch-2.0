import asyncio
from openai import OpenAI

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# ---------------------------------------------------------
# OpenAI Client
# ---------------------------------------------------------
client = OpenAI()

# ---------------------------------------------------------
# System Prompt (MATCHES rag.py SEMANTICS)
# ---------------------------------------------------------
BASE_SYSTEM_PROMPT = """
You are a helpful AI assistant.

You have been given content extracted from a PDF document.

Priority is to completely use that content and add the following content:
1. how this is used in devops
2. famous organisations that use the technology or concept
3. real world areas where this is used
4. any examples if possible and relevant to user query

Document Context:
"""

# ---------------------------------------------------------
# Main Logic
# ---------------------------------------------------------
async def main():
    query = input("> ")

    # -----------------------------------------------------
    # Connect to MCP RAG Server
    # -----------------------------------------------------
    async with streamable_http_client("http://localhost:8000/mcp") as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # -------------------------------------------------
            # Call MCP RAG Tool (RETRIEVAL ONLY)
            # -------------------------------------------------
            result = await session.call_tool(
                "rag_search",
                {
                    "query": query
                }
            )

            # Extract raw document text (NO formatting, NO logic)
            retrieved_chunks = result.content
    # -----------------------------------------------------
    # Build Context (EXACTLY like rag.py)
    # -----------------------------------------------------
    context = str(retrieved_chunks)

    system_prompt = BASE_SYSTEM_PROMPT + "\n" + context

    # -----------------------------------------------------
    # LLM Call
    # -----------------------------------------------------
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
    )

    print("\n🤖", response.choices[0].message.content)


if __name__ == "__main__":
    asyncio.run(main())

