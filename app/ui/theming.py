"""
Windsurf-inspired UI theming with dark mode and glassmorphism.
Contains all CSS styling for the application.
"""
import streamlit as st


def apply_windsurf_theme():
    """Apply the complete Windsurf-inspired dark theme with CSS."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Theming */
    :root {
        --primary: #4A90E2;
        --secondary: #0E1117;
        --accent: #7F5AF0;
        --background: #1A1F27;
        --surface: #2A2F36;
        --success: #2ECC71;
        --error: #E74C3C;
        --text-light: #EAEAEA;
        --text-muted: #A5A5A5;
    }
    
    /* Force Override ALL Streamlit Defaults to Dark Theme */
    html, body, [class*="css"], .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stHeader"], .main, .block-container, [data-testid="stSidebar"] {
        background-color: #0E1117 !important;
        color: #EAEAEA !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1A1F27 100%) !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar dark theme */
    [data-testid="stSidebar"] {
        background: #0E1117 !important;
        border-right: 1px solid rgba(127, 90, 240, 0.2);
    }
    
    /* Override input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background-color: #1A1F27 !important;
        color: #EAEAEA !important;
        border: 1px solid rgba(127, 90, 240, 0.3) !important;
    }
    
    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.07);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    
    /* Joke container */
    .joke-container {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.15) 0%, rgba(127, 90, 240, 0.1) 100%);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 14px;
        border: 1px solid rgba(74, 144, 226, 0.3);
        margin: 15px 0;
        font-size: 18px;
        line-height: 1.8;
        color: var(--text-light);
    }
    
    /* Agent Badge */
    .agent-badge {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(127, 90, 240, 0.3);
    }
    
    /* Buttons */
    .stButton > button {
        background: #1A1F27 !important;
        border: 1px solid #7F5AF0 !important;
        color: white !important;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0px 0px 12px #7F5AF0 !important;
        border: 1px solid #A28CFF !important;
        transform: translateY(-1px);
    }
    
    /* Gradient divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        margin: 30px 0;
        border-radius: 2px;
        opacity: 0.6;
    }
</style>
""", unsafe_allow_html=True)


def get_theme_colors() -> dict:
    """
    Get theme color definitions.
    
    Returns:
        Dictionary of theme colors
    """
    return {
        "primary": "#4A90E2",
        "accent": "#7F5AF0",
        "background": "#0E1117",
        "surface": "#1A1F27",
        "success": "#2ECC71",
        "error": "#E74C3C",
        "text_light": "#EAEAEA",
        "text_muted": "#A5A5A5",
    }

