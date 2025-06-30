"""Wiki search tool for MediaWiki API MCP integration."""

import logging
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_search_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_search tool with the MCP server."""

    @mcp.tool()
    async def wiki_search(
        query: str,
        namespaces: list[int] | None = None,
        limit: int = 10,
        offset: int = 0,
        what: str = "text",
        info: list[str] | None = None,
        prop: list[str] | None = None,
        interwiki: bool = False,
        enable_rewrites: bool = True,
        srsort: str = "relevance",
        qiprofile: str = "engine_autoselect",
    ) -> str:
        """Search for pages using MediaWiki's search API.

    Args:
        query: Search query string (required)
        namespaces: List of namespace IDs to search in (default: [0] for main namespace)
        limit: Maximum number of results (1-500, default: 10)
        offset: Search result offset for pagination (default: 0)
        what: Type of search - "text", "title", or "nearmatch" (default: "text")
        info: Metadata to return (options: rewrittenquery, suggestion, totalhits)
        prop: Properties to return for each search result
        interwiki: Include interwiki results if available (default: false)
        enable_rewrites: Enable internal query rewriting for better results (default: true)
        srsort: Sort order of returned results (default: relevance)
        qiprofile: Query independent ranking profile (default: engine_autoselect)
    """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_search

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "query": query,
                    "namespaces": namespaces,
                    "limit": limit,
                    "offset": offset,
                    "what": what,
                    "info": info,
                    "prop": prop,
                    "interwiki": interwiki,
                    "enable_rewrites": enable_rewrites,
                    "srsort": srsort,
                    "qiprofile": qiprofile,
                }

                result = await handle_search(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki search failed: {e}")
            return f"Error: {str(e)}"
