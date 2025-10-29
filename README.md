# MCP AI Agent Server

A real-world Model Context Protocol (MCP) server powered by LangChain that enables AI agents to perform actual tasks including:

- 🌐 **API Interactions**: Fetch weather data, news articles, and more
- 📁 **File Management**: Read, write, search, and organize files
- 🔍 **Web Scraping**: Extract data from websites
- 📊 **Data Processing**: Analyze and transform data
- 💡 **AI-Powered Tasks**: Use LangChain for intelligent decision-making

## Features

### Tools Available

1. **Weather Tool**: Get current weather for any location
2. **News Tool**: Fetch latest news articles by topic
3. **File Manager**: Create, read, update, delete files
4. **Web Fetcher**: Download and parse web content
5. **Calculator**: Perform complex calculations
6. **Search Tool**: Search files and data
7. **AI Agent**: LangChain-powered reasoning and task execution

## Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/elcaiseri/mcp-ai-agent-server.git
cd mcp-ai-agent-server
```

2. Install dependencies using uv:
```bash
uv pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the server:
```bash
uv run python -m src.server
```

## Configuration

Edit `.env` file with your API keys:

- `OPENAI_API_KEY`: OpenAI API key for LangChain
- `OPENWEATHER_API_KEY`: OpenWeatherMap API key
- `NEWS_API_KEY`: News API key

## Usage

### As MCP Server

The server implements the Model Context Protocol and can be connected to any MCP client (like Claude Desktop).

Add to your MCP client configuration:

```json
{
  "mcpServers": {
    "ai-agent": {
      "command": "uv",
      "args": ["run", "python", "-m", "src.server"],
      "cwd": "/path/to/mcp-ai-agent-server"
    }
  }
}
```

### Available Tools

#### 1. Get Weather
```python
# Get current weather for a location
get_weather(location="New York")
```

#### 2. Fetch News
```python
# Get latest news on a topic
fetch_news(topic="technology", limit=5)
```

#### 3. File Operations
```python
# Create a file
create_file(path="data/output.txt", content="Hello World")

# Read a file
read_file(path="data/input.txt")

# Search files
search_files(directory=".", pattern="*.py")
```

#### 4. Web Fetching
```python
# Fetch webpage content
fetch_webpage(url="https://example.com")
```

#### 5. AI Agent Tasks
```python
# Execute complex tasks using LangChain
execute_agent_task(task="Analyze the weather in Tokyo and write a report")
```

## Architecture

```
mcp-ai-agent-server/
├── src/
│   ├── server.py          # Main MCP server implementation
│   ├── tools/             # Individual tool implementations
│   │   ├── weather.py
│   │   ├── news.py
│   │   ├── file_manager.py
│   │   ├── web_fetcher.py
│   │   └── calculator.py
│   ├── agent/             # LangChain agent setup
│   │   └── ai_agent.py
│   └── utils/             # Utilities
│       └── config.py
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
└── README.md
```

## Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black src/
uv run ruff check src/
```

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Repository

GitHub: [https://github.com/elcaiseri/mcp-ai-agent-server](https://github.com/elcaiseri/mcp-ai-agent-server)
