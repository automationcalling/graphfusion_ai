from __future__ import annotations

from typing import Any

try:
    from opensearchpy import OpenSearch
except ImportError:  # pragma: no cover
    OpenSearch = None


class OpenSearchClient:
    def __init__(self, host: str, user: str, password: str):
        if OpenSearch is None:
            raise RuntimeError("opensearch-py is required for OpenSearchClient")
        self.client = OpenSearch(
            hosts=[host],
            http_auth=(user, password),
            use_ssl=False,
            verify_certs=False,
        )

    def index_document(self, index: str, doc_id: str, body: dict[str, Any]) -> dict[str, Any]:
        return self.client.index(index=index, id=doc_id, body=body)

    def search(self, index: str, query: dict[str, Any], size: int = 10) -> dict[str, Any]:
        return self.client.search(index=index, body=query, size=size)

    def create_index(self, index: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        if body is None:
            body = {}
        return self.client.indices.create(index=index, body=body, ignore=400)

    def close(self) -> None:
        self.client.close()
