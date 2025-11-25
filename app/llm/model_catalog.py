"""
Model catalog for all supported LLM providers.
Contains available models, defaults, and deprecated models.
"""
from typing import Dict, List


# Model catalog for available models per provider
# Updated: 2025 - Using currently supported models only
MODEL_CATALOG: Dict[str, List[str]] = {
    "groq": [
        "llama-3.3-70b-versatile",      # ✅ VERIFIED - Groq's flagship model
        "llama-3.1-8b-instant",         # ✅ VERIFIED - Fast, lightweight
    ],
    "openai": [
        # Static fallback - will be replaced by dynamic fetch in UI
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
    "huggingface": [
        "mistralai/Mistral-7B-Instruct-v0.2",      # ✅ VERIFIED - Working!
        "Qwen/Qwen2.5-7B-Instruct",                # ✅ VERIFIED - Working!
        # Gated models (require approval at huggingface.co):
        # "meta-llama/Llama-3.1-8B-Instruct",      # ⚠️  Gated - Request access first
        # "google/gemma-2b-it",                    # ⚠️  Gated - Request access first
    ],
    "together": [
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "mistralai/Mistral-7B-Instruct-v0.2",
        "Qwen/Qwen2.5-7B-Instruct-Turbo",
        "meta-llama/Llama-3.2-3B-Instruct-Turbo",
    ],
    "deepinfra": [
        "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "mistralai/Mistral-7B-Instruct-v0.2",
        "Qwen/Qwen2.5-7B-Instruct",
    ],
}

# Default models per provider
DEFAULT_MODELS: Dict[str, str] = {
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o-mini",
    "huggingface": "mistralai/Mistral-7B-Instruct-v0.2",
    "together": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    "deepinfra": "meta-llama/Meta-Llama-3.1-8B-Instruct",
}

# Deprecated/decommissioned models - DO NOT USE
DEPRECATED_MODELS: Dict[str, List[str]] = {
    "groq": [
        "llama-3.1-70b-versatile",  # Deprecated: Use llama-3.3-70b-versatile
        "llama-3.3-70b-specdec",     # DECOMMISSIONED (2025): Model removed by Groq
        "mixtral-8x7b-32768",        # Deprecated: Model removed
        "gemma2-9b-it",              # Deprecated: Model removed
    ],
    "openai": [
        # OpenAI maintains backward compatibility longer
    ],
}


def get_available_models(provider: str) -> List[str]:
    """
    Get list of available models for a provider.
    
    Args:
        provider: The LLM provider name
    
    Returns:
        List of available model IDs
    """
    return MODEL_CATALOG.get(provider, [])


def get_default_model(provider: str) -> str:
    """
    Get the default model for a provider.
    
    Args:
        provider: The LLM provider name
    
    Returns:
        Default model ID for the provider
    """
    return DEFAULT_MODELS.get(provider, "")


def is_deprecated(provider: str, model: str) -> bool:
    """
    Check if a model is deprecated.
    
    Args:
        provider: The LLM provider name
        model: The model ID
    
    Returns:
        True if the model is deprecated
    """
    deprecated_list = DEPRECATED_MODELS.get(provider, [])
    return model in deprecated_list


def get_all_providers() -> List[str]:
    """
    Get list of all supported providers.
    
    Returns:
        List of provider names
    """
    return list(MODEL_CATALOG.keys())
