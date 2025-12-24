from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore


# ---------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------
load_dotenv()


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
PDF_FILE = "data.pdf"

QDRANT_URL = "http://vector-db:6333"
COLLECTION_NAME = "learning_vectors"

EMBEDDING_MODEL = "text-embedding-3-large"


# ---------------------------------------------------------
# Step 1: Load PDF Document
# ---------------------------------------------------------
loader = PyPDFLoader(file_path=PDF_FILE)
documents = loader.load()


# ---------------------------------------------------------
# Step 2: Split Document into Chunks
# ---------------------------------------------------------
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunked_documents = text_splitter.split_documents(documents)


# ---------------------------------------------------------
# Step 3: Initialize Embedding Model
# ---------------------------------------------------------
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)


# ---------------------------------------------------------
# Step 4: Store Embeddings in Qdrant
# ---------------------------------------------------------
QdrantVectorStore.from_documents(
    documents=chunked_documents,
    embedding=embeddings,
    url=QDRANT_URL,
    collection_name=COLLECTION_NAME
)

print("Document indexing completed successfully.")
