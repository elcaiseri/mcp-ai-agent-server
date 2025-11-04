import sys
from ..server import MCPServer, logger
from ..tools.news_tools import news_tool
from ..utils.config import config


if __name__ == "__main__":
    tool_mapping = {
        # News tools
        "fetch_news": news_tool.fetch_news,
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())
