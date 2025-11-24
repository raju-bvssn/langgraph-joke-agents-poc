# 🏗️ Architecture Documentation

Detailed technical architecture of the LangGraph Joke Agents POC.

## 📐 System Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI                         │
│                    (app/main.py)                        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  Workflow Layer                         │
│              (app/graph/workflow.py)                    │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         LangGraph StateGraph                     │  │
│  │                                                  │  │
│  │  START → [Performer] → [Critic] → END          │  │
│  │           ↓            ↓                       │  │
│  │        State Pass   State Pass                 │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────┬────────────────┬─────────────────────┘
                   │                │
         ┌─────────▼────────┐  ┌────▼──────────┐
         │  Performer Agent │  │  Critic Agent │
         │  (creative LLM)  │  │ (analytical)  │
         │  temp: 0.9       │  │  temp: 0.3    │
         └──────────────────┘  └───────────────┘
                   │                │
                   └────────┬───────┘
                            ▼
                   ┌─────────────────┐
                   │   LLM Layer     │
                   │  (OpenAI/Groq)  │
                   └─────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │   LangSmith     │
                   │    Tracing      │
                   └─────────────────┘
```

## 🔄 State Flow

### State Definition

```python
class JokeWorkflowState(TypedDict):
    prompt: str              # Input from user
    joke: str                # Output from Performer
    feedback: dict           # Output from Critic
    performer_completed: bool
    critic_completed: bool
```

### State Transitions

1. **Initial State** (User Input)
   ```python
   {
       "prompt": "artificial intelligence",
       "joke": "",
       "feedback": {},
       "performer_completed": False,
       "critic_completed": False
   }
   ```

2. **After Performer**
   ```python
   {
       "prompt": "artificial intelligence",
       "joke": "Why did the AI go to therapy? ...",
       "feedback": {},
       "performer_completed": True,
       "critic_completed": False
   }
   ```

3. **Final State** (After Critic)
   ```python
   {
       "prompt": "artificial intelligence",
       "joke": "Why did the AI go to therapy? ...",
       "feedback": {
           "laughability_score": 75,
           "age_appropriateness": "Teen",
           "strengths": [...],
           "weaknesses": [...],
           "suggestions": [...],
           "overall_verdict": "..."
       },
       "performer_completed": True,
       "critic_completed": True
   }
   ```

## 🤖 Agent Architecture

### Performer Agent

**Purpose**: Generate creative, original jokes

**Configuration**:
- Temperature: 0.9 (high creativity)
- Model: GPT-4o-mini / Llama-3.3-70b
- Role: Creative comedian

**Prompt Structure**:
```
System: You are a creative comedian...
User: Generate a joke about: [topic]
```

**Output**: Plain text joke (2-4 sentences)

### Critic Agent

**Purpose**: Evaluate jokes with structured feedback

**Configuration**:
- Temperature: 0.3 (consistent analysis)
- Model: GPT-4o-mini / Llama-3.3-70b
- Role: Comedy critic

**Prompt Structure**:
```
System: You are an expert comedy critic...
User: Evaluate this joke: "[joke]"
```

**Output**: Structured JSON with metrics

```json
{
    "laughability_score": 0-100,
    "age_appropriateness": "Child|Teen|Adult",
    "strengths": ["point1", "point2"],
    "weaknesses": ["point1", "point2"],
    "suggestions": ["action1", "action2"],
    "overall_verdict": "summary"
}
```

## 🔧 Component Details

### Settings Management

**File**: `app/utils/settings.py`

- Uses Pydantic Settings for type-safe configuration
- Loads from `.env` file automatically
- Validates required keys based on provider
- Configures LangSmith environment variables

### LLM Provider Abstraction

**File**: `app/utils/llm.py`

- Factory functions for agent-specific LLM configs
- Support for multiple providers (OpenAI, Groq)
- Temperature tuning per agent
- Automatic LangSmith integration

### Workflow Orchestration

**File**: `app/graph/workflow.py`

**Graph Structure**:
```python
workflow = StateGraph(JokeWorkflowState)
workflow.add_node("performer", performer_agent)
workflow.add_node("critic", critic_agent)
workflow.set_entry_point("performer")
workflow.add_edge("performer", "critic")
workflow.add_edge("critic", END)
graph = workflow.compile()
```

**Execution**:
- Synchronous: `graph.invoke(state)`
- Asynchronous: `graph.ainvoke(state)`

## 📊 LangSmith Integration

### Tracing Configuration

Set via environment variables:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_API_KEY=ls-...
```

### What Gets Traced?

1. **Complete Workflow Execution**
   - Start and end times
   - Total duration
   - State at each step

2. **Agent Invocations**
   - Agent name and type
   - Input state
   - Output updates

