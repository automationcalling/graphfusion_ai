from __future__ import annotations

from typing import Any
from src.utils.logging import get_logger


logger = get_logger(__name__)


class Ranking:
    """Ranking and deduplication utilities."""

    @staticmethod
    def rank_results(results: list[dict[str, Any]], key: str = "score") -> list[dict[str, Any]]:
        """Rank results by score in descending order."""
        ranked = sorted(results, key=lambda x: x.get(key, 0), reverse=True)
        logger.info(f"Ranked {len(ranked)} results by {key}")
        return ranked

    @staticmethod
    def deduplicate_results(results: list[dict[str, Any]], key: str = "id") -> list[dict[str, Any]]:
        """Remove duplicate results by key."""
        seen = set()
        unique_results = []
        for result in results:
            result_key = result.get(key)
            if result_key not in seen:
                seen.add(result_key)
                unique_results.append(result)
        logger.info(f"Deduplicated: {len(results)} -> {len(unique_results)} results")
        return unique_results


def deduplicate_and_rank(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convenience function: deduplicate then rank by score."""
    unique = Ranking.deduplicate_results(results)
    return Ranking.rank_results(unique)
