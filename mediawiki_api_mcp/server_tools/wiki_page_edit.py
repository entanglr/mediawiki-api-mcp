"""Wiki page edit tool for MediaWiki API MCP integration."""

import logging
from collections.abc import Callable

from mcp.server.fastmcp import FastMCP

from ..client import MediaWikiClient, MediaWikiConfig

logger = logging.getLogger(__name__)


def register_wiki_page_edit_tool(mcp: FastMCP, get_config: Callable[[], MediaWikiConfig]) -> None:
    """Register the wiki_page_edit tool with the MCP server."""

    @mcp.tool()
    async def wiki_page_edit(
        title: str = "",
        pageid: int = 0,
        text: str = "",
        summary: str = "",
        section: str = "",
        sectiontitle: str = "",
        appendtext: str = "",
        prependtext: str = "",
        minor: bool = False,
        bot: bool = True,
        createonly: bool = False,
        nocreate: bool = False,
    ) -> str:
        """Edit or create a MediaWiki page.

        Args:
            title: Title of the page to edit
            pageid: Page ID of the page to edit (alternative to title)
            text: New page content (replaces existing content)
            summary: Edit summary describing the changes
            section: Section identifier (0 for top section, 'new' for new section)
            sectiontitle: Title for new section when using section='new'
            appendtext: Text to append to the page or section
            prependtext: Text to prepend to the page or section
            minor: Mark this edit as a minor edit
            bot: Mark this edit as a bot edit
            createonly: Don't edit the page if it exists already
            nocreate: Don't create the page if it doesn't exist
        """
        try:
            config = get_config()
            async with MediaWikiClient(config) as client:
                # Import here to avoid circular imports
                from ..handlers import handle_edit_page

                # Convert FastMCP parameters to handler arguments
                arguments = {
                    "title": title if title else None,
                    "pageid": pageid if pageid else None,
                    "text": text if text else None,
                    "summary": summary if summary else None,
                    "section": section if section else None,
                    "sectiontitle": sectiontitle if sectiontitle else None,
                    "appendtext": appendtext if appendtext else None,
                    "prependtext": prependtext if prependtext else None,
                    "minor": minor,
                    "bot": bot,
                    "createonly": createonly,
                    "nocreate": nocreate,
                }

                result = await handle_edit_page(client, arguments)
                # Return the formatted text from the handler
                return result[0].text if result else "No results"
        except Exception as e:
            logger.error(f"Wiki page edit failed: {e}")
            return f"Error: {str(e)}"
