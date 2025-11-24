"""
Streamlit UI for the Multi-Agent Joke System.
Provides an interactive interface to generate and evaluate jokes with enhanced UX.
"""
import streamlit as st
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import difflib

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.llm import get_performer_llm, get_critic_llm, get_llm, fetch_openai_models
from app.utils.settings import settings, MODEL_CATALOG
from app.graph.workflow import JokeWorkflow


# Cache the dynamic OpenAI models to avoid repeated API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_openai_models_cached():
    """Fetch OpenAI models with caching to avoid repeated API calls."""
    return fetch_openai_models()


# Page configuration
st.set_page_config(
    page_title="🎭 Joke Agent POC",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Modern AI-Themed Custom CSS with Glassmorphism & Animations
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
    
    /* Override Streamlit defaults */
    .stApp {
        background: linear-gradient(135deg, #0E1117 0%, #1A1F27 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0E1117 0%, #1A1F27 100%);
        border-right: 1px solid rgba(127, 90, 240, 0.2);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: var(--text-light);
        font-weight: 600;
    }
    
    /* Sidebar section headers */
    .sidebar-section-header {
        color: var(--primary);
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-top: 20px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(74, 144, 226, 0.3);
    }
    
    /* Sidebar navigation items */
    .sidebar-nav-item {
        background: rgba(255, 255, 255, 0.05);
        padding: 10px 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid var(--accent);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .sidebar-nav-item:hover {
        background: rgba(127, 90, 240, 0.15);
        border-left-color: var(--primary);
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(127, 90, 240, 0.2);
    }
    
    /* Hero Header */
    .hero-header {
        background: radial-gradient(circle at 20% 50%, rgba(127, 90, 240, 0.15), transparent 50%),
                    radial-gradient(circle at 80% 50%, rgba(74, 144, 226, 0.15), transparent 50%),
                    linear-gradient(135deg, #0E1117 0%, #1A1F27 100%);
        padding: 40px 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        border: 1px solid rgba(127, 90, 240, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        animation: shimmer 3s infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .hero-title {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(135deg, #4A90E2 0%, #7F5AF0 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        letter-spacing: -0.5px;
    }
    
    .hero-subtitle {
        color: var(--text-muted);
        font-size: 16px;
        line-height: 1.6;
        max-width: 800px;
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
    
    .glass-card:hover {
        border-color: rgba(127, 90, 240, 0.4);
        box-shadow: 0 12px 48px 0 rgba(127, 90, 240, 0.2);
        transform: translateY(-2px);
    }
    
    /* Joke container with AI theme */
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
        position: relative;
        overflow: hidden;
    }
    
    .joke-container::before {
        content: '😂';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 32px;
        opacity: 0.2;
    }
    
    /* Evaluation container with AI theme */
    .eval-container {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(74, 144, 226, 0.1) 100%);
        backdrop-filter: blur(10px);
        padding: 24px;
        border-radius: 14px;
        border: 1px solid rgba(46, 204, 113, 0.3);
        margin: 15px 0;
        position: relative;
    }
    
    .eval-container::before {
        content: '🧠';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 32px;
        opacity: 0.2;
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
    
    .agent-badge-performer {
        background: linear-gradient(135deg, #4A90E2 0%, #5BC0DE 100%);
    }
    
    .agent-badge-critic {
        background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%);
    }
    
    /* Cycle header with gradient */
    .cycle-header {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.2) 0%, rgba(127, 90, 240, 0.2) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(127, 90, 240, 0.4);
        color: var(--text-light);
        padding: 20px 24px;
        border-radius: 14px;
        margin: 25px 0 15px 0;
        font-weight: 700;
        font-size: 22px;
        position: relative;
        overflow: hidden;
    }
    
    .cycle-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        animation: slide 3s infinite;
    }
    
    @keyframes slide {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* AI-themed button group */
    .button-group {
        background: linear-gradient(135deg, rgba(127, 90, 240, 0.15) 0%, rgba(74, 144, 226, 0.15) 100%);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 14px;
        margin: 20px 0;
        border: 1px solid rgba(127, 90, 240, 0.3);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    
    /* Custom button styling */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        border: none;
        transition: all 0.3s ease;
        font-size: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(127, 90, 240, 0.4);
    }
    
    /* Diff viewer with AI theme */
    .diff-container {
        background: linear-gradient(135deg, rgba(127, 90, 240, 0.1) 0%, rgba(231, 76, 60, 0.1) 100%);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 14px;
        margin: 20px 0;
        border: 1px solid rgba(127, 90, 240, 0.3);
    }
    
    .diff-header {
        font-size: 18px;
        font-weight: 600;
        color: var(--text-light);
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* Models metadata */
    .models-info {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.15) 0%, rgba(74, 144, 226, 0.15) 100%);
        backdrop-filter: blur(10px);
        padding: 16px;
        border-radius: 12px;
        font-size: 14px;
        margin: 15px 0;
        border: 1px solid rgba(46, 204, 113, 0.3);
        color: var(--text-light);
    }
    
    .models-info code {
        background: rgba(0, 0, 0, 0.3);
        padding: 3px 8px;
        border-radius: 6px;
        color: var(--primary);
        font-weight: 600;
    }
    
    /* Score badges */
    .score-badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
        background: linear-gradient(135deg, var(--success) 0%, var(--primary) 100%);
        color: white;
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
    }
    
    /* Loading animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 0 20px rgba(127, 90, 240, 0.5); }
        50% { box-shadow: 0 0 40px rgba(127, 90, 240, 0.8); }
    }
    
    .loading-performer {
        border: 2px solid var(--primary);
        animation: glow 2s infinite, pulse 2s infinite;
    }
    
    .loading-critic {
        border: 2px solid var(--success);
        animation: glow 2s infinite, pulse 2s infinite;
    }
    
    /* Evaluation metrics styling */
    .eval-metric {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px 16px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 3px solid var(--accent);
        color: var(--text-light);
    }
    
    .eval-metric strong {
        color: var(--primary);
        font-weight: 600;
    }
    
    /* Gradient divider */
    .gradient-divider {
        height: 2px;
        background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
        margin: 30px 0;
        border-radius: 2px;
        opacity: 0.6;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .hero-title { font-size: 28px; }
        .glass-card { padding: 16px; }
        .joke-container, .eval-container { padding: 16px; }
    }
    
    /* Success message styling */
    .success-message {
        background: linear-gradient(135deg, rgba(46, 204, 113, 0.2) 0%, rgba(74, 144, 226, 0.2) 100%);
        border: 1px solid rgba(46, 204, 113, 0.4);
        color: var(--text-light);
        padding: 16px;
        border-radius: 12px;
        margin: 20px 0;
    }
    
    /* Info card */
    .info-card {
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.15) 0%, rgba(127, 90, 240, 0.15) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(74, 144, 226, 0.3);
        padding: 20px;
        border-radius: 14px;
        color: var(--text-light);
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)


def display_sidebar():
    """Display AI-themed configuration sidebar with dynamic model fetching and iteration navigation."""
    with st.sidebar:
        # AI-themed header
        st.markdown('<div class="sidebar-section-header">🤖 AI AGENTS CONTROL</div>', unsafe_allow_html=True)
        
        # Iterations Navigator (if history exists)
        if "history" in st.session_state and st.session_state.history:
            st.markdown("")
            st.markdown('<div class="sidebar-section-header">📘 ITERATION HISTORY</div>', unsafe_allow_html=True)
            st.caption("Navigate to specific revision cycles")
            
            for idx, cycle_data in enumerate(st.session_state.history):
                cycle_num = idx + 1
                cycle_type = cycle_data.get("cycle_type", "initial")
                
                if cycle_type == "initial":
                    emoji = "🎬"
                    label = f"Cycle {cycle_num}: Initial"
                elif cycle_type == "revised":
                    emoji = "✍️"
                    label = f"Cycle {cycle_num}: Revised"
                else:
                    emoji = "🔄"
                    label = f"Cycle {cycle_num}: Re-evaluated"
                
                # Create anchor link with AI-themed styling
                if st.button(f"{emoji} {label}", key=f"nav_{cycle_num}", use_container_width=True):
                    # Use Streamlit's experimental feature to scroll
                    st.session_state[f"scroll_to_cycle_{cycle_num}"] = True
                    st.rerun()
            
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-header">🎭 PERFORMER AGENT</div>', unsafe_allow_html=True)
        performer_provider = st.selectbox(
            "Provider",
            list(MODEL_CATALOG.keys()),
            key="performer_provider",
            help="Select LLM provider for joke generation"
        )
        
        # Get models based on provider (dynamic for OpenAI, static for others)
        if performer_provider == "openai":
            performer_models = get_openai_models_cached()
            if len(performer_models) > len(MODEL_CATALOG["openai"]):
                st.caption(f"✅ {len(performer_models)} models detected from your account")
        else:
            performer_models = MODEL_CATALOG[performer_provider]
        
        performer_model = st.selectbox(
            "Model",
            performer_models,
            key="performer_model",
            help="Select specific model for Performer"
        )
        
        st.caption(f"🎨 Temperature: 0.9 (creative)")
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-header">🧠 CRITIC AGENT</div>', unsafe_allow_html=True)
        critic_provider = st.selectbox(
            "Provider",
            list(MODEL_CATALOG.keys()),
            key="critic_provider",
            help="Select LLM provider for joke evaluation"
        )
        
        # Get models based on provider (dynamic for OpenAI, static for others)
        if critic_provider == "openai":
            critic_models = get_openai_models_cached()
            if len(critic_models) > len(MODEL_CATALOG["openai"]):
                st.caption(f"✅ {len(critic_models)} models detected from your account")
        else:
            critic_models = MODEL_CATALOG[critic_provider]
        
        critic_model = st.selectbox(
            "Model",
            critic_models,
            key="critic_model",
            help="Select specific model for Critic"
        )
        
        st.caption(f"🎯 Temperature: 0.3 (analytical)")
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-header">📊 LANGSMITH OBSERVABILITY</div>', unsafe_allow_html=True)
        st.markdown(f"**Project:** `{settings.langchain_project}`")
        st.markdown(f"**Tracing:** {'✅ Enabled' if settings.langchain_tracing_v2 == 'true' else '❌ Disabled'}")
        
        if settings.langchain_tracing_v2 == "true":
            st.success("🔍 All runs are being traced to LangSmith", icon="✅")
            st.markdown(
                f"[View Traces in LangSmith →]({settings.langchain_endpoint})"
            )
        
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section-header">ℹ️ SYSTEM INFO</div>', unsafe_allow_html=True)
        st.markdown("""
        **Multi-Agent Joke System v2.0**
        
        **Features:**
        - 🤖 Dual AI Agents
        - 🔄 LangGraph Orchestration
        - 📈 Real-time Observability
        - 🎨 5 LLM Providers
        - ✨ Iterative Refinement
        """)
        
        st.divider()
        
        with st.expander("🔧 Environment Status"):
            # Get OpenAI models for status display
            openai_models = get_openai_models_cached() if settings.openai_api_key else []
            
            status_text = f"""
API Keys:
  OpenAI: {'✓ Set' if settings.openai_api_key else '✗ Missing'}
  Groq: {'✓ Set' if settings.groq_api_key else '✗ Missing'}
  HuggingFace: {'✓ Set' if settings.huggingface_api_key else '✗ Missing'}
  Together AI: {'✓ Set' if settings.together_api_key else '✗ Missing'}
  DeepInfra: {'✓ Set' if settings.deepinfra_api_key else '✗ Missing'}
  LangSmith: {'✓ Set' if settings.langchain_api_key else '✗ Missing'}

Available Models:
  OpenAI: {len(openai_models)} detected
  Groq: {len(MODEL_CATALOG['groq'])} available
  HuggingFace: {len(MODEL_CATALOG['huggingface'])} available
  Together AI: {len(MODEL_CATALOG['together'])} available
  DeepInfra: {len(MODEL_CATALOG['deepinfra'])} available

Current Selection:
  Performer: {performer_provider}/{performer_model}
  Critic: {critic_provider}/{critic_model}
            """
            st.code(status_text.strip())
        
        # Return selections for use in main
        return {
            "performer_provider": performer_provider,
            "performer_model": performer_model,
            "critic_provider": critic_provider,
            "critic_model": critic_model,
        }


def display_header():
    """Display AI-themed hero header with futuristic design."""
    st.markdown("""
    <div class="hero-header">
        <div class="hero-title">🤖 AI Joke Agents Debate</div>
        <div class="hero-subtitle">
            Two AI agents collaborate to craft and refine humor through iterative evaluation. 
            Watch as the Performer creates and the Critic analyzes, forming a continuous improvement loop.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Info card explaining the system
    st.markdown("""
    <div class="info-card">
        <strong>💡 How This Works:</strong><br><br>
        <strong>🎭 Performer Agent</strong> → Generates creative, original jokes with high temperature (0.9)<br>
        <strong>🧠 Critic Agent</strong> → Provides structured feedback with analytical precision (temp: 0.3)<br>
        <strong>🔄 Iterative Refinement</strong> → Refine jokes through multiple cycles until perfect<br>
        <strong>🌐 Multi-LLM Support</strong> → Choose from 5 providers: OpenAI, Groq, HuggingFace, Together AI, DeepInfra
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables for history tracking."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "workflow_complete" not in st.session_state:
        st.session_state.workflow_complete = False
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    if "llm_config" not in st.session_state:
        st.session_state.llm_config = None


def show_diff_viewer(previous_joke: str, revised_joke: str, inside_expander: bool = False):
    """
    Display a side-by-side diff viewer for joke revisions with AI theme.
    
    Args:
        previous_joke: The original joke text
        revised_joke: The revised joke text
        inside_expander: Whether this is being called from within an expander (to avoid nesting)
    """
    st.markdown('<div class="diff-container">', unsafe_allow_html=True)
    st.markdown('<div class="diff-header">🔍 What Changed?</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Previous Version**")
        st.markdown(f'<div style="background: rgba(231, 76, 60, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #E74C3C; color: var(--text-light);">{previous_joke}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("**✨ Revised Version**")
        st.markdown(f'<div style="background: rgba(46, 204, 113, 0.1); padding: 15px; border-radius: 10px; border-left: 3px solid #2ECC71; color: var(--text-light);">{revised_joke}</div>', unsafe_allow_html=True)
    
    # Show text-level diff
    # Avoid nested expanders (Streamlit doesn't allow expander inside expander)
    if inside_expander:
        # Just show directly without another expander
        st.markdown("**📊 Detailed Changes:**")
        previous_words = previous_joke.split()
        revised_words = revised_joke.split()
        
        diff = difflib.unified_diff(
            previous_words,
            revised_words,
            lineterm='',
            n=0
        )
        
        diff_text = '\n'.join(diff)
        if diff_text:
            st.code(diff_text, language=None)
        else:
            st.info("No changes detected")
    else:
        # Use expander for latest cycle (not nested)
        with st.expander("📊 Detailed Changes"):
            previous_words = previous_joke.split()
            revised_words = revised_joke.split()
            
            diff = difflib.unified_diff(
                previous_words,
                revised_words,
                lineterm='',
                n=0
            )
            
            diff_text = '\n'.join(diff)
            if diff_text:
                st.code(diff_text, language=None)
            else:
                st.info("No changes detected")
    
    st.markdown('</div>', unsafe_allow_html=True)


def display_models_used(llm_config: Dict[str, str], cycle_num: int):
    """
    Display which models were used for a specific cycle.
    
    Args:
        llm_config: Dictionary containing provider and model information
        cycle_num: The cycle number
    """
    st.markdown('<div class="models-info">', unsafe_allow_html=True)
    st.markdown(f"""
    🧠 **Models Used in Cycle {cycle_num}:**
    - 🎭 Performer → `{llm_config['performer_provider']}/{llm_config['performer_model']}`
    - 🧐 Critic → `{llm_config['critic_provider']}/{llm_config['critic_model']}`
    """)
    st.markdown('</div>', unsafe_allow_html=True)


def display_cycle(cycle_data: dict, cycle_num: int, is_latest: bool = False, previous_joke: Optional[str] = None):
    """
    Display a single cycle of joke and evaluation with enhanced formatting.
    
    Args:
        cycle_data: Dictionary containing 'joke', 'feedback', and 'cycle_type'
        cycle_num: The cycle number (1, 2, 3, etc.)
        is_latest: Whether this is the most recent cycle
        previous_joke: Previous cycle's joke for diff viewer (if applicable)
    """
    cycle_type = cycle_data.get("cycle_type", "initial")
    
    # Create anchor for navigation
    st.markdown(f'<div id="cycle_{cycle_num}"></div>', unsafe_allow_html=True)
    
    # Determine the header based on cycle type
    if cycle_type == "initial":
        header_emoji = "🎬"
        header_text = f"Revision Cycle #{cycle_num} (Initial)"
    elif cycle_type == "revised":
        header_emoji = "✍️"
        header_text = f"Revision Cycle #{cycle_num} (Revised)"
    elif cycle_type == "reevaluated":
        header_emoji = "🔄"
        header_text = f"Revision Cycle #{cycle_num} (Re-evaluated)"
    else:
        header_emoji = "🔄"
        header_text = f"Revision Cycle #{cycle_num}"
    
    # For mobile responsiveness, use expanders for non-latest cycles
    if not is_latest:
        with st.expander(f"{header_emoji} {header_text}", expanded=False):
            display_cycle_content(cycle_data, cycle_num, is_latest, previous_joke)
    else:
        # Latest cycle displayed prominently
        st.markdown(f'<div class="cycle-header">{header_emoji} {header_text}</div>', unsafe_allow_html=True)
        display_cycle_content(cycle_data, cycle_num, is_latest, previous_joke)


def display_cycle_content(cycle_data: dict, cycle_num: int, is_latest: bool, previous_joke: Optional[str] = None):
    """Display the content of a cycle (joke + evaluation) with AI-themed styling."""
    cycle_type = cycle_data.get("cycle_type", "initial")
    
    # Wrap in glass card
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Display joke with agent badge
    st.markdown('<div class="agent-badge agent-badge-performer">🤖 Performer Agent</div>', unsafe_allow_html=True)
    st.markdown("### 😂 Generated Joke")
    st.markdown(f'<div class="joke-container">{cycle_data["joke"]}</div>', unsafe_allow_html=True)
    
    # Show diff viewer for revised jokes (cycle 2+)
    if cycle_num > 1 and cycle_type == "revised" and previous_joke and previous_joke != cycle_data["joke"]:
        # Pass inside_expander=True for non-latest cycles (which are wrapped in expanders)
        show_diff_viewer(previous_joke, cycle_data["joke"], inside_expander=not is_latest)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # Display evaluation
    if is_latest:
        display_evaluation_with_actions(cycle_data["feedback"], cycle_num)
    else:
        display_evaluation(cycle_data["feedback"], cycle_num)
    
    # Close glass card
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display models used
    if st.session_state.llm_config:
        display_models_used(st.session_state.llm_config, cycle_num)


def display_evaluation(feedback: dict, cycle_num: int):
    """Display evaluation without action buttons (for historical cycles) with AI theme."""
    # Agent badge
    st.markdown('<div class="agent-badge agent-badge-critic">🧠 Critic Agent</div>', unsafe_allow_html=True)
    st.markdown(f"### 🧐 Critical Analysis")
    st.markdown('<div class="eval-container">', unsafe_allow_html=True)
    
    # Score badge
    score = feedback["laughability_score"]
    st.markdown(f'<div class="score-badge">Laughability Score: {score}/100</div>', unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Visual indicator
        if score >= 80:
            st.success("🔥 Hilarious!")
        elif score >= 60:
            st.info("😄 Pretty funny!")
        elif score >= 40:
            st.warning("😐 Needs work")
        else:
            st.error("😬 Weak")
    
    with col2:
        st.markdown(f'<div class="eval-metric"><strong>Age Rating:</strong> {feedback["age_appropriateness"]}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="eval-metric"><strong>Status:</strong> ✅ Analyzed</div>', unsafe_allow_html=True)
    
    # Detailed feedback in structured format
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="eval-metric"><strong>💪 Strengths:</strong></div>', unsafe_allow_html=True)
        for strength in feedback["strengths"]:
            st.markdown(f"<div style='padding-left: 15px; color: #2ECC71;'>✓ {strength}</div>", unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown('<div class="eval-metric"><strong>⚠️ Weaknesses:</strong></div>', unsafe_allow_html=True)
        for weakness in feedback["weaknesses"]:
            st.markdown(f"<div style='padding-left: 15px; color: #E74C3C;'>✗ {weakness}</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="eval-metric"><strong>💡 Suggestions:</strong></div>', unsafe_allow_html=True)
        for suggestion in feedback["suggestions"]:
            st.markdown(f"<div style='padding-left: 15px; color: #4A90E2;'>→ {suggestion}</div>", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown(f'<div class="eval-metric"><strong>📝 Overall Verdict:</strong> {feedback["overall_verdict"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def display_evaluation_with_actions(feedback: dict, cycle_num: int):
    """Display evaluation with action buttons (for the latest cycle only) with AI theme."""
    # Agent badge
    st.markdown('<div class="agent-badge agent-badge-critic">🧠 Critic Agent</div>', unsafe_allow_html=True)
    st.markdown(f"### 🧐 Critical Analysis")
    st.markdown('<div class="eval-container">', unsafe_allow_html=True)
    
    # Score badge
    score = feedback["laughability_score"]
    st.markdown(f'<div class="score-badge">Laughability Score: {score}/100</div>', unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Visual indicator
        if score >= 80:
            st.success("🔥 Hilarious!")
        elif score >= 60:
            st.info("😄 Pretty funny!")
        elif score >= 40:
            st.warning("😐 Needs work")
        else:
            st.error("😬 Weak")
    
    with col2:
        st.markdown(f'<div class="eval-metric"><strong>Age Rating:</strong> {feedback["age_appropriateness"]}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="eval-metric"><strong>Status:</strong> ✅ Analyzed</div>', unsafe_allow_html=True)
    
    # Detailed feedback in structured format
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown('<div class="eval-metric"><strong>💪 Strengths:</strong></div>', unsafe_allow_html=True)
        for strength in feedback["strengths"]:
            st.markdown(f"<div style='padding-left: 15px; color: #2ECC71;'>✓ {strength}</div>", unsafe_allow_html=True)
        
        st.markdown("")
        st.markdown('<div class="eval-metric"><strong>⚠️ Weaknesses:</strong></div>', unsafe_allow_html=True)
        for weakness in feedback["weaknesses"]:
            st.markdown(f"<div style='padding-left: 15px; color: #E74C3C;'>✗ {weakness}</div>", unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="eval-metric"><strong>💡 Suggestions:</strong></div>', unsafe_allow_html=True)
        for suggestion in feedback["suggestions"]:
            st.markdown(f"<div style='padding-left: 15px; color: #4A90E2;'>→ {suggestion}</div>", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown(f'<div class="eval-metric"><strong>📝 Overall Verdict:</strong> {feedback["overall_verdict"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons section (if workflow not complete)
    if not st.session_state.workflow_complete:
        st.markdown('<div class="button-group">', unsafe_allow_html=True)
        st.markdown('<div style="text-align: center; margin-bottom: 15px;">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: var(--primary); margin: 0;">🎯 Next Action</h4>', unsafe_allow_html=True)
        st.markdown('<p style="color: var(--text-muted); font-size: 14px; margin: 5px 0 0 0;">Choose how to proceed with this joke</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            refine_button = st.button(
                "✍️ Revise Joke\n(Apply Feedback)",
                key=f"refine_{cycle_num}",
                help="Accept the evaluation and ask the Performer to revise the joke based on the Critic's feedback",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            reevaluate_button = st.button(
                "🔁 Re-Evaluate\nThis Joke",
                key=f"reevaluate_{cycle_num}",
                help="Keep the same joke but ask the Critic to provide fresh feedback with a different perspective",
                type="secondary",
                use_container_width=True
            )
        
        with col3:
            complete_button = st.button(
                "✔️ I'm All Set",
                key=f"complete_{cycle_num}",
                help="Finish the refinement process and mark the workflow as complete",
                use_container_width=True
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle button actions
        if refine_button:
            handle_refine_action()
        elif reevaluate_button:
            handle_reevaluate_action()
        elif complete_button:
            handle_complete_action()


def handle_refine_action():
    """Handle the 'Revise Joke (Apply Feedback)' button action with error handling."""
    if not st.session_state.history:
        st.error("❌ No history available to refine")
        return
    
    latest_cycle = st.session_state.history[-1]
    
    try:
        with st.spinner("🤖 Performer Agent is revising the joke based on feedback..."):
            # Get the workflow from session state
            workflow = st.session_state.workflow
            
            if not workflow:
                raise ValueError("Workflow not initialized. Please generate a new joke first.")
            
            # Revise the joke using the performer
            # revise_joke returns a string directly (the revised joke)
            revised_joke = workflow.revise_joke(
                latest_cycle["joke"],
                latest_cycle["feedback"]
            )
            
            if not revised_joke:
                raise ValueError("Failed to generate revised joke")
        
        # Evaluate the revised joke
        with st.spinner("🧠 Critic Agent is evaluating the revised joke..."):
            # evaluate_joke returns a dict directly (the feedback)
            new_feedback = workflow.evaluate_joke(revised_joke)
            
            if not new_feedback:
                raise ValueError("Failed to generate evaluation")
        
        # Add to history
        st.session_state.history.append({
            "joke": revised_joke,
            "feedback": new_feedback,
            "cycle_type": "revised",
            "previous_joke": latest_cycle["joke"]  # Store previous joke for diff
        })
        
        st.markdown('<div class="success-message">✅ Joke revised and re-evaluated successfully!</div>', unsafe_allow_html=True)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during revision: {str(e)}")
        st.warning("💡 Try switching providers or regenerating the joke. Some providers may have rate limits or temporary issues.")
        with st.expander("🔍 Error Details"):
            st.exception(e)


def handle_reevaluate_action():
    """Handle the 'Re-Evaluate This Joke' button action with error handling."""
    if not st.session_state.history:
        st.error("❌ No history available to re-evaluate")
        return
    
    latest_cycle = st.session_state.history[-1]
    
    try:
        with st.spinner("🧠 Critic Agent is running a new evaluation with fresh perspective..."):
            # Get the workflow from session state
            workflow = st.session_state.workflow
            
            if not workflow:
                raise ValueError("Workflow not initialized. Please generate a new joke first.")
            
            # Re-evaluate the same joke
            # reevaluate_joke returns a dict directly (the feedback)
            new_feedback = workflow.reevaluate_joke(latest_cycle["joke"])
            
            if not new_feedback:
                raise ValueError("Failed to generate new evaluation")
        
        # Add to history with same joke but new feedback
        st.session_state.history.append({
            "joke": latest_cycle["joke"],
            "feedback": new_feedback,
            "cycle_type": "reevaluated"
        })
        
        st.markdown('<div class="success-message">✅ Joke re-evaluated with fresh perspective!</div>', unsafe_allow_html=True)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during re-evaluation: {str(e)}")
        st.warning("💡 Try switching providers or regenerating the joke. Some providers may have rate limits or temporary issues.")
        with st.expander("🔍 Error Details"):
            st.exception(e)


def handle_complete_action():
    """Handle the 'I'm All Set' button action."""
    st.session_state.workflow_complete = True
    st.markdown('<div class="success-message">🎉 Workflow complete! Your joke has been refined to perfection!</div>', unsafe_allow_html=True)
    st.balloons()
    st.rerun()


def main():
    """Main Streamlit application with enhanced UX and error handling."""
    
    # Initialize session state
    initialize_session_state()
    
    # Get LLM selections from sidebar
    llm_config = display_sidebar()
    display_header()
    
    # Check for API keys based on selected providers
    try:
        # Check if required API keys are present for selected providers
        if llm_config["performer_provider"] == "openai" or llm_config["critic_provider"] == "openai":
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        
        if llm_config["performer_provider"] == "groq" or llm_config["critic_provider"] == "groq":
            if not settings.groq_api_key:
                raise ValueError("GROQ_API_KEY is required when using Groq provider")
        
        if llm_config["performer_provider"] == "huggingface" or llm_config["critic_provider"] == "huggingface":
            if not settings.huggingface_api_key:
                raise ValueError("HUGGINGFACE_API_KEY is required when using HuggingFace provider")
        
        if llm_config["performer_provider"] == "together" or llm_config["critic_provider"] == "together":
            if not settings.together_api_key:
                raise ValueError("TOGETHER_API_KEY is required when using Together AI provider")
        
        if llm_config["performer_provider"] == "deepinfra" or llm_config["critic_provider"] == "deepinfra":
            if not settings.deepinfra_api_key:
                raise ValueError("DEEPINFRA_API_KEY is required when using DeepInfra provider")
                
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        st.info("Please set the required API keys in your `.env` file or Streamlit Cloud secrets.")
        st.stop()
    
    # Input section with AI-themed styling
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🎯 Generate a New Joke")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_input(
            "Topic or Theme:",
            placeholder="e.g., programming, artificial intelligence, robots, etc.",
            help="What should the AI agents create a joke about?",
            key="joke_prompt",
            label_visibility="collapsed"
        )
    
    with col2:
        generate_button = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Generate joke on button click
    if generate_button:
        if not prompt:
            st.warning("⚠️ Please enter a topic first!")
        else:
            # Reset history for new joke
            st.session_state.history = []
            st.session_state.workflow_complete = False
            
            try:
                with st.spinner(f"🤖 Performer Agent is crafting a joke about '{prompt}'..."):
                    # Initialize workflow with runtime-selected LLMs
                    performer_llm = get_performer_llm(
                        provider=llm_config["performer_provider"],
                        model=llm_config["performer_model"]
                    )
                    critic_llm = get_critic_llm(
                        provider=llm_config["critic_provider"],
                        model=llm_config["critic_model"]
                    )
                    workflow = JokeWorkflow(performer_llm, critic_llm)
                    
                    # Store workflow in session state for later use
                    st.session_state.workflow = workflow
                    st.session_state.llm_config = llm_config
                    
                    # Run the workflow
                    result = workflow.run(prompt)
                
                # Evaluate the joke
                with st.spinner("🧠 Critic Agent is analyzing the joke..."):
                    # Add initial result to history
                    st.session_state.history.append({
                        "joke": result["joke"],
                        "feedback": result["feedback"],
                        "cycle_type": "initial"
                    })
                
                # Display success
                st.markdown('<div class="success-message">✅ Joke generated and evaluated successfully!</div>', unsafe_allow_html=True)
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating joke: {str(e)}")
                st.warning("💡 Try switching to a different provider or model. Some providers may have rate limits or temporary issues.")
                with st.expander("🔍 Error Details"):
                    st.exception(e)
    
    # Display history if it exists
    if st.session_state.history:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown('<h2 style="color: var(--primary); font-size: 28px; font-weight: 700;">📚 Refinement History</h2>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: var(--text-muted); font-size: 14px;">Total iterations: <strong>{len(st.session_state.history)}</strong></p>', unsafe_allow_html=True)
        
        # Display all cycles
        for idx, cycle_data in enumerate(st.session_state.history):
            cycle_num = idx + 1
            is_latest = (idx == len(st.session_state.history) - 1)
            
            # Get previous joke for diff viewer
            previous_joke = None
            if idx > 0:
                previous_joke = st.session_state.history[idx - 1]["joke"]
            
            display_cycle(cycle_data, cycle_num, is_latest, previous_joke)
            
            # Add gradient separator between cycles (except after the last one)
            if not is_latest:
                st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        
        # Show completion message if workflow is complete
        if st.session_state.workflow_complete:
            st.markdown("""
            <div class="success-message" style="text-align: center; padding: 25px;">
                <h3 style="color: #2ECC71; margin: 0;">🎉 Refinement Complete!</h3>
                <p style="margin-top: 10px; color: var(--text-light);">Your joke has been perfected through collaborative AI analysis.</p>
                <p style="color: var(--text-muted); font-size: 14px;">Generate a new joke above to start another refinement cycle.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # LangSmith trace info
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        if settings.langchain_tracing_v2 == "true":
            st.markdown("""
            <div class="info-card" style="text-align: center;">
                🔍 <strong>LangSmith Observability Active</strong><br>
                <span style="font-size: 14px; color: var(--text-muted);">All AI interactions are being traced for analysis and debugging</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Reset button
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 2])
        with col_reset1:
            if st.button("🔄 Start Over", help="Clear history and start fresh", use_container_width=True, type="secondary"):
                st.session_state.history = []
                st.session_state.workflow_complete = False
                st.session_state.workflow = None
                st.rerun()
    
    # Example prompts with AI-themed styling
    if not st.session_state.history:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💡 Need Inspiration?")
        st.caption("Try one of these AI-themed topics")
        
        example_prompts = [
            "🤖 artificial intelligence",
            "💻 programming bugs",
            "☕ coffee addiction",
            "🏠 working from home",
            "🐱 cats vs dogs",
            "👨 dad jokes",
            "⚛️ quantum physics",
            "📱 social media"
        ]
        
        cols = st.columns(4)
        for idx, example in enumerate(example_prompts):
            with cols[idx % 4]:
                if st.button(example, key=f"example_{idx}", use_container_width=True):
                    # Remove emoji from the prompt value
                    clean_prompt = example.split(" ", 1)[1]
                    
                    # Directly generate joke for this topic
                    st.session_state.history = []
                    st.session_state.workflow_complete = False
                    
                    try:
                        with st.spinner(f"🤖 Performer Agent is crafting a joke about '{clean_prompt}'..."):
                            # Initialize workflow with runtime-selected LLMs
                            performer_llm = get_performer_llm(
                                provider=llm_config["performer_provider"],
                                model=llm_config["performer_model"]
                            )
                            critic_llm = get_critic_llm(
                                provider=llm_config["critic_provider"],
                                model=llm_config["critic_model"]
                            )
                            workflow = JokeWorkflow(performer_llm, critic_llm)
                            
                            # Store workflow in session state for later use
                            st.session_state.workflow = workflow
                            st.session_state.llm_config = llm_config
                            
                            # Run the workflow
                            result = workflow.run(clean_prompt)
                        
                        # Evaluate the joke
                        with st.spinner("🧠 Critic Agent is analyzing the joke..."):
                            # Add initial result to history
                            st.session_state.history.append({
                                "joke": result["joke"],
                                "feedback": result["feedback"],
                                "cycle_type": "initial"
                            })
                        
                        # Display success
                        st.markdown('<div class="success-message">✅ Joke generated and evaluated successfully!</div>', unsafe_allow_html=True)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error generating joke: {str(e)}")
                        st.warning("💡 Try switching to a different provider or model. Some providers may have rate limits or temporary issues.")
                        with st.expander("🔍 Error Details"):
                            st.exception(e)
        
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
