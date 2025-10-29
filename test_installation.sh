#!/bin/bash

# Quick test script to verify the installation

echo "🧪 Testing MCP AI Agent Server Installation"
echo "=========================================="
echo ""

# Check Python version
echo "1️⃣  Checking Python version..."
python3 --version
echo ""

# Check uv
echo "2️⃣  Checking uv installation..."
if command -v uv &> /dev/null; then
    echo "✅ uv is installed: $(uv --version)"
else
    echo "❌ uv is not installed"
    echo "   Run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo ""

# Check virtual environment
echo "3️⃣  Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "✅ Virtual environment exists"
else
    echo "❌ Virtual environment not found"
    echo "   Run: ./setup.sh"
    exit 1
fi
echo ""

# Check .env file
echo "4️⃣  Checking environment configuration..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    
    # Check for API keys (without revealing them)
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "   ✅ OpenAI API key configured"
    else
        echo "   ⚠️  OpenAI API key not set (AI agent will be disabled)"
    fi
    
    if grep -q "OPENWEATHER_API_KEY=..*" .env; then
        echo "   ✅ Weather API key configured"
    else
        echo "   ⚠️  Weather API key not set"
    fi
    
    if grep -q "NEWS_API_KEY=..*" .env; then
        echo "   ✅ News API key configured"
    else
        echo "   ⚠️  News API key not set"
    fi
else
    echo "❌ .env file not found"
    echo "   Run: cp .env.example .env"
    echo "   Then edit .env with your API keys"
    exit 1
fi
echo ""

# Test imports
echo "5️⃣  Testing Python imports..."
uv run python -c "
import sys
try:
    import mcp
    print('   ✅ mcp')
except ImportError:
    print('   ❌ mcp - run: uv pip install -e .')
    sys.exit(1)

try:
    import httpx
    print('   ✅ httpx')
except ImportError:
    print('   ❌ httpx - run: uv pip install -e .')
    sys.exit(1)

try:
    import aiofiles
    print('   ✅ aiofiles')
except ImportError:
    print('   ❌ aiofiles - run: uv pip install -e .')
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
    print('   ✅ beautifulsoup4')
except ImportError:
    print('   ❌ beautifulsoup4 - run: uv pip install -e .')
    sys.exit(1)

try:
    import langchain
    print('   ✅ langchain')
except ImportError:
    print('   ❌ langchain - run: uv pip install -e .')
    sys.exit(1)

print('   ✅ All core dependencies installed')
"
echo ""

# Test calculator (no API key needed)
echo "6️⃣  Testing calculator tool..."
uv run python -c "
from src.tools.calculator import calculator
result = calculator.calculate('2 + 2')
if result['success'] and result['result'] == 4:
    print('   ✅ Calculator tool working')
else:
    print('   ❌ Calculator tool failed')
    exit(1)
"
echo ""

# Run pytest
echo "7️⃣  Running test suite..."
uv run pytest tests/ -v --tb=short
echo ""

echo "=========================================="
echo "✅ Installation verification complete!"
echo ""
echo "Next steps:"
echo "1. Configure API keys in .env file"
echo "2. Run demo: uv run python examples/usage_demo.py"
echo "3. Start server: uv run python -m src.server"
echo ""
echo "Documentation:"
echo "- README.md - Project overview"
echo "- QUICKSTART.md - Getting started"
echo "- docs/API.md - API reference"
echo "- PROJECT_SUMMARY.md - Complete summary"
echo ""
