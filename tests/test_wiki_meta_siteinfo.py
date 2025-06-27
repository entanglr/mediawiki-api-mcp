"""Tests for wiki_meta_siteinfo tool."""

from unittest.mock import AsyncMock

import pytest

from mediawiki_api_mcp.handlers.wiki_meta_siteinfo import handle_meta_siteinfo


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_general():
    """Test getting general site information."""
    # Mock client and response
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "general": {
                "sitename": "Test Wiki",
                "mainpage": "Main Page",
                "base": "https://example.com/wiki/Main_Page",
                "server": "https://example.com",
                "wikiid": "testwiki",
                "generator": "MediaWiki 1.39.0",
                "lang": "en",
                "case": "first-letter",
                "timezone": "UTC",
                "timeoffset": 0
            }
        }
    }

    arguments = {"siprop": ["general"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Test Wiki" in result[0].text
    assert "MediaWiki 1.39.0" in result[0].text
    assert "General Information" in result[0].text

    # Verify the client was called with correct parameters
    mock_client.get_siteinfo.assert_called_once_with(
        siprop=["general"],
        sifilteriw=None,
        sishowalldb=False,
        sinumberingroup=False,
        siinlanguagecode=None
    )


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_namespaces():
    """Test getting namespace information."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "namespaces": {
                "0": {"*": "", "case": "first-letter"},
                "1": {"*": "Talk", "case": "first-letter"},
                "2": {"*": "User", "case": "first-letter"},
                "3": {"*": "User talk", "case": "first-letter"}
            }
        }
    }

    arguments = {"siprop": ["namespaces"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Namespaces" in result[0].text
    assert "Talk" in result[0].text
    assert "User" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_statistics():
    """Test getting site statistics."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "statistics": {
                "pages": 12345,
                "articles": 5678,
                "edits": 98765,
                "images": 432,
                "users": 1234,
                "activeusers": 56,
                "admins": 3
            }
        }
    }

    arguments = {"siprop": ["statistics"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Site Statistics" in result[0].text
    assert "12,345" in result[0].text  # Check number formatting
    assert "Content pages: 5,678" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_multiple_props():
    """Test getting multiple types of site information."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "general": {
                "sitename": "Test Wiki",
                "generator": "MediaWiki 1.39.0"
            },
            "statistics": {
                "pages": 1000,
                "articles": 500
            }
        }
    }

    arguments = {"siprop": ["general", "statistics"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "General Information" in result[0].text
    assert "Site Statistics" in result[0].text
    assert "Test Wiki" in result[0].text
    assert "1,000" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_with_options():
    """Test getting site information with additional options."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "usergroups": [
                {
                    "name": "sysop",
                    "rights": ["delete", "undelete", "protect", "block"]
                },
                {
                    "name": "user",
                    "rights": ["read", "edit", "createpage"]
                }
            ]
        }
    }

    arguments = {
        "siprop": ["usergroups"],
        "sinumberingroup": True,
        "siinlanguagecode": "en"
    }
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "User Groups" in result[0].text
    assert "sysop" in result[0].text
    assert "delete" in result[0].text

    # Verify the client was called with correct parameters
    mock_client.get_siteinfo.assert_called_once_with(
        siprop=["usergroups"],
        sifilteriw=None,
        sishowalldb=False,
        sinumberingroup=True,
        siinlanguagecode="en"
    )


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_interwiki_filter():
    """Test getting interwiki information with filter."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "interwikimap": [
                {"prefix": "enwiki", "url": "https://en.wikipedia.org/wiki/$1", "local": True},
                {"prefix": "commons", "url": "https://commons.wikimedia.org/wiki/$1", "local": False}
            ]
        }
    }

    arguments = {
        "siprop": ["interwikimap"],
        "sifilteriw": "local"
    }
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Interwiki Map" in result[0].text
    assert "enwiki" in result[0].text

    # Verify the client was called with correct parameters
    mock_client.get_siteinfo.assert_called_once_with(
        siprop=["interwikimap"],
        sifilteriw="local",
        sishowalldb=False,
        sinumberingroup=False,
        siinlanguagecode=None
    )


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_error_response():
    """Test handling of unexpected response format."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {"error": "Invalid request"}

    arguments = {"siprop": ["general"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Unexpected response format" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_client_exception():
    """Test handling of client exceptions."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.side_effect = Exception("Network error")

    arguments = {"siprop": ["general"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error getting site information" in result[0].text
    assert "Network error" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_extensions():
    """Test getting extensions information."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "extensions": [
                {"name": "ParserFunctions", "version": "1.6.0"},
                {"name": "Cite", "version": "1.0.0"},
                {"name": "VisualEditor"}
            ]
        }
    }

    arguments = {"siprop": ["extensions"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Extensions" in result[0].text
    assert "ParserFunctions (v1.6.0)" in result[0].text
    assert "Cite (v1.0.0)" in result[0].text
    assert "VisualEditor" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_file_extensions():
    """Test getting file extensions information."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "fileextensions": [
                {"ext": "png"}, {"ext": "gif"}, {"ext": "jpg"}, {"ext": "jpeg"},
                {"ext": "webp"}, {"ext": "svg"}, {"ext": "pdf"}, {"ext": "ogg"},
                {"ext": "oga"}, {"ext": "ogv"}, {"ext": "webm"}, {"ext": "mp4"}
            ]
        }
    }

    arguments = {"siprop": ["fileextensions"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Allowed File Extensions" in result[0].text
    assert "png" in result[0].text
    assert "jpg" in result[0].text
    assert "pdf" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_languages():
    """Test getting languages information."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "languages": [
                {"code": "en", "*": "English"},
                {"code": "es", "*": "español"},
                {"code": "fr", "*": "français"},
                {"code": "de", "*": "Deutsch"}
            ]
        }
    }

    arguments = {"siprop": ["languages"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Supported Languages" in result[0].text
    assert "en: English" in result[0].text
    assert "es: español" in result[0].text
    assert "fr: français" in result[0].text
    assert "de: Deutsch" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_skins():
    """Test getting skins information."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "skins": [
                {"code": "vector", "*": "Vector"},
                {"code": "monobook", "*": "MonoBook"},
                {"code": "timeless", "*": "Timeless"},
                {"code": "modern", "*": "Modern"}
            ]
        }
    }

    arguments = {"siprop": ["skins"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Skins" in result[0].text
    assert "Vector" in result[0].text
    assert "MonoBook" in result[0].text
    assert "Timeless" in result[0].text
    assert "Modern" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_languages_legacy_format():
    """Test getting languages information in legacy dictionary format."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "languages": {
                "en": "English",
                "es": "español",
                "fr": "français"
            }
        }
    }

    arguments = {"siprop": ["languages"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Supported Languages" in result[0].text
    assert "en: English" in result[0].text
    assert "es: español" in result[0].text
    assert "fr: français" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_skins_legacy_format():
    """Test getting skins information in legacy dictionary format."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "skins": {
                "vector": {"*": "Vector"},
                "monobook": {"*": "MonoBook"},
                "timeless": {"*": "Timeless"}
            }
        }
    }

    arguments = {"siprop": ["skins"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "Skins" in result[0].text
    assert "Vector" in result[0].text
    assert "MonoBook" in result[0].text
    assert "Timeless" in result[0].text


@pytest.mark.asyncio
async def test_handle_meta_siteinfo_combined_props():
    """Test getting multiple types including languages and skins."""
    mock_client = AsyncMock()
    mock_client.get_siteinfo.return_value = {
        "query": {
            "general": {
                "sitename": "Test Wiki",
                "generator": "MediaWiki 1.39.0"
            },
            "languages": [
                {"code": "en", "*": "English"},
                {"code": "es", "*": "español"}
            ],
            "skins": [
                {"code": "vector", "*": "Vector"},
                {"code": "monobook", "*": "MonoBook"}
            ]
        }
    }

    arguments = {"siprop": ["general", "languages", "skins"]}
    result = await handle_meta_siteinfo(mock_client, arguments)

    assert len(result) == 1
    assert result[0].type == "text"
    assert "General Information" in result[0].text
    assert "Supported Languages" in result[0].text
    assert "Skins" in result[0].text
    assert "Test Wiki" in result[0].text
    assert "en: English" in result[0].text
    assert "Vector" in result[0].text

