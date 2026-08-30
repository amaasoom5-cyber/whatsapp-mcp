"""
Minimal ASGI middleware for the WATI MCP server.

WATI credentials are loaded from Render environment variables,
so no per-request Meta credential handling is required.
"""

from starlette.types import ASGIApp, Receive, Scope, Send


class CredentialsMiddleware:
    """
    Pass-through middleware.

    Kept for compatibility with __main__.py, which still wraps
    the MCP HTTP application with CredentialsMiddleware.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):
        await self.app(scope, receive, send)
