import sys
from ..server import MCPServer, logger
from ..tools.web_fetcher_tools import web_fetcher
from ..utils.config import config


if __name__ == "__main__":
    tool_mapping = {
        "web_fetcher": web_fetcher.fetch_webpage,
        # Add other tools as needed
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())
