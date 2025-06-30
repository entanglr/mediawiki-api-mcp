"""Wiki opensearch tool for MediaWiki API MCP integration."""

import logging
from typing import Callable

from mcp.server.fastmcp import FastMCP
from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_opensearch_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_opensearch tool with the MCP server."""

    @mcp.tool()
    async def wiki_opensearch(
        search: str,
        namespace: list[int] | None = None,
        limit: int = 10,
        profile: str = "engine_autoselect",
        redirects: str = "",
        format: str = "json",
        warningsaserror: bool = False,
    ) -> str:
        """Search the wiki using the OpenSearch protocol.

        Args:
            search: Search string (required)
            namespace: Namespaces to search (default: [0] for main namespace)
            limit: Maximum number of results (1-500, default: 10)
            profile: Search profile (default: "engine_autoselect")
            redirects: How to handle redirects - "return" or "resolve"
            format: Output format (default: "json")
            warningsaserror: Treat warnings as errors (default: False)
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_opensearch

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "search": search,
                    "namespace": namespace,
                    "limit": limit,
                    "profile": profile,
                    "redirects": redirects if redirects else None,
                    "format": format,
                    "warningsaserror": warningsaserror,
                }

                result = await handle_opensearch(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki opensearch failed: {e}")
            return f"Error: {str(e)}"
