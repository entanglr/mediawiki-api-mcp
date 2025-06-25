"""MediaWiki MCP tools package."""

from .edit import get_edit_tools
from .search import get_search_tools

__all__ = ["get_edit_tools", "get_search_tools"]
