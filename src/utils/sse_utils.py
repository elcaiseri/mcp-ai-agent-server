from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route

def sse_server(mcp: Server) -> Starlette:
    """Create an SSE server for the given MCP server."""
    sse = SseServerTransport("/messages/")

    class HandleSSE:
        def __init__(self, sse, mcp):
            self.sse = sse
            self.mcp = mcp

        async def __call__(self, scope, receive, send):
            async with self.sse.connect_sse(scope, receive, send) as (read_stream, write_stream):
                await self.mcp.run(
                    read_stream,
                    write_stream,
                    self.mcp.create_initialization_options()
                )

    class HandleMessages:
        def __init__(self, sse):
            self.sse = sse

        async def __call__(self, scope, receive, send):
            await self.sse.handle_post_message(scope, receive, send)

    routes = [
        Route("/sse", endpoint=HandleSSE(sse, mcp), methods=["GET"]),
        Route("/messages", endpoint=HandleMessages(sse), methods=["POST"])
    ]

    return Starlette(routes=routes)
