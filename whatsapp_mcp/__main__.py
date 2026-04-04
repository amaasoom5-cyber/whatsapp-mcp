"""
Entry point for running the WhatsApp MCP server.

Usage:
    python -m whatsapp_mcp                          # stdio (default)
    python -m whatsapp_mcp --transport sse           # HTTP+SSE on port 8000
    python -m whatsapp_mcp --transport streamable-http  # Streamable HTTP
    python -m whatsapp_mcp --transport sse --port 3000  # custom port
"""

import argparse

from whatsapp_mcp.server import mcp


def main():
    parser = argparse.ArgumentParser(description="WhatsApp MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to for HTTP transports (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transports (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport in ("sse", "streamable-http"):
        mcp.settings.host = args.host
        mcp.settings.port = args.port

    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
