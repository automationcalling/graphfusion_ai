# GraphFusion_AI Constitution

## Core Principles

### I. Core Architecture Principle
The system must follow an intent-aware hybrid retrieval architecture combining vector and graph-based reasoning.

All queries must be routed dynamically based on intent:
- Semantic → Vector retrieval
- Relationship → Graph retrieval
- Hybrid → Combined retrieval

### II. Technology Constraint
- **Python**: 3.12+ required; use built-in generics (`list`, `dict`, `X | None`) — no `typing.List/Dict/Optional`
- Vector DB: OpenSearch (POC), replaceable with AWS OpenSearch
- Graph DB: Neo4j (POC), replaceable with Neptune
- Backend: FastAPI
- UI: Streamlit
- LLM: Azure OpenAI
- RAG Engine: LlamaIndex
- Orchestration: Keep the POC minimal; add orchestration frameworks only when needed

### III. Deployment Rule
The system must be deployable locally using containerized services for POC.

All components must be loosely coupled to allow migration to managed cloud services without refactoring.

### IV. Data Ingestion Principle
All ingested data must support dual indexing:
- Vector embeddings for semantic retrieval
- Graph representation for relationship reasoning

Entity and document linkage should be possible across both stores (POC may be approximate).

Image/diagram handling must be explicit:
- OCR mode extracts raw text from images
- VLM mode extracts structured entities/relationships from images and converts them into text that is appended to document content for downstream ingestion

### V. Performance & Behavior Rules
- Default retrieval must NOT always be hybrid (cost optimization)
- Intent detection is mandatory before retrieval
- System must return explainable responses (source + reasoning type)

## Additional Constraints

### Security Requirements
- **NEVER** commit `.env` files or secrets to version control
- All credentials must be loaded from environment variables
- API keys must be validated at startup with clear error messages
- Temporary files from uploads must be cleaned up after processing
- Default/local passwords used for Docker demo are acceptable for a POC, but must be called out clearly as non-production defaults

### Code Quality Standards
- Dead code and unused file references must be removed promptly
- Task and spec files must reflect actual implementation
- Module structure should be flat and pragmatic (avoid over-engineering)

Technology stack requirements, compliance standards, deployment policies, etc.

## Development Workflow

Code review requirements, testing gates, deployment approval process, etc.

## Governance
Constitution supersedes all other practices; Amendments require documentation, approval, migration plan

All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance

**Version**: 1.2 | **Ratified**: 2026-04-23 | **Last Amended**: 2026-04-26
