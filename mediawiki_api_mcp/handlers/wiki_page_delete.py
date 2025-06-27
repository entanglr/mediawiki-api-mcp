"""MediaWiki delete handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_delete_page(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_delete tool calls."""
    title = arguments.get("title")
    pageid = arguments.get("pageid")

    if not title and not pageid:
        return [types.TextContent(
            type="text",
            text="Error: Either 'title' or 'pageid' must be provided"
        )]

    # Extract delete parameters
    delete_params = {
        "title": title,
        "pageid": pageid,
        "reason": arguments.get("reason"),
        "tags": arguments.get("tags"),
        "deletetalk": arguments.get("deletetalk", False),
        "watch": arguments.get("watch"),
        "watchlist": arguments.get("watchlist", "preferences"),
        "watchlistexpiry": arguments.get("watchlistexpiry"),
        "unwatch": arguments.get("unwatch"),
        "oldimage": arguments.get("oldimage")
    }

    # Remove None values
    delete_params = {k: v for k, v in delete_params.items() if v is not None}

    try:
        result = await client.delete_page(**delete_params)

        if "title" in result:
            page_title = result.get("title", title or f"Page ID {pageid}")
            reason_used = result.get("reason", "No reason provided")
            logid = result.get("logid", "unknown")

            return [types.TextContent(
                type="text",
                text=f"Successfully deleted page '{page_title}'. "
                     f"Reason: {reason_used}. "
                     f"Log ID: {logid}"
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Delete failed: {result}"
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error deleting page: {str(e)}"
        )]
