"""Main MCP server implementation."""
import asyncio
import json
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl

# Import tools
from .tools.weather import weather_tool
from .tools.news import news_tool
from .tools.file_manager import file_manager
from .tools.web_fetcher import web_fetcher
from .tools.calculator import calculator
from .utils.config import config

# Import LangChain components
from langchain_core.tools import Tool as LangChainTool
from .agent.ai_agent import AIAgent

# Initialize MCP server
app = Server("ai-agent-server")
print("MCP AI Agent Server initialized...")

# Initialize LangChain tools for the AI agent
langchain_tools = [
    LangChainTool(
        name="get_weather",
        func=lambda location: asyncio.run(weather_tool.get_weather(location)),
        description="Get current weather for a location. Input: location name (e.g., 'New York' or 'London, UK')"
    ),
    LangChainTool(
        name="fetch_news",
        func=lambda topic: asyncio.run(news_tool.fetch_news(topic, limit=5)),
        description="Fetch recent news articles on a topic. Input: topic/keyword to search for"
    ),
    LangChainTool(
        name="read_file",
        func=lambda path: asyncio.run(file_manager.read_file(path)),
        description="Read content from a file. Input: file path"
    ),
    LangChainTool(
        name="fetch_webpage",
        func=lambda url: asyncio.run(web_fetcher.fetch_webpage(url)),
        description="Fetch and extract text content from a webpage. Input: URL"
    ),
    LangChainTool(
        name="calculate",
        func=lambda expr: calculator.calculate(expr),
        description="Perform mathematical calculations. Input: mathematical expression (e.g., '2+2', 'sqrt(16)')"
    ),
]

# Initialize AI agent
ai_agent = AIAgent(langchain_tools)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        Tool(
            name="get_weather",
            description="Get current weather information for a specified location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name or 'City, Country Code' (e.g., 'New York' or 'London, UK')"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="fetch_news",
            description="Fetch recent news articles on a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Topic or keyword to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of articles to return (default: 5)",
                        "default": 5
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="create_file",
            description="Create a new file with specified content",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path (relative to data directory or absolute)"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="read_file",
            description="Read content from a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_file",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to delete"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="search_files",
            description="Search for files matching a pattern in a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in",
                        "default": "."
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., '*.txt', 'data_*')",
                        "default": "*"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_directory",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory path to list",
                        "default": "."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="fetch_webpage",
            description="Fetch and extract text content from a webpage",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL to fetch"
                    },
                    "extract_text": {
                        "type": "boolean",
                        "description": "Extract clean text from HTML",
                        "default": True
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="calculate",
            description="Perform mathematical calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression (e.g., '2+2', 'sqrt(16)', 'sin(pi/2)')"
                    }
                },
                "required": ["expression"]
            }
        ),
        Tool(
            name="convert_units",
            description="Convert between different units (temperature, length, weight)",
            inputSchema={
                "type": "object",
                "properties": {
                    "value": {
                        "type": "number",
                        "description": "Value to convert"
                    },
                    "from_unit": {
                        "type": "string",
                        "description": "Source unit"
                    },
                    "to_unit": {
                        "type": "string",
                        "description": "Target unit"
                    }
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        ),
        Tool(
            name="execute_agent_task",
            description="Execute a complex task using AI agent with access to all tools. Use this for multi-step tasks that require reasoning.",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description in natural language"
                    }
                },
                "required": ["task"]
            }
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution."""
    
    try:
        # Route to appropriate tool
        if name == "get_weather":
            result = await weather_tool.get_weather(arguments["location"])
        
        elif name == "fetch_news":
            result = await news_tool.fetch_news(
                arguments["topic"],
                arguments.get("limit", 5)
            )
        
        elif name == "create_file":
            result = await file_manager.create_file(
                arguments["path"],
                arguments["content"]
            )
        
        elif name == "read_file":
            result = await file_manager.read_file(arguments["path"])
        
        elif name == "delete_file":
            result = await file_manager.delete_file(arguments["path"])
        
        elif name == "search_files":
            result = file_manager.search_files(
                arguments.get("directory", "."),
                arguments.get("pattern", "*")
            )
        
        elif name == "list_directory":
            result = await file_manager.list_directory(
                arguments.get("directory", ".")
            )
        
        elif name == "fetch_webpage":
            result = await web_fetcher.fetch_webpage(
                arguments["url"],
                arguments.get("extract_text", True)
            )
        
        elif name == "calculate":
            result = calculator.calculate(arguments["expression"])
        
        elif name == "convert_units":
            result = calculator.convert_units(
                arguments["value"],
                arguments["from_unit"],
                arguments["to_unit"]
            )
        
        elif name == "execute_agent_task":
            if not ai_agent.is_available():
                result = {
                    "error": "AI Agent not available. Please configure OPENAI_API_KEY."
                }
            else:
                result = await ai_agent.execute_task(arguments["task"])
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        # Format result as JSON
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, default=str)
        )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": f"Error executing {name}: {str(e)}"
            }, indent=2)
        )]

async def main():
    """Run the MCP server."""
    # Ensure directories exist
    config.ensure_directories()
    
    # Validate configuration
    config.validate()
    
    # Run server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
