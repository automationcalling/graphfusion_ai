# GraphFusion_AI Architecture

## Overview

GraphFusion_AI is a local POC for hybrid retrieval using:
- OpenSearch for vector embeddings
- Neo4j for graph/relationship reasoning
- LlamaIndex for pipeline orchestration
- FastAPI for query API
- Streamlit for UI

## Data Flow

1. Document ingestion parses files, chunks text, generates embeddings, and extracts graph structure.
2. Embeddings are stored in OpenSearch.
3. Entities and relationships are stored in Neo4j.
4. Queries are classified as semantic, relationship, or hybrid.
5. Retrieval routes to OpenSearch, Neo4j, or both.
6. Hybrid queries fuse vector and graph context before response.
