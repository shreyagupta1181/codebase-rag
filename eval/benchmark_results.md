# Retrieval Evaluation Benchmark

## Overview

This benchmark evaluates the retrieval quality of the Codebase RAG system on the **Requests** repository using four retrieval configurations.

The evaluation focuses on retrieval effectiveness before LLM generation using standard Information Retrieval (IR) metrics.

---

## Repository

| Property | Value |
|----------|-------|
| Repository | requests |
| Language | Python |
| Indexed Chunks | 707 |
| Evaluation Queries | 20 |
| Benchmark Type | Symbol Lookup + Conceptual Retrieval |

---

## Retrieval Methods

1. BM25
2. Dense Retrieval (BGE + FAISS)
3. Hybrid Retrieval (Weighted Reciprocal Rank Fusion)
4. Hybrid Retrieval + CrossEncoder Reranker

---

## Evaluation Metrics

### Recall@3
Percentage of queries where at least one relevant chunk appears in the top 3 retrieved results.

### Recall@5
Percentage of queries where at least one relevant chunk appears in the top 5 retrieved results.

### MRR (Mean Reciprocal Rank)
Measures how early the first relevant result appears.

### nDCG@5
Measures ranking quality by rewarding relevant chunks appearing higher in the ranked list.

---

# Results

| Retriever | Recall@3 | Recall@5 | MRR | nDCG@5 |
|-----------|---------:|---------:|----:|--------:|
| BM25 | 0.500 | 0.600 | 0.439 | 0.479 |
| Dense (BGE + FAISS) | 0.850 | 0.900 | 0.713 | 0.761 |
| Hybrid (Weighted RRF) | **0.900** | **0.950** | 0.713 | 0.773 |
| Hybrid + CrossEncoder | 0.850 | 0.850 | **0.767** | **0.788** |

---

# Observations

### BM25

- Strong lexical retrieval.
- Performs well for exact identifier matching.
- Limited semantic understanding.

---

### Dense Retrieval

- Significant improvement over BM25.
- Better handling of conceptual queries.
- High semantic retrieval quality.

---

### Hybrid Retrieval

- Combines Dense Retrieval and BM25 using Weighted Reciprocal Rank Fusion.
- Achieved the highest Recall@3 and Recall@5.
- Improved retrieval coverage while preserving semantic relevance.

---

### Hybrid + CrossEncoder

- Re-ranked Hybrid retrieval candidates using a CrossEncoder.
- Produced the highest MRR and nDCG@5.
- Improved ranking quality by promoting more relevant chunks toward the top of the results.

---

# Conclusion

The evaluation demonstrates that combining lexical and dense retrieval improves retrieval coverage, while CrossEncoder reranking further improves ranking quality.

The final retrieval pipeline is:

Dense Retrieval (FAISS + BGE)
+
BM25
↓
Weighted Reciprocal Rank Fusion
↓
CrossEncoder Reranker
↓
Top-k Context for LLM Generation

---

## Future Work

- Evaluate on additional repositories
- Increase benchmark size beyond 20 queries
- Add latency benchmarking
- Evaluate answer generation quality
- Compare alternative reranker models