"""Main entry point for running the MCP server."""
from .ai_agent import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
