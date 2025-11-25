"""
Google Cloud Text-to-Speech implementation.
Uses REST API with API key authentication for voice generation.
"""
import os
import base64
import requests
import streamlit as st
from typing import Optional

from app.utils.exceptions import TTSError, ConfigurationError


# Voice style mapping for Google Cloud TTS
VOICE_STYLES = {
    "🎭 Stand-up Comedy": {
        "voice": "en-US-Wavenet-J",
        "pitch": 2.0,
        "rate": 1.07,
        "description": "Energetic male voice perfect for punchlines"
    },
    "🗣️ Deep Narrator": {
        "voice": "en-US-Wavenet-D",
        "pitch": -2.0,
        "rate": 0.95,
        "description": "Deep, measured voice for dramatic delivery"
    },
    "💬 Conversational": {
        "voice": "en-US-Wavenet-A",
        "pitch": 0.0,
        "rate": 1.0,
        "description": "Natural, friendly voice"
    },
    "⚡ High Energy": {
        "voice": "en-US-Wavenet-F",
        "pitch": 3.0,
        "rate": 1.15,
        "description": "Fast, excited delivery"
    },
    "📚 Storyteller": {
        "voice": "en-US-Neural2-J",
        "pitch": 1.0,
        "rate": 1.05,
        "description": "Warm, engaging narrative voice"
    },
    "📰 News Anchor": {
        "voice": "en-US-Neural2-D",
        "pitch": 0.0,
        "rate": 1.0,
        "description": "Clear, professional presentation"
    }
}


class GoogleTTS:
    """Google Cloud Text-to-Speech client."""
    
    def __init__(self):
        """Initialize Google TTS client."""
        self.api_key = self._get_api_key()
        self.endpoint = "https://texttospeech.googleapis.com/v1/text:synthesize"
    
    def _get_api_key(self) -> str:
        """
        Get Google Cloud API key from secrets or environment.
        
        Returns:
            API key string
        
        Raises:
            ConfigurationError: If API key not found
        """
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key or api_key.startswith("your-google"):
            raise ConfigurationError(
                "Google Cloud API key not found. "
                "Please configure GOOGLE_API_KEY in Streamlit secrets or .env file."
            )
        return api_key
    
    def _determine_gender(self, voice_name: str) -> str:
        """
        Determine voice gender from voice name.
        
        Args:
            voice_name: Google Cloud voice name
        
        Returns:
            Gender string (MALE, FEMALE, or NEUTRAL)
        """
        # D and J variants are typically male
        if any(x in voice_name for x in ["D", "J"]):
            return "MALE"
        # F and A variants are typically female/neutral
        return "NEUTRAL"
    
    def generate_audio(
        self,
        text: str,
        voice_name: str,
        pitch: float = 2.0,
        speaking_rate: float = 1.07
    ) -> bytes:
        """
        Generate audio from text using Google Cloud TTS.
        
        Args:
            text: Text to convert to speech
            voice_name: Google Cloud voice name (e.g., "en-US-Wavenet-J")
            pitch: Voice pitch (-20.0 to 20.0)
            speaking_rate: Speech speed (0.25 to 4.0)
        
        Returns:
            Audio bytes in MP3 format
        
        Raises:
            TTSError: If audio generation fails
        """
        try:
            url = f"{self.endpoint}?key={self.api_key}"
            gender = self._determine_gender(voice_name)
            
            payload = {
                "input": {"text": text},
                "voice": {
                    "languageCode": "en-US",
                    "name": voice_name,
                    "ssmlGender": gender
                },
                "audioConfig": {
                    "audioEncoding": "MP3",
                    "pitch": pitch,
                    "speakingRate": speaking_rate
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            audio_b64 = response.json().get("audioContent")
            if not audio_b64:
                raise TTSError("No audio content received from Google Cloud TTS")
            
            return base64.b64decode(audio_b64)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Google Cloud TTS API error: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    detail_msg = error_detail.get('error', {}).get('message', 'Unknown error')
                    error_msg += f"\nDetails: {detail_msg}"
                except:
                    pass
            raise TTSError(error_msg)
        except Exception as e:
            raise TTSError(f"Error generating voice: {str(e)}")


def get_voice_config(style_name: str) -> dict:
    """
    Get voice configuration for a given style name.
    
    Args:
        style_name: Display name of the voice style
    
    Returns:
        Dictionary with voice, pitch, and rate settings
    """
    return VOICE_STYLES.get(style_name, VOICE_STYLES["🎭 Stand-up Comedy"])


def get_available_styles() -> list[str]:
    """
    Get list of available voice styles.
    
    Returns:
        List of style display names
    """
    return list(VOICE_STYLES.keys())

