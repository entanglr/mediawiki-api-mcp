"""Tests for MediaWiki MCP server."""

from unittest.mock import AsyncMock, Mock, patch

import mcp.types as types
import pytest

from mediawiki_api_mcp.client import MediaWikiClient, MediaWikiConfig
from mediawiki_api_mcp.handlers import handle_edit_page, handle_get_page, handle_search
from mediawiki_api_mcp.server import mcp, get_config


@pytest.fixture
def mock_config():
    """Mock MediaWiki configuration."""
    return MediaWikiConfig(
        api_url="http://test.wiki/api.php",
        username="testuser",
        password="testpass",
        user_agent="Test-Bot/1.0"
    )


@pytest.fixture
def mock_search_response():
    """Mock search API response."""
    return {
        "batchcomplete": "",
        "continue": {
            "sroffset": 10,
            "continue": "-||"
        },
        "query": {
            "searchinfo": {
                "totalhits": 5060,
                "suggestion": "nelson mandela",
                "rewrittenquery": "nelson mandela"
            },
            "search": [
                {
                    "ns": 0,
                    "title": "Nelson Mandela",
                    "pageid": 21492751,
                    "size": 196026,
                    "wordcount": 23664,
                    "snippet": '<span class="searchmatch">Nelson</span> Rolihlahla <span class="searchmatch">Mandela</span> was a South African anti-apartheid revolutionary',
                    "timestamp": "2023-07-23T07:59:43Z"
                },
                {
                    "ns": 0,
                    "title": "Death of Nelson Mandela",
                    "pageid": 41284488,
                    "size": 133513,
                    "wordcount": 13512,
                    "snippet": 'On December 5, 2013, <span class="searchmatch">Nelson</span> <span class="searchmatch">Mandela</span>, the first President of South Africa',
                    "timestamp": "2023-07-19T17:30:59Z"
                }
            ]
        }
    }


@pytest.fixture
def mock_empty_search_response():
    """Mock empty search API response."""
    return {
        "batchcomplete": "",
        "query": {
            "searchinfo": {
                "totalhits": 0
            },
            "search": []
        }
    }


