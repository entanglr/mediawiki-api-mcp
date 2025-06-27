"""Tests for wiki page delete functionality."""

from unittest.mock import AsyncMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_delete import handle_delete_page


@pytest.fixture
def mock_client():
    """Create a mock MediaWiki client."""
    client = AsyncMock(spec=MediaWikiClient)
    return client


@pytest.mark.asyncio
async def test_handle_delete_page_success(mock_client):
    """Test successful page deletion."""
    # Mock successful delete response
    mock_client.delete_page.return_value = {
        "title": "Test Page",
        "reason": "Test deletion",
        "logid": 12345
    }

    arguments = {
        "title": "Test Page",
        "reason": "Test deletion"
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully deleted page 'Test Page'" in result[0].text
    assert "Test deletion" in result[0].text
    assert "12345" in result[0].text
    mock_client.delete_page.assert_called_once()


@pytest.mark.asyncio
async def test_handle_delete_page_with_pageid(mock_client):
    """Test page deletion using page ID."""
    mock_client.delete_page.return_value = {
        "title": "Test Page",
        "reason": "Auto-generated reason",
        "logid": 12346
    }

    arguments = {
        "pageid": 123,
        "reason": "Delete by ID"
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully deleted page 'Test Page'" in result[0].text

    # Check that delete_page was called with the expected arguments
    call_args = mock_client.delete_page.call_args[1]
    assert call_args["pageid"] == 123
    assert call_args["reason"] == "Delete by ID"
    assert "title" not in call_args  # title was None so should be filtered out
    mock_client.delete_page.assert_called_once()


@pytest.mark.asyncio
async def test_handle_delete_page_with_options(mock_client):
    """Test page deletion with optional parameters."""
    mock_client.delete_page.return_value = {
        "title": "Test Page",
        "reason": "Test deletion with options",
        "logid": 12347
    }

    arguments = {
        "title": "Test Page",
        "reason": "Test deletion with options",
        "deletetalk": True,
        "tags": ["test", "automated"],
        "watchlist": "watch"
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully deleted page 'Test Page'" in result[0].text

    # Check that delete_page was called with the expected arguments
    call_args = mock_client.delete_page.call_args[1]
    assert call_args["title"] == "Test Page"
    assert call_args["reason"] == "Test deletion with options"
    assert call_args["deletetalk"] is True
    assert call_args["tags"] == ["test", "automated"]
    assert call_args["watchlist"] == "watch"
    mock_client.delete_page.assert_called_once()


@pytest.mark.asyncio
async def test_handle_delete_page_missing_identifier(mock_client):
    """Test error when both title and pageid are missing."""
    arguments = {
        "reason": "Test deletion"
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Error: Either 'title' or 'pageid' must be provided" in result[0].text
    mock_client.delete_page.assert_not_called()


@pytest.mark.asyncio
async def test_handle_delete_page_api_error(mock_client):
    """Test handling of API errors."""
    mock_client.delete_page.side_effect = Exception("API Error")

    arguments = {
        "title": "Test Page",
        "reason": "Test deletion"
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Error deleting page: API Error" in result[0].text


@pytest.mark.asyncio
async def test_handle_delete_page_delete_failed(mock_client):
    """Test handling when delete operation fails."""
    mock_client.delete_page.return_value = {
        "error": {
            "code": "permissiondenied",
            "info": "You don't have permission to delete this page."
        }
    }

    arguments = {
        "title": "Test Page",
        "reason": "Test deletion"
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Delete failed:" in result[0].text


@pytest.mark.asyncio
async def test_handle_delete_page_none_values_filtered(mock_client):
    """Test that None values are filtered out from parameters."""
    mock_client.delete_page.return_value = {
        "title": "Test Page",
        "reason": "Test deletion",
        "logid": 12348
    }

    arguments = {
        "title": "Test Page",
        "pageid": None,
        "reason": None,
        "tags": None,
        "deletetalk": False,
        "oldimage": None
    }

    result = await handle_delete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully deleted page" in result[0].text

    # Verify that only non-None values were passed to delete_page
    call_args = mock_client.delete_page.call_args[1]
    assert "pageid" not in call_args
    assert "reason" not in call_args
    assert "tags" not in call_args
    assert "oldimage" not in call_args
    assert call_args["deletetalk"] is False  # False is kept, not filtered
