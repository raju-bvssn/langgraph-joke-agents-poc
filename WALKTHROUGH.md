# 🎯 Complete Walkthrough

Step-by-step guide to run and understand the LangGraph Joke Agents POC.

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10 or higher installed
- [ ] Git (if cloning)
- [ ] Terminal/command line access
- [ ] One of these API keys:
  - [ ] OpenAI API key (recommended)
  - [ ] OR Groq API key (free alternative)
- [ ] LangSmith API key (for tracing)

## 🚀 Step 1: Initial Setup (5 minutes)

### Navigate to Project

```bash
cd /Users/vbolisetti/AI-Projects/multi-agent-arb/langgraph-joke-agents-poc
```

### Create Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# You should see (venv) in your prompt
```

### Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# This will install:
# - langchain, langgraph, langsmith
# - streamlit
# - pydantic
# - Rich (for CLI)
```

Expected output:
```
Successfully installed langchain-0.3.13 langgraph-0.2.53 ...
```

## 🔑 Step 2: Configure API Keys (3 minutes)

### Create .env File

```bash
cp env.example .env
```

### Edit .env File

Open `.env` in your favorite editor:

```bash
# Using nano
nano .env

# Or VS Code
code .env

# Or any text editor
```

### Add Your Keys

**Minimum required**:

```bash
# Choose ONE LLM provider:

# Option A: OpenAI (recommended)
OPENAI_API_KEY=sk-proj-your-actual-key-here

# Option B: Groq (free alternative)
# GROQ_API_KEY=gsk-your-actual-key-here

# LangSmith (required for tracing)
LANGCHAIN_API_KEY=lsv2_pt_your-actual-key-here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_TRACING_V2=true

# Set your provider
LLM_PROVIDER=openai  # or 'groq'
```

**Important**: 
- Remove the placeholder text
- Don't add quotes around keys
- Keep the equals sign with no spaces

### Verify Configuration

```bash
python verify_setup.py
```

Expected output:
```
🔍 LangGraph Joke Agents - Setup Verification

✅ Python version: 3.10.x (>= 3.10)
✅ Environment file: .env found

📦 Dependencies:
✅ langchain - Installed - 0.3.13
✅ langgraph - Installed - 0.2.53
...

🔑 API Keys:
✅ OpenAI Key - ✓ Configured
✅ LangSmith Key - ✓ Configured

✅ All checks passed! You're ready to run the application.
```

## 🎭 Step 3: Run the Application (1 minute)

### Start Streamlit

```bash
streamlit run app/main.py
```

Expected output:
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.x:8501
```

Your browser should automatically open to `http://localhost:8501`

## 🎨 Step 4: Use the UI

### Main Interface Overview

```
┌─────────────────────────────────────────────────────┐
│  🎭 Multi-Agent Joke System                        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  🎯 Generate a Joke                                │
│  ┌─────────────────────────────────┬──────────────┐│
│  │ Enter topic: ____________       │ 🎭 Generate  ││
│  └─────────────────────────────────┴──────────────┘│
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Sidebar Configuration

```
⚙️ Configuration
├── 🤖 LLM Provider
│   └── [Select: openai / groq]
├── 📊 LangSmith
│   ├── Project: joke-agent-poc
│   └── Tracing: ✅ Enabled
└── ℹ️ About
```

### Generate Your First Joke

1. **Enter a topic** in the text field:
   - Examples: "programming", "cats", "artificial intelligence"

2. **Click "🎭 Generate Joke"**

3. **Watch the magic happen**:
   ```
   🎭 Performer is creating a joke...
   ```

4. **View the results**:

   ```
   ╔═══════════════════════════════════════════╗
   ║     🎭 Generated Joke                     ║
   ╠═══════════════════════════════════════════╣
   ║  Why do programmers prefer dark mode?     ║
   ║  Because light attracts bugs!             ║
   ╚═══════════════════════════════════════════╝
   
   🧐 Critic's Evaluation
   
   Laughability Score   Age Appropriateness   Status
   😄 75/100            Teen                   ✅ Complete
   
   💪 Strengths:
   • Clever wordplay on "bugs"
   • Relatable to programmer audience
   
   ⚠️ Weaknesses:
   • Somewhat predictable
   • Limited appeal outside tech
   
   💡 Suggestions:
   • Add unexpected twist
   • Consider broader audience
   
   📝 Overall Verdict:
   A solid programming joke with good wordplay
   ```

## 🔍 Step 5: View LangSmith Traces

### Access LangSmith

1. Open browser to https://smith.langchain.com
2. Login with your account
3. Navigate to **Projects**
4. Find and open **joke-agent-poc**

### Explore Your Traces

You'll see:

```
Run Name: JokeWorkflow
Duration: 8.2s
Status: ✓ Success
Cost: $0.003

Timeline:
├─ performer (4.1s)
│  └─ ChatOpenAI (4.0s)
│     ├─ Input: "Generate a joke about: programming"
│     └─ Output: "Why do programmers prefer..."
│
└─ critic (4.1s)
   └─ ChatOpenAI (4.0s)
      ├─ Input: "Evaluate this joke..."
      └─ Output: {"laughability_score": 75, ...}
