# Feature Specification: GraphFusion System Features

**Feature Branch**: `001-graphfusion-system-spec`  
**Created**: 2026-04-23  
**Status**: Implemented (POC)  
**Input**: User description: "Feature 1: Data Ingesiton Pipeline - Parse documents (PDF, text) - Chunk content - Generate embeddings - Extract entities and relationships - Convert diagrams/images to graph format - Store: - embeddings → OpenSearch - graph → Neo4j

Feature 2: Feature 2: Intent Detection Engine - Classify queries: - Semantic - Relationship - Hybrid - Initial version: rule-based - Future: LLM-based classification

Future 3: Retrieval Engine - Vector retrieval (OpenSearch) - Graph traversal (Neo4j) - Hybrid retrieval (fusion logic) - Ranking + deduplication

Feature 4: LlamaIndex Integration - Use LlamaIndex for: - ingestion support - chunking - retrieval pipeline - Extend with custom orchestration

Feature 5: API Layer (FAST API)

POST /query - Accept query - Run intent detection - Route retrieval - Return: - answer - sources - reasoning type

Feature 6: UI (Streamlit)

- Chat interface - Display: - response - sources - reasoning (vector/graph/hybrid)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Data Ingestion Pipeline (Priority: P1)

As a data engineer, I want to ingest documents (PDF, PowerPoint, Word, text) including embedded images so that they can be processed and stored for future retrieval.

**Why this priority**: This is the foundation of the system, enabling all subsequent features.

**Independent Test**: Can be fully tested by ingesting a sample document and verifying that embeddings are stored in OpenSearch and graph data in Neo4j.

**Acceptance Scenarios**:

1. **Given** a PDF document, **When** the ingestion pipeline is run, **Then** the document is parsed, chunked, embeddings generated, entities and relationships extracted, and stored in both OpenSearch and Neo4j.
2. **Given** a text document, **When** the ingestion pipeline is run, **Then** the same processing occurs successfully.
3. **Given** a PDF with embedded images/diagrams, **When** the ingestion pipeline is run, **Then** images are extracted, described using Vision API, embeddings generated, and graph data extracted.
4. **Given** a PowerPoint presentation, **When** the ingestion pipeline is run, **Then** slides are parsed, images extracted and processed, and all content ingested.
5. **Given** a Word document with images, **When** the ingestion pipeline is run, **Then** text and images are both processed and ingested.

---

### User Story 2 - Intent Detection Engine (Priority: P2)

As a user, I want my queries to be classified by intent so that the system can route to the appropriate retrieval method.

**Why this priority**: Enables efficient retrieval by avoiding unnecessary hybrid searches and ensuring the correct store is used.

**Independent Test**: Can be tested by sending various queries and verifying correct classification (semantic, relationship, hybrid).

**Acceptance Scenarios**:

1. **Given** a semantic query like "What is machine learning?", **When** intent detection runs, **Then** it classifies as "Semantic".
2. **Given** a relationship query like "How are John and Mary related?", **When** intent detection runs, **Then** it classifies as "Relationship".
3. **Given** a complex query that requires both content understanding and relationship context, **When** intent detection runs, **Then** it classifies as "Hybrid".

---

### User Story 3 - Retrieval Engine (Priority: P3)

As a user, I want to retrieve relevant information using vector, graph, or hybrid methods so that I get accurate answers.

**Why this priority**: Core functionality for answering queries.

**Independent Test**: Can be tested by querying the system and verifying retrieval from the correct stores with ranking and deduplication.

**Acceptance Scenarios**:

1. **Given** a semantic query, **When** retrieval is performed, **Then** results come from vector retrieval with ranking.
2. **Given** a relationship query, **When** retrieval is performed, **Then** results come from graph traversal.
3. **Given** a hybrid query, **When** retrieval is performed, **Then** the system fuses vector and graph context and returns a combined answer.

---

### User Story 4 - LlamaIndex Integration (Priority: P4)

As a developer, I want to use LlamaIndex for ingestion and retrieval so that I can leverage existing capabilities and extend them.

**Why this priority**: Builds on existing tools for faster development.

