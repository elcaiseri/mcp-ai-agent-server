#!/bin/bash

# MCP AI Agent Server - Setup Script
# This script sets up the development environment

echo "=================================="
echo "MCP AI Agent Server Setup"
echo "=================================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed."
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
uv pip install -e .

# Install dev dependencies
echo ""
echo "Installing development dependencies..."
uv pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env and add your API keys"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create directories
echo ""
echo "Creating data directories..."
mkdir -p mcp_data
mkdir -p temp_files

echo ""
echo "=================================="
echo "Setup Complete! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Run the server: uv run python -m src.server"
echo "3. Or run demo: uv run python examples/usage_demo.py"
echo ""
echo "For testing: uv run pytest"
echo ""
