"""MediaWiki edit handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_edit_page(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_edit_page tool calls."""
    title = arguments.get("title")
    pageid = arguments.get("pageid")

    if not title and not pageid:
        return [types.TextContent(
            type="text",
            text="Error: Either 'title' or 'pageid' must be provided"
        )]

    # Extract edit parameters
    edit_params = {
        "title": title,
        "pageid": pageid,
        "text": arguments.get("text"),
        "summary": arguments.get("summary"),
        "section": arguments.get("section"),
        "sectiontitle": arguments.get("sectiontitle"),
        "appendtext": arguments.get("appendtext"),
        "prependtext": arguments.get("prependtext"),
        "minor": arguments.get("minor", False),
        "bot": arguments.get("bot", True),
        "createonly": arguments.get("createonly", False),
        "nocreate": arguments.get("nocreate", False)
    }

    # Remove None values
    edit_params = {k: v for k, v in edit_params.items() if v is not None}

    try:
        result = await client.edit_page(**edit_params)

        if result.get("result") == "Success":
            page_title = result.get("title", title or f"Page ID {pageid}")
            revision_id = result.get("newrevid", "unknown")
            timestamp = result.get("newtimestamp", "unknown")

            return [types.TextContent(
                type="text",
                text=f"Successfully edited page '{page_title}'. "
                     f"New revision ID: {revision_id}, "
                     f"Timestamp: {timestamp}"
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Edit failed: {result}"
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error editing page: {str(e)}"
        )]
