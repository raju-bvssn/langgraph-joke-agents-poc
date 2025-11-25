"""
Text-to-Speech module with Google Cloud TTS and fallback support.
"""
from app.tts.google_tts import VOICE_STYLES, get_voice_config, get_available_styles
from app.tts.factory import create_tts_engine, generate_audio
from app.tts.fallback_tts import display_fallback_tts

__all__ = [
    "VOICE_STYLES",
    "get_voice_config",
    "get_available_styles",
    "create_tts_engine",
    "generate_audio",
    "display_fallback_tts",
]

