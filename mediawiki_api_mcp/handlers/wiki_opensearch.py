"""MediaWiki opensearch handlers for MCP server."""

import logging
from collections.abc import Sequence
from typing import Any

import mcp.types as types

from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_opensearch(
    client: MediaWikiClient,
    arguments: dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_opensearch tool calls with OpenSearch protocol functionality."""
    search = arguments.get("search")

    if not search:
        return [types.TextContent(
            type="text",
            text="Error: Search parameter is required"
        )]

    # Extract opensearch parameters with defaults
    namespace = arguments.get("namespace")
    limit = arguments.get("limit", 10)
    profile = arguments.get("profile", "engine_autoselect")
    redirects = arguments.get("redirects")
    format_type = arguments.get("format", "json")
    warningsaserror = arguments.get("warningsaserror", False)

    try:
        result = await client.opensearch(
            search=search,
            namespace=namespace,
            limit=limit,
            profile=profile,
            redirects=redirects,
            format=format_type,
            warningsaserror=warningsaserror
        )

        # OpenSearch returns a 4-element array: [search_term, titles, descriptions, urls]
        if not isinstance(result, list) or len(result) != 4:
            return [types.TextContent(
                type="text",
                text=f"Unexpected OpenSearch response format: {result}"
            )]

        search_term, titles, descriptions, urls = result

        # Format opensearch results
        response_text = f"OpenSearch Results for: '{search_term}'\n"
        response_text += "=" * (len(response_text) - 1) + "\n\n"

        if not titles or len(titles) == 0:
            response_text += "No results found."
        else:
            response_text += f"Found {len(titles)} result(s):\n\n"

            for i, title in enumerate(titles):
                response_text += f"{i + 1}. **{title}**\n"

                # Add description if available
                if i < len(descriptions) and descriptions[i]:
                    response_text += f"   Description: {descriptions[i]}\n"

                # Add URL if available
                if i < len(urls) and urls[i]:
                    response_text += f"   URL: {urls[i]}\n"

                response_text += "\n"

        return [types.TextContent(
            type="text",
            text=response_text
        )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error performing OpenSearch: {str(e)}"
        )]
