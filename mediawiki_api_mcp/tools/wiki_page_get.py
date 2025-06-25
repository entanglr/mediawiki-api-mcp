"""MediaWiki page retrieval tools definition."""


import mcp.types as types


def get_page_tools() -> list[types.Tool]:
    """Get page retrieval-related MediaWiki tools."""
    return [
        types.Tool(
            name="wiki_page_get",
            description="Get information and content of a MediaWiki page using various retrieval methods",
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
                    },
                    "method": {
                        "type": "string",
                        "enum": ["revisions", "parse", "raw", "extracts"],
                        "default": "revisions",
                        "description": "Retrieval method: 'revisions' for wikitext via Revisions API, 'parse' for HTML/wikitext via Parse API, 'raw' for fastest wikitext retrieval, 'extracts' for plain text extracts"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["wikitext", "html", "text"],
                        "default": "wikitext",
                        "description": "Content format: 'wikitext' for raw markup, 'html' for parsed HTML (parse method only), 'text' for plain text (extracts method only)"
                    },
                    "sentences": {
                        "type": "integer",
                        "description": "Number of sentences to extract (extracts method only)"
                    },
                    "chars": {
                        "type": "integer",
                        "description": "Character limit for extract (extracts method only)"
                    }
                },
                "required": []
            }
        )
    ]
