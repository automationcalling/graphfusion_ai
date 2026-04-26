"""Azure OpenAI LLM client for answer generation from retrieved context."""

from __future__ import annotations

import os
import logging
from openai import AzureOpenAI, APIError, APITimeoutError


logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    """Client for Azure OpenAI API with error handling and configuration management."""

    def __init__(
        self,
        api_key: str | None = None,
        api_version: str | None = None,
        api_endpoint: str | None = None,
        deployment_name: str | None = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ):
        """
        Initialize Azure OpenAI client.

        Args:
            api_key: Azure OpenAI API key (defaults to AZURE_OPENAI_API_KEY env var)
            api_version: API version (defaults to AZURE_OPENAI_API_VERSION env var)
            api_endpoint: API endpoint (defaults to AZURE_OPENAI_ENDPOINT env var)
            deployment_name: Model deployment name (defaults to AZURE_OPENAI_DEPLOYMENT_NAME env var)
            max_tokens: Maximum tokens in response (default: 1024)
            temperature: Temperature for sampling (default: 0.7)
        """
        from src.config import settings
        self.api_key = api_key or settings.AZURE_OPENAI_API_KEY
        self.api_version = api_version or settings.AZURE_OPENAI_API_VERSION
        self.api_endpoint = api_endpoint or settings.AZURE_OPENAI_ENDPOINT
        self.deployment_name = deployment_name or settings.AZURE_OPENAI_DEPLOYMENT_NAME
        self.max_tokens = max_tokens
        self.temperature = temperature

        if not self.api_key or not self.api_endpoint:
            raise ValueError(
                "Azure OpenAI API key and endpoint must be provided or set via environment variables"
            )

        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.api_endpoint,
        )

        logger.info(f"Azure OpenAI client initialized with deployment: {self.deployment_name}")

    def generate_answer(
        self,
        query: str,
        context: str,
        system_prompt: str | None = None,
        timeout: int = 30,
    ) -> dict:
        """
        Generate an answer from retrieved context using Azure OpenAI.

        Args:
            query: User query
            context: Fused context from retrieval (vector + graph)
            system_prompt: System prompt (defaults to standard RAG prompt)
            timeout: Request timeout in seconds

        Returns:
            Dictionary with keys:
                - answer: Generated answer text
                - tokens_used: Total tokens used
                - model: Model used
                - finish_reason: Reason for completion ("stop", "length", etc.)

        Raises:
            APIError: If API request fails
            ValueError: If response is invalid
        """
        try:
            if system_prompt is None:
                system_prompt = self._get_default_system_prompt()

            messages = [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nContext:\n{context}\n\nProvide a concise, accurate answer based on the context above.",
                },
            ]

            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_completion_tokens=self.max_tokens,
                temperature=self.temperature,
                timeout=timeout,
            )

            answer = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0

            logger.info(f"Generated answer using {tokens_used} tokens, finish_reason: {response.choices[0].finish_reason}")

            return {
                "answer": answer,
                "tokens_used": tokens_used,
                "model": self.deployment_name,
                "finish_reason": response.choices[0].finish_reason,
            }

        except APITimeoutError as e:
            logger.error(f"Azure OpenAI API timeout: {e}")
            raise
        except APIError as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating answer: {e}")
            raise

    def generate_answer_with_fallback(
        self,
        query: str,
        context: str,
        system_prompt: str | None = None,
    ) -> dict:
        """
        Generate an answer with fallback to raw context summary if LLM fails.

        Args:
            query: User query
            context: Fused context from retrieval
            system_prompt: System prompt

        Returns:
            Dictionary with answer and metadata (same format as generate_answer)
        """
        try:
            return self.generate_answer(query, context, system_prompt)
        except Exception as e:
            logger.warning(f"LLM generation failed, falling back to context summary: {e}")
            # Fallback: return first 500 chars of context as answer
            fallback_answer = context[:500] + "..." if len(context) > 500 else context
            return {
                "answer": fallback_answer,
                "tokens_used": 0,
                "model": "fallback",
                "finish_reason": "fallback",
                "error": str(e),
            }

    @staticmethod
    def _get_default_system_prompt() -> str:
        """Get default system prompt for RAG-style answer generation."""
        return (
            "You are a helpful AI assistant. Your task is to answer user queries based on the provided context. "
            "Always cite sources from the context. If the context doesn't contain relevant information, "
            "clearly state that the answer cannot be found in the provided context. Be concise and accurate."
        )

    def validate_connection(self) -> bool:
        """Validate that Azure OpenAI connection is working."""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_completion_tokens=10,
            )
            logger.info("Azure OpenAI connection validated successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to validate Azure OpenAI connection: {e}")
            return False
