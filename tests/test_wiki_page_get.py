"""Test suite for MediaWiki page retrieval handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_get import handle_get_page


class TestGetHandlers:
    """Test cases for page retrieval-related handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    # Test parameter validation
    @pytest.mark.asyncio
    async def test_handle_get_page_missing_params(self, mock_client):
        """Test get page with missing required parameters."""
        arguments = {}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Either 'title' or 'pageid' must be provided" in result[0].text

    # Tests for revisions method (default)
    @pytest.mark.asyncio
    async def test_handle_get_page_revisions_success(self, mock_client):
        """Test successful page retrieval using revisions method with formatversion=2."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 12345,
                        "title": "Test Page",
                        "revisions": [
                            {
                                "slots": {
                                    "main": {
                                        "content": "Test page content with '''bold''' text"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }

        arguments = {"title": "Test Page"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "Method: Revisions API" in result[0].text
        assert "Format: Wikitext" in result[0].text
        assert "Test page content with '''bold''' text" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_revisions_with_pageid(self, mock_client):
        """Test revisions method with pageid instead of title."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 54321,
                        "title": "Another Test Page",
                        "revisions": [
                            {
                                "slots": {
                                    "main": {
                                        "content": "Content from pageid lookup"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }

        arguments = {"pageid": 54321, "method": "revisions"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Another Test Page (ID: 54321)" in result[0].text
        assert "Content from pageid lookup" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_revisions_missing_page(self, mock_client):
        """Test revisions method for non-existent page."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": [
                    {
                        "title": "Nonexistent Page",
                        "missing": True
                    }
                ]
            }
        }

        arguments = {"title": "Nonexistent Page", "method": "revisions"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page not found: Nonexistent Page" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_revisions_no_content(self, mock_client):
        """Test revisions method with page that has no content."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 67890,
                        "title": "Empty Page",
                        "revisions": []
                    }
                ]
            }
        }

        arguments = {"title": "Empty Page", "method": "revisions"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Empty Page (ID: 67890)" in result[0].text
        assert "No content available" in result[0].text

    # Tests for raw method
    @pytest.mark.asyncio
    async def test_handle_get_page_raw_success(self, mock_client):
        """Test successful page retrieval using raw method."""
        mock_client.get_page_raw.return_value = "Raw wikitext content\n\n== Section ==\nSome content here"

        arguments = {"title": "Test Page", "method": "raw"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (Raw Wikitext)" in result[0].text
        assert "Raw wikitext content" in result[0].text
        assert "== Section ==" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_raw_with_pageid(self, mock_client):
        """Test raw method with pageid."""
        mock_client.get_page_raw.return_value = "Content retrieved by ID"

        arguments = {"pageid": 12345, "method": "raw"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: ID: 12345 (Raw Wikitext)" in result[0].text
        assert "Content retrieved by ID" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_raw_exception(self, mock_client):
        """Test raw method with client exception."""
        mock_client.get_page_raw.side_effect = Exception("Network error")

        arguments = {"title": "Test Page", "method": "raw"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error with raw method: Network error" in result[0].text

    # Tests for parse method
    @pytest.mark.asyncio
    async def test_handle_get_page_parse_html(self, mock_client):
        """Test parse method with HTML format."""
        mock_client.get_page_parse.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "text": "<p>Parsed <b>HTML</b> content</p>"
            }
        }

        arguments = {"title": "Test Page", "method": "parse", "format": "html"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "Method: Parse API" in result[0].text
        assert "Format: HTML" in result[0].text
        assert "<p>Parsed <b>HTML</b> content</p>" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_parse_wikitext(self, mock_client):
        """Test parse method with wikitext format."""
        mock_client.get_page_parse.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "wikitext": "'''Bold''' text and [[links]]"
            }
        }

        arguments = {"title": "Test Page", "method": "parse", "format": "wikitext"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "Method: Parse API" in result[0].text
        assert "Format: Wikitext" in result[0].text
        assert "'''Bold''' text and [[links]]" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_parse_no_content(self, mock_client):
        """Test parse method with no content available."""
        mock_client.get_page_parse.return_value = {
            "parse": {
                "title": "Empty Page",
                "pageid": 99999
            }
        }

        arguments = {"title": "Empty Page", "method": "parse"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Empty Page (ID: 99999)" in result[0].text
        assert "No content available" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_parse_exception(self, mock_client):
        """Test parse method with client exception."""
        mock_client.get_page_parse.side_effect = Exception("Parse error")

        arguments = {"title": "Test Page", "method": "parse"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error with parse method: Parse error" in result[0].text

    # Tests for extracts method
    @pytest.mark.asyncio
    async def test_handle_get_page_extracts_plain_text(self, mock_client):
        """Test extracts method with plain text."""
        mock_client.get_page_extracts.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 12345,
                        "title": "Test Page",
                        "extract": "This is a plain text extract of the page content without any markup."
                    }
                ]
            }
        }

        arguments = {"title": "Test Page", "method": "extracts", "format": "text"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "Method: TextExtracts API" in result[0].text
        assert "Format: Plain Text" in result[0].text
        assert "This is a plain text extract" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_extracts_with_sentences(self, mock_client):
        """Test extracts method with sentence limit."""
        mock_client.get_page_extracts.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 12345,
                        "title": "Test Page",
                        "extract": "First sentence. Second sentence."
                    }
                ]
            }
        }

        arguments = {"title": "Test Page", "method": "extracts", "sentences": 2}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "(Limited to 2 sentences)" in result[0].text
        assert "First sentence. Second sentence." in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_extracts_with_chars(self, mock_client):
        """Test extracts method with character limit."""
        mock_client.get_page_extracts.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 12345,
                        "title": "Test Page",
                        "extract": "This is a character-limited extract"
                    }
                ]
            }
        }

        arguments = {"title": "Test Page", "method": "extracts", "chars": 100}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "(Limited to 100 characters)" in result[0].text
        assert "This is a character-limited extract" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_extracts_limited_html(self, mock_client):
        """Test extracts method with limited HTML format."""
        mock_client.get_page_extracts.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 12345,
                        "title": "Test Page",
                        "extract": "<p>Limited HTML extract with some <b>formatting</b></p>"
                    }
                ]
            }
        }

        arguments = {"title": "Test Page", "method": "extracts", "format": "wikitext"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Format: Limited HTML" in result[0].text
        assert "<p>Limited HTML extract" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_extracts_missing_page(self, mock_client):
        """Test extracts method for non-existent page."""
        mock_client.get_page_extracts.return_value = {
            "query": {
                "pages": [
                    {
                        "title": "Nonexistent Page",
                        "missing": True
                    }
                ]
            }
        }

        arguments = {"title": "Nonexistent Page", "method": "extracts"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page not found: Nonexistent Page" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_extracts_exception(self, mock_client):
        """Test extracts method with client exception."""
        mock_client.get_page_extracts.side_effect = Exception("Extracts error")

        arguments = {"title": "Test Page", "method": "extracts"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error with extracts method: Extracts error" in result[0].text

    # Test error handling and edge cases
    @pytest.mark.asyncio
    async def test_handle_get_page_unexpected_response_format_revisions(self, mock_client):
        """Test revisions method with unexpected response format."""
        mock_client.get_page_info.return_value = {
            "unexpected": "format"
        }

        arguments = {"title": "Test Page", "method": "revisions"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Unexpected response format from MediaWiki API" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_unexpected_response_format_parse(self, mock_client):
        """Test parse method with unexpected response format."""
        mock_client.get_page_parse.return_value = {
            "unexpected": "format"
        }

        arguments = {"title": "Test Page", "method": "parse"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Unexpected response format from Parse API" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_unexpected_response_format_extracts(self, mock_client):
        """Test extracts method with unexpected response format."""
        mock_client.get_page_extracts.return_value = {
            "unexpected": "format"
        }

        arguments = {"title": "Test Page", "method": "extracts"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Unexpected response format from TextExtracts API" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_general_exception(self, mock_client):
        """Test general exception handling."""
        mock_client.get_page_info.side_effect = Exception("General network error")

        arguments = {"title": "Test Page"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error retrieving page: General network error" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_empty_pages_list(self, mock_client):
        """Test handling when pages list is empty."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": []
            }
        }

        arguments = {"title": "Test Page", "method": "revisions"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "No pages found" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_method_fallback_to_revisions(self, mock_client):
        """Test that unknown methods fall back to revisions."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": [
                    {
                        "pageid": 12345,
                        "title": "Test Page",
                        "revisions": [
                            {
                                "slots": {
                                    "main": {
                                        "content": "Fallback content"
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        }

        arguments = {"title": "Test Page", "method": "unknown_method"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "Method: Revisions API" in result[0].text
        assert "Fallback content" in result[0].text
