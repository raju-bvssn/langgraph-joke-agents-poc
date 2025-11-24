# 🚀 Deployment Quick Start

**5-Minute Guide to Deploy Your LangGraph Joke Agents POC**

---

## ⚡ Prerequisites (5 minutes)

1. **Get API Keys** (at least one):
   - [Groq (FREE)](https://console.groq.com/keys) ← Recommended
   - [OpenAI](https://platform.openai.com/api-keys)
   - [LangSmith (optional)](https://smith.langchain.com/settings)

2. **Create GitHub Account** if you don't have one: [github.com/signup](https://github.com/signup)

3. **Create Lovable Account**: [lovable.dev](https://lovable.dev)

---

## 📝 Step 1: Push to GitHub (2 minutes)

```bash
cd langgraph-joke-agents-poc

# Initialize Git
git init

# Stage all files
git add .

# Verify .env is ignored
git status --ignored | grep .env  # Should show .env

# Commit
git commit -m "Initial commit: Lovable-ready LangGraph Joke System"

# Set branch name
git branch -M main
```

**Create GitHub Repo:**
1. Go to [github.com/new](https://github.com/new)
2. Name: `langgraph-joke-agents-poc`
3. Don't check any boxes
4. Click "Create repository"

**Link & Push:**
```bash
git remote add origin https://github.com/<YOUR-USERNAME>/langgraph-joke-agents-poc.git
git push -u origin main
```

✅ **Checkpoint**: Your code is now on GitHub!

---

## 🌐 Step 2: Deploy to Lovable (3 minutes)

1. **Log in to [lovable.dev](https://lovable.dev)**

2. **Click "New Project" → "Import from GitHub"**

3. **Select your repository**: `<your-username>/langgraph-joke-agents-poc`

4. **Go to Settings → Environment Variables**

5. **Add these variables** (copy-paste, replace with your real keys):

```bash
GROQ_API_KEY=gsk_YOUR_ACTUAL_GROQ_KEY_HERE
LANGCHAIN_API_KEY=ls_YOUR_ACTUAL_LANGSMITH_KEY
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_TRACING_V2=true
LLM_PROVIDER=groq
```

6. **Click "Deploy"**

7. **Wait 2-3 minutes** for build to complete

8. **Open your URL**: `https://your-project-name.lovable.app`

✅ **Done!** Your app is live!

---

## ✅ Verify Deployment (1 minute)

1. **Check environment status** in sidebar → Should show "✅ Configured"
2. **Select LLM providers** → Choose Groq for both Performer and Critic
3. **Enter topic**: "programming"
4. **Click "Generate Joke"**
5. **Verify**:
   - Joke appears
   - Evaluation appears
   - Three buttons show: ✅ Refine | ❌ Re-evaluate | 🎉 I'm all set

🎉 **Success!** Your multi-agent system is deployed!

---

## 🆘 Quick Troubleshooting

### "Invalid API Key" Error
- Double-check your API key is correct (no extra spaces)
- Ensure you used your actual key, not the placeholder
- Try regenerating the API key

### "No models available"
- Verify your Groq API key is valid
- Check you have credits (Groq free tier should work)

### "Environment not configured"
- Go back to Lovable Settings → Environment Variables
- Ensure all variables are saved
- Redeploy the project

---

## 📚 Full Documentation

For detailed guides, see:
- **[LOVABLE_DEPLOYMENT.md](./LOVABLE_DEPLOYMENT.md)** - Complete step-by-step guide
- **[DEPLOYMENT_READY.md](./DEPLOYMENT_READY.md)** - Readiness checklist
- **[README.md](./README.md)** - Full project documentation

---

## 💡 Next Steps

**After successful deployment:**
1. Test the refinement loop (click ✅ Refine Joke)
2. Check LangSmith traces (if configured)
3. Try different LLM providers
4. Share your deployed URL!

**Customize:**
- Add more LLM providers (OpenAI, HuggingFace, etc.)
- Adjust agent prompts in `app/agents/`
- Modify workflow in `app/graph/workflow.py`
- Customize UI in `app/main.py`

---

## 🔗 Useful Links

- **Your GitHub Repo**: `https://github.com/<your-username>/langgraph-joke-agents-poc`
- **Lovable Dashboard**: [lovable.dev/dashboard](https://lovable.dev/dashboard)
- **Groq Console**: [console.groq.com](https://console.groq.com)
- **LangSmith Dashboard**: [smith.langchain.com](https://smith.langchain.com)

---

**Total Time**: ~10 minutes from start to deployed app! 🚀

For help: Check [LOVABLE_DEPLOYMENT.md](./LOVABLE_DEPLOYMENT.md#troubleshooting) troubleshooting section.

