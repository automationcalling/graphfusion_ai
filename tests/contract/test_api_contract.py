"""Contract tests: verify API response shapes match the spec (FR-022)."""
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_query_response_contract():
    """POST /query must return answer, sources, and reasoning_type."""
    response = client.post("/query", json={"query": "What is machine learning?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data
    assert "reasoning_type" in data
    assert data["reasoning_type"] in {"semantic", "relationship", "hybrid"}
    assert isinstance(data["sources"], list)


def test_health_response_contract():
    """GET /health must return status field."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()


def test_upload_response_contract():
    """POST /upload must return filename, format, chunk_count, entity_count, relationship_count."""
    import io
    fake_file = io.BytesIO(b"Sample text content for contract testing.")
    response = client.post("/upload", files={"file": ("sample.txt", fake_file, "text/plain")})
    assert response.status_code == 200
    data = response.json()
    assert "filename" in data
    assert "format" in data
    assert "chunk_count" in data
    assert "entity_count" in data
    assert "relationship_count" in data
