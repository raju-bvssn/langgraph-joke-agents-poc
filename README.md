# 🎭 LangGraph Joke Agents POC

A complete proof-of-concept demonstrating a **multi-agent system** using **LangGraph**, **LangChain**, and **LangSmith**. This project showcases how two AI agents collaborate to generate and evaluate jokes with full observability.

## 🎯 Overview

This POC implements a simple but complete multi-agent workflow:

1. **🎭 Performer Agent**: Generates creative, original jokes based on user prompts
2. **🧐 Critic Agent**: Evaluates jokes with structured metrics and actionable feedback
3. **🔄 LangGraph Workflow**: Orchestrates agent collaboration with state management
4. **📊 LangSmith Integration**: Full tracing and observability for all agent interactions

## ✨ Features

- ✅ **Complete Multi-Agent System** with state passing
- ✅ **Structured Output** using Pydantic models
- ✅ **LangSmith Tracing** for full observability
- ✅ **Interactive Streamlit UI**
- ✅ **Multiple LLM Providers** (OpenAI and Groq)
- ✅ **Runtime LLM Selection** - Choose different models for each agent
- ✅ **Production-Ready Architecture** with proper separation of concerns
- ✅ **Updated 2025 Models** - Only currently supported, non-deprecated models
- ✅ **Comprehensive Testing** - Automated validation of all model combinations

## 📊 Agent Metrics

The **Critic Agent** evaluates jokes using:

- **Laughability Score** (0-100%): Quantitative humor rating
- **Age Appropriateness** (Child/Teen/Adult): Content maturity classification
- **Strengths**: What works well in the joke
- **Weaknesses**: Areas needing improvement
- **Suggestions**: Actionable recommendations for refinement
- **Overall Verdict**: Summary assessment

## 🔁 Iterative Refinement Loop

**NEW**: The system now supports user-driven iterative refinement! After generating a joke and receiving an evaluation, you have three options to improve your joke:

### Three Action Buttons

After each evaluation, you'll see three buttons next to "Critic's Evaluation":

1. **✅ Refine Joke** (Green Check)
   - **What it does**: Accepts the evaluation and asks the Performer to revise the joke based on the Critic's feedback
   - **When to use**: When the feedback is helpful and you want to improve the joke
   - **Result**: A revised joke is generated and automatically re-evaluated
   - **Example**: Original score 65/100 → Performer revises → New score 75/100

2. **❌ Re-evaluate** (Red Cross)
   - **What it does**: Rejects the current evaluation and asks the Critic for fresh feedback on the same joke
   - **When to use**: When you disagree with the evaluation or want a different perspective
   - **Result**: The same joke gets a fresh evaluation
   - **Example**: Same joke → Fresh evaluation with different insights

3. **🎉 I'm all set** (Completion)
   - **What it does**: Stops the refinement process and marks the workflow as complete
   - **When to use**: When you're satisfied with the current joke and evaluation
   - **Result**: No more iterations; workflow is finalized

### Refinement History

All iterations are preserved and displayed chronologically:

```
📝 Generated Joke (Cycle 1)
🧐 Critic's Evaluation (Cycle 1)
  ✅ Refine Joke | ❌ Re-evaluate | 🎉 I'm all set

---

📝 Revised Joke (Cycle 2)
🧐 Critic's Evaluation (Cycle 2)
  ✅ Refine Joke | ❌ Re-evaluate | 🎉 I'm all set

---

📝 Revised Joke (Cycle 3)
🧐 Critic's Evaluation (Cycle 3)
  ✅ Refine Joke | ❌ Re-evaluate | 🎉 I'm all set

[Click "I'm all set" to complete]
```

### Example Refinement Timeline

Here's a real example of how iterative refinement works:

**Cycle 1 (Initial):**
- **Joke**: "Why did the programmer quit? Because they didn't get arrays!"
- **Score**: 65/100
- **Weaknesses**: Predictable punchline
- **Action**: User clicks "✅ Refine Joke"

**Cycle 2 (Revised):**
- **Joke**: "Why did the programmer quit? Because they couldn't C their future!"
- **Score**: 75/100
- **Improvements**: Better wordplay with C language pun
- **Action**: User clicks "❌ Re-evaluate" to get a different perspective

