"""MediaWiki page retrieval tools definition."""

from typing import List
import mcp.types as types


def get_page_tools() -> List[types.Tool]:
    """Get page retrieval-related MediaWiki tools."""
    return [
        types.Tool(
            name="wiki_page_get",
            description="Get information and content of a MediaWiki page",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the page to retrieve"
                    },
                    "pageid": {
                        "type": "integer",
                        "description": "Page ID of the page to retrieve (alternative to title)"
                    }
                },
                "required": []
            }
        )
    ]
