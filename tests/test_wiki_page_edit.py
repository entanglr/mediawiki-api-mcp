"""Test suite for MediaWiki edit handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_edit import handle_edit_page


class TestEditHandlers:
    """Test cases for edit-related handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_edit_page_success(self, mock_client):
        """Test successful page edit."""
        # Setup mock response
        mock_client.edit_page.return_value = {
            "result": "Success",
            "title": "Test Page",
            "newrevid": 12345,
            "newtimestamp": "2024-01-01T12:00:00Z"
        }

        arguments = {
            "title": "Test Page",
            "text": "Test content",
            "summary": "Test edit"
        }

        result = await handle_edit_page(mock_client, arguments)

        assert len(result) == 1
        assert "Successfully edited page 'Test Page'" in result[0].text
        assert "New revision ID: 12345" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_edit_page_missing_params(self, mock_client):
        """Test edit page with missing required parameters."""
        arguments = {}

        result = await handle_edit_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Either 'title' or 'pageid' must be provided" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_edit_page_failure(self, mock_client):
        """Test edit page failure response."""
        mock_client.edit_page.return_value = {
            "result": "Failure",
            "error": "Permission denied"
        }

        arguments = {
            "title": "Test Page",
            "text": "Test content"
        }

        result = await handle_edit_page(mock_client, arguments)

        assert len(result) == 1
        assert "Edit failed:" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_edit_page_exception(self, mock_client):
        """Test edit page with client exception."""
        mock_client.edit_page.side_effect = Exception("Network error")

        arguments = {
            "title": "Test Page",
            "text": "Test content"
        }

        result = await handle_edit_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error editing page: Network error" in result[0].text
