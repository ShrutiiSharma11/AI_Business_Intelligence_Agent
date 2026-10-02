"""
LLM Model Configuration and Initialization.
Supports multiple LLM providers with flexible configuration.
"""

import os
import logging
from typing import Optional
from abc import ABC, abstractmethod

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def get_model(self, model_name: str = None, temperature: float = 0.7):
        """Return configured LLM model."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        logger.info("OpenAI provider initialized")

    def get_model(self, model_name: str = "gpt-4o", temperature: float = 0.7):
        """Get OpenAI model."""
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                api_key=self.api_key,
                max_tokens=4096
            )
        except ImportError:
            raise ImportError("langchain-openai not installed. Run: pip install langchain-openai")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        logger.info("Anthropic provider initialized")

    def get_model(self, model_name: str = "claude-3-sonnet-20240229", temperature: float = 0.7):
        """Get Anthropic model."""
        try:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=model_name,
                temperature=temperature,
                api_key=self.api_key,
                max_tokens=4096
            )
        except ImportError:
            raise ImportError("langchain-anthropic not installed. Run: pip install langchain-anthropic")


class LLMFactory:
    """Factory for creating LLM instances."""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }

    @staticmethod
    def get_provider(provider_name: str = "openai") -> LLMProvider:
        """Get LLM provider by name."""
        provider_name = provider_name.lower()

        if provider_name not in LLMFactory.PROVIDERS:
            logger.warning(f"Unknown provider: {provider_name}. Using OpenAI.")
            provider_name = "openai"

        try:
            provider_class = LLMFactory.PROVIDERS[provider_name]
            return provider_class()
        except ValueError as e:
            logger.error(f"Failed to initialize {provider_name} provider: {str(e)}")
            raise

    @staticmethod
    def create_llm(
            provider: str = "openai",
            model: str = None,
            temperature: float = 0.7
    ):
        """
        Create LLM instance.

        Args:
            provider: LLM provider name (openai, anthropic, etc.)
            model: Specific model name
            temperature: Model temperature for output diversity

        Returns:
            Configured LLM instance
        """
        provider_instance = LLMFactory.get_provider(provider)

        if model is None:
            model = "gpt-4o" if provider == "openai" else "claude-3-sonnet-20240229"

        return provider_instance.get_model(model_name=model, temperature=temperature)


def get_default_llm(temperature: float = 0.7):
    """Get default LLM with reasonable settings."""
    provider = os.getenv("LLM_PROVIDER", "openai")
    return LLMFactory.create_llm(provider=provider, temperature=temperature)


def get_fast_llm(temperature: float = 0.3):
    """Get fast LLM for simple tasks."""
    return get_default_llm(temperature=temperature)


def get_reasoning_llm(temperature: float = 0.5):
    """Get LLM optimized for reasoning."""
    return get_default_llm(temperature=temperature)


class EmbeddingsProvider:
    """Embeddings provider configuration."""

    @staticmethod
    def get_embeddings(provider: str = "openai"):
        """Get embeddings model."""
        if provider == "openai":
            try:
                from langchain_openai import OpenAIEmbeddings
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found")
                return OpenAIEmbeddings(api_key=api_key, model="text-embedding-3-small")
            except ImportError:
                raise ImportError("langchain-openai not installed")
        else:
            raise ValueError(f"Unsupported embeddings provider: {provider}")
