"""
Fallback TTS implementation using browser-based text-to-speech.
Used when Google Cloud TTS is unavailable.
"""
import streamlit as st
from typing import Optional


def generate_browser_tts_html(text: str, voice_id: str = "default") -> str:
    """
    Generate HTML/JavaScript for browser-based TTS playback.
    
    Args:
        text: Text to convert to speech
        voice_id: Voice identifier (not fully supported across browsers)
    
    Returns:
        HTML string with embedded JavaScript for TTS
    """
    # Escape quotes in text
    escaped_text = text.replace("'", "\\'").replace('"', '\\"')
    
    html = f"""
    <div style="margin: 10px 0;">
        <button onclick="speakText_{hash(text)}" style="
            background: linear-gradient(135deg, #4A90E2 0%, #7F5AF0 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        ">
            🔊 Play with Browser TTS
        </button>
    </div>
    <script>
        function speakText_{hash(text)}() {{
            const text = "{escaped_text}";
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.1;  // Slightly faster for comedy timing
            utterance.pitch = 1.1; // Slightly higher pitch
            speechSynthesis.speak(utterance);
        }}
    </script>
    """
    return html


def display_fallback_tts(text: str):
    """
    Display fallback TTS option when Google Cloud TTS is unavailable.
    
    Args:
        text: Text to convert to speech
    """
    st.info(
        "💡 Google Cloud TTS is not configured. "
        "Using browser-based fallback (quality may vary)."
    )
    st.markdown(generate_browser_tts_html(text), unsafe_allow_html=True)

