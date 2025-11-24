# 🚀 Quick Start Guide

Get the **LangGraph Joke Agents POC** running in 5 minutes!

## ⚡ Super Quick Setup

```bash
# 1. Navigate to project
cd langgraph-joke-agents-poc

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp env.example .env

# 5. Edit .env and add your API keys
# You need:
# - Either OPENAI_API_KEY or GROQ_API_KEY
# - LANGCHAIN_API_KEY (from smith.langchain.com)

# 6. Run the app!
streamlit run app/main.py
```

## 🔑 Getting API Keys

### OpenAI (Recommended)
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### Groq (Free Alternative)
1. Visit https://console.groq.com/keys
2. Create a new API key
3. Add to `.env`: `GROQ_API_KEY=gsk-...`

### LangSmith (Required for Tracing)
1. Visit https://smith.langchain.com
2. Sign up/login
3. Go to Settings → API Keys
4. Create a new API key
5. Add to `.env`: `LANGCHAIN_API_KEY=ls-...`

## 🧪 Test Without UI

Test the workflow from command line:

```bash
# Test with default topic
python test_workflow.py

# Test with custom topic
python test_workflow.py "programming"
python test_workflow.py "coffee and cats"
```

## 📊 View Traces in LangSmith

1. Run the application and generate a joke
2. Visit https://smith.langchain.com
3. Navigate to your project: `joke-agent-poc`
4. See complete execution traces with:
   - Agent calls
   - LLM interactions
   - State transitions
   - Timing and costs

## ❓ Troubleshooting

**"No module named 'app'"**
- Make sure you're in the `langgraph-joke-agents-poc` directory
- Activate your virtual environment

**"API Key not found"**
- Check that `.env` file exists
- Verify API keys are set correctly (no quotes needed)
- Ensure no extra spaces around `=` sign

**"LangSmith traces not appearing"**
- Verify `LANGCHAIN_TRACING_V2=true` in `.env`
- Check that `LANGCHAIN_API_KEY` is valid
- Wait a few seconds for traces to appear

## 🎯 What's Next?

- Try different joke topics
- Check the feedback metrics
- View traces in LangSmith
- Experiment with different LLM providers
- Read the full [README.md](README.md) for architecture details

---

**Ready to create some jokes? Let's go! 🎭**

