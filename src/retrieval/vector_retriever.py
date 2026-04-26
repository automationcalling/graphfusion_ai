from __future__ import annotations

from typing import Any
from src.search.opensearch_client import OpenSearchClient
from src.utils.logging import get_logger


logger = get_logger(__name__)


class VectorRetriever:
    """Vector retrieval using OpenSearch embeddings."""

    def __init__(self, opensearch_client: OpenSearchClient):
        self.client = opensearch_client

    def retrieve(self, query_embedding: list[float], index: str, top_k: int = 5) -> list[dict[str, Any]]:
        """Retrieve semantically similar chunks."""
        search_body = {
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k,
                    }
                }
            },
            "size": top_k,
        }
        
        results = self.client.search(index, search_body)
        logger.info(f"Vector retrieval returned {len(results.get('hits', {}).get('hits', []))} results")
        
        return [
            {
                "id": hit["_id"],
                "content": hit["_source"].get("content", ""),
                "score": hit.get("_score", 0),
                "source": "vector",
            }
            for hit in results.get("hits", {}).get("hits", [])
        ]
