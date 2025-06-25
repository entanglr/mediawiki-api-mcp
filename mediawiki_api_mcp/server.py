"""Main MCP server implementation for MediaWiki API integration."""

import logging
import os

from mcp.server.fastmcp import FastMCP

from .client import MediaWikiClient, MediaWikiConfig

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
            # Call edit_page with proper typed arguments
            result = await client.edit_page(
                title=title if title else None,
                pageid=pageid if pageid else None,
                text=text if text else None,
                summary=summary if summary else None,
                section=section if section else None,
                sectiontitle=sectiontitle if sectiontitle else None,
                appendtext=appendtext if appendtext else None,
                prependtext=prependtext if prependtext else None,
                minor=minor,
                bot=bot,
                createonly=createonly,
                nocreate=nocreate
            )
            return f"Page edit successful: {result}"
    except Exception as e:
        logger.error(f"Wiki page edit failed: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wiki_page_get(
    title: str = "",
    pageid: int = 0,
) -> str:
    """Get information and content from a MediaWiki page.

    Args:
        title: Title of the page to retrieve
        pageid: Page ID of the page to retrieve (alternative to title)
    """
    try:
        config = get_config()
        async with MediaWikiClient(config) as client:
            if title:
                info = await client.get_page_info(title=title)
            elif pageid:
                info = await client.get_page_info(pageid=pageid)
            else:
                return "Error: Either title or pageid must be provided"

            return f"Page information retrieved: {info}"
    except Exception as e:
        logger.error(f"Wiki page get failed: {e}")
        return f"Error: {str(e)}"


@mcp.tool()
async def wiki_search(
    search_query: str,
    limit: int = 10,
    offset: int = 0,
    what: str = "text",
) -> str:
    """Search for pages using MediaWiki's search API.

    Args:
        search_query: Search query string (required)
        limit: Maximum number of results (1-500, default: 10)
        offset: Search result offset for pagination (default: 0)
        what: Type of search - "text", "title", or "nearmatch" (default: "text")
    """
    try:
        config = get_config()
        async with MediaWikiClient(config) as client:
            result = await client.search_pages(
                search_query=search_query,
                limit=limit,
                offset=offset,
                what=what
            )
            return f"Search completed: {result}"
    except Exception as e:
        logger.error(f"Wiki search failed: {e}")
        return f"Error: {str(e)}"


def run_server() -> None:
    """Synchronous entry point for the MCP server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    run_server()
