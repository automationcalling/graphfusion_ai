from __future__ import annotations

from typing import Any
from src.utils.logging import get_logger

try:
    from neo4j import GraphDatabase
except ImportError:  # pragma: no cover
    GraphDatabase = None

logger = get_logger(__name__)

# Idempotent schema setup — safe to run on every startup
_SCHEMA_QUERIES = [
    # Uniqueness constraint on Entity.id (also creates a backing index)
    "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
    # Index on Entity.name for fast graph retrieval lookups by name
    "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
]


class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        if GraphDatabase is None:
            raise RuntimeError("neo4j is required for Neo4jClient")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def ensure_schema(self) -> None:
        """Create constraints and indexes if they don't already exist."""
        for query in _SCHEMA_QUERIES:
            try:
                self.run(query)
            except Exception as e:
                # Older Neo4j versions may not support IF NOT EXISTS — log and continue
                logger.warning(f"Schema setup query skipped: {e}")
        logger.info("Neo4j schema ensured (constraints + indexes)")

    def close(self) -> None:
        self.driver.close()

    def run(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
