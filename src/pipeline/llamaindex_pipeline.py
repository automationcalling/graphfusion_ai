"""
LlamaIndex-based ingestion pipeline — one-stop solution for vector + graph storage.

Vector path:  SentenceSplitter → AzureOpenAIEmbedding → OpensearchVectorStore
Graph path:   SchemaLLMPathExtractor (GPT-4o) → Neo4jPropertyGraphStore

To switch the graph backend to Amazon Neptune, replace _build_graph_store() with:

    from llama_index.graph_stores.neptune import NeptuneAnalyticsGraphStore
    return NeptuneAnalyticsGraphStore(graph_identifier="<your-graph-id>")

No other code changes required — both stores implement the same LlamaIndex interface.
"""

from __future__ import annotations

from typing import Any

from src.config import settings
from src.ingestion.parser import parse_document
from src.utils.logging import get_logger

logger = get_logger(__name__)

_CHUNK_SIZE = 500
_CHUNK_OVERLAP = 50


def _build_llm():
    from llama_index.llms.azure_openai import AzureOpenAI

    return AzureOpenAI(
        model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        deployment_name=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )


def _build_embed_model():
    from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

    return AzureOpenAIEmbedding(
        model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
        deployment_name=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
        api_key=settings.AZURE_OPENAI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_API_VERSION,
    )


def _build_vector_store(index: str):
    from llama_index.vector_stores.opensearch import (
        OpensearchVectorClient,
        OpensearchVectorStore,
    )

    client = OpensearchVectorClient(
        endpoint=settings.OPENSEARCH_HOST,
        index=index,
        dim=settings.embedding_dimension,
        embedding_field="embedding",
        text_field="content",
        http_auth=(settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD),
        use_ssl=settings.OPENSEARCH_HOST.startswith("https"),
        verify_certs=False,
        ssl_show_warn=False,
    )
    return OpensearchVectorStore(client)


def _build_graph_store():
    """
    Neo4j graph store via LlamaIndex abstraction.

    refresh_schema=False prevents the store from calling apoc.meta.data on
    startup — APOC is required for schema refresh but not for data ingestion.
    Start Neo4j with NEO4J_PLUGINS='["apoc"]' to enable schema refresh.

    Neptune swap (future):
        from llama_index.graph_stores.neptune import NeptuneAnalyticsGraphStore
        return NeptuneAnalyticsGraphStore(graph_identifier="<graph-id>")
    """
    from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

    return Neo4jPropertyGraphStore(
        username=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
        url=settings.NEO4J_URI,
        refresh_schema=False,  # avoids apoc.meta.data call — safe without APOC plugin
        sanitize_query_output=False,
    )


