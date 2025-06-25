"""Main MCP server implementation for MediaWiki API integration."""

import asyncio
import logging
import os
from typing import Any, Dict, List, Sequence

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .client import MediaWikiClient, MediaWikiConfig
from .tools import get_edit_tools, get_search_tools
from .handlers import handle_edit_page, handle_get_page, handle_search

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Server("mediawiki-api-server")


def get_config() -> MediaWikiConfig:
    """Get MediaWiki configuration from environment variables."""
    api_url = os.getenv("MEDIAWIKI_API_URL")
    username = os.getenv("MEDIAWIKI_API_BOT_USERNAME")
    password = os.getenv("MEDIAWIKI_API_BOT_PASSWORD")
    user_agent = os.getenv("MEDIAWIKI_API_BOT_USER_AGENT", "MediaWiki-MCP-Bot/1.0")

    if not api_url:
        raise ValueError("MEDIAWIKI_API_URL environment variable is required")
    if not username:
        raise ValueError("MEDIAWIKI_API_BOT_USERNAME environment variable is required")
    if not password:
        raise ValueError("MEDIAWIKI_API_BOT_PASSWORD environment variable is required")

    return MediaWikiConfig(
        api_url=api_url,
        username=username,
        password=password,
        user_agent=user_agent
    )


@app.list_tools()
async def list_tools() -> List[types.Tool]:
    """List available MediaWiki tools."""
    tools = []
    tools.extend(get_edit_tools())
    tools.extend(get_search_tools())
    return tools


@app.call_tool()
async def call_tool(
    name: str,
    arguments: Dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle tool calls for MediaWiki operations."""
    try:
        config = get_config()

        async with MediaWikiClient(config) as client:
            if name == "wiki_page_edit":
                return await handle_edit_page(client, arguments)
            elif name == "wiki_page_get":
                return await handle_get_page(client, arguments)
            elif name == "wiki_search":
                return await handle_search(client, arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Tool call failed: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


def run_server():
    """Synchronous entry point for the MCP server."""
    asyncio.run(main())


if __name__ == "__main__":
    run_server()
