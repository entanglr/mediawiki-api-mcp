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
            # Import here to avoid circular imports
            from .handlers import handle_edit_page

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
            from .handlers import handle_get_page

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
            from .handlers import handle_search

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
            from .handlers import handle_opensearch

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


def run_server() -> None:
    """Synchronous entry point for the MCP server."""
    mcp.run(transport='stdio')


if __name__ == "__main__":
    run_server()
