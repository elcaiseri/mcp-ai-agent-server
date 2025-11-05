"""Main MCP server implementation."""
import sys
import json
import logging
from typing import Any, Sequence
from fastapi import FastAPI
from mcp.server import Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
from fastmcp.tools.tool import FunctionTool

# Import tools
from .tools.weather_tools import weather_tool
from .tools.news_tools import news_tool
from .tools.file_manager_tools import file_manager
from .tools.web_fetcher_tools import web_fetcher
from .tools.calculator_tools import calculator
from .tools.cli_tools import cli_utils
from .tools.memory_tools import memory

from .utils.config import config

config.ensure_directories() # Ensure directories exist
config.validate() # Validate configuration

# Configure logging
logging.disable(config.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Initialize MCP server
class MCPServer:
    """MCP AI Agent Server."""
    def __init__(self, tool2call: dict[str, Any]) -> Server:
        self.server = Server("ai-agent-server")
        self.tool2call = tool2call

        self.setup_tools()
        logger.info("MCP AI Agent Server initialized with %d tools", len(tool2call))

    def setup_tools(self):
        """Register tools with the MCP server."""
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools."""
            logger.debug("Listing available tools")
            return [
                FunctionTool.from_function(func, name=name, output_schema=None).to_mcp_tool()
                for name, func in self.tool2call.items()
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool execution."""
            logger.info("Executing tool: %s with arguments: %s", name, arguments)
            try:
                if name in self.tool2call:
                    result = await self.tool2call[name](**arguments)
                    logger.info("Tool %s executed successfully", name)
                else:
                    logger.error("Unknown tool requested: %s", name)
                    result = {"error": f"Unknown tool: {name}"}

                # Format result as JSON
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, indent=2, default=str)
                    )
                ]

            except Exception as e:
                logger.exception("Error executing tool %s: %s", name, str(e))
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": f"Error executing {name}: {str(e)}"}, indent=2)
                    )
                ]
        @self.server.list_resources()
        async def list_resources() -> list[Resource]:
            """List all available resources."""
            logger.debug("Listing available resources")
            return [
                Resource(
                    uri="memory://retrieve",
                    name="Retrieve Stored Memories",
                    description="Access to all user stored memories",
                    mimeType="text/plain"
                )
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            logger.info("Reading resource: %s", uri)
            if str(uri).startswith("memory"):
                logger.debug("Loading memory resource")
                return str(await memory.load_memory())
            else:
                logger.error("Unknown resource requested: %s", uri)
                return f"Unknown resource: {uri}"

    async def stdio_run(self):
        """Run the MCP server with stdio."""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting MCP server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

    def sse_run(self):
        """Run the MCP server with SSE."""
        logger.info("Initializing MCP server with SSE transport")
        app = FastAPI(title="MCP AI Agent ASGI Server")

        from .utils.sse_utils import sse_server
        app.mount("/", sse_server(self.server))

        @app.get("/health")
        async def health():
            logger.debug("Health check requested")
            return {"status": "MCP HEALTHY"}
        
        import uvicorn
        uvicorn.run(app, host=config.SERVER_HOST, port=config.SERVER_PORT)

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
        "update_file": file_manager.update_file,
        "retrieve_current_working_directory": file_manager.retrieve_current_working_directory,
        
        # Web tools
        "fetch_webpage": web_fetcher.fetch_webpage,
        
        # Calculator tools
        "calculate": calculator.calculate,
        "convert_units": calculator.convert_units,

        # CLI utilities
        "execute_command": cli_utils.execute_command,

        # Memory management tools
        "store_memory": memory.store_memory,
        "forget_memory": memory.forget_memory,
        #"retrieve_memory": memory.retrieve_memory,
    }

    mcp = MCPServer(tool2call)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())
