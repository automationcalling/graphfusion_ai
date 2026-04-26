from __future__ import annotations

from openai import AzureOpenAI
from src.config import settings


_client: AzureOpenAI | None = None


def _get_client() -> AzureOpenAI:
    global _client
    if _client is None:
        if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_ENDPOINT:
            raise ValueError(
                "AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT must be set in environment"
            )
        _client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )
    return _client


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings using Azure OpenAI. Reuses a single client instance."""
    client = _get_client()
    response = client.embeddings.create(
        model=settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME,
        input=texts,
    )
    return [item.embedding for item in response.data]
