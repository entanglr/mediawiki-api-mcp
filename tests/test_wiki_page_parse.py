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
        assert "MediaWiki API Error: Invalid request" in result[0].text

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

    @pytest.mark.asyncio
    async def test_handle_parse_page_invalid_section(self, mock_client):
        """Test parse page with invalid section parameter."""
        # Mock a validation error
        mock_client.parse_page.side_effect = ValueError("Section parameter must be a number, 'new', or 'T-' prefixed template section")

        arguments = {
            "title": "Test Page",
            "section": "invalid_section"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Section parameter must be a number, 'new', or 'T-' prefixed template section" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_valid_section_types(self, mock_client):
        """Test parse page with valid section parameter types."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Section content</p>"}
            }
        }

        # Test integer section
        arguments = {
            "title": "Test Page",
            "section": "1"
        }
        result = await handle_parse_page(mock_client, arguments)
        assert len(result) == 1
        assert "Parse Results for: Test Page" in result[0].text

        # Test "new" section
        arguments["section"] = "new"
        result = await handle_parse_page(mock_client, arguments)
        assert len(result) == 1
        assert "Parse Results for: Test Page" in result[0].text

        # Test template section
        arguments["section"] = "T-1"
        result = await handle_parse_page(mock_client, arguments)
        assert len(result) == 1
        assert "Parse Results for: Test Page" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_minimal_content_detection(self, mock_client):
        """Test detection of minimal content issues."""
        # Test minimal content that should trigger warning
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": '<div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr"></div>'}
            }
        }

        arguments = {
            "title": "Test Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "WARNING: Content appears minimal" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_missing_content(self, mock_client):
        """Test detection of completely missing content."""
        # Test no text content returned for existing page
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890
                # No "text" field
            }
        }

        arguments = {
            "title": "Test Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "WARNING: No text content in parse result" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_parse_page_summary_only(self, mock_client):
        """Test parsing summary parameter independently."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "API",
                "pageid": 0,
                "revid": 0,
                "text": {"*": "<p>Some <b>summary</b> content</p>"}
            }
        }

        arguments = {
            "summary": "Some [[link]] summary"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        assert "Parse Results for: API" in result[0].text
        # Verify the summary parameter was passed correctly
        mock_client.parse_page.assert_called_once()
        call_args = mock_client.parse_page.call_args
        assert call_args.kwargs["summary"] == "Some [[link]] summary"
        # Verify prop was set to empty list for summary parsing
        assert call_args.kwargs["prop"] == []

    @pytest.mark.asyncio
    async def test_handle_parse_page_summary_fallback_mechanism(self, mock_client):
        """Test fallback mechanism when summary parsing returns minimal content."""
        # First call (summary parsing) returns minimal content
        # Second call (fallback text parsing) returns proper content
        side_effect_values = [
            {
                "parse": {
                    "title": "API",
                    "pageid": 0,
                    "revid": 0,
                    "text": {"*": '<div class="mw-parser-output"></div>'}  # Minimal content
                }
            },
            {
                "parse": {
                    "title": "API",
                    "pageid": 0,
                    "revid": 0,
                    "text": {"*": "<p>Some <a href=\"/wiki/Link\">link</a> and <b>formatting</b></p>"},
                    "links": [{"*": "Link"}],
                    "parsewarnings": []
                }
            }
        ]

        mock_client.parse_page.side_effect = side_effect_values

        arguments = {
            "summary": "Some [[link]] and '''formatting'''"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        result_text = result[0].text

        # Should show the fallback worked
        assert "Parse Results for: API" in result_text
        assert "Some <a href=\"/wiki/Link\">link</a>" in result_text or "Link" in result_text
        assert "formatting" in result_text

        # Verify both calls were made - first for summary, then for fallback
        assert mock_client.parse_page.call_count == 2

        # Check first call (summary parsing)
        first_call = mock_client.parse_page.call_args_list[0]
        assert first_call.kwargs["summary"] == "Some [[link]] and '''formatting'''"
        assert first_call.kwargs["prop"] == []

        # Check second call (fallback text parsing)
        second_call = mock_client.parse_page.call_args_list[1]
        assert second_call.kwargs["text"] == "Some [[link]] and '''formatting'''"
        assert second_call.kwargs["contentmodel"] == "wikitext"
        assert "text" in second_call.kwargs["prop"]

    @pytest.mark.asyncio
    async def test_handle_parse_page_summary_no_fallback_when_content_good(self, mock_client):
        """Test that fallback is not triggered when summary parsing returns good content."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "API",
                "pageid": 0,
                "revid": 0,
                "text": {"*": "<p>Good summary content with <a href=\"/wiki/Link\">link</a> and <b>formatting</b></p>"}
            }
        }

        arguments = {
            "summary": "Good summary with [[link]] and '''formatting'''"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        result_text = result[0].text

        # Should show the good content
        assert "Good summary content" in result_text
        assert "link" in result_text
        assert "formatting" in result_text

        # Should only make one call (no fallback needed)
        assert mock_client.parse_page.call_count == 1

        # Verify it was the summary call
        call_args = mock_client.parse_page.call_args
        assert call_args.kwargs["summary"] == "Good summary with [[link]] and '''formatting'''"

    @pytest.mark.asyncio
    async def test_minimal_content_detection(self):
        """Test the _is_minimal_content helper function."""
        from mediawiki_api_mcp.handlers.wiki_page_parse import _is_minimal_content

        # Should detect minimal content
        assert _is_minimal_content("") == True
        assert _is_minimal_content("   ") == True
        assert _is_minimal_content("<p></p>") == True
        assert _is_minimal_content("<div></div>") == True
        assert _is_minimal_content('<div class="mw-parser-output"></div>') == True
        assert _is_minimal_content('<div class="mw-parser-output">   </div>') == True

        # Should not detect good content as minimal
        assert _is_minimal_content("<p>Real content here</p>") == False
        assert _is_minimal_content("<p>Some <b>formatted</b> text</p>") == False
        assert _is_minimal_content('<div class="mw-parser-output"><p>Actual content</p></div>') == False

    @pytest.mark.asyncio
    async def test_title_vs_page_parameter_consistency(self, mock_client):
        """Test that title and page parameters produce identical API calls."""
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Test content</p>"}
            }
        }

        # Test with title parameter
        arguments_title = {"title": "Test Page"}
        await handle_parse_page(mock_client, arguments_title)

        # Get the call arguments for title
        title_call_args = mock_client.parse_page.call_args

        # Reset mock
        mock_client.reset_mock()
        mock_client.parse_page.return_value = {
            "parse": {
                "title": "Test Page",
                "pageid": 12345,
                "revid": 67890,
                "text": {"*": "<p>Test content</p>"}
            }
        }

        # Test with page parameter
        arguments_page = {"page": "Test Page"}
        await handle_parse_page(mock_client, arguments_page)

        # Get the call arguments for page
        page_call_args = mock_client.parse_page.call_args

        # The API calls should be identical - both should use page parameter
        assert title_call_args.kwargs.get("page") == "Test Page"
        assert page_call_args.kwargs.get("page") == "Test Page"
        assert title_call_args.kwargs.get("title") is None  # title should not be passed to API
        assert page_call_args.kwargs.get("title") is None

    @pytest.mark.asyncio
    async def test_enhanced_error_handling(self, mock_client):
        """Test enhanced error handling with detailed diagnostic information."""
        # Test case where page is missing
        mock_client.parse_page.return_value = {
            "query": {
                "pages": {
                    "-1": {
                        "missing": True,
                        "title": "Nonexistent Page"
                    }
                }
            }
        }

        arguments = {
            "title": "Nonexistent Page"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        error_text = result[0].text

        # Check that enhanced error information is present
        assert "Error: Unexpected response format from Parse API" in error_text
        assert "Response keys: ['query']" in error_text
        assert "Received 'query' response - this indicates the wrong API endpoint was used" in error_text
        assert "Used parameters: title='Nonexistent Page'" in error_text
        assert "page(s) marked as missing in query response" in error_text

    @pytest.mark.asyncio
    async def test_enhanced_error_handling_invalid_params(self, mock_client):
        """Test enhanced error handling for invalid parameter combinations."""
        # Test case with parameter conflict error
        mock_client.parse_page.return_value = {
            "error": {
                "code": "invalidparammix",
                "info": "The parameters page, title cannot be used together."
            }
        }

        arguments = {
            "title": "Test Page",
            "text": "Some text"
        }

        result = await handle_parse_page(mock_client, arguments)

        assert len(result) == 1
        error_text = result[0].text

        # Should handle this as a regular API error, not unexpected response
        assert "MediaWiki API Error (invalidparammix)" in error_text
        assert "parameters page, title cannot be used together" in error_text

    @pytest.mark.asyncio
    async def test_empty_prop_parameter_included_in_api_request(self, mock_client):
        """Test that empty prop parameter is correctly included in API request for summary parsing."""
        from unittest.mock import AsyncMock, patch

        # Create a real MediaWiki client to test the parameter handling
        with patch('mediawiki_api_mcp.client_modules.client_page.MediaWikiPageClient') as MockPageClient:
            # Create a mock auth client
            mock_auth = AsyncMock()
            mock_auth._make_request = AsyncMock()
            mock_auth._make_request.return_value = {
                "parse": {
                    "title": "API",
                    "pageid": 0,
                    "revid": 0,
                    "text": {"*": "<p>Summary content</p>"}
                }
            }

            # Create the actual client instance to test
            from mediawiki_api_mcp.client_modules.client_page import MediaWikiPageClient
            page_client = MediaWikiPageClient(mock_auth)

            # Test summary parsing with empty prop
            await page_client.parse_page(summary="Test [[link]] summary")

            # Verify the API request was made with prop=""
            mock_auth._make_request.assert_called_once()
            call_args = mock_auth._make_request.call_args
            api_params = call_args[1]['params']  # GET request uses params

            # The critical fix: prop should be present with empty value
            assert 'prop' in api_params
            assert api_params['prop'] == ""  # Empty string, not missing
            assert api_params['summary'] == "Test [[link]] summary"
            assert api_params['action'] == "parse"