**Independent Test**: Can be tested by verifying LlamaIndex handles chunking and retrieval as specified.

**Acceptance Scenarios**:

1. **Given** documents, **When** LlamaIndex is used for ingestion, **Then** chunking and initial processing is handled.
2. **Given** a query, **When** LlamaIndex retrieval pipeline is used, **Then** it integrates with custom orchestration.

---

### User Story 5 - API Layer (Priority: P5)

As an API consumer, I want to query the system via REST API so that I can integrate it into other applications.

**Why this priority**: Provides programmatic access.

**Independent Test**: Can be tested by sending POST /query requests and verifying responses include answer, sources, and reasoning type.

**Acceptance Scenarios**:

1. **Given** a query, **When** POST /query is called, **Then** intent detection runs, retrieval routes correctly, context is fused, sent to Azure OpenAI, and response includes all required fields.

---

### User Story 6 - UI (Priority: P6)

As an end user, I want a chat interface to interact with the system so that I can ask questions and see responses with sources and reasoning.

**Why this priority**: User-facing interface for interaction.

**Independent Test**: Can be tested by using the Streamlit UI to submit queries and verify display of response, sources, and reasoning type.

**Acceptance Scenarios**:

1. **Given** a query in the chat interface, **When** submitted, **Then** retrieval occurs, context is sent to Azure OpenAI for answer generation, and response, sources, and reasoning (vector/graph/hybrid) are displayed.

---

### User Story 7 - Document Upload for Data Ingestion (Priority: P0)

As a user, I want to upload documents through the UI so that they can be ingested into the knowledge base without using command-line tools.

**Why this priority**: This is the primary entry point for populating the knowledge base. Without ingested documents, the system has no data to retrieve from.

**Independent Test**: Can be tested by uploading a document via the UI and verifying that embeddings are stored in OpenSearch and graph data in Neo4j.

**Acceptance Scenarios**:

1. **Given** a PDF document, **When** uploaded via the UI and ingestion is triggered, **Then** the document is parsed, chunked, embeddings generated, entities and relationships extracted, and stored in both OpenSearch and Neo4j.
2. **Given** a Word document, **When** uploaded via the UI and ingestion is triggered, **Then** the same processing occurs successfully.
3. **Given** a PowerPoint presentation, **When** uploaded via the UI and ingestion is triggered, **Then** slides are parsed and all content ingested.
4. **Given** an Excel spreadsheet, **When** uploaded via the UI and ingestion is triggered, **Then** sheet data is parsed and ingested.
5. **Given** a text file, **When** uploaded via the UI and ingestion is triggered, **Then** the content is ingested.
6. **Given** an unsupported file format (e.g., .exe, .zip), **When** uploaded via the UI, **Then** the system rejects it with an appropriate error message.
7. **Given** a document upload, **When** ingestion completes, **Then** the UI displays ingestion statistics (filename, format, chunk count, entity count, relationship count).

### Edge Cases

- What happens when a document fails to parse?
- How does system handle unsupported file formats?
- What if intent detection is ambiguous?
- How to handle empty or malformed queries?
- What if retrieval returns no results?
- What happens when Azure OpenAI is unavailable or rate-limited?
- How does system handle LLM hallucinations or irrelevant responses?
- What if fused context exceeds LLM token limits?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST parse documents (PDF, Word, PowerPoint, text)
- **FR-002**: System MUST chunk content
- **FR-003**: System MUST generate embeddings using Azure OpenAI embedding models
- **FR-004**: System MUST support graph extraction into Neo4j using an LLM-based extractor (POC)
- **FR-005**: System MUST support extracting text from embedded images using either:
  - OCR mode (raw text), or
  - VLM mode (structured entities/relationships converted into text and appended to the document)
