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
        totitle: str = "",
        toid: int = 0,
        torev: int = 0,
        fromslots: str = "",
        toslots: str = "",
        prop: str = "",
        difftype: str = "",
        fromtext: str = "",
        totext: str = "",
        fromcontentformat: str = "",
        tocontentformat: str = "",
        fromcontentmodel: str = "",
        tocontentmodel: str = "",
        tosection: str = "",
        # Slot-specific parameters
        fromtext_main: str = "",
        totext_main: str = "",
        fromcontentformat_main: str = "",
        tocontentformat_main: str = "",
        fromcontentmodel_main: str = "",
        tocontentmodel_main: str = "",
        fromsection_main: str = "",
        tosection_main: str = "",
        frompst_main: bool = False,
        topst_main: bool = False,
    ) -> str:
        """Compare two revisions of wiki pages or arbitrary content.

        Args:
            fromtitle: First title to compare
            fromid: First page ID to compare
            fromrev: First revision to compare
            totitle: Second title to compare
            toid: Second page ID to compare
            torev: Second revision to compare
            fromslots: Specify slots to be modified (pipe-separated)
            toslots: Specify slots to be modified (pipe-separated)
            prop: Which pieces of information to return (use '*' for all)
            difftype: Format of diff output ('inline', 'table', 'unified')
            fromtext: Legacy - Text content for 'from' side (deprecated)
            totext: Legacy - Text content for 'to' side (deprecated)
            fromcontentformat: Legacy - Content format for 'from' side (deprecated)
            tocontentformat: Legacy - Content format for 'to' side (deprecated)
            fromcontentmodel: Legacy - Content model for 'from' side (deprecated)
            tocontentmodel: Legacy - Content model for 'to' side (deprecated)
            tosection: Legacy - Section identifier for 'to' side (deprecated)
            fromtext_main: Text content for the main slot on 'from' side
            totext_main: Text content for the main slot on 'to' side
            fromcontentformat_main: Content format for main slot on 'from' side
            tocontentformat_main: Content format for main slot on 'to' side
            fromcontentmodel_main: Content model for main slot on 'from' side
            tocontentmodel_main: Content model for main slot on 'to' side
            fromsection_main: Section for main slot on 'from' side
            tosection_main: Section for main slot on 'to' side
            frompst_main: Pre-save transform for main slot on 'from' side
            topst_main: Pre-save transform for main slot on 'to' side
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_compare_page

                # Convert FastMCP parameters to handler arguments
                arguments = {}

                # Basic page identification parameters
                if fromtitle:
                    arguments["fromtitle"] = fromtitle
                if fromid:
                    arguments["fromid"] = str(fromid)
                if fromrev:
                    arguments["fromrev"] = str(fromrev)
                if totitle:
                    arguments["totitle"] = totitle
                if toid:
                    arguments["toid"] = str(toid)
                if torev:
                    arguments["torev"] = str(torev)

                # Slot and output parameters
                if fromslots:
                    arguments["fromslots"] = fromslots
                if toslots:
                    arguments["toslots"] = toslots
                if prop:
                    arguments["prop"] = prop
                if difftype:
                    arguments["difftype"] = difftype

                # Legacy parameters
                if fromtext:
                    arguments["fromtext"] = fromtext
                if totext:
                    arguments["totext"] = totext
                if fromcontentformat:
                    arguments["fromcontentformat"] = fromcontentformat
                if tocontentformat:
                    arguments["tocontentformat"] = tocontentformat
                if fromcontentmodel:
                    arguments["fromcontentmodel"] = fromcontentmodel
                if tocontentmodel:
                    arguments["tocontentmodel"] = tocontentmodel
                if tosection:
                    arguments["tosection"] = tosection

                # Slot-specific parameters (main slot)
                if fromtext_main:
                    arguments["fromtext-main"] = fromtext_main
                if totext_main:
                    arguments["totext-main"] = totext_main
                if fromcontentformat_main:
                    arguments["fromcontentformat-main"] = fromcontentformat_main
                if tocontentformat_main:
                    arguments["tocontentformat-main"] = tocontentformat_main
                if fromcontentmodel_main:
                    arguments["fromcontentmodel-main"] = fromcontentmodel_main
                if tocontentmodel_main:
                    arguments["tocontentmodel-main"] = tocontentmodel_main
                if fromsection_main:
                    arguments["fromsection-main"] = fromsection_main
                if tosection_main:
                    arguments["tosection-main"] = tosection_main
                if frompst_main:
                    arguments["frompst-main"] = str(frompst_main).lower()
                if topst_main:
                    arguments["topst-main"] = str(topst_main).lower()

                result = await handle_compare_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page compare failed: {e}")
            return f"Error: {str(e)}"
