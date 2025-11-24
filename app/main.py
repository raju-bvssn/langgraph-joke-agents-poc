"""
Streamlit UI for the Multi-Agent Joke System.
Provides an interactive interface to generate and evaluate jokes.
"""
import streamlit as st
import os
import sys
from pathlib import Path

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


def display_sidebar():
    """Display configuration sidebar with dynamic model fetching."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        st.subheader("🎭 Performer Agent LLM")
        performer_provider = st.selectbox(
            "Provider",
            list(MODEL_CATALOG.keys()),
            key="performer_provider",
            help="Select LLM provider for joke generation"
        )
        
        # Get models based on provider (dynamic for OpenAI, static for Groq)
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
        
        # Get models based on provider (dynamic for OpenAI, static for Groq)
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
    """Display main header."""
    st.title("🎭 Multi-Agent Joke System")
    st.markdown("""
    Welcome to the **Joke Agent POC**! This system uses two AI agents:
    - **🎭 Performer**: Generates creative jokes
    - **🧐 Critic**: Evaluates jokes with structured feedback
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


def display_cycle(cycle_data: dict, cycle_num: int, is_latest: bool = False):
    """
    Display a single cycle of joke and evaluation.
    
    Args:
        cycle_data: Dictionary containing 'joke', 'feedback', and 'cycle_type'
        cycle_num: The cycle number (1, 2, 3, etc.)
        is_latest: Whether this is the most recent cycle
    """
    cycle_type = cycle_data.get("cycle_type", "initial")
    
    # Determine the title based on cycle type
    if cycle_type == "initial":
        joke_title = f"📝 Generated Joke (Cycle {cycle_num})"
    elif cycle_type == "revised":
        joke_title = f"📝 Revised Joke (Cycle {cycle_num})"
    elif cycle_type == "reevaluated":
        joke_title = f"📝 Same Joke (Cycle {cycle_num})"
    else:
        joke_title = f"📝 Joke (Cycle {cycle_num})"
    
    # Create an expander for non-latest cycles to keep UI clean
    if is_latest:
        # Display latest cycle directly
        st.markdown(f"### {joke_title}")
        st.info(cycle_data["joke"])
        
        st.divider()
        
        # Display feedback with action buttons
        display_evaluation_with_actions(cycle_data["feedback"], cycle_num, is_latest)
    else:
        # Use expander for historical cycles
        with st.expander(f"🔽 {joke_title}", expanded=False):
            st.info(cycle_data["joke"])
            st.markdown("---")
            display_evaluation(cycle_data["feedback"], cycle_num)


def display_evaluation(feedback: dict, cycle_num: int):
    """Display evaluation without action buttons (for historical cycles)."""
    st.markdown(f"### 🧐 Critic's Evaluation (Cycle {cycle_num})")
    
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
        st.metric("Status", "✅ Complete")
    
    # Detailed feedback
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


def display_evaluation_with_actions(feedback: dict, cycle_num: int, is_latest: bool):
    """Display evaluation with action buttons (for the latest cycle only)."""
    # Header with action buttons
    col_header, col_btn1, col_btn2, col_btn3 = st.columns([3, 1, 1, 1])
    
    with col_header:
        st.markdown(f"### 🧐 Critic's Evaluation (Cycle {cycle_num})")
    
    # Only show buttons if workflow is not complete
    if not st.session_state.workflow_complete:
        with col_btn1:
            refine_button = st.button(
                "✅ Refine Joke",
                key=f"refine_{cycle_num}",
                help="Accept evaluation and revise joke based on feedback",
                type="secondary"
            )
        
        with col_btn2:
            reevaluate_button = st.button(
                "❌ Re-evaluate",
                key=f"reevaluate_{cycle_num}",
                help="Reject evaluation and get fresh feedback",
                type="secondary"
            )
        
        with col_btn3:
            complete_button = st.button(
                "🎉 I'm all set",
                key=f"complete_{cycle_num}",
                help="Finish refinement process",
                type="primary"
            )
    
    # Display metrics
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
        st.metric("Status", "✅ Complete")
    
    # Detailed feedback
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
    
    # Handle button actions
    if not st.session_state.workflow_complete:
        if 'refine_button' in locals() and refine_button:
            handle_refine_action()
        elif 'reevaluate_button' in locals() and reevaluate_button:
            handle_reevaluate_action()
        elif 'complete_button' in locals() and complete_button:
            handle_complete_action()


