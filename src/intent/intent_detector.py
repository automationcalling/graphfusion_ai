from __future__ import annotations

from src.utils.logging import get_logger


logger = get_logger(__name__)


class IntentDetector:
    """Rule-based intent detection for queries."""

    def __init__(self):
        self.semantic_keywords = {"what", "how", "explain", "describe", "define"}
        self.relationship_keywords = {"who", "related", "connection", "associate", "link", "between"}

    def detect_intent(self, query: str) -> str:
        """Classify query as semantic, relationship, or hybrid."""
        query_lower = query.lower()
        
        has_semantic = any(kw in query_lower for kw in self.semantic_keywords)
        has_relationship = any(kw in query_lower for kw in self.relationship_keywords)
        
        if has_semantic and has_relationship:
            logger.info(f"Query classified as HYBRID: {query}")
            return "hybrid"
        elif has_relationship:
            logger.info(f"Query classified as RELATIONSHIP: {query}")
            return "relationship"
        else:
            logger.info(f"Query classified as SEMANTIC: {query}")
            return "semantic"
