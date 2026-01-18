from dotenv import load_dotenv
from typing import List

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

# ---------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# FastMCP Server
# ---------------------------------------------------------
mcp = FastMCP("RAG-MCP-Server")

# ---------------------------------------------------------
# Embedding Model
# ---------------------------------------------------------
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# ---------------------------------------------------------
# Qdrant Connection
# ---------------------------------------------------------
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)
print(vector_db.client.get_collection("learning_vectors"))
# ---------------------------------------------------------
# MCP Tool: RAG Search (FIXED)
# ---------------------------------------------------------
@mcp.tool()
def rag_search(query: str):
    """
    Perform similarity search over the document corpus.
    Returns MCP-native TextContent blocks.
    """
    search_results = vector_db.similarity_search(query=query)
    context_blocks = []

    for result in search_results:
        block = f"""
    Page Content:
    {result.page_content}

    Page Number: {result.metadata.get("page_label", "N/A")}
    Source File: {result.metadata.get("source", "N/A")}
    """
    context_blocks.append(block.strip())

    context = "\n\n---\n\n".join(context_blocks)
    return context

    
# ---------------------------------------------------------
# Run Server
# ---------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