**Cycle 3 (Re-evaluated):**
- **Joke**: (Same as Cycle 2)
- **Score**: 78/100
- **New insights**: "On second thought, the visual pun works really well"
- **Action**: User clicks "🎉 I'm all set"

**Result**: Joke improved from 65 to 78 through 3 refinement cycles!

### Features

- ✅ **Unlimited Iterations**: Refine as many times as you want
- ✅ **Complete History**: All cycles preserved and viewable
- ✅ **LangSmith Tracing**: Every iteration is traced
- ✅ **No Data Loss**: Original joke and all revisions kept
- ✅ **User Control**: You decide when to stop
- ✅ **Collapsible History**: Previous cycles in expandable sections

## 🏗️ Project Structure

```
langgraph-joke-agents-poc/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── performer.py       # Joke generation agent
│   │   └── critic.py          # Joke evaluation agent
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py        # LangGraph workflow orchestration
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm.py            # LLM configuration & provider setup
│   │   └── settings.py       # Environment settings
│   ├── __init__.py
│   └── main.py               # Streamlit UI (primary application)
├── main.py                   # Root entry point (for deployment)
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- OpenAI API key OR Groq API key
- LangSmith API key (for tracing)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd langgraph-joke-agents-poc

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required: Choose one LLM provider
OPENAI_API_KEY=sk-your-openai-key-here
# OR
GROQ_API_KEY=gsk-your-groq-key-here

# Required: LangSmith for tracing
LANGCHAIN_API_KEY=ls-your-langsmith-key-here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_TRACING_V2=true

# Optional: Choose provider (default: openai)
LLM_PROVIDER=openai
```

### 4. Run the Application

**Option 1: Root-level entry point (recommended for deployment)**
```bash
streamlit run main.py
```

**Option 2: Direct app entry point (for local development)**
```bash
streamlit run app/main.py
```

Both commands are equivalent. The application will open in your browser at `http://localhost:8501`

## 🎮 Usage

1. **Enter a topic** in the input field (e.g., "programming", "cats", "coffee")
2. **Click "Generate Joke"** to start the workflow
3. **View the results**:
   - Generated joke from the Performer
   - Detailed evaluation from the Critic
   - Metrics, strengths, weaknesses, and suggestions
4. **Check LangSmith** for full execution traces

## 🧠 Runtime LLM Selection for Agents

**NEW FEATURE**: Each agent can now use a different LLM provider and model at runtime!

### How to Use

In the Streamlit UI sidebar, you'll find independent LLM configuration sections for each agent:

#### 🎭 Performer Agent LLM
- **Provider Dropdown**: Choose between `groq` or `openai`
- **Model Dropdown**: Select from available models for the chosen provider
- **Temperature**: Fixed at 0.9 (creative)

#### 🧐 Critic Agent LLM
- **Provider Dropdown**: Choose between `groq` or `openai`
- **Model Dropdown**: Select from available models for the chosen provider
- **Temperature**: Fixed at 0.3 (analytical)

### Available Models (Updated 2025 - Tested & Verified)

**Groq (Free):** ✅ **ALL TESTED & WORKING**
- `llama-3.3-70b-versatile` ✅ (default, flagship model - **VERIFIED**)
- `llama-3.1-8b-instant` ✅ (fastest, lightweight - **VERIFIED**)

**OpenAI (Paid):** 🔄 **DYNAMICALLY DETECTED FROM YOUR ACCOUNT**
- Models are automatically fetched from your OpenAI account
- Only models you have access to will appear in dropdowns
- Common models include:
  - `o3`, `o3-mini` (Latest O3 series)
  - `o1`, `o1-mini` (O1 series)
  - `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano` (GPT-4.1 series)
  - `gpt-4o`, `gpt-4o-mini` (GPT-4o series)
  - `gpt-3.5-turbo` (legacy)

**HuggingFace Inference API (Free):** 🆓 **NEW!**
- `mistralai/Mistral-7B-Instruct-v0.2` (default, balanced)
- `meta-llama/Llama-3.1-8B-Instruct` (powerful, fast)
- `microsoft/Phi-3-mini-4k-instruct` (efficient, small)
- `google/gemma-2b-it` (lightweight)
- `Qwen/Qwen2.5-7B-Instruct` (multilingual)

