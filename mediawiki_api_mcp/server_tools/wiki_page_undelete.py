"""Wiki page undelete tool for MediaWiki API MCP integration."""

import logging
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..client import MediaWikiClient
from ..config import MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_undelete_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_undelete tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_undelete(
        title: str,
        reason: str = "",
        tags: str = "",
        timestamps: str = "",
        fileids: str = "",
        undeletetalk: bool = False,
        watchlist: str = "preferences",
        watchlistexpiry: str = "",
    ) -> str:
        """Undelete (restore) the revisions of a deleted page.

        Args:
            title: Title of the page to undelete (required).
            reason: Reason for restoring.
            tags: Change tags to apply to the entry in the deletion log (separate with |).
            timestamps: Timestamps of the revisions to undelete (separate with |). If both timestamps and fileids are empty, all will be undeleted.
            fileids: IDs of the file revisions to restore (separate with |). If both timestamps and fileids are empty, all will be restored.
            undeletetalk: Undelete all revisions of the associated talk page, if any.
            watchlist: Unconditionally add or remove the page from the current user's watchlist, use preferences (ignored for bot users) or do not change watch.
            watchlistexpiry: Watchlist expiry timestamp. Omit this parameter entirely to leave the current expiry unchanged.
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_undelete_page

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "title": title,
                    "reason": reason if reason else None,
                    "tags": tags.split("|") if tags else None,
                    "timestamps": timestamps.split("|") if timestamps else None,
                    "fileids": [int(x) for x in fileids.split("|")] if fileids else None,
                    "undeletetalk": undeletetalk,
                    "watchlist": watchlist if watchlist != "preferences" else None,
                    "watchlistexpiry": watchlistexpiry if watchlistexpiry else None,
                }

                result = await handle_undelete_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page undelete failed: {e}")
            return f"Error: {str(e)}"
