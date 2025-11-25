"""
LLM configuration utilities.
Provides helpers for reading API keys and configuration from environment/secrets.
"""
import os
import streamlit as st
from typing import Optional
from app.utils.exceptions import APIKeyMissingError


def get_api_key(key_name: str, provider: Optional[str] = None, required: bool = True) -> Optional[str]:
    """
    Get an API key from Streamlit secrets or environment variables.
    
    Args:
        key_name: Name of the API key (e.g., "OPENAI_API_KEY")
        provider: Provider name for error messages (optional)
        required: Whether to raise an error if key is missing
    
    Returns:
        API key string, or None if not found and not required
    
    Raises:
        APIKeyMissingError: If key is not found and required=True
    """
    # Try Streamlit secrets first
    key = st.secrets.get(key_name)
    
    # Fall back to environment variables
    if not key:
        key = os.environ.get(key_name)
    
    # Handle missing key
    if not key and required:
        raise APIKeyMissingError(key_name, provider)
    
    return key


def get_temperature(agent_type: str) -> float:
    """
    Get the appropriate temperature setting for an agent type.
    
    Args:
        agent_type: Either "performer" or "critic"
    
    Returns:
        Temperature value (0.0 to 1.0)
    """
    if agent_type == "performer":
        return 0.9  # Higher creativity for joke generation
    elif agent_type == "critic":
        return 0.3  # Lower temperature for consistent evaluation
    else:
        return 0.7  # Default


def get_max_tokens(agent_type: str) -> int:
    """
    Get the appropriate max_tokens setting for an agent type.
    
    Args:
        agent_type: Either "performer" or "critic"
    
    Returns:
        Max tokens integer
    """
    if agent_type == "performer":
        return 500  # Jokes are usually short
    elif agent_type == "critic":
        return 1000  # Evaluations need more detail
    else:
        return 500  # Default

