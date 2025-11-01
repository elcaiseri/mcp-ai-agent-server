"""Main MCP server implementation."""
import json
from typing import Any, Sequence
from fastapi import FastAPI
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource


# Import tools
from .tools.weather import weather_tool
from .tools.news import news_tool
from .tools.file_manager import file_manager
from .tools.web_fetcher import web_fetcher
from .tools.calculator import calculator
from .tools.cli import cli_utils
from .utils.helper import func_to_tool

# Initialize MCP server

class MCPServer:
    """MCP AI Agent Server."""
    def __init__(self, tool2call: dict[str, Any]) -> Server:
        self.server = Server("ai-agent-server")
        self.tool2call = tool2call

        self.setup_tools()
        print("MCP AI Agent Server initialized...")

    def setup_tools(self):
        """Register tools with the MCP server."""
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""

            return [
                Tool(
                    **func_to_tool(func, name)
                ) for name, func in self.tool2call.items()
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool execution."""
            try:
                if name in self.tool2call:
                    result = await self.tool2call[name](**arguments)
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
            

async def stdio_run(mcp):
    """Run the MCP server with stdio."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            mcp.create_initialization_options()
        )

def sse_run(mcp):
    """Run the MCP server with SSE."""
    app = FastAPI(title="MCP AI Agent ASGI Server")

    from .utils.sse_utils import sse_server
    app.mount("/", sse_server(mcp))

    @app.get("/health")
    async def health():
        return {"status": "MCP HEALTHY"}

    return app
if __name__ == "__main__":
    # uv run python -m src.server --sse (unless stdio)

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
    
    from .utils.config import config

    config.ensure_directories() # Ensure directories exist
    config.validate() # Validate configuration
    mcp = MCPServer(tool2call).server

    import sys

    if "--sse" in sys.argv:
        app = sse_run(mcp)
        import uvicorn
        uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)

    else:
        import asyncio
        asyncio.run(stdio_run(mcp))
