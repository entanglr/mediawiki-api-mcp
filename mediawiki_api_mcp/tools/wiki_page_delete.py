"""MediaWiki delete tools definition."""


import mcp.types as types


def get_delete_tools() -> list[types.Tool]:
    """Get delete-related MediaWiki tools."""
    return [
        types.Tool(
            name="wiki_page_delete",
            description="Delete a MediaWiki page",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the page to delete. Cannot be used together with pageid."
                    },
                    "pageid": {
                        "type": "integer",
                        "description": "Page ID of the page to delete. Cannot be used together with title."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the deletion. If not set, an automatically generated reason will be used."
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Change tags to apply to the entry in the deletion log"
                    },
                    "deletetalk": {
                        "type": "boolean",
                        "description": "Delete the talk page, if it exists",
                        "default": False
                    },
                    "watch": {
                        "type": "boolean",
                        "description": "Add the page to the current user's watchlist (deprecated, use watchlist instead)"
                    },
                    "watchlist": {
                        "type": "string",
                        "enum": ["nochange", "preferences", "unwatch", "watch"],
                        "description": "Unconditionally add or remove the page from the current user's watchlist, use preferences (ignored for bot users) or do not change watch",
                        "default": "preferences"
                    },
                    "watchlistexpiry": {
                        "type": "string",
                        "description": "Watchlist expiry timestamp. Omit this parameter entirely to leave the current expiry unchanged."
                    },
                    "unwatch": {
                        "type": "boolean",
                        "description": "Remove the page from the current user's watchlist (deprecated, use watchlist instead)"
                    },
                    "oldimage": {
                        "type": "string",
                        "description": "The name of the old image to delete as provided by action=query&prop=imageinfo&iiprop=archivename"
                    }
                },
                "required": []
            }
        )
    ]
