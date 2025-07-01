"""Test suite for MediaWiki page parse handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_parse import handle_parse_page


class TestParseHandlers:
    """Test cases for parse-related handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_parse_page_success(self, mock_client):
        """Test successful page parsing."""
        # Setup mock response
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Hello world</p>"},
                "wikitext": {"*": "Hello world"},
                "categories": [{"*": "Category:Test"}],
                "links": [{"*": "Another Page"}],
                "sections": [{"level": 1, "line": "Introduction"}]
            }
        }

        arguments = {
            "title": "Test Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Parse Results for: Test Page" in result[0].text
        assert "Page ID: 12345" in result[0].text
        assert "Revision ID: 67890" in result[0].text
        assert "## Parsed HTML" in result[0].text
        assert "Hello world" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_by_text(self, mock_client):
        """Test parsing arbitrary text."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "API",
                "pageid": 0,
                "revid": 0,
                "text": {"*": "<p>Some <b>bold</b> text</p>"},
                "wikitext": {"*": "Some '''bold''' text"}
            }
        }

        arguments = {
            "text": "Some '''bold''' text",
            "title": "Test"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Parse Results for: API" in result[0].text
        assert "## Parsed HTML" in result[0].text
        assert "bold" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_with_prop_filter(self, mock_client):
        """Test parsing with specific prop filter."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Hello world</p>"},
                "categories": [{"*": "Category:Test"}]
            }
        }

        arguments = {
            "title": "Test Page",
            "prop": "text|categories"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Requested properties: text, categories" in result[0].text
        assert "## Parsed HTML" in result[0].text
        assert "## Categories" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_missing_content_source(self, mock_client):
        """Test parse page with missing content source parameters."""
        arguments = {}

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Must provide one of: title, pageid, oldid, text, page, or summary" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_unexpected_response(self, mock_client):
        """Test parse page with unexpected API response."""
        mock_client.parse_page.return_value = {
            "error": "Invalid request"
        }

        arguments = {
            "title": "Test Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Unexpected response format from Parse API" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_exception(self, mock_client):
        """Test parse page with client exception."""
        mock_client.parse_page.side_effect = Exception("Network error")

        arguments = {
            "title": "Test Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error parsing content: Network error" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_comprehensive_output(self, mock_client):
        """Test parse page with comprehensive output sections."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Comprehensive Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Main content</p>"},
                "wikitext": {"*": "Main content"},
                "categories": [{"*": "Category:Test"}, {"*": "Category:Example"}],
                "links": [{"*": "Link One"}, {"*": "Link Two"}],
                "templates": [{"*": "Template:Info"}],
                "images": ["File:Example.jpg"],
                "externallinks": ["https://example.com"],
                "sections": [
                    {"level": 1, "line": "Introduction"},
                    {"level": 2, "line": "Details"}
                ],
                "langlinks": [{"lang": "es", "*": "Página de prueba"}],
                "iwlinks": [{"prefix": "w", "*": "Main Page"}],
                "properties": [{"name": "displaytitle", "*": "Display Title"}],
                "parsewarnings": ["Warning message"],
                "displaytitle": "Custom Display Title"
            }
        }

        arguments = {
            "title": "Comprehensive Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        content = result[0].text

        # Check that all sections are present
        assert "## Parsed HTML" in content
        assert "## Wikitext" in content
        assert "## Categories" in content
        assert "## Internal Links" in content
        assert "## Templates" in content
        assert "## Images" in content
        assert "## External Links" in content
        assert "## Sections" in content
        assert "## Language Links" in content
        assert "## Interwiki Links" in content
        assert "## Properties" in content
        assert "## Parse Warnings" in content
        assert "## Display Title" in content

        # Check specific content
        assert "Category:Test" in content
        assert "Link One" in content
        assert "Template:Info" in content
        assert "File:Example.jpg" in content
        assert "https://example.com" in content
        assert "Level 1: Introduction" in content
        assert "es: Página de prueba" in content
        assert "w: Main Page" in content
        assert "Custom Display Title" in content

    @pytest.mark.asyncio
    async def test_handle_parse_page_prop_parsing(self, mock_client):
        """Test proper parsing of prop parameter from string to list."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Test content</p>"}
            }
        }

        arguments = {
            "title": "Test Page",
            "prop": "text | categories | links"  # Test with spaces
        }

        await handle_parse_page(mock_client, arguments)

        # Verify the prop was properly parsed and passed to the client
        mock_client.parse_page.assert_called_once()
        call_args = mock_client.parse_page.call_args
        assert call_args.kwargs["prop"] == ["text", "categories", "links"]

    @pytest.mark.asyncio
    async def test_handle_parse_page_template_sandbox_parsing(self, mock_client):
        """Test proper parsing of template sandbox prefix parameter."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Test content</p>"}
            }
        }

        arguments = {
            "title": "Test Page",
            "templatesandboxprefix": "User:Test | User:Demo"  # Test with spaces
        }

        await handle_parse_page(mock_client, arguments)

        # Verify the templatesandboxprefix was properly parsed and passed to the client
        mock_client.parse_page.assert_called_once()
        call_args = mock_client.parse_page.call_args
        assert call_args.kwargs["templatesandboxprefix"] == ["User:Test", "User:Demo"]
