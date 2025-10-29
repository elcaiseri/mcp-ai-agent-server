# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### Problem: `uv: command not found`

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Restart your terminal or source your profile
source ~/.zshrc  # for zsh
# or
source ~/.bashrc  # for bash
```

#### Problem: Import errors after installation

**Solution:**
```bash
# Make sure you're in the project directory
cd /Users/kassem/Desktop/mcp

# Install in development mode
uv pip install -e .

# Or run the full setup
./setup.sh
```

#### Problem: `ModuleNotFoundError: No module named 'mcp'`

**Solution:**
```bash
# Install the MCP SDK specifically
uv pip install 'mcp>=0.9.0'

# Or reinstall all dependencies
uv pip install -e .
```

---

### Configuration Issues

#### Problem: `.env file not found`

**Solution:**
```bash
# Create from template
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

#### Problem: API keys not working

**Solution:**
1. Check that keys are in `.env` file (not `.env.example`)
2. Ensure no extra spaces around the `=` sign
3. Don't wrap keys in quotes unless they contain spaces
4. Verify keys are valid on the provider's website

```bash
# Correct format in .env:
OPENAI_API_KEY=sk-proj-abc123...
OPENWEATHER_API_KEY=abc123...
NEWS_API_KEY=abc123...
```

---

### Runtime Issues

#### Problem: Weather tool returns error

**Possible causes:**
1. No API key configured
2. Invalid API key
3. Invalid location name
4. API rate limit exceeded

**Solution:**
```bash
# Test with a simple location
uv run python -c "
import asyncio
from src.tools.weather import weather_tool

result = asyncio.run(weather_tool.get_weather('London'))
print(result)
"

# Check your API key
grep OPENWEATHER_API_KEY .env
```

#### Problem: News API returns no results

**Possible causes:**
1. No API key configured
2. Invalid search term
3. API rate limit (100 calls/day on free tier)

**Solution:**
```bash
# Test with a common topic
uv run python -c "
import asyncio
from src.tools.news import news_tool

result = asyncio.run(news_tool.fetch_news('technology', limit=3))
print(result)
"
```

#### Problem: AI Agent not working

**Possible causes:**
1. No OpenAI API key
2. Invalid API key
3. Insufficient credits
4. Network issues

**Solution:**
```bash
# Check if API key is set
grep OPENAI_API_KEY .env

# Test OpenAI connection
uv run python -c "
from langchain_openai import ChatOpenAI
from src.utils.config import config

llm = ChatOpenAI(
    model='gpt-4o-mini',
    openai_api_key=config.OPENAI_API_KEY
)
print('✅ OpenAI connection successful')
"
```

#### Problem: File operations fail

**Possible causes:**
1. Permission issues
2. Path doesn't exist
3. Disk full

**Solution:**
```bash
# Check directories exist
ls -la mcp_data/
ls -la temp_files/

# Create if missing
mkdir -p mcp_data temp_files

# Check permissions
chmod 755 mcp_data temp_files
```

---

### MCP Integration Issues

#### Problem: Claude Desktop can't connect to server

**Solution:**

1. Check configuration file path:
```bash
# macOS
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
cat ~/.config/Claude/claude_desktop_config.json
```

2. Verify JSON syntax is correct:
```json
{
  "mcpServers": {
    "ai-agent": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.server"],
      "cwd": "/Users/kassem/Desktop/mcp"
    }
  }
}
```

3. Check the `cwd` path is correct:
```bash
# Verify path exists
ls -la /Users/kassem/Desktop/mcp
```

4. Restart Claude Desktop completely
5. Check Claude Desktop logs for errors

#### Problem: Tools not showing in Claude

**Solution:**
1. Restart Claude Desktop
2. Try reconnecting
3. Check server logs for errors
4. Verify server is running: `uv run python -m src.server`

---

### Testing Issues

#### Problem: Tests fail

**Solution:**
```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests with verbose output
uv run pytest -v --tb=short

# Run specific failing test
uv run pytest tests/test_calculator.py -v
```

#### Problem: Import errors in tests

**Solution:**
```bash
# Make sure you're running tests with uv
uv run pytest

# Not just: pytest
```

---

### Performance Issues

#### Problem: Slow API responses

**Possible causes:**
1. Network latency
2. API rate limiting
3. Large data transfers

**Solution:**
```python
# Increase timeout in tool calls
# Edit src/tools/weather.py (or other tool)

async with httpx.AsyncClient() as client:
    response = await client.get(
        url,
        timeout=30.0  # Increase from 10.0
    )
```

#### Problem: Memory issues

**Solution:**
```python
# Limit data size in tools
# For example, in web_fetcher.py:

result["text"] = text[:10000]  # Increase limit if needed
```

---

### Development Issues

#### Problem: Code formatting errors

**Solution:**
```bash
# Format code
uv run black src/

# Fix linting issues
uv run ruff check src/ --fix
```

#### Problem: Type checking errors

**Solution:**
```bash
# Install type stubs
uv pip install types-aiofiles
uv pip install types-beautifulsoup4

# Or ignore specific errors
# Add # type: ignore comment
```

---

## Debug Mode

Enable verbose logging:

```python
# Add to src/utils/config.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Getting Help

### Check Logs
```bash
# Run with verbose output
uv run python -m src.server --verbose

# Or add print statements
print(f"Debug: {variable}")
```

### Verify Installation
```bash
# Run installation test
./test_installation.sh

# Check Python version
python3 --version  # Should be 3.10+

# Check dependencies
uv pip list
```

### Clean Reinstall
```bash
# Remove virtual environment
rm -rf .venv

# Remove installed packages
rm -rf *.egg-info

# Run setup again
./setup.sh
```

## API-Specific Issues

### OpenWeatherMap
- **Rate limit**: 60 calls/minute (free tier)
- **Error 401**: Invalid API key
- **Error 404**: Location not found
- **Test endpoint**: https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY

### NewsAPI
- **Rate limit**: 100 calls/day (free tier)
- **Error 401**: Invalid API key
- **Error 426**: Upgrade required
- **Test endpoint**: https://newsapi.org/v2/everything?q=technology&apiKey=YOUR_KEY

### OpenAI
- **Rate limits**: Varies by tier
- **Error 401**: Invalid API key
- **Error 429**: Rate limit exceeded
- **Error 500**: OpenAI server error
- **Test**: https://platform.openai.com/playground

## Still Having Issues?

1. **Check existing issues**: Look at project issues on GitHub
2. **Create detailed issue**: Include error messages, steps to reproduce
3. **Ask for help**: Provide context and what you've tried
4. **Check documentation**: Review README.md, QUICKSTART.md, API.md

## Quick Diagnostics

Run this diagnostic script:

```bash
uv run python -c "
import sys
print(f'Python version: {sys.version}')

try:
    import mcp
    print('✅ mcp installed')
except ImportError:
    print('❌ mcp not installed')

try:
    import httpx
    print('✅ httpx installed')
except ImportError:
    print('❌ httpx not installed')

try:
    import langchain
    print('✅ langchain installed')
except ImportError:
    print('❌ langchain not installed')

try:
    from src.utils.config import config
    print('✅ Can import project modules')
    print(f'   Data dir: {config.DATA_DIR}')
except Exception as e:
    print(f'❌ Cannot import project: {e}')
"
```

---

**Remember**: Most issues are related to:
1. Missing API keys
2. Not running with `uv run`
3. Dependencies not installed
4. Wrong working directory

Always check these first! 🔍
