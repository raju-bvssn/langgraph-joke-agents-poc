"""
LLM provider implementations for different services.
Each provider class encapsulates the initialization logic for its respective service.
"""
import os
import streamlit as st
from typing import Optional
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

from app.utils.exceptions import LLMProviderError, ConfigurationError


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def create_client(self, model: str, temperature: float, **kwargs) -> BaseChatModel:
        """
        Create an LLM client instance.
        
        Args:
            model: Model identifier
            temperature: Temperature setting
            **kwargs: Additional provider-specific parameters
        
        Returns:
            Configured LLM client
        
        Raises:
            LLMProviderError: If client creation fails
        """
        pass
    
    @abstractmethod
    def get_api_key(self) -> str:
        """
        Get API key from secrets or environment.
        
        Returns:
            API key string
        
        Raises:
            ConfigurationError: If API key not found
        """
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""
    
    def get_api_key(self) -> str:
        """Get OpenAI API key from secrets or environment."""
        api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not api_key or api_key.startswith("sk-your"):
            raise ConfigurationError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in your .env file or Streamlit secrets."
            )
        return api_key
    
    def create_client(self, model: str, temperature: float, **kwargs) -> BaseChatModel:
        """Create OpenAI chat client."""
        try:
            project_name = kwargs.get("langsmith_project", "joke-agent-poc")
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.get_api_key(),
                model_kwargs={
                    "extra_headers": {
                        "X-LangSmith-Project": project_name
                    }
                }
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to create OpenAI client: {str(e)}")


class GroqProvider(LLMProvider):
    """Groq LLM provider."""
    
    def get_api_key(self) -> str:
        """Get Groq API key from secrets or environment."""
        api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not api_key or api_key.startswith("gsk-your"):
            raise ConfigurationError(
                "GROQ_API_KEY not found in environment. "
                "Please set it in your .env file or Streamlit secrets."
            )
        return api_key
    
    def create_client(self, model: str, temperature: float, **kwargs) -> BaseChatModel:
        """Create Groq chat client."""
        try:
            return ChatGroq(
                model=model,
                temperature=temperature,
                api_key=self.get_api_key(),
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to create Groq client: {str(e)}")


class HuggingFaceProvider(LLMProvider):
    """HuggingFace LLM provider."""
    
    def get_api_key(self) -> str:
        """Get HuggingFace API key from secrets or environment."""
        api_key = st.secrets.get("HUGGINGFACE_API_KEY") or os.environ.get("HUGGINGFACE_API_KEY")
        if not api_key or api_key.startswith("hf_your"):
            raise ConfigurationError(
                "HUGGINGFACE_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your key at: https://huggingface.co/settings/tokens"
            )
        return api_key
    
    def create_client(self, model: str, temperature: float, **kwargs) -> BaseChatModel:
        """Create HuggingFace chat client."""
        try:
            from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        except ImportError:
            raise LLMProviderError(
                "langchain-huggingface package not installed. "
                "Install with: pip install langchain-huggingface"
            )
        
        try:
            llm = HuggingFaceEndpoint(
                repo_id=model,
                temperature=temperature,
                max_new_tokens=512,
                huggingfacehub_api_token=self.get_api_key(),
            )
            return ChatHuggingFace(llm=llm)
        except Exception as e:
            raise LLMProviderError(f"Failed to create HuggingFace client: {str(e)}")


class TogetherProvider(LLMProvider):
    """Together AI LLM provider (OpenAI-compatible API)."""
    
    def get_api_key(self) -> str:
        """Get Together AI API key from secrets or environment."""
        api_key = st.secrets.get("TOGETHER_API_KEY") or os.environ.get("TOGETHER_API_KEY")
        if not api_key or api_key.startswith("your-together"):
            raise ConfigurationError(
                "TOGETHER_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your key at: https://api.together.xyz/settings/api-keys"
            )
        return api_key
    
    def create_client(self, model: str, temperature: float, **kwargs) -> BaseChatModel:
        """Create Together AI chat client (OpenAI-compatible)."""
        try:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.get_api_key(),
                base_url="https://api.together.xyz/v1",
                max_tokens=512,
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to create Together AI client: {str(e)}")


class DeepInfraProvider(LLMProvider):
    """DeepInfra LLM provider (OpenAI-compatible API)."""
    
    def get_api_key(self) -> str:
        """Get DeepInfra API key from secrets or environment."""
        api_key = st.secrets.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_API_KEY")
        if not api_key or api_key.startswith("your-deepinfra"):
            raise ConfigurationError(
                "DEEPINFRA_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your key at: https://deepinfra.com/dash/api_keys"
            )
        return api_key
    
    def create_client(self, model: str, temperature: float, **kwargs) -> BaseChatModel:
        """Create DeepInfra chat client (OpenAI-compatible)."""
        try:
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=self.get_api_key(),
                base_url="https://api.deepinfra.com/v1/openai",
                max_tokens=512,
            )
        except Exception as e:
            raise LLMProviderError(f"Failed to create DeepInfra client: {str(e)}")


# Provider registry
PROVIDER_REGISTRY = {
    "openai": OpenAIProvider(),
    "groq": GroqProvider(),
    "huggingface": HuggingFaceProvider(),
    "together": TogetherProvider(),
    "deepinfra": DeepInfraProvider(),
}


def get_provider(provider_name: str) -> LLMProvider:
    """
    Get a provider instance by name.
    
    Args:
        provider_name: Name of the provider
    
    Returns:
        Provider instance
    
    Raises:
        ValueError: If provider not found
    """
    provider = PROVIDER_REGISTRY.get(provider_name.lower())
    if not provider:
        raise ValueError(
            f"Unsupported LLM provider: {provider_name}. "
            f"Supported: {', '.join(PROVIDER_REGISTRY.keys())}"
        )
    return provider


def fetch_openai_models() -> list[str]:
    """
    Query OpenAI's API to retrieve available models for the current API key.
    
    Returns:
        List of available model IDs, sorted by capability.
        Falls back to default models if API call fails.
    """
    from openai import OpenAI
    
    fallback_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    try:
        provider = OpenAIProvider()
        client = OpenAI(api_key=provider.get_api_key())
        models_response = client.models.list()
        all_models = [model.id for model in models_response.data]
        
        # Filter for chat-capable models
        chat_prefixes = ["gpt-4o", "gpt-4-", "gpt-4", "o1", "o3", "gpt-3.5-turbo"]
        chat_models = [
            m for m in all_models
            if any(m.startswith(p) for p in chat_prefixes) and ':' not in m
        ]
        
        # Sort by priority
        def priority(model_id: str) -> int:
            if model_id.startswith("o3"): return 0
            elif model_id.startswith("o1") and "mini" not in model_id: return 1
            elif model_id.startswith("o1-mini"): return 2
            elif model_id.startswith("gpt-4o") and "mini" not in model_id: return 3
            elif model_id.startswith("gpt-4o-mini"): return 4
            elif model_id.startswith("gpt-4-turbo"): return 5
            elif model_id.startswith("gpt-4"): return 6
            elif model_id.startswith("gpt-3.5-turbo"): return 7
            return 999
        
        chat_models.sort(key=priority)
        return chat_models if chat_models else fallback_models
        
    except Exception as e:
        print(f"⚠️ Error fetching OpenAI models: {str(e)}")
        return fallback_models
