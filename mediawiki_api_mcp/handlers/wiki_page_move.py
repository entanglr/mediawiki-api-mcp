"""MediaWiki move handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_move_page(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_page_move tool calls."""
    from_title = arguments.get("from")
    fromid = arguments.get("fromid")
    to = arguments.get("to")

    if not from_title and not fromid:
        return [types.TextContent(
            type="text",
            text="Error: Either 'from' or 'fromid' must be provided"
        )]

    if not to:
        return [types.TextContent(
            type="text",
            text="Error: 'to' parameter is required"
        )]

    # Extract move parameters
    move_params = {
        "from_title": from_title,
        "fromid": fromid,
        "to": to,
        "reason": arguments.get("reason"),
        "movetalk": arguments.get("movetalk", False),
        "movesubpages": arguments.get("movesubpages", False),
        "noredirect": arguments.get("noredirect", False),
        "watchlist": arguments.get("watchlist", "preferences"),
        "watchlistexpiry": arguments.get("watchlistexpiry"),
        "ignorewarnings": arguments.get("ignorewarnings", False),
        "tags": arguments.get("tags")
    }

    # Remove None values
    move_params = {k: v for k, v in move_params.items() if v is not None}

    try:
        result = await client.move_page(**move_params)

        # Check if the move was successful
        if "from" in result and "to" in result:
            from_page = result.get("from", from_title or f"Page ID {fromid}")
            to_page = result.get("to", to)
            reason = result.get("reason", "No reason provided")

            response_text = f"Successfully moved page '{from_page}' to '{to_page}'"
            if reason:
                response_text += f". Reason: {reason}"

            # Include talk page move info if applicable
            if "talkfrom" in result and "talkto" in result:
                response_text += f". Talk page moved from '{result['talkfrom']}' to '{result['talkto']}'"

            # Include subpage move info if applicable
            if "subpages" in result:
                subpage_count = len(result["subpages"])
                response_text += f". {subpage_count} subpages moved"

            return [types.TextContent(
                type="text",
                text=response_text
            )]
        else:
            # Handle error responses
            if "error" in result:
                error_info = result["error"]
                error_code = error_info.get("code", "unknown")
                error_message = error_info.get("info", "Unknown error")
                return [types.TextContent(
                    type="text",
                    text=f"Move failed ({error_code}): {error_message}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Move failed: {result}"
                )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error moving page: {str(e)}"
        )]
