"""Main MCP server implementation."""
import asyncio
import json
from typing import Any, Sequence
from fastapi import FastAPI
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import AnyUrl

# Import tools
from .tools.weather import weather_tool
from .tools.news import news_tool
from .tools.file_manager import file_manager
from .tools.web_fetcher import web_fetcher
from .tools.calculator import calculator
from .tools.cli import cli_utils
from .utils.config import config

# Initialize MCP server
mcp = Server("ai-agent-server")
print("MCP AI Agent Server initialized...")

@mcp.list_tools()
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
            name="cli_utils",
            description="Execute shell commands asynchronously with timeout and working directory options",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute"
                    },
                    "cwd": {
                        "type": "string",
                        "description": "Working directory for command execution (optional)",
                        "default": "."
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (optional)"
                    }
                },
                "required": ["command"]
            }
        ),
    ]

# Tool routing dictionary
tool2call = {
    # Weather tools
    "get_weather": weather_tool.get_weather,
    
    # News tools
    "fetch_news": news_tool.fetch_news,
    
    # File management tools
    "create_file": file_manager.create_file,
    "read_file": file_manager.read_file,
    "delete_file": file_manager.delete_file,
    "search_files": file_manager.search_files,
    "list_directory": file_manager.list_directory,
    
    # Web tools
    "fetch_webpage": web_fetcher.fetch_webpage,
    
    # Calculator tools
    "calculate": calculator.calculate,
    "convert_units": calculator.convert_units,

    # CLI utilities
    "cli_utils": cli_utils.execute,
}

@mcp.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution."""
    
    try:
        if name in tool2call:
            result = await tool2call[name](**arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        # Format result as JSON
        return [
            TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )
        ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": f"Error executing {name}: {str(e)}"}, indent=2)
            )
        ]

async def stdio_run():
    """Run the MCP server with stdio."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            mcp.create_initialization_options()
        )

def sse_run():
    """Run the MCP server with SSE."""
    app = FastAPI(title="MCP AI Agent ASGI Server")

    from .utils.sse_utils import sse_server
    app.mount("/", sse_server(mcp))

    @app.get("/health")
    async def health():
        return {"status": "MCP HEALTHY"}

    import uvicorn
    uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)

if __name__ == "__main__":
    # uv run python -m src.server --sse (unless stdio)
    
    config.ensure_directories() # Ensure directories exist
    config.validate() # Validate configuration

    import sys
    if "--sse" in sys.argv:
        sse_run()
    else:
        asyncio.run(stdio_run())
