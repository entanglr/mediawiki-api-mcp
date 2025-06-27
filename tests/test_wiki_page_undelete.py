"""Tests for wiki page undelete functionality."""

from unittest.mock import AsyncMock

import pytest

from mediawiki_api_mcp.client import MediaWikiClient
from mediawiki_api_mcp.handlers.wiki_page_undelete import handle_undelete_page


@pytest.fixture
def mock_client():
    """Create a mock MediaWiki client."""
    client = AsyncMock(spec=MediaWikiClient)
    return client


@pytest.mark.asyncio
async def test_handle_undelete_page_success(mock_client):
    """Test successful page undelete."""
    # Mock successful undelete response
    mock_client.undelete_page.return_value = {
        "title": "Test Page",
        "reason": "Test restoration",
        "revisions": 2,
        "fileversions": 0
    }

    arguments = {
        "title": "Test Page",
        "reason": "Test restoration"
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully undeleted page 'Test Page'" in result[0].text
    assert "Test restoration" in result[0].text
    assert "Revisions restored: 2" in result[0].text
    assert "File versions restored: 0" in result[0].text
    mock_client.undelete_page.assert_called_once()


@pytest.mark.asyncio
async def test_handle_undelete_page_with_timestamps(mock_client):
    """Test page undelete with specific timestamps."""
    mock_client.undelete_page.return_value = {
        "title": "Test Page",
        "reason": "Selective restoration",
        "revisions": 1,
        "fileversions": 0
    }

    arguments = {
        "title": "Test Page",
        "reason": "Selective restoration",
        "timestamps": ["2023-01-01T12:00:00Z"]
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully undeleted page 'Test Page'" in result[0].text
    assert "Selective restoration" in result[0].text
    assert "Revisions restored: 1" in result[0].text
    mock_client.undelete_page.assert_called_once_with(
        title="Test Page",
        reason="Selective restoration",
        timestamps=["2023-01-01T12:00:00Z"]
    )


@pytest.mark.asyncio
async def test_handle_undelete_page_with_fileids(mock_client):
    """Test page undelete with specific file IDs."""
    mock_client.undelete_page.return_value = {
        "title": "File:Test.jpg",
        "reason": "File restoration",
        "revisions": 0,
        "fileversions": 2
    }

    arguments = {
        "title": "File:Test.jpg",
        "reason": "File restoration",
        "fileids": [123, 456]
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully undeleted page 'File:Test.jpg'" in result[0].text
    assert "File restoration" in result[0].text
    assert "File versions restored: 2" in result[0].text
    mock_client.undelete_page.assert_called_once_with(
        title="File:Test.jpg",
        reason="File restoration",
        fileids=[123, 456]
    )


@pytest.mark.asyncio
async def test_handle_undelete_page_with_undeletetalk(mock_client):
    """Test page undelete with talk page restoration."""
    mock_client.undelete_page.return_value = {
        "title": "Test Page",
        "reason": "Complete restoration",
        "revisions": 3,
        "fileversions": 0
    }

    arguments = {
        "title": "Test Page",
        "reason": "Complete restoration",
        "undeletetalk": True
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully undeleted page 'Test Page'" in result[0].text
    mock_client.undelete_page.assert_called_once_with(
        title="Test Page",
        reason="Complete restoration",
        undeletetalk=True
    )


@pytest.mark.asyncio
async def test_handle_undelete_page_with_tags(mock_client):
    """Test page undelete with tags."""
    mock_client.undelete_page.return_value = {
        "title": "Test Page",
        "reason": "Tagged restoration",
        "revisions": 1,
        "fileversions": 0
    }

    arguments = {
        "title": "Test Page",
        "reason": "Tagged restoration",
        "tags": ["test-tag", "restoration"]
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully undeleted page 'Test Page'" in result[0].text
    mock_client.undelete_page.assert_called_once_with(
        title="Test Page",
        reason="Tagged restoration",
        tags=["test-tag", "restoration"]
    )


@pytest.mark.asyncio
async def test_handle_undelete_page_missing_title(mock_client):
    """Test undelete with missing title."""
    arguments = {}

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Error: 'title' parameter is required" in result[0].text
    mock_client.undelete_page.assert_not_called()


@pytest.mark.asyncio
async def test_handle_undelete_page_empty_title(mock_client):
    """Test undelete with empty title."""
    arguments = {"title": ""}

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Error: 'title' parameter is required" in result[0].text
    mock_client.undelete_page.assert_not_called()


@pytest.mark.asyncio
async def test_handle_undelete_page_none_title(mock_client):
    """Test undelete with None title."""
    arguments = {"title": None}

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Error: 'title' parameter is required" in result[0].text
    mock_client.undelete_page.assert_not_called()


@pytest.mark.asyncio
async def test_handle_undelete_page_api_error(mock_client):
    """Test undelete with API error."""
    mock_client.undelete_page.side_effect = Exception("API Error: Permission denied")

    arguments = {
        "title": "Test Page",
        "reason": "Test restoration"
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Error undeleting page: API Error: Permission denied" in result[0].text
    mock_client.undelete_page.assert_called_once()


@pytest.mark.asyncio
async def test_handle_undelete_page_bad_response(mock_client):
    """Test undelete with bad API response."""
    # Mock response without expected structure
    mock_client.undelete_page.return_value = {
        "error": {
            "code": "cantundelete",
            "info": "Couldn't undelete: the requested revisions may not exist"
        }
    }

    arguments = {
        "title": "Test Page",
        "reason": "Test restoration"
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Undelete failed:" in result[0].text
    mock_client.undelete_page.assert_called_once()


@pytest.mark.asyncio
async def test_handle_undelete_page_with_watchlist(mock_client):
    """Test page undelete with watchlist settings."""
    mock_client.undelete_page.return_value = {
        "title": "Test Page",
        "reason": "Watched restoration",
        "revisions": 1,
        "fileversions": 0
    }

    arguments = {
        "title": "Test Page",
        "reason": "Watched restoration",
        "watchlist": "watch",
        "watchlistexpiry": "1 month"
    }

    result = await handle_undelete_page(mock_client, arguments)

    assert len(result) == 1
    assert "Successfully undeleted page 'Test Page'" in result[0].text
    mock_client.undelete_page.assert_called_once_with(
        title="Test Page",
        reason="Watched restoration",
        watchlist="watch",
        watchlistexpiry="1 month"
    )
