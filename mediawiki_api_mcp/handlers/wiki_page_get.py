"""MediaWiki page retrieval handlers for MCP server."""

import logging
from typing import Any, Dict, Sequence
import mcp.types as types
from ..client import MediaWikiClient

logger = logging.getLogger(__name__)


async def handle_get_page(
    client: MediaWikiClient,
    arguments: Dict[str, Any]
) -> Sequence[types.TextContent]:
    """Handle wiki_get_page tool calls."""
    title = arguments.get("title")
    pageid = arguments.get("pageid")

    if not title and not pageid:
        return [types.TextContent(
            type="text",
            text="Error: Either 'title' or 'pageid' must be provided"
        )]

    try:
        result = await client.get_page_info(title=title, pageid=pageid)

        if "query" in result and "pages" in result["query"]:
            pages = result["query"]["pages"]

            if not pages:
                return [types.TextContent(
                    type="text",
                    text="No pages found"
                )]

            # Get the first (and likely only) page
            page_data = list(pages.values())[0]

            if "missing" in page_data:
                return [types.TextContent(
                    type="text",
                    text=f"Page not found: {title or pageid}"
                )]

            page_title = page_data.get("title", "Unknown")
            page_id = page_data.get("pageid", "Unknown")

            # Get page content if available
            content = "No content available"
            if "revisions" in page_data and page_data["revisions"]:
                revision = page_data["revisions"][0]
                if "*" in revision:
                    content = revision["*"]

            return [types.TextContent(
                type="text",
                text=f"Page: {page_title} (ID: {page_id})\n\nContent:\n{content}"
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Unexpected response format: {result}"
            )]

    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error retrieving page: {str(e)}"
        )]
