# 🧠 Runtime LLM Selection Feature

## Overview

This document describes the runtime LLM selection feature that allows each agent (Performer and Critic) to independently choose different LLM providers and models at runtime.

## What's New

### ✨ Key Features

- **🎭 Independent Agent Configuration**: Each agent can use a different LLM provider and model
- **🔄 Runtime Selection**: Change models without restarting or reconfiguring the application
- **🎨 UI Controls**: Intuitive Streamlit dropdowns for easy model selection
- **💻 CLI Support**: Command-line arguments for testing different configurations
- **📊 Model Catalog**: Centralized registry of available models per provider

## Architecture Changes

### 1. Model Catalog (`app/utils/settings.py`)

Added centralized model registry:

```python
MODEL_CATALOG = {
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
    ],
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-3.5-turbo",
    ],
}

DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o-mini",
}
```

### 2. Unified LLM Factory (`app/utils/llm.py`)

Enhanced `get_llm()` function:

```python
def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None
) -> BaseChatModel:
    """
    Get configured LLM with runtime provider and model selection.
    
    Args:
        provider: "openai" or "groq" (uses settings default if None)
        model: Specific model name (uses provider default if None)
        temperature: Temperature override (uses settings default if None)
    """
```

Updated convenience functions:

```python
def get_performer_llm(provider=None, model=None) -> BaseChatModel:
    """Returns LLM with temperature=0.9 for creativity"""
    return get_llm(provider=provider, model=model, temperature=0.9)

def get_critic_llm(provider=None, model=None) -> BaseChatModel:
    """Returns LLM with temperature=0.3 for consistency"""
    return get_llm(provider=provider, model=model, temperature=0.3)
```

### 3. Streamlit UI Updates (`app/main.py`)

#### Sidebar Configuration

Added independent LLM selection for each agent:

```python
# Performer Agent Configuration
st.subheader("🎭 Performer Agent LLM")
performer_provider = st.selectbox("Provider", list(MODEL_CATALOG.keys()))
performer_model = st.selectbox("Model", MODEL_CATALOG[performer_provider])

# Critic Agent Configuration  
st.subheader("🧐 Critic Agent LLM")
critic_provider = st.selectbox("Provider", list(MODEL_CATALOG.keys()))
critic_model = st.selectbox("Model", MODEL_CATALOG[critic_provider])
```

#### Dynamic Workflow Initialization

```python
# Initialize with runtime-selected LLMs
performer_llm = get_performer_llm(
    provider=llm_config["performer_provider"],
    model=llm_config["performer_model"]
)
critic_llm = get_critic_llm(
    provider=llm_config["critic_provider"],
    model=llm_config["critic_model"]
)
workflow = JokeWorkflow(performer_llm, critic_llm)
```

### 4. CLI Test Tool Updates (`test_workflow.py`)

Added command-line arguments:

```bash
python test_workflow.py "topic" \
  --performer-provider groq \
  --performer-model llama-3.3-70b-versatile \
  --critic-provider openai \
  --critic-model gpt-4o-mini
```

## Usage Examples

### Example 1: Free Setup (Both Groq)

**UI Selection:**
- Performer: `groq` / `llama-3.3-70b-versatile`
- Critic: `groq` / `llama-3.1-8b-instant`

**CLI:**
```bash
python test_workflow.py "programming" \
  --performer-provider groq \
  --performer-model llama-3.3-70b-versatile \
  --critic-provider groq \
  --critic-model llama-3.1-8b-instant
```

### Example 2: Mixed Providers

**UI Selection:**
- Performer: `groq` / `llama-3.3-70b-versatile` (free, creative)
- Critic: `openai` / `gpt-4o-mini` (paid, precise)

**Programmatic:**
```python
from app.utils.llm import get_performer_llm, get_critic_llm
from app.graph.workflow import JokeWorkflow

performer_llm = get_performer_llm(provider="groq", model="llama-3.3-70b-versatile")
critic_llm = get_critic_llm(provider="openai", model="gpt-4o-mini")

workflow = JokeWorkflow(performer_llm, critic_llm)
result = workflow.run("artificial intelligence")
```

### Example 3: Premium Setup

**UI Selection:**
- Performer: `openai` / `gpt-4o`
- Critic: `openai` / `gpt-4o`

### Example 4: Testing Different Models

**CLI:**
```bash
# Test with fastest models
python test_workflow.py "cats" \
  --performer-model llama-3.1-8b-instant \
  --critic-model llama-3.1-8b-instant

# Test with premium models
python test_workflow.py "cats" \
  --performer-provider openai \
  --performer-model gpt-4o \
  --critic-provider openai \
  --critic-model gpt-4o
```

## Performance Comparison

| Configuration | Cost | Speed | Quality | Use Case |
|--------------|------|-------|---------|----------|
| Groq/Groq (8B models) | Free | ⚡⚡⚡ Fast | Good | Development/Testing |
| Groq/Groq (70B models) | Free | ⚡⚡ Fast | Excellent | Production (Free) |
| Groq/OpenAI mini | Low | ⚡⚡ Fast | Excellent | Balanced |
| OpenAI mini/mini | Medium | ⚡ Medium | Excellent | Production (Cost-effective) |
| OpenAI 4o/4o | High | Medium | Best | Premium Quality |

## Model Characteristics

### Groq Models

| Model | Speed | Quality | Context | Best For |
|-------|-------|---------|---------|----------|
| llama-3.3-70b-versatile | Fast | Excellent | 8K | Performer (Creative) |
| llama-3.1-70b-versatile | Fast | Excellent | 131K | Long context |
| llama-3.1-8b-instant | ⚡ Fastest | Good | 131K | Critic (Fast eval) |
| mixtral-8x7b-32768 | Fast | Excellent | 32K | General purpose |
| gemma2-9b-it | Fast | Good | 8K | Lightweight |

