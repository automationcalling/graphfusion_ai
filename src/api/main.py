from __future__ import annotations

import asyncio
import os
import tempfile
from typing import Any

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config import settings
from src.graph.neo4j_client import Neo4jClient
from src.ingestion.embeddings import generate_embeddings
from src.ingestion.ingest_pipeline import run_ingest_llamaindex
from src.intent.intent_router import IntentRouter
from src.llm.azure_openai_client import AzureOpenAIClient
from src.retrieval.graph_retriever import GraphRetriever
from src.retrieval.ranking import deduplicate_and_rank
from src.retrieval.vector_retriever import VectorRetriever
from src.search.opensearch_client import OpenSearchClient
from src.utils.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(title="GraphFusion_AI API")

# CORS — restrict origins in production via ALLOWED_ORIGINS env var
_allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# Max upload size enforced at request level
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx", ".doc", ".pptx", ".ppt", ".xlsx", ".xls"}


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict[str, Any]]
    reasoning_type: str


class UploadResponse(BaseModel):
    status: str
    filename: str
    format: str
    chunk_count: int
    entity_count: int
    relationship_count: int


router = IntentRouter()

try:
    llm_client = AzureOpenAIClient(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
    )
    logger.info("Azure OpenAI LLM client initialized")
except ValueError as e:
    logger.warning(f"Azure OpenAI not configured: {e}")
    llm_client = None


def _get_os_client() -> OpenSearchClient:
    return OpenSearchClient(
        host=settings.OPENSEARCH_HOST,
        user=settings.OPENSEARCH_USER,
        password=settings.OPENSEARCH_PASSWORD,
    )


def _get_neo4j_client() -> Neo4jClient:
    return Neo4jClient(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
    )


def fuse_context(sources: list[dict[str, Any]]) -> str:
    if not sources:
        return "No relevant context found."
    parts = []
    for i, s in enumerate(sources, 1):
        parts.append(f"[{s.get('id', i)}] (score: {s.get('score', 0):.2f}):\n{s.get('content', '')}")
    return "\n\n---\n\n".join(parts)


def _retrieve(query: str, intent: str, use_vector: bool, use_graph: bool) -> list[dict[str, Any]]:
    """Run the appropriate retriever(s) and return a merged, ranked source list."""
    os_client = _get_os_client()
    neo4j_client = _get_neo4j_client()

    try:
        vector_retriever = VectorRetriever(os_client)
        graph_retriever = GraphRetriever(neo4j_client)

        results: list[dict[str, Any]] = []

        if use_vector:
            query_embeddings = generate_embeddings([query])
            vector_results = vector_retriever.retrieve(
                query_embedding=query_embeddings[0],
                index=settings.OPENSEARCH_INDEX,
            )
            results.extend(vector_results)

        if use_graph:
            # Use the first significant word as entity name for graph lookup
            entity_name = next((w for w in query.split() if len(w) > 3), query.split()[0])
            graph_results = graph_retriever.retrieve(entity_name=entity_name)
            results.extend(graph_results)

        return deduplicate_and_rank(results)
    finally:
        os_client.close()
        neo4j_client.close()


@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest) -> QueryResponse:
    """Query the GraphFusion system with intent-routed retrieval and LLM answer generation."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    logger.info(f"Received query: {request.query}")

    routing = router.route(request.query)
    intent = routing["intent"]

    try:
        sources = _retrieve(
            query=request.query,
            intent=intent,
            use_vector=routing["use_vector"],
            use_graph=routing["use_graph"],
        )
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        sources = []

    fused = fuse_context(sources)

    if llm_client:
        llm_result = llm_client.generate_answer_with_fallback(query=request.query, context=fused)
        answer = llm_result["answer"]
    else:
        answer = fused[:500] + ("..." if len(fused) > 500 else "")

    return QueryResponse(
        query=request.query,
        answer=answer,
        sources=sources,
        reasoning_type=intent,
    )


@app.post("/upload", response_model=UploadResponse)
async def upload_document(request: Request, file: UploadFile = File(...)) -> UploadResponse:
    """Upload and ingest a document into OpenSearch and Neo4j."""
    # Enforce file size limit before reading into memory
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
        )

    original_filename = file.filename or "unknown"
    file_ext = os.path.splitext(original_filename.lower())[1]

    if file_ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {file_ext}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    logger.info(f"Received upload: {original_filename}")

    temp_file_path: str | None = None

    try:
        content = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB.",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            temp_file_path = tmp.name
            tmp.write(content)

        # Run blocking LlamaIndex ingestion in a thread so asyncio.run()
        # inside LlamaIndex doesn't conflict with FastAPI's running event loop.
        result = await asyncio.to_thread(
            run_ingest_llamaindex,
            file_path=temp_file_path,
            index=settings.OPENSEARCH_INDEX,
            original_filename=original_filename,
        )

        return UploadResponse(**result)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed for {original_filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@app.get("/health")
def health_check() -> dict[str, str]:
    llm_status = "healthy" if llm_client and llm_client.validate_connection() else "unavailable"
    return {"status": "healthy", "llm": llm_status}
