"""Test suite initialization module for MediaWiki MCP server."""

from .test_edit import TestEditHandlers
from .test_search import TestSearchHandlers
from .test_tools import TestToolDefinitions

__all__ = ["TestEditHandlers", "TestSearchHandlers", "TestToolDefinitions"]
