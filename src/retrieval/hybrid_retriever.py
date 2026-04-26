from __future__ import annotations

from typing import Any
from src.retrieval.vector_retriever import VectorRetriever
from src.retrieval.graph_retriever import GraphRetriever
from src.utils.logging import get_logger


logger = get_logger(__name__)


class HybridRetriever:
    """Fuses vector and graph results for hybrid queries."""

    def __init__(self, vector_retriever: VectorRetriever, graph_retriever: GraphRetriever):
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever

    def retrieve_hybrid(
        self, query_embedding: list[float], entity_name: str
    ) -> dict[str, Any]:
        """Fuse vector and graph context."""
        vector_results = self.vector_retriever.retrieve(query_embedding, index="graphfusion_chunks")
        graph_results = self.graph_retriever.retrieve(entity_name)
        
        fused_results = {
            "vector_results": vector_results,
            "graph_results": graph_results,
            "reasoning_type": "hybrid",
            "fusion_note": "Combined vector semantic results with graph relationship context",
        }
        
        logger.info("Hybrid retrieval fused vector and graph results")
        return fused_results
