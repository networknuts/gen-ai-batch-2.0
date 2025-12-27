from fastapi import FastAPI, UploadFile
from dotenv import load_dotenv
import shutil
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

load_dotenv()
app = FastAPI()

QDRANT_URL = os.getenv("QDRANT_URL")
COLLECTION_NAME = "learning_vectors"
EMBEDDING_MODEL = "text-embedding-3-large"


@app.post("/ingest")
async def ingest_pdf(file: UploadFile):
    file_path = f"/tmp/{file.filename}"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400
    )
    chunks = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        url=QDRANT_URL,
        collection_name=COLLECTION_NAME
    )

    return {"status": "indexed", "chunks": len(chunks)}

