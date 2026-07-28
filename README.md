# Codebase RAG

Codebase RAG is a repository-aware question answering system that allows developers to ingest a GitHub repository and ask natural-language questions about its implementation.

Instead of treating source code as plain text, the system parses Python code using AST-based structural chunking, builds both dense and sparse retrieval indexes, performs hybrid retrieval using FAISS and BM25, and generates grounded answers with source citations.

The project includes a FastAPI backend and a React frontend for repository ingestion and interactive codebase exploration.

---

## Features

- Ingest public GitHub repositories
- Clone or update previously ingested repositories
- Parse Python source code using AST
- Chunk code by functions, classes, and methods
- Preserve symbol metadata and source line numbers
- Dense semantic retrieval using vector embeddings and FAISS
- Sparse lexical retrieval using BM25
- Hybrid retrieval using Reciprocal Rank Fusion (RRF)
- Symbol-aware query routing
- Grounded LLM answer generation
- Source citations with file paths and line numbers
- Repository persistence across frontend refreshes
- React-based chat interface

---

## Architecture

```text
                        GitHub Repository
                               │
                               ▼
                       Repository Ingestion
                               │
                         Clone / Update
                               │
                               ▼
                           AST Parser
                               │
                Functions / Classes / Methods
                               │
                               ▼
                         Code Chunking
                               │
                  ┌────────────┴────────────┐
                  │                         │
                  ▼                         ▼
             Embeddings                Tokenisation
                  │                         │
                  ▼                         ▼
                FAISS                     BM25
             Dense Search             Sparse Search
                  │                         │
                  └────────────┬────────────┘
                               │
                               ▼
                  Reciprocal Rank Fusion
                               │
                               ▼
                         Query Router
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
              Symbol Lookup        Hybrid Retrieval
                    │                     │
                    └──────────┬──────────┘
                               ▼
                        Retrieved Context
                               │
                               ▼
                         Local LLM
                           (Ollama)
                               │
                               ▼
                  Grounded Answer + Sources
                               │
                               ▼
                        React Frontend
```

---

## How It Works

### 1. Repository Ingestion

The user provides the URL of a public GitHub repository.

The backend clones the repository locally. If the repository has already been cloned, the existing copy is updated instead of creating another copy.

The repository is then passed through the parsing and indexing pipeline.

---

### 2. AST-Based Code Parsing

Python files are parsed using Python's Abstract Syntax Tree (`ast`) module.

Instead of splitting source code using arbitrary character or token boundaries, the parser extracts meaningful programming structures such as:

- functions
- async functions
- classes
- methods
- imports
- docstrings
- assignments

Methods are stored using qualified names such as:

```text
APIRouter.include_router
FastAPI.openapi
GenerationService.generate
```

This provides more meaningful retrieval units than fixed-size text chunks.

---

### 3. Code Chunking

Parsed structures are converted into independently searchable chunks.

Each chunk contains the source code along with metadata such as:

```text
file
type
name
start_line
end_line
```

For example:

```text
Type: method
Name: APIRouter.include_router
File: fastapi/routing.py
Lines: 3082-3269
```

The metadata is later used both for retrieval and source citations.

---

## Retrieval System

Codebase RAG combines two retrieval strategies.

### Dense Retrieval — FAISS

Each code chunk is converted into a vector embedding.

FAISS stores these vectors and performs similarity search between the user's query embedding and repository code embeddings.

Dense retrieval is useful for conceptual questions where the query may not contain the exact terminology used in the source code.

For example:

```text
How does the application combine search results?
```

may retrieve code related to hybrid retrieval even if the exact wording does not appear in the source.

---

### Sparse Retrieval — BM25

BM25 performs lexical retrieval based on token overlap between the query and indexed code.

The tokenizer handles common programming naming conventions such as:

```text
include_router → include router
getOpenAPISchema → get Open API Schema
```

The BM25 document representation includes symbol name, type, filename, and source code.

This makes BM25 particularly useful for exact identifiers such as:

```text
APIRouter
include_router
GenerationService
```

---

### Hybrid Retrieval

Dense and sparse retrieval are combined to benefit from both semantic similarity and exact lexical matching.

```text
Query
  │
  ├── FAISS ──► semantic candidates
  │
  └── BM25 ───► lexical candidates
                    │
                    ▼
           Reciprocal Rank Fusion
                    │
                    ▼
               Final Ranking
```

A larger candidate pool is retrieved from both systems before fusion.

Test-file results are slightly penalised during ranking so that implementation code is preferred when relevance is otherwise similar.

---

## Reciprocal Rank Fusion

FAISS and BM25 scores are not directly comparable because the two systems use different scoring methods.

Instead of combining raw scores, Codebase RAG uses Reciprocal Rank Fusion (RRF).

For a result ranked at position `r`:

```text
RRF score = 1 / (k + r)
```

Results appearing highly in both retrieval systems accumulate a higher combined score.

This allows the application to combine heterogeneous retrieval systems without normalising their raw scores.

---

## Query Routing

Not every question should be handled in exactly the same way.

The query router distinguishes between symbol-oriented queries and conceptual queries.

For example:

```text
APIRouter.include_router
```

can benefit from direct symbol lookup.

Whereas:

```text
How does FastAPI include routers?
```

requires broader hybrid retrieval.

The router therefore chooses between symbol lookup and hybrid retrieval depending on the structure of the query.

---

## Grounded Answer Generation

Retrieved chunks are passed to the LLM as repository context.

The generation layer is instructed to answer using only the retrieved repository information.

The model returns structured output containing:

```json
{
  "answerable": true,
  "answer": "Generated answer...",
  "used_sources": [1, 2]
}
```

Only sources actually used to support the answer are returned to the frontend.

If the retrieved repository context is insufficient, the system returns:

