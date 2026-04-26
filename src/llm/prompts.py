"""Prompt templates for context fusion and answer generation."""

from __future__ import annotations

from enum import Enum


class PromptType(Enum):
    """Types of prompts for different retrieval intents."""

    SEMANTIC = "semantic"
    RELATIONSHIP = "relationship"
    HYBRID = "hybrid"


class PromptTemplates:
    """Collection of prompt templates for RAG-style answer generation."""

    # System prompts for different retrieval types
    SEMANTIC_SYSTEM_PROMPT = (
        "You are a helpful AI assistant specialized in semantic understanding and content analysis. "
        "Your task is to answer user queries based on the provided semantic context (vector-retrieved documents). "
        "Focus on conceptual understanding, relevance, and accuracy. Always cite specific passages from the context. "
        "If the context doesn't contain relevant information, clearly state that."
    )

    RELATIONSHIP_SYSTEM_PROMPT = (
        "You are an AI assistant specialized in relationship and connection analysis. "
        "Your task is to answer user queries based on the provided graph-based context (entity relationships, connections). "
        "Focus on explaining connections, relationships, and structural information. "
        "Always cite the entities and relationships from the context. "
        "If no relevant relationships are found, clearly state that."
    )

    HYBRID_SYSTEM_PROMPT = (
        "You are a comprehensive AI assistant that combines semantic understanding with relationship analysis. "
        "Your task is to answer user queries by synthesizing both semantic context (vector-retrieved documents) "
        "and relationship context (entity connections and graph structure). "
        "Provide a holistic answer that leverages both types of information. "
        "Always cite sources from the context. Be balanced and accurate."
    )

    # User message templates
    SEMANTIC_USER_TEMPLATE = (
        "Query: {query}\n\n"
        "Semantic Context (from vector retrieval):\n"
        "{context}\n\n"
        "Based on the semantic context above, provide a concise and accurate answer to the query. "
        "Focus on content relevance and conceptual understanding."
    )

    RELATIONSHIP_USER_TEMPLATE = (
        "Query: {query}\n\n"
        "Relationship Context (from graph traversal):\n"
        "{context}\n\n"
        "Based on the relationship and entity connections above, provide an answer explaining the relevant connections. "
        "Focus on entity relationships and structural information."
    )

    HYBRID_USER_TEMPLATE = (
        "Query: {query}\n\n"
        "Semantic Context (from vector retrieval):\n"
        "{semantic_context}\n\n"
        "Relationship Context (from graph traversal):\n"
        "{relationship_context}\n\n"
        "Synthesize both contexts above to provide a comprehensive answer. "
        "Explain both the semantic relevance and relationship context."
    )

    @classmethod
    def get_system_prompt(cls, prompt_type: PromptType) -> str:
        """Get system prompt for a given retrieval type."""
        if prompt_type == PromptType.SEMANTIC:
            return cls.SEMANTIC_SYSTEM_PROMPT
        elif prompt_type == PromptType.RELATIONSHIP:
            return cls.RELATIONSHIP_SYSTEM_PROMPT
        else:  # HYBRID
            return cls.HYBRID_SYSTEM_PROMPT

    @classmethod
    def get_user_prompt(cls, prompt_type: PromptType, **kwargs) -> str:
        """
        Get user prompt for a given retrieval type.

        For SEMANTIC and RELATIONSHIP:
            kwargs: query, context

        For HYBRID:
            kwargs: query, semantic_context, relationship_context
        """
        if prompt_type == PromptType.SEMANTIC:
            return cls.SEMANTIC_USER_TEMPLATE.format(
                query=kwargs.get("query", ""),
                context=kwargs.get("context", ""),
            )
        elif prompt_type == PromptType.RELATIONSHIP:
            return cls.RELATIONSHIP_USER_TEMPLATE.format(
                query=kwargs.get("query", ""),
                context=kwargs.get("context", ""),
            )
        else:  # HYBRID
            return cls.HYBRID_USER_TEMPLATE.format(
                query=kwargs.get("query", ""),
                semantic_context=kwargs.get("semantic_context", ""),
                relationship_context=kwargs.get("relationship_context", ""),
            )

    @classmethod
    def build_prompt_context(
        cls,
        query: str,
        reasoning_type: str,
        context: str | None = None,
        semantic_context: str | None = None,
        relationship_context: str | None = None,
    ) -> dict[str, str]:
        """
        Build complete prompt context for LLM generation.

        Args:
            query: User query
            reasoning_type: "semantic", "relationship", or "hybrid"
            context: For semantic/relationship prompts
            semantic_context: For hybrid prompts
            relationship_context: For hybrid prompts

        Returns:
            Dictionary with system_prompt and user_prompt
        """
        prompt_type_map = {
            "semantic": PromptType.SEMANTIC,
            "relationship": PromptType.RELATIONSHIP,
            "hybrid": PromptType.HYBRID,
        }

        prompt_type = prompt_type_map.get(reasoning_type.lower(), PromptType.SEMANTIC)

        if prompt_type == PromptType.HYBRID:
            user_prompt = cls.get_user_prompt(
                prompt_type,
                query=query,
                semantic_context=semantic_context or "",
                relationship_context=relationship_context or "",
            )
        else:
            user_prompt = cls.get_user_prompt(
                prompt_type,
                query=query,
                context=context or "",
            )

        return {
            "system_prompt": cls.get_system_prompt(prompt_type),
            "user_prompt": user_prompt,
            "prompt_type": reasoning_type,
        }
