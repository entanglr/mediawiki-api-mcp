"""MediaWiki MCP handlers package."""

from .wiki_opensearch import handle_opensearch
from .wiki_page_delete import handle_delete_page
from .wiki_page_edit import handle_edit_page
from .wiki_page_get import handle_get_page
from .wiki_page_move import handle_move_page
from .wiki_page_undelete import handle_undelete_page
from .wiki_search import handle_search

__all__ = ["handle_edit_page", "handle_get_page", "handle_search", "handle_opensearch", "handle_move_page", "handle_delete_page", "handle_undelete_page"]
