"""Test suite for MediaWiki search handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_search import handle_search


class TestSearchHandlers:
    """Test cases for search-related handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_search_success(self, mock_client):
        """Test successful search operation."""
        # Setup mock response
        mock_client.search_pages.return_value = {
            "query": {
                "searchinfo": {
                    "totalhits": 2
                },
                "search": [
                    {
                        "title": "Test Page 1",
                        "pageid": 123,
                        "ns": 0,
                        "size": 1024,
                        "wordcount": 200,
                        "timestamp": "2024-01-01T12:00:00Z",
                        "snippet": "This is a test <span class=\"searchmatch\">snippet</span>"
                    },
                    {
                        "title": "Test Page 2",
                        "pageid": 124,
                        "ns": 0,
                        "size": 2048,
                        "wordcount": 400,
                        "timestamp": "2024-01-02T12:00:00Z",
                        "snippet": "Another test <span class=\"searchmatch\">snippet</span>"
                    }
                ]
            }
        }

        arguments = {"query": "test search"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "Search Results for: 'test search'" in response_text
        assert "Total hits: 2" in response_text
        assert "Test Page 1" in response_text
        assert "Test Page 2" in response_text
        assert "**snippet**" in response_text  # HTML tags should be converted

    @pytest.mark.asyncio
    async def test_handle_search_no_results(self, mock_client):
        """Test search with no results."""
        mock_client.search_pages.return_value = {
            "query": {
                "searchinfo": {
                    "totalhits": 0
                },
                "search": []
            }
        }

        arguments = {"query": "nonexistent"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "Search Results for: 'nonexistent'" in response_text
        assert "No search results found." in response_text

    @pytest.mark.asyncio
    async def test_handle_search_missing_query(self, mock_client):
        """Test search with missing query parameter."""
        arguments = {}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Search query is required" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_search_with_pagination(self, mock_client):
        """Test search with pagination parameters."""
        mock_client.search_pages.return_value = {
            "query": {
                "search": [
                    {
                        "title": "Test Page",
                        "pageid": 123,
                        "ns": 0
                    }
                ]
            },
            "continue": {
                "sroffset": 10
            }
        }

        arguments = {
            "query": "test",
            "limit": 5,
            "offset": 5
        }

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "starting from result #6" in response_text
        assert "More results available. Use offset=10" in response_text

        # Verify client was called with correct parameters
        mock_client.search_pages.assert_called_once_with(
            search_query="test",
            namespaces=None,
            limit=5,
            offset=5,
            what="text",
            info=None,
            prop=None,
            interwiki=False,
            enable_rewrites=True,
            srsort="relevance",
            qiprofile="engine_autoselect"
        )

    @pytest.mark.asyncio
    async def test_handle_search_with_metadata(self, mock_client):
        """Test search with various metadata fields."""
        mock_client.search_pages.return_value = {
            "query": {
                "searchinfo": {
                    "totalhits": 1,
                    "suggestion": "alternative query",
                    "rewrittenquery": "modified query"
                },
                "search": [
                    {
                        "title": "Main Page",
                        "pageid": 1,
                        "ns": 0,
                        "redirecttitle": "HomePage",
                        "redirectsnippet": "<span class=\"searchmatch\">match</span>",
                        "sectiontitle": "Introduction",
                        "sectionsnippet": "Section <span class=\"searchmatch\">content</span>",
                        "categorysnippet": "<span class=\"searchmatch\">info</span>",
                        "isfilematch": True
                    }
                ]
            }
        }

        arguments = {"query": "homepage"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "Did you mean: alternative query" in response_text
        assert "Query rewritten to: modified query" in response_text
        assert "Redirected from: HomePage" in response_text
        assert "Redirect match: **match**" in response_text
        assert "Section: Introduction" in response_text
        assert "Section match: **content**" in response_text
        assert "Category: **info**" in response_text
        assert "File content match: Yes" in response_text

    @pytest.mark.asyncio
    async def test_handle_search_unexpected_format(self, mock_client):
        """Test search with unexpected response format."""
        mock_client.search_pages.return_value = {
            "error": "Invalid request"
        }

        arguments = {"query": "test"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        assert "Unexpected response format:" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_search_exception(self, mock_client):
        """Test search with client exception."""
        mock_client.search_pages.side_effect = Exception("Network error")

        arguments = {"query": "test"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        assert "Error performing search: Network error" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_search_custom_parameters(self, mock_client):
        """Test search with custom parameters."""
        mock_client.search_pages.return_value = {
            "query": {
                "search": []
            }
        }

        arguments = {
            "query": "test",
            "namespaces": [0, 1],
            "what": "title",
            "srsort": "last_edit_desc",
            "qiprofile": "popular_inclinks"
        }

        await handle_search(mock_client, arguments)

        # Verify client was called with custom parameters
        mock_client.search_pages.assert_called_once_with(
            search_query="test",
            namespaces=[0, 1],
            limit=10,
            offset=0,
            what="title",
            info=None,
            prop=None,
            interwiki=False,
            enable_rewrites=True,
            srsort="last_edit_desc",
            qiprofile="popular_inclinks"
        )
