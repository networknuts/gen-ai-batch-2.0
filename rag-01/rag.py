from dotenv import load_dotenv
from openai import OpenAI

from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings


# ---------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------
load_dotenv()
client = OpenAI()


# ---------------------------------------------------------
# Embedding Model (must match indexing model)
# ---------------------------------------------------------
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)


# ---------------------------------------------------------
# Connect to Existing Qdrant Collection
# ---------------------------------------------------------
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)


# ---------------------------------------------------------
# Accept User Query
# ---------------------------------------------------------
query = input("> ")


# ---------------------------------------------------------
# Perform Similarity Search
# ---------------------------------------------------------
search_results = vector_db.similarity_search(query=query)


# ---------------------------------------------------------
# Build Context from Retrieved Documents
# ---------------------------------------------------------
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


# ---------------------------------------------------------
# System Prompt (Simplified & Clear)
# ---------------------------------------------------------
SYSTEM_PROMPT = f"""
You are a helpful AI assistant.

You have been given content extracted from a PDF document.
Each section includes:
- The text content
- The page number
- The source file location

Answer the user's question using ONLY this provided information.

If the answer exists:
- Respond clearly and concisely
- Mention the relevant page number so the user can read more

If the answer is NOT found in the content:
- Clearly say that the information is not available in the document

Do NOT add outside knowledge.

Document Context:
{context}
"""


# ---------------------------------------------------------
# Generate Answer
# ---------------------------------------------------------
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
)


print(f"\n🤖 {response.choices[0].message.content}")
