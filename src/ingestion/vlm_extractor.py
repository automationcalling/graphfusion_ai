"""
VLM-based image entity extraction using Azure OpenAI vision models.

Extracts entities and relationships from diagrams, charts, flowcharts, and technical images.
"""

from __future__ import annotations

import base64
import json
from typing import Any

from src.config import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Vision model prompt for extracting structured knowledge from images
VLM_EXTRACTION_PROMPT = """
Analyze this image and extract entities and relationships as a knowledge graph.

Focus on:
- Named entities (people, organizations, concepts, components)
- Relationships between entities (arrows, connections, hierarchies, dependencies)
- Labels, titles, and annotations in the image

Return JSON in this exact format:
{
    "entities": [
        {"name": "EntityName", "type": "EntityType", "description": "Brief description"}
    ],
    "relationships": [
        {"from": "EntityA", "to": "EntityB", "type": "RELATIONSHIP_TYPE", "description": "Brief description"}
    ]
}

If the image contains no extractable entities (e.g., decorative images, photos without diagrams), return:
{"entities": [], "relationships": [], "note": "No structured entities found"}

Be precise with entity names as they appear in the image.
"""


def encode_image_to_base64(image_path: str) -> str:
    """Encode an image file to base64 string for API transmission."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def extract_entities_from_image(image_path: str) -> dict[str, Any]:
    """
    Extract entities and relationships from an image using Azure OpenAI vision model.

    Args:
        image_path: Path to the image file (PNG, JPEG, etc.)

    Returns:
        Dictionary with 'entities' and 'relationships' lists
    """
    from openai import AzureOpenAI

    client = AzureOpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        api_version=settings.AZURE_OPENAI_API_VERSION,
        azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
    )

    image_base64 = encode_image_to_base64(image_path)

    try:
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_VISION_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a knowledge graph extraction specialist. Extract structured entities and relationships from diagrams, charts, and technical images.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VLM_EXTRACTION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=2000,
        )

        result_text = response.choices[0].message.content.strip()

        # Parse JSON from response (handle potential markdown code blocks)
        result_text = result_text.replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(result_text)
            logger.debug(
                f"VLM extracted {len(result.get('entities', []))} entities, "
                f"{len(result.get('relationships', []))} relationships from {image_path}"
            )
            return result
        except json.JSONDecodeError as e:
            logger.warning(f"VLM response was not valid JSON: {e}. Raw: {result_text[:200]}")
            return {"entities": [], "relationships": [], "parse_error": str(e)}

    except Exception as e:
        logger.error(f"VLM extraction failed for {image_path}: {e}")
        return {"entities": [], "relationships": [], "error": str(e)}


def extract_entities_from_images_batch(image_paths: list[str]) -> dict[str, Any]:
    """
    Extract entities from multiple images.

    Args:
        image_paths: List of image file paths

    Returns:
        Aggregated dictionary with all entities and relationships
    """
    all_entities = []
    all_relationships = []

    for img_path in image_paths:
        result = extract_entities_from_image(img_path)
        all_entities.extend(result.get("entities", []))
        all_relationships.extend(result.get("relationships", []))

    logger.info(
        f"VLM batch extraction: {len(all_entities)} entities, "
        f"{len(all_relationships)} relationships from {len(image_paths)} images"
    )

    return {"entities": all_entities, "relationships": all_relationships}
