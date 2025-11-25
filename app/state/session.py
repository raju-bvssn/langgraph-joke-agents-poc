"""
Session state management for the Streamlit application.
Provides centralized initialization and access to session state.
"""
import streamlit as st
from typing import Any, Optional


class SessionState:
    """Wrapper for Streamlit session state with type-safe access."""
    
    @staticmethod
    def initialize():
        """Initialize all session state variables with defaults."""
        defaults = {
            "history": [],
            "workflow": None,
            "workflow_complete": False,
            "llm_config": {
                "performer_provider": "groq",
                "performer_model": "llama-3.3-70b-versatile",
                "critic_provider": "groq",
                "critic_model": "llama-3.3-70b-versatile",
            },
            "cycle_audio": {},
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get a value from session state.
        
        Args:
            key: Session state key
            default: Default value if key not found
        
        Returns:
            Value from session state or default
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any):
        """
        Set a value in session state.
        
        Args:
            key: Session state key
            value: Value to set
        """
        st.session_state[key] = value
    
    @staticmethod
    def get_history() -> list:
        """Get the joke/evaluation history."""
        return st.session_state.get("history", [])
    
    @staticmethod
    def add_to_history(joke: str, feedback: dict, cycle_type: str = "initial"):
        """
        Add a new cycle to history.
        
        Args:
            joke: The joke text
            feedback: The critic feedback dictionary
            cycle_type: Type of cycle (initial, revised, reevaluated)
        """
        history = st.session_state.get("history", [])
        history.append({
            "joke": joke,
            "feedback": feedback,
            "cycle_type": cycle_type
        })
        st.session_state["history"] = history
    
    @staticmethod
    def clear_history():
        """Clear the joke/evaluation history."""
        st.session_state["history"] = []
    
    @staticmethod
    def get_llm_config() -> dict:
        """Get the current LLM configuration."""
        return st.session_state.get("llm_config", {})
    
    @staticmethod
    def update_llm_config(config: dict):
        """
        Update LLM configuration.
        
        Args:
            config: Dictionary with LLM configuration
        """
        current_config = st.session_state.get("llm_config", {})
        current_config.update(config)
        st.session_state["llm_config"] = current_config
    
    @staticmethod
    def get_workflow():
        """Get the current workflow instance."""
        return st.session_state.get("workflow")
    
    @staticmethod
    def set_workflow(workflow):
        """
        Set the workflow instance.
        
        Args:
            workflow: JokeWorkflow instance
        """
        st.session_state["workflow"] = workflow
    
    @staticmethod
    def is_workflow_complete() -> bool:
        """Check if the workflow is complete."""
        return st.session_state.get("workflow_complete", False)
    
    @staticmethod
    def set_workflow_complete(complete: bool):
        """
        Set workflow completion status.
        
        Args:
            complete: Whether the workflow is complete
        """
        st.session_state["workflow_complete"] = complete
    
    @staticmethod
    def store_audio(cycle_num: int, audio_bytes: bytes):
        """
        Store audio for a specific cycle.
        
        Args:
            cycle_num: Cycle number
            audio_bytes: Audio data in bytes
        """
        if "cycle_audio" not in st.session_state:
            st.session_state["cycle_audio"] = {}
        st.session_state["cycle_audio"][cycle_num] = audio_bytes
    
    @staticmethod
    def get_audio(cycle_num: int) -> Optional[bytes]:
        """
        Get stored audio for a cycle.
        
        Args:
            cycle_num: Cycle number
        
        Returns:
            Audio bytes or None if not found
        """
        cycle_audio = st.session_state.get("cycle_audio", {})
        return cycle_audio.get(cycle_num)

