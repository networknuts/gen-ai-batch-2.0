from dotenv import load_dotenv
from typing import List, Dict

from mcp.server.fastmcp import FastMCP
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

# ---------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------
load_dotenv()

# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------
mcp = FastMCP("RAG-MCP-Server")

# ---------------------------------------------------------
# Embedding Model (same as your original)
# ---------------------------------------------------------
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# ---------------------------------------------------------
# Qdrant Connection (same as your original)
# ---------------------------------------------------------
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

# ---------------------------------------------------------
# MCP Tool: RAG Search
# ---------------------------------------------------------
@mcp.tool()
def rag_search(query: str, top_k: int = 4) -> List[Dict]:
    """
    Perform similarity search over the document corpus.
    """
    results = vector_db.similarity_search(query=query, k=top_k)

    chunks = []
    for r in results:
        chunks.append({
            "content": r.page_content,
            "page": r.metadata.get("page_label", "N/A"),
            "source": r.metadata.get("source", "N/A"),
        })

    return chunks


if __name__ == "__main__":
    # Serve MCP over HTTP so multiple agents can connect
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )
