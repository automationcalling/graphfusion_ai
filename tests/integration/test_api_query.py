from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.api.main import app, fuse_context


def test_query_endpoint():
    """Test basic query endpoint functionality."""
    client = TestClient(app)
    response = client.post("/query", json={"query": "What is GraphFusion?"})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is GraphFusion?"
    assert "answer" in data
    assert data["reasoning_type"] in {"semantic", "relationship", "hybrid"}


def test_query_with_llm_response():
    """Test query endpoint with LLM-generated answer."""
    client = TestClient(app)
    
    with patch('src.api.main.llm_client') as mock_llm:
        mock_llm.generate_answer_with_fallback.return_value = {
            "answer": "GraphFusion is a hybrid retrieval system combining vector and graph-based reasoning.",
            "tokens_used": 25,
            "model": "gpt-4",
        }
        
        response = client.post("/query", json={"query": "What is GraphFusion?"})
        assert response.status_code == 200
        data = response.json()
        assert "hybrid retrieval system" in data["answer"]


def test_query_with_sources():
    """Test that query response includes retrieved sources."""
    client = TestClient(app)
    response = client.post("/query", json={"query": "What is machine learning?"})
    assert response.status_code == 200
    data = response.json()
    assert "sources" in data
    assert isinstance(data["sources"], list)


def test_fuse_context_with_multiple_sources():
    """Test context fusion with multiple sources."""
    sources = [
        {"id": "doc1", "content": "First document", "score": 0.95},
        {"id": "doc2", "content": "Second document", "score": 0.85},
    ]
    context = fuse_context(sources, "semantic")
    
    assert "doc1" in context
    assert "doc2" in context
    assert "0.95" in context
    assert "0.85" in context


def test_fuse_context_empty():
    """Test context fusion with empty sources."""
    context = fuse_context([], "semantic")
    assert "No relevant context found" in context


def test_health_check():
    """Test health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
