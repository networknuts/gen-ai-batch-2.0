
# PDF Ingestion and Vector Indexing with LangChain and Qdrant

This project demonstrates how to ingest a PDF document, split it into meaningful text chunks, generate vector embeddings using OpenAI, and store those embeddings in a Qdrant vector database.  
This pattern is commonly used as the **ingestion phase of a Retrieval-Augmented Generation (RAG) pipeline**.

---

## High-Level Workflow

1. Load environment variables (API keys, configs)
2. Load a PDF document
3. Split the document into overlapping chunks
4. Generate embeddings for each chunk
5. Store embeddings in Qdrant for similarity search

---

## Prerequisites

- Python 3.9+
- OpenAI API key
- Running Qdrant instance (local or containerized)

---

## Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
````

---

## Code Walkthrough

### 1. Environment Setup

```python
from dotenv import load_dotenv
load_dotenv()
```

Loads environment variables from a `.env` file into the runtime.
This is required so libraries like `langchain-openai` can access the OpenAI API key securely.

**Documentation**

* [https://pypi.org/project/python-dotenv/](https://pypi.org/project/python-dotenv/)

---

### 2. Configuration

```python
PDF_FILE = "data.pdf"
QDRANT_URL = "http://vector-db:6333"
COLLECTION_NAME = "learning_vectors"
EMBEDDING_MODEL = "text-embedding-3-large"
```

* **PDF_FILE**: Input document to be indexed
* **QDRANT_URL**: Qdrant service endpoint
* **COLLECTION_NAME**: Logical namespace for vectors
* **EMBEDDING_MODEL**: OpenAI embedding model

**Embedding model reference**

* [https://platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings)

---

### 3. Load PDF Document

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader(file_path=PDF_FILE)
documents = loader.load()
```

* Reads the PDF
* Converts each page into a `Document` object
* Preserves metadata like page number and source file

**Documentation**

* [https://python.langchain.com/docs/integrations/document_loaders/pdf](https://python.langchain.com/docs/integrations/document_loaders/pdf)

---

### 4. Split Document into Chunks

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=400
)

chunked_documents = text_splitter.split_documents(documents)
```

Why chunking is required:

* LLMs and embedding models have token limits
* Smaller chunks improve semantic retrieval accuracy

Why overlap matters:

* Prevents loss of context between chunk boundaries

**Documentation**

* [https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters)

---

### 5. Initialize OpenAI Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)
```

This component:

* Converts text chunks into high-dimensional vectors
* Uses OpenAI’s hosted embedding models

**Documentation**

* [https://python.langchain.com/docs/integrations/text_embedding/openai](https://python.langchain.com/docs/integrations/text_embedding/openai)
* [https://platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings)

---

### 6. Store Embeddings in Qdrant

```python
from langchain_qdrant import QdrantVectorStore

QdrantVectorStore.from_documents(
    documents=chunked_documents,
    embedding=embeddings,
    url=QDRANT_URL,
    collection_name=COLLECTION_NAME
)
```

This step:

* Creates the Qdrant collection (if not present)
* Embeds each chunk
* Stores vectors + metadata for later similarity search

**Documentation**

* LangChain Qdrant integration
  [https://python.langchain.com/docs/integrations/vectorstores/qdrant](https://python.langchain.com/docs/integrations/vectorstores/qdrant)
* Qdrant official docs
  [https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)

---

## Output

After successful execution:

* All PDF content is indexed into Qdrant
* Each chunk is searchable via vector similarity
* Metadata (page number, source) is preserved

```text
Document indexing completed successfully.
```

---

## Summary

| Component                      | Purpose                  |
| ------------------------------ | ------------------------ |
| PyPDFLoader                    | Load PDF content         |
| RecursiveCharacterTextSplitter | Chunk text with overlap  |
| OpenAIEmbeddings               | Convert text → vectors   |
| QdrantVectorStore              | Store and search vectors |

This setup is production-ready for small to medium-scale RAG systems and can be containerized easily.

---
