"""Evaluate semantic retrieval on the local skills index."""

import argparse

from skill_mcp.db.embedder import embedder
from skill_mcp.db.qdrant_manager import qdrant_manager


def run_eval(queries: list[str]) -> None:
    qdrant_manager.connect()
    
    for q in queries:
        print(f"\n--- Query: '{q}' ---")
        vector = embedder.embed(q)
        results = qdrant_manager.search_frontmatter(vector, top_k=5)
        
        if not results:
            print("No results found.")
            continue
            
        for i, r in enumerate(results, 1):
            score = getattr(r, "score", 0.0)
            print(f"{i}. {r.skill_id} (score: {score:.4f})")
            print(f"   {r.description[:100]}...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "queries", 
        nargs="*", 
        default=[
            "how to debug react hooks",
            "sql injection scanning",
            "terraform aws module deployment"
        ],
        help="Search queries to evaluate"
    )
    args = parser.parse_args()
    run_eval(args.queries)
