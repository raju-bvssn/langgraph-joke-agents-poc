# 🚀 Deployment Guide

Options for deploying the LangGraph Joke Agents POC to production.

## 📋 Deployment Options

1. **Streamlit Cloud** (Easiest)
2. **Docker + Cloud Run** (Recommended)
3. **AWS/Azure/GCP** (Enterprise)
4. **FastAPI + Vercel** (API-first)

---

## 1️⃣ Streamlit Cloud (Free & Easy)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free)

### Steps

1. **Push to GitHub**

```bash
cd langgraph-joke-agents-poc
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/joke-agents.git
git push -u origin main
```

2. **Deploy to Streamlit Cloud**

- Visit https://share.streamlit.io
- Click "New app"
- Select your repository
- Set main file: `app/main.py`
- Click "Deploy"

3. **Configure Secrets**

In Streamlit Cloud dashboard:

```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "sk-..."
LANGCHAIN_API_KEY = "lsv2_pt_..."
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_PROJECT = "joke-agent-poc"
LANGCHAIN_TRACING_V2 = "true"
LLM_PROVIDER = "openai"
```

4. **Access Your App**

Your app will be live at: `https://yourusername-joke-agents.streamlit.app`

### Pros
- ✅ Free hosting
- ✅ Automatic HTTPS
- ✅ Easy updates (push to GitHub)
- ✅ No server management

### Cons
- ⚠️ Limited resources
- ⚠️ May sleep after inactivity
- ⚠️ Public by default

---

## 2️⃣ Docker + Cloud Run (Recommended)

### Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY env.example .env.example

# Expose port
EXPOSE 8080

# Set environment
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run app
CMD ["streamlit", "run", "app/main.py"]
```

### Create .dockerignore

```
venv/
__pycache__/
*.pyc
.env
.git/
*.md
tests/
```

### Build and Test Locally

```bash
# Build image
docker build -t joke-agents:latest .

# Test locally
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY \
  joke-agents:latest
```

### Deploy to Google Cloud Run

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/joke-agents

# Deploy
gcloud run deploy joke-agents \
  --image gcr.io/YOUR_PROJECT_ID/joke-agents \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY,LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY
```

### Pros
- ✅ Scalable
- ✅ Pay per use
- ✅ Always available
- ✅ HTTPS included

### Cons
- ⚠️ Requires GCP account
- ⚠️ Costs for high traffic

---

## 3️⃣ AWS Elastic Beanstalk

### Create requirements.txt for EB

Already included in project!

### Create .ebextensions

```yaml
# .ebextensions/python.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.main:app
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8080
```

### Deploy

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 joke-agents

# Create environment
eb create joke-agents-env

# Set environment variables
eb setenv OPENAI_API_KEY=$OPENAI_API_KEY \
         LANGCHAIN_API_KEY=$LANGCHAIN_API_KEY

# Deploy updates
eb deploy

# Open in browser
eb open
```

---

## 4️⃣ FastAPI + Vercel (API First)

### Convert to FastAPI

Create `api/main.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.llm import get_performer_llm, get_critic_llm
from app.graph.workflow import JokeWorkflow

app = FastAPI(title="Joke Agent API")

class JokeRequest(BaseModel):
    topic: str

class JokeResponse(BaseModel):
    joke: str
    feedback: dict

@app.post("/generate", response_model=JokeResponse)
async def generate_joke(request: JokeRequest):
    try:
        workflow = JokeWorkflow(
            get_performer_llm(),
            get_critic_llm()
        )
        result = await workflow.arun(request.topic)
        
        return JokeResponse(
            joke=result["joke"],
            feedback=result["feedback"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### Create vercel.json

```json
{
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/main.py"
    }
  ]
}
```

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables
vercel env add OPENAI_API_KEY
vercel env add LANGCHAIN_API_KEY

# Production deployment
vercel --prod
```

### API Usage

```bash
curl -X POST https://your-app.vercel.app/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "programming"}'
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

Never commit:
- `.env` file
- API keys
- Secrets

Always use:
- Cloud provider secret managers
- Environment variables
- `.env.example` as template

### 2. Authentication

Add basic auth for production:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    return credentials
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/generate")
@limiter.limit("5/minute")
async def generate_joke(request: JokeRequest):
    ...
```

---

## 📊 Monitoring

### LangSmith (Already Configured!)

- All production runs traced automatically
- Monitor performance and costs
- Debug issues in real-time

### Additional Monitoring

**Application Performance**:
```python
# Add Sentry
import sentry_sdk
sentry_sdk.init(dsn="YOUR_DSN")
```

**Custom Metrics**:
```python
from prometheus_client import Counter, Histogram

joke_requests = Counter('joke_requests_total', 'Total joke requests')
joke_latency = Histogram('joke_latency_seconds', 'Joke generation latency')
```

---

## 💰 Cost Optimization

### 1. Model Selection

```python
# Development: Use cheaper models
OPENAI_MODEL = "gpt-4o-mini"  # ~$0.0001 per 1K tokens

# Production: Balance cost vs quality
# Consider caching for repeated requests
```

### 2. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_joke(topic: str):
    return workflow.run(topic)
```

### 3. Request Throttling

Limit concurrent requests to manage costs:

```python
from asyncio import Semaphore

sem = Semaphore(5)  # Max 5 concurrent

async def rate_limited_generate(topic):
    async with sem:
        return await workflow.arun(topic)
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: python -m pytest tests/
      
      - name: Deploy to Cloud Run
        run: |
          gcloud auth activate-service-account --key-file=${{ secrets.GCP_SA_KEY }}
          gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT }}/joke-agents
          gcloud run deploy joke-agents --image gcr.io/${{ secrets.GCP_PROJECT }}/joke-agents
```

---

## 📈 Scaling Considerations

### Horizontal Scaling

- Use managed services (Cloud Run, Lambda)
- Auto-scale based on load
- Load balancer for multiple instances

### Vertical Scaling

- Increase memory/CPU for complex workflows
- Use GPU instances for larger models
- Consider model optimization

### Database (Optional)

Store joke history:

```python
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JokeRecord(Base):
    __tablename__ = "jokes"
    
    id = Column(String, primary_key=True)
    topic = Column(String)
    joke = Column(String)
    feedback = Column(JSON)
    timestamp = Column(DateTime)
```

---

## ✅ Pre-Deployment Checklist

- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Error handling tested
- [ ] Rate limiting implemented
- [ ] Monitoring setup
- [ ] LangSmith tracing verified
- [ ] Health check endpoint
- [ ] HTTPS enabled
- [ ] CORS configured (if API)
- [ ] Documentation updated
- [ ] Backup strategy
- [ ] Cost limits set

---

## 🎯 Recommended Setup

**For POC/Demo**:
→ Streamlit Cloud (free, easy)

**For Production**:
→ Docker + Cloud Run (scalable, reliable)

**For API Service**:
→ FastAPI + Vercel/Cloud Run

**For Enterprise**:
→ Kubernetes + AWS/Azure/GCP

---

## 📚 Resources

- **Streamlit Cloud**: https://streamlit.io/cloud
- **Google Cloud Run**: https://cloud.google.com/run
- **AWS EB**: https://aws.amazon.com/elasticbeanstalk/
- **Vercel**: https://vercel.com
- **Docker**: https://docs.docker.com/

---

**Choose the deployment that fits your needs and scale as you grow!**

