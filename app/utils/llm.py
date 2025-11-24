"""
LLM configuration and initialization.
Supports multiple LLM providers with LangSmith tracing:
- OpenAI (paid, dynamic model detection)
- Groq (free)
- HuggingFace Inference API (free)
- Together AI (free)
- DeepInfra (free)

Runtime selection of provider and model per agent.
"""
from typing import Optional, List

from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel


def fetch_openai_models() -> List[str]:
    """
    Query OpenAI's API to retrieve the list of models available for the current API key.
    
    Filters to include only chat-capable models (GPT-4, GPT-4o, o1, o3, etc.).
    
    Returns:
        List of available model IDs, sorted by capability (higher-tier first).
        Falls back to default models if API call fails.
    """
    from .settings import settings
    
    # Fallback models if API call fails
    fallback_models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    
    # Check if OpenAI API key is available
    if not settings.openai_api_key or settings.openai_api_key.startswith("sk-your"):
        print("⚠️  No valid OpenAI API key found. Using fallback models.")
        return fallback_models
    
    try:
        from openai import OpenAI
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Fetch all models
        models_response = client.models.list()
        
        # Extract model IDs
        all_models = [model.id for model in models_response.data]
        
        # Filter for chat-capable models
        chat_models = []
        
        # Define prefixes for chat models
        chat_prefixes = [
            "gpt-4o",           # GPT-4 Optimized variants
            "gpt-4-",           # GPT-4 variants (turbo, etc.)
            "gpt-4",            # Base GPT-4 models
            "o1",               # O1 series
            "o3",               # O3 series  
            "gpt-3.5-turbo",    # GPT-3.5 turbo
        ]
        
        for model_id in all_models:
            # Check if model starts with any chat prefix
            if any(model_id.startswith(prefix) for prefix in chat_prefixes):
                # Exclude fine-tuned models (contain ':')
                if ':' not in model_id:
                    chat_models.append(model_id)
        
        # Sort models by priority (more capable models first)
        def model_priority(model_id: str) -> int:
            """Assign priority for sorting (lower number = higher priority)"""
            if model_id.startswith("o3"):
                return 0
            elif model_id.startswith("o1") and "mini" not in model_id:
                return 1
            elif model_id.startswith("o1-mini"):
                return 2
            elif model_id.startswith("gpt-4o") and "mini" not in model_id:
                return 3
            elif model_id.startswith("gpt-4o-mini"):
                return 4
            elif model_id.startswith("gpt-4-turbo"):
                return 5
            elif model_id.startswith("gpt-4") and "turbo" not in model_id:
                return 6
            elif model_id.startswith("gpt-3.5-turbo"):
                return 7
            else:
                return 999
        
        chat_models.sort(key=model_priority)
        
        if not chat_models:
            print("⚠️  No chat models found in OpenAI account. Using fallback models.")
            return fallback_models
        
        print(f"✅ Detected {len(chat_models)} OpenAI models from account")
        return chat_models
        
    except Exception as e:
        print(f"⚠️  Error fetching OpenAI models: {str(e)}")
        print(f"   Using fallback models: {fallback_models}")
        return fallback_models


# Import settings after defining fetch_openai_models
from .settings import settings, MODEL_CATALOG, DEFAULT_MODELS


def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> BaseChatModel:
    """
    Get configured LLM instance with runtime provider and model selection.
    
    Supports: OpenAI, Groq, HuggingFace, Together AI, DeepInfra
    
    Args:
        provider: LLM provider. Uses settings.llm_provider if None.
        model: Model name. Uses default for provider if None.
        temperature: Temperature setting. Uses settings.temperature if None.
        
    Returns:
        Configured chat model instance with LangSmith tracing enabled.
        
    Raises:
        ValueError: If provider is unsupported or API key is missing.
    """
    # Use defaults from settings if not provided
    provider = provider or settings.llm_provider
    temp = temperature if temperature is not None else settings.temperature
    
    # Get default model for provider if not specified
    if model is None:
        model = DEFAULT_MODELS.get(provider, settings.openai_model)
    
    # Validate model is in catalog (skip validation for OpenAI since models are dynamic)
    if provider != "openai" and provider in MODEL_CATALOG and model not in MODEL_CATALOG[provider]:
        raise ValueError(
            f"Model '{model}' not found in catalog for provider '{provider}'. "
            f"Available models: {', '.join(MODEL_CATALOG[provider])}"
        )
    
    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment. "
                "Please set it in your .env file."
            )
        
        return ChatOpenAI(
            model=model,
            temperature=temp,
            api_key=settings.openai_api_key,
            model_kwargs={
                "extra_headers": {
                    "X-LangSmith-Project": settings.langchain_project
                }
            }
        )
    
    elif provider == "groq":
        if not settings.groq_api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment. "
                "Please set it in your .env file."
            )
        
        return ChatGroq(
            model=model,
            temperature=temp,
            api_key=settings.groq_api_key,
        )
    
    elif provider == "huggingface":
        if not settings.huggingface_api_key:
            raise ValueError(
                "HUGGINGFACE_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your key at: https://huggingface.co/settings/tokens"
            )
        
        try:
            from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
        except ImportError:
            raise ValueError(
                "langchain-huggingface package not installed. "
                "Install with: pip install langchain-huggingface"
            )
        
        # Create the endpoint
        llm = HuggingFaceEndpoint(
            repo_id=model,
            temperature=temp,
            max_new_tokens=512,
            huggingfacehub_api_token=settings.huggingface_api_key,
        )
        
        # Wrap in ChatHuggingFace for chat interface
        return ChatHuggingFace(llm=llm)
    
    elif provider == "together":
        if not settings.together_api_key:
            raise ValueError(
                "TOGETHER_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your key at: https://api.together.xyz/settings/api-keys"
            )
        
        # Together AI has OpenAI-compatible API
        return ChatOpenAI(
            model=model,
            temperature=temp,
            api_key=settings.together_api_key,
            base_url="https://api.together.xyz/v1",
            max_tokens=512,
        )
    
    elif provider == "deepinfra":
        if not settings.deepinfra_api_key:
            raise ValueError(
                "DEEPINFRA_API_KEY not found in environment. "
                "Please set it in your .env file. "
                "Get your key at: https://deepinfra.com/dash/api_keys"
            )
        
        # DeepInfra has OpenAI-compatible API
        return ChatOpenAI(
            model=model,
            temperature=temp,
            api_key=settings.deepinfra_api_key,
            base_url="https://api.deepinfra.com/v1/openai",
            max_tokens=512,
        )
    
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported: openai, groq, huggingface, together, deepinfra"
        )


def get_performer_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None
) -> BaseChatModel:
    """
    Get LLM configured for the Performer agent (creative, higher temperature).
    
    Args:
        provider: Optional provider override.
        model: Optional model override.
        
    Returns:
        Configured LLM with temperature=0.9 for creativity.
    """
    return get_llm(provider=provider, model=model, temperature=0.9)


def get_critic_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None
) -> BaseChatModel:
    """
    Get LLM configured for the Critic agent (analytical, lower temperature).
    
    Args:
        provider: Optional provider override.
        model: Optional model override.
        
    Returns:
        Configured LLM with temperature=0.3 for consistency.
    """
    return get_llm(provider=provider, model=model, temperature=0.3)

