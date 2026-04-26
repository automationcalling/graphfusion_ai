from __future__ import annotations

from src.pipeline.llamaindex_pipeline import LlamaIndexIngestionPipeline


def run_ingest_llamaindex(
    file_path: str,
    index: str,
    original_filename: str = "",
) -> dict:
    """
    LlamaIndex ingestion entry point.

    Connections to OpenSearch and Neo4j are configured from app settings inside
    the pipeline — no client objects needed from the caller.
    """
    pipeline = LlamaIndexIngestionPipeline()
    return pipeline.run(file_path=file_path, original_filename=original_filename, index=index)