3. **LLM Calls**
   - Model used
   - Prompt sent
   - Response received
   - Token usage
   - Latency

4. **State Transitions**
   - State before/after each node
   - Fields added/modified

### Viewing Traces

1. Visit https://smith.langchain.com
2. Select project: `joke-agent-poc`
3. View runs with:
   - Timeline visualization
   - Input/output inspection
   - Cost analysis
   - Error tracking

## 🎨 UI Architecture

### Streamlit Components

**Main Interface** (`app/main.py`):
- Input field for joke topics
- Generate button
- Results display (joke + feedback)
- Configuration sidebar

**Sidebar**:
- Provider selection
- LangSmith status
- Environment diagnostics
- About/help information

**Results Display**:
- Joke in prominent panel
- Metrics cards (score, age, status)
- Strengths/weaknesses columns
- Suggestions list
- Overall verdict

## 🔌 Extension Points

### Adding New Agents

1. Create agent class in `app/agents/`:
   ```python
   class NewAgent:
       def __init__(self, llm):
           self.llm = llm
       
       def __call__(self, state):
           # Process state
           return {"new_field": value}
   ```

2. Update workflow:
   ```python
   workflow.add_node("new_agent", new_agent)
   workflow.add_edge("critic", "new_agent")
   workflow.add_edge("new_agent", END)
   ```

3. Update state definition:
   ```python
   class JokeWorkflowState(TypedDict):
       # existing fields...
       new_field: str
   ```

### Adding Conditional Routing

```python
def should_refine(state):
    score = state["feedback"]["laughability_score"]
    return "refine" if score < 60 else "end"

workflow.add_conditional_edges(
    "critic",
    should_refine,
    {
        "refine": "performer",
        "end": END
    }
)
```

### Adding Iterative Refinement

```python
class JokeWorkflowState(TypedDict):
    # existing fields...
    iteration: int
    max_iterations: int

def should_continue(state):
    if state["iteration"] >= state["max_iterations"]:
        return "end"
    if state["feedback"]["laughability_score"] >= 80:
        return "end"
    return "refine"
```

## 📈 Performance Considerations

### Latency

- **Performer**: ~2-5 seconds (generation)
- **Critic**: ~3-6 seconds (evaluation + parsing)
- **Total**: ~5-11 seconds end-to-end

### Optimization Strategies

1. **Async Execution**: Use `ainvoke()` for better concurrency
2. **Streaming**: Implement streaming responses for real-time feedback
3. **Caching**: Cache similar prompts to reduce LLM calls
4. **Parallel Evaluation**: Run multiple critics simultaneously

### Cost Optimization

- Use cheaper models (GPT-4o-mini vs GPT-4)
- Implement prompt caching
- Set max token limits
- Monitor via LangSmith

## 🔒 Security Best Practices

1. **API Keys**
   - Store in `.env` (never commit)
   - Use environment variables
   - Rotate regularly

2. **Input Validation**
   - Sanitize user inputs
   - Limit prompt length
   - Filter inappropriate content

3. **Rate Limiting**
   - Implement request throttling
   - Set usage quotas
   - Monitor costs

## 🧪 Testing Strategy

### Unit Tests
```python
def test_performer_generates_joke():
    agent = PerformerAgent(mock_llm)
    joke = agent.generate_joke("test")
    assert len(joke) > 0

def test_critic_evaluates_joke():
    agent = CriticAgent(mock_llm)
    feedback = agent.evaluate_joke("test joke")
    assert 0 <= feedback.laughability_score <= 100
```

### Integration Tests
```python
def test_full_workflow():
    workflow = JokeWorkflow(performer_llm, critic_llm)
    result = workflow.run("test")
    assert result["joke"]
    assert result["feedback"]
    assert result["performer_completed"]
    assert result["critic_completed"]
```

### LangSmith Evaluation
- Create test datasets
- Run evaluations
- Compare model performance
- Track regression

## 📚 Design Patterns Used

1. **Factory Pattern**: LLM configuration (`get_llm()`)
2. **Strategy Pattern**: Multiple LLM providers
3. **State Pattern**: Workflow state management
4. **Observer Pattern**: LangSmith tracing
5. **Builder Pattern**: StateGraph construction

## 🔄 Future Enhancements

- [ ] Multi-turn refinement loops
- [ ] A/B testing different prompts
- [ ] Voice output for jokes
- [ ] Joke rating history
- [ ] User feedback collection
- [ ] Batch processing
- [ ] API endpoint (FastAPI)
- [ ] Docker deployment
- [ ] Async streaming responses
- [ ] Multi-language support

---

**This architecture is designed to be extensible, observable, and production-ready.**

