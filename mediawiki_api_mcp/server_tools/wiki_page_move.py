"""Wiki page move tool for MediaWiki API MCP integration."""

import logging
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_move_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_move tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_move(
        from_title: str = "",
        fromid: int = 0,
        to: str = "",
        reason: str = "",
        movetalk: bool = False,
        movesubpages: bool = False,
        noredirect: bool = False,
        watchlist: str = "preferences",
        watchlistexpiry: str = "",
        ignorewarnings: bool = False,
        tags: str = "",
    ) -> str:
        """Move a page.

        Args:
            from_title: Title of the page to rename. Cannot be used together with fromid.
            fromid: Page ID of the page to rename. Cannot be used together with from.
            to: Title to rename the page to.
            reason: Reason for the rename.
            movetalk: Rename the talk page, if it exists.
            movesubpages: Rename subpages, if applicable.
            noredirect: Don't create a redirect.
            watchlist: Unconditionally add or remove the page from the current user's watchlist, use preferences (ignored for bot users) or do not change watch.
            watchlistexpiry: Watchlist expiry timestamp. Omit this parameter entirely to leave the current expiry unchanged.
            ignorewarnings: Ignore any warnings.
            tags: Change tags to apply to the entry in the move log and to the null revision on the destination page.
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_move_page

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "from": from_title if from_title else None,
                    "fromid": fromid if fromid else None,
                    "to": to if to else None,
                    "reason": reason if reason else None,
                    "movetalk": movetalk,
                    "movesubpages": movesubpages,
                    "noredirect": noredirect,
                    "watchlist": watchlist if watchlist != "preferences" else None,
                    "watchlistexpiry": watchlistexpiry if watchlistexpiry else None,
                    "ignorewarnings": ignorewarnings,
                    "tags": tags.split("|") if tags else None,
                }

                result = await handle_move_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page move failed: {e}")
            return f"Error: {str(e)}"
