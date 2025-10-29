◊# Quick Start Guide

## Installation Steps

1. **Install uv** (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Clone and Setup**:
```bash
cd /Users/kassem/Desktop/mcp
uv venv
source .venv/bin/activate  # On macOS/Linux
uv pip install -e .
```

3. **Configure Environment**:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. **Run the Server**:
```bash
uv run python -m src.server
```

## Getting API Keys

### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=sk-...`

### OpenWeatherMap API Key
1. Visit https://openweathermap.org/api
2. Sign up for a free account
3. Get your API key from the dashboard
4. Add to `.env`: `OPENWEATHER_API_KEY=your_key`

### News API Key
1. Visit https://newsapi.org/
2. Register for a free account
3. Copy your API key
4. Add to `.env`: `NEWS_API_KEY=your_key`

## Testing the Server

Run the example demonstrations:
```bash
uv run python examples/usage_demo.py
```

Run tests:
```bash
uv run pytest
```

## Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ai-agent": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "src.server"
      ],
      "cwd": "/Users/kassem/Desktop/mcp",
      "env": {
        "OPENAI_API_KEY": "your-key-here",
        "OPENWEATHER_API_KEY": "your-key-here",
        "NEWS_API_KEY": "your-key-here"
      }
    }
  }
}
```

## Example Commands

Once connected through Claude Desktop, you can use natural language:

- "What's the weather in Paris?"
- "Fetch the latest news about climate change"
- "Create a file called notes.txt with my ideas"
- "Calculate the square root of 144"
- "Fetch content from https://example.com"
- "Use the AI agent to analyze weather patterns and write a summary"

## Troubleshooting

### Import Errors
```bash
uv pip install -e .
```

### API Key Issues
Check your `.env` file and ensure keys are properly set.

### MCP Connection Issues
Restart Claude Desktop after configuration changes.
