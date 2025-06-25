"""MediaWiki edit tools definition."""


import mcp.types as types


def get_edit_tools() -> list[types.Tool]:
    """Get edit-related MediaWiki tools."""
    return [
        types.Tool(
            name="wiki_page_edit",
            description="Edit or create a MediaWiki page",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Title of the page to edit"
                    },
                    "pageid": {
                        "type": "integer",
                        "description": "Page ID of the page to edit (alternative to title)"
                    },
                    "text": {
                        "type": "string",
                        "description": "Complete page content (replaces existing content)"
                    },
                    "summary": {
                        "type": "string",
                        "description": "Edit summary describing the changes"
                    },
                    "section": {
                        "type": "string",
                        "description": "Section to edit (0 for top section, 'new' for new section)"
                    },
                    "sectiontitle": {
                        "type": "string",
                        "description": "Title for new section when using section='new'"
                    },
                    "appendtext": {
                        "type": "string",
                        "description": "Text to append to the page or section"
                    },
                    "prependtext": {
                        "type": "string",
                        "description": "Text to prepend to the page or section"
                    },
                    "minor": {
                        "type": "boolean",
                        "description": "Mark this edit as a minor edit",
                        "default": False
                    },
                    "bot": {
                        "type": "boolean",
                        "description": "Mark this edit as a bot edit",
                        "default": True
                    },
                    "createonly": {
                        "type": "boolean",
                        "description": "Don't edit the page if it exists already",
                        "default": False
                    },
                    "nocreate": {
                        "type": "boolean",
                        "description": "Don't create the page if it doesn't exist",
                        "default": False
                    }
                },
                "required": []
            }
        )
    ]
