"""MediaWiki move tools definition."""

import mcp.types as types


def get_move_tools() -> list[types.Tool]:
    """Get move-related MediaWiki tools."""
    return [
        types.Tool(
            name="wiki_page_move",
            description="Move a page",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_title": {
                        "type": "string",
                        "description": "Title of the page to rename. Cannot be used together with fromid."
                    },
                    "fromid": {
                        "type": "integer",
                        "description": "Page ID of the page to rename. Cannot be used together with from."
                    },
                    "to": {
                        "type": "string",
                        "description": "Title to rename the page to."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the rename."
                    },
                    "movetalk": {
                        "type": "boolean",
                        "description": "Rename the talk page, if it exists.",
                        "default": False
                    },
                    "movesubpages": {
                        "type": "boolean",
                        "description": "Rename subpages, if applicable.",
                        "default": False
                    },
                    "noredirect": {
                        "type": "boolean",
                        "description": "Don't create a redirect.",
                        "default": False
                    },
                    "watchlist": {
                        "type": "string",
                        "description": "Unconditionally add or remove the page from the current user's watchlist, use preferences (ignored for bot users) or do not change watch.",
                        "enum": ["nochange", "preferences", "unwatch", "watch"],
                        "default": "preferences"
                    },
                    "watchlistexpiry": {
                        "type": "string",
                        "description": "Watchlist expiry timestamp. Omit this parameter entirely to leave the current expiry unchanged."
                    },
                    "ignorewarnings": {
                        "type": "boolean",
                        "description": "Ignore any warnings.",
                        "default": False
                    },
                    "tags": {
                        "type": "string",
                        "description": "Change tags to apply to the entry in the move log and to the null revision on the destination page."
                    }
                },
                "required": ["to"]
            }
        )
    ]
