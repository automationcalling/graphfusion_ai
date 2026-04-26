from __future__ import annotations

from typing import Any

from src.graph.neo4j_client import Neo4jClient
from src.utils.logging import get_logger

logger = get_logger(__name__)


class GraphRetriever:
    """Graph retrieval using Neo4j relationships."""

    def __init__(self, neo4j_client: Neo4jClient):
        self.client = neo4j_client

    def retrieve(self, entity_name: str, depth: int = 2) -> list[dict[str, Any]]:
        """Retrieve entities related to entity_name up to `depth` hops."""
        # depth is validated to an int to avoid any injection via string formatting
        depth = max(1, min(int(depth), 5))

        # LlamaIndex's Neo4jPropertyGraphStore uses `:__Node__` as the base label.
        # Relationship types are not fixed (LLM-extracted), so we query generically.
        #
        # We also support a fuzzy fallback when an exact name match isn't found.
        query = """
        // 1) Try exact match on name first
        OPTIONAL MATCH (e:__Node__ {name: $entity_name})
        WITH e
        CALL {
            WITH e
            MATCH (e)-[r]->(related:__Node__)
            RETURN related AS related, type(r) AS relationship, 1 AS depth
            UNION
            WITH e
            MATCH (e)<-[r]-(related:__Node__)
            RETURN related AS related, type(r) AS relationship, 1 AS depth
        }
        WITH e, related, relationship, depth
        WHERE e IS NOT NULL
        RETURN related.name AS name,
               coalesce(related.type, head(labels(related))) AS type,
               relationship AS relationship,
               depth AS depth
        LIMIT $limit
        UNION
        // 2) Fuzzy fallback if exact match didn't exist
        MATCH (e:__Node__)
        WHERE e.name IS NOT NULL AND toLower(e.name) CONTAINS toLower($entity_name)
        WITH e
        CALL {
            WITH e
            MATCH (e)-[r]->(related:__Node__)
            RETURN related AS related, type(r) AS relationship, 1 AS depth
            UNION
            WITH e
            MATCH (e)<-[r]-(related:__Node__)
            RETURN related AS related, type(r) AS relationship, 1 AS depth
        }
        RETURN related.name AS name,
               coalesce(related.type, head(labels(related))) AS type,
               relationship AS relationship,
               depth AS depth
        LIMIT $limit
        """

        results = self.client.run(query, {"entity_name": entity_name, "limit": 10})
        logger.info(f"Graph retrieval for '{entity_name}' returned {len(results)} results")

        return [
            {
                "id": f"graph_{i}",
                "content": f"{r.get('name')} ({r.get('type')}) — {r.get('relationship')} — {entity_name}",
                "score": 1.0,
                "source": "graph",
                "entity": r.get("name"),
                "relationship": r.get("relationship"),
            }
            for i, r in enumerate(results)
        ]
