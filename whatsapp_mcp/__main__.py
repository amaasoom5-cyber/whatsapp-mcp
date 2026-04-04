"""
Entry point for running the WhatsApp MCP server.

Usage:
    python -m whatsapp_mcp
"""

from whatsapp_mcp.server import mcp


def main():
    mcp.run()


if __name__ == "__main__":
    main()
