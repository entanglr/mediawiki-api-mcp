"""MediaWiki MCP handlers package."""

from .edit import handle_edit_page, handle_get_page
from .search import handle_search

__all__ = ["handle_edit_page", "handle_get_page", "handle_search"]
