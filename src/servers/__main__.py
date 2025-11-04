from ..server import MCPServer, logger
from ..utils.config import config
import sys

from ..tools.web_fetcher_tools import web_fetcher

if __name__ == "__main__":
    tool_mapping = {
        # Add your tool mappings here
        "fetch_webpage": web_fetcher.fetch_webpage,
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())