"""MediaWiki API search operations client."""

import logging
from typing import Any

from .client_auth import MediaWikiAuthClient

logger = logging.getLogger(__name__)


class MediaWikiSearchClient:
    """Client for handling MediaWiki search operations."""

    def __init__(self, auth_client: MediaWikiAuthClient):
        self.auth_client = auth_client

    async def search_pages(
        self,
        search_query: str,
        namespaces: list[int] | None = None,
        limit: int = 10,
        offset: int = 0,
        what: str = "text",
        info: list[str] | None = None,
        prop: list[str] | None = None,
        interwiki: bool = False,
        enable_rewrites: bool = True,
        srsort: str = "relevance",
        qiprofile: str = "engine_autoselect"
    ) -> dict[str, Any]:
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
            srsort: Sort order for results (default: "relevance")
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
        params["srlimit"] = str(max(1, min(500, limit)))
        if offset > 0:
            params["sroffset"] = str(offset)

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
        if srsort in valid_sorts:
            params["srsort"] = srsort

        try:
            response = await self.auth_client._make_request("GET", params=params)
            logger.info(f"Search completed for query: '{search_query}'")
            return response

        except Exception as e:
            logger.error(f"Search request failed: {e}")
            raise

    async def opensearch(
        self,
        search: str,
        namespace: list[int] | None = None,
        limit: int = 10,
        profile: str = "engine_autoselect",
        redirects: str | None = None,
        format: str = "json",
        warningsaserror: bool = False
    ) -> dict[str, Any]:
        """
        Search the wiki using the OpenSearch protocol.

        Args:
            search: Search string (required)
            namespace: Namespaces to search (default: [0] for main namespace)
            limit: Maximum number of results (1-500, default: 10)
            profile: Search profile (default: "engine_autoselect")
            redirects: How to handle redirects - "return" or "resolve"
            format: Output format (default: "json")
            warningsaserror: Treat warnings as errors (default: False)

        Returns:
            Dictionary containing OpenSearch results in standard format:
            [search_term, [titles], [descriptions], [urls]]
        """
        if not search:
            raise ValueError("Search parameter is required")

        # Build opensearch parameters
        params = {
            "action": "opensearch",
            "search": search,
            "format": format
        }

        # Set namespaces (default to main namespace if not specified)
        if namespace is None:
            namespace = [0]
        if namespace:
            params["namespace"] = "|".join(str(ns) for ns in namespace)

        # Set limit (clamp to valid range)
        params["limit"] = str(max(1, min(500, limit)))

        # Set search profile
        valid_profiles = [
            "strict", "normal", "normal-subphrases", "fuzzy", "fast-fuzzy",
            "fuzzy-subphrases", "classic", "engine_autoselect"
        ]
        if profile in valid_profiles:
            params["profile"] = profile

        # Set redirect handling
        if redirects in ["return", "resolve"]:
            params["redirects"] = redirects

        # Set warnings as error flag
        if warningsaserror:
            params["warningsaserror"] = "1"

        try:
            response = await self.auth_client._make_request("GET", params=params)
            logger.info(f"OpenSearch completed for query: '{search}'")
            return response

        except Exception as e:
            logger.error(f"OpenSearch request failed: {e}")
            raise
