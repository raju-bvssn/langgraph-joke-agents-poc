"""
Custom exceptions for the joke agents application.
"""


class JokeAgentException(Exception):
    """Base exception for all joke agent errors."""
    pass


class LLMProviderError(JokeAgentException):
    """Raised when an LLM provider fails or is misconfigured."""
    pass


class TTSError(JokeAgentException):
    """Raised when text-to-speech generation fails."""
    pass


class WorkflowError(JokeAgentException):
    """Raised when the LangGraph workflow encounters an error."""
    pass


class ConfigurationError(JokeAgentException):
    """Raised when configuration is invalid or missing."""
    pass
