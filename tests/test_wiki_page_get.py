"""Test suite for MediaWiki page retrieval handlers."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from mediawiki_api_mcp.handlers.wiki_page_get import handle_get_page
from mediawiki_api_mcp.client import MediaWikiClient


class TestGetHandlers:
    """Test cases for page retrieval-related handlers."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock MediaWiki client."""
        client = MagicMock(spec=MediaWikiClient)
        return client

    @pytest.mark.asyncio
    async def test_handle_get_page_success(self, mock_client):
        """Test successful page retrieval."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": {
                    "12345": {
                        "pageid": 12345,
                        "title": "Test Page",
                        "revisions": [
                            {"*": "Test page content"}
                        ]
                    }
                }
            }
        }

        arguments = {"title": "Test Page"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page: Test Page (ID: 12345)" in result[0].text
        assert "Test page content" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_missing(self, mock_client):
        """Test get page for non-existent page."""
        mock_client.get_page_info.return_value = {
            "query": {
                "pages": {
                    "-1": {
                        "title": "Nonexistent Page",
                        "missing": True
                    }
                }
            }
        }

        arguments = {"title": "Nonexistent Page"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Page not found: Nonexistent Page" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_missing_params(self, mock_client):
        """Test get page with missing required parameters."""
        arguments = {}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error: Either 'title' or 'pageid' must be provided" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_get_page_exception(self, mock_client):
        """Test get page with client exception."""
        mock_client.get_page_info.side_effect = Exception("Network error")

        arguments = {"title": "Test Page"}

        result = await handle_get_page(mock_client, arguments)

        assert len(result) == 1
        assert "Error retrieving page: Network error" in result[0].text