**Together AI (Free Trial):** 🆓 **NEW!**
- `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` (default, optimized)
- `mistralai/Mistral-7B-Instruct-v0.2` (balanced)
- `Qwen/Qwen2.5-7B-Instruct-Turbo` (fast, multilingual)
- `meta-llama/Llama-3.2-3B-Instruct-Turbo` (lightweight)

**DeepInfra (Free Trial):** 🆓 **NEW!**
- `meta-llama/Meta-Llama-3.1-8B-Instruct` (default, powerful)
- `mistralai/Mistral-7B-Instruct-v0.2` (balanced)
- `microsoft/Phi-3-mini-4k-instruct` (efficient)
- `Qwen/Qwen2.5-7B-Instruct` (multilingual)

**⚠️ Deprecated/Decommissioned Models:**
- ~~`llama-3.1-70b-versatile`~~ → Use `llama-3.3-70b-versatile`
- ~~`llama-3.3-70b-specdec`~~ → **DECOMMISSIONED by Groq (2025)**
- ~~`mixtral-8x7b-32768`~~ → Model discontinued by Groq
- ~~`gemma2-9b-it`~~ → Model discontinued by Groq

### 🆓 Free LLM Providers Setup

**NEW**: The POC now supports 3 additional FREE LLM providers! No credit card required for trials.

#### HuggingFace Inference API

