#!/bin/bash

# Setup script for the LangGraph Joke Agents POC

echo "🎭 Setting up LangGraph Joke Agents POC..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  No .env file found!"
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "📝 Please edit .env and add your API keys:"
    echo "   - OPENAI_API_KEY or GROQ_API_KEY"
    echo "   - LANGCHAIN_API_KEY"
    echo ""
else
    echo "✓ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Edit .env and add your API keys"
echo "  3. Run the app: streamlit run app/main.py"
echo "  4. Or test via CLI: python test_workflow.py \"your topic\""
echo ""