```

### What to Look For

- ✅ **Complete workflow execution**
- ✅ **Both agent calls traced**
- ✅ **Input/output for each step**
- ✅ **Token usage and cost**
- ✅ **Timing information**

## 🧪 Step 6: Test via CLI (Optional)

### Run CLI Test

```bash
python test_workflow.py "artificial intelligence"
```

Expected output (with colors in terminal):
```
╔══════════════════════════════════════════════╗
║  🎭 Multi-Agent Joke System - CLI Test      ║
╚══════════════════════════════════════════════╝

✅ Using OPENAI provider

Topic: artificial intelligence

Initializing agents...
✓ Agents initialized

🎭 Performer is generating a joke...

╔═══════════════════════════════════════════════╗
║     🎭 Generated Joke                         ║
╠═══════════════════════════════════════════════╣
║  Why did the AI go to therapy?                ║
║  It had too many neural networks and couldn't ║
║  process its feelings!                        ║
╚═══════════════════════════════════════════════╝

🧐 Critic's Evaluation

Laughability Score    🔥 82/100
Age Appropriateness   Teen

💪 Strengths:
  • Creative use of AI terminology
  • Good setup and punchline structure
  • Appeals to tech-savvy audience

⚠️ Weaknesses:
  • Requires technical knowledge
  • Could be more universally accessible

💡 Suggestions:
  • Consider adding visual imagery
  • Make the punchline more surprising

╔═══════════════════════════════════════════════╗
║ 📝 Overall Verdict                            ║
╠═══════════════════════════════════════════════╣
║ A clever AI joke with strong wordplay that   ║
║ effectively uses technical concepts.          ║
╚═══════════════════════════════════════════════╝

🔍 This run has been traced in LangSmith project: joke-agent-poc
```

## 🎯 Step 7: Experiment!

### Try Different Topics

**Technical**:
```bash
python test_workflow.py "quantum physics"
python test_workflow.py "blockchain"
python test_workflow.py "debugging"
```

**Everyday**:
```bash
python test_workflow.py "coffee addiction"
python test_workflow.py "working from home"
python test_workflow.py "cats vs dogs"
```

**Creative**:
```bash
python test_workflow.py "time travel"
python test_workflow.py "artificial intelligence dating"
python test_workflow.py "programmer dad jokes"
```

### Switch LLM Providers

Edit `.env`:
```bash
# Try Groq instead
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-your-key-here
```

Restart Streamlit and compare results!

## 📊 Step 8: Analyze Patterns

### In LangSmith Dashboard

1. **Compare runs**:
   - Which topics generate better jokes?
   - Which provider is faster?
   - Cost differences?

2. **View metrics**:
   - Average laughability scores
   - Token usage patterns
   - Latency distribution

3. **Debug issues**:
   - Failed runs
   - Error traces
   - Timeout patterns

## 🔧 Troubleshooting Common Issues

### Issue 1: "ModuleNotFoundError"

**Solution**:
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 2: "API Key not found"

**Solution**:
```bash
# Check .env exists
ls -la .env

# Verify contents (don't share keys!)
cat .env

# Make sure no quotes around keys
# ✓ OPENAI_API_KEY=sk-123
# ✗ OPENAI_API_KEY="sk-123"
```

### Issue 3: "LangSmith traces not appearing"

**Solution**:
```bash
# Verify in .env:
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...

# Wait 10-30 seconds for traces to appear
# Refresh LangSmith dashboard
```

### Issue 4: Streamlit won't start

**Solution**:
```bash
# Check if port 8501 is in use
lsof -i :8501

# Kill existing process if needed
kill -9 <PID>

# Or use different port
streamlit run app/main.py --server.port 8502
```

## ✅ Success Checklist

After completing this walkthrough, you should have:

- [x] Installed all dependencies
- [x] Configured API keys
- [x] Run the Streamlit UI
- [x] Generated at least one joke
- [x] Viewed results with metrics
- [x] Checked traces in LangSmith
- [x] Tested via CLI (optional)
- [x] Experimented with different topics

## 🎓 What You've Learned

By completing this walkthrough, you've learned:

1. **Multi-Agent Systems**
   - How agents collaborate
   - State passing between agents
   - Specialized agent roles

2. **LangGraph**
   - Workflow creation
   - Node and edge definition
   - State management

3. **LangSmith**
   - Trace configuration
   - Observability setup
   - Performance monitoring

4. **Production Patterns**
   - Environment configuration
   - Type safety with Pydantic
   - Error handling
   - Modular architecture

## 🚀 Next Steps

### Beginner
- Generate 10+ jokes on different topics
- Compare scores across topics
- Try both OpenAI and Groq
- Explore LangSmith traces

### Intermediate
- Read ARCHITECTURE.md
- Modify agent prompts
- Adjust temperature settings
- Add new example topics to UI

### Advanced
- Add a third agent (Editor/Refiner)
- Implement iterative refinement loop
- Add conditional routing based on score
- Create FastAPI endpoint
- Deploy to cloud

## 📚 Additional Resources

- **Full Documentation**: README.md
- **Quick Setup**: QUICKSTART.md
- **Architecture Details**: ARCHITECTURE.md
- **Project Overview**: PROJECT_SUMMARY.md

## 🎉 Congratulations!

You've successfully:
- ✅ Set up a complete multi-agent system
- ✅ Generated AI-powered jokes
- ✅ Evaluated content with structured metrics
- ✅ Traced execution with LangSmith
- ✅ Explored a production-ready POC

**Now go create some laughs! 🎭**

---

**Questions or issues?** Check the troubleshooting section or review the documentation.

