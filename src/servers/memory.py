import sys
from ..server import MCPServer, logger
from ..tools.memory_tools import memory
from ..utils.config import config


if __name__ == "__main__":
    tool_mapping = {
        # Memory management tools
        "store_memory": memory.store_memory,
        "forget_memory": memory.forget_memory,
        "retrieve_memory": memory.retrieve_memory,
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())
