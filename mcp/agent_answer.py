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

Answer the user's question using ONLY this document content.

You may summarize, rephrase, and combine information
from multiple sections to form a complete answer.

You must also mention the relevant page numbers of the document 
you received the data from to make the complete answer.

If the answer is NOT found in the document:
- Clearly say that the information is not available.

Do NOT add outside knowledge.

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

