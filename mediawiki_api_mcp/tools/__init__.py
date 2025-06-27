"""MediaWiki MCP tools package."""

from .wiki_page_delete import get_delete_tools
from .wiki_page_edit import get_edit_tools
from .wiki_page_get import get_page_tools
from .wiki_page_move import get_move_tools
from .wiki_search import get_search_tools

__all__ = ["get_edit_tools", "get_page_tools", "get_search_tools", "get_move_tools", "get_delete_tools"]
