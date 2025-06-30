"""Wiki page get tool for MediaWiki API MCP integration."""

import logging
from typing import Callable

from mcp.server.fastmcp import FastMCP
from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_get_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_get tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_get(
        title: str = "",
        pageid: int = 0,
        method: str = "revisions",
        format: str = "wikitext",
        sentences: int = 0,
        chars: int = 0,
    ) -> str:
        """Get information and content from a MediaWiki page.

        Args:
            title: Title of the page to retrieve
            pageid: Page ID of the page to retrieve (alternative to title)
            method: Retrieval method - "revisions", "raw", "parse", or "extracts"
            format: Content format - "wikitext", "html", or "text"
            sentences: Limit extracts to this many sentences (extracts method only)
            chars: Limit extracts to this many characters (extracts method only)
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_get_page

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "title": title if title else None,
                    "pageid": pageid if pageid else None,
                    "method": method,
                    "format": format,
                    "sentences": sentences if sentences > 0 else None,
                    "chars": chars if chars > 0 else None,
                }

                result = await handle_get_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page get failed: {e}")
            return f"Error: {str(e)}"
