"""MediaWiki API client for handling authentication and requests."""

import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MediaWikiConfig(BaseModel):
    """Configuration for MediaWiki API connection."""
    api_url: str
    username: str
    password: str
    user_agent: str = "MediaWiki-MCP-Bot/1.0"


class MediaWikiClient:
    """Client for interacting with MediaWiki API."""

    def __init__(self, config: MediaWikiConfig):
        self.config = config
        self.session = httpx.AsyncClient()
        self.csrf_token: Optional[str] = None
        self.logged_in = False

    async def __aenter__(self):
        """Async context manager entry."""
        await self.login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.session.aclose()

    async def _make_request(
        self,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the MediaWiki API."""
        url = self.config.api_url
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "application/json"
        }

        if method == "GET":
            response = await self.session.get(url, params=params, headers=headers)
        else:
            response = await self.session.post(url, data=data, headers=headers)

        response.raise_for_status()
        return response.json()

    async def login(self) -> bool:
        """Authenticate with MediaWiki using bot credentials."""
        try:
            # Step 1: Get login token
            login_token_params = {
                "action": "query",
                "meta": "tokens",
                "type": "login",
                "format": "json"
            }

            response = await self._make_request("GET", params=login_token_params)
            login_token = response["query"]["tokens"]["logintoken"]

            # Step 2: Login with credentials
            login_data = {
                "action": "login",
                "lgname": self.config.username,
                "lgpassword": self.config.password,
                "lgtoken": login_token,
                "format": "json"
            }

            login_response = await self._make_request("POST", data=login_data)

            if login_response.get("login", {}).get("result") == "Success":
                self.logged_in = True
                logger.info("Successfully logged in to MediaWiki")
                return True
            else:
                logger.error(f"Login failed: {login_response}")
                return False

        except Exception as e:
            logger.error(f"Login error: {e}")
            return False

    async def get_csrf_token(self) -> Optional[str]:
        """Get CSRF token for editing operations."""
        if not self.logged_in:
            await self.login()

        try:
            params = {
                "action": "query",
                "meta": "tokens",
                "format": "json"
            }

            response = await self._make_request("GET", params=params)
            self.csrf_token = response["query"]["tokens"]["csrftoken"]
            return self.csrf_token

        except Exception as e:
            logger.error(f"Failed to get CSRF token: {e}")
            return None

    async def edit_page(
        self,
        title: Optional[str] = None,
        pageid: Optional[int] = None,
        text: Optional[str] = None,
        summary: Optional[str] = None,
        section: Optional[str] = None,
        sectiontitle: Optional[str] = None,
        appendtext: Optional[str] = None,
        prependtext: Optional[str] = None,
        minor: bool = False,
        bot: bool = True,
        createonly: bool = False,
        nocreate: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Edit a MediaWiki page.

        Args:
            title: Title of the page to edit
            pageid: Page ID of the page to edit
            text: New page content
            summary: Edit summary
            section: Section identifier (0 for top, "new" for new section)
            sectiontitle: Title for new section
            appendtext: Text to append to page
            prependtext: Text to prepend to page
            minor: Mark as minor edit
            bot: Mark as bot edit
            createonly: Don't edit if page exists
            nocreate: Don't create if page doesn't exist
            **kwargs: Additional parameters

        Returns:
            API response dictionary
        """
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        if not self.csrf_token:
            await self.get_csrf_token()

        if not self.csrf_token:
            raise ValueError("Could not obtain CSRF token")

        # Build edit parameters
        edit_data = {
            "action": "edit",
            "format": "json",
            "token": self.csrf_token
        }

        # Page identification
        if title:
            edit_data["title"] = title
        if pageid:
            edit_data["pageid"] = pageid

        # Content parameters
        if text is not None:
            edit_data["text"] = text
        if appendtext is not None:
            edit_data["appendtext"] = appendtext
        if prependtext is not None:
            edit_data["prependtext"] = prependtext

        # Section handling
        if section is not None:
            edit_data["section"] = section
        if sectiontitle is not None:
            edit_data["sectiontitle"] = sectiontitle

        # Metadata
        if summary:
            edit_data["summary"] = summary
        if minor:
            edit_data["minor"] = "1"
        if bot:
            edit_data["bot"] = "1"
        if createonly:
            edit_data["createonly"] = "1"
        if nocreate:
            edit_data["nocreate"] = "1"

        # Add any additional parameters
        edit_data.update(kwargs)

        try:
            response = await self._make_request("POST", data=edit_data)

            if "edit" in response and response["edit"].get("result") == "Success":
                logger.info(f"Successfully edited page: {title or pageid}")
                return response["edit"]
            else:
                logger.error(f"Edit failed: {response}")
                return response

        except Exception as e:
            logger.error(f"Edit request failed: {e}")
            raise

    async def get_page_info(
        self,
        title: Optional[str] = None,
        pageid: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get information about a page using the Revisions API with proper parameters."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "prop": "revisions",
            "rvslots": "*",
            "rvprop": "content"
        }

        if title:
            params["titles"] = title
        if pageid:
            params["pageids"] = str(pageid)

        response = await self._make_request("GET", params=params)
        return response

    async def get_page_raw(
        self,
        title: Optional[str] = None,
        pageid: Optional[int] = None
    ) -> str:
        """Get raw wikitext content using the raw action (fastest method)."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "raw"
        }

        if title:
            params["title"] = title
        elif pageid:
            params["curid"] = str(pageid)

        # Raw action returns plain text, not JSON
        url = self.config.api_url
        headers = {
            "User-Agent": self.config.user_agent
        }

        response = await self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.text

    async def get_page_parse(
        self,
        title: Optional[str] = None,
        pageid: Optional[int] = None,
        format_type: str = "wikitext"
    ) -> Dict[str, Any]:
        """Get page content using the Parse API (HTML or wikitext)."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "parse",
            "format": "json",
            "formatversion": "2"
        }

        if title:
            params["page"] = title
        elif pageid:
            params["oldid"] = str(pageid)

        if format_type == "html":
            params["prop"] = "text"
        else:
            params["prop"] = "wikitext"

        response = await self._make_request("GET", params=params)
        return response

    async def get_page_extracts(
        self,
        title: Optional[str] = None,
        pageid: Optional[int] = None,
        sentences: Optional[int] = None,
        chars: Optional[int] = None,
        plain_text: bool = True
    ) -> Dict[str, Any]:
        """Get page extracts using the TextExtracts API."""
        if not title and not pageid:
            raise ValueError("Either title or pageid must be provided")

        params = {
            "action": "query",
            "format": "json",
            "formatversion": "2",
            "prop": "extracts",
            "exlimit": "1"
        }

        if title:
            params["titles"] = title
        elif pageid:
            params["pageids"] = str(pageid)

        if sentences:
            params["exsentences"] = str(sentences)
        elif chars:
            params["exchars"] = str(chars)

        if plain_text:
            params["explaintext"] = "1"

        response = await self._make_request("GET", params=params)
        return response

    async def search_pages(
        self,
        search_query: str,
        namespaces: Optional[list] = None,
        limit: int = 10,
        offset: int = 0,
        what: str = "text",
        info: Optional[list] = None,
        prop: Optional[list] = None,
        interwiki: bool = False,
        enable_rewrites: bool = True,
        sort_order: str = "relevance",
        qiprofile: str = "engine_autoselect"
    ) -> Dict[str, Any]:
        """
        Perform a full-text search using MediaWiki's search API.

        Args:
            search_query: Search query string (required)
            namespaces: List of namespace IDs to search in (default: [0] for main namespace)
            limit: Maximum number of results (1-500, default: 10)
            offset: Search result offset for pagination (default: 0)
            what: Type of search - "text", "title", or "nearmatch" (default: "text")
            info: Metadata to return - list from ["rewrittenquery", "suggestion", "totalhits"]
            prop: Properties to return - list from available search properties
            interwiki: Include interwiki results if available (default: False)
            enable_rewrites: Enable internal query rewriting (default: True)
            sort_order: Sort order for results (default: "relevance")
            qiprofile: Query independent ranking profile (default: "engine_autoselect")

        Returns:
            Dictionary containing search results and metadata
        """
        if not search_query:
            raise ValueError("Search query (srsearch) is required")

        # Build search parameters
        params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json"
        }

        # Set namespaces (default to main namespace if not specified)
        if namespaces is None:
            namespaces = [0]
        if namespaces:
            params["srnamespace"] = "|".join(str(ns) for ns in namespaces)

        # Set limits and pagination
        params["srlimit"] = max(1, min(500, limit))
        if offset > 0:
            params["sroffset"] = offset

        # Set search type
        if what in ["text", "title", "nearmatch"]:
            params["srwhat"] = what

        # Set query independent profile
        valid_profiles = [
            "classic", "classic_noboostlinks", "empty", "engine_autoselect",
            "popular_inclinks", "popular_inclinks_pv", "wsum_inclinks", "wsum_inclinks_pv"
        ]
        if qiprofile in valid_profiles:
            params["srqiprofile"] = qiprofile

        # Set metadata info to return
        if info is None:
            info = ["totalhits", "suggestion", "rewrittenquery"]
        if info:
            valid_info = ["rewrittenquery", "suggestion", "totalhits"]
            filtered_info = [i for i in info if i in valid_info]
            if filtered_info:
                params["srinfo"] = "|".join(filtered_info)

        # Set search result properties
        if prop is None:
            prop = ["size", "wordcount", "timestamp", "snippet"]
        if prop:
            valid_props = [
                "categorysnippet", "extensiondata", "isfilematch", "redirectsnippet",
                "redirecttitle", "sectionsnippet", "sectiontitle", "size", "snippet",
                "timestamp", "titlesnippet", "wordcount"
            ]
            filtered_props = [p for p in prop if p in valid_props]
            if filtered_props:
                params["srprop"] = "|".join(filtered_props)

        # Set optional boolean parameters
        if interwiki:
            params["srinterwiki"] = "1"
        if enable_rewrites:
            params["srenablerewrites"] = "1"

        # Set sort order
        valid_sorts = [
            "create_timestamp_asc", "create_timestamp_desc", "incoming_links_asc",
            "incoming_links_desc", "just_match", "last_edit_asc", "last_edit_desc",
            "none", "random", "relevance", "user_random"
        ]
        if sort_order in valid_sorts:
            params["srsort"] = sort_order

        try:
            response = await self._make_request("GET", params=params)
            logger.info(f"Search completed for query: '{search_query}'")
            return response

        except Exception as e:
            logger.error(f"Search request failed: {e}")
            raise
