# MCP AI Agent Server

A dual-mode AI agent system that combines the Model Context Protocol (MCP) server capabilities with a standalone CLI agent, powered by LangChain.

## 🎯 Two Modes of Operation

### 1. **MCP Server Mode** 
Run as an MCP server that can be connected to any MCP client (like Claude Desktop) or inspected using the MCP Inspector.

### 2. **CLI Agent Mode**
Run as a standalone command-line agent for direct interaction and task execution.

## ✨ Capabilities

- 🌐 **API Interactions**: Fetch weather data, news articles, and more
- 📁 **File Management**: Read, write, search, and organize files
- 🔍 **Web Scraping**: Extract data from websites
- 📊 **Data Processing**: Analyze and transform data
- 💡 **AI-Powered Tasks**: Use LangChain for intelligent decision-making

## 🛠️ Tools Available

1. **Weather Tool**: Get current weather for any location
2. **News Tool**: Fetch latest news articles by topic
3. **File Manager**: Create, read, update, delete files
4. **Web Fetcher**: Download and parse web content
5. **Calculator**: Perform complex calculations
6. **Search Tool**: Search files and data
7. **AI Agent**: LangChain-powered reasoning and task execution

## 📦 Installation

### Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js (for MCP Inspector)

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

Required API keys in `.env`:
```env
OPENAI_API_KEY=your_openai_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
NEWS_API_KEY=your_news_api_key
```

## 🚀 Usage

### Mode 1: MCP Server with Inspector

The MCP server can be tested and debugged using the official MCP Inspector tool.

**Start the server with inspector:**
```bash
npx @modelcontextprotocol/inspector uv run python -m src.server
```

This will:
- Launch the MCP server
- Open the MCP Inspector in your browser
- Allow you to test all available tools interactively
- View request/response logs in real-time

**Connect to MCP Clients:**

Add to your MCP client configuration (e.g., Claude Desktop):

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

### Mode 2: Standalone CLI Agent

Run the agent directly from the command line for interactive sessions.

**Start the CLI agent:**
```bash
uv run python -m src.agent
```

**Example interactions:**
```
> What's the weather in Tokyo?
> Fetch the latest news about AI
> Create a file called notes.txt with today's summary
> Search for all Python files in the current directory
```

The CLI agent uses LangChain to:
- Understand natural language commands
- Select appropriate tools automatically
- Chain multiple operations together
- Provide conversational responses

## 📚 Tool Examples

### Weather Tool
```python
# Get current weather for a location
get_weather(location="New York")
# Returns: temperature, conditions, humidity, wind speed
```

### News Tool
```python
# Get latest news on a topic
fetch_news(topic="technology", limit=5)
# Returns: list of articles with title, description, URL
```

### File Operations
```python
# Create a file
create_file(path="data/output.txt", content="Hello World")

# Read a file
read_file(path="data/input.txt")

# Search files
search_files(directory=".", pattern="*.py")
```

### Web Fetching
```python
# Fetch webpage content
fetch_webpage(url="https://example.com")
# Returns: parsed HTML content and text
```

### AI Agent Tasks
```python
# Execute complex multi-step tasks
execute_agent_task(task="Analyze the weather in Tokyo and write a report")
```

## 🏗️ Architecture

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
├── .env.example           # Environment template
└── README.md
```

## 🔧 Development

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

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.