# GraphFusion AI

**Proof-of-concept: Intent-aware hybrid retrieval combining vector search + graph reasoning**

> **Status**: POC / Learning project — not production-ready. No benchmarks yet. Contributions welcome.

## About

**GraphFusion AI** is an intent-aware hybrid RAG POC that fuses **vector search** (OpenSearch) with **graph reasoning** (Neo4j). It includes document ingestion (LlamaIndex), a FastAPI query API, a Streamlit UI, and Azure OpenAI for embeddings + answer synthesis.

**Suggested GitHub topics:** `rag`, `hybrid-search`, `retrieval-augmented-generation`, `knowledge-graph`, `graph-rag`, `neo4j`, `opensearch`, `llamaindex`, `fastapi`, `streamlit`, `azure-openai`, `embeddings`, `intent-detection`, `document-ingestion`, `ocr`

GraphFusion demonstrates a hybrid RAG architecture that routes queries by intent and fuses results from multiple retrieval sources:

- **Intent detection** classifies queries as semantic, relationship, or hybrid
- **Vector retrieval** (OpenSearch) for semantic similarity
- **Graph retrieval** (Neo4j) for relationship reasoning  
- **Fusion logic** combines and ranks results from both stores
- **LLM synthesis** generates answers with source attribution

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
# Then start all services
docker-compose up -d

# Access services:
# - UI: http://localhost:8501
# - API: http://localhost:8000/docs (Swagger)
# - OpenSearch: http://localhost:9200
# - Neo4j: http://localhost:7474
```

### Notes (POC defaults)

- Docker Compose uses a **default Neo4j password** (`neo4j/password`) for local demos. Do not reuse this in production.
- OpenSearch security is disabled for local use.
- Ingestion logs can be noisy (especially PDFs with many embedded images). Reduce verbosity by setting `LOG_LEVEL=WARNING`.

### Option 2: Local Python

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Start OpenSearch and Neo4j separately, then:
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
streamlit run src/ui/app.py --server.port 8501
```

## What This POC Demonstrates

| Feature | Status | Notes |
|---------|--------|-------|
| Intent-aware query routing | Working | Rule-based classification |
| Vector retrieval (OpenSearch) | Working | Cosine similarity on embeddings |
| Graph retrieval (Neo4j) | Working | Entity/relationship lookups |
| Hybrid fusion | Basic | Score-weighted concatenation |
| Document ingestion (PDF, Word, PPT, Excel) | Working | Via LlamaIndex |
| Azure OpenAI integration | Working | Chat + embeddings |
| Streamlit UI | Working | Chat + upload interface |
| **Benchmarks / Evaluation** | Missing | Planned |
| **Test suite** | Missing | Planned |
| Image/diagram extraction | Working (POC) | OCR (default) or VLM mode; extracted content is appended to document text |

## Architecture

```mermaid
flowchart LR
  %% ───────────────────────── Ingestion ─────────────────────────
  subgraph ING[Ingestion (Upload)]
    U[User uploads document\n(PDF/Word/PPT/Excel/TXT)] --> APIU[FastAPI: POST /upload]
    APIU --> PARSE[Parser: extract text + embedded images]
    PARSE --> IMG{Images found?}
    IMG -- No --> DOC[Combined document text]
    IMG -- Yes --> MODE{IMAGE_EXTRACTION_MODE}
    MODE -- OCR --> OCR[OCR: pytesseract\n(raw text)]
    MODE -- VLM --> VLM[VLM: Azure OpenAI Vision\n(entities/relationships → text)]
    OCR --> DOC
    VLM --> DOC
    DOC --> LI[LlamaIndex ingestion]
    LI --> SPLIT[SentenceSplitter\n(chunking)]
    SPLIT --> EMB[Azure OpenAI Embeddings]
    EMB --> OS[(OpenSearch\nVector Index)]
    DOC --> KG[LLM Graph Extraction\n(SimpleLLMPathExtractor)]
    KG --> N4J[(Neo4j\nProperty Graph Store)]
  end

  %% ───────────────────────── Query ─────────────────────────
  subgraph QRY[Query (Chat/API)]
    Q[User query] --> APIQ[FastAPI: POST /query]
    APIQ --> INT[Intent detector + router]
    INT -->|semantic| VR[Vector retriever\n(OpenSearch kNN)]
    INT -->|relationship| GR[Graph retriever\n(Neo4j traversal)]
    INT -->|hybrid| BOTH[Vector + Graph]
    VR --> FUSE[Fusion + ranking\n(dedup + score)]
    GR --> FUSE
    BOTH --> FUSE
    FUSE --> LLM[Azure OpenAI (chat)]
    LLM --> OUT[Answer + sources\n+ reasoning_type]
  end
```

**Key modules:**

- `src/intent/` — Query intent classification (semantic, relationship, hybrid)
- `src/retrieval/` — Vector, graph, and hybrid retrievers with ranking
- `src/ingestion/` — Document parsing, chunking, embedding, graph extraction
- `src/api/` — FastAPI REST API (`POST /query`, `POST /upload`)
- `src/ui/` — Streamlit chat interface
- `src/llm/` — Azure OpenAI client wrapper
- `src/graph/` — Neo4j client
- `src/search/` — OpenSearch client
- `src/utils/` — Logging and utilities

See [docs/architecture.md](docs/architecture.md) for detailed architecture.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/query` | POST | `{"query": "your question"}` → answer, sources, reasoning_type |
| `/upload` | POST | Multipart form with `file` field → ingestion stats |
| `/health` | GET | Health check with LLM status |

## Configuration

Required environment variables (see `.env.example`):

```bash
# Azure OpenAI (required)
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large

# OpenSearch (required)
OPENSEARCH_HOST=http://localhost:9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_INDEX=graphfusion_chunks

# Neo4j (required)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-password>
```

### Image extraction modes

- `IMAGE_EXTRACTION_MODE=ocr` (default): uses OCR to extract raw text from embedded images.
- `IMAGE_EXTRACTION_MODE=vlm`: calls a vision-capable Azure OpenAI model to extract structured entities/relationships from images; these are converted into text and appended to the document before ingestion.

See `docs/IMAGE_EXTRACTION.md`.

## Known Gaps (Next Steps)

This is a **proof-of-concept**, not production software:

- [ ] **No test suite** — unit, integration, and contract tests needed
- [ ] **No benchmarks** — need evaluation showing when hybrid beats single-store
- [ ] **Basic fusion logic** — currently score-weighted concatenation; RRF or learned re-ranking would improve results
- [ ] **Graph schema alignment** — ensure graph retrieval queries match the Neo4j schema created by LlamaIndex
- [ ] **No CI/CD** — GitHub Actions for tests and linting needed
- [ ] **Limited error handling** — graceful degradation when services are unavailable

## Publishing to GitHub (safety)

- Do not commit `.env` (it is ignored). Commit `.env.example` only.
- If you added any keys while testing, rotate them before publishing.

## Contributing

This is a learning project. If you find bugs or want to add features:

1. Fork the repo
2. Create a feature branch
3. Open a PR describing your change

Priority contributions:
- Test coverage (pytest)
- Evaluation benchmarks (retrieval quality, latency)
- Advanced fusion algorithms (reciprocal rank fusion, query-dependent weighting)
- Image/diagram-to-graph extraction

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Built with:** FastAPI, Streamlit, OpenSearch, Neo4j, LlamaIndex, Azure OpenAI