```text
I couldn't find enough information in the repository.
```

instead of intentionally relying on external knowledge.

---

## Source Citations

Answers include the source code locations used during generation.

Example:

```text
FastAPI.openapi

app/applications.py

method · lines 1070–1103
```

This allows users to verify generated explanations against the repository itself.

---

## Tech Stack

### Backend

- Python
- FastAPI
- GitPython
- Python AST
- FAISS
- BM25 (`rank-bm25`)
- Hugging Face / Sentence Transformers
- Ollama

### Frontend

- React
- Vite
- JavaScript
- CSS

---

## Project Structure

```text
codebase-rag/
│
├── app/
│   ├── api/
│   │   ├── ask.py
│   │   └── ingest.py
│   │
│   ├── services/
│   │   ├── ast_parser.py
│   │   ├── bm25_store.py
│   │   ├── chunking_service.py
│   │   ├── embedding_service.py
│   │   ├── generation_service.py
│   │   ├── git_service.py
│   │   ├── hybrid_retrieval.py
│   │   ├── indexing_service.py
│   │   ├── llm_service.py
│   │   ├── query_router.py
│   │   ├── retrieval_service.py
│   │   └── vector_store.py
│   │
│   └── main.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── main.jsx
│   │
│   └── package.json
│
├── repositories/
├── vector_store/
├── bm25_store/
├── requirements.txt
└── README.md
```

> The exact structure may vary slightly as the project evolves.

---

## API Endpoints

### `POST /ingest`

Ingest and index a GitHub repository.

Example request:

```json
{
  "repo_url": "https://github.com/user/repository"
}
```

The ingestion pipeline:

```text
GitHub
  ↓
Clone / Update
  ↓
AST Parsing
  ↓
Chunking
  ↓
Embeddings
  ↓
FAISS + BM25
  ↓
Ready
```

---

### `POST /ask`

Ask a question about the currently indexed repository.

Example:

```json
{
  "question": "How does hybrid retrieval work?"
}
```

Example response:

```json
{
  "answer": "The repository combines dense and sparse retrieval...",
  "sources": [
    {
      "id": 1,
      "file": "app/services/hybrid_retrieval.py",
      "type": "function",
      "name": "hybrid_search",
      "start_line": 51,
      "end_line": 61
    }
  ]
}
```

---

### `GET /repository`

Returns information about the currently indexed repository.

The frontend uses this endpoint to restore the active repository after a browser refresh.

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/shreyagupta1181/codebase-rag.git
cd codebase-rag
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Ollama

Make sure Ollama is installed and the configured model is available locally.

Then start the backend:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### 5. Start the frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend will normally run at:

```text
http://localhost:5173
```

---

## Example Questions

After indexing a repository, users can ask questions such as:

```text
What does APIRouter.include_router do?

How does FastAPI generate its OpenAPI schema?

How does hybrid retrieval work?

How does the query router decide when to use symbol lookup?

What does GenerationService.generate do?
```

---

## Current Limitations

### Single Active Repository

The current version maintains one active retrieval index at a time.

Indexing another repository replaces the active FAISS and BM25 indexes.

Multi-repository index management and repository switching could be added in a future version.

### Python-Focused Structural Parsing

AST-based structural parsing currently focuses on Python source code.

Supporting languages such as JavaScript, TypeScript, Java, C++, and Go would require language-specific parsers or a general parsing framework such as Tree-sitter.

### Inherited Symbol Resolution

Symbols are indexed according to the class in which they are defined.

For example, if:

```text
Flask → App → Scaffold
```

and `route()` is defined by `Scaffold`, the index contains:

```text
Scaffold.route
```

A query for:

```text
Flask.route
```

does not currently resolve the inheritance chain deterministically.

Future work could build a symbol graph containing inheritance and other code relationships.

### Retrieval Quality

Hybrid retrieval improves robustness but does not guarantee that the most relevant implementation chunk will always rank first.

Large repositories containing extensive tests, documentation, repeated identifiers, and complex inheritance structures can introduce retrieval noise.

---

## Future Improvements

Potential extensions include:

- inheritance-aware symbol resolution
- multi-repository index management
- repository selector and switching
- support for additional programming languages
- Tree-sitter based parsing
- reranking retrieved chunks
- code dependency and call graphs
- conversation history
- incremental indexing of changed files
- GitHub authentication for private repositories
- clickable GitHub source links
- streaming LLM responses

---

## Design Decisions

### Why AST instead of fixed-size chunking?

Source code has structural boundaries.

A function or method represents a meaningful unit of behaviour, while splitting code every fixed number of characters can separate a function from its context.

AST parsing allows chunks to follow actual program structure.

### Why both BM25 and FAISS?

Code questions can be both lexical and semantic.

BM25 is strong when users provide exact identifiers, while dense retrieval can match conceptually similar descriptions.

Combining both makes retrieval more robust.

### Why RRF?

BM25 and FAISS produce scores on different scales.

RRF combines rankings rather than raw scores, avoiding the need to directly compare incompatible scoring systems.

### Why grounded generation?

An LLM can answer programming questions from its pre-existing knowledge, but that does not guarantee that the answer describes the repository currently being analysed.

Grounding generation in retrieved repository context makes answers repository-specific and allows the system to provide verifiable source locations.

---

## Status

The current version implements the complete core RAG pipeline:

```text
Repository
    ↓
AST Parsing
    ↓
Structural Chunking
    ↓
FAISS + BM25
    ↓
Hybrid Retrieval
    ↓
Query Routing
    ↓
Grounded Generation
    ↓
Source Citations
    ↓
React Interface
```

The project is currently focused on improving retrieval quality, repository generalisation, and deployment.

---

## Author

**Shreya Gupta**

GitHub: `shreyagupta1181`