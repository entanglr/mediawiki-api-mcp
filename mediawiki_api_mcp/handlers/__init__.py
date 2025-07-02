"""MediaWiki MCP handlers package."""

from .wiki_meta_siteinfo import handle_meta_siteinfo
from .wiki_opensearch import handle_opensearch
from .wiki_page_compare import handle_compare_pages
from .wiki_page_delete import handle_delete_page
from .wiki_page_edit import handle_edit_page
from .wiki_page_get import handle_get_page
from .wiki_page_move import handle_move_page
from .wiki_page_parse import handle_parse_page
from .wiki_page_undelete import handle_undelete_page
from .wiki_search import handle_search

__all__ = ["handle_edit_page", "handle_get_page", "handle_parse_page", "handle_search", "handle_opensearch", "handle_move_page", "handle_delete_page", "handle_undelete_page", "handle_meta_siteinfo", "handle_compare_pages"]
