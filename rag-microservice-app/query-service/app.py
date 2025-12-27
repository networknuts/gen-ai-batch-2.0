from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os

from openai import OpenAI
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings

load_dotenv()
app = FastAPI()
client = OpenAI()

QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = "learning_vectors"
EMBEDDING_MODEL = "text-embedding-3-large"


class QueryRequest(BaseModel):
    question: str


@app.post("/query")
def query_rag(payload: QueryRequest):
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    vector_db = QdrantVectorStore.from_existing_collection(
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME,
        embedding=embeddings
    )

    docs = vector_db.similarity_search(payload.question)

    context = "\n\n".join(
        f"{d.page_content}\n(Page: {d.metadata.get('page_label')})"
        for d in docs
    )

    system_prompt = f"""
    Answer ONLY using the context below.
    If the answer is not present, say so clearly.

    Context:
    {context}
    """

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": payload.question},
        ]
    )

    return {"answer": response.choices[0].message.content}

