import json
from pathlib import Path

from app.services.retrieval_service import search as dense_search
from app.services.bm25_store import BM25Store
from app.services.hybrid_retrieval import (
    hybrid_search,
    reload_bm25_store,
)
from app.services.hybrid_rerank import hybrid_rerank_search

from eval.metrics import (
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
)

QUERIES_FILE = Path(__file__).parent / "queries.json"


def load_queries():
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_results(results, relevant_chunks):
    return {
        "recall@3": recall_at_k(results, relevant_chunks, 3),
        "recall@5": recall_at_k(results, relevant_chunks, 5),
        "rr": reciprocal_rank(results, relevant_chunks),
        "ndcg@5": ndcg_at_k(results, relevant_chunks, 5),
    }


def average_metrics(metrics):

    if not metrics:
        return {}

    return {
        key: sum(x[key] for x in metrics) / len(metrics)
        for key in metrics[0]
    }


def print_results(name, metrics):

    print(f"\n{name}")
    print("-" * 40)
    print(f"Recall@3 : {metrics['recall@3']:.3f}")
    print(f"Recall@5 : {metrics['recall@5']:.3f}")
    print(f"MRR      : {metrics['rr']:.3f}")
    print(f"nDCG@5   : {metrics['ndcg@5']:.3f}")


def print_topk(name, results):

    print(f"\n{name} Top-{len(results)}")

    if not results:
        print("No results")
        return

    for rank, result in enumerate(results, start=1):

        md = result["chunk"]["metadata"]

        print(
            f"{rank}. "
            f"{md['name']} "
            f"(line {md['start_line']}) "
            f"score={result['score']:.4f}"
        )


def main():

    queries = load_queries()

    bm25 = BM25Store()
    bm25.load("bm25_store")

    reload_bm25_store()

    bm25_metrics = []
    dense_metrics = []
    hybrid_metrics = []
    rerank_metrics = []

    print(f"\nEvaluating {len(queries)} queries...\n")

    for item in queries:

        query = item["query"]
        relevant = item["relevant_chunks"]

        print("=" * 80)
        print(f"[{item['id']}] {query}")

        bm25_results = bm25.search(query, k=5)
        dense_results = dense_search(query, k=5)
        hybrid_results = hybrid_search(query, k=5)
        rerank_results = hybrid_rerank_search(query, k=5)

        bm25_score = evaluate_results(
            bm25_results,
            relevant,
        )

        dense_score = evaluate_results(
            dense_results,
            relevant,
        )

        hybrid_score = evaluate_results(
            hybrid_results,
            relevant,
        )

        rerank_score = evaluate_results(
            rerank_results,
            relevant,
        )

        bm25_metrics.append(bm25_score)
        dense_metrics.append(dense_score)
        hybrid_metrics.append(hybrid_score)
        rerank_metrics.append(rerank_score)

        print(
            f"BM25     : "
            f"R@3={bm25_score['recall@3']:.2f} "
            f"R@5={bm25_score['recall@5']:.2f} "
            f"MRR={bm25_score['rr']:.2f} "
            f"nDCG={bm25_score['ndcg@5']:.2f}"
        )

        print(
            f"Dense    : "
            f"R@3={dense_score['recall@3']:.2f} "
            f"R@5={dense_score['recall@5']:.2f} "
            f"MRR={dense_score['rr']:.2f} "
            f"nDCG={dense_score['ndcg@5']:.2f}"
        )

        print(
            f"Hybrid   : "
            f"R@3={hybrid_score['recall@3']:.2f} "
            f"R@5={hybrid_score['recall@5']:.2f} "
            f"MRR={hybrid_score['rr']:.2f} "
            f"nDCG={hybrid_score['ndcg@5']:.2f}"
        )

        print(
            f"Reranker : "
            f"R@3={rerank_score['recall@3']:.2f} "
            f"R@5={rerank_score['recall@5']:.2f} "
            f"MRR={rerank_score['rr']:.2f} "
            f"nDCG={rerank_score['ndcg@5']:.2f}"
        )

        print_topk("BM25", bm25_results)
        print_topk("Dense", dense_results)
        print_topk("Hybrid", hybrid_results)
        print_topk("Reranker", rerank_results)

    print("\n")
    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    print_results(
        "BM25",
        average_metrics(bm25_metrics),
    )

    print_results(
        "Dense",
        average_metrics(dense_metrics),
    )

    print_results(
        "Hybrid",
        average_metrics(hybrid_metrics),
    )

    print_results(
        "Hybrid + Reranker",
        average_metrics(rerank_metrics),
    )


if __name__ == "__main__":
    main()