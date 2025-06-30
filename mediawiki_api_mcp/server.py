"""Main MCP server implementation for MediaWiki API integration."""

import logging
import os

from mcp.server.fastmcp import FastMCP

from .client import MediaWikiConfig
from .server_tools.wiki_meta_siteinfo import register_wiki_meta_siteinfo_tool
from .server_tools.wiki_opensearch import register_wiki_opensearch_tool
from .server_tools.wiki_page_delete import register_wiki_page_delete_tool
from .server_tools.wiki_page_edit import register_wiki_page_edit_tool
from .server_tools.wiki_page_get import register_wiki_page_get_tool
from .server_tools.wiki_page_move import register_wiki_page_move_tool
from .server_tools.wiki_page_undelete import register_wiki_page_undelete_tool
from .server_tools.wiki_search import register_wiki_search_tool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("mediawiki-api-server")


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


# Register all tools
register_wiki_page_edit_tool(mcp, get_config)
register_wiki_page_get_tool(mcp, get_config)
register_wiki_search_tool(mcp, get_config)
register_wiki_opensearch_tool(mcp, get_config)
register_wiki_page_move_tool(mcp, get_config)
register_wiki_page_delete_tool(mcp, get_config)
register_wiki_page_undelete_tool(mcp, get_config)
register_wiki_meta_siteinfo_tool(mcp, get_config)


def run_server() -> None:
    """Synchronous entry point for the MCP server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    run_server()
