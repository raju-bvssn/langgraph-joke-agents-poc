"""
Google Cloud Text-to-Speech integration for joke voice playback.
Uses the REST API with simple API key authentication.
"""
import streamlit as st
import os
import base64
import requests
from typing import Optional


def generate_standup_voice(text: str, voice_name: str, pitch: float = 2.0, speaking_rate: float = 1.07) -> Optional[bytes]:
    """
    Generate expressive audio from text using Google Cloud Text-to-Speech API.
    
    Args:
        text: The joke text to convert to speech
        voice_name: Google Cloud voice name (e.g., "en-US-Wavenet-J")
        pitch: Voice pitch adjustment (-20.0 to 20.0, default 2.0 for energetic)
        speaking_rate: Speech speed (0.25 to 4.0, default 1.07 for comedy timing)
    
    Returns:
        Audio bytes in MP3 format, or None on error
    """
    try:
        # Get Google Cloud API key from secrets or environment
        api_key = st.secrets.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            st.error("Google Cloud API key not found. Please configure GOOGLE_API_KEY in Streamlit secrets.")
            return None
        
        # Google Cloud TTS REST API endpoint
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
        
        # Determine gender from voice name (Wavenet-D/J are typically male, others vary)
        gender = "MALE" if any(x in voice_name for x in ["D", "J"]) else "NEUTRAL"
        
        # Request payload
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
        
        # Make API request
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        # Extract and decode audio
        audio_b64 = response.json().get("audioContent")
        if not audio_b64:
            st.error("No audio content received from Google Cloud TTS.")
            return None
        
        return base64.b64decode(audio_b64)
        
    except requests.exceptions.RequestException as e:
        st.error(f"Google Cloud TTS API error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                st.error(f"Details: {error_detail.get('error', {}).get('message', 'Unknown error')}")
            except:
                pass
        return None
    except Exception as e:
        st.error(f"Error generating voice with Google Cloud TTS: {str(e)}")
        return None


# Voice style mapping for the UI
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


def get_voice_config(style_name: str) -> dict:
    """
    Get voice configuration for a given style name.
    
    Args:
        style_name: The display name of the voice style
    
    Returns:
        Dictionary with voice, pitch, and rate settings
    """
    return VOICE_STYLES.get(style_name, VOICE_STYLES["🎭 Stand-up Comedy"])

