import sys
from ..server import MCPServer, logger
from ..tools.cli_tools import cli_utils
from ..utils.config import config


if __name__ == "__main__":
    tool_mapping = {
        # CLI utilities
        "execute_command": cli_utils.execute_command,
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())
