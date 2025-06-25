"""MediaWiki search tools definition."""


import mcp.types as types


def get_search_tools() -> list[types.Tool]:
    """Get search-related MediaWiki tools."""
    return [
        types.Tool(
            name="wiki_search",
            description="Search for wiki pages by title or content using MediaWiki's search API",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query string (required)"
                    },
                    "namespaces": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of namespace IDs to search in (default: [0] for main namespace)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-500, default: 10)",
                        "minimum": 1,
                        "maximum": 500,
                        "default": 10
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Search result offset for pagination (default: 0)",
                        "minimum": 0,
                        "default": 0
                    },
                    "what": {
                        "type": "string",
                        "enum": ["text", "title", "nearmatch"],
                        "description": "Type of search to perform (default: text)",
                        "default": "text"
                    },
                    "info": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["rewrittenquery", "suggestion", "totalhits"]
                        },
                        "description": "Metadata to return (default: all)"
                    },
                    "prop": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "categorysnippet", "extensiondata", "isfilematch",
                                "redirectsnippet", "redirecttitle", "sectionsnippet",
                                "sectiontitle", "size", "snippet", "timestamp",
                                "titlesnippet", "wordcount"
                            ]
                        },
                        "description": "Properties to return for each search result"
                    },
                    "interwiki": {
                        "type": "boolean",
                        "description": "Include interwiki results if available (default: false)",
                        "default": False
                    },
                    "enable_rewrites": {
                        "type": "boolean",
                        "description": "Enable internal query rewriting for better results (default: true)",
                        "default": True
                    },
                    "sort": {
                        "type": "string",
                        "enum": [
                            "create_timestamp_asc", "create_timestamp_desc",
                            "incoming_links_asc", "incoming_links_desc", "just_match",
                            "last_edit_asc", "last_edit_desc", "none", "random",
                            "relevance", "user_random"
                        ],
                        "description": "Sort order of returned results (default: relevance)",
                        "default": "relevance"
                    },
                    "qiprofile": {
                        "type": "string",
                        "enum": [
                            "classic", "classic_noboostlinks", "empty",
                            "engine_autoselect", "popular_inclinks",
                            "popular_inclinks_pv", "wsum_inclinks", "wsum_inclinks_pv"
                        ],
                        "description": "Query independent ranking profile (default: engine_autoselect)",
                        "default": "engine_autoselect"
                    }
                },
                "required": ["query"]
            }
        )
    ]
