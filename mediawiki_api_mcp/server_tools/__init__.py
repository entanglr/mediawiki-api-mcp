"""Server tools package for MediaWiki API MCP integration."""

from .wiki_meta_siteinfo import register_wiki_meta_siteinfo_tool
from .wiki_opensearch import register_wiki_opensearch_tool
from .wiki_page_delete import register_wiki_page_delete_tool
from .wiki_page_edit import register_wiki_page_edit_tool
from .wiki_page_get import register_wiki_page_get_tool
from .wiki_page_move import register_wiki_page_move_tool
from .wiki_page_undelete import register_wiki_page_undelete_tool
from .wiki_search import register_wiki_search_tool

__all__ = [
    "register_wiki_page_edit_tool",
    "register_wiki_page_get_tool",
    "register_wiki_search_tool",
    "register_wiki_opensearch_tool",
    "register_wiki_page_move_tool",
    "register_wiki_page_delete_tool",
    "register_wiki_page_undelete_tool",
    "register_wiki_meta_siteinfo_tool",
]
