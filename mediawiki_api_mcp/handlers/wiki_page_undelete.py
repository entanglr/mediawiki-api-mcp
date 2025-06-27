"""MediaWiki undelete handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_undelete_page(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_undelete tool calls."""
    title = arguments.get("title")

    if not title:
        return [types.TextContent(
            type="text",
            text="Error: 'title' parameter is required"
        )]

    # Extract undelete parameters
    undelete_params = {
        "title": title,
    }

    # Add optional parameters only if they're provided and not defaults
    if arguments.get("reason"):
        undelete_params["reason"] = arguments["reason"]
    if arguments.get("tags"):
        undelete_params["tags"] = arguments["tags"]
    if arguments.get("timestamps"):
        undelete_params["timestamps"] = arguments["timestamps"]
    if arguments.get("fileids"):
        undelete_params["fileids"] = arguments["fileids"]
    if arguments.get("undeletetalk", False):
        undelete_params["undeletetalk"] = arguments["undeletetalk"]
    if arguments.get("watchlist") and arguments["watchlist"] != "preferences":
        undelete_params["watchlist"] = arguments["watchlist"]
    if arguments.get("watchlistexpiry"):
        undelete_params["watchlistexpiry"] = arguments["watchlistexpiry"]

    try:
        result = await client.undelete_page(**undelete_params)

        if "title" in result:
            page_title = result.get("title", title)
            reason_used = result.get("reason", "No reason provided")
            revisions = result.get("revisions", 0)
            fileversions = result.get("fileversions", 0)

            response_text = f"Successfully undeleted page '{page_title}'. "
            response_text += f"Reason: {reason_used}. "
            response_text += f"Revisions restored: {revisions}. "
            response_text += f"File versions restored: {fileversions}."

            return [types.TextContent(
                type="text",
                text=response_text
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Undelete failed: {result}"
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error undeleting page: {str(e)}"
        )]
