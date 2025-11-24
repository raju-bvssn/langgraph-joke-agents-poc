"""
Configuration settings for the multi-agent joke system.
Loads environment variables and provides centralized config.
"""
import os
from typing import Literal, Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


# Model catalog for available models per provider
# Updated: 2025 - Using currently supported models only
# ✅ Groq models tested and verified working (see test_llms.py)
# ⚠️ OpenAI models: Dynamically fetched from account (call fetch_openai_models() in llm.py)
# 🆓 New Free Providers: HuggingFace, Together AI, DeepInfra
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


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = ""
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    together_api_key: str = ""
    deepinfra_api_key: str = ""
    langchain_api_key: str = ""
    
    # LangSmith Configuration
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_project: str = "joke-agent-poc"
    langchain_tracing_v2: str = "true"
    
    # LLM Provider
    llm_provider: Literal["openai", "groq", "huggingface", "together", "deepinfra"] = "openai"
    
    # Model Configuration
    openai_model: str = "gpt-4o-mini"
    groq_model: str = "llama-3.3-70b-versatile"
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.2"
    together_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    deepinfra_model: str = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    temperature: float = 0.7
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def validate_keys(self) -> bool:
        """Validate that required API keys are present."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when using Groq provider")
        if self.llm_provider == "huggingface" and not self.huggingface_api_key:
            raise ValueError("HUGGINGFACE_API_KEY is required when using HuggingFace provider")
        if self.llm_provider == "together" and not self.together_api_key:
            raise ValueError("TOGETHER_API_KEY is required when using Together AI provider")
        if self.llm_provider == "deepinfra" and not self.deepinfra_api_key:
            raise ValueError("DEEPINFRA_API_KEY is required when using DeepInfra provider")
        return True


# Singleton instance
settings = Settings()

# Set environment variables for LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
if settings.langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key

