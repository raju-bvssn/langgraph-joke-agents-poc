"""
Factory for creating TTS engines with fallback support.
"""
from typing import Optional
import streamlit as st

from app.tts.google_tts import GoogleTTS
from app.utils.exceptions import ConfigurationError, TTSError


def create_tts_engine() -> Optional[GoogleTTS]:
    """
    Create a TTS engine instance with fallback handling.
    
    Returns:
        GoogleTTS instance if configured, None if fallback should be used
    """
    try:
        return GoogleTTS()
    except ConfigurationError:
        return None


def generate_audio(
    text: str,
    voice_name: str,
    pitch: float = 2.0,
    speaking_rate: float = 1.07,
    use_fallback: bool = True
) -> Optional[bytes]:
    """
    Generate audio from text with automatic fallback.
    
    Args:
        text: Text to convert to speech
        voice_name: Voice identifier
        pitch: Voice pitch adjustment
        speaking_rate: Speech speed
        use_fallback: Whether to use fallback TTS if Google Cloud fails
    
    Returns:
        Audio bytes in MP3 format, or None if using fallback
    """
    try:
        tts = create_tts_engine()
        if tts:
            return tts.generate_audio(text, voice_name, pitch, speaking_rate)
        elif use_fallback:
            # Signal to use browser-based fallback
            return None
        else:
            raise TTSError("Google Cloud TTS not configured and fallback disabled")
    except (TTSError, ConfigurationError) as e:
        if use_fallback:
            st.warning(f"⚠️ {str(e)}")
            return None
        else:
            raise