def handle_refine_action():
    """Handle the 'Refine Joke' button action."""
    if not st.session_state.history:
        return
    
    latest_cycle = st.session_state.history[-1]
    
    with st.spinner("🎭 Performer is revising the joke..."):
        try:
            # Get the workflow from session state
            workflow = st.session_state.workflow
            
            # Revise the joke using the performer
            revised_joke = workflow.revise_joke(
                latest_cycle["joke"],
                latest_cycle["feedback"]
            )
            
            # Evaluate the revised joke
            with st.spinner("🧐 Critic is evaluating the revised joke..."):
                new_feedback = workflow.evaluate_joke(revised_joke)
            
            # Add to history
            st.session_state.history.append({
                "joke": revised_joke,
                "feedback": new_feedback,
                "cycle_type": "revised"
            })
            
            st.success("✅ Joke revised and re-evaluated!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during revision: {str(e)}")
            st.exception(e)


def handle_reevaluate_action():
    """Handle the 'Re-evaluate' button action."""
    if not st.session_state.history:
        return
    
    latest_cycle = st.session_state.history[-1]
    
    with st.spinner("🧐 Critic is re-evaluating the joke..."):
        try:
            # Get the workflow from session state
            workflow = st.session_state.workflow
            
            # Re-evaluate the same joke
            new_feedback = workflow.reevaluate_joke(latest_cycle["joke"])
            
            # Add to history with same joke but new feedback
            st.session_state.history.append({
                "joke": latest_cycle["joke"],
                "feedback": new_feedback,
                "cycle_type": "reevaluated"
            })
            
            st.success("✅ Joke re-evaluated!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error during re-evaluation: {str(e)}")
            st.exception(e)


def handle_complete_action():
    """Handle the 'I'm all set' button action."""
    st.session_state.workflow_complete = True
    st.success("🎉 Workflow complete! Great job refining your joke!")
    st.balloons()
    st.rerun()


def main():
    """Main Streamlit application with iterative refinement loop."""
    
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
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        st.info("Please set the required API keys in your `.env` file.")
        st.stop()
    
    # Input section
    st.subheader("🎯 Generate a Joke")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_input(
            "Enter a topic or theme:",
            placeholder="e.g., programming, cats, coffee, etc.",
            help="What should the joke be about?"
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
            
            with st.spinner(f"🎭 Performer ({llm_config['performer_provider']}/{llm_config['performer_model']}) is creating a joke..."):
                try:
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
                    
                    # Add initial result to history
                    st.session_state.history.append({
                        "joke": result["joke"],
                        "feedback": result["feedback"],
                        "cycle_type": "initial"
                    })
                    
                    # Display results
                    st.success("✅ Joke generated and evaluated!")
                    
                    # Show which models were used
                    st.info(f"🎭 Performer: {llm_config['performer_provider']}/{llm_config['performer_model']} | "
                           f"🧐 Critic: {llm_config['critic_provider']}/{llm_config['critic_model']}")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
    
    # Display history if it exists
    if st.session_state.history:
        st.divider()
        st.markdown("## 📚 Refinement History")
        
        # Display LLM configuration
        if st.session_state.llm_config:
            llm_cfg = st.session_state.llm_config
            st.info(f"🎭 Performer: {llm_cfg['performer_provider']}/{llm_cfg['performer_model']} | "
                   f"🧐 Critic: {llm_cfg['critic_provider']}/{llm_cfg['critic_model']}")
        
        # Display all cycles
        for idx, cycle_data in enumerate(st.session_state.history):
            cycle_num = idx + 1
            is_latest = (idx == len(st.session_state.history) - 1)
            
            display_cycle(cycle_data, cycle_num, is_latest)
            
            # Add separator between cycles (except after the last one)
            if not is_latest:
                st.markdown("---")
        
        # Show completion message if workflow is complete
        if st.session_state.workflow_complete:
            st.success("🎉 Workflow complete! You can generate a new joke above.")
        
        # LangSmith trace info
        st.divider()
        st.info("🔍 All interactions are traced in LangSmith. Check your project dashboard for details.")
        
        # Reset button
        if st.button("🔄 Start Over", help="Clear history and start fresh"):
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
                    if st.button(example, key=f"example_{idx}"):
                        st.rerun()


if __name__ == "__main__":
    main()