### OpenAI Models

| Model | Speed | Quality | Context | Cost | Best For |
|-------|-------|---------|---------|------|----------|
| gpt-4o-mini | Medium | Excellent | 128K | $ | Balanced |
| gpt-4o | Medium | Best | 128K | $$$ | Premium |
| gpt-4-turbo | Medium | Best | 128K | $$$ | Long context |
| gpt-3.5-turbo | ⚡ Fast | Very Good | 16K | $ | Speed-focused |

## Configuration Recommendations

### Development

```
Performer: groq/llama-3.1-8b-instant
Critic: groq/llama-3.1-8b-instant
```
- Fastest iteration
- Zero cost
- Good enough for testing

### Production (Free)

```
Performer: groq/llama-3.3-70b-versatile
Critic: groq/llama-3.1-70b-versatile
```
- Excellent quality
- Free inference
- Fast performance

### Production (Paid - Recommended)

```
Performer: groq/llama-3.3-70b-versatile
Critic: openai/gpt-4o-mini
```
- Creative generation (free)
- Precise evaluation (low cost)
- Best value

### Premium

```
Performer: openai/gpt-4o
Critic: openai/gpt-4o
```
- Highest quality
- Most reliable
- Best for demos

## API Key Requirements

Based on your selected providers:

| Selection | Required Keys |
|-----------|--------------|
| Both Groq | `GROQ_API_KEY` only |
| Both OpenAI | `OPENAI_API_KEY` only |
| Mixed | Both `GROQ_API_KEY` and `OPENAI_API_KEY` |

The application automatically validates that required keys are present for selected providers.

## Extending the Model Catalog

To add new models or providers:

1. **Update `app/utils/settings.py`**:

```python
MODEL_CATALOG = {
    "groq": [...],
    "openai": [...],
    "anthropic": [  # New provider
        "claude-3-opus",
        "claude-3-sonnet",
    ],
}

DEFAULT_MODELS = {
    "groq": "llama-3.3-70b-versatile",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-sonnet",
}
```

2. **Update `app/utils/llm.py`**:

```python
def get_llm(provider, model, temperature):
    # ... existing code ...
    
    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=settings.anthropic_api_key
        )
```

3. **Update `app/utils/settings.py`** (add API key):

```python
class Settings(BaseSettings):
    # ... existing keys ...
    anthropic_api_key: str = ""
```

## Testing

### Manual UI Testing

1. Start Streamlit: `streamlit run app/main.py`
2. In sidebar, select different providers/models for each agent
3. Generate jokes and compare results
4. Check LangSmith traces to see which models were used

### CLI Testing

```bash
# Test default configuration
python test_workflow.py "artificial intelligence"

# Test with specific models
python test_workflow.py "programming" \
  --performer-provider groq \
  --performer-model llama-3.3-70b-versatile \
  --critic-provider openai \
  --critic-model gpt-4o-mini

# Compare different configurations
python test_workflow.py "cats" --performer-model llama-3.1-8b-instant
python test_workflow.py "cats" --performer-model llama-3.3-70b-versatile
```

### Programmatic Testing

```python
from app.utils.llm import get_llm
from app.graph.workflow import JokeWorkflow

# Test all Groq models
for model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
    performer = get_llm("groq", model, 0.9)
    critic = get_llm("groq", model, 0.3)
    workflow = JokeWorkflow(performer, critic)
    result = workflow.run("test")
    print(f"{model}: {result['feedback']['laughability_score']}")
```

## LangSmith Tracing

All model selections are automatically traced in LangSmith:

- **Run metadata** includes provider and model for each agent
- **Compare runs** with different configurations
- **Analyze performance** differences between models
- **Track costs** across providers

## Troubleshooting

### Error: "Model not found in catalog"

**Cause**: Model name doesn't match catalog entry

**Solution**: Check `MODEL_CATALOG` in `app/utils/settings.py` for valid model names

### Error: "API Key required"

**Cause**: Selected provider but missing API key

**Solution**: Add required key to `.env` file:
```bash
GROQ_API_KEY=gsk-...
OPENAI_API_KEY=sk-...
```

### Error: "Invalid API Key"

**Cause**: API key is incorrect or expired

**Solution**: Verify key at provider's dashboard and update `.env`

## Benefits

### For Development

- **Fast Iteration**: Use free Groq models for rapid testing
- **Cost Control**: Switch to paid models only when needed
- **Experimentation**: Test different model combinations easily

### For Production

- **Flexibility**: Adjust models based on load/budget
- **Optimization**: Use appropriate model for each task
- **Fallback**: Switch providers if one is unavailable
- **Cost Efficiency**: Mix free and paid models strategically

### For Research

- **Comparison**: A/B test different models
- **Benchmarking**: Measure quality across providers
- **Analysis**: Understand model strengths/weaknesses

## Summary

The runtime LLM selection feature provides:

✅ **Independent agent configuration**  
✅ **UI and CLI support**  
✅ **Model catalog management**  
✅ **Backward compatibility**  
✅ **LangSmith integration**  
✅ **Cost optimization options**  
✅ **Extensible architecture**  

No code changes needed for existing workflows - the feature is fully backward compatible while providing powerful new capabilities for advanced users.

---

**For more information, see:**
- [README.md](README.md) - Main documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [WALKTHROUGH.md](WALKTHROUGH.md) - Step-by-step guide

