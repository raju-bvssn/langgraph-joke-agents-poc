# 🚀 Lovable Deployment Guide

Complete guide to deploying the LangGraph Joke Agents POC to Lovable.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [GitHub Setup](#github-setup)
3. [Lovable Configuration](#lovable-configuration)
4. [Environment Variables](#environment-variables)
5. [Deployment](#deployment)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)
8. [Production Considerations](#production-considerations)

---

## 📦 Prerequisites

Before deploying, ensure you have:

### Required Accounts

1. **GitHub Account** - [Sign up](https://github.com/signup)
2. **Lovable Account** - [Sign up](https://lovable.dev)
3. **At least ONE LLM Provider API Key**:
   - 🟢 **Groq** (FREE, recommended) - [Get key](https://console.groq.com/keys)
   - 💰 **OpenAI** (paid) - [Get key](https://platform.openai.com/api-keys)
   - 🟢 **HuggingFace** (FREE) - [Get key](https://huggingface.co/settings/tokens)
   - 🟡 **Together AI** (free trial) - [Get key](https://api.together.xyz/settings/api-keys)
   - 🟡 **DeepInfra** (free trial) - [Get key](https://deepinfra.com/dash/api_keys)

4. **LangSmith API Key** (optional, for observability) - [Get key](https://smith.langchain.com/settings)

### System Requirements

- Git installed locally
- Terminal/command line access
- Project files (this repository)

---

## 🐙 GitHub Setup

### Step 1: Initialize Git Repository

If not already done:

```bash
cd langgraph-joke-agents-poc
git init
```

### Step 2: Stage All Files

```bash
git add .
```

**Verify** that sensitive files are ignored:
```bash
git status --ignored
```

You should see `.env` listed under "Ignored files" ✅

### Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: Lovable-ready LangGraph Joke System POC"
```

### Step 4: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. **Repository name**: `langgraph-joke-agents-poc`
3. **Description**: "Multi-agent joke generation system with LangGraph, LangChain & LangSmith"
4. **Visibility**: Choose Public or Private
5. ⚠️ **DO NOT** check:
   - "Add a README file"
   - "Add .gitignore"
   - "Choose a license"
6. Click **"Create repository"**

### Step 5: Link Local Repo to GitHub

Replace `<your-username>` with your GitHub username:

```bash
git branch -M main
git remote add origin https://github.com/<your-username>/langgraph-joke-agents-poc.git
```

### Step 6: Push to GitHub

```bash
git push -u origin main
```

### ✅ Verify GitHub Setup

Visit your repository: `https://github.com/<your-username>/langgraph-joke-agents-poc`

You should see:
- ✅ All project files
- ✅ `main.py` in the root directory
- ✅ `requirements.txt` present
- ✅ `.env` NOT present (correctly ignored)

---

## ⚙️ Lovable Configuration

### Step 1: Connect GitHub to Lovable

1. Log in to [lovable.dev](https://lovable.dev)
2. Click **"New Project"** or **"Import from GitHub"**
3. Authorize Lovable to access your GitHub account
4. Select repository: `<your-username>/langgraph-joke-agents-poc`
5. Grant required permissions
6. Click **"Import"**

### Step 2: Project Settings

Lovable will auto-detect:
- ✅ **Framework**: Streamlit
- ✅ **Build Command**: `pip install -r requirements.txt`
- ✅ **Start Command**: `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`

If these are not auto-detected, configure manually in **Settings → Build & Deploy**.

---

## 🔐 Environment Variables

### Navigate to Environment Variables

In your Lovable project:
1. Go to **Settings**
2. Click **Environment Variables**
3. Add the following variables:

### Required Variables

#### Option A: Using Groq (Free, Recommended)

```bash
GROQ_API_KEY=gsk_your_actual_groq_key_here
LANGCHAIN_API_KEY=ls_your_actual_langsmith_key_here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_TRACING_V2=true
LLM_PROVIDER=groq
```

#### Option B: Using OpenAI (Paid)

```bash
OPENAI_API_KEY=sk-your_actual_openai_key_here
LANGCHAIN_API_KEY=ls_your_actual_langsmith_key_here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=joke-agent-poc
LANGCHAIN_TRACING_V2=true
LLM_PROVIDER=openai
```

### Optional Additional Providers

If you want to enable multiple providers for runtime selection:

```bash
HUGGINGFACE_API_KEY=hf_your_actual_key_here
TOGETHER_API_KEY=your_actual_key_here
DEEPINFRA_API_KEY=your_actual_key_here
```

### ⚠️ Important Notes

- **DO NOT** wrap values in quotes in Lovable UI
- **DO NOT** use placeholder values like `sk-your-key-here`
- Replace all `your_actual_key_here` with real API keys
- You can leave LangSmith keys empty if you don't want tracing
- At least ONE LLM provider key is required

---

## 🚀 Deployment

### Step 1: Trigger Deployment

After adding environment variables:
1. Click **"Deploy"** or **"Save & Deploy"**
2. Lovable will begin building your project

### Step 2: Monitor Build Logs

Watch the deployment logs for:
- ✅ Installing dependencies from `requirements.txt`
- ✅ Starting Streamlit server
- ✅ Health check passing

### Step 3: Get Your Deployment URL

Once deployment succeeds, Lovable will provide:
- **Public URL**: `https://your-project-name.lovable.app`

---

## ✅ Verification

### Test 1: Application Loads

1. Open your Lovable deployment URL
2. Verify the page loads without errors
3. Check the sidebar appears

**Expected**: Streamlit UI loads with "LangGraph Joke Agents POC" header

### Test 2: Environment Configuration

In the sidebar, check **"Environment Status"**:
- ✅ Should show "Configured" for your LLM provider
- ✅ Should show "Configured" for LangSmith (if keys provided)

**If it shows "⚠️ Not configured"**:
- Go back to Lovable Settings → Environment Variables
- Verify keys are correct and saved

### Test 3: Generate a Joke

1. Select **Performer Provider** (e.g., Groq)
2. Select **Performer Model** (e.g., llama-3.3-70b-versatile)
3. Select **Critic Provider** and **Model**
4. Enter a topic: "programming"
5. Click **"Generate Joke"**

**Expected**:
- Joke appears within 5-10 seconds
- Evaluation displays with metrics
- Three action buttons appear (✅ Refine, ❌ Re-evaluate, 🎉 I'm all set)

### Test 4: Refinement Loop

1. Click **"✅ Refine Joke"**
2. Wait for revised joke and new evaluation
3. Verify both Cycle 1 and Cycle 2 are visible

**Expected**:
- Previous cycle collapses into expander
- New cycle displays with buttons
- History preserved

### Test 5: LangSmith Tracing (Optional)

If you configured LangSmith:
1. Go to [smith.langchain.com](https://smith.langchain.com)
2. Navigate to your project: "joke-agent-poc"
3. Verify traces appear for your joke generation

---

## 🐛 Troubleshooting

### Issue: "Invalid API Key" Error

**Symptoms**: Error message "API Key not found" or "401 Unauthorized"

**Solutions**:
1. Go to Lovable Settings → Environment Variables
2. Verify keys are **not placeholder values**
3. Ensure no extra spaces or quotes
4. Re-generate API keys if needed
5. Click "Save & Deploy" after changes

### Issue: "No module named 'openai'" or "No module named 'langchain'"

**Symptoms**: ImportError in deployment logs

**Solutions**:
1. Verify `requirements.txt` is in your repository root
2. Ensure it includes all dependencies:
   ```
   langchain==0.3.13
   langchain-openai==0.2.14
   langchain-groq==0.2.1
   openai>=1.12.0
   streamlit==1.40.2
   # ... (see full requirements.txt)
   ```
3. Push changes to GitHub:
   ```bash
   git add requirements.txt
   git commit -m "Update dependencies"
   git push
   ```
4. Redeploy in Lovable

### Issue: Models Not Showing in Dropdown

**Symptoms**: Empty or missing model options

**Solutions**:
1. Check that your API key is valid
2. For OpenAI: Ensure you have a funded account
3. Try switching to Groq (free tier, more reliable)
4. Check browser console for errors (F12)

### Issue: LangSmith Traces Not Appearing

**Symptoms**: No traces in LangSmith dashboard

**Solutions**:
1. Verify `LANGCHAIN_TRACING_V2=true` (no quotes)
2. Check `LANGCHAIN_API_KEY` is valid
3. Ensure `LANGCHAIN_PROJECT` matches dashboard project name
4. LangSmith can take 30-60 seconds to show traces

### Issue: Port Binding Errors

**Symptoms**: "Address already in use" or similar

**Solutions**:
- Lovable handles port binding automatically via `$PORT`
- If error persists, check deployment logs
- Contact Lovable support if issue continues

### Issue: Slow Performance

**Symptoms**: Long wait times for joke generation

**Causes & Solutions**:
| Provider | Speed | Solution |
|----------|-------|----------|
| HuggingFace | Slowest | Switch to Groq or OpenAI |
| Groq | Fastest (free) | Keep using (recommended) |
| OpenAI | Fast | Use if you have credits |
| Together AI | Moderate | Check rate limits |
| DeepInfra | Varies | Ensure positive balance |

---

## 🏭 Production Considerations

### Security

✅ **DO**:
- Rotate API keys regularly
- Use separate keys for dev/staging/prod
- Monitor API usage in provider dashboards
- Enable LangSmith for observability

❌ **DON'T**:
- Commit `.env` files
- Share API keys publicly
- Use personal keys in production
- Ignore security warnings

### Performance

**Optimize for Speed**:
1. Use Groq for fastest free inference
2. Use OpenAI for highest quality
3. Consider caching responses
4. Monitor LangSmith for slow traces

**Optimize for Cost**:
1. Start with Groq (free)
2. Add OpenAI selectively
3. Monitor API usage daily
4. Set provider-specific rate limits

### Monitoring

**LangSmith Dashboard**:
- Track token usage
- Monitor latency
- Debug failed requests
- Analyze agent behavior

**Lovable Logs**:
- Check application logs
- Monitor deployment health
- Review error traces

### Scaling

**Current Setup**: Single Streamlit instance
**If traffic increases**:
- Consider async processing
- Add Redis for session state
- Implement request queuing
- Move to FastAPI backend

---

## 📞 Support

### Resources

- **Lovable Docs**: [lovable.dev/docs](https://lovable.dev/docs)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **LangGraph Docs**: [langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)
- **LangSmith Docs**: [docs.smith.langchain.com](https://docs.smith.langchain.com/)

### Getting Help

1. **Check this guide** for common issues
2. **Review deployment logs** in Lovable
3. **Test locally first**: `streamlit run main.py`
4. **Open an issue** on GitHub if you find bugs

---

## ✅ Deployment Checklist

Before going live:

- [ ] GitHub repository created and pushed
- [ ] At least one LLM provider API key obtained
- [ ] LangSmith API key obtained (optional)
- [ ] Lovable account created
- [ ] GitHub connected to Lovable
- [ ] Environment variables added in Lovable
- [ ] Deployment successful
- [ ] Application loads in browser
- [ ] Environment status shows "Configured"
- [ ] Test joke generation works
- [ ] Refinement loop buttons appear
- [ ] LangSmith traces visible (if configured)
- [ ] No console errors (F12)
- [ ] Tested on mobile (optional)
- [ ] Shared URL with team/users

---

**Congratulations! Your LangGraph Joke Agents POC is now live on Lovable!** 🎉

For questions or issues, refer to the [main README](./README.md) or open an issue on GitHub.

