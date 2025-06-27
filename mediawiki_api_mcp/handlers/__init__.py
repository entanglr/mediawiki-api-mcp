"""MediaWiki MCP handlers package."""

from .wiki_page_edit import handle_edit_page
from .wiki_page_get import handle_get_page
from .wiki_search import handle_search
from .wiki_opensearch import handle_opensearch

__all__ = ["handle_edit_page", "handle_get_page", "handle_search", "handle_opensearch"]