class TestSearchFunctionality:
    """Test suite for search functionality."""

    @pytest.mark.asyncio
    async def test_handle_search_basic_query(self, mock_config, mock_search_response):
        """Test basic search functionality."""
        mock_client = Mock(spec=MediaWikiClient)
        mock_client.search_pages = AsyncMock(return_value=mock_search_response)

        arguments = {"query": "Nelson Mandela"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        assert isinstance(result[0], types.TextContent)

        response_text = result[0].text
        assert "Search Results for: 'Nelson Mandela'" in response_text
        assert "Total hits: 5060" in response_text
        assert "Nelson Mandela" in response_text
        assert "Death of Nelson Mandela" in response_text
        assert "Page ID: 21492751" in response_text
        assert "**Nelson** Rolihlahla **Mandela**" in response_text

        # Verify client was called with correct parameters
        mock_client.search_pages.assert_called_once_with(
            search_query="Nelson Mandela",
            namespaces=None,
            limit=10,
            offset=0,
            what="text",
            info=None,
            prop=None,
            interwiki=False,
            enable_rewrites=True,
            sort_order="relevance",
            qiprofile="engine_autoselect"
        )

    @pytest.mark.asyncio
    async def test_handle_search_with_parameters(self, mock_config, mock_search_response):
        """Test search with custom parameters."""
        mock_client = Mock(spec=MediaWikiClient)
        mock_client.search_pages = AsyncMock(return_value=mock_search_response)

        arguments = {
            "query": "test query",
            "namespaces": [0, 1, 4],
            "limit": 20,
            "offset": 5,
            "what": "title",
            "info": ["totalhits", "suggestion"],
            "prop": ["size", "wordcount", "snippet"],
            "interwiki": True,
            "enable_rewrites": False,
            "sort": "last_edit_desc",
            "qiprofile": "classic"
        }

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1

        # Verify client was called with custom parameters
        mock_client.search_pages.assert_called_once_with(
            search_query="test query",
            namespaces=[0, 1, 4],
            limit=20,
            offset=5,
            what="title",
            info=["totalhits", "suggestion"],
            prop=["size", "wordcount", "snippet"],
            interwiki=True,
            enable_rewrites=False,
            sort_order="last_edit_desc",
            qiprofile="classic"
        )

    @pytest.mark.asyncio
    async def test_handle_search_empty_results(self, mock_config, mock_empty_search_response):
        """Test search with no results."""
        mock_client = Mock(spec=MediaWikiClient)
        mock_client.search_pages = AsyncMock(return_value=mock_empty_search_response)

        arguments = {"query": "nonexistent term"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "No search results found." in response_text
        assert "Total hits: 0" in response_text

    @pytest.mark.asyncio
    async def test_handle_search_missing_query(self, mock_config):
        """Test search without query parameter."""
        mock_client = Mock(spec=MediaWikiClient)

        arguments = {}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Search query is required" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_search_with_pagination(self, mock_config, mock_search_response):
        """Test search with pagination info."""
        mock_client = Mock(spec=MediaWikiClient)
        mock_client.search_pages = AsyncMock(return_value=mock_search_response)

        arguments = {"query": "test", "offset": 0}

        result = await handle_search(mock_client, arguments)

        response_text = result[0].text
        assert "More results available. Use offset=10 to see the next page." in response_text

    @pytest.mark.asyncio
    async def test_handle_search_with_rich_metadata(self, mock_config):
        """Test search with rich metadata fields."""
        rich_response = {
            "query": {
                "searchinfo": {
                    "totalhits": 100,
                    "suggestion": "corrected query",
                    "rewrittenquery": "rewritten query"
                },
                "search": [
                    {
                        "ns": 0,
                        "title": "Test Page",
                        "pageid": 12345,
                        "size": 5000,
                        "wordcount": 800,
                        "snippet": 'Test <span class="searchmatch">content</span> here',
                        "timestamp": "2023-01-01T12:00:00Z",
                        "titlesnippet": 'Test <span class="searchmatch">Page</span>',
                        "redirecttitle": "Original Title",
                        "redirectsnippet": 'Original <span class="searchmatch">Title</span>',
                        "sectiontitle": "Section Name",
                        "sectionsnippet": 'Section <span class="searchmatch">content</span>',
                        "categorysnippet": 'Category: <span class="searchmatch">Test</span>',
                        "isfilematch": True
                    }
                ]
            }
        }

        mock_client = Mock(spec=MediaWikiClient)
        mock_client.search_pages = AsyncMock(return_value=rich_response)

        arguments = {"query": "test"}

        result = await handle_search(mock_client, arguments)

        response_text = result[0].text
        assert "Total hits: 100" in response_text
        assert "Did you mean: corrected query" in response_text
        assert "Query rewritten to: rewritten query" in response_text
        assert "Title match: Test **Page**" in response_text
        assert "Redirected from: Original Title" in response_text
        assert "Section: Section Name" in response_text
        assert "Category: Category: **Test**" in response_text
        assert "File content match: Yes" in response_text

    @pytest.mark.asyncio
    async def test_handle_search_api_error(self, mock_config):
        """Test search when API call fails."""
        mock_client = Mock(spec=MediaWikiClient)
        mock_client.search_pages = AsyncMock(side_effect=Exception("API Error"))

        arguments = {"query": "test"}

        result = await handle_search(mock_client, arguments)

        assert len(result) == 1
        assert "Error performing search: API Error" in result[0].text

    @pytest.mark.asyncio
    async def test_search_client_method(self, mock_config):
        """Test the MediaWiki client search_pages method."""
        with patch('mediawiki_api_mcp.client.MediaWikiClient._make_request') as mock_request:
            mock_request.return_value = {
                "query": {
                    "search": [{"title": "Test", "pageid": 123}]
                }
            }

            client = MediaWikiClient(mock_config)

            result = await client.search_pages("test query")

            # Verify the request was made with correct parameters
            expected_params = {
                "action": "query",
                "list": "search",
                "srsearch": "test query",
                "format": "json",
                "srnamespace": "0",
                "srlimit": 10,
                "srwhat": "text",
                "srqiprofile": "engine_autoselect",
                "srinfo": "totalhits|suggestion|rewrittenquery",
                "srprop": "size|wordcount|timestamp|snippet",
                "srenablerewrites": "1",
                "srsort": "relevance"
            }

            mock_request.assert_called_once_with("GET", params=expected_params)
            assert result["query"]["search"][0]["title"] == "Test"


class TestExistingFunctionality:
    """Test existing edit and get page functionality."""

    @pytest.mark.asyncio
    async def test_handle_edit_page_success(self, mock_config):
        """Test successful page edit."""
        mock_client = Mock(spec=MediaWikiClient)
        mock_client.edit_page = AsyncMock(return_value={
            "result": "Success",
            "title": "Test Page",
            "newrevid": 12345,
            "newtimestamp": "2023-01-01T12:00:00Z"
        })

        arguments = {
            "title": "Test Page",
            "text": "Test content",
            "summary": "Test edit"
        }

        result = await handle_edit_page(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "Successfully edited page 'Test Page'" in response_text
        assert "New revision ID: 12345" in response_text

    @pytest.mark.asyncio
    async def test_handle_get_page_success(self, mock_config):
        """Test successful page retrieval."""
        mock_response = {
            "query": {
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "title": "Test Page",
                        "revisions": [
                            {"*": "This is the page content"}
                        ]
                    }
                }
            }
        }

        mock_client = Mock(spec=MediaWikiClient)
        mock_client.get_page_info = AsyncMock(return_value=mock_response)

        arguments = {"title": "Test Page"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        response_text = result[0].text
        assert "Page: Test Page (ID: 12345)" in response_text
        assert "This is the page content" in response_text


@pytest.mark.asyncio
async def test_list_tools():
    """Test that search tool is included in tool list."""
    tools = await mcp.list_tools()

    tool_names = [tool.name for tool in tools]
    assert "wiki_search" in tool_names
    assert "wiki_page_edit" in tool_names
    assert "wiki_page_get" in tool_names

    # Find the search tool and verify its schema
    search_tool = next(tool for tool in tools if tool.name == "wiki_search")
    assert search_tool.description == "Search for wiki pages by title or content using MediaWiki's search API"

    # Verify required fields
    assert "query" in search_tool.inputSchema["required"]

    # Verify search-specific properties exist
    properties = search_tool.inputSchema["properties"]
    assert "query" in properties
    assert "namespaces" in properties
    assert "limit" in properties
    assert "what" in properties
    assert "sort" in properties
    assert "qiprofile" in properties


def test_get_config_with_env_vars():
    """Test configuration loading from environment variables."""
    with patch.dict('os.environ', {
        'MEDIAWIKI_API_URL': 'http://test.wiki/api.php',
        'MEDIAWIKI_API_BOT_USERNAME': 'testuser',
        'MEDIAWIKI_API_BOT_PASSWORD': 'testpass',
        'MEDIAWIKI_API_BOT_USER_AGENT': 'Test-Bot/1.0'
    }):
        config = get_config()
        assert config.api_url == 'http://test.wiki/api.php'
        assert config.username == 'testuser'
        assert config.password == 'testpass'
        assert config.user_agent == 'Test-Bot/1.0'
