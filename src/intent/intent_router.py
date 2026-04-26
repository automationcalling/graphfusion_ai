from __future__ import annotations

from typing import Any
from src.intent.intent_detector import IntentDetector
from src.utils.logging import get_logger


logger = get_logger(__name__)


class IntentRouter:
    """Routes queries to appropriate retrieval based on intent."""

    def __init__(self):
        self.detector = IntentDetector()

    def route(self, query: str) -> dict[str, Any]:
        """Route query based on detected intent."""
        intent = self.detector.detect_intent(query)
        
        routing = {
            "query": query,
            "intent": intent,
            "use_vector": intent in ["semantic", "hybrid"],
            "use_graph": intent in ["relationship", "hybrid"],
        }
        
        logger.info(f"Routing: {routing}")
        return routing
