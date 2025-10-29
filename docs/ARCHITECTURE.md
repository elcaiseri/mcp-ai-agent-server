# Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────────┐
│                   MCP Client (e.g., Claude)              │
│                                                          │
│  Natural Language Request                                │
└──────────────────────┬──────────────────────────────────┘
                       │ MCP Protocol
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  MCP Server (Python)                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         Request Router & Handler               │    │
│  └───────────┬────────────────────────────────────┘    │
│              │                                          │
│  ┌───────────▼────────────────────────────────────┐    │
│  │              Tool Registry                      │    │
│  └─┬──────┬──────┬──────┬──────┬──────┬──────────┘    │
│    │      │      │      │      │      │                │
│  ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──────────┐    │
│  │Wea-│ │News│ │File│ │Web │ │Calc│ │ AI Agent   │    │
│  │ther│ │    │ │Mgr │ │    │ │    │ │ (LangChain)│    │
│  └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘ └─┬──────────┘    │
└────┼──────┼──────┼──────┼──────┼──────┼──────────────┘
     │      │      │      │      │      │
┌────▼──────▼──────▼──────▼──────▼──────▼──────────────┐
│                External Resources                      │
│                                                        │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌────────┐ │
│  │OpenW │  │News  │  │File  │  │Web   │  │OpenAI  │ │
│  │eather│  │API   │  │System│  │Sites │  │API     │ │
│  └──────┘  └──────┘  └──────┘  └──────┘  └────────┘ │
└────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. MCP Server (`src/server.py`)
- **Responsibility**: Main entry point, handles MCP protocol
- **Functions**:
  - Register and list available tools
  - Route tool calls to appropriate handlers
  - Format responses according to MCP spec
  - Manage server lifecycle

### 2. Tools (`src/tools/`)
Each tool is a self-contained module:

#### Weather Tool (`weather.py`)
- **API**: OpenWeatherMap
- **Functions**: Get current weather by location
- **Error Handling**: API key validation, location validation

#### News Tool (`news.py`)
- **API**: NewsAPI
- **Functions**: Search news by topic, date, language
- **Features**: Pagination, filtering, source selection

#### File Manager (`file_manager.py`)
- **Operations**: CRUD (Create, Read, Update, Delete)
- **Features**: Path resolution, glob patterns, directory traversal
- **Safety**: Sandboxed to data directory

#### Web Fetcher (`web_fetcher.py`)
- **Functions**: Fetch HTML, extract text, download files
- **Parser**: BeautifulSoup4 for HTML parsing
- **Features**: Text extraction, link following

#### Calculator (`calculator.py`)
- **Operations**: Arithmetic, trigonometry, unit conversion
- **Safety**: Safe eval with restricted scope
- **Units**: Temperature, length, weight

### 3. AI Agent (`src/agent/ai_agent.py`)
- **Framework**: LangChain
- **LLM**: OpenAI GPT-4
- **Capabilities**:
  - Tool selection and chaining
  - Multi-step reasoning
  - Natural language understanding
  - Error recovery

### 4. Configuration (`src/utils/config.py`)
- **Environment**: Loads from `.env`
- **Validation**: Checks required API keys
- **Directories**: Manages data/temp folders

## Data Flow

### Simple Tool Call
```
Client Request → Server → Tool → External API → Tool → Server → Client
```

### AI Agent Task
```
Client Request → Server → AI Agent
                          ↓
                    Plan Tasks
                          ↓
                    ┌─────┴─────┐
                    │           │
              Tool 1      Tool 2
                    │           │
                    └─────┬─────┘
                          ↓
                    Synthesize
                          ↓
                  Server → Client
```

## Technology Stack

### Core
- **Python 3.10+**: Modern Python features
- **MCP SDK**: Model Context Protocol implementation
- **LangChain**: AI agent framework
- **OpenAI**: LLM provider

### Libraries
- **httpx**: Async HTTP client
- **aiofiles**: Async file operations
- **BeautifulSoup4**: HTML parsing
- **Pydantic**: Data validation
- **python-dotenv**: Environment management

### Tools
- **uv**: Fast Python package manager
- **pytest**: Testing framework
- **black/ruff**: Code formatting and linting

## Design Patterns

### 1. Tool Pattern
Each tool follows a consistent interface:
```python
class Tool:
    async def operation(self, **kwargs) -> Dict[str, Any]:
        try:
            result = await self.perform_operation(**kwargs)
            return {
                "success": True,
                "data": result,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
```

### 2. Singleton Pattern
Tools are instantiated once and reused:
```python
weather_tool = WeatherTool()
```

### 3. Factory Pattern
Server routes calls to appropriate tools based on name.

### 4. Strategy Pattern
AI agent selects tools dynamically based on task.

## Security Considerations

1. **API Keys**: Stored in environment, never in code
2. **File Access**: Sandboxed to data directory
3. **Code Execution**: Calculator uses restricted eval
4. **Web Requests**: User-Agent headers, timeout limits
5. **Input Validation**: Pydantic schemas for all inputs

## Scalability

### Current State
- Single-threaded async server
- In-memory state
- File-based storage

### Future Enhancements
- Multi-process workers
- Database integration
- Caching layer (Redis)
- Rate limiting
- Authentication/authorization
- Webhooks for long-running tasks

## Testing Strategy

1. **Unit Tests**: Test individual tools
2. **Integration Tests**: Test tool combinations
3. **Mocking**: Mock external APIs
4. **Fixtures**: Reusable test data
5. **Coverage**: Aim for >80%

## Deployment Options

1. **Local Development**: Direct Python execution
2. **Claude Desktop**: MCP client integration
3. **Docker**: Container deployment
4. **Cloud Functions**: Serverless deployment
5. **Docker Compose**: Multi-container setup

## Monitoring & Logging

- **Logging**: Python logging module
- **Metrics**: Tool call counts, latencies
- **Errors**: Structured error responses
- **Debug**: Verbose mode for development

## Extension Guide

To add a new tool:

1. Create `src/tools/your_tool.py`
2. Implement tool class with async methods
3. Add tool registration in `src/server.py`
4. Add LangChain tool wrapper if needed
5. Write tests in `tests/test_your_tool.py`
6. Update documentation

Example:
```python
# src/tools/your_tool.py
class YourTool:
    async def do_something(self, param: str) -> Dict[str, Any]:
        # Implementation
        pass

your_tool = YourTool()
```

```python
# src/server.py
from .tools.your_tool import your_tool

@app.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "your_tool":
        result = await your_tool.do_something(arguments["param"])
    # ...
```
