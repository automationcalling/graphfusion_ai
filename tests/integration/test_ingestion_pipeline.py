import pytest
from src.ingestion.parser import parse_document


def test_parse_document(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("Hello world")
    doc = parse_document(str(p))
    assert "content" in doc
    assert doc["content"] == "Hello world"
