import os
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


# Embedding dimensions by model name — used for OpenSearch index mapping
EMBEDDING_DIMENSIONS: dict = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


def _base_endpoint(url: str) -> str:
    """
    Strip path and query string from an Azure endpoint URL.
    The Azure OpenAI SDK expects just the base URL
    e.g. https://resource.cognitiveservices.azure.com/
    """
    if not url:
        return url
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}/"


class Settings:
    # OpenSearch
    OPENSEARCH_HOST: str = os.getenv("OPENSEARCH_HOST", "http://localhost:9200")
    OPENSEARCH_USER: str = os.getenv("OPENSEARCH_USER", "admin")
    OPENSEARCH_PASSWORD: str = os.getenv("OPENSEARCH_PASSWORD", "")
    OPENSEARCH_INDEX: str = os.getenv("OPENSEARCH_INDEX", "graphfusion_chunks")

    # Neo4j
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")

    # Azure OpenAI — shared across all modules
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = _base_endpoint(os.getenv("AZURE_OPENAI_ENDPOINT", ""))
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME", "text-embedding-3-large")

    # Image extraction: "ocr" (pytesseract) or "vlm" (Azure OpenAI vision)
    IMAGE_EXTRACTION_MODE: str = os.getenv("IMAGE_EXTRACTION_MODE", "ocr")
    AZURE_OPENAI_VISION_MODEL: str = os.getenv("AZURE_OPENAI_VISION_MODEL", "gpt-4o")

    # App
    APP_ENV: str = os.getenv("APP_ENV", "local")
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    @property
    def embedding_dimension(self) -> int:
        return EMBEDDING_DIMENSIONS.get(self.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME, 1536)


settings = Settings()
