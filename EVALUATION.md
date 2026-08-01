# Evaluation

## Overview

To evaluate the retrieval performance of the Codebase RAG system, a manual benchmark was created using the **Requests** repository. The objective was to compare different retrieval strategies before LLM generation and quantify their effectiveness using standard Information Retrieval (IR) metrics.

The benchmark measures retrieval quality only; it does not evaluate answer generation by the language model.

---

# Benchmark Setup

## Repository

| Property | Value |
|----------|-------|
| Repository | requests |
| Language | Python |
| Indexed Chunks | 707 |
| Evaluation Queries | 20 |

---

## Query Types

The benchmark consists of 20 manually curated queries covering two categories:

### Symbol Lookup

Queries that require locating a specific implementation.

Examples:

- Where is `HTTPAdapter` defined?
- Where is `PreparedRequest.prepare_url` defined?
- Where is `proxy_manager_for` implemented?

### Conceptual Retrieval

Queries requiring semantic understanding of the codebase.

Examples:

- How are redirects handled?
- How does Requests verify SSL certificates?
- How is Digest authentication implemented?

---

# Retrieval Pipelines

The following retrieval methods were evaluated.

## 1. BM25

Traditional sparse lexical retrieval using token matching.

---

## 2. Dense Retrieval

Semantic retrieval using:

- **BAAI/bge-small-en-v1.5**
- **FAISS IndexFlatIP**
- Cosine similarity search

---

## 3. Hybrid Retrieval

Combines BM25 and Dense Retrieval using **Weighted Reciprocal Rank Fusion (RRF)**.

This improves retrieval coverage by leveraging both lexical and semantic similarity.

---

## 4. Hybrid + CrossEncoder Reranker

The top candidates from Hybrid Retrieval are reranked using

**cross-encoder/ms-marco-MiniLM-L-6-v2**

The reranker scores each *(query, chunk)* pair jointly and produces a better final ranking.

---

# Evaluation Metrics

## Recall@3

Measures whether a relevant chunk appears within the top 3 retrieved results.

---

## Recall@5

Measures whether a relevant chunk appears within the top 5 retrieved results.

---

## Mean Reciprocal Rank (MRR)

Measures how early the first relevant result appears.

Higher values indicate that relevant chunks are ranked closer to the top.

---

## nDCG@5

Normalized Discounted Cumulative Gain.

Rewards retrieval systems that rank relevant chunks higher while penalizing lower-ranked relevant results.

---

# Results

| Retriever | Recall@3 | Recall@5 | MRR | nDCG@5 |
|-----------|---------:|---------:|----:|--------:|
| BM25 | 0.500 | 0.600 | 0.439 | 0.479 |
| Dense (BGE + FAISS) | 0.850 | 0.900 | 0.713 | 0.761 |
| Hybrid (Weighted RRF) | **0.900** | **0.950** | 0.713 | 0.773 |
| Hybrid + CrossEncoder | 0.850 | 0.850 | **0.767** | **0.788** |

---

# Analysis

### BM25

- Strong lexical matching
- Performs well for exact symbol searches
- Limited semantic understanding

---

### Dense Retrieval

- Significant improvement over BM25
- Better semantic matching
- Handles conceptual queries effectively

---

### Hybrid Retrieval

- Combines lexical and semantic retrieval
- Achieved the highest Recall@3 and Recall@5
- Increased retrieval coverage compared to individual retrievers

---

### Hybrid + CrossEncoder

- Produced the highest MRR
- Produced the highest nDCG@5
- Improved ranking quality by moving relevant chunks closer to the top of the ranked list

Although Recall@5 decreased slightly compared to Hybrid Retrieval, ranking quality improved substantially.

---

# Retrieval Architecture

```text
Repository
      │
      ▼
Chunking
      │
      ▼
Dense Embeddings (BGE)
      │
      ▼
FAISS
      │
      ├──────────────┐
      │              │
      ▼              ▼
 Dense          BM25 Retrieval
      │              │
      └──────┬───────┘
             ▼
 Weighted Reciprocal Rank Fusion
             ▼
 CrossEncoder Reranker
             ▼
 Top-k Context
             ▼
 Large Language Model
```

---

# Key Findings

- Dense retrieval significantly outperformed lexical retrieval alone.
- Hybrid retrieval achieved the highest retrieval coverage.
- CrossEncoder reranking improved ranking quality by increasing MRR and nDCG.
- Combining lexical retrieval, dense retrieval, and reranking provides a more robust retrieval pipeline than any individual method.

---

# Limitations

- Evaluation was conducted on a single repository.
- Benchmark size is limited to 20 manually curated queries.
- Ground truth labels were manually created.
- Generation quality was not evaluated.

---

# Future Work

- Evaluate on additional repositories.
- Expand the benchmark with more diverse conceptual queries.
- Compare multiple embedding models.
- Evaluate larger CrossEncoder rerankers.
- Measure retrieval latency (P50/P95).
- Evaluate end-to-end answer quality using RAG-specific metrics.

---

# Reproducibility

Run the evaluation suite:

```bash
python -m eval.run_eval
```

The benchmark computes:

- Recall@3
- Recall@5
- Mean Reciprocal Rank (MRR)
- nDCG@5

for all implemented retrieval strategies.