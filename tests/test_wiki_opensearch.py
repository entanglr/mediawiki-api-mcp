"""Test cases for wiki_opensearch tool."""

from unittest.mock import AsyncMock, Mock

import pytest

from mediawiki_api_mcp.handlers.wiki_opensearch import handle_opensearch


@pytest.mark.asyncio
async def test_handle_opensearch_success():
    """Test successful opensearch operation."""
    mock_client = Mock()
    mock_client.opensearch = AsyncMock(return_value=[
        "test search",
        ["Test Page 1", "Test Page 2"],
        ["Description 1", "Description 2"],
        ["https://example.com/Test_Page_1", "https://example.com/Test_Page_2"]
    ])

    arguments = {
        "search": "test search",
        "namespace": [0],
        "limit": 10,
        "profile": "engine_autoselect"
    }

    result = await handle_opensearch(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "OpenSearch Results for: 'test search'" in result[0].text
    assert "Test Page 1" in result[0].text
    assert "Test Page 2" in result[0].text
    assert "Description 1" in result[0].text
    assert "Description 2" in result[0].text


@pytest.mark.asyncio
async def test_handle_opensearch_missing_search():
    """Test opensearch with missing search parameter."""
    mock_client = Mock()

    arguments = {}

    result = await handle_opensearch(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error: Search parameter is required" in result[0].text


@pytest.mark.asyncio
async def test_handle_opensearch_empty_results():
    """Test opensearch with no results."""
    mock_client = Mock()
    mock_client.opensearch = AsyncMock(return_value=[
        "nonexistent search",
        [],
        [],
        []
    ])

    arguments = {
        "search": "nonexistent search"
    }

    result = await handle_opensearch(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "No results found." in result[0].text


@pytest.mark.asyncio
async def test_handle_opensearch_client_error():
    """Test opensearch with client error."""
    mock_client = Mock()
    mock_client.opensearch = AsyncMock(side_effect=Exception("API Error"))

    arguments = {
        "search": "test search"
    }

    result = await handle_opensearch(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error performing OpenSearch: API Error" in result[0].text


@pytest.mark.asyncio
async def test_handle_opensearch_invalid_response_format():
    """Test opensearch with invalid response format."""
    mock_client = Mock()
    mock_client.opensearch = AsyncMock(return_value={"invalid": "format"})

    arguments = {
        "search": "test search"
    }

    result = await handle_opensearch(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Unexpected OpenSearch response format:" in result[0].text


@pytest.mark.asyncio
async def test_handle_opensearch_with_all_parameters():
    """Test opensearch with all parameters specified."""
    mock_client = Mock()
    mock_client.opensearch = AsyncMock(return_value=[
        "comprehensive search",
        ["Comprehensive Page"],
        ["A comprehensive description"],
        ["https://example.com/Comprehensive_Page"]
    ])

    arguments = {
        "search": "comprehensive search",
        "namespace": [0, 1],
        "limit": 20,
        "profile": "fuzzy",
        "redirects": "resolve",
        "format": "json",
        "warningsaserror": True
    }

    result = await handle_opensearch(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "OpenSearch Results for: 'comprehensive search'" in result[0].text
    assert "Comprehensive Page" in result[0].text

    # Verify all parameters were passed to the client
    mock_client.opensearch.assert_called_once_with(
        search="comprehensive search",
        namespace=[0, 1],
        limit=20,
        profile="fuzzy",
        redirects="resolve",
        format="json",
        warningsaserror=True
    )
