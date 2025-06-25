"""MediaWiki page retrieval handlers for MCP server."""

import logging
from typing import Any, Dict, Optional, Sequence
import mcp.types as types
from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_get_page(
    client: MediaWikiClient,
    arguments: Dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_get tool calls with support for multiple retrieval methods."""
    title = arguments.get("title")
    pageid = arguments.get("pageid")
    method = arguments.get("method", "revisions")
    content_format = arguments.get("format", "wikitext")
    sentences = arguments.get("sentences")
    chars = arguments.get("chars")

    if not title and not pageid:
        return [types.TextContent(
            type="text",
            text="Error: Either 'title' or 'pageid' must be provided"
        )]

    try:
        if method == "raw":
            return await _handle_raw_method(client, title, pageid)
        elif method == "parse":
            return await _handle_parse_method(client, title, pageid, content_format)
        elif method == "extracts":
            return await _handle_extracts_method(client, title, pageid, content_format, sentences, chars)
        else:  # Default to "revisions"
            return await _handle_revisions_method(client, title, pageid)

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error retrieving page: {str(e)}"
        )]


async def _handle_raw_method(
    client: MediaWikiClient,
    title: Optional[str],
    pageid: Optional[int]
) -> Sequence[types.TextContent]:
    """Handle raw action method for fastest wikitext retrieval."""
    try:
        content = await client.get_page_raw(title=title, pageid=pageid)
        page_identifier = title or f"ID: {pageid}"

        return [types.TextContent(
            type="text",
            text=f"Page: {page_identifier} (Raw Wikitext)\n\n{content}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error with raw method: {str(e)}"
        )]


async def _handle_revisions_method(
    client: MediaWikiClient,
    title: Optional[str],
    pageid: Optional[int]
) -> Sequence[types.TextContent]:
    """Handle revisions API method with proper formatversion=2 response parsing."""
    try:
        result = await client.get_page_info(title=title, pageid=pageid)

        if "query" not in result or "pages" not in result["query"]:
            return [types.TextContent(
                type="text",
                text="Error: Unexpected response format from MediaWiki API"
            )]

        pages = result["query"]["pages"]
        if not pages:
            return [types.TextContent(
                type="text",
                text="No pages found"
            )]

        page_data = pages[0]  # formatversion=2 returns pages as array

        if "missing" in page_data:
            page_identifier = title or f"ID: {pageid}"
            return [types.TextContent(
                type="text",
                text=f"Page not found: {page_identifier}"
            )]

        page_title = page_data.get("title", "Unknown")
        page_id = page_data.get("pageid", "Unknown")

        # Extract content from formatversion=2 structure
        content = "No content available"
        if "revisions" in page_data and page_data["revisions"]:
            revision = page_data["revisions"][0]
            if "slots" in revision and "main" in revision["slots"]:
                main_slot = revision["slots"]["main"]
                if "content" in main_slot:
                    content = main_slot["content"]

        return [types.TextContent(
            type="text",
            text=f"Page: {page_title} (ID: {page_id})\nMethod: Revisions API\nFormat: Wikitext\n\nContent:\n{content}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error with revisions method: {str(e)}"
        )]


async def _handle_parse_method(
    client: MediaWikiClient,
    title: Optional[str],
    pageid: Optional[int],
    content_format: str
) -> Sequence[types.TextContent]:
    """Handle parse API method for HTML or wikitext content."""
    try:
        result = await client.get_page_parse(title=title, pageid=pageid, format_type=content_format)

        if "parse" not in result:
            return [types.TextContent(
                type="text",
                text="Error: Unexpected response format from Parse API"
            )]

        parse_data = result["parse"]
        page_title = parse_data.get("title", "Unknown")
        page_id = parse_data.get("pageid", "Unknown")

        if content_format == "html" and "text" in parse_data:
            content = parse_data["text"]
            format_label = "HTML"
        elif "wikitext" in parse_data:
            content = parse_data["wikitext"]
            format_label = "Wikitext"
        else:
            content = "No content available"
            format_label = content_format.capitalize()

        return [types.TextContent(
            type="text",
            text=f"Page: {page_title} (ID: {page_id})\nMethod: Parse API\nFormat: {format_label}\n\nContent:\n{content}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error with parse method: {str(e)}"
        )]


async def _handle_extracts_method(
    client: MediaWikiClient,
    title: Optional[str],
    pageid: Optional[int],
    content_format: str,
    sentences: Optional[int],
    chars: Optional[int]
) -> Sequence[types.TextContent]:
    """Handle TextExtracts API method for plain text extracts."""
    try:
        plain_text = content_format == "text"
        result = await client.get_page_extracts(
            title=title,
            pageid=pageid,
            sentences=sentences,
            chars=chars,
            plain_text=plain_text
        )

        if "query" not in result or "pages" not in result["query"]:
            return [types.TextContent(
                type="text",
                text="Error: Unexpected response format from TextExtracts API"
            )]

        pages = result["query"]["pages"]
        if not pages:
            return [types.TextContent(
                type="text",
                text="No pages found"
            )]

        page_data = pages[0]  # formatversion=2 returns pages as array

        if "missing" in page_data:
            page_identifier = title or f"ID: {pageid}"
            return [types.TextContent(
                type="text",
                text=f"Page not found: {page_identifier}"
            )]

        page_title = page_data.get("title", "Unknown")
        page_id = page_data.get("pageid", "Unknown")
        extract = page_data.get("extract", "No extract available")

        limit_info = ""
        if sentences:
            limit_info = f" (Limited to {sentences} sentences)"
        elif chars:
            limit_info = f" (Limited to {chars} characters)"

        format_label = "Plain Text" if plain_text else "Limited HTML"

        return [types.TextContent(
            type="text",
            text=f"Page: {page_title} (ID: {page_id})\nMethod: TextExtracts API\nFormat: {format_label}{limit_info}\n\nExtract:\n{extract}"
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error with extracts method: {str(e)}"
        )]