1. Sign up at [HuggingFace](https://huggingface.co/join)
2. Go to [Settings → Tokens](https://huggingface.co/settings/tokens)
3. Create a new token with "Read" access
4. Add to `.env`: `HUGGINGFACE_API_KEY=hf_your_token_here`

**Benefits:**
- ✅ Completely free (rate-limited)
- ✅ Access to 5+ models
- ✅ No credit card required
- ✅ Great for testing and development

#### Together AI

1. Sign up at [Together AI](https://api.together.xyz/)
2. Go to [Settings → API Keys](https://api.together.xyz/settings/api-keys)
3. Create a new API key
4. Add to `.env`: `TOGETHER_API_KEY=your_key_here`

**Benefits:**
- ✅ Free trial with $25 credit
- ✅ Fast inference (optimized models)
- ✅ OpenAI-compatible API
- ✅ Turbo variants for speed

#### DeepInfra

1. Sign up at [DeepInfra](https://deepinfra.com/)
2. Go to [Dashboard → API Keys](https://deepinfra.com/dash/api_keys)
3. Create a new API key
4. Add to `.env`: `DEEPINFRA_API_KEY=your_key_here`

**Benefits:**
- ✅ Free trial available
- ✅ Wide model selection
- ✅ OpenAI-compatible API
- ✅ Good performance

#### Testing All Providers

Run the comprehensive test suite:

```bash
python test_all_providers.py
```

This will:
- Check which API keys are configured
- Test each provider/model combination
- Show which ones are working
- Provide setup instructions for missing keys

### Auto-Detecting Available OpenAI Models 🔄

**NEW**: The application now automatically detects which OpenAI models your API key has access to!

#### How It Works

1. **Dynamic Fetching**: When you open the Streamlit UI, the app queries the OpenAI API
2. **Account-Specific**: Only models available on YOUR account appear in dropdowns
3. **Cached**: Results are cached for 1 hour to avoid repeated API calls
4. **Sorted**: Models are sorted by capability (most powerful first)

#### Testing Your Available Models

Run the diagnostic script to see which models you have access to:

```bash
python test_openai_models.py
```

**Sample Output:**
```
✅ Detected 38 chat-capable models:

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃ #  ┃ Model ID                 ┃ Category           ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ o3-mini                  │ O3 Series (Latest) │
│ 2  │ o1                       │ O1 Series          │
│ 3  │ gpt-4.1                  │ GPT-4              │
│ 4  │ gpt-4.1-mini             │ GPT-4              │
│ 5  │ gpt-4.1-nano             │ GPT-4              │
│ 6  │ gpt-4o                   │ GPT-4o             │
│ 7  │ gpt-4o-mini              │ GPT-4o Mini        │
...
```

#### Benefits

- ✅ **No Hardcoding**: Models update automatically
- ✅ **Access Control**: Only shows models you can actually use
- ✅ **Future-Proof**: New models appear automatically
- ✅ **Account-Aware**: Different API keys → different model lists

#### Troubleshooting

**Issue**: "No models detected" or using fallback models

**Causes & Solutions:**
1. **Invalid API key**: Verify `OPENAI_API_KEY` in `.env` is correct
2. **Placeholder key**: Replace `sk-your-openai-key-here` with real key
3. **Network issues**: Check internet connection
4. **API errors**: Run `python test_openai_models.py` to see detailed error

**Issue**: Missing expected models

**Solution**: Your API key may not have access. Check:
- Account tier (some models require paid plans)
- API key permissions
- Model availability in your region

### Testing & Verification

All Groq models are automatically tested. Run the comprehensive test suite:

```bash
python test_llms.py
```

**Latest Test Results (Groq Models):**
```
✅ groq/llama-3.3-70b-versatile - PASSED (Performer & Critic)
✅ groq/llama-3.1-8b-instant - PASSED (Performer & Critic)
❌ groq/llama-3.3-70b-specdec - FAILED (Decommissioned)
```

The test suite validates:
- Model instantiation
- Performer agent functionality
- Critic agent functionality  
- Complete workflow execution
- Cross-provider combinations

### Example Configurations

**Mix and Match:**
```
Performer: groq/llama-3.3-70b-versatile
Critic: openai/gpt-4o-mini
```
Use free Groq for creative generation, OpenAI for precise evaluation.

**All Groq (Free):**
```
Performer: groq/llama-3.3-70b-versatile
Critic: groq/llama-3.1-8b-instant
```
Completely free setup with fast performance.

**Premium OpenAI:**
```
Performer: openai/gpt-4o
Critic: openai/gpt-4o
```
Highest quality with both agents using GPT-4o.

**Different Models, Same Provider:**
```
Performer: openai/gpt-4o (creative, powerful)
Critic: openai/gpt-4o-mini (fast, cost-effective)
```

### Performance Notes

- **Groq**: Faster inference, free tier, great for development
- **OpenAI GPT-4o**: Best quality, higher cost
- **OpenAI GPT-4o-mini**: Balanced quality/cost, good for production
- **Mix providers**: Balance cost and performance based on task complexity

### Programmatic Usage

You can also use runtime LLM selection in code:

```python
from app.utils.llm import get_llm, get_performer_llm, get_critic_llm
from app.graph.workflow import JokeWorkflow

# Option 1: Use the unified get_llm function
performer_llm = get_llm(provider="groq", model="llama-3.3-70b-versatile", temperature=0.9)
critic_llm = get_llm(provider="openai", model="gpt-4o-mini", temperature=0.3)

# Option 2: Use convenience functions with overrides
performer_llm = get_performer_llm(provider="groq", model="llama-3.1-70b-versatile")
critic_llm = get_critic_llm(provider="openai", model="gpt-4o")

# Create workflow with selected LLMs
workflow = JokeWorkflow(performer_llm, critic_llm)
result = workflow.run("artificial intelligence")
```

### Model Catalog

The available models are defined in `app/utils/settings.py`:

```python
MODEL_CATALOG = {
    "groq": ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", ...],
    "openai": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", ...],
}
```

You can extend this to add new providers or models.

## 🔍 Viewing LangSmith Traces

Every workflow execution is automatically traced to LangSmith:

1. Visit [smith.langchain.com](https://smith.langchain.com)
2. Navigate to your project: `joke-agent-poc`
3. View traces showing:
   - Agent execution flow
   - LLM calls and responses
   - Timing and token usage
   - State transitions between agents

## 🧪 Testing the POC

### Manual Testing

1. **Test Performer Agent**:
   ```bash
   python -c "
   from app.utils.llm import get_performer_llm
   from app.agents.performer import PerformerAgent
   
   agent = PerformerAgent(get_performer_llm())
   joke = agent.generate_joke('artificial intelligence')
   print(f'Joke: {joke}')
   "
   ```

2. **Test Critic Agent**:
   ```bash
   python -c "
   from app.utils.llm import get_critic_llm
   from app.agents.critic import CriticAgent
   
   agent = CriticAgent(get_critic_llm())
   feedback = agent.evaluate_joke('Why do programmers prefer dark mode? Because light attracts bugs!')
   print(f'Score: {feedback.laughability_score}')
   print(f'Verdict: {feedback.overall_verdict}')
   "
   ```

3. **Test Full Workflow**:
   ```bash
   python -c "
   from app.utils.llm import get_performer_llm, get_critic_llm
   from app.graph.workflow import JokeWorkflow
   
   workflow = JokeWorkflow(get_performer_llm(), get_critic_llm())
   result = workflow.run('cats')
   print(f'Joke: {result[\"joke\"]}')
   print(f'Score: {result[\"feedback\"][\"laughability_score\"]}')
   "
   ```

### Verify LangSmith Integration

After running any test:

1. Check your terminal for execution logs
2. Visit your LangSmith project dashboard
3. Verify that traces appear with:
   - Performer agent execution
   - Critic agent execution
   - Complete state transitions

## 🧪 Comprehensive Model Testing

### Automated Test Suite

The project includes a comprehensive testing script that validates all models in the catalog:

```bash
python test_llms.py
```

This script tests:

1. **Model Instantiation** - Verifies each model can be loaded
2. **Agent Functionality** - Tests Performer and Critic with each model
3. **Workflow Combinations** - Tests complete workflows with mixed providers
4. **Deprecated Model Detection** - Alerts about removed models

### What Gets Tested

The test suite validates:

- ✅ All models in `MODEL_CATALOG` can be instantiated
- ✅ Each model works as a Performer agent (generates jokes)
- ✅ Each model works as a Critic agent (evaluates jokes)
- ✅ Cross-provider combinations work (Groq Performer + OpenAI Critic, etc.)
- ✅ Complete LangGraph workflows execute successfully

### Sample Output

```
╔════════════════════════════════════════╗
║ 🧪 LangGraph Joke Agents - LLM Model  ║
║    Testing Suite                      ║
╚════════════════════════════════════════╝

Checking API Keys:
  OpenAI: ✅ Set
  Groq: ✅ Set

═══ Testing Model Instantiation ═══

Testing GROQ models:
  ✅ groq/llama-3.3-70b-versatile - OK
  ✅ groq/llama-3.3-70b-specdec - OK
  ✅ groq/llama-3.1-8b-instant - OK

Testing OPENAI models:
  ✅ openai/gpt-4o-mini - OK
  ✅ openai/gpt-4o - OK
  ✅ openai/gpt-4-turbo - OK
  ✅ openai/gpt-3.5-turbo - OK

═══ Test Summary ═══

Test Category          Passed  Failed  Total
──────────────────────────────────────────────
Model Instantiation    7       0       7
Agent Functionality    14      0       14
Workflow Combinations  4       0       4
──────────────────────────────────────────────
TOTAL                  25      0       25

╔════════════════════════════════════════╗
║ ✅ ALL TESTS PASSED                    ║
║                                        ║
║ Successfully tested 25 configurations. ║
║ All models in MODEL_CATALOG are       ║
║ working correctly!                    ║
╚════════════════════════════════════════╝
```

### Troubleshooting Model Issues

If a model fails testing:

1. **Check API Keys**: Ensure correct provider key is set in `.env`
2. **Verify Model Name**: Confirm model ID against provider documentation
3. **Check Deprecation**: Model may have been deprecated by provider
4. **Network Issues**: Ensure you can reach provider API endpoints
5. **Rate Limits**: Some providers have strict rate limits

### Updating Models

When provider model catalogs change:

1. Update `MODEL_CATALOG` in `app/utils/settings.py`
2. Add deprecated models to `DEPRECATED_MODELS`
3. Run `python test_llms.py` to validate changes
4. Update documentation with new model list

## 🛠️ Technical Details

### LangGraph Workflow

The workflow implements a linear pipeline:

```
START
  ↓
PERFORMER (Generate Joke)
  ↓
CRITIC (Evaluate Joke)
  ↓
END
```

### State Management

State is passed between agents using a typed dictionary:

```python
class JokeWorkflowState(TypedDict):
    prompt: str              # Input topic
    joke: str                # Generated joke
    feedback: dict           # Structured evaluation
    performer_completed: bool
    critic_completed: bool
```

### LLM Configuration

- **Performer Agent**: Higher temperature (0.9) for creativity
- **Critic Agent**: Lower temperature (0.3) for consistency
- Supports both OpenAI (GPT-4o-mini) and Groq (Llama-3.3-70b)

## 📸 Screenshots

### Main Interface
*(Run the app and take screenshots of the main UI)*

### Generated Joke with Evaluation
*(Screenshot of a completed joke generation with feedback)*

### LangSmith Trace View
*(Screenshot from LangSmith showing the execution trace)*

## 🔧 Customization

### Adding More Agents

1. Create a new agent class in `app/agents/`
2. Add the agent as a node in `workflow.py`
3. Update the state type to include new fields
4. Connect the agent in the graph flow

### Using Different LLMs

Update `app/utils/settings.py` to add new providers:

```python
llm_provider: Literal["openai", "groq", "anthropic"] = "openai"
```

Then implement the new provider in `app/utils/llm.py`

## 📝 Key Learnings

This POC demonstrates:

1. **Multi-agent orchestration** with LangGraph
2. **State management** across agent interactions
3. **Structured outputs** using Pydantic
4. **Observability** with LangSmith tracing
5. **Production patterns** for LLM applications

## 🐛 Troubleshooting

### "API Key not found" error

- Verify your `.env` file exists and contains the correct keys
- Ensure you've selected the correct provider in the sidebar

### LangSmith traces not appearing

- Verify `LANGCHAIN_TRACING_V2=true` in your `.env`
- Check that `LANGCHAIN_API_KEY` is valid
- Ensure the project name matches in LangSmith dashboard

### Import errors

- Activate your virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## 🚀 Deployment

### 📦 Deploy to Lovable

This project is fully configured for **Lovable** deployment with zero configuration changes required.

#### Prerequisites

1. **GitHub Repository** (see GitHub setup below)
2. **Lovable Account** - Sign up at [lovable.dev](https://lovable.dev)
3. **API Keys** for at least one LLM provider:
   - **Groq** (recommended for free tier): [Get API key](https://console.groq.com/keys)
   - **OpenAI** (paid): [Get API key](https://platform.openai.com/api-keys)
   - **HuggingFace** (free): [Get API key](https://huggingface.co/settings/tokens)
   - **Together AI** (free trial): [Get API key](https://api.together.xyz/settings/api-keys)
   - **DeepInfra** (free trial): [Get API key](https://deepinfra.com/dash/api_keys)
4. **LangSmith API Key** (free tier available): [Get API key](https://smith.langchain.com/settings)

#### Deployment Steps

**1. Connect Your GitHub Repository to Lovable**

- Log into your Lovable dashboard
- Click "New Project" or "Import from GitHub"
- Select your repository: `<your-username>/langgraph-joke-agents-poc`
- Grant Lovable access permissions

**2. Configure Environment Variables in Lovable UI**

In the Lovable dashboard, navigate to **Settings → Environment Variables** and add:

```bash
# Required: At least one LLM provider
GROQ_API_KEY=gsk_your_actual_groq_key_here
OPENAI_API_KEY=sk-your_actual_openai_key_here
HUGGINGFACE_API_KEY=hf_your_actual_huggingface_key_here
TOGETHER_API_KEY=your_actual_together_key_here
DEEPINFRA_API_KEY=your_actual_deepinfra_key_here

# Required: LangSmith tracing
LANGCHAIN_API_KEY=ls_your_actual_langsmith_key_here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_TRACING_V2=true

# Optional: Default provider
LLM_PROVIDER=groq
```

**Important**: 
- You need **at least ONE** LLM provider API key (Groq recommended for free tier)
- LangSmith is **optional** but recommended for observability
- Do NOT include quotes around values in Lovable's environment variable UI

**3. Deploy**

Lovable will automatically:
- Install dependencies from `requirements.txt`
- Run the application with: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`
- Provide you with a public URL

**4. Verify Deployment**

Once deployed, test your application:
- ✅ Open the provided Lovable URL
- ✅ Ensure the sidebar shows "Environment Status: ✅ Configured"
- ✅ Select LLM providers for Performer and Critic
- ✅ Generate a test joke
- ✅ Verify the refinement loop buttons appear
- ✅ Check LangSmith dashboard for traces (if configured)

#### Deployment Notes

**✅ What Works Automatically:**
- Multi-provider LLM selection (Groq, OpenAI, HuggingFace, Together AI, DeepInfra)
- Dynamic OpenAI model detection
- LangSmith tracing and observability
- Iterative refinement loop with history
- Responsive Streamlit UI

**⚠️ Known Limitations:**
- HuggingFace models may be slower (free tier)
- DeepInfra requires positive balance after trial
- Together AI free tier has rate limits

**🔧 Troubleshooting Lovable Deployment:**

| Issue | Solution |
|-------|----------|
| "Invalid API Key" error | Double-check environment variables in Lovable settings |
| "No module named 'openai'" | Ensure `requirements.txt` is committed to GitHub |
| Models not showing | Verify API keys are valid and not placeholders |
| LangSmith traces missing | Set `LANGCHAIN_TRACING_V2=true` (no quotes) |
| Port binding errors | Lovable handles this automatically; check logs |

---

### 🐙 GitHub Setup

#### First-Time Repository Setup

If you haven't pushed this project to GitHub yet:

```bash
# 1. Initialize Git repository (if not already done)
git init

# 2. Add all files to staging
git add .

# 3. Create initial commit
git commit -m "Initial commit: Lovable-ready LangGraph Joke System"

# 4. Rename default branch to 'main'
git branch -M main

# 5. Create a new repository on GitHub
# Go to: https://github.com/new
# Repository name: langgraph-joke-agents-poc
# Description: Multi-agent joke generation system with LangGraph
# Visibility: Public or Private (your choice)
# Do NOT initialize with README, .gitignore, or license

# 6. Link your local repo to GitHub (replace with your username)
git remote add origin https://github.com/<your-username>/langgraph-joke-agents-poc.git

# 7. Push to GitHub
git push -u origin main
```

#### Subsequent Updates

After making changes to your code:

```bash
# 1. Check what changed
git status

# 2. Stage changes
git add .

# 3. Commit with descriptive message
git commit -m "feat: add new feature or fix: resolve bug"

# 4. Push to GitHub
git push
```

**⚠️ Important:** 
- Your `.env` file is automatically excluded by `.gitignore`
- **NEVER** commit API keys to GitHub
- Use environment variables in deployment platforms like Lovable

#### Verifying Git Setup

Check if your repository is properly configured:

```bash
# Check remote URL
git remote -v

# Should output:
# origin  https://github.com/<your-username>/langgraph-joke-agents-poc.git (fetch)
# origin  https://github.com/<your-username>/langgraph-joke-agents-poc.git (push)

# Check current branch
git branch

# Should show:
# * main

# Check ignored files
git status --ignored

# Should show .env, venv/, __pycache__/, etc. as ignored
```

---

### 🔐 Security Best Practices

**✅ DO:**
- Store API keys in `.env` locally
- Use environment variables in deployment platforms
- Keep `.env` in `.gitignore`
- Use different API keys for dev/prod if possible
- Regularly rotate API keys

**❌ DON'T:**
- Commit `.env` to Git
- Share API keys in code or documentation
- Use production keys in public repositories
- Hardcode API keys in source files

---

### 🌐 Alternative Deployment Platforms

This project can also be deployed to:

**Streamlit Cloud** (Free)
```bash
# Deploy directly from GitHub
# Visit: https://share.streamlit.io
# Click "New app" → Connect GitHub → Select repo
# Set environment variables in dashboard
# Command: streamlit run main.py
```

**Heroku** (Paid)
```bash
# Add Procfile:
# web: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0

# Deploy:
heroku create langgraph-joke-agents
git push heroku main
heroku config:set GROQ_API_KEY=your_key_here
heroku config:set LANGCHAIN_API_KEY=your_key_here
```

**Railway** (Free tier)
```bash
# Deploy from GitHub
# Visit: https://railway.app
# Click "New Project" → "Deploy from GitHub"
# Add environment variables in dashboard
```

**Render** (Free tier)
```bash
# Deploy from GitHub
# Visit: https://render.com
# Click "New" → "Web Service"
# Build Command: pip install -r requirements.txt
# Start Command: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0
```

---

## 📚 Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## 📄 License

This is a proof-of-concept project for educational purposes.

## 🤝 Contributing

This is a POC, but feel free to fork and extend it with:

- Additional agents (e.g., Editor, Ranker)
- Iterative refinement loops
- More complex workflows
- Different UI frameworks
- Async processing

---

**Built with ❤️ using LangGraph, LangChain, and LangSmith**

