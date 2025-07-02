"""Wiki page compare tool for MediaWiki API MCP integration."""

import logging
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..client import MediaWikiClient
from ..config import MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_compare_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_compare tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_compare(
        fromtitle: str = "",
        fromid: int = 0,
        fromrev: int = 0,
        fromslots: str = "",
        frompst: bool = False,
        totitle: str = "",
        toid: int = 0,
        torev: int = 0,
        torelative: str = "",
        toslots: str = "",
        topst: bool = False,
        prop: str = "",
        slots: str = "",
        difftype: str = "table",
        # Templated slot parameters for from side
        fromtext_main: str = "",
        fromsection_main: str = "",
        fromcontentmodel_main: str = "",
        fromcontentformat_main: str = "",
        # Templated slot parameters for to side
        totext_main: str = "",
        tosection_main: str = "",
        tocontentmodel_main: str = "",
        tocontentformat_main: str = "",
    ) -> str:
        """Get the difference between two pages.

        A revision number, a page title, a page ID, text, or a relative reference for both "from" and "to" must be passed.

        Args:
            fromtitle: First title to compare
            fromid: First page ID to compare
            fromrev: First revision to compare
            fromslots: Override content of the revision specified by fromtitle, fromid or fromrev (use pipe-separated values)
            frompst: Do a pre-save transform on fromtext-{slot}
            totitle: Second title to compare
            toid: Second page ID to compare
            torev: Second revision to compare
            torelative: Use a revision relative to the revision determined from fromtitle, fromid or fromrev ("cur", "next", "prev")
            toslots: Override content of the revision specified by totitle, toid or torev (use pipe-separated values)
            topst: Do a pre-save transform on totext
            prop: Which pieces of information to get (pipe-separated: comment, diff, diffsize, ids, parsedcomment, rel, size, timestamp, title, user)
            slots: Return individual diffs for these slots rather than one combined diff (pipe-separated, use "*" for all slots)
            difftype: Return the comparison formatted as "inline", "table", or "unified"
            fromtext_main: Text of the main slot for from side (when fromslots contains "main")
            fromsection_main: Section identifier for from main slot content
            fromcontentmodel_main: Content model of fromtext_main
            fromcontentformat_main: Content serialization format of fromtext_main
            totext_main: Text of the main slot for to side (when toslots contains "main")
            tosection_main: Section identifier for to main slot content
            tocontentmodel_main: Content model of totext_main
            tocontentformat_main: Content serialization format of totext_main
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_compare_pages

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "fromtitle": fromtitle if fromtitle else None,
                    "fromid": fromid if fromid else None,
                    "fromrev": fromrev if fromrev else None,
                    "fromslots": fromslots if fromslots else None,
                    "frompst": frompst,
                    "totitle": totitle if totitle else None,
                    "toid": toid if toid else None,
                    "torev": torev if torev else None,
                    "torelative": torelative if torelative else None,
                    "toslots": toslots if toslots else None,
                    "topst": topst,
                    "prop": prop if prop else None,
                    "slots": slots if slots else None,
                    "difftype": difftype,
                }

                # Add templated slot parameters
                if fromtext_main:
                    arguments["fromtext-main"] = fromtext_main
                if fromsection_main:
                    arguments["fromsection-main"] = fromsection_main
                if fromcontentmodel_main:
                    arguments["fromcontentmodel-main"] = fromcontentmodel_main
                if fromcontentformat_main:
                    arguments["fromcontentformat-main"] = fromcontentformat_main
                if totext_main:
                    arguments["totext-main"] = totext_main
                if tosection_main:
                    arguments["tosection-main"] = tosection_main
                if tocontentmodel_main:
                    arguments["tocontentmodel-main"] = tocontentmodel_main
                if tocontentformat_main:
                    arguments["tocontentformat-main"] = tocontentformat_main

                result = await handle_compare_pages(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page compare failed: {e}")
            return f"Error: {str(e)}"
