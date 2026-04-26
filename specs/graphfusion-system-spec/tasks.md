# Tasks: GraphFusion System Features

**Input**: Specification in `specs/graphfusion-system-spec/spec.md`
**Prerequisites**: `specs/graphfusion-system-spec/spec.md` completed

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure, configuration, and dependencies.

- [x] T001 Create `requirements.txt` with LlamaIndex, FastAPI, Streamlit, OpenSearch, Neo4j, and dependency libraries
- [x] T002 Create `src/config.py` for environment-driven OpenSearch, Neo4j, and LLM settings
- [x] T003 [P] Create package structure with `src/ingestion/`, `src/retrieval/`, `src/intent/`, `src/api/`, `src/ui/`, `src/pipeline/`, `src/llm/`, `src/graph/`, `src/search/`, and `src/utils/`
- [x] T004 [P] Create base `src/__init__.py` and package entry points
- [x] T005 Create `tests/` structure with `tests/unit/`, `tests/integration/`, and `tests/contract/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement shared connectors, models, and pipeline scaffolding before user stories.

- [x] T006 Implement OpenSearch client wrapper in `src/search/opensearch_client.py`
- [x] T007 Implement Neo4j client wrapper in `src/graph/neo4j_client.py`
- [x] T008 Data models handled inline within ingestion and retrieval modules (no separate models package)
- [x] T009 Implement LlamaIndex pipeline skeleton in `src/pipeline/llamaindex_pipeline.py`
- [x] T010 Implement shared logging and error handling in `src/utils/logging.py`
- [x] T011 Create `.env.example` for local configuration of OpenSearch, Neo4j, and service settings
- [x] T012 Implement Azure OpenAI client wrapper in `src/llm/azure_openai_client.py`
- [x] T013 Create prompt templates for context fusion in `src/llm/prompts.py`

---

## Phase 3: User Story 1 - Data Ingestion Pipeline (Priority: P1)

**Goal**: Build local ingestion support for documents into OpenSearch and Neo4j.

**Independent Test**: Ingest a sample document and verify OpenSearch embeddings and Neo4j graph records exist.

- [x] T014 [US1] Implement document parsing in `src/ingestion/parser.py`
- [x] T015 [US1] Content chunking handled within LlamaIndex ingestion pipeline
- [x] T016 [US1] Implement embedding generation in `src/ingestion/embeddings.py`
- [x] T017 [US1] Image extraction implemented with OCR or VLM modes in `src/ingestion/parser.py` + `src/ingestion/vlm_extractor.py`
- [x] T018 [US1] OpenSearch vector ingestion handled by LlamaIndex OpenSearch vector store
- [x] T019 [US1] Neo4j graph ingestion handled by LlamaIndex Neo4j property graph store
- [x] T020 [US1] Implement end-to-end ingest pipeline in `src/ingestion/ingest_pipeline.py`
- [x] T021 [US1] Add integration test for ingestion pipeline in `tests/integration/test_ingestion_pipeline.py`

---

## Phase 4: User Story 2 - Intent Detection Engine (Priority: P2)

**Goal**: Classify queries into Semantic, Relationship, or Hybrid so retrieval routes correctly.

**Independent Test**: Send sample queries and verify correct intent labels.

- [x] T022 [US2] Implement rule-based intent classification in `src/intent/intent_detector.py`
- [x] T023 [US2] Implement intent routing in `src/intent/intent_router.py`
- [x] T024 [US2] Add unit tests for intent detection in `tests/unit/test_intent_detector.py`

---

## Phase 5: User Story 3 - Retrieval Engine (Priority: P3)

**Goal**: Implement vector, graph, and hybrid retrieval with ranking and deduplication.

**Independent Test**: Query the system and verify retrieval from the correct store, and hybrid queries fuse results.

- [x] T025 [US3] Implement vector retrieval in `src/retrieval/vector_retriever.py`
- [x] T026 [US3] Implement graph retrieval in `src/retrieval/graph_retriever.py`
- [x] T027 [US3] Implement hybrid fusion retriever in `src/retrieval/hybrid_retriever.py`
- [x] T028 [US3] Implement ranking and deduplication in `src/retrieval/ranking.py`
- [x] T029 [US3] Add integration tests for retrieval and hybrid fusion in `tests/integration/test_retrieval_pipeline.py`

---

## Phase 6: User Story 4 - LlamaIndex Integration (Priority: P4)

**Goal**: Wire ingestion and retrieval through LlamaIndex while preserving custom orchestration.

**Independent Test**: Verify LlamaIndex pipeline executes ingestion and retrieval according to spec.

- [x] T030 [US4] Integrate ingestion steps with LlamaIndex in `src/pipeline/llamaindex_pipeline.py`
- [x] T031 [US4] Implement custom LlamaIndex retrieval orchestration in `src/pipeline/llamaindex_pipeline.py`
- [x] T032 [US4] Add LlamaIndex pipeline integration tests in `tests/integration/test_llamaindex_pipeline.py`

---

## Phase 7: User Story 5 - API Layer (Priority: P5)

**Goal**: Provide `POST /query` with answer, sources, and reasoning type.

**Independent Test**: Send API requests and verify full response structure.

- [x] T033 [US5] Implement FastAPI app in `src/api/main.py` (response formatting via Pydantic models in main.py)
- [x] T035 [US5] Add API integration tests in `tests/integration/test_api_query.py`
- [x] T036 [US5] Integrate LLM for answer generation in `src/api/main.py`
- [x] T037 [US5] Add LLM error handling in `src/api/main.py`
- [x] T038 [US5] Update API tests for LLM responses in `tests/integration/test_api_query.py`

---

## Phase 8: User Story 6 - UI (Priority: P6)

**Goal**: Build a Streamlit chat interface displaying responses, sources, and reasoning.

**Independent Test**: Use the UI and verify displayed response, sources, and reasoning type.

- [x] T039 [US6] Implement Streamlit chat UI in `src/ui/app.py`
- [x] T040 [US6] Display result, sources, and reasoning type in the UI
- [x] T041 [US6] Add a simple UI validation guide in `specs/001-graphfusion-system-spec/checklists/requirements.md`
- [x] T042 [US6] Integrate LLM in UI for answer display in `src/ui/app.py`
- [x] T043 [US6] Update UI validation for LLM responses in `specs/001-graphfusion-system-spec/checklists/requirements.md`

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, cleanup, and end-to-end validation.

- [x] T044 [P] Document local setup and ingestion flow in `README.md`
- [x] T045 [P] Add architecture notes in `docs/architecture.md`
- [x] T046 [P] Run end-to-end local validation for ingestion, retrieval, API, and UI

---

## Phase 10: Docker & Containerization

**Purpose**: Enable containerized deployment as specified in spec assumptions.

- [x] T047 [P] Create `Dockerfile` for API service
- [x] T048 [P] Create `Dockerfile.ui` for Streamlit UI
- [x] T049 [P] Create `docker-compose.yml` for full stack (OpenSearch, Neo4j, API, UI)
- [x] T050 [P] Add `.gitignore` for Python/Docker artifacts
- [x] T051 [P] Document Docker setup in `README.md`

---

---

## Phase 11: Python 3.12 Migration

**Purpose**: Upgrade the runtime target to Python 3.12 and modernize type annotations throughout the codebase.

- [x] T052 [P] Upgrade `Dockerfile` and `Dockerfile.ui` base image from `python:3.11-slim` to `python:3.12-slim`
- [x] T053 [P] Update `requirements.txt` package versions for Python 3.12 compatibility
- [x] T054 [P] Replace deprecated `typing.List`, `typing.Dict`, `typing.Optional` with built-in `list`, `dict`, and `X | None` syntax across all `src/` modules
- [x] T055 [P] Update constitution and spec to codify Python 3.12+ as the minimum supported runtime

---

## Phase 12: Pre-GitHub Publish Checklist (POC hygiene)

- [x] T056 Ensure `.env` is ignored and only `.env.example` is published
- [x] T057 Confirm Docker default passwords are clearly documented as non-production defaults
- [ ] T058 Align graph retrieval Cypher with actual Neo4j labels/properties created by LlamaIndex (optional, improves demo clarity)

---

## Dependencies & Execution Order

- Phase 1 tasks can start immediately.
- Phase 2 tasks must complete before user stories begin.
- User Story phases can run in parallel after Phase 2 is complete.
- Hybrid retrieval and API tasks depend on intent detection and ingestion foundation.
- LLM integration tasks (T036-T038, T042-T043) depend on LLM foundational tasks (T012-T013) and their respective user story tasks.
- Final polish tasks depend on user story completion.

## Parallel Opportunities

- Setup tasks `T003` and `T004` can run in parallel.
- Foundational tasks `T006`, `T007`, `T008`, `T009`, `T010`, `T012`, and `T013` can be developed in parallel where dependencies allow.
- User story implementation tasks for different stories can run in parallel after foundational setup.
- LLM integration tasks `T036`-`T038` and `T042`-`T043` can run in parallel after their dependencies.
- Documentation and validation tasks in Phase 9 can run in parallel with final story implementation.
