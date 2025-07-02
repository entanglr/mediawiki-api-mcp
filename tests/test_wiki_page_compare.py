"""Test suite for MediaWiki page comparison handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_compare import handle_compare_page


class TestCompareHandlers:
    """Test cases for page comparison handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_compare_page_success_basic(self, mock_client):
        """Test successful page comparison with basic parameters."""
        # Setup mock response
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "fromid": 123,
                "fromrevid": 456,
                "fromns": 0,
                "totitle": "Page B",
                "toid": 789,
                "torevid": 12,
                "tons": 0,
                "body": "<tr><td colspan='2' width='50%' align='center' class='diff-otitle'>Revision as of 10:00, 1 January 2024</td><td colspan='2' width='50%' align='center' class='diff-ntitle'>Revision as of 11:00, 1 January 2024</td></tr><tr><td>-</td><td class='diff-deletedline'><div>Old content</div></td><td>+</td><td class='diff-addedline'><div>New content</div></td></tr>"
            }
        }

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "difftype": "table"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "# Page Comparison Result" in result[0].text
        assert "**From:** Title: Page A, ID: 123, Revision: 456, Namespace: 0" in result[0].text
        assert "**To:** Title: Page B, ID: 789, Revision: 12, Namespace: 0" in result[0].text
        assert "**Diff format:** table" in result[0].text
        assert "## Comparison Output" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_success_revisions(self, mock_client):
        """Test successful page comparison between specific revisions."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromrevid": 100,
                "torevid": 200,
                "fromtitle": "Example Page",
                "totitle": "Example Page",
                "body": "<table class='diff'><tr><td>Example diff content</td></tr></table>"
            }
        }

        arguments = {
            "fromrev": 100,
            "torev": 200,
            "difftype": "table"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "**From:** Title: Example Page, Revision: 100" in result[0].text
        assert "**To:** Title: Example Page, Revision: 200" in result[0].text
        assert "Example diff content" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_with_slot_params(self, mock_client):
        """Test page comparison with slot-specific parameters."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page A",
                "body": "Slot-based comparison result"
            }
        }

        arguments = {
            "fromtitle": "Page A",
            "toslots": "main",
            "totext-main": "Modified content",
            "tocontentmodel-main": "wikitext",
            "frompst-main": True,
            "difftype": "unified"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "# Page Comparison Result" in result[0].text
        assert "**Diff format:** unified" in result[0].text

        # Verify that slot parameters were passed to the client
        mock_client.compare_page.assert_called_once()
        call_args = mock_client.compare_page.call_args
        assert call_args[1]["fromtitle"] == "Page A"
        assert call_args[1]["toslots"] == "main"
        assert call_args[1]["slot_params"]["totext-main"] == "Modified content"
        assert call_args[1]["slot_params"]["tocontentmodel-main"] == "wikitext"
        assert call_args[1]["slot_params"]["frompst-main"] is True

    @pytest.mark.asyncio
    async def test_handle_compare_page_legacy_parameters(self, mock_client):
        """Test page comparison with legacy parameters."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Test Page",
                "totitle": "Test Page",
                "*": "Legacy format diff content"
            }
        }

        arguments = {
            "fromtitle": "Test Page",
            "totext": "New content",
            "fromcontentformat": "text/x-wiki",
            "tocontentmodel": "wikitext",
            "tosection": "1"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "Legacy format diff content" in result[0].text

        # Verify legacy parameters were passed correctly
        mock_client.compare_page.assert_called_once()
        call_args = mock_client.compare_page.call_args
        assert call_args[1]["totext"] == "New content"
        assert call_args[1]["fromcontentformat"] == "text/x-wiki"
        assert call_args[1]["tocontentmodel"] == "wikitext"
        assert call_args[1]["tosection"] == "1"

    @pytest.mark.asyncio
    async def test_handle_compare_page_with_metadata(self, mock_client):
        """Test page comparison result with metadata."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page B",
                "fromsize": 1024,
                "tosize": 2048,
                "diff": "Diff content with metadata"
            }
        }

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "prop": "*"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "## Metadata" in result[0].text
        assert "From size: 1024 bytes" in result[0].text
        assert "To size: 2048 bytes" in result[0].text
        assert "## Diff Comparison" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_unexpected_response(self, mock_client):
        """Test handling of unexpected API response format."""
        mock_client.compare_page.return_value = {
            "error": "Invalid parameters"
        }

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Unexpected response format from MediaWiki Compare API" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_raw_response_fallback(self, mock_client):
        """Test fallback to raw response when expected fields are missing."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page B",
                "someunknownfield": "Unknown data structure"
            }
        }

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "## Raw API Response" in result[0].text
        assert "someunknownfield" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_exception(self, mock_client):
        """Test handling of client exceptions."""
        mock_client.compare_page.side_effect = Exception("Network error")

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error comparing pages: Network error" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_multiple_diff_fields(self, mock_client):
        """Test handling of different diff field formats."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page B",
                "text": "Text format diff content"
            }
        }

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "difftype": "inline"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "## Text Comparison" in result[0].text
        assert "Text format diff content" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_compare_page_html_diff(self, mock_client):
        """Test handling of HTML diff format."""
        mock_client.compare_page.return_value = {
            "compare": {
                "fromtitle": "Page A",
                "totitle": "Page B",
                "html": "<div class='diff-html'>HTML diff content</div>"
            }
        }

        arguments = {
            "fromtitle": "Page A",
            "totitle": "Page B",
            "difftype": "table"
        }

        result = await handle_compare_page(mock_client, arguments)

        assert len(result) == 1
        assert "## Html Comparison" in result[0].text
        assert "<div class='diff-html'>HTML diff content</div>" in result[0].text
