"""Wiki page delete tool for MediaWiki API MCP integration."""

import logging
from typing import Callable

from mcp.server.fastmcp import FastMCP
from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_delete_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_delete tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_delete(
        title: str = "",
        pageid: int = 0,
        reason: str = "",
        tags: str = "",
        deletetalk: bool = False,
        watch: bool = False,
        watchlist: str = "preferences",
        watchlistexpiry: str = "",
        unwatch: bool = False,
        oldimage: str = "",
    ) -> str:
        """Delete a page.

        Args:
            title: Title of the page to delete. Cannot be used together with pageid.
            pageid: Page ID of the page to delete. Cannot be used together with title.
            reason: Reason for the deletion. If not set, an automatically generated reason will be used.
            tags: Change tags to apply to the entry in the deletion log (separate with |).
            deletetalk: Delete the talk page, if it exists.
            watch: Add the page to the current user's watchlist (deprecated, use watchlist).
            watchlist: Unconditionally add or remove the page from the current user's watchlist, use preferences (ignored for bot users) or do not change watch.
            watchlistexpiry: Watchlist expiry timestamp. Omit this parameter entirely to leave the current expiry unchanged.
            unwatch: Remove the page from the current user's watchlist (deprecated, use watchlist).
            oldimage: The name of the old image to delete as provided by action=query&prop=imageinfo&iiprop=archivename.
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_delete_page

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "title": title if title else None,
                    "pageid": pageid if pageid else None,
                    "reason": reason if reason else None,
                    "tags": tags.split("|") if tags else None,
                    "deletetalk": deletetalk,
                    "watch": watch if watch else None,
                    "watchlist": watchlist if watchlist != "preferences" else None,
                    "watchlistexpiry": watchlistexpiry if watchlistexpiry else None,
                    "unwatch": unwatch if unwatch else None,
                    "oldimage": oldimage if oldimage else None,
                }

                result = await handle_delete_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page delete failed: {e}")
            return f"Error: {str(e)}"
