"""
Factory for creating LLM instances with different providers and configurations.
"""
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel

from app.llm.providers import get_provider
from app.llm.model_catalog import get_default_model, MODEL_CATALOG
from app.utils.exceptions import LLMProviderError


def create_llm(
    provider: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> BaseChatModel:
    """
    Factory function to create an LLM client instance.
    
    Args:
        provider: Provider name (openai, groq, huggingface, together, deepinfra)
        model: Model identifier (uses default if None)
        temperature: Temperature setting (0.0-1.0)
        **kwargs: Additional provider-specific parameters
    
    Returns:
        Configured LLM client instance
    
    Raises:
        LLMProviderError: If client creation fails
        ValueError: If provider or model is invalid
    """
    # Get default model if not specified
    if model is None:
        model = get_default_model(provider)
        if not model:
            raise ValueError(f"No default model configured for provider: {provider}")
    
    # Validate model is in catalog (skip for openai - dynamic models)
    if provider != "openai":
        if provider in MODEL_CATALOG and model not in MODEL_CATALOG[provider]:
            available = ", ".join(MODEL_CATALOG[provider])
            raise ValueError(
                f"Model '{model}' not found for provider '{provider}'. "
                f"Available: {available}"
            )
    
    # Get provider instance and create client
    provider_instance = get_provider(provider)
    return provider_instance.create_client(model, temperature, **kwargs)


def create_performer_llm(
    provider: str,
    model: Optional[str] = None
) -> BaseChatModel:
    """
    Create LLM configured for Performer agent (creative, higher temperature).
    
    Args:
        provider: Provider name
        model: Model identifier (uses default if None)
    
    Returns:
        LLM configured with temperature=0.9 for creativity
    """
    return create_llm(provider, model, temperature=0.9)


def create_critic_llm(
    provider: str,
    model: Optional[str] = None
) -> BaseChatModel:
    """
    Create LLM configured for Critic agent (analytical, lower temperature).
    
    Args:
        provider: Provider name
        model: Model identifier (uses default if None)
    
    Returns:
        LLM configured with temperature=0.3 for consistency
    """
    return create_llm(provider, model, temperature=0.3)
