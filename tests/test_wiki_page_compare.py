"""Test suite for MediaWiki page compare handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_compare import handle_compare_pages


class TestCompareHandlers:
    """Test cases for page comparison handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_compare_pages_by_title_success(self, mock_client):
        """Test successful page comparison by titles."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromid": 12345,
                "fromrevid": 987654,
                "fromns": 0,
                "fromtitle": "Page A",
                "toid": 67890,
                "torevid": 543210,
                "tons": 0,
                "totitle": "Page B",
                "diff": "<tr><td class='diff-marker'>+</td><td class='diff-content'>Added content</td></tr>",
                "diffsize": 123
            }
        }

        # Test arguments
        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "prop": "diff|ids|title|diffsize"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify client was called correctly
        mock_client.compare_pages.assert_called_once_with(
            fromtitle="Page A",
            fromid=None,
            fromrev=None,
            fromslots=None,
            frompst=False,
            totitle="Page B",
            toid=None,
            torev=None,
            torelative=None,
            toslots=None,
            topst=False,
            prop=["diff", "ids", "title", "diffsize"],
            slots=None,
            difftype="table"
        )

        # Verify result format
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Comparing: 'Page A' → 'Page B'" in result[0].text
        assert "Revisions: 987654 → 543210" in result[0].text
        assert "Diff size: 123 bytes" in result[0].text
        assert "Diff HTML:" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_by_revision_success(self, mock_client):
        """Test successful page comparison by revision IDs."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromid": 12345,
                "fromrevid": 100,
                "toid": 12345,
                "torevid": 200,
                "fromtimestamp": "2024-01-01T10:00:00Z",
                "totimestamp": "2024-01-01T11:00:00Z",
                "fromuser": "User1",
                "touser": "User2",
                "fromcomment": "Initial revision",
                "tocomment": "Updated content",
                "diff": ""
            }
        }

        # Test arguments
        arguments = {
            "fromrev": 100,
            "torev": 200,
            "prop": "diff|ids|timestamp|user|comment"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify client was called correctly
        mock_client.compare_pages.assert_called_once_with(
            fromtitle=None,
            fromid=None,
            fromrev=100,
            fromslots=None,
            frompst=False,
            totitle=None,
            toid=None,
            torev=200,
            torelative=None,
            toslots=None,
            topst=False,
            prop=["diff", "ids", "timestamp", "user", "comment"],
            slots=None,
            difftype="table"
        )

        # Verify result format
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Revisions: 100 → 200" in result[0].text
        assert "From timestamp: 2024-01-01T10:00:00Z" in result[0].text
        assert "To timestamp: 2024-01-01T11:00:00Z" in result[0].text
        assert "From user: User1" in result[0].text
        assert "To user: User2" in result[0].text
        assert "From comment: Initial revision" in result[0].text
        assert "To comment: Updated content" in result[0].text
        assert "No differences found between the compared revisions." in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_relative_comparison(self, mock_client):
        """Test page comparison with relative revision."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromid": 12345,
                "fromrevid": 100,
                "toid": 12345,
                "torevid": 101,
                "diff": "<tr><td class='diff-marker'>+</td><td class='diff-content'>New line</td></tr>"
            }
        }

        # Test arguments
        arguments = {
            "fromrev": 100,
            "torelative": "next"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify client was called correctly
        mock_client.compare_pages.assert_called_once_with(
            fromtitle=None,
            fromid=None,
            fromrev=100,
            fromslots=None,
            frompst=False,
            totitle=None,
            toid=None,
            torev=None,
            torelative="next",
            toslots=None,
            topst=False,
            prop=None,
            slots=None,
            difftype="table"
        )

        # Verify result
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Revisions: 100 → 101" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_with_slots(self, mock_client):
        """Test page comparison with slot-specific diffs."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromid": 12345,
                "fromrevid": 100,
                "toid": 12345,
                "torevid": 101,
                "diff": "<tr><td>Combined diff</td></tr>",
                "slots": {
                    "main": {
                        "diff": "<tr><td>Main slot diff</td></tr>"
                    }
                }
            }
        }

        # Test arguments
        arguments = {
            "fromrev": 100,
            "torev": 101,
            "slots": "main"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify client was called correctly
        mock_client.compare_pages.assert_called_once_with(
            fromtitle=None,
            fromid=None,
            fromrev=100,
            fromslots=None,
            frompst=False,
            totitle=None,
            toid=None,
            torev=101,
            torelative=None,
            toslots=None,
            topst=False,
            prop=None,
            slots=["main"],
            difftype="table"
        )

        # Verify result includes slot-specific diffs
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Slot-specific diffs:" in result[0].text
        assert "Slot 'main':" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_with_templated_parameters(self, mock_client):
        """Test page comparison with templated slot parameters."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromid": 12345,
                "fromrevid": 100,
                "toid": 12345,
                "torevid": 101,
                "diff": "<tr><td>Text comparison diff</td></tr>"
            }
        }

        # Test arguments
        arguments = {
            "fromrev": 100,
            "torev": 101,
            "fromslots": "main",
            "fromtext-main": "Original text",
            "fromcontentmodel-main": "wikitext",
            "totext-main": "Modified text",
            "tocontentmodel-main": "wikitext"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify client was called with templated parameters
        mock_client.compare_pages.assert_called_once_with(
            fromtitle=None,
            fromid=None,
            fromrev=100,
            fromslots=["main"],
            frompst=False,
            totitle=None,
            toid=None,
            torev=101,
            torelative=None,
            toslots=None,
            topst=False,
            prop=None,
            slots=None,
            difftype="table",
            **{
                "fromtext-main": "Original text",
                "fromcontentmodel-main": "wikitext",
                "totext-main": "Modified text",
                "tocontentmodel-main": "wikitext"
            }
        )

        # Verify result
        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_handle_compare_pages_missing_from_parameters(self, mock_client):
        """Test error when no 'from' parameters are specified."""
        arguments = {
            "totitle": "Page B"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify error message
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Must specify at least one 'from' parameter" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_missing_to_parameters(self, mock_client):
        """Test error when no 'to' parameters are specified."""
        arguments = {
            "fromtitle": "Page A"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify error message
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Must specify at least one 'to' parameter" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_api_error(self, mock_client):
        """Test handling of API errors."""
        # Setup mock to raise an exception
        mock_client.compare_pages.side_effect = Exception("API connection failed")

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify error handling
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error comparing pages: API connection failed" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_unexpected_response(self, mock_client):
        """Test handling of unexpected API response format."""
        # Setup mock response without 'compare' key
        mock_client.compare_pages.return_value = {
            "error": {
                "code": "badtitle",
                "info": "Invalid title"
            }
        }

        arguments = {
            "fromtitle": "Invalid Title",
            "totitle": "Page B"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify error handling
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Error: Unexpected response format from MediaWiki Compare API" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_pages_pipe_separated_values(self, mock_client):
        """Test handling of pipe-separated parameter values."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page B",
                "diff": "<tr><td>diff</td></tr>"
            }
        }

        # Test arguments with pipe-separated values
        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "prop": "diff|ids|title|user",
            "slots": "*",
            "fromslots": "main"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify lists were parsed correctly
        mock_client.compare_pages.assert_called_once_with(
            fromtitle="Page A",
            fromid=None,
            fromrev=None,
            fromslots=["main"],
            frompst=False,
            totitle="Page B",
            toid=None,
            torev=None,
            torelative=None,
            toslots=None,
            topst=False,
            prop=["diff", "ids", "title", "user"],
            slots=["*"],
            difftype="table"
        )

        assert len(result) == 1
        assert result[0].type == "text"

    @pytest.mark.asyncio
    async def test_handle_compare_pages_different_diff_types(self, mock_client):
        """Test page comparison with different diff format types."""
        # Setup mock response
        mock_client.compare_pages.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page B",
                "diff": "Unified diff format content"
            }
        }

        # Test arguments with unified diff type
        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "difftype": "unified"
        }

        result = await handle_compare_pages(mock_client, arguments)

        # Verify difftype was passed correctly
        mock_client.compare_pages.assert_called_once_with(
            fromtitle="Page A",
            fromid=None,
            fromrev=None,
            fromslots=None,
            frompst=False,
            totitle="Page B",
            toid=None,
            torev=None,
            torelative=None,
            toslots=None,
            topst=False,
            prop=None,
            slots=None,
            difftype="unified"
        )

        assert len(result) == 1
        assert result[0].type == "text"