- **FR-006**: System MUST store embeddings in OpenSearch
- **FR-007**: System MUST store graph data in Neo4j
- **FR-008**: System MUST classify queries as Semantic, Relationship, or Hybrid
- **FR-009**: System MUST use rule-based classification initially
- **FR-010**: System MUST support vector retrieval from OpenSearch
- **FR-011**: System MUST support graph traversal from Neo4j
- **FR-012**: System MUST support hybrid retrieval with fusion logic
- **FR-013**: System MUST fuse vector and graph context for hybrid queries
- **FR-014**: System MUST perform ranking and deduplication on results
- **FR-015**: System MUST integrate LlamaIndex for ingestion support
- **FR-016**: System MUST integrate LlamaIndex for chunking
- **FR-016**: System MUST integrate LlamaIndex for retrieval pipeline
- **FR-017**: System MUST extend LlamaIndex with custom orchestration
- **FR-018**: System MUST provide POST /query endpoint
- **FR-019**: System MUST accept query in POST /query
- **FR-020**: System MUST run intent detection on query
- **FR-021**: System MUST route retrieval based on intent
- **FR-022**: System MUST return answer, sources, and reasoning type
- **FR-023**: System MUST provide chat interface in Streamlit
- **FR-024**: System MUST display response in UI
- **FR-025**: System MUST display sources in UI
- **FR-026**: System MUST display reasoning type (vector/graph/hybrid) in UI
- **FR-027**: System MUST integrate Azure OpenAI as the LLM for answer generation
- **FR-028**: System MUST set up Azure OpenAI client with environment-based configuration
- **FR-029**: System MUST create prompts that fuse retrieved context (vector/graph/hybrid) with user query
- **FR-030**: System MUST send fused context to Azure OpenAI for answer generation
- **FR-031**: System MUST parse and format LLM response as the final answer
- **FR-032**: System MUST handle LLM errors gracefully (e.g., fallback to raw context summary)
- **FR-033**: System MUST provide POST /upload endpoint for document ingestion
- **FR-034**: System MUST accept file uploads (PDF, Word, PowerPoint, Excel, text) via the API
- **FR-035**: System MUST validate file format and reject unsupported formats with appropriate error messages
- **FR-036**: System MUST return ingestion statistics (filename, format, chunk count, entity count, relationship count) after successful upload
- **FR-037**: System MUST provide file uploader UI component in Streamlit sidebar
- **FR-038**: System MUST display ingestion progress and results in the UI
- **FR-039**: System MUST clean up temporary files after ingestion completes
- **FR-040**: System MUST provide Docker Compose configuration for full stack deployment
- **FR-041**: System MUST include Dockerfiles for API and UI services
- **FR-042**: System MUST support environment-based configuration for containerized deployment

### Key Entities *(include if feature involves data)*

- **Document**: Represents ingested files (PDF, text), with attributes like filename, content, type
- **Chunk**: Portions of document content, linked to document
- **Embedding**: Vector representation of chunks, stored in OpenSearch
- **Entity**: Extracted named entities from content
- **Relationship**: Connections between entities, forming graph structure in Neo4j
- **Query**: User input, classified by intent
- **Result**: Retrieved information with ranking, sources, and reasoning
- **LLM Response**: Generated answer from Azure OpenAI, including text, confidence, and metadata

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System can ingest and process 100 documents per hour
- **SC-002**: Intent detection accuracy reaches 90% on test queries
- **SC-003**: Retrieval returns relevant results in under 2 seconds for 95% of queries
- **SC-004**: API responds to queries with complete data (answer, sources, reasoning) in under 3 seconds
- **SC-005**: UI loads and displays results within 1 second after query submission
- **SC-006**: Generated answers achieve 85% relevance score on test queries (measured by semantic similarity to ground truth)

## Assumptions

- Documents are in supported formats (PDF, Word, powerpoint,text)
- OpenSearch and Neo4j are available and configured
- LlamaIndex is installed and accessible
- Users have basic understanding of query types
- System runs in containerized environment for POC using Docker Compose
- Docker Compose orchestrates OpenSearch, Neo4j, API, and UI services
- Azure OpenAI service is accessible and configured with valid credentials
- LLM responses are in English and fit within token limits for cost optimization
- **Python 3.12+** is the minimum supported runtime; all type annotations use built-in generics
- **Security**: All credentials must be loaded from environment variables; never commit `.env` files
  - POC Docker defaults (e.g., Neo4j `neo4j/password`) are acceptable for local demos only
