import sys
from ..server import MCPServer, logger
from ..tools.weather_tools import weather_tool
from ..utils.config import config


if __name__ == "__main__":
    tool_mapping = {
        # Weather tools
        "get_weather": weather_tool.get_weather,
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info(
            "Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT
        )
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio

        asyncio.run(mcp.stdio_run())
