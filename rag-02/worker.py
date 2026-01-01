import redis
import ast
from dotenv import load_dotenv
from openai import OpenAI

from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

# -----------------------------------------
# Environment
# -----------------------------------------
load_dotenv()
client = OpenAI()

# -----------------------------------------
# Redis
# -----------------------------------------
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# -----------------------------------------
# Embeddings
# -----------------------------------------
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

# -----------------------------------------
# Qdrant
# -----------------------------------------
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)

print("Worker started. Waiting for jobs...")

# -----------------------------------------
# Worker Loop
# -----------------------------------------
while True:
    _, raw_payload = redis_client.blpop("rag:requests")

    payload = ast.literal_eval(raw_payload)
    job_id = payload["job_id"]
    query = payload["query"]

    print(f"Processing job {job_id}")

    # -----------------------------------------
    # Similarity Search
    # -----------------------------------------
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

    # -----------------------------------------
    # System Prompt
    # -----------------------------------------
    system_prompt = f"""
You are a helpful AI assistant.

You have been given content extracted from a PDF document.
Each section includes:
- The text content
- The page number
- The source file location

Answer the user's question using ONLY this provided information.

If the answer exists:
- Respond clearly and concisely
- Mention the relevant page number

If the answer does NOT exist:
- Clearly state that the information is not available in the document

Document Context:
{context}
"""

    # -----------------------------------------
    # LLM Call
    # -----------------------------------------
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]
    )

    answer = response.choices[0].message.content

    # -----------------------------------------
    # Store Result
    # -----------------------------------------
    redis_client.set(
        f"rag:response:{job_id}",
        answer,
        ex=3600  # optional TTL
    )

    print(f"Job {job_id} completed")
