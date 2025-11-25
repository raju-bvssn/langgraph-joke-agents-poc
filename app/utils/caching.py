"""
Caching utilities for the joke agents application.
Provides decorators and helpers for caching expensive operations.
"""
import streamlit as st
from functools import wraps
from typing import Callable, Any


def cache_openai_models(ttl: int = 3600) -> Callable:
    """
    Decorator to cache OpenAI model fetching.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
    
    Returns:
        Decorated function with caching
    """
    return st.cache_data(ttl=ttl, show_spinner=False)


def cache_tts_audio(ttl: int = 3600) -> Callable:
    """
    Decorator to cache TTS audio generation.
    
    Args:
        ttl: Time to live in seconds (default 1 hour)
    
    Returns:
        Decorated function with caching
    """
    return st.cache_data(ttl=ttl, show_spinner=False)


def cache_llm_response(ttl: int = 300) -> Callable:
    """
    Decorator to cache LLM responses.
    
    Args:
        ttl: Time to live in seconds (default 5 minutes)
    
    Returns:
        Decorated function with caching
    """
    return st.cache_data(ttl=ttl, show_spinner=False)
