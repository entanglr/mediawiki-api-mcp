"""MediaWiki API client for handling authentication and requests."""

import logging
from typing import Any

from pydantic import BaseModel

from .client_modules import (
    MediaWikiAuthClient,
    MediaWikiMetaClient,
    MediaWikiPageClient,
    MediaWikiSearchClient,
)

logger = logging.getLogger(__name__)


class MediaWikiConfig(BaseModel):
    """Configuration for MediaWiki API connection."""
    api_url: str
    username: str
    password: str
    user_agent: str = "MediaWiki-MCP-Bot/1.0"


class MediaWikiClient:
    """Orchestrating client for interacting with MediaWiki API."""

    def __init__(self, config: MediaWikiConfig):
        self.config = config
        self.auth_client = MediaWikiAuthClient(
            api_url=config.api_url,
            username=config.username,
            password=config.password,
            user_agent=config.user_agent
        )
        self.page_client = MediaWikiPageClient(self.auth_client)
        self.search_client = MediaWikiSearchClient(self.auth_client)
        self.meta_client = MediaWikiMetaClient(self.auth_client)

    async def __aenter__(self) -> "MediaWikiClient":
        """Async context manager entry."""
        await self.auth_client.__aenter__()
        return self

    async def __aexit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object | None) -> None:
        """Async context manager exit."""
        await self.auth_client.__aexit__(exc_type, exc_val, exc_tb)

    # Page operations delegation
    async def edit_page(self, **kwargs: Any) -> dict[str, Any]:
        """Edit a MediaWiki page."""
        return await self.page_client.edit_page(**kwargs)

    async def get_page_info(self, **kwargs: Any) -> dict[str, Any]:
        """Get information about a page using the Revisions API."""
        return await self.page_client.get_page_info(**kwargs)

    async def get_page_raw(self, **kwargs: Any) -> str:
        """Get raw wikitext content using the raw action."""
        return await self.page_client.get_page_raw(**kwargs)

    async def get_page_parse(self, **kwargs: Any) -> dict[str, Any]:
        """Get page content using the Parse API."""
        return await self.page_client.get_page_parse(**kwargs)

    async def get_page_extracts(self, **kwargs: Any) -> dict[str, Any]:
        """Get page extracts using the TextExtracts API."""
        return await self.page_client.get_page_extracts(**kwargs)

    async def move_page(self, **kwargs: Any) -> dict[str, Any]:
        """Move a MediaWiki page."""
        return await self.page_client.move_page(**kwargs)

    async def delete_page(self, **kwargs: Any) -> dict[str, Any]:
        """Delete a MediaWiki page."""
        return await self.page_client.delete_page(**kwargs)

    async def undelete_page(self, **kwargs: Any) -> dict[str, Any]:
        """Undelete (restore) the revisions of a deleted MediaWiki page."""
        return await self.page_client.undelete_page(**kwargs)

    # Search operations delegation
    async def search_pages(self, **kwargs: Any) -> dict[str, Any]:
        """Perform a full-text search using MediaWiki's search API."""
        return await self.search_client.search_pages(**kwargs)

    async def opensearch(self, **kwargs: Any) -> dict[str, Any]:
        """Search the wiki using the OpenSearch protocol."""
        return await self.search_client.opensearch(**kwargs)

    # Meta operations delegation
    async def get_siteinfo(self, **kwargs: Any) -> dict[str, Any]:
        """Get overall site information from MediaWiki."""
        return await self.meta_client.get_siteinfo(**kwargs)

    # Authentication delegation
    async def login(self) -> bool:
        """Authenticate with MediaWiki using bot credentials."""
        return await self.auth_client.login()

    async def get_csrf_token(self) -> str | None:
        """Get CSRF token for editing operations."""
        return await self.auth_client.get_csrf_token()
