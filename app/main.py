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


# Custom CSS for better styling
st.markdown("""
<style>
    /* Joke container styling */
    .joke-container {
        background-color: #e3f2fd;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2196f3;
        margin: 10px 0;
    }
    
    /* Evaluation container styling */
    .eval-container {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    /* Cycle header styling */
    .cycle-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 20px 0 10px 0;
        font-weight: bold;
    }
    
    /* Button group styling */
    .button-group {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border: 2px dashed #ff9800;
    }
    
    /* Diff viewer styling */
    .diff-container {
        background-color: #fff8e1;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    /* Models info styling */
    .models-info {
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 8px;
        font-size: 0.9em;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def display_sidebar():
    """Display configuration sidebar with dynamic model fetching and iteration navigation."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Iterations Navigator (if history exists)
        if "history" in st.session_state and st.session_state.history:
            st.divider()
            st.subheader("📍 Iterations")
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
                
                # Create anchor link
                if st.button(f"{emoji} {label}", key=f"nav_{cycle_num}", use_container_width=True):
                    # Use Streamlit's experimental feature to scroll
                    st.session_state[f"scroll_to_cycle_{cycle_num}"] = True
                    st.rerun()
            
            st.divider()
        
        st.subheader("🎭 Performer Agent LLM")
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
        
        st.divider()
        
        st.subheader("🧐 Critic Agent LLM")
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
        
        st.divider()
        
        st.subheader("📊 LangSmith")
        st.markdown(f"**Project:** `{settings.langchain_project}`")
        st.markdown(f"**Tracing:** {'✅ Enabled' if settings.langchain_tracing_v2 == 'true' else '❌ Disabled'}")
        
        if settings.langchain_tracing_v2 == "true":
            st.info("🔍 All runs are being traced to LangSmith")
            st.markdown(
                f"[View in LangSmith →]({settings.langchain_endpoint})"
            )
        
        st.divider()
        
        st.subheader("ℹ️ About")
        st.markdown("""
        **Multi-Agent Joke System**
        
        A POC demonstrating:
        - 🎭 Performer Agent (creative)
        - 🧐 Critic Agent (analytical)
        - 🔄 LangGraph workflow
        - 📈 LangSmith tracing
        - 🔧 Runtime LLM selection
        - 🆓 5 LLM providers (3 free!)
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
    """Display main header with explanation card."""
    st.title("🎭 Multi-Agent Joke System")
    
    # Explanation card
    st.success("""
    💡 **How this app works:**
    
    This app uses two AI agents — a **Performer** that writes jokes and a **Critic** that evaluates them. 
    You can refine the joke multiple times using the action buttons below each evaluation.
    
    🎭 **Performer Agent** → Generates creative, original jokes  
    🧐 **Critic Agent** → Provides structured feedback with metrics  
    🔄 **Iterative Refinement** → Improve your joke through multiple cycles
    """)
    
    st.divider()


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


def show_diff_viewer(previous_joke: str, revised_joke: str):
    """
    Display a side-by-side diff viewer for joke revisions.
    
    Args:
        previous_joke: The original joke text
        revised_joke: The revised joke text
    """
    st.markdown('<div class="diff-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 What Changed?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Previous Joke**")
        st.markdown(f"> {previous_joke}")
    
    with col2:
        st.markdown("**✍️ Revised Joke**")
        st.markdown(f"> {revised_joke}")
    
    # Show text-level diff
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
    """Display the content of a cycle (joke + evaluation)."""
    cycle_type = cycle_data.get("cycle_type", "initial")
    
    # Display joke
    st.markdown("### 📝 Joke")
    st.markdown(f'<div class="joke-container">{cycle_data["joke"]}</div>', unsafe_allow_html=True)
    
    # Show diff viewer for revised jokes (cycle 2+)
    if cycle_num > 1 and cycle_type == "revised" and previous_joke and previous_joke != cycle_data["joke"]:
        show_diff_viewer(previous_joke, cycle_data["joke"])
    
    st.markdown("---")
    
    # Display evaluation
    if is_latest:
        display_evaluation_with_actions(cycle_data["feedback"], cycle_num)
    else:
        display_evaluation(cycle_data["feedback"], cycle_num)
    
    # Display models used
    if st.session_state.llm_config:
        display_models_used(st.session_state.llm_config, cycle_num)


def display_evaluation(feedback: dict, cycle_num: int):
    """Display evaluation without action buttons (for historical cycles)."""
    st.markdown(f"### 🧐 Critic's Evaluation")
    st.markdown('<div class="eval-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = feedback["laughability_score"]
        st.metric("Laughability Score", f"{score}/100")
        
        # Visual indicator
        if score >= 80:
            st.success("🔥 Hilarious!")
        elif score >= 60:
            st.info("😄 Pretty funny!")
        elif score >= 40:
            st.warning("😐 Meh...")
        else:
            st.error("😬 Needs work")
    
    with col2:
        st.metric("Age Appropriateness", feedback["age_appropriateness"])
    
    with col3:
        st.metric("Status", "✅ Evaluated")
    
    # Detailed feedback in two columns
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**💪 Strengths:**")
        for strength in feedback["strengths"]:
            st.markdown(f"- {strength}")
        
        st.markdown("**⚠️ Weaknesses:**")
        for weakness in feedback["weaknesses"]:
            st.markdown(f"- {weakness}")
    
    with col_right:
        st.markdown("**💡 Suggestions:**")
        for suggestion in feedback["suggestions"]:
            st.markdown(f"- {suggestion}")
    
    st.markdown(f"**📝 Overall Verdict:** {feedback['overall_verdict']}")
    st.markdown('</div>', unsafe_allow_html=True)


def display_evaluation_with_actions(feedback: dict, cycle_num: int):
    """Display evaluation with action buttons (for the latest cycle only)."""
    st.markdown(f"### 🧐 Critic's Evaluation")
    st.markdown('<div class="eval-container">', unsafe_allow_html=True)
    
    # Display metrics first
    col1, col2, col3 = st.columns(3)
    
    with col1:
        score = feedback["laughability_score"]
        st.metric("Laughability Score", f"{score}/100")
        
        # Visual indicator
        if score >= 80:
            st.success("🔥 Hilarious!")
        elif score >= 60:
            st.info("😄 Pretty funny!")
        elif score >= 40:
            st.warning("😐 Meh...")
        else:
            st.error("😬 Needs work")
    
    with col2:
        st.metric("Age Appropriateness", feedback["age_appropriateness"])
    
    with col3:
        st.metric("Status", "✅ Evaluated")
    
    # Detailed feedback in two columns
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**💪 Strengths:**")
        for strength in feedback["strengths"]:
            st.markdown(f"- {strength}")
        
        st.markdown("**⚠️ Weaknesses:**")
        for weakness in feedback["weaknesses"]:
            st.markdown(f"- {weakness}")
    
    with col_right:
        st.markdown("**💡 Suggestions:**")
        for suggestion in feedback["suggestions"]:
            st.markdown(f"- {suggestion}")
    
    st.markdown(f"**📝 Overall Verdict:** {feedback['overall_verdict']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Action buttons section (if workflow not complete)
    if not st.session_state.workflow_complete:
        st.markdown('<div class="button-group">', unsafe_allow_html=True)
        st.markdown("#### 🎯 What would you like to do next?")
        st.caption("Choose an action below to continue refining your joke")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            refine_button = st.button(
                "✅ Revise Joke\n(Apply Feedback)",
                key=f"refine_{cycle_num}",
                help="Accept the evaluation and ask the Performer to revise the joke based on the Critic's feedback",
                type="primary",
                use_container_width=True
            )
        
        with col2:
            reevaluate_button = st.button(
                "❌ Re-Evaluate\nThis Joke",
                key=f"reevaluate_{cycle_num}",
                help="Keep the same joke but ask the Critic to provide fresh feedback with a different perspective",
                type="secondary",
                use_container_width=True
            )
        
        with col3:
            complete_button = st.button(
                "🎉 I'm All Set",
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
        with st.spinner("✍️ Performer is revising the joke based on feedback..."):
            # Get the workflow from session state
            workflow = st.session_state.workflow
            
            if not workflow:
                raise ValueError("Workflow not initialized. Please generate a new joke first.")
            
            # Revise the joke using the performer
            revised_result = workflow.revise_joke(
                latest_cycle["joke"],
                latest_cycle["feedback"]
            )
            
            # Extract the revised joke
            revised_joke = revised_result.get("joke", "")
            
            if not revised_joke:
                raise ValueError("Failed to generate revised joke")
        
        # Evaluate the revised joke
        with st.spinner("🧐 Critic is evaluating the revised joke..."):
            new_feedback_result = workflow.evaluate_joke(revised_joke)
            new_feedback = new_feedback_result.get("feedback", {})
            
            if not new_feedback:
                raise ValueError("Failed to generate evaluation")
        
        # Add to history
        st.session_state.history.append({
            "joke": revised_joke,
            "feedback": new_feedback,
            "cycle_type": "revised"
        })
        
        st.success("✅ Joke revised and re-evaluated successfully!")
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
        with st.spinner("🔄 Critic is running a new evaluation..."):
            # Get the workflow from session state
            workflow = st.session_state.workflow
            
            if not workflow:
                raise ValueError("Workflow not initialized. Please generate a new joke first.")
            
            # Re-evaluate the same joke
            new_feedback_result = workflow.reevaluate_joke(latest_cycle["joke"])
            new_feedback = new_feedback_result.get("feedback", {})
            
            if not new_feedback:
                raise ValueError("Failed to generate new evaluation")
        
        # Add to history with same joke but new feedback
        st.session_state.history.append({
            "joke": latest_cycle["joke"],
            "feedback": new_feedback,
            "cycle_type": "reevaluated"
        })
        
        st.success("✅ Joke re-evaluated with fresh perspective!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error during re-evaluation: {str(e)}")
        st.warning("💡 Try switching providers or regenerating the joke. Some providers may have rate limits or temporary issues.")
        with st.expander("🔍 Error Details"):
            st.exception(e)


def handle_complete_action():
    """Handle the 'I'm All Set' button action."""
    st.session_state.workflow_complete = True
    st.success("🎉 Workflow complete! Great job refining your joke!")
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
    
    # Input section
    st.subheader("🎯 Generate a Joke")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_input(
            "Enter a topic or theme:",
            placeholder="e.g., programming, cats, coffee, etc.",
            help="What should the joke be about?",
            key="joke_prompt"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        generate_button = st.button("🎭 Generate Joke", type="primary", use_container_width=True)
    
    # Generate joke on button click
    if generate_button:
        if not prompt:
            st.warning("⚠️ Please enter a topic first!")
        else:
            # Reset history for new joke
            st.session_state.history = []
            st.session_state.workflow_complete = False
            
            try:
                with st.spinner(f"🎭 Performer is writing a new joke about '{prompt}'..."):
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
                with st.spinner("🧐 Critic is evaluating the joke..."):
                    # Add initial result to history
                    st.session_state.history.append({
                        "joke": result["joke"],
                        "feedback": result["feedback"],
                        "cycle_type": "initial"
                    })
                
                # Display success
                st.success("✅ Joke generated and evaluated successfully!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error generating joke: {str(e)}")
                st.warning("💡 Try switching to a different provider or model. Some providers may have rate limits or temporary issues.")
                with st.expander("🔍 Error Details"):
                    st.exception(e)
    
    # Display history if it exists
    if st.session_state.history:
        st.divider()
        st.markdown("## 📚 Refinement History")
        st.caption(f"Total cycles: {len(st.session_state.history)}")
        
        # Display all cycles
        for idx, cycle_data in enumerate(st.session_state.history):
            cycle_num = idx + 1
            is_latest = (idx == len(st.session_state.history) - 1)
            
            # Get previous joke for diff viewer
            previous_joke = None
            if idx > 0:
                previous_joke = st.session_state.history[idx - 1]["joke"]
            
            display_cycle(cycle_data, cycle_num, is_latest, previous_joke)
            
            # Add separator between cycles (except after the last one)
            if not is_latest:
                st.markdown("---")
        
        # Show completion message if workflow is complete
        if st.session_state.workflow_complete:
            st.success("🎉 Workflow complete! You can generate a new joke above.")
            st.info("📊 **Final Result:** Check the cycle history above to see how your joke evolved!")
        
        # LangSmith trace info
        st.divider()
        if settings.langchain_tracing_v2 == "true":
            st.info("🔍 All interactions are traced in LangSmith. Check your project dashboard for detailed execution traces.")
        
        # Reset button
        col_reset1, col_reset2, col_reset3 = st.columns([1, 1, 2])
        with col_reset1:
            if st.button("🔄 Start Over", help="Clear history and start fresh", use_container_width=True):
                st.session_state.history = []
                st.session_state.workflow_complete = False
                st.session_state.workflow = None
                st.rerun()
    
    # Example prompts
    if not st.session_state.history:
        with st.expander("💡 Need inspiration? Try these topics:"):
            example_prompts = [
                "artificial intelligence",
                "working from home",
                "coffee addiction",
                "cats vs dogs",
                "programming bugs",
                "dad jokes",
                "quantum physics",
                "social media"
            ]
            
            cols = st.columns(4)
            for idx, example in enumerate(example_prompts):
                with cols[idx % 4]:
                    if st.button(example, key=f"example_{idx}", use_container_width=True):
                        st.session_state["joke_prompt"] = example
                        st.rerun()


if __name__ == "__main__":
    main()
