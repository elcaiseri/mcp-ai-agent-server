import sys
from ..server import MCPServer, logger
from ..tools.file_manager_tools import file_manager
from ..utils.config import config


if __name__ == "__main__":
    tool_mapping = {
        # File management tools
        "create_file": file_manager.create_file,
        "read_file": file_manager.read_file,
        "delete_file": file_manager.delete_file,
        "search_files": file_manager.search_files,
        "list_directory": file_manager.list_directory,
        "update_file": file_manager.update_file,
        "retrieve_current_working_directory": file_manager.retrieve_current_working_directory,
    }

    mcp = MCPServer(tool_mapping)

    if "--sse" in sys.argv:
        logger.info("Running in SSE mode on %s:%d", config.SERVER_HOST, config.SERVER_PORT)
        mcp.sse_run()
    else:
        logger.info("Running in stdio mode")
        import asyncio
        asyncio.run(mcp.stdio_run())
