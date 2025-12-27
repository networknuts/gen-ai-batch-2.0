# Querying a Vector Database and Answering Questions Using RAG

This project demonstrates the **retrieval and answer-generation phase** of a Retrieval-Augmented Generation (RAG) system.

It performs the following tasks:

1. Accepts a user query
2. Searches a Qdrant vector database for semantically similar content
3. Builds a controlled context from retrieved documents
4. Sends that context to an LLM
5. Produces an answer strictly grounded in the retrieved data

---

## High-Level Workflow

```

User Query
↓
Vector Similarity Search (Qdrant)
↓
Relevant PDF Chunks
↓
System Prompt with Context
↓
LLM Answer (Context-Only)

````

---

## Prerequisites

- Python 3.9+
- OpenAI API key
- A running Qdrant instance
- A pre-indexed Qdrant collection (created during ingestion)

---

## Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
````

---

## Code Walkthrough

---

### 1. Environment Setup

```python
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()
```

* Loads environment variables
* Initializes the OpenAI client for LLM interaction

**Documentation**

* python-dotenv
  [https://pypi.org/project/python-dotenv/](https://pypi.org/project/python-dotenv/)
* OpenAI Python SDK
  [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)

---

### 2. Embedding Model (Must Match Indexing)

```python
from langchain_openai import OpenAIEmbeddings

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)
```

**Important rule:**
The embedding model **must be identical** to the one used during ingestion.
Mismatch leads to incorrect similarity results.

**Documentation**

* LangChain OpenAI Embeddings
  [https://python.langchain.com/docs/integrations/text_embedding/openai](https://python.langchain.com/docs/integrations/text_embedding/openai)
* OpenAI Embeddings Guide
  [https://platform.openai.com/docs/guides/embeddings](https://platform.openai.com/docs/guides/embeddings)

---

### 3. Connect to Existing Qdrant Collection

```python
from langchain_qdrant import QdrantVectorStore

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning_vectors",
    embedding=embedding_model
)
```

This does **not** re-index data. It:

* Connects to an already populated collection
* Enables similarity search operations

**Documentation**

* LangChain Qdrant Vector Store
  [https://python.langchain.com/docs/integrations/vectorstores/qdrant](https://python.langchain.com/docs/integrations/vectorstores/qdrant)
* Qdrant Official Docs
  [https://qdrant.tech/documentation/](https://qdrant.tech/documentation/)

---

### 4. Accept User Query

```python
query = input("> ")
```

* Reads user input from the terminal
* Acts as the search query for vector similarity

---

### 5. Perform Similarity Search

```python
search_results = vector_db.similarity_search(query=query)
```

This step:

* Converts the query into an embedding
* Performs cosine similarity search
* Returns the most relevant document chunks

Each result contains:

* `page_content`
* `metadata` (page number, source file)

**Documentation**

* Similarity Search
  [https://python.langchain.com/docs/modules/data_connection/vectorstores](https://python.langchain.com/docs/modules/data_connection/vectorstores)

---

### 6. Build Context from Retrieved Documents

```python
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
```

Purpose:

* Formats retrieved chunks into a clean, readable context
* Preserves page numbers for traceability
* Separates chunks using delimiters

This context is later injected into the system prompt.

---

### 7. System Prompt (Strict Grounding)

```python
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
- Mention the relevant page number

If the answer is NOT found:
- Clearly say it is not available in the document

Do NOT add outside knowledge.

Document Context:
{context}
"""
```

Why this matters:

* Prevents hallucination
* Enforces document-grounded answers
* Makes the system auditable and explainable

---

### 8. Generate Answer Using LLM

```python
response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query},
    ]
)
```

* Sends controlled context to the LLM
* Uses GPT-4.1 for high-quality reasoning
* Produces a response constrained by the system prompt

**Documentation**

* Chat Completions API
  [https://platform.openai.com/docs/api-reference/chat](https://platform.openai.com/docs/api-reference/chat)

---

### 9. Output

```python
print(f"\n🤖 {response.choices[0].message.content}")
```

* Displays the final answer to the user
* Includes page references if applicable

---

## Key Design Principles

| Principle               | Description                         |
| ----------------------- | ----------------------------------- |
| Grounded Answers        | LLM can only use retrieved context  |
| Traceability            | Page numbers preserved              |
| Deterministic Retrieval | Same embeddings = consistent search |
| Separation of Concerns  | Retrieval ≠ Generation              |


## Summary

| Component         | Purpose                  |
| ----------------- | ------------------------ |
| OpenAIEmbeddings  | Encode query             |
| QdrantVectorStore | Retrieve relevant chunks |
| System Prompt     | Control hallucination    |
| GPT-4.1           | Generate final answer    |


