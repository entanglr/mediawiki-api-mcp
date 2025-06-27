"""Test suite for MediaWiki move handlers."""

from unittest.mock import MagicMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_move import handle_move_page


class TestMoveHandlers:
    """Test cases for move-related handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_move_page_success(self, mock_client):
        """Test successful page move."""
        # Setup mock response
        mock_client.move_page.return_value = {
            "from": "Old Title",
            "to": "New Title",
            "reason": "Test move"
        }

        arguments = {
            "from": "Old Title",
            "to": "New Title",
            "reason": "Test move"
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Successfully moved page 'Old Title' to 'New Title'" in result[0].text
        assert "Reason: Test move" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_move_page_with_talk(self, mock_client):
        """Test page move with talk page."""
        # Setup mock response
        mock_client.move_page.return_value = {
            "from": "Old Title",
            "to": "New Title",
            "reason": "Test move",
            "talkfrom": "Talk:Old Title",
            "talkto": "Talk:New Title"
        }

        arguments = {
            "from": "Old Title",
            "to": "New Title",
            "reason": "Test move",
            "movetalk": True
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Successfully moved page 'Old Title' to 'New Title'" in result[0].text
        assert "Talk page moved from 'Talk:Old Title' to 'Talk:New Title'" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_move_page_missing_from_params(self, mock_client):
        """Test move page with missing from parameters."""
        arguments = {
            "to": "New Title"
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Either 'from' or 'fromid' must be provided" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_move_page_missing_to_param(self, mock_client):
        """Test move page with missing to parameter."""
        arguments = {
            "from": "Old Title"
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: 'to' parameter is required" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_move_page_error_response(self, mock_client):
        """Test move page with error response."""
        mock_client.move_page.return_value = {
            "error": {
                "code": "cantmove",
                "info": "You don't have permission to move this page"
            }
        }

        arguments = {
            "from": "Old Title",
            "to": "New Title"
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Move failed (cantmove): You don't have permission to move this page" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_move_page_exception(self, mock_client):
        """Test move page with client exception."""
        mock_client.move_page.side_effect = Exception("Network error")

        arguments = {
            "from": "Old Title",
            "to": "New Title"
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error moving page: Network error" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_move_page_with_fromid(self, mock_client):
        """Test page move using page ID."""
        # Setup mock response
        mock_client.move_page.return_value = {
            "from": "Old Title",
            "to": "New Title",
            "reason": ""
        }

        arguments = {
            "fromid": 12345,
            "to": "New Title"
        }

        result = await handle_move_page(mock_client, arguments)

        assert len(result) == 1
        assert "Successfully moved page 'Old Title' to 'New Title'" in result[0].text