class LlamaIndexIngestionPipeline:
    """
    One-stop LlamaIndex ingestion pipeline.

    Vector path:
        parse → SentenceSplitter → AzureOpenAIEmbedding → OpensearchVectorStore

    Graph path:
        parse → SchemaLLMPathExtractor (GPT-4o) → Neo4jPropertyGraphStore

    Both paths run from a single call to run(). No external client objects needed —
    all connections are configured from app settings.
    """

    def run(self, file_path: str, original_filename: str = "", index: str = "") -> dict[str, Any]:
        index = index or settings.OPENSEARCH_INDEX

        # 1. Parse document using existing multi-format parser
        parsed = parse_document(file_path)
        display_filename = original_filename or parsed["filename"]
        images: list[str] = parsed.get("images", [])
        logger.info(f"[LlamaIndex] Parsed '{display_filename}' ({parsed.get('format')}, {len(images)} images)")

        # 1b. Extract text from embedded images (OCR or VLM based on config)
        from src.ingestion.parser import extract_text_from_image

        image_text_parts: list[str] = []
        if images:
            for img_path in images:
                try:
                    extracted = extract_text_from_image(img_path)
                    if extracted:
                        image_text_parts.append(extracted)
                finally:
                    # Clean up temp image file
                    try:
                        import os as _os
                        if _os.path.exists(img_path):
                            _os.unlink(img_path)
                    except Exception:
                        pass

        combined_text = parsed["content"]
        if image_text_parts:
            extraction_mode = settings.IMAGE_EXTRACTION_MODE.upper()
            combined_text += f"\n\n--- Extracted from images ({extraction_mode}) ---\n\n" + "\n\n".join(image_text_parts)
            logger.info(f"[LlamaIndex] Appended {extraction_mode} text from {len(image_text_parts)} images to document")

        # 2. Wrap as LlamaIndex Document
        from llama_index.core import Document as LlamaDocument
        llama_docs = [
            LlamaDocument(
                text=combined_text,
                metadata={"filename": display_filename, "format": parsed.get("format", "unknown")},
            )
        ]

        # 3. Build shared LLM and embedding model
        llm = _build_llm()
        embed_model = _build_embed_model()

        # ── Vector path ──────────────────────────────────────────────────────
        # SentenceSplitter → AzureOpenAIEmbedding → OpensearchVectorStore
        from llama_index.core.ingestion import IngestionPipeline
        from llama_index.core.node_parser import SentenceSplitter

        vector_pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=_CHUNK_SIZE, chunk_overlap=_CHUNK_OVERLAP),
                embed_model,
            ],
            vector_store=_build_vector_store(index),
        )
        nodes = vector_pipeline.run(documents=llama_docs)
        chunk_count = len(nodes)
        logger.info(f"[LlamaIndex] Stored {chunk_count} chunks in OpenSearch index '{index}'")

        # ── Graph path ───────────────────────────────────────────────────────
        # SimpleLLMPathExtractor (GPT) → Neo4jPropertyGraphStore
        # SimpleLLMPathExtractor auto-extracts (subject, relation, object) triplets
        # without requiring a predefined entity/relation schema.
        from llama_index.core import PropertyGraphIndex
        from llama_index.core.indices.property_graph import SimpleLLMPathExtractor

        graph_store = _build_graph_store()

        # Test LLM is reachable before attempting extraction
        try:
            test = llm.complete("Reply with the single word OK")
            logger.info(f"[LlamaIndex] LLM reachability check: {str(test).strip()[:50]}")
        except Exception as e:
            logger.error(f"[LlamaIndex] LLM unreachable — graph extraction will be skipped: {e}")
            return {
                "status": "success",
                "filename": display_filename,
                "format": parsed.get("format", "unknown"),
                "chunk_count": chunk_count,
                "entity_count": 0,
                "relationship_count": 0,
            }

        extractor = SimpleLLMPathExtractor(llm=llm, max_paths_per_chunk=10)
        logger.info(f"[LlamaIndex] Starting graph extraction on {len(nodes)} chunks...")
        try:
            pg_index = PropertyGraphIndex.from_documents(
                llama_docs,
                llm=llm,
                embed_model=embed_model,
                kg_extractors=[extractor],
                property_graph_store=graph_store,
                show_progress=True,
            )
            logger.info(f"[LlamaIndex] PropertyGraphIndex built: {pg_index}")
        except Exception as e:
            logger.error(f"[LlamaIndex] Graph extraction failed: {e}", exc_info=True)
            raise

        # Raw Neo4j state after extraction
        try:
            raw = graph_store.structured_query(
                "MATCH (n) RETURN labels(n) AS labels, count(n) AS cnt"
            )
            logger.info(f"[LlamaIndex] Neo4j node state after extraction: {raw}")
        except Exception as e:
            logger.warning(f"[LlamaIndex] Could not query Neo4j state: {e}")

        # Count entities and relationships stored for this document
        entity_count, relationship_count = _count_graph_data(graph_store)
        logger.info(
            f"[LlamaIndex] Stored {entity_count} entities, "
            f"{relationship_count} relationships in Neo4j"
        )

        return {
            "status": "success",
            "filename": display_filename,
            "format": parsed.get("format", "unknown"),
            "chunk_count": chunk_count,
            "entity_count": entity_count,
            "relationship_count": relationship_count,
        }


def _count_graph_data(graph_store) -> tuple[int, int]:
    """Query Neo4j for entity and relationship counts after ingestion.
    LlamaIndex PropertyGraphStore uses __Node__ (not __Entity__) as the base label.
    """
    try:
        entity_result = graph_store.structured_query(
            "MATCH (n:__Node__) WHERE n.name IS NOT NULL RETURN count(n) AS count"
        )
        rel_result = graph_store.structured_query(
            "MATCH ()-[r]->() WHERE type(r) <> 'MENTIONS' RETURN count(r) AS count"
        )
        entity_count = entity_result[0]["count"] if entity_result else 0
        rel_count = rel_result[0]["count"] if rel_result else 0
        return entity_count, rel_count
    except Exception as e:
        logger.warning(f"Could not query graph counts: {e}")
        return 0, 0
