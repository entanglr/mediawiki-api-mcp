"""Test suite initialization module for MediaWiki MCP server."""

from .test_wiki_page_edit import TestEditHandlers
from .test_wiki_page_get import TestGetHandlers
from .test_wiki_search import TestSearchHandlers
from .test_tools import TestToolDefinitions

__all__ = ["TestEditHandlers", "TestGetHandlers", "TestSearchHandlers", "TestToolDefinitions"]
